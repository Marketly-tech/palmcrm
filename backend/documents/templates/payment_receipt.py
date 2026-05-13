"""
Payment Receipt template.
Generates a one-page A4 receipt that matches RRL Builders' physical receipt
format (header with logo + address, label/value pairs with underlined fields,
amount box in the bottom-right with authorised signature).
"""
from documents.templates.common import (
    COMPANY_NAME,
    get_logo_img_tag,
    format_customer_names,
)
from utils import format_indian_currency
from utils.payment_helpers import PAYMENT_STAGES


def _number_to_words(n: int) -> str:
    """Convert positive int to Indian English words (lakhs/crores)."""
    if n == 0:
        return "Zero"
    if n < 0:
        return "Minus " + _number_to_words(-n)

    ones = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
            "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen",
            "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy",
            "Eighty", "Ninety"]

    def two_digits(num):
        if num < 20:
            return ones[num]
        return tens[num // 10] + (" " + ones[num % 10] if num % 10 else "")

    def three_digits(num):
        out = ""
        if num >= 100:
            out += ones[num // 100] + " Hundred"
            num %= 100
            if num:
                out += " "
        if num:
            out += two_digits(num)
        return out

    parts = []
    crore = n // 10000000
    if crore:
        parts.append(three_digits(crore) + " Crore")
        n %= 10000000
    lakh = n // 100000
    if lakh:
        parts.append(two_digits(lakh) + " Lakh")
        n %= 100000
    thousand = n // 1000
    if thousand:
        parts.append(two_digits(thousand) + " Thousand")
        n %= 1000
    if n:
        parts.append(three_digits(n))
    return " ".join(parts).strip()


def _format_date_ddmmyyyy(date_str: str) -> str:
    """Convert YYYY-MM-DD to DD/MM/YYYY; pass through other formats unchanged."""
    if not date_str:
        return ""
    if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
        return f"{date_str[8:10]}/{date_str[5:7]}/{date_str[0:4]}"
    return date_str


def _stage_label(stage: str) -> str:
    """Human label for a transaction stage."""
    if not stage:
        return "Payment"
    found = next((s for s in PAYMENT_STAGES if s.get("key") == stage), None)
    if found and found.get("name"):
        return f"{found['name']} Payment"
    return stage.replace("_", " ").title() + " Payment"


def generate_payment_receipt_html(customer: dict, transaction: dict) -> str:
    """Render the payment receipt HTML for a single transaction.

    Layout mirrors the printed RRL receipt: top-right Receipt Number + Date,
    label/value rows for "Received from", amount in words, cheque/draft no.,
    flat number and stage; bottom right amount box + authorised signature.
    """
    amount_int = int(round(float(transaction.get("amount", 0) or 0)))
    amount_words = f"Rupees {_number_to_words(amount_int)} Only"
    amount_formatted = format_indian_currency(amount_int, decimals=False)

    receipt_no = transaction.get("receipt_number") or "—"
    txn_date = _format_date_ddmmyyyy(transaction.get("transaction_date", ""))

    bank = transaction.get("bank_name") or ""
    txn_no = transaction.get("transaction_number") or ""
    cheque_field = f"{txn_no} ({bank})" if bank and txn_no else (txn_no or bank or "—")

    customer_names = format_customer_names(customer)
    flat_no = customer.get("unit_number", "") or ""
    tower = customer.get("tower", "") or ""
    flat_label = f"{tower}-{flat_no}" if tower and flat_no else (flat_no or "—")

    stage_label = _stage_label(transaction.get("transaction_stage", ""))

    logo_img = get_logo_img_tag(80)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Payment Receipt {receipt_no}</title>
<style>
  @page {{ size: A4; margin: 18mm 16mm; }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: 'Georgia', 'Times New Roman', serif;
    color: #111;
    margin: 0;
    padding: 0;
  }}
  .receipt {{
    border: 2px solid #111;
    padding: 18px 22px 24px 22px;
    position: relative;
  }}
  .header {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 18px;
    padding-bottom: 8px;
    border-bottom: 1px solid #333;
    margin-bottom: 14px;
  }}
  .header .logo {{ flex: 0 0 90px; }}
  .header .logo img {{ width: 80px; height: auto; }}
  .header .title-block {{ text-align: center; flex: 1; }}
  .header .title-block h1 {{
    margin: 0;
    font-size: 18px;
    letter-spacing: 1px;
    font-weight: 700;
  }}
  .header .title-block .addr {{
    margin-top: 2px;
    font-size: 11px;
    color: #444;
    line-height: 1.4;
  }}
  .header .title-block .url {{
    margin-top: 2px;
    font-size: 11px;
    color: #1a4f8a;
  }}
  .meta {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-bottom: 14px;
    font-size: 12px;
  }}
  .meta .left {{ font-style: italic; font-size: 13px; font-weight: 600; }}
  .meta .right {{ text-align: right; }}
  .meta .right .row {{ margin-bottom: 4px; }}
  .meta .right .lbl {{ font-weight: 600; margin-right: 6px; }}
  .meta .right .val {{
    display: inline-block;
    min-width: 110px;
    border-bottom: 1px solid #222;
    padding: 0 6px;
    font-weight: 500;
  }}
  .field {{
    display: flex;
    align-items: baseline;
    margin: 12px 0;
    font-size: 13px;
  }}
  .field .lbl {{
    flex: 0 0 auto;
    margin-right: 8px;
    font-weight: 600;
  }}
  .field .val {{
    flex: 1;
    border-bottom: 1px dotted #222;
    padding: 0 4px;
    min-height: 18px;
  }}
  .field .val.italic {{ font-style: italic; }}
  .footer {{
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-top: 28px;
    gap: 20px;
  }}
  .footer .signature {{
    flex: 1;
    border-top: 1px solid #222;
    padding-top: 4px;
    font-size: 11px;
    text-align: left;
    color: #444;
  }}
  .amount-box {{
    flex: 0 0 230px;
    text-align: center;
  }}
  .amount-box .company {{
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    margin-bottom: 6px;
  }}
  .amount-box .amount {{
    border: 1.5px solid #111;
    padding: 10px 12px;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 6px;
    background: #fafafa;
  }}
  .amount-box .auth {{
    border-top: 1px solid #222;
    padding-top: 4px;
    font-size: 11px;
    letter-spacing: 0.6px;
    font-weight: 600;
    color: #333;
  }}
  .note {{
    margin-top: 16px;
    font-size: 10px;
    font-style: italic;
    color: #666;
    text-align: left;
  }}
