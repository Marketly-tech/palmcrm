# TDS Calculation Logic — RRL CRM (LOCKED-IN BUSINESS RULE)

> 🚨 **MANDATORY READING BEFORE TOUCHING ANY TDS CODE.**
> Last revised **2026-06-06** — Demand Letter now shows BOTH a per-slab
> "Current TDS due" and a lifetime "Total TDS Payable", and the Net Amount
> Payable formula now subtracts the per-slab figure (not the lifetime total).
> The same logic must be used in:
> - `/app/backend/documents/templates/demand_letter.py` (PDF)
> - `/app/frontend/src/components/customer/payment/PaymentSummaryCard.jsx` (UI)
> - Any future "TDS overview" widget or report

---

## The Four TDS Numbers (post-2026-06-06)

| Field | Formula | Meaning |
|---|---|---|
| **Current TDS due for Slab {X%}** | `current_due ÷ 101` | TDS owed for **the current installment only**. `current_due = stage_percentage × total_price`. Label uses `cumulative_percentage` (e.g. "50%") so it matches the Payment Stage header. |
| **Total TDS Payable** | `demand_raised ÷ 101` | Lifetime TDS owed up to current cumulative stage. `demand_raised = cumulative_percentage × total_price`, gross-inclusive of 1% TDS u/s 194-IA. *Was called "TDS Payable" pre-2026-06-06.* |
| **TDS Paid** | Sum of `transactions` where `transaction_stage == "tds"` | Actual TDS challans submitted by the customer. **NOT** 1% of all payments. |
| **TDS To Be Paid** | `Total TDS Payable − TDS Paid` | Outstanding TDS still due across the entire booking. Always `max(0, ...)`. |

### Net Amount Payable

```
Net Amount Payable = max(0, Total Outstanding − Current TDS due for Slab {X%})
```

**Why subtract the per-slab figure and not the lifetime total?**
The demand letter asks for the *current installment*. The customer will deduct
1% TDS from THIS payment and remit it themselves. Lifetime TDS shortfall is
shown separately ("TDS To Be Paid") so the customer/accounts team can true up
prior slabs, but the current cheque amount only nets the current-slab TDS.

---

## ❌ Common Mistakes (Do NOT do these)

1. **WRONG**: `tds_paid = amount_paid / 101` — this treats every booking/agreement/disbursement payment as if it carried TDS. It doesn't. TDS challans are recorded as **separate transactions** with `transaction_stage == "tds"`.

2. **WRONG**: `tds_payable = expected_amount × 0.01` — this is just 1% of the amount. Since the demand is gross-inclusive of TDS, the correct ratio is `÷ 101`, not `× 1%`.

3. **WRONG**: Mixing the two formulas between UI and PDF (e.g., UI uses `× 0.01` but PDF uses `÷ 101`). They MUST match — same numbers everywhere.

4. **WRONG (post-2026-06-06)**: `net_amount_payable = total_outstanding − tds_payable`. The lifetime Total TDS Payable will over-credit prior-slab TDS that wasn't part of this demand. Always subtract **`current_tds_due`** (current slab only).

---

## ✅ Reference Implementations

### Backend (Demand Letter PDF) — `documents/templates/demand_letter.py`

```python
# ─── TDS Calculation (Section 194-IA) ───
tds_payable     = round(demand_raised / 101, 2) if demand_raised else 0       # lifetime
current_tds_due = round(current_due   / 101, 2) if current_due   else 0       # this slab only
tds_paid = round(
    sum(
        float(t.get('amount', 0) or 0)
        for t in transactions
        if (t.get('transaction_stage') or '').lower() == 'tds'
    ),
    2,
)
tds_to_be_paid     = max(0, round(tds_payable     - tds_paid, 2))
net_amount_payable = max(0, round(total_outstanding - current_tds_due, 2))

# Render order in the demand-letter table:
#   ... Total Outstanding ...
#   Current TDS due for Slab {cumulative_percentage}%
#   Total TDS Payable
#   TDS Paid
#   TDS To be Paid
#   Net Amount Payable  (Total Outstanding − Current TDS due for Slab X%)
```

### Frontend (Payment Tracking Card) — `components/customer/payment/PaymentSummaryCard.jsx`

```jsx
const tdsPayable = Math.round((overdueInfo?.expected_amount || 0) / 101);
const tdsPaid = transactions
  .filter((t) => t.transaction_stage === 'tds')
  .reduce((sum, t) => sum + (t.amount || 0), 0);
const tdsBalance = Math.max(0, tdsPayable - Math.round(tdsPaid));
```

> The Payment Tracking UI currently shows only the lifetime numbers. If a
> per-slab card is added in future, mirror the demand-letter formula:
> `current_tds_due = current_due / 101`.

---

## ✅ Verified Test Case (2026-06-06) — Ramya test lead

**Input**:
- `total_price` = ₹2,11,656
- `cumulative_percentage` = 40% → `demand_raised` = ₹84,662
- `stage_percentage` (this slab's incremental %) = 40% → `current_due` = ₹84,662
- Transactions: total ₹85,560 paid, no `transaction_stage='tds'` rows

**Output verified in PDF**:
- Current TDS due for Slab 40%: **₹838** (84,662 ÷ 101 = 838.24)
- Total TDS Payable: **₹838**
- TDS Paid: ₹0
- TDS To be Paid: ₹838
- Total Outstanding: ₹0
- Net Amount Payable: ₹0 (`max(0, 0 − 838)`)

✅ Verified end-to-end via `/api/documents/generate` → `/api/documents/html/{id}`.

---

## Interest Amount handling in Demand Letter

`customer.interest_amount` is a flat amount the customer owes outside the
cumulative slab demand (it's a post-GST add-on per `PRD.md`). It is **added
to Total Outstanding** in the demand letter:

```
Total Outstanding = (Demand Raised − Amount Paid) + Interest Amount
                  =  (A)            − (C)          + (D)
```

The "Interest (D)" row in the demand-letter table renders
`customer.interest_amount`, NOT a hardcoded `0`.

`Net Amount Payable = Total Outstanding − Current TDS due for Slab X%`
(updated 2026-06-06).

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

**Last updated**: 2026-06-06 by user request (added per-slab Current TDS due,
renamed TDS Payable → Total TDS Payable, changed Net Amount Payable formula).
If you change anything in this logic, update this file in the same commit.
