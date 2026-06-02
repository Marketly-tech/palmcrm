# BESCOM Charges — Pricing Logic (LOCKED-IN BUSINESS RULE)

> 🚨 **MANDATORY READING BEFORE TOUCHING BESCOM IN ANY FILE.**
> User-approved on **2026-02-15**.

---

## Formula

```
bescom_amount = bescom_rate (₹/sqft) × saleable_area
```

Example: 1500 sqft × ₹50/sqft = ₹75,000

---

## Tax treatment

- **Included in subtotal**, BEFORE GST and Labour Cess.
- That means: `labour_cess` (0.7%) and `gst` (5%) **DO** apply on top of BESCOM.
- Order in subtotal: `base_price + floor_rise_total + club_house + parking + additional_charges + bescom_amount` → then labour_cess + GST on this whole subtotal → then interest_amount (if any) flat after GST.

---

## Storage

| Field | Type | Default | Where |
|---|---|---|---|
| `bescom_rate` | float (₹/sqft) | 0 | `customers/models.py::Customer` |

The **amount** is NOT stored separately — always derived on the fly from `bescom_rate × saleable_area` to stay consistent if either input changes. (`bescom_amount` is sent through on save for downstream consumers, but the canonical source of truth is `bescom_rate`.)

---

## Where it appears

| Surface | Behaviour |
|---|---|
| Customer Profile → Property & Pricing card | Editable input "BESCOM Rate (₹/sq.ft)". Live preview shows `rate × sqft` total. Saved on Save Changes. |
| Live Price Calculator preview | Shows `BESCOM (₹50/sq.ft): ₹75,000` row when rate > 0. Included in subtotal. |
| Price Breakup PDF (`documents/templates/price_breakup.py`) | Conditional `bescom_row` rendered between Additional Parking and Grand Total. Hidden if amount = 0. |
| Other PDFs (allotment, demand, NOCs) | Not shown explicitly — they consume `total_price` only. |

---

## Reference implementations

### Frontend live calc — `hooks/useCustomerPage.js::calculateLivePrice`

```js
const bescomRate = parseFloat(data.bescom_rate) || 0;
const bescomAmount = bescomRate * saleableArea;
const subtotal = basePrice + floorRiseTotal + clubHouse + parkingCharges + additionalCharges + bescomAmount;
// then labour_cess + gst on subtotal, then interest_amount flat
```

### Backend PDF — `documents/templates/price_breakup.py`

```python
bescom_rate = float(customer.get('bescom_rate', 0) or 0)
saleable_area = float(customer.get('saleable_area', 0) or 0)
bescom_amount = round(bescom_rate * saleable_area)
bescom_row = (
    f'<tr><td>BESCOM Charges (&#8377;{bescom_rate:g}/sq.ft &times; {saleable_area:g})</td>'
    f'<td class="amount">{format_inr(bescom_amount)}</td></tr>'
    if bescom_amount else ''
)
```

---

## ❌ Common mistakes (do NOT do these)

1. **WRONG**: Storing `bescom_amount` as primary field and `bescom_rate` as derived. If saleable_area is later edited, the amount becomes stale. Always derive `amount = rate × area` on demand.
2. **WRONG**: Skipping GST/labour cess on BESCOM. Per user, BESCOM is part of subtotal — full tax treatment applies.
3. **WRONG**: Adding BESCOM after GST like Interest Amount. Interest is post-GST; BESCOM is pre-GST. They are NOT the same.

---

## Verified test case (2026-02-15)

- saleable_area = 11 sqft (test customer Ramya)
- bescom_rate = ₹50/sqft
- → Expected BESCOM amount = ₹550 ✓ (rendered in price_breakup HTML)

---

**Last updated**: 2026-02-15 by user request. Change only with explicit user confirmation.
