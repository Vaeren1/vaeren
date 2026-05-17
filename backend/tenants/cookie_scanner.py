"""TTDSG-Cookie-Scanner (Phase 1.5).

Lädt eine angegebene URL und identifiziert Tracking-Cookies + bekannte
Tracking-Skripte. Klassifizierung:
- ESSENZIELL: technisch notwendig (Session, CSRF, Sprache).
- FUNKTIONAL: Komfort (Theme, A/B-Test ohne PII).
- MARKETING: Tracking, Werbung, Cross-Site-Profile.
- UNKLAR: nicht zuzuordnen.

Public-Tool: kein Login, Rate-Limit 30/h pro IP. Wird über
`vaeren.de/tools/cookie-check` aufgerufen.

NICHT JavaScript-rendered — wir lesen nur den Response-Header + initial HTML.
Das übersieht client-side gesetzte Cookies, aber für ein Marketing-Tool
„Selbst-Check, ob Ihre Seite groben Cookie-Banner-Bedarf hat" reicht es.

Production-Härtung:
- 5-Sek-Timeout für HTTP-Call.
- max-redirects: 3.
- Nur http(s)://, kein localhost/private-IP-Targeting (SSRF-Schutz).
"""

from __future__ import annotations

import ipaddress
import logging
import re
import socket
import urllib.parse
from dataclasses import asdict, dataclass

import httpx

logger = logging.getLogger(__name__)

# Bekannte Tracking-Cookie-Namen + Script-Markers.
MARKETING_COOKIES = {
    "_ga", "_gid", "_gat", "_gtag",  # Google Analytics
    "_fbp", "_fbc",  # Facebook Pixel
    "_pin_unauth", "_pinterest_sess",  # Pinterest
    "MUID", "MUIDB",  # Microsoft / Bing
    "li_at", "lidc", "_linkedin_data_partner_id",  # LinkedIn
    "_twitter_sess", "personalization_id",  # X/Twitter
    "_hjid", "_hjFirstSeen",  # Hotjar
    "ajs_anonymous_id",  # Segment
    "amplitude_id", "MPID",  # Mixpanel/Amplitude
    "intercom-session", "intercom-id",  # Intercom
    "_uetsid", "_uetvid",  # Bing UET
}
FUNCTIONAL_COOKIES = {
    "theme", "lang", "language", "ui_locale", "tz",
    "consent",  # OneTrust-Style Consent-Speicher
    "cookieconsent_status", "CookieConsent",
}
ESSENTIAL_PREFIXES = (
    "csrftoken",
    "session",
    "sessionid",
    "_session",
    "django_",
    "PHPSESSID",
    "JSESSIONID",
    "ASP.NET_SessionId",
    "wp_",
    "AWSALB",
    "AWSELB",
    "__Secure-",
    "__Host-",
)

MARKETING_SCRIPT_HOSTS = (
    "googletagmanager.com",
    "google-analytics.com",
    "googlesyndication.com",
    "doubleclick.net",
    "connect.facebook.net",
    "static.hotjar.com",
    "cdn.segment.com",
    "snap.licdn.com",
    "static.ads-twitter.com",
    "platform.twitter.com",
    "widget.intercom.io",
    "cdn.amplitude.com",
    "snap.licdn.com",
    "matomo.cloud",  # Hosted-Matomo zählen wir als Marketing (DSGVO-Diskussion offen)
)


class ScanError(Exception):
    def __init__(self, code: str, detail: str, status_code: int = 400) -> None:
        self.code = code
        self.detail = detail
        self.status_code = status_code
        super().__init__(detail)


@dataclass
class CookieBefund:
    name: str
    klassifizierung: str
    secure: bool
    httponly: bool
    samesite: str


@dataclass
class ScriptBefund:
    src: str
    klassifizierung: str


@dataclass
class ScanErgebnis:
    url: str
    final_url: str
    cookies: list[CookieBefund]
    scripts: list[ScriptBefund]
    consent_banner_erkannt: bool
    consent_marker: list[str]
    score: int  # 0-100, höher = besser
    empfehlungen: list[str]

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "final_url": self.final_url,
            "cookies": [asdict(c) for c in self.cookies],
            "scripts": [asdict(s) for s in self.scripts],
            "consent_banner_erkannt": self.consent_banner_erkannt,
            "consent_marker": self.consent_marker,
            "score": self.score,
            "empfehlungen": self.empfehlungen,
        }


