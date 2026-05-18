# RRL Nature Crust — New Project Spec (for fresh fork)

> **For the new chat/agent who picks this up:** You are starting a **new
> project**. Use this file as the source of truth. Do NOT depend on
> anything in the "RRL Palm Altezze" CRM running at https://rrlcrm.com —
> it's a separate deployment. The customer wants this to be a **standalone
> clone** of the existing RRL CRM codebase, rebranded.

---

## 1. Product Identity

| Field | Value |
|---|---|
| **Product name** | RRL Nature Crust |
| **Tagline / footer credit** | powered by Marketly.tech |
| **Project name (used in documents)** | RRL Nature Crust (replaces "RRL PALM ALTEZZE" everywhere in PDFs) |
| **Production domain (target)** | naturecrust (final URL TBD — user will confirm. Assume `naturecrust.com` or `naturecrust.rrlbuildersanddevelopers.com` placeholder) |
| **Theme** | Same dark + gold as the original CRM. Do NOT change colors, fonts, or layout. |
| **RRL Group logo** | Same gold "RRL GROUP" logo — keep as is. |
| **RRL Palm Altezze logo / project artwork** | **REPLACE** with the new Nature Crust project artwork (user will supply). For now, use a placeholder + leave a TODO comment. |

---

## 2. Scope for v1 (MVP — first deploy only)

Only these 3 modules must work in the first cut:

1. **Public Lead Form** (`/lead-form` route + public link with shareable URL)
2. **Leads list** (admin dashboard side) — list, view, qualify, reject, convert to customer
3. **Customers** module — list + customer detail page (Property & Pricing, Payment Tracking, Documents, Communication tabs)

**Out of scope for v1 (defer):** Dashboard metrics, Document Templates Editor, Reports, Email Tracking inbox, Activity Logs, Settings → Payment Stages, Bulk import/export, Disbursement slab cards.

> The full CRM has these modules; keep their routes in code but mark them
> as `coming-soon` placeholders OR hide their nav items behind a feature
> flag. The user explicitly said: *"As of now I just need lead form link
> and leads, customers."*

---

## 3. Footer / Letterhead Constants

Update these constants in `/app/backend/documents/templates/noc_templates.py`
and any other template that uses them. Get the exact strings from the user
**before generating real customer PDFs**.

```python
# /app/backend/documents/templates/noc_templates.py
RRL_ADDRESS = "4th Floor, RRL TOWERS, Sompura Gate, Sarjapura Road, Bengaluru - 562125"  # KEEP SAME — corporate address
RRL_WEBSITE = "www.rrlbuildersanddevelopers.com"  # confirm with user
RRL_EMAIL   = "crm@rrlbuildersanddevelopers.com"  # confirm — may stay the same
RRL_RERA    = "<NEW_RERA_NUMBER_TO_BE_CONFIRMED>"  # ⚠️ DIFFERENT from Palm Altezze. ASK USER.

# Site address — different from Palm Altezze
NATURE_CRUST_SITE_ADDRESS = "<NEW_SITE_ADDRESS — ASK USER>"
```

Replace all hardcoded `"RRL Palm Altezze"` / `"RRL PALM ALTEZZE"` / Palm
Altezze site address (`SY NO: 73/6, Janthagondanahalli Village...`) with
the new Nature Crust values in:

- `/app/backend/documents/templates/noc_templates.py` (HDFC / BOB / TATA bodies)
- `/app/backend/documents/templates/sales_agreement_html.py`
- `/app/backend/documents/templates/sales_agreement_template.py`
- `/app/backend/documents/templates/allotment_letter.py`
- `/app/backend/documents/templates/price_breakup.py`
- `/app/backend/documents/templates/cost_breakup.py`
- `/app/backend/documents/templates/demand_letter.py`
- `/app/backend/documents/templates/payment_schedule.py`
- `/app/backend/documents/templates/payment_receipt.py`
- `/app/backend/documents/templates/booking_form.py`
- `/app/backend/documents/templates/email_templates.py`

> **TIP**: `grep -rn "Palm Altezze\|PALM ALTEZZE\|Janthagondanahalli" /app/backend` to find them all.

Also "powered by Marketly.tech" must appear:
- In the **frontend footer** of every page (small grey text, centered, like a SaaS footer).
- In the **footer band** of every PDF — append at the very bottom-right.

---

## 4. Frontend Rebranding

| Place | Current | Change to |
|---|---|---|
| Browser tab title | "RRL CRM" | "RRL Nature Crust" |
| Top-left logo + product name (sidebar header) | "RRL CRM" | "RRL Nature Crust" |
| Login page hero | "RRL Builders" / "Streamline Your Customer Management" | "RRL Nature Crust" + same hero copy |
| Login page subtitle / footer | "Post-Sales CRM" | "Post-Sales CRM · powered by Marketly.tech" |
| Public lead-form page header | RRL Palm Altezze logo + name | RRL Nature Crust logo + name |
| Every page footer | (none) | "© 2026 RRL Builders and Developers Pvt. Ltd. · powered by Marketly.tech" |
| Email "From" name | RRL Builders | RRL Nature Crust |
| Welcome email body | references Palm Altezze | references Nature Crust |

Files to touch (most likely):
- `/app/frontend/public/index.html` (title)
- `/app/frontend/src/layouts/*` or `Sidebar.jsx` (sidebar header)
- `/app/frontend/src/pages/LoginPage.js`
- `/app/frontend/src/pages/PublicLeadForm.js` (or whatever the public form route is)
- `/app/frontend/src/components/Footer.jsx` (create if missing — add "powered by Marketly.tech")

