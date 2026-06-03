# TDS Calculation Logic — RRL CRM (LOCKED-IN BUSINESS RULE)

> 🚨 **MANDATORY READING BEFORE TOUCHING ANY TDS CODE.**
> User-approved on **2026-02-15**. Do NOT change these formulas without explicit
> user confirmation. The same logic must be used in:
> - `/app/backend/documents/templates/demand_letter.py` (PDF)
> - `/app/frontend/src/components/customer/payment/PaymentSummaryCard.jsx` (UI)
> - Any future "TDS overview" widget or report

---

## The Three TDS Numbers

| Field | Formula | Source |
|---|---|---|
| **TDS Payable** | `demand_raised ÷ 101` | Total TDS owed up to current stage. `demand_raised` = cumulative % × total price, gross-inclusive of 1% TDS u/s 194-IA. |
| **TDS Paid** | Sum of `transactions` where `transaction_stage == "tds"` | Actual TDS challans submitted by the customer. **NOT** 1% of all payments. |
| **TDS To Be Paid** | `TDS Payable − TDS Paid` | Outstanding TDS still due. Always `max(0, ...)`. |

---

## ❌ Common Mistakes (Do NOT do these)

1. **WRONG**: `tds_paid = amount_paid / 101` — this treats every booking/agreement/disbursement payment as if it carried TDS. It doesn't. TDS challans are recorded as **separate transactions** with `transaction_stage == "tds"`.

2. **WRONG**: `tds_payable = expected_amount × 0.01` — this is just 1% of the amount. Since the demand is gross-inclusive of TDS, the correct ratio is `÷ 101`, not `× 1%`.

3. **WRONG**: Mixing the two formulas between UI and PDF (e.g., UI uses `× 0.01` but PDF uses `÷ 101`). They MUST match — same numbers everywhere.

---

## ✅ Reference Implementations

### Backend (Demand Letter PDF) — `documents/templates/demand_letter.py`

```python
# ─── TDS Calculation (Section 194-IA) ───
tds_payable = round(demand_raised / 101, 2) if demand_raised else 0
tds_paid = round(
    sum(
        float(t.get('amount', 0) or 0)
        for t in transactions
        if (t.get('transaction_stage') or '').lower() == 'tds'
    ),
    2,
)
tds_to_be_paid = max(0, round(tds_payable - tds_paid, 2))
```

### Frontend (Payment Tracking Card) — `components/customer/payment/PaymentSummaryCard.jsx`

```jsx
const tdsPayable = Math.round((overdueInfo?.expected_amount || 0) / 101);
const tdsPaid = transactions
  .filter((t) => t.transaction_stage === 'tds')
  .reduce((sum, t) => sum + (t.amount || 0), 0);
const tdsBalance = Math.max(0, tdsPayable - Math.round(tdsPaid));
```

---

## ✅ Verified Test Case (2026-02-15)

**Input**:
- `total_price` = ₹1,00,00,000
- `cumulative_percentage` = 50% → `demand_raised` = ₹50,00,000
- Transactions:
  - booking: ₹5,00,000
  - agreement: ₹10,00,000
  - **tds**: ₹5,000
  - **tds**: ₹7,500
  - scheduled_disbursement: ₹20,00,000

**Expected Output**:
- TDS Payable: ₹49,505 (50,00,000 ÷ 101)
- TDS Paid: ₹12,500 (5,000 + 7,500 — only TDS-stage txns)
- TDS To Be Paid: ₹37,005 (49,505 − 12,500)

✅ Verified rendered output matches exactly.

---

## Interest Amount handling in Demand Letter (added 2026-02-15)

`customer.interest_amount` is a flat amount the customer owes outside the
cumulative slab demand (it's a post-GST add-on per `PRD.md`). It is **added
to Total Outstanding** in the demand letter:

```
Total Outstanding = (Demand Raised − Amount Paid) + Interest Amount
                  =  (A)            − (C)          + (D)
```

The "Interest (D)" row in the demand-letter table renders
`customer.interest_amount`, NOT a hardcoded `0`.

`Net Amount Payable = Total Outstanding − TDS Payable` (unchanged).

✅ Verified: total_price ₹1Cr, 50% cumulative, paid ₹30L, interest ₹25K →
Outstanding = ₹20,25,000.

---

## How to add a TDS transaction (data integrity)

When a TDS challan is submitted by the customer, accounts team must:
1. Customer Profile → Payments tab → **Add Transaction**
2. Set **Transaction Stage = "TDS"** (this is the critical field for filtering)
3. Enter the challan amount
4. Save

The system will automatically pick it up in:
- Payment Tracking → Stage-wise TDS card → "TDS Paid"
- Demand Letter PDF → "TDS Paid" row

---

**Last updated**: 2026-02-15 by user request. If you change anything in this
logic, update this file in the same commit.
