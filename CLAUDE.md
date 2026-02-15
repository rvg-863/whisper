# Whisper — E2E Encrypted Messaging Platform

Domain: hush-hush.work

## Dev Commands

```bash
# Start infrastructure
docker compose up -d

# Backend (from whisper/)
source ../myenv/bin/activate
pip install -r server/requirements.txt
cd server && alembic upgrade head
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (from whisper/client/)
npm install
npm run dev

# Run alembic migration
cd server && alembic revision --autogenerate -m "description"
cd server && alembic upgrade head
```

## Architecture

- **Backend:** FastAPI + async SQLAlchemy + PostgreSQL 16
- **Real-time:** WebSockets with Redis pub/sub
- **Storage:** MinIO (S3-compatible) for file uploads
- **Auth:** JWT + Argon2 password hashing
- **Encryption:** Signal Protocol (X3DH + Double Ratchet) for E2E encryption
- **Frontend:** React + TypeScript + Vite + Zustand

## Project Structure

```
whisper/
├── server/          # FastAPI backend
│   ├── models/      # SQLAlchemy models
│   ├── routes/      # API endpoints
│   ├── services/    # Business logic
│   ├── ws/          # WebSocket handlers
│   └── alembic/     # Database migrations
├── client/          # React frontend
│   └── src/
│       ├── api/         # API client
│       ├── components/  # React components
│       ├── crypto/      # Signal Protocol + file encryption
│       ├── hooks/       # Custom hooks
│       └── stores/      # Zustand stores
└── docker-compose.yml
```
