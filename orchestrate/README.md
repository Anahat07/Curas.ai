# IBM Orchestrate Workflow

See `CONTRACTS.md §6 main_workflow.yaml` for the full state machine spec.

## Setup

1. Log in to IBM Orchestrate
2. Import `workflows/main_workflow.yaml`
3. Set the webhook URL to `https://<render-url>/api/orchestrate/advance-phase`
4. Set the `X-Orchestrate-Secret` header value to match `ORCHESTRATE_SHARED_SECRET` in Render env vars
