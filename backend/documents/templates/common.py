"""Common utilities shared across document templates."""
import base64
import logging
from datetime import datetime
from pathlib import Path
from utils import number_to_indian_words, format_indian_currency, get_ordinal_suffix
from documents.templates.logo_data import RRL_LOGO_BASE64

logger = logging.getLogger(__name__)

# Company name constant used across all documents
COMPANY_NAME = "RRL Builders and Developers Pvt. Ltd."
COMPANY_NAME_UPPER = "RRL BUILDERS AND DEVELOPERS PVT. LTD."
COMPANY_NAME_FULL = "RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED"

# Static welcome-email attachments — these PDFs are NOT generated per customer;
# they live on disk in /app/backend/assets/welcome_email/ and are reused as-is
# for every welcome email going out (auto + manual).
WELCOME_EMAIL_STATIC_DIR = Path(__file__).resolve().parents[2] / "assets" / "welcome_email"

# (filename_sent_to_customer, on_disk_filename)
WELCOME_EMAIL_STATIC_ATTACHMENTS: list[tuple[str, str]] = [
    ("RRL_Total_Registration_Charges.pdf", "Total_Registration_Charges.pdf"),
]


def get_welcome_email_static_attachments() -> list[dict]:
    """Return the static welcome-email add-on PDFs as Resend-ready attachments.

    Each item: ``{"filename": <name shown to customer>, "content": <base64 str>}``.
    Missing files are logged and skipped — never raise so the welcome email
    still goes out even if the static asset is somehow absent on deploy.
    """
    out: list[dict] = []
    for sent_name, disk_name in WELCOME_EMAIL_STATIC_ATTACHMENTS:
        path = WELCOME_EMAIL_STATIC_DIR / disk_name
        if not path.is_file():
            logger.warning(f"Static welcome attachment missing on disk: {path}")
            continue
        try:
            out.append({
                "filename": sent_name,
                "content": base64.b64encode(path.read_bytes()).decode(),
            })
        except Exception as e:
            logger.error(f"Failed to read static welcome attachment {path}: {e}")
    return out

def get_logo_img_tag(width=120, height="auto"):
    """Return an <img> tag with the embedded base64 RRL Group logo."""
    return f'<img src="data:image/png;base64,{RRL_LOGO_BASE64}" alt="RRL Group" style="width: {width}px; height: {height};" />'


def calculate_age(date_of_birth):
    """Calculate age from a date_of_birth string (YYYY-MM-DD) or datetime. Returns empty string if unavailable."""
    if not date_of_birth:
        return ""
    try:
        if isinstance(date_of_birth, str):
            dob_date = datetime.strptime(date_of_birth, "%Y-%m-%d")
        else:
            dob_date = date_of_birth
        today = datetime.now()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        return str(age)
    except Exception:
        return ""


def get_salutation(gender):
    """Return S/o, D/o, or W/o based on gender."""
    gender = (gender or '').lower()
    if gender == 'female':
        return "D/o"
    elif gender == 'spouse':
        return "W/o"
    return "S/o"


def format_applicant_block(customer, prefix=""):
    """
    Format applicant/co-applicant details as a text block for documents.
    prefix="" for main applicant, prefix="co_applicant_" for co-applicant.
    
    Returns HTML string like:
    Name, aged XX years, S/o Father Name, residing at Address.
    Aadhaar: XXXX, PAN: XXXX, Phone: XXXX
    
    If age is blank, skips age. If address is blank, skips address.
    Returns empty string if name is missing.
    """
    if prefix:
        name = customer.get(f'{prefix}name', '') or ''
        father_name = customer.get(f'{prefix}father_name', '') or ''
        dob = customer.get(f'{prefix}date_of_birth', '') or ''
        address = customer.get(f'{prefix}address', '') or ''
        aadhaar = customer.get(f'{prefix}aadhar', '') or customer.get(f'{prefix}aadhaar', '') or ''
        pan = customer.get(f'{prefix}pan', '') or ''
        phone = customer.get(f'{prefix}phone', '') or ''
        gender = customer.get(f'{prefix}gender', '') or customer.get('gender', '') or 'male'
    else:
        name = customer.get('name', '') or ''
        father_name = customer.get('father_name', '') or ''
        dob = customer.get('date_of_birth', '') or ''
        address = customer.get('address', '') or ''
        aadhaar = customer.get('aadhar_number', '') or customer.get('aadhaar_number', '') or ''
        pan = customer.get('pan_number', '') or ''
        phone = customer.get('phone', '') or ''
        gender = customer.get('gender', '') or 'male'

    if not name:
        return ""

    age = calculate_age(dob)
    salutation = get_salutation(gender)

    # Build the description line
    parts = [f"<strong>{name}</strong>"]
    if age:
        parts.append(f"aged {age} years")
    if father_name:
        parts.append(f"{salutation} {father_name}")
    
    line1 = ", ".join(parts)
    
    if address:
        line1 += f", residing at {address}"
    
    # Build the ID line
    id_parts = []
    if aadhaar:
        id_parts.append(f"Aadhaar: {aadhaar}")
    if pan:
        id_parts.append(f"PAN: {pan}")
    if phone:
        id_parts.append(f"Phone: {phone}")
    
    line2 = ", ".join(id_parts)
    
    result = line1
    if line2:
        result += f"<br/>{line2}"
    
    return result