---

## 5. Admin Credentials (seed on first boot)

```python
# In /app/backend/auth/seed.py (or wherever admin is seeded)
DEFAULT_ADMIN_EMAIL    = "crm@rrlbuildersanddevelopers.com"  # SAME as Palm Altezze
DEFAULT_ADMIN_PASSWORD = "#Nature123"                         # NEW
```

> ⚠️ **Same email, different password** — confirmed by user. Make sure
> seed is **idempotent** (don't overwrite an existing user, only create if
> missing). Document the credential in `/app/memory/test_credentials.md`
> of the new project.

---

## 6. Database

- **Fresh, empty MongoDB.** Do NOT carry over any Palm Altezze data.
- Keep `DB_NAME` in `/app/backend/.env` — Emergent platform provisions a
  separate DB automatically for a forked project.
- The auto-seed should ONLY create:
  - 1 admin user (above)
  - The default payment schedule template (DEFAULT_PAYMENT_SCHEDULE — keep as is, customer can edit later)
  - The canonical banks registry (`/app/backend/utils/banks.py` — keep as is)
- DO NOT seed dummy customers/leads for prod. Optional: seed a single test customer behind a `SEED_DEMO=true` env var.

---

## 7. Public Lead Form

This is the **most important v1 feature** — it's the shareable link the
sales team will distribute.

- Route: `/lead/<slug>` or `/lead-form/<project-slug>` (keep same path as
  Palm Altezze for simplicity, customer never sees it duplicated).
- Header: "RRL Nature Crust" + Nature Crust artwork.
- Fields: same as Palm Altezze public form (applicant, co-applicant, contact, address, document uploads).
- On submit → creates a Lead in MongoDB with `project: "RRL Nature Crust"`, status `pending_approval`.
- Shareable URL: `https://<naturecrust-domain>/lead-form` (or signed slug if Palm Altezze does that).

Verify after first deploy: open the public URL in incognito, fill the form, confirm the lead shows up in admin's Leads list.

---

## 8. Modules to KEEP visible in v1

- Sidebar nav: Dashboard (skeleton), Leads, Customers, **(hide)** Payments / Documents / Payment Tracking / Email Tracking / Reports / Settings.
- Alternatively, keep them but show a "Coming Soon" empty state inside each tab so the new agent doesn't need to rip out routing.

The handoff agent should ask the customer which approach they prefer.

---

## 9. Step-by-step plan for the new chat's agent

After the platform fork, the new agent should:

1. **Day 1 — Rebrand**:
   - Replace all "Palm Altezze" strings (use `grep -rn "Palm Altezze\|PALM ALTEZZE" /app`).
   - Replace all "RRL CRM" product strings → "RRL Nature Crust".
   - Update browser tab title, sidebar header, login page.
   - Add "powered by Marketly.tech" footer everywhere.
   - Reset seed admin password to `#Nature123`.
   - Sanity-check: yarn build, supervisor restart, login works.

2. **Day 1 — DB reset**:
   - Confirm fresh DB on the new preview env.
   - Run admin seed → confirm only 1 user exists.

3. **Day 1 — Site/RERA constants**:
   - Ask user for exact new site address + RERA number.
   - Update template constants. Re-run the letterhead regression test
     (`/app/backend/tests/test_letterhead_iteration36.py`) → all 13 pass.

4. **Day 2 — Scope MVP**:
   - Decide with user: hide unused modules OR show "Coming Soon" placeholders. Implement that.
   - Smoke-test public lead form end-to-end.
   - Generate one HDFC NOC for a test customer to verify branding came through.

5. **Day 2 — Deploy**:
   - User triggers deploy via Emergent platform.
   - Confirm production URL serves Nature Crust branding.

---

## 10. What stays the SAME (do NOT touch)

- `DOCUMENT_FORMAT_REFERENCE.md` rules — dark band, gold accents, footer band, etc.
- All Python module structure under `/app/backend/`.
- All React component structure under `/app/frontend/src/`.
- Banks registry (`utils/banks.py`).
- Authentication flow (JWT + bcrypt).
- DEFAULT_PAYMENT_SCHEDULE (the 13-milestone template).
- RRL Group logo (gold "RRL GROUP" base64 PNG in `/app/backend/documents/templates/logo_data.py`).
- All bug-fixes shipped to Palm Altezze (Payment Schedule auto-gen, Interest Amount field, NOC dark-band format, Cost Breakup logo).

---

## 11. Reference: existing Palm Altezze test credentials

(for the cloning agent to compare against — do not seed these on Nature Crust)

```
Admin (Palm Altezze prod): crm@rrlbuildersanddevelopers.com / #RRLnew2026
Accounts (Palm Altezze):   accounts@rrlbuilders.com / accounts123
Test customer (Palm Altezze): Ramya test lead, id=6d902613-5106-4294-bc3e-b907f85127f7
```

```
Admin (Nature Crust — NEW): crm@rrlbuildersanddevelopers.com / #Nature123
```

---

## 12. Open questions for the new chat to ask the user up-front

1. Exact site address for Nature Crust project (used in all PDFs).
2. Exact RERA number for Nature Crust project.
3. Final production domain (`naturecrust.com`? `naturecrust.rrlbuildersanddevelopers.com`?).
4. Nature Crust project logo / hero image — please upload PNG/SVG.
5. Welcome email body — same template with project name swapped, or different copy?
6. Hide unused modules in sidebar, or show "Coming Soon" placeholders?

---

**Last updated**: 2026-02-15 by Palm Altezze chat agent E1.
**Hand off to**: New "RRL Nature Crust" chat (fork from this repo).
