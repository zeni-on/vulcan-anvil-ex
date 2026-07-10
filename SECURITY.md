# Security Policy

Vulcan-Anvil Ex is experimental software. The Dashboard reads local project documents and can write comment sidecars or open local files, so it must be treated as a local development tool rather than a network service.

## Supported Version

Security fixes are applied to the latest tagged release and the current `main` branch. Older experimental releases are not maintained separately.

## Dashboard Safety Defaults

- `npm run dev` and `npm start` bind to `127.0.0.1` only.
- Remote hosts and cross-origin write requests are rejected unless `VULCAN_DASHBOARD_ALLOW_REMOTE=1` is explicitly set.
- Set `VULCAN_DASHBOARD_TOKEN` to require a token. Open `http://127.0.0.1:3001/?token=<value>` once to establish the local HttpOnly session cookie, or send the token in `X-Vulcan-Dashboard-Token` for API access.
- Set `VULCAN_DASHBOARD_ALLOWED_ROOTS` to an OS path-delimiter-separated allowlist of directories that may be registered as local projects.
- Do not enable remote access on an untrusted network. A reverse proxy, TLS, and an external authentication layer are required for any non-local deployment.

## Reporting a Vulnerability

Do not include secrets, customer data, or exploit payloads in a public issue. Use GitHub's private vulnerability reporting for this repository when available. Include the affected version, reproduction steps, impact, and the smallest safe proof of concept.

Security reports are acknowledged on a best-effort basis because the project is experimental and has no commercial support SLA.
