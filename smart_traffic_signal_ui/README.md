# Smart Traffic Signal UI

Role-based React + Tailwind dashboard for Smart Traffic Signal Automation.

## Start Backend API

1. Open terminal in the `smart_traffic` folder.
2. Run:

```bash
python api_server.py
```

Backend API runs on `http://127.0.0.1:5000`.

## Start Frontend

1. Open terminal in the `smart_traffic_signal_ui` folder.
2. Run:

```bash
npm install
npm run dev
```

Frontend runs on `http://127.0.0.1:5173`.

## Demo Accounts

- `officer / officer123` -> `TRAFFIC_PERSONNEL`
- `admin / admin123` -> `SYSTEM_ADMIN`
- `viewer / viewer123` -> `VIEW_ONLY`

## Implemented Security/Admin Sections

- Username/password login form.
- Role-based access control in both UI and backend endpoints.
- Menu-based admin screens:
  - System Health
  - Audit Trail
  - Violation Reports
- Direct manipulation operator screen for live intersection controls.
- Open Backend UI button (opens `http://127.0.0.1:5000`).
