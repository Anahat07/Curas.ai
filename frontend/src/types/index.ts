// Spec: CONTRACTS.md §3 Pydantic Models
// Mirror every model here as a TypeScript interface.
// Keep in sync with any contract changes — post in team channel first.

export type WorkflowState =
  | "pending"
  | "brief_ready"
  | "in_appointment"
  | "appointment_complete"
  | "form_ready"
  | "completed";

export type AppointmentPhase =
  | "pre_appointment"
  | "during_appointment"
  | "post_appointment"
  | "completed";

export type FormType = "T2201";

// Add remaining interfaces per CONTRACTS.md §3
