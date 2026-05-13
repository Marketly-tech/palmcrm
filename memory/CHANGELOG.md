# CHANGELOG

## 2026-02 — Payment Schedule Document Auto-Generation Fix
- **Bug fixed**: Generating a "Payment Schedule" document from Customer Profile → Documents tab failed with a generic "Failed to generate document" toast for any customer that had not yet auto-generated the schedule items.
- **Backend**: `documents/generators.py::_render_payment_schedule` now auto-creates the schedule from `DEFAULT_PAYMENT_SCHEDULE` (13 milestones) and persists it on the fly if missing. Same behavior also applied to `POST /api/documents/generate-payment-schedule-pdf/{customer_id}` (now routes through `render_document_content`).
- **Frontend**: `CustomerDetailPage.js` onGenerateDocument now surfaces backend `error.response.data.detail` in the toast instead of swallowing it, so future failures are diagnosable end-to-end.
- Verified via curl for both Ramya (existing schedule) and NANDAKUMAR (no schedule) — both return `Document generated` with full HTML content.
