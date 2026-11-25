# Portals

Angular apps for Council of Ancients.

| App | Path | Port | Notes |
|-----|------|------|-------|
| Customer portal | [`customer-portal/`](customer-portal/) | `4200` | Sign-in, pack chrome, chamber, settings → deliberate API |
| Admin portal | `admin-portal/` (later) | `4201` | KB ingest / schema management (not shipped yet) |

## Local scripts

```bash
npm run local:portals:all:start
npm run local:portals:all:status
npm run local:portals:all:stop
```

Customer is started today; admin is wired in the scripts and skipped until the folder exists.

See [`customer-portal/README.md`](customer-portal/README.md) for the open-source UI stack.
