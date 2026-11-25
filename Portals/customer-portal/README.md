# Council of Ancients — Customer Portal

Angular 19 customer portal for topics, chamber chat, and settings that merge into `coa_agents_api` deliberate `ctx_data`.

## Open-source UI stack

| Library | Use |
|---------|-----|
| [Angular](https://angular.dev) 19 | App framework |
| [PrimeNG](https://primeng.org) + [@primeng/themes](https://www.npmjs.com/package/@primeng/themes) | Enterprise components (buttons, tables, inputs, toasts patterns) |
| [PrimeIcons](https://primeng.org/icons) | Icon set for PrimeNG controls |
| [Bootstrap](https://getbootstrap.com) 5 | Grid / utility layout |
| [ng-bootstrap](https://ng-bootstrap.github.io) | Bootstrap Angular widgets (available) |
| [Bootstrap Icons](https://icons.getbootstrap.com) | Left-nav and chrome icons |
| [Font Awesome](https://fontawesome.com) (`@fortawesome/angular-fontawesome`) | Brand / hero marks |
| [Animate.css](https://animate.style) | Entrance motion |
| [ngx-cookie-service](https://www.npmjs.com/package/ngx-cookie-service) | Auth token stub cookie |
| [Google Fonts](https://fonts.google.com) Syne + Source Sans 3 | Display / body typography |
| [Unsplash](https://unsplash.com) photos | Auth / overview atmosphere imagery |

## Design direction

Teal + copper professional palette (not gray / black / washed-light admin). Chat-first shell: top topic bar, topic left nav, chamber canvas, collapsible sources rail.

## Run

```bash
cd Portals/customer-portal
npm start
# http://localhost:4200
```

From repo root (customer now; admin later on `:4201`):

```bash
npm run local:portals:all:start
npm run local:portals:all:status
npm run local:portals:all:stop
```

Sign up locally (stub auth until `coa_auth_api`). Chamber calls `http://localhost:8090/v1/council/deliberate` when agents API is up; otherwise shows an offline preview reply.

## Settings merge

`global → topic → chat window` → sent as `ctx_data.settings` with topic id, left nav, domain options, and recent turns.
