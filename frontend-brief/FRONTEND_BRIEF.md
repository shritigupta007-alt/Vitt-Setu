# VittSetu frontend handoff

Build a React + Vite + TypeScript frontend around the FastAPI service in
`../backend`. The OpenAPI contract served at `/openapi.json` is authoritative.
Do not modify backend schemas, score calculation, lender-status labels, safety
copy, or the illustrative registry data from the frontend.

## User flow

1. **Start**: Select one of the three synthetic demo personas. Clearly label
   every persona as demo data.
2. **Consent**: State purpose, five feature categories, session-only browser
   retention, and a clear-session control. Keep Continue disabled until the
   user checks the consent acknowledgement.
3. **Summary**: Display derived features only, with units and visible markers
   for unavailable data. Do not add raw transaction input.
4. **Result**: Call `POST /api/score`. Show score, band, evidence-confidence
   label, three contribution reasons, one product category, two tips, and all
   limitations. Score output must never imply approval.
5. **Lender check**: Call `GET /api/lenders/search?q=`. Render the status
   exactly as supplied, along with registry provenance, evidence, required
   next action, and safety checklist.

## Required UI behaviour

- Use React Router for deep links between flow steps.
- Store persona choice and consent in `sessionStorage` only.
- A Clear Session action removes all VittSetu keys and returns to Start.
- Support loading, validation, no-results, and API-error states.
- Use accessible semantic controls, visible keyboard focus, and text
  equivalents for any score visualization.
- Prioritize a 360 px wide mobile viewport; core copy must be complete in
  simple English. Hindi is a later enhancement.

## API base URL

Use `VITE_API_BASE_URL`, defaulting to `http://127.0.0.1:8000`. Do not embed a
production URL in source code.

## Acceptance path

Radha -> consent -> summary -> result -> search `Udyam Sathi Demo` -> see
`LISTED_ASSOCIATION` plus its caveat -> clear session. This must work on a
mobile viewport in under 90 seconds.

## Safety checklist copy

Show these independent checks for every lender result:

- Is anyone demanding an upfront fee before funds are disbursed?
- Are the APR, Key Fact Statement, and repayment schedule missing or unclear?
- Does the app request permissions that do not fit its purpose?
- Is payment requested to a personal account or unrelated UPI ID?
- Is anyone using coercive, threatening, or harassing messaging?

If any answer is Yes, emphasize: **Stop, preserve evidence, and use official
support or reporting routes.** This is a conduct concern, not a fraud verdict.