</style>
</head>
<body>
  <div class="receipt">
    <div class="header">
      <div class="logo">{logo_img}</div>
      <div class="title-block">
        <h1>{COMPANY_NAME.upper()}</h1>
        <div class="addr">
          4th Floor, RRL Tower, Sompura Gate, Sarjapura Road, Anekal Taluk, Bengaluru &mdash; 562125
        </div>
        <div class="url">www.rrlbuildersanddevelopers.com</div>
      </div>
    </div>

    <div class="meta">
      <div class="left">Receipt No.</div>
      <div class="right">
        <div class="row">
          <span class="lbl">Receipt Number:</span>
          <span class="val">{receipt_no}</span>
        </div>
        <div class="row">
          <span class="lbl">Date:</span>
          <span class="val">{txn_date}</span>
        </div>
      </div>
    </div>

    <div class="field">
      <div class="lbl">Received with thanks from</div>
      <div class="val">{customer_names}</div>
    </div>
    <div class="field">
      <div class="lbl">A sum of Rupees</div>
      <div class="val italic">{amount_words}</div>
    </div>
    <div class="field">
      <div class="lbl">by Cheque / Draft No.</div>
      <div class="val">{cheque_field}</div>
    </div>
    <div class="field">
      <div class="lbl">Dated</div>
      <div class="val">{txn_date}</div>
    </div>
    <div class="field">
      <div class="lbl">For Palm Altezze &mdash; Flat No.</div>
      <div class="val">{flat_label}</div>
    </div>
    <div class="field">
      <div class="lbl">Towards</div>
      <div class="val">{stage_label}</div>
    </div>

    <div class="footer">
      <div class="signature">Receiver's Signature</div>
      <div class="amount-box">
        <div class="company">For RRL BUILDERS AND DEVELOPERS PVT LTD</div>
        <div class="amount">Rs. {amount_formatted}/-</div>
        <div class="auth">AUTHORISED SIGNATURE</div>
      </div>
    </div>

    <div class="note">* Cheque/s are subject to realisation</div>
  </div>
</body>
</html>"""
