
 # Dunkin Demand Intelligence

 This repository contains the Dunkin Demand Intelligence application — a React + Vite frontend and a Flask backend that provides forecasting, accuracy, approval, and learning endpoints.

 ## Overview

 - Frontend: React + Vite + Tailwind (folder: `frontend/`)
 - Backend: Flask (folder: `backend/`)
 - Database: PostgreSQL (connected via `DATABASE_URL`)

 ## Quickstart (Development)

 Prerequisites:
 - Python 3.12
 - Node 18+
 - PostgreSQL (local or managed)

 Backend

 ```bash
 python -m venv .venv
 .venv\Scripts\Activate.ps1  # Windows PowerShell
 pip install -r backend/requirements.txt
 cd backend
 python -m app
```

 Frontend

 ```bash
 cd frontend
 npm install
 npm run dev
```

 Open `http://localhost:5173` for the frontend and `http://localhost:5000` for the backend.

 ## Environment Variables

 Create a `.env` file or configure your host with these variables:

 - `DATABASE_URL` — PostgreSQL connection string; example:
   `postgresql://username:password@host:5432/database`
 - `VITE_API_URL` — Frontend API base URL; example:
   `https://your-backend-host.com/api/v1`

 ## Important API Endpoints

 - POST `/api/v1/auth/signup` — Create user
 - POST `/api/v1/auth/login` — Login
 - GET `/api/v1/forecast?store_id=1&target_date=YYYY-MM-DD` — Forecast
 - GET `/api/v1/forecast/history?limit=30` — Forecast history
 - GET `/api/v1/forecast/accuracy` — Accuracy metrics
 - GET `/api/v1/forecast/approvals?status=pending` — Approvals
 - GET `/api/v1/forecast/learning/summary` — Learning summary
 - GET `/api/v1/dashboard/daily?store_id=1&date=YYYY-MM-DD` — Daily snapshot

 ## Database: Users Table

 The `users` table stores registered users. The backend uses the following columns when creating users in `backend/models/user_model.py`:

 - `id` (primary key)
 - `name`
 - `email`
 - `password_hash` (bcrypt hashed password)

 ## Deployment Notes (Vercel / Render)

 - Frontend: Vercel. Build command: `cd frontend && npm run build`. Output directory: `frontend/build`.
 - Backend: Render / Railway / Heroku — ensure `DATABASE_URL` is set.

 ## Troubleshooting

 - `Failed to fetch`: verify `VITE_API_URL` is correct and the backend is reachable. Check browser devtools Network tab for the exact URL and response.
 - CORS: the backend enables CORS for `/*` during development. If you see CORS errors, ensure the deployed host allows the frontend origin.

 ## Contributions

 Open PRs for fixes and features. For deployment fixes, include exact build logs and environment variables (do not share secrets).

 ---

 If you want, I can also add a sample SQL seed for creating a test user and automate a small smoke test for signup/login.
