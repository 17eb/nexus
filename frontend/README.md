# BPTM frontend

Vite + React 18 + TypeScript + Tailwind v4. TanStack Query for server
state, i18next for i18n (en, ko, ja, en-ko, en-ja), dark/light theming
via Tailwind's `class` strategy and CSS variables in `src/index.css`.

```bash
npm install
npm run dev      # http://localhost:5173, proxies /api to Django on :8000
npm run build
```

In dev, `vite.config.ts` proxies `/api` to `http://localhost:8000` so
the browser sees everything as same-origin — no CORS config needed.
From the repo root, `make dev` runs this alongside `manage.py runserver`.
