# VittSetu

VittSetu is a hackathon prototype for explainable financial readiness and
lender-safety guidance for credit-invisible workers. It uses **synthetic demo
data only**. It is not a credit score, underwriting system, loan application,
or a fraud-detection service.

## Current milestone

The repository starts with a stateless FastAPI backend that provides:

- three illustrative demo personas;
- a deterministic 0-100 Financial Readiness Score and explanation;
- non-binding product-category guidance;
- an illustrative, dated lender/app registry lookup; and
- a public model card for frontend and judge review.

See [the backend README](backend/README.md) to run the service and
[the frontend handoff brief](frontend-brief/FRONTEND_BRIEF.md) to build a UI
against it.

## Safety boundaries

- Do not add bank credentials, SMS, contacts, call logs, precise location, or
  raw transaction narratives.
- Do not represent any prototype registry entry as an RBI verification.
- Do not display "not found" as fraud or promise credit eligibility, amount,
  price, or approval.
- Do not persist personal data in the initial prototype.
