# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm install          # install deps
npm run dev          # dev server at :5173
npm run build        # tsc -b && vite build
npm run lint         # eslint
npm run preview      # preview production build
```

Copy `.env.example` to `.env.local` and set values before running.

## Architecture

This is a single-page React + Vite + TypeScript app. There is **no routing library** — phase transitions are managed entirely by a `phase` state variable in `Curas.tsx`.

### File map

| File | Role |
|---|---|
| `src/Curas.tsx` | Entire application — all components live here as local functions |
| `src/lib/api.ts` | REST client wrapping `fetch`; all calls to the FastAPI backend go through the `api` object |
| `src/types/index.ts` | TypeScript interfaces that mirror CONTRACTS.md Pydantic models — keep in sync |
| `src/config.ts` | Exports `DEMO_MODE` (true when `VITE_DEMO_MODE !== 'false'`) |
| `src/mockData.ts` | Static demo fixtures (unused by Curas.tsx which has its own inline DEMO_* constants) |

### Phase state machine

`Curas()` root component drives the app through five phases via `setPhase(...)`:

```
"list" → "pre" → "during" → "post" → "done"
```

Each phase renders a distinct component (`PatientList`, `PreAppointment`, `DuringAppointment`, `PostAppointment`, `CompletionScreen`). All state (`selectedPatient`, `appointmentId`, `soapNoteId`) is held at the root and passed down as props.

### Demo mode vs. live mode

`DEMO_MODE` (`src/config.ts`) gates every API call. When true, components use inline `DEMO_*` constants and simulate loading with `setTimeout`. When false, they call `api.*` methods and handle errors by showing a warning and falling back to demo data.

The `VITE_APPOINTMENT_ID` env var is used as a hardcoded appointment ID in demo/dev — set it in `.env.local` to avoid `null` appointment IDs when testing against the real backend.

### SSE stream (During Appointment)

`DuringAppointment` opens an `EventSource` to `GET /api/patients/{id}/appointment/stream?token=<jwt>` when recording starts. It listens for `soap_update` events (updates SOAP textarea state) and `done` (closes stream, calls `POST /appointment/end`). The JWT is read from `localStorage.getItem("supabase_token")`.

### API client (`src/lib/api.ts`)

`BASE` defaults to `VITE_API_BASE_URL` (fallback: `http://localhost:8000`). All methods throw on non-2xx responses. Type parameters are currently `any` — tighten to the interfaces in `src/types/index.ts` when implementing a feature.

### Styling

No CSS framework. All styles are inline `style={{}}` objects. Color constants are defined at the top of `Curas.tsx` (e.g. `TEAL`, `AMBER`, `RED`). The `DM Sans` and `DM Mono` fonts are loaded via a Google Fonts `<link>` injected directly in the JSX. One responsive breakpoint at 768px is handled by a `<style>` tag inside each phase component.

## Environment variables

| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | FastAPI backend URL (default `http://localhost:8000`) |
| `VITE_DEMO_MODE` | Set to `'false'` to enable live backend calls (default: demo on) |
| `VITE_APPOINTMENT_ID` | Hardcoded appointment UUID used when selecting a patient in dev |
| `VITE_SUPABASE_URL` | Supabase project URL (for future auth wiring) |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key |
