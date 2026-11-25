# Portals

Angular apps for Council of Ancients.

| App | Path | Port | Notes |
|-----|------|------|-------|
| Customer portal | [`customer-portal/`](customer-portal/) | `4200` | Sign-in, topic chrome, chamber, settings → deliberate API |
| Admin portal | [`admin-portal/`](admin-portal/) | `4201` | Knowledge sources / ingest ops → `coa_admin_api` only |

## Local scripts

```bash
npm run local:portals:all:start
npm run local:portals:all:status
npm run local:portals:all:stop
```

Admin UI never calls Airflow or Knowledge API directly.

See [`customer-portal/README.md`](customer-portal/README.md) and [`admin-portal/README.md`](admin-portal/README.md).
