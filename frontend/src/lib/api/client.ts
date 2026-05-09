/**
 * Vaeren-API-Client.
 *
 * - Session-Cookie-Auth (HTTP-only, von Django gesetzt). KEIN JWT.
 * - CSRF: vor jedem unsicheren Request einmal `/api/auth/csrf/` ziehen,
 *   Token cachen, in `X-CSRFToken`-Header setzen.
 * - `credentials: "include"` damit der Cookie domain-übergreifend
 *   (Vite-Proxy → Django) mitgeschickt wird.
 */

let csrfToken: string | null = null;

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown) {
    super(`API ${status}`);
    this.status = status;
    this.body = body;
  }
}

async function getCsrfToken(force = false): Promise<string> {
  if (csrfToken && !force) return csrfToken;
  const res = await fetch("/api/auth/csrf/", { credentials: "include" });
  if (!res.ok) {
    throw new ApiError(res.status, await safeBody(res));
  }
  const data = (await res.json()) as { csrf_token: string };
  csrfToken = data.csrf_token;
  return csrfToken;
}

export function _resetCsrfCacheForTests(): void {
  csrfToken = null;
}

async function safeBody(res: Response): Promise<unknown> {
  try {
    return await res.json();
  } catch {
    return await res.text();
  }
}

export interface ApiRequestInit extends Omit<RequestInit, "body"> {
  json?: unknown;
}

export async function api<T>(
  path: string,
  init: ApiRequestInit = {},
): Promise<T> {
  const method = (init.method ?? "GET").toUpperCase();
  const headers = new Headers(init.headers);

  let body: BodyInit | undefined;
  if (init.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(init.json);
  }

  if (method !== "GET" && method !== "HEAD" && method !== "OPTIONS") {
    headers.set("X-CSRFToken", await getCsrfToken());
  }

  const res = await fetch(path, {
    ...init,
    method,
    headers,
    body,
    credentials: "include",
  });

  if (!res.ok) {
    throw new ApiError(res.status, await safeBody(res));
  }
  if (res.status === 204) return undefined as T;
  const ct = res.headers.get("content-type") ?? "";
  if (ct.includes("application/json")) {
    return (await res.json()) as T;
  }
  return (await res.text()) as unknown as T;
}
