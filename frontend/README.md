# Frontend Configuration

## API Base URL

The frontend reads the backend URL from `VITE_API_BASE_URL`.

1. Copy `.env.example` to `.env`.
2. Set the backend endpoint:

```env
VITE_API_BASE_URL=http://localhost:8000
```

If this value is not set, the app defaults to `http://localhost:8000`.
