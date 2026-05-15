# DOCUMENT FORMAT REFERENCE — RRL CRM

> **READ THIS BEFORE TOUCHING ANY PDF TEMPLATE.**
> This file is the **source of truth** for how every customer-facing document
> must look. Each session/agent may forget visual decisions — this file
> carries them forward. If a user asks for a format change, update this file
> in the SAME commit as the code change.

---

## 1. Builder NOC (HDFC / Bank of Baroda / TATA Capital)

**File**: `/app/backend/documents/templates/noc_templates.py`
**Approved by user on**: Apr 2026 (yesterday's working PDF — see analysis below)
**Last restored to spec on**: Feb 15, 2026

### Layout (top → bottom)

| Block | Position | Style |
|---|---|---|
| **Header band** | Top, full bleed (left/right edges) | Background `#1A1A1A` (dark charcoal). ~18px padding. Logo on left, company text on right. |
| Logo | Inside header band, left | Gold "RRL GROUP" logo, ~70px wide. Embedded base64 PNG via `get_logo_img_tag(70)`. |
| Company name | Inside header band, right | "RRL Builders and Developers Pvt. Ltd." — 18px, bold, **WHITE** color on dark band. |
| Tagline | Below company name | "Beyond Homes. A Lifestyle" — 11px, italic, **gold `#D4AF37`**. |
| **Doc title** | Centered, below header | "BUILDER NOC — \<BANK NAME\>" — 15px, bold, uppercase, with `#D4AF37` underline. Bank name = "HDFC Bank" / "Bank of Baroda" / "TATA Capital". |
| Date | Right-aligned | "Date: DD/MM/YY" |
| To, addressee | Left-aligned | Bank name + bank address |
| "Dear Sir," / "Dear Sir / Madam," | Left | |
| Body paragraphs | Left, justified | Property + financial details |
| Signature | Left | "For RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED" + "Authorized Signatory" |
| **Footer band** | Fixed at bottom, full bleed | Background `#F5F5F5`, top border `#D4AF37`. Two lines: (1) address + website + email; (2) RERA + Document Generated date + Ref. Separators are gold `\|` pipes. |

### Footer band content (exact text)

```
4th Floor, RRL TOWERS, Sompura Gate, Sarjapura Road, Bengaluru - 562125 | www.rrlbuildersanddevelopers.com | crm@rrlbuildersanddevelopers.com
RERA: PRM/KA/RERA/1251/308/PR/141025/008167 | Document Generated: DD/MM/YY | Ref: RRL-XXXXX
```

Constants live in `noc_templates.py`:
```python
RRL_ADDRESS = "4th Floor, RRL TOWERS, Sompura Gate, Sarjapura Road, Bengaluru - 562125"
RRL_WEBSITE = "www.rrlbuildersanddevelopers.com"
RRL_EMAIL = "crm@rrlbuildersanddevelopers.com"
RRL_RERA = "PRM/KA/RERA/1251/308/PR/141025/008167"
```

### Page setup
- `@page { size: A4; margin: 0 20mm 30mm 20mm; }` — zero top margin so the header band touches the page edge; 30mm bottom margin reserved for the fixed footer band.

### Reference asset
- **User-approved PDF (yesterday's working version)**: `RRL_Noc_Hdfc_SOVARAJ_PRUSTY (4).pdf`
- Analysis snapshot: see git commit on Feb 15, 2026 — `analyze_file_tool` output.

### Do NOT
- Do NOT replace the dark header band with a white-background, bordered "letterhead".
- Do NOT drop the footer band.
- Do NOT change the gold accent color (`#D4AF37`).
- Do NOT change the company contact constants without explicit user approval.

---

## 2. Other documents (snapshot)

| Doc | File | Has letterhead? | Notes |
|---|---|---|---|
| Sales Agreement | `templates/sales_agreement_html.py` | Yes (built-in) | Long form, uses `format_applicant_block` |
| Allotment Letter | `templates/allotment_letter.py` | Yes (gold border) | |
| Price Breakup | `templates/price_breakup.py` | Yes (gold border, logo left) | Interest Amount row added Feb 2026 (post-GST) |
| Cost Breakup | `templates/cost_breakup.py` | **Yes — restored Feb 15, 2026** (logo was missing before) | |
| Demand Letter | `templates/demand_letter.py` | Yes | Uses payment_stage settings |
| Payment Schedule | `templates/payment_schedule.py` | Yes | Auto-generates 13 milestones if missing (Feb 2026 fix) |
| Payment Receipt | `templates/payment_receipt.py` | Yes | Auto receipt-number `PAR-XXX` |
| NOC (HDFC/BOB/TATA) | `templates/noc_templates.py` | **Yes — restored Feb 15, 2026** (dark band + footer band) | |

---

## 3. Letterhead helpers (per template)

NOCs use `noc_templates._letterhead_html()` / `_letterhead_styles()` / `_footer_band_html()` / `_doc_title_html()`.

> **TODO (recommended, not done yet)**: Promote these helpers to
> `documents/templates/common.py` so ALL templates share one letterhead
> implementation. Currently each template re-implements its own header,
> which is the root cause of "letterhead silently dropped after deploy"
> regressions. See `/app/test_reports/iteration_36.json` action items.

---

## 4. Regression-prevention test

`/app/backend/tests/test_letterhead_iteration36.py` enumerates **all 10 doc
types** and asserts each rendered HTML contains:
1. The base64 RRL logo prefix `data:image/png;base64,iVBOR`
2. The company name substring `RRL Builders and Developers`
3. The downloaded PDF starts with `%PDF-` and is `> 50KB`

**Run before every deploy**:
```bash
cd /app/backend && python -m pytest tests/test_letterhead_iteration36.py -v
```

If any test fails, **do not deploy** — the regression must be fixed first.

For NOC-specific format (dark band + footer band), see
`tests/test_noc_format_iteration37.py` (if/when added).

---

## 5. How to update this file

When a user approves a new visual format:
1. Add a new section here describing the exact layout.
2. Attach the approved reference PDF URL or filename.
3. Update the relevant template in `/app/backend/documents/templates/`.
4. Add/update the regression test.
5. Commit all three together with a message like:
   `docs(format): approved <doc_type> layout — <user>`.

This keeps the visual contract explicit across agent sessions so
"yesterday's PDF" never gets accidentally redesigned.