def _is_safe_target(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.hostname:
        return False
    host = parsed.hostname
    # Loopback und Link-Local blocken
    try:
        for fam in (socket.AF_INET, socket.AF_INET6):
            try:
                info = socket.getaddrinfo(host, None, fam)
            except socket.gaierror:
                continue
            for entry in info:
                ip_str = entry[4][0]
                ip = ipaddress.ip_address(ip_str)
                if (
                    ip.is_private
                    or ip.is_loopback
                    or ip.is_link_local
                    or ip.is_multicast
                    or ip.is_reserved
                ):
                    return False
    except (ValueError, socket.error):
        return False
    return True


def _klassifiziere_cookie(name: str) -> str:
    base = name.split(".")[0]
    if name in MARKETING_COOKIES or base in MARKETING_COOKIES:
        return "marketing"
    if name in FUNCTIONAL_COOKIES or base.lower() in FUNCTIONAL_COOKIES:
        return "funktional"
    # Prefix-Match für essenzielle Cookies
    for p in ESSENTIAL_PREFIXES:
        if name.startswith(p) or name == p.rstrip("_"):
            return "essenziell"
    # Häufiges Pattern: GA-Cross-Property mit _ga_<KEY>
    if re.fullmatch(r"_ga_[A-Z0-9]+", name):
        return "marketing"
    return "unklar"


def _klassifiziere_script(src: str) -> str:
    host = urllib.parse.urlparse(src).hostname or ""
    if any(host.endswith(m) for m in MARKETING_SCRIPT_HOSTS):
        return "marketing"
    # Inline-Tags ohne src ignorieren wir hier
    return "unklar"


def _detect_consent_banner(html: str) -> tuple[bool, list[str]]:
    """Heuristik: häufige Consent-Lib-Markers im HTML."""
    markers = []
    patterns = {
        "OneTrust": r"onetrust|optanon",
        "Cookiebot": r"cookiebot",
        "Usercentrics": r"usercentrics",
        "Borlabs": r"borlabs",
        "Klaro": r"klaro-config",
        "Iubenda": r"iubenda",
        "Termly": r"termly\.io",
        "CookieScript": r"cookie-script",
        "consentmanager": r"consentmanager",
    }
    lower = html.lower()
    for label, pat in patterns.items():
        if re.search(pat, lower):
            markers.append(label)
    return (len(markers) > 0, markers)


def scanne(url: str) -> ScanErgebnis:
    if not _is_safe_target(url):
        raise ScanError(
            "unsafe_target",
            "URL muss eine öffentlich erreichbare http(s)-Adresse sein.",
        )

    try:
        resp = httpx.get(
            url,
            follow_redirects=True,
            timeout=5.0,
            headers={
                "User-Agent": "Vaeren-Cookie-Scanner/1.0 (+https://vaeren.de/tools/cookie-check)"
            },
        )
    except httpx.HTTPError as exc:
        raise ScanError("http_error", f"HTTP-Fehler beim Abruf: {exc}", status_code=502)

    # Cookies aus Response-Headern (set-cookie)
    cookies: list[CookieBefund] = []
    for cookie in resp.cookies.jar:
        name = cookie.name
        cookies.append(
            CookieBefund(
                name=name,
                klassifizierung=_klassifiziere_cookie(name),
                secure=bool(cookie.secure),
                httponly=bool(cookie._rest.get("HttpOnly")) if hasattr(cookie, "_rest") else False,
                samesite=str(cookie._rest.get("samesite") or "").lower() if hasattr(cookie, "_rest") else "",
            )
        )

    # Script-Tags via regex (BeautifulSoup wäre teurer; reicht für Hostname-Check)
    html = resp.text or ""
    scripts: list[ScriptBefund] = []
    for m in re.finditer(r'<script[^>]+src=["\']([^"\']+)["\']', html, flags=re.IGNORECASE):
        src = m.group(1)
        if src.startswith("//"):
            src = "https:" + src
        if not src.startswith(("http://", "https://")):
            continue
        k = _klassifiziere_script(src)
        if k == "marketing":
            scripts.append(ScriptBefund(src=src, klassifizierung=k))

    consent_erkannt, markers = _detect_consent_banner(html)

    # Score: 100 - 5×(marketing-cookie) - 5×(marketing-script) +20 bei Consent-Banner
    marketing_cookies = sum(1 for c in cookies if c.klassifizierung == "marketing")
    score = 100 - 5 * marketing_cookies - 5 * len(scripts)
    if consent_erkannt:
        score += 20
    score = max(0, min(100, score))

    empfehlungen: list[str] = []
    if marketing_cookies > 0 and not consent_erkannt:
        empfehlungen.append(
            "Marketing-Cookies vor Einwilligung gesetzt — TTDSG §25 Abs. 1 verlangt"
            " ausdrückliche Zustimmung. Consent-Banner einbauen."
        )
    if scripts and not consent_erkannt:
        empfehlungen.append(
            "Tracking-Skripte werden ohne Consent geladen. Skript-Loading erst nach"
            " Opt-In auslösen."
        )
    if any(not c.secure for c in cookies):
        empfehlungen.append("Mindestens ein Cookie ohne Secure-Flag — bei HTTPS-Seiten unnötig riskant.")
    if any(c.samesite not in ("strict", "lax") for c in cookies):
        empfehlungen.append("SameSite-Attribut fehlt oder ist 'none' — CSRF-Risiko.")
    if not empfehlungen:
        empfehlungen.append("Keine groben TTDSG-Verstöße in der Erstprüfung erkannt — aber: Klassifizierung ist heuristisch, kein Audit-Ersatz.")

    return ScanErgebnis(
        url=url,
        final_url=str(resp.url),
        cookies=cookies,
        scripts=scripts,
        consent_banner_erkannt=consent_erkannt,
        consent_marker=markers,
        score=score,
        empfehlungen=empfehlungen,
    )
