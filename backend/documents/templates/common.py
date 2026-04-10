"""Common utilities shared across document templates."""
from datetime import datetime
from utils import number_to_indian_words, format_indian_currency, get_ordinal_suffix
from documents.templates.logo_data import RRL_LOGO_BASE64

# Company name constant used across all documents
COMPANY_NAME = "RRL Builders and Developers Pvt. Ltd."
COMPANY_NAME_UPPER = "RRL BUILDERS AND DEVELOPERS PVT. LTD."
COMPANY_NAME_FULL = "RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED"

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