def format_customer_names(customer, uppercase=False):
    """
    Format applicant + co-applicant names for use in document body text.
    
    Rules:
    - If gender is 'spouse' (W/o), use "Mr. and Mrs. NAME" (only one name needed)
    - Otherwise, just use "NAME" (no Mr./Mrs. prefix)
    - If co-applicant exists and gender is NOT spouse: "NAME AND CO-APPLICANT NAME"
    - If co-applicant exists and gender IS spouse: "Mr. and Mrs. NAME"
    
    Returns the formatted name string.
    """
    name = customer.get('name', '') or ''
    co_name = customer.get('co_applicant_name', '') or ''
    gender = (customer.get('gender', '') or '').lower()
    
    if uppercase:
        name = name.upper()
        co_name = co_name.upper()
    
    if gender == 'spouse' and co_name:
        return f"Mr. and Mrs. {name}"
    
    if co_name:
        return f"{name} AND {co_name}"
    
    return name



def _year_to_words(year: int) -> str:
    """Convert a 4-digit year like 2026 to 'Two Thousand and Twenty Six'."""
    ones_w = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
              'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
              'Seventeen', 'Eighteen', 'Nineteen']
    tens_w = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
    year = int(year)
    thousands = year // 1000
    hundreds = (year % 1000) // 100
    remainder = year % 100
    parts: list[str] = []
    if thousands == 2:
        parts.append("Two Thousand")
    elif thousands == 1:
        parts.append("One Thousand")
    if hundreds > 0:
        parts.append(ones_w[hundreds] + " Hundred")
    if remainder > 0:
        if parts:
            parts.append("and")
        if remainder < 20:
            parts.append(ones_w[remainder])
        else:
            t_word = tens_w[remainder // 10]
            o_word = ones_w[remainder % 10]
            parts.append((t_word + " " + o_word).strip() if o_word else t_word)
    return " ".join(parts)


def build_agreement_date_text(agreement_date: datetime = None) -> str:
    """Return the Sales-Agreement style date string.

    Example: '14th Day of February, Two Thousand and Twenty Six- (14-02-2026)'.
    """
    if agreement_date is None:
        agreement_date = datetime.now()
    day_ordinal = str(agreement_date.day) + get_ordinal_suffix(agreement_date.day)
    month_name = agreement_date.strftime("%B")
    year_words = _year_to_words(agreement_date.year)
    date_numeric = agreement_date.strftime("%d-%m-%Y")
    return f"{day_ordinal} Day of {month_name}, {year_words}- ({date_numeric})"


def build_applicant_details_block(customer: dict) -> str:
    """Build the <p>applicant</p> + optional <p>Co-Applicant</p> HTML block used
    by templates that expose the {applicant_details_block} placeholder.
    """
    applicant_block = format_applicant_block(customer)
    co_applicant_block = format_applicant_block(customer, prefix="co_applicant_")
    html = f'<p>{applicant_block}</p>' if applicant_block else ''
    if co_applicant_block:
        html += (
            f'<p style="margin-top: 10px;"><strong>Co-Applicant:</strong>'
            f'<br/>{co_applicant_block}</p>'
        )
    return html


# Default 13-milestone payment schedule used when the customer has no explicit
# schedule saved. Kept here so both the Sales Agreement generator and the
# fallback template renderer produce identical row HTML.
_DEFAULT_SALES_AGREEMENT_MILESTONES: list[tuple[str, int]] = [
    ("Initial Booking Amount (within 10 days of Booking)", 10),
    ("Post Execution of Agreement", 10),
    ("On Completion of Foundation", 10),
    ("On Completion of Podium Slab", 10),
    ("Upon Completion of 2nd Floor Roof Slab", 5),
    ("Upon Completion of 6th Floor Roof Slab", 5),
    ("Upon Completion of 10th Floor Roof Slab", 5),
    ("Upon Completion of 14th Floor Roof Slab", 5),
    ("Upon Completion of 18th Floor Roof Slab", 5),
    ("Upon Completion of 22nd Floor Roof Slab", 5),
    ("Upon Completion of Top Roof Slab", 10),
    ("Upon Completion of Flooring of Particular Property", 10),
    ("Upon Handover / Possession / Registration", 10),
]


def build_payment_schedule_rows_html(customer: dict, schedule_items: list) -> str:
    """Render the <tr>...</tr> rows for the Sales Agreement / Payment Schedule
    tables. Falls back to a default 13-milestone template when the customer has
    no schedule saved.
    """
    total = customer.get('total_price', 0) or 0
    rows = ""
    cumulative_pct = 0
    if schedule_items and len(schedule_items) > 0:
        for i, item in enumerate(schedule_items, 1):
            milestone_name = item.get('installment_name', '') or item.get('milestone', '')
            percentage = item.get('percentage', 0) or 0
            amount = item.get('amount', 0) or 0
            cumulative_pct += percentage
            if amount == 0 and percentage > 0 and total > 0:
                amount = total * percentage / 100
            rows += f'''
            <tr>
                <td style="text-align: center;">{i}</td>
                <td>{milestone_name}</td>
                <td style="text-align: center;">{percentage}%</td>
                <td style="text-align: center;">{cumulative_pct}%</td>
                <td class="amount">{format_indian_currency(amount)}</td>
            </tr>
            '''
    else:
        for i, (name, pct) in enumerate(_DEFAULT_SALES_AGREEMENT_MILESTONES, 1):
            cumulative_pct += pct
            amount = total * pct / 100 if total > 0 else 0
            rows += f'''
            <tr>
                <td style="text-align: center;">{i}</td>
                <td>{name}</td>
                <td style="text-align: center;">{pct}%</td>
                <td style="text-align: center;">{cumulative_pct}%</td>
                <td class="amount">{format_indian_currency(amount)}</td>
            </tr>
            '''
    return rows


def build_transaction_rows_html(customer: dict, transactions: list) -> str:
    """Render the <tr>...</tr> rows for the Sales Agreement 'Transaction Details'
    table (booking + agreement stage payments)."""
    booking_amount = customer.get('booking_amount', 0) or 0
    rows = ""
    row_num = 1
    booking_seen = False
    for txn in transactions or []:
        stage = (
            txn.get('transaction_stage', '') or txn.get('transaction_type', '') or ''
        ).lower()
        if stage in ['booking', 'booking_amount', 'agreement', 'agreement_amount', 'post_agreement']:
            amount = txn.get('amount', 0) or 0
            stage_display = 'Booking' if 'booking' in stage else 'Agreement'
            if 'booking' in stage:
                booking_seen = True
            txn_date = txn.get('transaction_date', '') or ''
            bank = txn.get('bank_name', '') or ''
            txn_no = txn.get('transaction_number', '') or ''
            bank_ref = f"{bank} - {txn_no}" if bank or txn_no else stage_display + " Payment"
            rows += f'''
                <tr>
                    <td style="text-align: center;">{row_num}</td>
                    <td>{txn_date}</td>
                    <td>{stage_display}</td>
                    <td>{bank_ref}</td>
                    <td class="amount">{format_indian_currency(amount)}</td>
                </tr>
                '''
            row_num += 1
    if booking_amount > 0 and not booking_seen:
        booking_date_val = customer.get('booking_date', '') or ''
        txn_bank = customer.get('transaction_bank', '') or ''
        txn_ref = customer.get('transaction_details', '') or ''
        bank_ref = f"{txn_bank} - {txn_ref}" if txn_bank or txn_ref else "Booking Payment"
        rows = f'''
        <tr>
            <td style="text-align: center;">1</td>
            <td>{booking_date_val}</td>
            <td>Booking</td>
            <td>{bank_ref}</td>
            <td class="amount">{format_indian_currency(booking_amount)}</td>
        </tr>
        ''' + rows
    if not rows:
        rows = '''
        <tr>
            <td colspan="5" style="text-align: center; color: #666; padding: 15px;">No payments received yet</td>
        </tr>
        '''
    return rows


def format_inr(amount):
    """Format amount in Indian Rupee notation."""
    try:
        amount = float(amount or 0)
    except (ValueError, TypeError):
        amount = 0
    if amount == 0:
        return "0"
    is_negative = amount < 0
    amount = abs(amount)
    s = f"{amount:,.2f}"
    parts = s.split(".")
    whole = parts[0].replace(",", "")
    decimal = parts[1] if len(parts) > 1 else "00"
    if len(whole) <= 3:
        formatted = whole
    else:
        last3 = whole[-3:]
        rest = whole[:-3]
        groups = []
        while rest:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        formatted = ",".join(groups) + "," + last3
    result = f"{formatted}.{decimal}"
    return f"-{result}" if is_negative else result
