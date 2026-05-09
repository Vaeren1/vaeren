# GlitchTip-Stack

Self-hosted Sentry-API für Vaeren-Production-Error-Monitoring. Lebt parallel
zum ai-act-Stack auf demselben Server unter `/opt/glitchtip/` und nutzt das
gleiche `caddy-net` für Reverse-Proxy.

## Setup (Reproduzierbar)

1. `mkdir -p /opt/glitchtip && cd /opt/glitchtip`
2. `cp docker-compose.yml /opt/glitchtip/`
3. `python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))" > /opt/glitchtip/.env`
4. `docker compose up -d`  (migrate-Container läuft 1× und exited)
5. `docker network connect caddy-net glitchtip-web`
6. Caddyfile-Block für `errors.app.vaeren.de` aktiv → `caddy reload`
7. Admin-User per `manage.py shell`:
   ```python
   from django.contrib.auth import get_user_model
   U = get_user_model()
   u = U.objects.create_user('konrad@vaeren.de', password='<starkes-pw>',
                              is_staff=True, is_superuser=True)
   ```
8. Org/Project anlegen via Web-UI oder shell, DSN kopieren
9. DSN ins Vaeren `.env.production` als `SENTRY_DSN=...`
10. `./deploy.sh` von Vaeren

## Backup

GlitchTip-Postgres ist NICHT im Vaeren-restic-Backup enthalten. Wenn das
Setup-Reproducible-Sein soll und Issue-History keinen Wert hat → kein
Backup nötig (neuer Setup = leerer Issue-Tracker, weiterhin funktional).
Falls Issue-History wichtig wird (Trend-Analysen): zweites restic-Repo auf
gleicher Storage-Box anlegen, separater pg_dump-Cron für glitchtip-postgres.
