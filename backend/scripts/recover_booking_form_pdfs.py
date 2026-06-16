"""One-time recovery script — pulls the originally-sent Booking Form Preview PDFs
from Resend's storage and locks them in as immutable attachments on the
matching customer records.

This compensates for the fact that, historically, the auto-welcome email path
generated PDFs in memory and discarded them — so the customer record is now
the only place the *truly original* attachment can be re-anchored.

Idempotent: skips customers that already have a recovered PDF (i.e.
``original_booking_form_pdf_b64`` is non-empty).

Usage
-----
Requires a Resend FULL-ACCESS API key (not the send-only key in backend/.env).
Pass it via env var ``RESEND_RECOVERY_API_KEY`` or as the first CLI arg.

    cd /app/backend
    RESEND_RECOVERY_API_KEY="re_xxxx" python -m scripts.recover_booking_form_pdfs
    # or:
    python -m scripts.recover_booking_form_pdfs re_xxxx
"""
from __future__ import annotations

import asyncio
import base64
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load /app/backend/.env regardless of where the script is invoked from
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

RESEND_API_BASE = "https://api.resend.com"
WELCOME_SUBJECT_HINTS = ("welcome", "booking confirmation")
BOOKING_PDF_FILENAME_PREFIX = "RRL_BookingFormPreview_"


def _list_sent_emails(api_key: str, limit: int = 100) -> list[dict]:
    """List all sent emails accessible to this API key."""
    r = requests.get(
        f"{RESEND_API_BASE}/emails",
        headers={"Authorization": f"Bearer {api_key}"},
        params={"limit": limit},
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("data", [])


def _list_attachments(api_key: str, email_id: str) -> list[dict]:
    r = requests.get(
        f"{RESEND_API_BASE}/emails/{email_id}/attachments",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=20,
    )
    if r.status_code != 200:
        return []
    return r.json().get("data", [])


def _download_pdf_bytes(download_url: str) -> bytes | None:
    r = requests.get(download_url, timeout=60)
    if r.status_code != 200:
        return None
    return r.content


def _is_welcome_subject(subject: str) -> bool:
    s = (subject or "").lower()
    return any(h in s for h in WELCOME_SUBJECT_HINTS)


async def main(api_key: str) -> None:
    mongo_url = os.environ["MONGO_URL"]
    db_name = os.environ["DB_NAME"]
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    print("\n── RRL Builders Booking-Form PDF Recovery ──")
    print(f"Mongo: {db_name}")

    # Build customer email → customer doc lookup (lowercase, trimmed)
    customers_by_email: dict[str, dict] = {}
    async for c in db.customers.find({}, {"_id": 0, "id": 1, "name": 1, "email": 1, "original_booking_form_pdf_b64": 1}):
        em = (c.get("email") or "").strip().lower()
        if em:
            customers_by_email[em] = c
    print(f"Customers with email on file: {len(customers_by_email)}")

    # Fetch sent emails
    emails = _list_sent_emails(api_key)
    print(f"Sent emails accessible via Resend: {len(emails)}")

    # Group emails per recipient — keep the OLDEST welcome per customer
    # (because that's the original "Day 1" send).
    candidates_by_recipient: dict[str, dict] = {}
    for e in emails:
        if not _is_welcome_subject(e.get("subject", "")):
            continue
        to_list = e.get("to") or []
        if not to_list:
            continue
        to = (to_list[0] or "").strip().lower()
        existing = candidates_by_recipient.get(to)
        # Resend dates are ISO strings — lexicographic compare works
        if not existing or e["created_at"] < existing["created_at"]:
            candidates_by_recipient[to] = e
    print(f"Welcome/booking emails (oldest per recipient): {len(candidates_by_recipient)}")

    recovered = 0
    skipped_already = 0
    skipped_no_match = 0
    skipped_no_pdf = 0
    failed: list[dict] = []

    for to_email, e in candidates_by_recipient.items():
        customer = customers_by_email.get(to_email)
        if not customer:
            skipped_no_match += 1
            print(f"  ✗ {to_email}  — no matching customer in DB (subject={e['subject'][:60]!r})")
            continue
        if customer.get("original_booking_form_pdf_b64"):
            skipped_already += 1
            print(f"  • {to_email}  — already has recovered PDF, skip")
            continue

        atts = _list_attachments(api_key, e["id"])
        booking_pdfs = [
            a for a in atts
            if (a.get("filename") or "").startswith(BOOKING_PDF_FILENAME_PREFIX)
        ]
        if not booking_pdfs:
            # Fall back: just take any PDF attachment
            booking_pdfs = [a for a in atts if (a.get("filename") or "").lower().endswith(".pdf")]
        if not booking_pdfs:
            skipped_no_pdf += 1
            print(f"  ⚠ {to_email}  — email {e['id'][:8]} has no PDF attachments")
            continue

        att = booking_pdfs[0]
        dl = att.get("download_url")
        if not dl:
            skipped_no_pdf += 1
            failed.append({"email": to_email, "reason": "no download_url"})
            continue

        pdf_bytes = _download_pdf_bytes(dl)
        if not pdf_bytes:
            failed.append({"email": to_email, "reason": "download failed"})
            print(f"  ✗ {to_email}  — download failed")
            continue

        b64 = base64.b64encode(pdf_bytes).decode()
        await db.customers.update_one(
            {"id": customer["id"]},
            {"$set": {
                "original_booking_form_pdf_b64": b64,
                "original_booking_form_pdf_recovered_from": f"resend:{e['id']}",
                "original_booking_form_snapshot_at":
                    customer.get("original_booking_form_snapshot_at")
                    or datetime.now(timezone.utc).isoformat(),
            }},
        )
        recovered += 1
        print(
            f"  ✓ {to_email}  → {customer['name'][:30]:30s} "
            f"({len(pdf_bytes):>7} bytes from {att['filename']})"
        )

    print("\n── Summary ──")
    print(f"  Recovered:                 {recovered}")
    print(f"  Skipped (already had PDF): {skipped_already}")
    print(f"  Skipped (no DB match):     {skipped_no_match}")
    print(f"  Skipped (no PDF in email): {skipped_no_pdf}")
    if failed:
        print(f"  Failed downloads: {len(failed)}")
        for f in failed:
            print(f"    - {f}")


if __name__ == "__main__":
    key = (
        os.environ.get("RESEND_RECOVERY_API_KEY")
        or (sys.argv[1] if len(sys.argv) > 1 else "")
    ).strip()
    if not key:
        sys.exit("Provide a Resend full-access key via RESEND_RECOVERY_API_KEY env var or first CLI arg.")
    asyncio.run(main(key))
