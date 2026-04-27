# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm install
npm run dev       # dev server at :5173
npm run build     # tsc -b && vite build
npm run lint      # eslint
npm run preview   # preview production build
```

Copy `.env.example` to `.env.local` and set values before running. There is no test suite.

## Architecture

Single-page React + Vite + TypeScript app. No routing library — phase transitions are driven by a `phase` state variable in `Curas.tsx`.

### File map

| File | Role |
|---|---|
| `src/Curas.tsx` | Entire application — root `Curas()` component + all phase components as non-exported local functions |
| `src/lib/api.ts` | REST client; all backend calls go through the `api` object exported from here |
| `src/types/index.ts` | TypeScript interfaces mirroring CONTRACTS.md Pydantic models — keep in sync with backend |
| `src/config.ts` | Exports `DEMO_MODE = VITE_DEMO_MODE !== 'false'` (default true) |
| `src/mockData.ts` | Static fixtures — **not used by `Curas.tsx`**, which has its own inline `DEMO_*` constants |
| `src/App.tsx` | Thin shell that renders `<Curas />` — no logic here |

### Phase state machine

`Curas()` holds all shared state (`selectedPatient`, `appointmentId`, `soapNoteId`) and drives five phases:

```
"list" → "pre" → "during" → "post" → "done"
```

Each phase renders a distinct component defined locally in `Curas.tsx`: `PatientList`, `PreAppointment`, `DuringAppointment`, `PostAppointment`, `CompletionScreen`.

### Patient type duplication

`src/types/index.ts` exports a `Patient` interface mirroring the backend. `Curas.tsx` re-declares a **local** `Patient` that extends it with UI-only display fields (`apptTime`, `apptType`, `lastVisit`). These extra fields come from demo data only — the real API doesn't return them.

### Demo mode vs. live mode

`DEMO_MODE` is checked inline at every API call site. In live mode, errors fall back to demo data silently (with an amber warning banner), so the UI never hard-blocks on backend failures. The `VITE_APPOINTMENT_ID` env var overrides the appointment ID in dev so `null` IDs don't break scribe flows when testing against a real backend.

### Live scribe flow (During Appointment)

The SSE stream is opened **only after** recording stops and both upload steps succeed:
1. `POST /api/patients/{id}/appointment/upload-audio` → returns `audio_file_path`
2. `POST /api/patients/{id}/appointment/start` with that path → triggers Whisper on the backend
3. `EventSource` opens to `GET /api/patients/{id}/appointment/stream?appointment_id=...&token=...`

JWT for SSE auth is read from `localStorage.getItem("supabase_token")`. The `done` SSE event triggers `POST /appointment/end` to finalise and persist the SOAP note.

### API client (`src/lib/api.ts`)

`BASE` defaults to `VITE_API_BASE_URL` (fallback `http://localhost:8000`). Auth header is injected from `localStorage.getItem("supabase_token")` on every call. All methods throw on non-2xx. Return types are currently `any` — tighten to the interfaces in `src/types/index.ts` when implementing new features.

### Styling

No CSS framework. All styles are inline `style={{}}` objects. Color constants (`TEAL`, `AMBER`, `RED`, etc.) are defined at the top of `Curas.tsx`. Fonts (`DM Sans`, `DM Mono`) are loaded via a Google Fonts `<link>` rendered in JSX. One responsive breakpoint at 768px, handled by a `<style>` tag inside each phase component.

## Environment variables

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | FastAPI backend URL (default `http://localhost:8000`) |
| `VITE_DEMO_MODE` | Set to `'false'` to enable live backend calls (default: demo on) |
| `VITE_APPOINTMENT_ID` | Hardcoded appointment UUID for dev/demo when selecting a patient |
| `VITE_SUPABASE_URL` | Supabase project URL |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key |
