"""
HTML template generators for RRL CRM document generation.
All PDF/HTML document templates are defined here.
"""
from datetime import datetime
from utils import number_to_indian_words, format_indian_currency, get_ordinal_suffix
from utils.enums import DocumentType

def generate_sales_agreement_template():
    """Generate Sales Agreement HTML template with black and gold theme - Full 23 Page Version"""
    return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        @page {
            size: A4;
            margin: 20mm 15mm 20mm 15mm;
        }
        
        body {
            font-family: 'Roboto', serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1A1A1A;
            background: #fff;
            padding: 15px 25px;
        }
        
        /* Prevent orphans and widows */
        p, li, td {
            orphans: 3;
            widows: 3;
        }
        
        /* Prevent page breaks inside important elements */
        .party-section, table, .clause, .sub-clause {
            page-break-inside: avoid;
        }
        
        /* Ensure tables don't break badly */
        table {
            page-break-inside: auto;
        }
        
        tr {
            page-break-inside: avoid;
            page-break-after: auto;
        }
        
        thead {
            display: table-header-group;
        }
        
        tfoot {
            display: table-footer-group;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #D4AF37;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo {
            width: 50px;
            height: 50px;
            background: #1A1A1A;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #D4AF37;
            font-weight: bold;
            font-size: 18px;
        }
        
        .company-name {
            font-size: 16px;
            font-weight: 700;
            color: #1A1A1A;
        }
        
        .company-tagline {
            font-size: 9px;
            color: #666;
        }
        
        h1.main-title {
            text-align: center;
            font-size: 18px;
            font-weight: 700;
            color: #1A1A1A;
            margin: 25px 0;
            text-decoration: underline;
            text-transform: uppercase;
        }
        
        .section-title {
            font-weight: 700;
            color: #1A1A1A;
            font-size: 12pt;
            margin: 20px 0 12px 0;
            padding: 8px 12px;
            background: #f5f5f5;
            border-left: 4px solid #D4AF37;
            text-transform: uppercase;
        }
        
        .sub-section-title {
            font-weight: 600;
            color: #1A1A1A;
            font-size: 11pt;
            margin: 15px 0 10px 0;
            text-decoration: underline;
        }
        
        .highlight {
            color: #D4AF37;
            font-weight: 600;
        }
        
        .content p {
            margin: 10px 0;
            text-align: justify;
        }
        
        .party-section {
            margin: 15px 0;
            padding: 15px;
            background: #fafafa;
            border-left: 4px solid #D4AF37;
        }
        
        .party-section p {
            margin: 5px 0;
        }
        
        .party-title {
            font-weight: 700;
            color: #1A1A1A;
            margin-bottom: 10px;
        }
        
        table.details {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        table.details th, table.details td {
            border: 1px solid #D4AF37;
            padding: 8px 10px;
            text-align: left;
            font-size: 10pt;
        }
        
        table.details th {
            background: #1A1A1A;
            color: #D4AF37;
            font-weight: 500;
            width: 40%;
        }
        
        table.details td {
            background: #fafafa;
        }
        
        table.schedule {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 9pt;
            page-break-inside: auto;
        }
        
        table.schedule th, table.schedule td {
            border: 1px solid #D4AF37;
            padding: 6px 8px;
            text-align: left;
        }
        
        table.schedule th {
            background: #1A1A1A;
            color: #D4AF37;
            font-weight: 500;
        }
        
        table.schedule tr {
            page-break-inside: avoid;
        }
        
        table.schedule tr:nth-child(even) {
            background: #fafafa;
        }
        
        table.schedule .amount {
            text-align: right;
            font-family: 'Roboto Mono', monospace;
        }
        
        .clause {
            margin: 8px 0;
            text-align: justify;
            page-break-inside: avoid;
        }
        
        .clause-number {
            font-weight: 700;
            color: #D4AF37;
        }
        
        .sub-clause {
            margin: 8px 0 8px 25px;
            text-align: justify;
        }
        
        .roman-list {
            margin-left: 25px;
        }
        
        .roman-list li {
            margin: 8px 0;
            text-align: justify;
        }
        
        .signature-section {
            margin-top: 40px;
            page-break-inside: avoid;
        }
        
        .signature-row {
            display: flex;
            justify-content: space-between;
            margin-top: 30px;
        }
        
        .signature-box {
            width: 45%;
            text-align: center;
        }
        
        .signature-line {
            border-top: 1px solid #1A1A1A;
            margin-top: 80px;
            padding-top: 10px;
        }
        
        .schedule-section {
            margin-top: 15px;
            margin-bottom: 10px;
        }
        
        .schedule-header {
            background: #1A1A1A;
            color: #D4AF37;
            padding: 10px 15px;
            font-weight: 700;
            font-size: 13pt;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .boundary-table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        .boundary-table th, .boundary-table td {
            border: 1px solid #D4AF37;
            padding: 10px;
            font-size: 10pt;
        }
        
        .boundary-table th {
            background: #f5f5f5;
            width: 30%;
            text-align: left;
        }
        
        .specs-list {
            margin: 10px 0 10px 25px;
        }
        
        .specs-list li {
            margin: 6px 0;
        }
        
        .amenities-list {
            margin: 10px 0 10px 25px;
            columns: 2;
        }
        
        .amenities-list li {
            margin: 5px 0;
        }
        
        .witness-section {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #D4AF37;
        }
        
        .footer {
            margin-top: 20px;
            padding-top: 15px;
            border-top: 2px solid #D4AF37;
            text-align: center;
            font-size: 9pt;
            color: #666;
        }
        
        /* Position footer at bottom of last page */
        @page:last {
            @bottom-center {
                content: element(footer);
            }
        }
        
        .page-break {
            page-break-after: always;
        }
        
        /* Prevent content from overlapping at page boundaries */
        .section-title, .sub-section-title {
            page-break-after: avoid;
        }
        
        .party-section {
            page-break-inside: avoid;
        }
        
        .witness-section {
            page-break-inside: avoid;
        }
        
        .signature-section {
            page-break-inside: avoid;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-section">
            <div class="logo">RRL</div>
            <div>
                <div class="company-name">RRL Builders and Developers</div>
                <div class="company-tagline">Beyond homes. A lifestyle</div>
            </div>
        </div>
    </div>
    
    <h1 class="main-title">Agreement for Sale</h1>
    
    <div class="content">
        <p>This <strong>Agreement For Sale</strong> is made and entered into on this <span class="highlight">{agreement_date_text}</span> at Bengaluru.</p>
        
        <p style="text-align: center; font-weight: 700; margin: 20px 0;">BETWEEN:</p>
        
        <!-- OWNER PARTIES -->
        <div class="party-section">
            <p class="party-title">1. MRS. MUNITHAYAMMA</p>
            <p>Aged about 60 years, W/o Late Narayana Reddy</p>
            <p>Residing at: Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District - 560087</p>
            <p>AADHAAR No: 504904154718 | PAN No.: CFDPM2534P</p>
        </div>
        
        <div class="party-section">
            <p class="party-title">2. MRS. YESHASWINI N</p>
            <p>Aged about 36 years, D/o Late Narayana Reddy</p>
            <p>Residing at: Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District - 560087</p>
            <p>AADHAAR No: 661099599743 | PAN No.: AUCPY4059M</p>
        </div>
        
        <div class="party-section">
            <p class="party-title">3. MAST. HRUTHVIK REDDY S</p>
            <p>Aged about 4 years, S/o Yeshaswini N</p>
            <p>Residing at: Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District - 560087</p>
            <p>AADHAAR No: 318812583405 | PAN No.: NA</p>
            <p style="margin-top: 15px;">Represented by his natural guardian, mother.</p>
            <p class="party-title" style="margin-top: 15px;">MRS. YESHASWINI N</p>
            <p>Aged about 34 years</p>
            <p>D/o Late Narayana Reddy</p>
            <p>Residing at: Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District - 560087</p>
            <p>AADHAAR No: 661099599743 | PAN No.: AUCPY4059M</p>
        </div>
        
        <div class="party-section">
            <p class="party-title">4. MS. TEJASWINI N</p>
            <p>Aged about 27 years, D/o Late Narayana Reddy</p>
            <p>Residing at: Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District - 560087</p>
            <p>AADHAAR No: 358161939490 | PAN No.: BIOPT0038E</p>
        </div>
        
        <p style="margin: 15px 0;"><strong>All are represented by the General Power of Attorney Holder:</strong></p>
        
        <div class="party-section">
            <p class="party-title">M/s. RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</p>
            <p>A Private Limited Company having its registered office at:</p>
            <p>4th Floor, RRL TOWERS, Sompura Gate, Sarjapura Road, Bengaluru – 562125</p>
            <p>PAN No. AAKCR4125J</p>
            <p style="margin-top: 10px;"><strong>Represented by its Managing Director,</strong></p>
            <p style="margin-left: 20px;"><strong>MR. RAM R</strong></p>
            <p style="margin-left: 20px;">Aged about 36 years</p>
            <p style="margin-left: 20px;">S/o C Rajareddy</p>
            <p style="margin-left: 20px;">Residing at: #23/1, Sarjapura Road, Sompura Gate, Vinayaka Nagar, Sompura, Bengaluru, Karnataka - 562125</p>
            <p style="margin-left: 20px;">AADHAAR No: 457278356452</p>
            <p style="margin-left: 20px;">PAN No.: BELPR1909B</p>
        </div>
        
        <p>Hereinafter referred to as the <strong>'OWNER'</strong> (which expression unless repugnant to the context shall mean and include his heirs, legal representatives, administrators, executors, successors and assigns); and</p>
        
        <div class="party-section">
            <p class="party-title">5. M/s. RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</p>
            <p>A Private Limited Company having its registered office at:</p>
            <p>4th Floor, RRL TOWERS, Sompura Gate, Sarjapura Road, Bengaluru – 562125</p>
            <p>PAN No. AAKCR4125J</p>
            <p style="margin-top: 10px;"><strong>Represented by its Managing Director,</strong></p>
            <p style="margin-left: 20px;"><strong>MR. RAM R</strong></p>
            <p style="margin-left: 20px;">Aged about 36 years</p>
            <p style="margin-left: 20px;">S/o C. Rajareddy</p>
            <p style="margin-left: 20px;">Residing at: #23/1, Sarjapura Road, Sompura Gate, Vinayaka Nagar, Sompura, Bengaluru, Karnataka - 562125</p>
            <p style="margin-left: 20px;">AADHAAR No: 457278356452</p>
            <p style="margin-left: 20px;">PAN No.: BELPR1909B</p>
        </div>
        
        <p>Hereinafter referred to as the <strong>'BUILDER'</strong> (which expression unless repugnant to the context shall mean and include his successors in office and assigns)</p>
        
        <p style="margin: 15px 0;">Both 'Owner' and 'Builder' are collectively hereinafter referred to as the <strong>'VENDORS'</strong> and together forming ONE Part.</p>
        
        <p style="text-align: center; font-weight: 700; margin: 20px 0;">AND</p>
        
        <!-- PURCHASER SECTION -->
        <div class="party-section">
            <p class="party-title">PURCHASER:</p>
            <p><strong><span class="highlight">{customer_name}</span></strong></p>
            <p>Aged about <span class="highlight">{age}</span> years, {salutation} <span class="highlight">{father_name}</span></p>
            <p>Residing at: <span class="highlight">{address}</span></p>
            <p>AADHAAR No.: <span class="highlight">{aadhaar_number}</span> | PAN No.: <span class="highlight">{pan_number}</span> | Mobile: <span class="highlight">{phone}</span></p>
        </div>
        
        <p>Hereinafter referred to as the <strong>PURCHASER/S / ALLOTTEE/S</strong> (which expression unless repugnant to the context shall mean and include his/her/their legal heirs, representatives, administrators, executors, successors and assigns) of the OTHER Part.</p>
        
        <p style="margin: 15px 0;">As the context may require the PURCHASER/S and VENDORS are sometimes hereinafter collectively referred to as the "Parties" and severally as a "Party".</p>
        
        <p style="text-align: center; font-weight: 700; margin: 25px 0; font-size: 12pt;">NOW THIS AGREEMENT FOR SALE WITNESSETH AS FOLLOWS:</p>
        
        <!-- SECTION I: FLOW OF TITLE -->
        <div class="section-title">I. FLOW OF TITLE</div>
        
        <p class="clause">WHEREAS the OWNERS represent that they are the absolute owners of agricultural land bearing Sy. No. 73/6 (Old Sy. No. 73/5 and Old Old Sy. No. 73) to an extent of 1 Acre 38 Guntas, situated at Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, morefully described in the schedule hereunder mentioned and herein after referred to as the "Schedule Property".</p>
        
        <p class="clause">Whereas the larger extent of agricultural land measuring 03 – 36 (Acres – Guntas), situated at Sy. No. 73, Jantagondanahalli Village, Sarjapura Hobli, Anekal taluk, Bengaluru Urban District, originally belonged to one Mr. Late Gurappa S/o Nanjappa.</p>
        
        <p class="clause">Thereafter, one Mr. Late Narayana Reddy @ Narayana @ Narayanappa S/o Mr. Late Gurappa and Nanjappa @ Nanja Reddy S/o Late Gurappa has been in joint possession and enjoyment of larger extent of agricultural land measuring 03 – 36 (Acres – Guntas), in Sy. No. 73, situated at Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District.</p>
        
        <p class="clause">Thereafter, Mr. Late Narayana Reddy @ Narayana @ Narayanappa, S/o Mr. Late Gurappa, more specifically has been in enjoyment and possession of 02 – 1 ½ (Acres – Guntas) in Sy. No. 73, situated at Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, by way of family arrangement.</p>
        
        <p class="clause">Thereafter, on demise of Mr. Late Narayana Reddy @ Narayana @ Narayanappa, S/o Mr. Late Gurappa, his wife Mrs. T. Munithayamma is in enjoyment and possession of agricultural land to the extent of 02 – 1 ½ (Acres – Guntas) in Sy. No. 73, situated at Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District.</p>
        
        <p class="clause">Thereafter, a suit for partition bearing OS No. 82/2004 on file of Hon'ble Principal Civil Judge (Sr. Div.), Bengaluru Rural District, Bengaluru was filed by one of the ancestors of Mr. Late Gurappa S/o Nanjappa. Thereafter, upon arrival of compromise amongst parties, the aforesaid suit was decreed on 02-06-2004 in accordance with the compromise petition filed before the court aforesaid.</p>
        
        <p class="clause">In view of the same, the Schedule Property was allotted to the share of Mrs. Munithayamma, Baby Yashaswini and Baby Thejaswini, by virtue of a Decree drawn and registered in the Office of Sub-Registrar, Anekal, Bengaluru, vide Document No. ANK-1-08680-2004-05 dated 05-08-2004. Thereafter, the records were mutated in the name of Mrs. T. Munithayamma.</p>
        
        <p class="clause">Thereafter, Mrs. T. Munithayamma, Mrs. Yeshaswini N, Master Hruthvik Reddy and Ms. Tejaswini N, have entered into a Memorandum of Understanding with M/s. RRL Builders and Developers Private Limited for development of Schedule Property herein below mentioned, registered in the office of the Sub-Registrar, Sarjapura, Bengaluru, vide Document No. SRJ-1-03312-2023-24 dated 26-07-2023.</p>
        
        <p class="clause">Thereafter, Mrs. T. Munithayamma, Mrs. Yeshaswini N, Master Hruthvik Reddy S represented by his natural guardian mother, and Ms. Tejaswini N have executed a Joint Development Agreement with M/s. RRL Builders and Developers Private Limited, represented by its Managing Director, Mr. Ram R, for development of the Schedule Property into a Residential Apartment Building and has agreed to the share of saleable development area in the ratio of 33:67, and the same is registered as Document No. SRJ-1-07944-2024-25 dated 29-11-2024, registered in the office of the Sub-Registrar, Sarjapura, Bengaluru.</p>
        
        <p class="clause">Thereafter, Mrs. T. Munithayamma, Mrs. Yeshaswini N, Master Hruthvik Reddy S represented by his natural guardian mother, and Ms. Tejaswini N have also executed a Power of Attorney (pursuant to the Joint Development Agreement dated 27-11-2025) in favour of M/s. RRL Builders and Developers Private Limited, represented by its Managing Director, Mr. Ram R, to do such acts, including to sell the flats falling into the share of M/s. RRL Builders and Developers Private Limited, amongst others, and the same is registered as Document No. SRJ-4-00669-2024-25 dated 29-11-2024, registered in the office of the Sub-Registrar, Sarjapura, Bengaluru.</p>
        
        <p class="clause">Thereafter, Mrs. T. Munithayamma has applied for 'Change of Land Use' from 'agricultural' to 'residential' purpose. On 02-01-2025, the Member-Secretary and Joint Director of City and Town Planning Authority, Anekal Planning Authority, vide its letter bearing No. APA/L.C/10/2023-24, has permitted for 'Change of Land Use' as above.</p>
        
        <p class="clause">Thereafter, Mrs. T. Munithayamma has applied for a deemed conversion of land from agricultural to residential purpose and the Office of the Deputy Commissioner, Bengaluru, has issued an official memorandum bearing No. 741998 dated 12-02-2025 by approving conversion of agricultural land in Sy. No. 73/6 (Old Sy. No. 73/5 and Old Old Sy. No. 73) measuring 1 Acre 38 Guntas, situated at Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, as above.</p>
        
        <p class="clause">Thereafter, E-Katha bearing No. 73/6, PID No. 150200101600120805, has been issued by Neriga Gram Panchayat, w.r.t. land measuring a total extent of 7,891.37 Sq. Mts., situated on Sy. 73/6 Jantagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, and the same stands in the name of Mrs. T. Munithayamma and she has paid property tax for the period.</p>
        
        <p class="clause">Office of the Neriga Gram Panchayat, Sarjapura Hobli, Anekal taluk, Bengaluru Urban District, vide its letter bearing No. GP/CR/73/24-25 has issued 'No Objection Certificate' for development of Schedule Property.</p>
        
        <p class="clause">Office of the Tehsildar, Anekal Taluk vide Certificate No. RD1218028021831, dated 03-10-2024 has issued 'nil tenancy' certificate, confirming that there are no 'tenancy' applications pending in relation to the Schedule Property.</p>
        
        <p class="clause">Office of the Assistant Commissioner, Bangalore South Sub-Division, vide Endorsement bearing No. L.R.F.(A) C.R:35/2025 dated 27-02-2025 has stated that since Sections 79(a)(b) of Land Reforms Act, 1961 has been omitted by Land Reforms (Second Amendment) Act, 2020, there is no provision to issue any endorsement regarding any pendency of any case in relation to the Schedule Property.</p>
        
        <p class="clause">Office of the Assistant Commissioner, Bangalore South Sub-Division, vide Endorsement bearing No. P.T.C.L(A)/C.R:955/2024-25 dated 01-03-2025 has stated that, there are no cases registered under the Karnataka Scheduled Castes and Scheduled Tribes (Prohibition of Transfer of Certain Lands) Act, 1978 and since the Schedule Property has been converted for residential purpose, the same shall not apply.</p>
        
        <p class="clause">WHEREAS, the OWNER herein, in order to develop the Schedule A Property into a multistoried residential apartment, have entered into a Joint Development Agreement dated 27-11-2024 with M/s. RRL Builders and Developers Private Limited, represented by its Managing Director, Mr. Ram R S/o. Mr. C. Raja Reddy, the BUILDER herein and registered as document No. SRJ-1-07944-2024-25, the same have registered on 29-11-2024 and stored in Central Cloud, in the office of the Senior Sub-Registrar, Basavanagudi (Sarjapura) (hereinafter referred to as "JDA").</p>
        
        <p class="clause">WHEREAS, in accordance with JDA, the BUILDER has agreed to build and construct a residential apartment building, which is later named as <strong>"RRL PALM ALTEZZE"</strong> on the Schedule A Property and to deliver to the OWNER free from any encumbrances and liabilities 33% of the super built-up area (including 33% of open/covered car parking space) in the aforesaid residential apartment, which is earmarked as 'Owner's Constructed Area'.</p>
        
        <p class="clause">In consideration whereof, the OWNER herein has conveyed 67% of undivided, title and interest in favour of the BUILDER in the Schedule A Property and similarly, the BUILDER shall be entitled to retain free from any encumbrances and liabilities 67% of the super built-up area (including 67% of open/covered car parking space) in the Schedule A Property, which is earmarked as 'Developer's Constructed Area'.</p>
        
        <p class="clause">WHEREAS, the OWNER herein, pursuant to execution of JDA have executed a General Power of Attorney dated 27-11-2024 in favour of the BUILDER, registered as document No. SRJ-4-00669-2024-25, same as registered on 29-11-2024 & and stored in Central Cloud, in the office of the Senior Sub-Registrar, Basavanagudi (Sarjapura).</p>
        
        <p class="clause">WHEREAS, the OWNER, pursuant to GPA, has authorised the BUILDER to execute such documents and indenture in relation to development and building of residential apartment building on the Schedule A Property and to convey, absolute right title and interest by way of sale, mortgage, lease to anybody, on behalf of the OWNER w.r.t. 67% of the super built-up area (including 67% of open/covered car parking space) in the Schedule 'A' Property, which is earmarked as 'Developer's Constructed Area' and to receive such consideration w.r.t. the same.</p>
        
        <p class="clause">WHEREAS, the BUILDER, has formulated a plan for development of the Schedule A Property into a multi storied residential Apartment and has obtained Single Plan Approval for construction of Residential Apartment, vide the order of the Member Secretary and Joint Director of Urban and Rural Planning, Anekal Planning Authority, Anekal, vide their letter bearing No. APA/LAO/119/2024-25 dated 13-05-2025.</p>
        
        <p class="clause">WHEREAS, the BUILDER, thereafter has received Commencement Certificate bearing No. CC/241/2025-26 dated 18-08-2025 from the Member Secretary and Joint Director, Town and Country Planning, Satellite Ring Road Planning Authority, Bengaluru for construction of Basement + Ground + 23 Upper Floors in Tower 1 & Tower 2 on the Schedule A Property.</p>
        
        <p class="clause">WHEREAS, the BUILDER, thereafter has received necessary permissions from various authorities and has received construction license dated 07-10-2025 from Jantagondanahalli Gram Panchayat in the name of the OWNER.</p>
        
        <p class="clause">WHEREAS, the BUILDER, thereafter has registered the aforesaid project in the name and style of <strong>'RRL PALM ALTEZZE'</strong> ("Project") and has obtained registration from Real Estate Regulatory Authority vide <strong>RERA Reg. No. PRM/KA/RERA/1251/308/PR/141025/008167</strong>.</p>
        
        <p class="clause">WHEREAS, the BUILDER and the VENDOR has executed a Sharing Agreement dated 29-11-2024, as document No. SRJ-1-04868-2025-26 and stored in Central Cloud, in the office of the Senior Sub-Registrar, Basavanagudi (Sarjapura) wherein the OWNER and the BUILDER has earmarked their respective share in the aforesaid building 'RRL PALM ALTEZZE' in the ratio of 33 : 67 ('Owner's Constructed Area' : 'Developer's Constructed Area').</p>
        
        <p class="clause">WHEREAS, in pursuance of the above a residential <span class="highlight">{bhk_type}</span> flat bearing Flat No. <span class="highlight">{unit_number}</span>, to be built on the <span class="highlight">{floor_ordinal}</span> Floor measuring about <span class="highlight">{saleable_area}</span> Sq. Ft. of Super Built-up Area, to be built on the Schedule 'A' Property along with one covered Car Parking Space (more fully described herein and hereinafter referred to as the "Schedule 'C' Property") along with <span class="highlight">{uds}</span> Sq. Ft. of Undivided Share, title and interest in the Schedule 'A' Property (morefully described herein and hereinafter referred to as the "Schedule 'B' Property") has fallen into the share of the BUILDER herein.</p>
        
        <p class="clause">WHEREAS, the ALLOTTEE/S has applied to the BUILDER to purchase the Schedule 'B' Property and Schedule 'C' Property along with proportionate share in the common areas of the building built on Schedule 'A' Property along with one covered car parking space.</p>
        
        <p class="clause">WHEREAS, the VENDORS have allotted Schedule 'B' Property and Schedule 'C' Property in favour of the PURCHASER/S and has intended to sell the same for valuable consideration herein below mentioned.</p>
        
        <p class="clause">WHEREAS the VENDORS have agreed to sell the Schedule 'B' Property and Schedule 'C' Property to the ALLOTTEE/S and the ALLOTTEE/S has/have agreed to purchase the Schedule 'B' Property and Schedule 'C' Property for consideration mentioned herein below and upon such other terms and conditions agreed to between them as detailed herein below.</p>
        
        <p class="clause">The Parties have gone through all the terms and conditions set out in this Agreement and understood the mutual rights and obligations detailed herein.</p>
        
        <p class="clause">The Parties hereby confirm that they are signing this Agreement with full knowledge of all the laws, rules, regulations, notifications, etc., applicable to the Project.</p>
        
        <p class="clause">The Parties, relying on the confirmations, representations and assurances of each other to faithfully abide by all the terms, conditions and stipulations contained in this Agreement and all applicable laws, are now willing to enter into this Agreement on the terms and conditions appearing hereinafter.</p>
        
        <!-- SECTION II: TERMS AND CONDITIONS -->
        <div class="section-title">II. IT IS HEREBY AGREED BY AND BETWEEN THE PARTIES AS FOLLOWS:</div>
        
        <div class="sub-section-title">SALE PRICE AND TERMS OF PAYMENT:</div>
        
        <p class="clause"><span class="clause-number">(i)</span> The VENDORS agrees to sell, and the PURCHASER/S agrees to buy the Schedule 'B' Property and Schedule 'C' Property, for a total sale consideration of <strong>Rs. <span class="highlight">{total_price_formatted}</span>/- (<span class="highlight">{total_price_words}</span> Only)</strong> as given.</p>
        
        <p class="clause"><strong>Note:</strong> Stamp Duty, Registration Fee & Other Expenses to be incurred towards the same shall have to be borne by the PURCHASER/S at the time of Registration. All payments to be made in the name of BUILDER (i.e. M/s. RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED) in the following ESCROW Account.</p>
        
        <table class="details">
            <tr><th>Account Holder Name</th><td>RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</td></tr>
            <tr><th>Bank</th><td>HDFC BANK</td></tr>
            <tr><th>Branch</th><td>SOMPURA</td></tr>
            <tr><th>Account Number</th><td>57500001802063</td></tr>
            <tr><th>IFSC Number</th><td>HDFC0009590</td></tr>
        </table>
        
        <p class="clause">Bajaj Housing Finance Limited ("Lender" or "BHFL") is the Lender of the Project and the properties of the Project have been charged/mortgaged in favour of the Lender and any sale consideration in respect of the units of the Project shall be deposited by the PURCHASER/S directly in the aforesaid Escrow Account. Also the Borrower(s) hereby undertakes that existing and proposed unit buyers of the Project and mortgage financing institution wherever unit buyers availed/are availing Residential Purchase loans shall be informed to deposit balance consideration in the Escrow Account as provided herein.</p>
        
        <p class="clause"><span class="clause-number">(ii)</span> Accordingly, the PURCHASER/S as a token of acceptance, has paid a sum of <strong>Rs. <span class="highlight">{booking_amount_formatted}</span>/- (<span class="highlight">{booking_amount_words}</span> Only)</strong> vide payment details recorded separately. The receipt of which the VENDORS hereby accepts and acknowledges in the presence of the witnesses attesting hereunder.</p>
        
        <p class="clause"><span class="clause-number">(iii)</span> The payment of sale consideration being the essence of this Agreement, the PURCHASER/S will pay the balance consideration and all amounts payable under this Agreement without any default in accordance with the payment schedule and timelines mentioned hereunder. All such payments shall be made after deduction of applicable TDS (if any).</p>
        
        <div class="sub-section-title">Payment Schedule:</div>
        
        <table class="schedule">
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 45%;">Milestone / Particulars</th>
                    <th style="width: 10%;">%</th>
                    <th style="width: 12%;">Cumulative %</th>
                    <th style="width: 28%;">Amount (Rs.)</th>
                </tr>
            </thead>
            <tbody>
                {payment_schedule_rows}
            </tbody>
            <tfoot>
                <tr style="background: #1A1A1A;">
                    <td colspan="2" style="color: #D4AF37; font-weight: bold;">TOTAL</td>
                    <td style="color: #D4AF37; font-weight: bold;">100%</td>
                    <td style="color: #D4AF37; font-weight: bold;">100%</td>
                    <td class="amount" style="color: #D4AF37; font-weight: bold;">{total_price_formatted}</td>
                </tr>
            </tfoot>
        </table>
        
        <div class="sub-section-title">Transaction Details (Payments Received):</div>
        
        <table class="schedule">
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 20%;">Date</th>
                    <th style="width: 20%;">Stage</th>
                    <th style="width: 25%;">Bank / Reference</th>
                    <th style="width: 30%;">Amount (Rs.)</th>
                </tr>
            </thead>
            <tbody>
                {transaction_rows}
            </tbody>
            <tfoot>
                <tr style="background: #1A1A1A;">
                    <td colspan="4" style="color: #D4AF37; font-weight: bold;">TOTAL RECEIVED</td>
                    <td class="amount" style="color: #D4AF37; font-weight: bold;">{total_received_formatted}</td>
                </tr>
            </tfoot>
        </table>
        
        <p class="clause"><strong>Note:</strong></p>
        <p class="sub-clause">a. All the payments shall have to be made within 7 days from the date of completion of the milestone above mentioned. The PURCHASER/S shall pay the installments as mentioned above regularly in favour of BUILDER as above mentioned either by way of DD/Cheque/RTGS/NEFT on or before the due dates. The BUILDER shall be entitled to claim simple interest calculated at the rate of 1.5% per month on all delayed payments of installments from the PURCHASER/S from the date due till the date of payment. However, if the PURCHASER/S fails to make payment beyond 60 days from the date due, the BUILDER shall be entitled to terminate this Agreement on the account of 'non-payment'.</p>
        
        <p class="sub-clause">b. The PURCHASER/S may choose to avail housing loan from any Banks/Financial Institutions. Builder under any circumstances shall not be responsible or liable for non-sanction of loans or as per timelines aforesaid.</p>
        
        <p class="sub-clause">c. The ALLOTTEE/S, if resident outside India, shall be solely responsible for complying with the necessary formalities as laid down in Foreign Exchange Management Act, 1999, Reserve Bank of India Act, 1934 and the Rules and Regulations made thereunder or any statutory amendment(s) modification(s) made thereof and all other applicable laws including that of remittance of payment acquisition/sale/transfer of immovable properties in India etc. and provide the BUILDER with such permission, approvals which would enable the BUILDER to fulfill its obligations under this Agreement.</p>
        
        <p class="sub-clause">d. Any refund, transfer of security, if provided in terms of the Agreement shall be made in accordance with the provisions of Foreign Exchange Management Act, 1999 or the statutory enactments or amendments thereof and the Rules and Regulations of the Reserve Bank of India or any other applicable law. The ALLOTTEE/S understands and agrees that in the event of any failure on his/her part to comply with the applicable guidelines issued by the Reserve Bank of India, he/she may be liable for any action under the Foreign Exchange Management Act, 1999 or other laws as applicable, as amended from time to time. The BUILDER accepts no responsibility in regard to matters specified in para above. The ALLOTTEE/S shall keep the BUILDER fully indemnified and harmless in this regard.</p>
        
        <p class="sub-clause">e. Whenever there is any change in the residential status of the ALLOTTEE/S subsequent to the signing of this Agreement, it shall be the sole responsibility of the ALLOTTEE/S to intimate the same in writing to the BUILDER immediately and comply with necessary formalities if any under the applicable laws.</p>
        
        <p class="sub-clause">f. The BUILDER shall not be responsible towards any third-party making payment/remittances on behalf of any ALLOTTEE/S and such third party shall not have any right in the application/allotment of the said apartment applied for herein in any way and the BUILDER shall be issuing the payment receipts in favour of the ALLOTTEE/S only.</p>
        
        <div class="sub-section-title">CONSTRUCTION OF THE PROJECT:</div>
        <p class="clause">The ALLOTTEE/S has seen the proposed layout plan, specifications, amenities and facilities of Apartment and accepted the floor plan, payment plan and the specifications, amenities and facilities which has been approved by the competent authority, as represented by the BUILDER. The BUILDER shall develop the Project in accordance with the said layout plans, floor plans and specifications, amenities and facilities. Subject to the terms in this Agreement and permissible deviations.</p>
        
        <div class="sub-section-title">POSSESSION OF THE APARTMENT:</div>
        <p class="clause">The BUILDER understands that timely delivery of possession of the Apartment to the ALLOTTEE/S and the common areas to the association of ALLOTTEE/S or the competent authority, as the case may be, is the essence of the Agreement. The BUILDER assures to hand over possession of the Apartment along with ready and complete common areas with all specifications, amenities and facilities of the project in place on or before <strong><span class="highlight">{possession_date}</span></strong>, unless there is delay or failure due to war, flood, drought, fire, cyclone, earthquake, non-availability of manpower, non-availability of materials, court orders, regulatory orders, change in policy, or any other calamity, epidemic, lockdowns, strikes, etc. affecting the regular development of the real estate project ("Force Majeure").</p>
        
        <p class="clause">If, however, the completion of the Project is delayed due to the Force Majeure conditions then the ALLOTTEE/S agrees that the BUILDER shall be entitled to such extension of time for delivery of possession of the Apartment.</p>
        
        <p class="clause">The ALLOTTEE/S agrees and confirms that, in the event it becomes impossible for the BUILDER to implement the project due to Force Majeure conditions, then this allotment shall stand terminated and the BUILDER shall refund to the ALLOTTEE/S the entire amount received by the BUILDER from the allotment within 90 days from the date of such communication. If the client has opted for Pre EMI, then interest amount paid by the builder (if any) will be kept on hold. Along with that, 5% GST amount will also be kept on hold and the balance amount will be refunded to the client. The BUILDER shall intimate the allottee about such termination. After refund of the money paid by the ALLOTTEE/S, the ALLOTTEE/S agrees that he/she shall not have any rights, claims etc. against the BUILDER and that the BUILDER shall be released and discharged from all its obligations and liabilities under this Agreement.</p>
        
        <p class="clause">The BUILDER, upon obtaining the occupancy certificate from the competent authority shall offer in writing the possession of the Apartment, to the ALLOTTEE/S in terms of this Agreement to be taken within three months from the date of issue of occupancy certificate.</p>
        
        <p class="clause">The BUILDER agrees and undertakes to indemnify the ALLOTTEE/S in case of failure of fulfillment of any of the provisions, formalities, documentation on part of the BUILDER.</p>
        
        <p class="clause">The ALLOTTEE/S, after taking the possession, agree(s) to pay the maintenance charges as determined by the BUILDER/association of ALLOTTEE/S, as the case may be after the issuance of the completion certificate for the project. Failure of ALLOTTEE/S to take Possession of Apartment upon receiving a written intimation from the BUILDER, the ALLOTTEE/S shall take possession of the Apartment from the BUILDER by executing such deed of conveyance or 'Deed of Absolute Sale' as envisaged in this Agreement and after making all payments, and the BUILDER shall give possession of the Apartment to the ALLOTTEE/S.</p>
        
        <p class="clause">In case the ALLOTTEE/S fails to take possession or make payments as stipulated under this Agreement, within the time provided, in such event, this Agreement, at the option of the BUILDER shall stand terminated and the BUILDER shall be entitled to sell the Apartment to any such prospective buyer. In the event, the ALLOTTEE/S has made payment and fails to take handover of the Apartment for any other reason, then such ALLOTTEE/S shall continue to be liable to pay maintenance charges.</p>
        
        <p class="clause">After handing over physical possession of the Apartment to the ALLOTTEE/S, it shall be the responsibility of the BUILDER to hand over the necessary documents and plans, including common areas, to the association of ALLOTTEE/S or the competent authority, as the case may be, as per applicable laws.</p>
        
        <p class="clause">In the event the ALLOTTEE/S proposes to cancel/withdraw from the project without any fault of the BUILDER, the BUILDER herein is entitled to forfeit the booking amount paid for the allotment by the ALLOTTEE/S and return the balance amount of money paid by the ALLOTTEE/S within 90 days of such cancellation.</p>
        
        <p class="clause">In the event BUILDER fails to deliver the possession of the Apartment to the ALLOTTE/S for any reason other than reason of occurrence of Force Majeure event within the aforesaid stipulated time, the BUILDER shall be liable to pay on demand to the ALLOTTEE/S the amount received under this Agreement along with interest as stipulated under law within 90 days from the date of such demand, in the event of termination of this Agreement by the ALLOTTEE/S.</p>
        
        <p class="clause">In the event ALLOTTEE/S does not intend to terminate this Agreement, then the BUILDER agrees to pay such delay penalty prescribed under law by the competent authority until the date of handover of possession.</p>
        
        <div class="sub-section-title">REPRESENTATIONS AND WARRANTIES OF THE VENDORS:</div>
        <p class="clause"><span class="clause-number">(i)</span> The VENDORS hereby represents and warrants to the ALLOTTEE/S as follows:</p>
        
        <ol class="roman-list" type="a">
            <li>The VENDORS has absolute, clear and marketable title with respect to the Schedule 'A' Property, including the requisite rights to carry out development upon the said land and absolute, actual, physical and legal possession of the said land for the Project;</li>
            <li>The VENDORS has lawful rights and requisite approvals from the competent authorities to carry out development of the Project;</li>
            <li>There are no encumbrances upon the Schedule 'A' Property or the Project;</li>
            <li>There are no litigations pending before any court of law or authority with respect to Schedule 'A' Property, Project or the Apartment;</li>
            <li>All approvals, licenses and permits issued by the competent authorities with respect to the Project, said Land and Apartment are valid and subsisting and have been obtained by following due process of law;</li>
            <li>The VENDORS have the right to enter into this Agreement and has not committed or omitted to perform any act or thing, whereby the right, title and interest of the ALLOTTEE/S created herein, may prejudicially be affected;</li>
            <li>The VENDORS have not entered into any agreement for sale/arrangement with any person or party with respect to the said land, including the Project and the Schedule 'C' Property, which will, in any manner, affect the rights of ALLOTTEE/S under this Agreement;</li>
            <li>The VENDORS confirms that the VENDORS are not restricted in any manner whatsoever from selling the Schedule 'C' Property to the ALLOTTEE/S in the manner contemplated in this Agreement;</li>
            <li>At the time of execution of the conveyance deed the VENDORS shall handover lawful, vacant, peaceful, physical possession of the Schedule 'C' Property and constructive possession of the Schedule 'B' Property to the ALLOTEE/S and the common areas to the Association of the allottees or the competent authority, as the case may be;</li>
            <li>The Schedule 'A' Property is not the subject matter of any HUF and that no part thereof is owned by any minor and/or no minor has any right, title and claim over the Schedule 'A' Property;</li>
            <li>The VENDORS have duly paid and shall continue to pay and discharge all governmental dues, rates, charges and taxes and other monies, levies, impositions, premiums, damages and/or penalties and other outgoings, whatsoever, payable with respect to the Project to the competent authorities till the completion certificate has been issued and possession of apartment, plot or buildings, as the case may be, along with common areas (equipped with all the specifications, amenities and facilities) has been handed over to the ALLOTTEE/S and the association of allottees or the competent authority, as the case may be;</li>
            <li>No notice from the Government or any other local body or authority or any legislative enactment, government ordinance, order, notification (including any notice for acquisition or requisition of the said property) has been received by or served upon the BUILDER in respect of the said Land and/or the Project.</li>
        </ol>
        
        <div class="sub-section-title">CONVEYANCE OF THE SCHEDULE 'B' PROPERTY AND SCHEDULE 'C' PROPERTY:</div>
        <p class="clause">The BUILDER, on receipt of total consideration towards Schedule 'B' Property and Schedule 'C' Property as envisaged under this Agreement from the ALLOTTEE/S, shall execute a conveyance deed in favour of the ALLOTTEE/S and convey the title of the Schedule 'C' Property together with proportionate indivisible share in the Schedule 'A' Property within 3 months from the date of issuance of the occupancy certificate / completion certificate, as the case may be, provided the ALLOTTEE/S pays the stamp duty, registration fees and charges.</p>
        
        <div class="sub-section-title">MAINTENANCE OF THE PROJECT:</div>
        <p class="clause">The BUILDER shall be responsible to provide and maintain essential services in the Project till the taking over of the maintenance of the Project by the association of the allottees or for a period of one year from the date of receipt of completion certificate /occupancy certificate, whichever is earlier. The ALLOTEE/S agrees to deposit one year's maintenance and corpus amount in advance on the date of conveyance of the Schedule 'C' Property or such date stipulated by the BUILDER.</p>
        
        <div class="sub-section-title">DEFECT LIABILITY:</div>
        <p class="clause">It is agreed that in case any structural defect in workmanship, quality or provision of services or any other obligations of the BUILDER as per this Agreement is brought to the notice of the BUILDER within a period of 5 (five) years by the ALLOTTEE/S from the date of handing over possession, it shall be the duty of the BUILDER to rectify such defects.</p>
        
        <div class="sub-section-title">RIGHT TO ENTER THE PROJECT FOR REPAIRS:</div>
        <p class="clause">The BUILDER /maintenance agency /association of allottees shall have rights of unrestricted access to all common areas, garages/covered parking and parking spaces for providing necessary maintenance services and the ALLOTTEE/S agrees to permit the association of allottees and/or maintenance agency to enter into the Apartment or any part thereof, after due notice and during the normal working hours, unless the circumstances warrant otherwise, with a view to set right any defect/issues.</p>
        
        <div class="sub-section-title">USAGE:</div>
        <p class="clause">The basement and service areas, if any, as located within the Project, shall be earmarked for purposes such as parking spaces and services including but not limited to electric sub-station, transformer, DG set rooms, underground water tanks, pump rooms, maintenance and service rooms, fire-fighting pumps and equipment etc. and other permitted uses as per sanctioned plans. The ALLOTTEE/S shall not be permitted to use the services areas and the basements in any manner whatsoever, other than those earmarked as parking spaces, and the same shall be reserved for use by the association of allottees formed by the allottees for rendering maintenance services.</p>
        
        <div class="sub-section-title">10. COVENANTS OF ALLOTTEE/S / PURCHASER/S:</div>
        <p class="clause">ALLOTTEE/S agrees that after taking possession and handover of the Apartment from the BUILDER, he/her/they shall be solely responsible to maintain the Apartment at his/her/their own cost, in good repair and condition and shall not do or suffer to be done anything in or to the Building, or the Apartment or the staircases, lifts, common passages, corridors, circulation areas, atrium or the compound which may be in violation of any laws or rules of any authority or change or alter or make additions to the Apartment and keep the Apartment, its walls and partitions, sewers, drains, pipe and appurtenances thereto or belonging thereto, in good and tenantable repair and maintain the same in a fit and proper condition and ensure that the support, shelter etc. of the Building is not in any way damaged or jeopardized.</p>
        
        <p class="clause">The ALLOTTEE/S further undertakes, assures and guarantees that he/she would not put any sign-board / name-plate, neon light, publicity material or advertisement material etc. on the face/facade of the building or anywhere on the exterior of the Project, buildings therein or Common Areas. The ALLOTTEE/S shall also not change the colour scheme of the outer walls or painting of the exterior side of the windows or carry out any change in the exterior elevation or design. Further the ALLOTTEE/S shall not store any hazardous or combustible goods in the Apartment/Building or place any heavy material in the common passages or staircase of the Building/Common Areas. The ALLOTTEE/S shall also not remove any wall, including the outer and load bearing wall of the Apartment.</p>
        
        <p class="clause">iii. The ALLOTTEE/S shall plan and distribute its electrical load in conformity with the electrical systems installed by the BUILDER and thereafter the association of ALLOTTEE/S and/or maintenance agency appointed by association of allottees. The ALLOTTEE/S shall be responsible for any loss or damages arising out of breach of any of the aforesaid conditions.</p>
        
        <p class="clause">iv. The ALLOTTEE/S shall not cause any obstruction for the free passage and movement in driveways, pathways, passages and other common areas.</p>
        
        <p class="clause">v. The ALLOTTEE/S in the event intends to sell the Schedule 'C' Property, shall take NOC from the association formed by the ALLOTTEE/S.</p>
        
        <p class="clause">vi. The ALLOTTEE/S shall mandatorily be required to be a member of the Apartment Owners Association to be formed for maintaining and management of common amenities and facilities with other allotees of the building under appropriate and applicable laws. The ALLOTTEE/S shall pay maintenance from time to time to the constituted Apartment Owners Association post-handover from BUILDER, to access common amenities and towards maintenance of the BUILDING and shall be bound by such bye-laws adopted and rules and regulations applicable.</p>
        
        <p class="clause">vii. The ALLOTTEE/S shall have no right, title or interest in the areas earmarked as 'common areas' other than 'right to use' the same in common in a prudent manner. The ALLOTTEE/S shall live in harmony with other allottees of the BUILDING and shall not disturb anybody's peaceful enjoyment of the BUILDING.</p>
        
        <p class="clause">viii. The ALLOTTEE/S shall pay the pro-rata or stipulated property taxes and cess and outgoing expenses for maintenance of common areas and common facilities including common water charges, street lights, security, repair and maintenance determined by constituted Apartment Owners Association from time to time.</p>
        
        <p class="clause">ix. The ALLOTTEE/S shall maintain surroundings of Schedule 'C' Property and the BUILDING clean and tidy and shall not cause any nuisance to other occupants. The ALLOTTEE/S shall keep no other animal except pet dog/cat in the Apartment and shall ensure that the same shall not cause any disturbance to other occupants of the BUILDING.</p>
        
        <p class="clause">x. The ALLOTTEE/S in the event of leasing the Schedule 'C' Property, shall keep informed the Apartment Owners Association about the same and shall furnish the details of such lessee and it shall be the primary responsibility of the ALLOTTEE/S to ensure compliance of the terms in this Agreement and applicable bye laws by such lessee.</p>
        
        <p class="clause">xi. The ALLOTTEE/S shall not change the name of the building "RRL PALM ALTEZZE". The ALLOTTEE/S shall use treated STP water for gardening and other secondary purpose.</p>
        
        <p class="clause">xii. The ALLOTTEE/S shall not be entitled to assign the terms of this Agreement, without prior approval of the BUILDER and payment of transfer fees, and if flat is booked through CP and purchase wants to cancel the flat after the agreement 3% of the flat value will be holding by the builder.</p>
        
        <p class="clause">xiii. The ALLOTTEE/S understands that they along with all other allottees shall be responsible for routine maintenance including:</p>
        <ul class="specs-list">
            <li>painting, white washing, cleaning of the Apartment;</li>
            <li>maintenance of the pumped, sanitary and electrical lines common to the BUILDING;</li>
            <li>replacement of lights/bulbs in the common areas;</li>
            <li>maintenance of gardens, parks, plants in the common areas;</li>
            <li>maintenance of common amenities, swimming pool, play area, lifts, etc.;</li>
            <li>deployment of security, maintenance and housekeeping staff.</li>
        </ul>
        
        <p class="clause">xiv. ALLOTTEE/S understands that in the event of default of payment due for any common expenses, benefits or amenities, a majority of the owners while carrying out the services as contemplated above, shall have the right to remove such common benefits, or amenities from his/her/their enjoyment, until payment of all dues.</p>
        
        <div class="sub-section-title">11. RIGHTS OF THE PURCHASER/S / ALLOTTEE/S:</div>
        <p class="clause">The right to own an apartment described in Schedule 'C' Property for residential purpose. The right and liberty to the PURCHASER/S and all persons entitled, authorized or permitted by the PURCHASER/S (in common with all other persons entitled, permitted or authorized to a similar right) at all times and for all purposes, to use the staircases, passages and common areas in the building for ingress and egress and use in common. The right to subjacent, lateral, vertical and horizontal support for the Schedule 'C' Property from the other parts of the building.</p>
        
        <p class="clause">The right to free and uninterrupted passage of water, reticulated gas, electricity, sewage, etc., from and to the Schedule 'C' Property through the pipes, wires, sewer lines, drain and water courses and cables which are or may at any time hereafter be, in, under or passing through the building or any part thereof.</p>
        
        <p class="clause">The right to lay cables or wires for television, telephone, internet, gas, cable, etc. and such other installations through the common walls is subject to the bye-laws of the 'Apartment Owners Association', thereby recognizing and reciprocating such rights of the other residents of the apartment.</p>
        
        <p class="clause">Right of entry and passage for the PURCHASER/S with or without workmen to other parts of the Building at all reasonable time to enter into and upon other parts of the building for the purpose of repairs to or maintenance of the Schedule 'C' Property or for repairing, cleaning, maintaining or removing the sewer, drains and water courses, cables, pipes and wires causing as little disturbance as possible to the other residents of the apartment and making good any damage caused.</p>
        
        <p class="clause">Right to use along with other owners and residents of the apartments, all the common facilities provided therein on payment of such sums as may be prescribed from time to time by 'Apartment Owners Association' / BUILDER, as the case may be.</p>
        
        <p class="clause">Right to use and enjoy the common roads, common areas and parks and open space and common facilities in Schedule 'A' Property in accordance with the purpose for which they are provided without endangering or encroaching the lawful rights of other owners/users.</p>
        
        <p class="clause">The PURCHASER/S shall be entitled in common with the owners and residents of the other apartments in the BUILDING, to use and enjoy the common areas and facilities listed here under:</p>
        <ul class="specs-list">
            <li>Entrance lobbies, passages and corridors;</li>
            <li>Lifts/pumps/generators, generator room;</li>
            <li>Staircase, driveways in the basements, roads and pavements;</li>
            <li>Common facilities, subject to compliance of rules, regulations of the Maintenance Agency and byelaws of the 'Apartment Owners Association'.</li>
        </ul>
        
        <div class="sub-section-title">12. ENTIRE AGREEMENT:</div>
        <p class="clause">This Agreement, along with its schedules, constitutes the entire Agreement between the Parties with respect to the subject matter hereof and supersedes any and all understandings, any other agreements, allotment letter, correspondences, arrangements whether written or oral, if any, between the Parties in regard to the said apartment/plot/building, as the case may be.</p>
        
        <div class="sub-section-title">13. RIGHT TO AMEND:</div>
        <p class="clause">This Agreement may only be amended through written consent of the Parties.</p>
        
        <div class="sub-section-title">14. PROVISIONS OF THIS AGREEMENT APPLICABLE ON ALLOTTEE/S OR SUBSEQUENT ALLOTTEE/S:</div>
        <p class="clause">It is clearly understood and so agreed by and between the Parties hereto that all the provisions contained herein and the obligations arising hereunder in respect of the Apartment and the Project shall equally be applicable to and enforceable against and by any subsequent ALLOTTEE/S of the Apartment, in case of a transfer, as the said obligations go along with the Apartment for all intents and purposes.</p>
        
        <div class="sub-section-title">15. WAIVER NOT A LIMITATION TO ENFORCE:</div>
        <p class="clause">The BUILDER may, at its sole option and discretion, without prejudice to its rights as set out in this Agreement, waive the breach by the ALLOTTEE/S in not making payments as per the payment schedule including waiving the payment of interest for delayed payment. It is made clear and so agreed by the ALLOTTEE/S that exercise of discretion by the BUILDER in the case of one ALLOTTEE/S shall not be construed to be a precedent and /or binding on the BUILDING to exercise such discretion in the case of other ALLOTTEE/S.</p>
        
        <div class="sub-section-title">16. SEVERABILITY:</div>
        <p class="clause">If any provision of this Agreement shall be determined to be void or unenforceable under the applicable acts or rules and regulations made thereunder or under other applicable laws, such provisions of the Agreement shall be deemed amended or deleted in so far as reasonably inconsistent with the purpose of this Agreement and to the extent necessary, and the remaining provisions of this Agreement shall remain valid and enforceable as applicable at the time of execution of this Agreement.</p>
        
        <div class="sub-section-title">17. NOTICES:</div>
        <p class="clause">That all notices to be served on the ALLOTTEE/S and the VENDORS as contemplated by this Agreement shall be deemed to have been duly served if sent to the respective parties by Registered Email / Post at the addresses aforesaid.</p>
        
        <div class="sub-section-title">18. JOINT ALLOTTEES:</div>
        <p class="clause">That in case there are joint allottees all communications shall be sent by the BUILDER to the ALLOTTEE/S whose name appears first and at the address given by him/her which shall for all intents and purposes to consider as properly served on all the ALLOTTEE/S.</p>
        
        <div class="sub-section-title">19. GOVERNING LAW & JURISDICTION:</div>
        <p class="clause">That the rights and obligations of the parties under or arising out of this Agreement shall be construed and enforced in accordance with Indian Laws and the parties shall submit to exclusive jurisdiction of courts at Anekal / Bengaluru Rural.</p>
        
        <!-- SCHEDULE A -->
        <div class="schedule-section">
            <div class="schedule-header">SCHEDULE 'A' PROPERTY</div>
            <p style="text-align: center; font-weight: 600; margin-bottom: 15px;">(DESCRIPTION OF THE LAND ON WHICH PROJECT IS DEVELOPED)</p>
            
            <p class="clause">All that piece and parcel of the undeveloped converted land bearing Sy. No.73/6 (Old Sy. No. 73/5 and Old Old Sy. No. 73) (bearing PID No.150200101600120805), measuring 1-0 (One) Acre 0-38 (Thirty Eight) Guntas, converted from agricultural to non-agricultural residential purpose vide conversion order bearing No. APL/L.U/10/2023-24 dated 22/11/2024, issued by the Member Secretary & Joint Director, Anekal Planning Authority, situated at Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bangalore Urban District, bounded on the:</p>
            
            <table class="boundary-table">
                <tr><th>East by:</th><td>Chikka Muniswamy's Land</td></tr>
                <tr><th>West by:</th><td>C Schedule Land / Nanjappa's Land</td></tr>
                <tr><th>North by:</th><td>Road</td></tr>
                <tr><th>South by:</th><td>Chikka Obareddy's Land</td></tr>
            </table>
        </div>
        
        <!-- SCHEDULE B -->
        <div class="schedule-section">
            <div class="schedule-header">SCHEDULE 'B' PROPERTY</div>
            <p style="text-align: center; font-weight: 600; margin-bottom: 15px;">(UNDIVIDED INTEREST HEREBY CONVEYED)</p>
            
            <p class="clause"><span class="highlight">{uds}</span> Sq. Ft. of undivided share, right, title, interest and ownership in the Schedule 'A' Property.</p>
        </div>
        
        <!-- SCHEDULE C -->
        <div class="schedule-section">
            <div class="schedule-header">SCHEDULE 'C' PROPERTY</div>
            <p style="text-align: center; font-weight: 600; margin-bottom: 15px;">(DESCRIPTION OF THE APARTMENT HEREBY CONVEYED)</p>
            
            <p class="clause">All that <span class="highlight">{bhk_type}</span> Residential Flat bearing Flat No. <span class="highlight">{unit_number}</span> on the <span class="highlight">{floor_ordinal}</span> Floor, measuring about <span class="highlight">{saleable_area}</span> Sq.Ft., of super built-up area, to be developed and constructed on Schedule 'A' Property, along with one covered car parking space{additional_parking_text}, in the project/building known as <strong>RRL PALM ALTEZZE</strong>.</p>
            
            <div class="sub-section-title">Specifications of the Building:</div>
            <ul class="specs-list">
                <li>R.C.C. Framed Structure;</li>
                <li>2.5 Track Fabricated Windows for living and bedroom with mosquito mesh;</li>
                <li>Main Door Frame and all other doors with Pre hung doors shutters;</li>
                <li>Client can select Tile Flooring / Wooden flooring for master bedroom, Wooden flooring will not have any warranty or guaranty;</li>
                <li>Concealed copper wiring with Anchor/Roma Switches, Socket and Slides;</li>
                <li>Individual TV & Telephone points in Living and Master Bedroom;</li>
                <li>Emulsion Paint for internal walls and exterior with Apex paints;</li>
                <li>Vitrified tiles for flooring and anti-skid tiles for balcony;</li>
                <li>Kerovit Sanitary fittings by Kajaria;</li>
                <li>Anti-Skid ceramic tiled flooring and glazed dado tiles up to 7" for toilets;</li>
            </ul>
            
            <div class="sub-section-title">Amenities:</div>
            <ul class="amenities-list">
                <li>Club House (gym, multipurpose hall, steam bath, sauna bath, indoor games, kids play area, sit out, mini theater)</li>
                <li>STP, Gas Bank</li>
                <li>Swimming Pool</li>
                <li>Lifts by OTIS</li>
                <li>Indoor/Outdoor Games</li>
                <li>Power Back-up for common area and flat</li>
            </ul>
        </div>
        
        <!-- SIGNATURE SECTION -->
        <div class="signature-section">
            <p style="font-weight: 700; margin-bottom: 20px;">IN WITNESS WHEREOF the Parties hereto have set and subscribed their respective hands and seals on the day, month and year first above-written.</p>
            
            <div class="party-section" style="margin-bottom: 20px;">
                <p><strong>OWNERS:</strong></p>
                <p>MRS. MUNITHAYAMMA</p>
                <p>MRS. YESHASWINI N</p>
                <p>MASTER HRUTHVIK REDDY S, Represented by his natural guardian mother, Mrs. Yeshaswini N.</p>
                <p>MS. TEJASWINI N</p>
                <p style="margin-top: 10px;"><strong>All are Represented by the General Power of Attorney Holder:</strong></p>
                <p>M/s. RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</p>
                <p>Represented by its Managing Director, <strong>MR. RAM R</strong></p>
            </div>
            
            <div class="signature-row">
                <div class="signature-box">
                    <p><strong>VENDORS</strong></p>
                    <div class="signature-line">
                        <p>For RRL Builders & Developers Pvt. Ltd.</p>
                        <p>Authorized Signatory</p>
                    </div>
                </div>
                <div class="signature-box">
                    <p><strong>PURCHASER/S</strong></p>
                    <div class="signature-line">
                        <p>{customer_name}</p>
                    </div>
                </div>
            </div>
            
            <div class="witness-section">
                <p><strong>WITNESSES:</strong></p>
                <div class="signature-row" style="margin-top: 20px;">
                    <div class="signature-box">
                        <div class="signature-line">
                            <p>1. ____________________</p>
                        </div>
                    </div>
                    <div class="signature-box">
                        <div class="signature-line">
                            <p>2. ____________________</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p><strong>RRL Builders and Developers Pvt. Ltd.</strong></p>
        <p>4th Floor, RRL TOWERS, Sompura Gate, Sarjapura Road, Bengaluru – 562125</p>
        <p>www.rrlbuildersanddevelopers.com | RERA: PRM/KA/RERA/1251/308/PR/141025/008167</p>
        <p style="margin-top: 10px;">Document Generated: {date} | Ref: {customer_id}</p>
    </div>
</body>
</html>
"""

def get_default_template(doc_type: DocumentType) -> str:
    templates = {
        DocumentType.SALES_AGREEMENT: generate_sales_agreement_template(),
        DocumentType.ALLOTMENT_LETTER: """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Roboto', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1A1A1A;
            background: #fff;
            padding: 25px 40px;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 3px solid #D4AF37;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo {
            width: 50px;
            height: 50px;
            background: #1A1A1A;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #D4AF37;
            font-weight: bold;
            font-size: 18px;
        }
        
        .company-name {
            font-size: 16px;
            font-weight: 700;
            color: #1A1A1A;
        }
        
        .company-tagline {
            font-size: 10px;
            color: #666;
        }
        
        .document-title {
            background: #1A1A1A;
            color: #D4AF37;
            padding: 8px 18px;
            border-radius: 4px;
            font-weight: 500;
            font-size: 12px;
            text-transform: uppercase;
        }
        
        .recipient {
            margin-bottom: 15px;
            padding: 15px;
            background: #fafafa;
            border-left: 4px solid #D4AF37;
        }
        
        .recipient p {
            margin: 3px 0;
            font-size: 11px;
        }
        
        .highlight {
            color: #D4AF37;
            font-weight: 600;
        }
        
        .subject {
            margin: 15px 0;
            font-weight: 600;
            color: #1A1A1A;
        }
        
        .greeting {
            margin: 10px 0;
        }
        
        .content {
            text-align: justify;
            margin: 12px 0;
            font-size: 10.5pt;
        }
        
        .section-title {
            font-weight: 600;
            color: #D4AF37;
            margin: 18px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 2px solid #D4AF37;
            font-size: 11pt;
        }
        
        .terms {
            margin-left: 15px;
        }
        
        .terms p {
            margin: 10px 0;
            text-align: justify;
            font-size: 10pt;
        }
        
        .terms-number {
            font-weight: 600;
            color: #D4AF37;
        }
        
        table.details {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        
        table.details th, table.details td {
            border: 1px solid #D4AF37;
            padding: 8px 12px;
            text-align: left;
            font-size: 10.5pt;
        }
        
        table.details th {
            background: #1A1A1A;
            color: #D4AF37;
            font-weight: 500;
            width: 40%;
        }
        
        table.details td {
            background: #fafafa;
        }
        
        .signature-section {
            margin-top: 35px;
            display: flex;
            justify-content: space-between;
        }
        
        .signature-box {
            width: 45%;
        }
        
        .signature-line {
            border-top: 1px solid #1A1A1A;
            margin-top: 50px;
            padding-top: 5px;
        }
        
        .declaration {
            margin-top: 25px;
            padding: 15px;
            border: 2px solid #D4AF37;
            background: #fafafa;
            font-size: 10pt;
        }
        
        .bank-details {
            margin: 12px 0;
            padding: 12px;
            background: #1A1A1A;
            color: #fff;
            border-radius: 4px;
        }
        
        .bank-details p {
            margin: 3px 0;
            font-size: 10pt;
        }
        
        .bank-details strong {
            color: #D4AF37;
        }
        
        .footer {
            margin-top: 25px;
            padding-top: 15px;
            border-top: 2px solid #D4AF37;
            text-align: center;
            font-size: 9pt;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-section">
            <div class="logo">RRL</div>
            <div>
                <div class="company-name">RRL Builders and Developers</div>
                <div class="company-tagline">Beyond homes. A lifestyle</div>
            </div>
        </div>
        <div class="document-title">Allotment Letter</div>
    </div>
    
    <div class="recipient">
        <p><strong>To,</strong></p>
        <p><strong>Dear Mr./Mrs. <span class="highlight">{customer_name}</span></strong></p>
        <p>Phone No: <span class="highlight">{phone}</span></p>
        <p>Email: <span class="highlight">{email}</span></p>
        <p>PAN: <span class="highlight">{pan_number}</span></p>
    </div>
    
    <div class="subject">
        <p>Subject: Confirmation of Allotment</p>
    </div>
    
    <div class="greeting">
        <p>Dear Sir/Madam,</p>
    </div>
    
    <div class="content">
        <p>We are issuing this allotment letter pursuant to your submission of an expression of interest dated <span class="highlight">{booking_date}</span>, requesting unit No. <span class="highlight">{unit_number}</span> in our project being developed under the name of "<strong>{project}</strong>" RERA No. PRM/KA/RERA/1251/308/PR/141025/008167. Upon due consideration of your EOI, we are pleased to confirm your booking and allot Flat No. <span class="highlight">{unit_number}</span> in "{project}" subject to the Terms and conditions set out herein. We take this opportunity to welcome you to "RRL BUILDERS AND DEVELOPERS PVT LTD" family and are pleased that you have chosen to purchase your home from us.</p>
        
        <p style="margin-top: 12px;">You hereby acknowledge and confirm that the copies of title documents have been handed over to you and that you have scrutinized and are satisfied with the title of the Developer to the project being good and marketable.</p>
    </div>
    
    <div class="section-title">A. ALLOTMENT DETAILS</div>
    
    <table class="details">
        <tr>
            <th>Heading</th>
            <th>Particulars</th>
        </tr>
        <tr>
            <td>Name of the Project</td>
            <td><span class="highlight">{project}</span></td>
        </tr>
        <tr>
            <td>RERA No.</td>
            <td>PRM/KA/RERA/1251/308/PR/141025/008167</td>
        </tr>
        <tr>
            <td>Flat Number</td>
            <td><span class="highlight">{tower} - {unit_number}</span></td>
        </tr>
        <tr>
            <td>UDS (in Sqft)</td>
            <td><span class="highlight">{uds}</span></td>
        </tr>
        <tr>
            <td>Super Built-up Area (in Sq ft)</td>
            <td><span class="highlight">{saleable_area}</span></td>
        </tr>
        <tr>
            <td>Total Cost of the Flat including GST</td>
            <td><span class="highlight">Rs. {total_price_formatted}/-</span></td>
        </tr>
    </table>
    
    <div class="section-title">TERMS & CONDITIONS</div>
    
    <div class="terms">
        <p><span class="terms-number">1.</span> In consideration of and subject to the Allottee(s) complying with the terms and conditions of this letter, executing and registering necessary documents and agreements under applicable law, and agreeing to make and making timely payment of amounts due, the developer allots the Flat in the project "{project}" in the favour of <span class="highlight">Mr./Mrs. {customer_name}</span>.</p>
        
        <p><span class="terms-number">2.</span> All payments to be made by A/c Payee Cheque/Banker Cheque/Pay order/Demand Draft at Bangalore only or through Electronic Fund Transfer (EFT) mode drawn in favor of/to the account of "RRL BUILDERS AND DEVELOPERS PVT LTD"</p>
        
        <div class="bank-details">
            <p><strong>Account Holder Name:</strong> RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</p>
            <p><strong>Bank:</strong> HDFC BANK</p>
            <p><strong>Branch:</strong> SOMPURA</p>
            <p><strong>Account Number:</strong> 57500001802063</p>
            <p><strong>IFSC Number:</strong> HDFC0009590</p>
        </div>
        
        <p><span class="terms-number">3.</span> The Allottee shall be liable to pay the total sale consideration (more fully described in the cost sheet) and other charges as specified herein together with the applicable government taxes and levies as per the payment plan annexed herewith, time being of the essence.</p>
        
        <p><span class="terms-number">4.</span> The Allottee has applied for booking and allotment of Flat being fully aware of the cost of the Flat, and also of the tax regime of GST. The Applicant also confirms that he/she shall not claim any GST credit and/or claim any reduction in price of the Flat due to application of GST.</p>
        
        <p><span class="terms-number">5.</span> To avoid penal consequences under the Income Tax Act 1961, the Allottee is required to comply with provisions of section 194IA of the Income Tax Act, 1961, by deduction Tax at Source (TDS) at the prevailing rate from installment/payment. The Allottee shall be required to submit TDS Certificate and challan showing proof of deposition of the same within 7 (Seven) days from the date of tax so deposited to the Developer so that the appropriate credit may be allowed to the account of the Allottee.</p>
        
        <p><span class="terms-number">6.</span> Taxation particulars of Developer is as follows:</p>
        <p style="margin-left: 20px;">PAN No: AAKCR4125J</p>
        <p style="margin-left: 20px;">GST No: 29AAKCR4125J1Z2</p>
        
        <p><span class="terms-number">7.</span> If the upfront advance is paid by cheque, the confirmation of allotment is conditional upon realization of the cheque and funds being credited to the developer's account within 7 (Seven) days of submission of the EOI. In the event the cheque is dishonored for the first time, a sum of Rs.10,000/- (Rupees Ten Thousand Only) will be debited from the Allottee's account in addition to bank charges. In the event such default repeats for the second time, a sum of Rs.20,000/- (Rupees Twenty Thousand Only) will be debited from the Allottee's account in addition to bank charges. In the event such default repeats for the third time, the developer reserves the right to terminate this letter, at sole discretion.</p>
        
        <p><span class="terms-number">8.</span> In the event of cancellation and/or termination of documents and agreements executed and registered pursuant to this Letter, the Allottee agrees to forfeit, in the Developer's favor, the application amount paid by the Allottee plus an amount equal to 5% (Five percent) of the Total Sale Consideration for the allotted Flat and amounts paid by the Allottee on account of applicable GST. The balance amount, if any, shall be refunded to the Allottee, without interest, within 60 (sixty) days from the resale of the unit to a third party.</p>
        
        <p><span class="terms-number">9.</span> Stamp duty and registration charges on actuals and as per prevailing rates shall be payable by the Allottee over and above the Total Sale Consideration.</p>
        
        <p><span class="terms-number">10.</span> In the event any amount by the Allottee is prepaid, the Developer is entitled to retain and adjust the balance/excess amounts received against the next installment due, without paying any interest on such additional amounts.</p>
        
        <p><span class="terms-number">11.</span> For this Project, the schedule of payments is linked to stage-wise completion of the Flat, which schedule has been communicated to and accepted by the Allottee at the time of submitting the EOI. The payment schedule will also be included as an annexure to the agreement of sale.</p>
        
        <p><span class="terms-number">12.</span> Any delay or default in payment by the Allottee will attract penal interest as per the Rules on the Outstanding amount calculated from the applicable due dates till the date of actual receipt.</p>
        
        <p><span class="terms-number">13.</span> This Letter is neither transferable nor assignable, without the Developer's prior written consent and upon payment of including but not limited to such administrative charges as may be specified by the Developer in this regard.</p>
        
        <p><span class="terms-number">14.</span> Pre EMI (Interest Only) will be paid by the builder till the completion of the flat or ready for interior. Rate of interest will be calculated considering 30-year tenure irrespective of client's tenure period.</p>
        
        <p><span class="terms-number">15.</span> <strong>Guidelines for External Vendors:</strong> Should you choose to engage a service provider other than the In-House Team, please be advised that the following security protocols will strictly apply to safeguard the property: Security Deposit of Rs.2,00,000 (Two Lakhs) must be maintained. The flat owner remains fully liable for any damages caused by their vendor to the premises.</p>
        
        <p><span class="terms-number">16.</span> Maintenance will be collected for 12 months, Rs. 3 Per sqft per month, should be paid before registration along with GST 18% on above maintenance. Corpus fund collected for 12 months at Rs. 2.5 Per sqft per month. Car parking will be allotted based on sequential basis.</p>
        
        <p><span class="terms-number">17.</span> These terms and conditions shall be deemed to be an integral part of the duly executed agreement for sale. Any and all disputes in relation to this Letter shall be referred exclusively to the jurisdictional Real Estate Regulatory Authority, for resolution in accordance with applicable procedure.</p>
    </div>
    
    <div class="declaration">
        <p>I/We, <span class="highlight">Mr./Mrs. {customer_name}</span> have fully read and understood the terms and conditions as set out in this Letter and Schedules hereto. I/We undertake to abide by such terms and conditions including any amendment therein from time to time. I/We further declare that the details/information provided in the Letter are true and correct.</p>
    </div>
    
    <div class="signature-section">
        <div class="signature-box">
            <p><strong>FOR RRL BUILDERS AND DEVELOPERS PVT LTD</strong></p>
            <div class="signature-line">
                <p>Authorized Signatory</p>
            </div>
        </div>
        <div class="signature-box">
            <p><strong>ALLOTTEE SIGNATURES</strong></p>
            <div class="signature-line">
                <p>{customer_name}</p>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p><strong>RRL Builders and Developers Pvt. Ltd.</strong></p>
        <p>www.rrlbuildersanddevelopers.com</p>
        <p>Date: {date} | Ref: {customer_id}</p>
    </div>
</body>
</html>
""",
        DocumentType.DISBURSEMENT_LETTER: """
BANK DISBURSEMENT REQUEST LETTER

Date: {date}
To,
The Manager
[Bank Name]
[Branch Address]

Subject: Request for Disbursement of Home Loan for {customer_name}

Dear Sir/Madam,

We hereby request the disbursement of the following amount towards the purchase of property by the below mentioned applicant:

APPLICANT DETAILS:
Name: {customer_name}
PAN: {pan_number}
Phone: {phone}

PROPERTY DETAILS:
Project: {project}
Tower: {tower}
Unit Number: {unit_number}
Agreement Value: Rs. {total_price}/-

The construction has reached the required stage and we request you to process the disbursement.

For RRL Builders and Developers

_______________________
Authorized Signatory
"""
    }
    return templates.get(doc_type, "Template not found")

# ==================== PDF GENERATION ====================
def generate_price_breakup_html(customer: dict) -> str:
    """Generate HTML for Price Breakup PDF with black and gold theme"""
    
    # Format currency in Indian format
    def format_inr(amount):
        """Format amount in Indian Rupee style without L/Cr abbreviations"""
        amount = float(amount) if amount else 0
        int_part = int(amount)
        decimal_part = f"{amount:.2f}".split('.')[1]
        
        # Format with Indian comma system
        s = str(int_part)
        if len(s) > 3:
            result = s[-3:]
            s = s[:-3]
            while s:
                result = s[-2:] + ',' + result
                s = s[:-2]
        else:
            result = s
        
        return f"₹{result}.{decimal_part}"
    
    booking_date = customer.get('booking_date', datetime.now().strftime("%d/%m/%Y"))
    if booking_date and '-' in booking_date:
        try:
            dt = datetime.strptime(booking_date, "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #f5f5f5;
                padding: 30px;
                color: #1A1A1A;
            }}
            
            .container {{
                background: #fff;
                border: 2px solid #D4AF37;
                border-radius: 8px;
                padding: 35px;
                max-width: 800px;
                margin: 0 auto;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 3px solid #D4AF37;
                padding-bottom: 20px;
                margin-bottom: 25px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .logo {{
                width: 55px;
                height: 55px;
                background: #1A1A1A;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #D4AF37;
                font-weight: bold;
                font-size: 20px;
            }}
            
            .company-name {{
                font-size: 20px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 11px;
                color: #666;
            }}
            
            .document-title {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 13px;
                text-transform: uppercase;
            }}
            
            .section {{
                margin-bottom: 20px;
            }}
            
            .section-title {{
                font-size: 14px;
                color: #1A1A1A;
                font-weight: 600;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 2px solid #D4AF37;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }}
            
            .info-item {{
                display: flex;
                justify-content: space-between;
                padding: 8px 10px;
                background: #fafafa;
                border-left: 3px solid #D4AF37;
            }}
            
            .info-label {{
                color: #666;
                font-size: 12px;
            }}
            
            .info-value {{
                color: #1A1A1A;
                font-weight: 500;
                font-size: 12px;
            }}
            
            .price-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            
            .price-table th, .price-table td {{
                padding: 12px;
                text-align: left;
                font-size: 12px;
            }}
            
            .price-table th {{
                background: #1A1A1A;
                color: #D4AF37;
                font-weight: 500;
            }}
            
            .price-table td {{
                border-bottom: 1px solid #e0e0e0;
            }}
            
            .price-table tr:nth-child(even) {{
                background: #fafafa;
            }}
            
            .price-table .total-row {{
                background: #1A1A1A !important;
                color: #D4AF37;
                font-weight: 700;
                font-size: 14px;
            }}
            
            .price-table .amount {{
                text-align: right;
                font-family: 'Roboto Mono', monospace;
            }}
            
            .footer {{
                margin-top: 25px;
                padding-top: 15px;
                border-top: 2px solid #D4AF37;
                font-size: 11px;
                color: #666;
            }}
            
            .footer-note {{
                margin-bottom: 8px;
            }}
            
            .footer-company {{
                margin-top: 15px;
                text-align: center;
                color: #1A1A1A;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-section">
                    <div class="logo">RRL</div>
                    <div>
                        <div class="company-name">RRL Builders and Developers</div>
                        <div class="company-tagline">Beyond homes. A lifestyle</div>
                    </div>
                </div>
                <div class="document-title">Price Break-Up</div>
            </div>
            
            <div class="section">
                <div class="section-title">Customer Details</div>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Name:</span>
                        <span class="info-value">{customer.get('name', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Contact:</span>
                        <span class="info-value">{customer.get('phone', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Email:</span>
                        <span class="info-value">{customer.get('email', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Booking Date:</span>
                        <span class="info-value">{booking_date}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Unit Details</div>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Unit No.:</span>
                        <span class="info-value">{customer.get('unit_number', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Tower:</span>
                        <span class="info-value">{customer.get('tower', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Unit Type:</span>
                        <span class="info-value">{customer.get('bhk_type', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Floor:</span>
                        <span class="info-value">{customer.get('floor', '-')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Saleable Area:</span>
                        <span class="info-value">{customer.get('saleable_area', 0)} sq.ft</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">UDS:</span>
                        <span class="info-value">{customer.get('uds', 0)}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Rate/Sq.ft:</span>
                        <span class="info-value">₹{customer.get('rate_per_sqft', 0):,.0f}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Price Breakdown</div>
                <table class="price-table">
                    <thead>
                        <tr>
                            <th>Particulars</th>
                            <th class="amount">Amount (₹)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Base Price ({customer.get('saleable_area', 0)} sq.ft × ₹{customer.get('rate_per_sqft', 0):,.0f})</td>
                            <td class="amount">{format_inr(customer.get('base_price', 0))}</td>
                        </tr>
                        <tr>
                            <td>Club House, Infrastructure & One Covered Car Parking</td>
                            <td class="amount">{format_inr(customer.get('club_house_charges', 200000))}</td>
                        </tr>
                        <tr>
                            <td>Additional Car Parking ({customer.get('additional_parking', 0)} nos.)</td>
                            <td class="amount">{format_inr(customer.get('additional_parking_charges', 0))}</td>
                        </tr>
                        <tr>
                            <td>Labour Cess (0.70%)</td>
                            <td class="amount">{format_inr(customer.get('labour_cess', 0))}</td>
                        </tr>
                        <tr>
                            <td>GST (5%)</td>
                            <td class="amount">{format_inr(customer.get('gst_amount', 0))}</td>
                        </tr>
                        <tr class="total-row">
                            <td><strong>GRAND TOTAL</strong></td>
                            <td class="amount"><strong>{format_inr(customer.get('total_price', 0))}</strong></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <div class="footer">
                <p class="footer-note">* Maintenance charges will attract GST as applicable</p>
                <p class="footer-note">* Registration as per government norms</p>
                <p class="footer-company">
                    <strong>RRL Builders and Developers Pvt. Ltd.</strong><br>
                    www.rrlbuildersanddevelopers.com<br>
                    Thank you for choosing RRL Palm Altezze
                </p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html


def generate_cost_breakup_html(customer: dict) -> str:
    """Generate HTML for Cost Breakup PDF matching the user-provided template"""
    
    # Format currency in Indian format
    def format_inr(amount):
        """Format amount in Indian Rupee style without decimal places for cleaner look"""
        amount = float(amount) if amount else 0
        int_part = int(amount)
        
        # Format with Indian comma system
        s = str(int_part)
        if len(s) > 3:
            result = s[-3:]
            s = s[:-3]
            while s:
                result = s[-2:] + ',' + result
                s = s[:-2]
        else:
            result = s
        
        return result
    
    def number_to_words(num):
        """Convert number to words in Indian format"""
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
                'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if num == 0:
            return 'Zero'
        
        num = int(num)
        
        if num < 20:
            return ones[num]
        
        if num < 100:
            return tens[num // 10] + ('' if num % 10 == 0 else '-' + ones[num % 10])
        
        if num < 1000:
            return ones[num // 100] + ' Hundred' + ('' if num % 100 == 0 else ' ' + number_to_words(num % 100))
        
        if num < 100000:
            return number_to_words(num // 1000) + ' Thousand' + ('' if num % 1000 == 0 else ' ' + number_to_words(num % 1000))
        
        if num < 10000000:
            return number_to_words(num // 100000) + ' Lakh' + ('' if num % 100000 == 0 else ' ' + number_to_words(num % 100000))
        
        return number_to_words(num // 10000000) + ' Crore' + ('' if num % 10000000 == 0 else ' ' + number_to_words(num % 10000000))
    
    # Get customer details
    name = customer.get('name', '')
    co_applicant_name = customer.get('co_applicant_name', '')
    age = customer.get('age', '')
    co_applicant_age = customer.get('co_applicant_age', '')
    
    # Build customer text
    customer_text_parts = []
    if name:
        if customer.get('gender') == 'female':
            prefix = "Mrs." if customer.get('marital_status') == 'married' else "Ms."
        else:
            prefix = "Mr."
        age_text = f" aged about {age} years" if age else ""
        customer_text_parts.append(f"{prefix} {name}{age_text}")
    
    if co_applicant_name:
        co_age_text = f" aged about {co_applicant_age} years" if co_applicant_age else ""
        co_prefix = "Mrs." if customer.get('co_applicant_gender') == 'female' else "Mr."
        customer_text_parts.append(f"{co_prefix} {co_applicant_name}{co_age_text}")
    
    customer_names = " and ".join(customer_text_parts) if customer_text_parts else "Customer"
    
    # Property details
    flat_no = customer.get('unit_number', '-')
    tower = customer.get('tower', '1')
    saleable_area = customer.get('saleable_area', 0)
    uds = customer.get('uds', 0)
    # Estimate carpet area (approx 62.5% of saleable area)
    carpet_area = round(saleable_area * 0.625, 2) if saleable_area else 0
    
    # Pricing components mapping to cost breakup
    basic_cost = customer.get('base_price', 0)
    bescom = customer.get('infrastructure_charges', 150000)  # Default 1.5L for BESCOM
    car_parking = customer.get('additional_charges', 200000)  # Default 2L for car parking
    amenities = customer.get('club_house_charges', 150000)  # Amenities
    
    # Total - either use stored total or calculate
    total_value = customer.get('total_price', 0)
    if not total_value:
        total_value = basic_cost + bescom + car_parking + amenities
    
    # Get date
    booking_date = customer.get('booking_date', datetime.now().strftime("%Y-%m-%d"))
    if booking_date and '-' in str(booking_date):
        try:
            dt = datetime.strptime(str(booking_date), "%Y-%m-%d")
            date_display = dt.strftime("%d - %m - %Y")
        except (ValueError, TypeError):
            date_display = datetime.now().strftime("%d - %m - %Y")
    else:
        date_display = datetime.now().strftime("%d - %m - %Y")
    
    # Total in words
    total_words = f"Rupees {number_to_words(total_value)} Only"
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            @page {{
                size: A4;
                margin: 25mm 20mm 25mm 20mm;
            }}
            
            body {{
                font-family: 'Roboto', sans-serif;
                font-size: 12px;
                line-height: 1.6;
                color: #1A1A1A;
                background: #fff;
            }}
            
            .container {{
                max-width: 100%;
            }}
            
            .header {{
                text-align: right;
                margin-bottom: 30px;
                padding-bottom: 15px;
                border-bottom: 3px solid #D4AF37;
            }}
            
            .header-title {{
                font-size: 22px;
                font-weight: 700;
                color: #1A1A1A;
                margin-bottom: 5px;
            }}
            
            .header-subtitle {{
                font-size: 16px;
                font-weight: 600;
                color: #D4AF37;
            }}
            
            .customer-info {{
                margin-bottom: 25px;
                text-align: justify;
                font-size: 12px;
            }}
            
            .site-address {{
                margin-bottom: 25px;
            }}
            
            .site-address-title {{
                font-weight: 700;
                margin-bottom: 5px;
                font-size: 12px;
            }}
            
            .site-address-text {{
                font-size: 11px;
                color: #444;
            }}
            
            .price-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 25px 0;
            }}
            
            .price-table th {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 12px 15px;
                text-align: left;
                font-weight: 600;
                font-size: 13px;
                text-transform: uppercase;
            }}
            
            .price-table th.amount {{
                text-align: right;
            }}
            
            .price-table td {{
                padding: 10px 15px;
                border-bottom: 1px solid #e0e0e0;
                font-size: 12px;
            }}
            
            .price-table td.amount {{
                text-align: right;
                font-family: 'Roboto Mono', monospace;
                font-weight: 500;
            }}
            
            .price-table tr:nth-child(even) {{
                background: #f9f9f9;
            }}
            
            .price-table .total-row {{
                background: #1A1A1A !important;
            }}
            
            .price-table .total-row td {{
                color: #D4AF37;
                font-weight: 700;
                font-size: 14px;
                border-bottom: none;
            }}
            
            .total-words {{
                margin: 25px 0;
                font-size: 12px;
                text-align: justify;
            }}
            
            .total-words strong {{
                color: #D4AF37;
            }}
            
            .thank-you {{
                margin: 25px 0;
                font-size: 12px;
            }}
            
            .date-section {{
                margin-top: 30px;
                font-size: 12px;
            }}
            
            .footer {{
                margin-top: 40px;
                padding-top: 15px;
                border-top: 2px solid #D4AF37;
                text-align: center;
                font-size: 11px;
                color: #666;
            }}
            
            .footer strong {{
                color: #1A1A1A;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="header-title">RRL PALM ALTEZZE</div>
                <div class="header-subtitle">Cost Break Up</div>
            </div>
            
            <div class="customer-info">
                {customer_names} purchased Flat No. {flat_no}, Tower-{tower} measuring Super Builtup Area {saleable_area} Sq.ft. with UDS of {uds:.2f} Sq.ft, Carpet Area of {carpet_area} Sq.ft,
            </div>
            
            <div class="site-address">
                <div class="site-address-title">Site Address:</div>
                <div class="site-address-text">
                    Sy No. 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087.
                </div>
            </div>
            
            <table class="price-table">
                <thead>
                    <tr>
                        <th>PARTICULARS</th>
                        <th class="amount">AMOUNT</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>BASIC COST</td>
                        <td class="amount">{format_inr(basic_cost)}</td>
                    </tr>
                    <tr>
                        <td>BESCOM</td>
                        <td class="amount">{format_inr(bescom)}</td>
                    </tr>
                    <tr>
                        <td>CAR PARKING</td>
                        <td class="amount">{format_inr(car_parking)}</td>
                    </tr>
                    <tr>
                        <td>AMENITIES</td>
                        <td class="amount">{format_inr(amenities)}</td>
                    </tr>
                    <tr class="total-row">
                        <td><strong>TOTAL</strong></td>
                        <td class="amount"><strong>{format_inr(total_value)}</strong></td>
                    </tr>
                </tbody>
            </table>
            
            <div class="total-words">
                Total Sale Value is <strong>Rs. {format_inr(total_value)} /-</strong> ({total_words}).
            </div>
            
            <div class="thank-you">
                Thanking You.
            </div>
            
            <div class="date-section">
                Date : {date_display}
            </div>
            
            <div class="footer">
                <strong>RRL Builders and Developers Pvt. Ltd.</strong><br>
                www.rrlbuildersanddevelopers.com
            </div>
        </div>
    </body>
    </html>
    '''
    return html


# ==================== BANK NOC DOCUMENT GENERATORS ====================

def generate_noc_hdfc_html(customer: dict) -> str:
    """Generate HDFC Bank NOC (No Objection Certificate) for disbursement"""
    
    def format_inr(amount):
        """Format amount in Indian Rupee style"""
        amount = float(amount) if amount else 0
        return "{:,.0f}".format(amount).replace(",", ",")
    
    def number_to_words(num):
        """Convert number to words in Indian format"""
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
                'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if num == 0:
            return 'Zero'
        num = int(num)
        if num < 20:
            return ones[num]
        if num < 100:
            return tens[num // 10] + ('' if num % 10 == 0 else ' ' + ones[num % 10])
        if num < 1000:
            return ones[num // 100] + ' Hundred' + ('' if num % 100 == 0 else ' ' + number_to_words(num % 100))
        if num < 100000:
            return number_to_words(num // 1000) + ' Thousand' + ('' if num % 1000 == 0 else ' ' + number_to_words(num % 1000))
        if num < 10000000:
            return number_to_words(num // 100000) + ' Lakh' + ('' if num % 100000 == 0 else ' ' + number_to_words(num % 100000))
        return number_to_words(num // 10000000) + ' Crore' + ('' if num % 10000000 == 0 else ' ' + number_to_words(num % 10000000))
    
    # Customer details
    name = customer.get('name', '')
    co_applicant_name = customer.get('co_applicant_name', '')
    
    # Build customer names string
    if co_applicant_name:
        customer_names = f"Mr. {name} and Mrs. {co_applicant_name}"
    else:
        customer_names = f"Mr. {name}"
    
    # Property details
    flat_no = customer.get('unit_number', '')
    tower = customer.get('tower', '1')
    floor = customer.get('floor', '')
    floor_text = f"{floor}th" if floor else ""
    
    # Financial details
    total_price = customer.get('total_price', 0) or 0
    booking_amount = customer.get('booking_amount', 0) or 0
    balance = total_price - booking_amount
    loan_amount = customer.get('loan_amount', 0) or balance
    
    # Format amounts with words
    total_price_words = f"Rupees {number_to_words(total_price)} Only"
    booking_words = f"Rupees {number_to_words(booking_amount)} Only"
    balance_words = f"Rupees {number_to_words(balance)} Only"
    loan_words = f"Rupees {number_to_words(loan_amount)} Only"
    
    # Dates
    booking_date = customer.get('booking_date', datetime.now().strftime("%Y-%m-%d"))
    agreement_date = customer.get('agreement_date', booking_date)
    today_date = datetime.now().strftime("%d-%m-%Y")
    
    if agreement_date and '-' in str(agreement_date):
        try:
            dt = datetime.strptime(str(agreement_date), "%Y-%m-%d")
            agreement_display = dt.strftime("%d-%m-%Y")
        except:
            agreement_display = today_date
    else:
        agreement_display = today_date
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            @page {{ size: A4; margin: 25mm 20mm 25mm 20mm; }}
            body {{ font-family: 'Roboto', sans-serif; font-size: 12px; line-height: 1.8; color: #1A1A1A; }}
            .header {{ text-align: right; margin-bottom: 20px; }}
            .header-title {{ font-size: 16px; font-weight: 700; }}
            .date {{ text-align: right; margin-bottom: 20px; }}
            .addressee {{ margin-bottom: 20px; }}
            .addressee p {{ margin: 0; }}
            .salutation {{ margin-bottom: 15px; }}
            .content {{ text-align: justify; margin-bottom: 15px; }}
            .signature {{ margin-top: 40px; }}
            .signature-line {{ margin-top: 30px; font-weight: 500; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-title">Builder NOC</div>
        </div>
        
        <div class="date">Date: {today_date}</div>
        
        <div class="addressee">
            <p>To,</p>
            <p><strong>HDFC BANK LTD</strong></p>
            <p>NO.51, KASTURBA ROAD,</p>
            <p>BANGALORE – 560 001</p>
        </div>
        
        <div class="salutation">Dear Sir,</div>
        
        <div class="content">
            <p>This is to confirm that we have sold Flat No.{flat_no}, Tower-{tower}, {floor_text} Floor in the building called <strong>RRL PALM ALTEZZE</strong> situated at RRL Palm Altezze, SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087, to <strong>{customer_names}</strong> for a total consideration of <strong>Rs.{format_inr(total_price)}/-</strong> ({total_price_words}) out of which <strong>Rs.{format_inr(booking_amount)}/-</strong> ({booking_words}) has been received by us and balance <strong>Rs.{format_inr(balance)}/-</strong> ({balance_words}) is due on {agreement_display}.</p>
            
            <p>We hereby assure you that the said flat appurtenant there to be not subject to any encumbrance, charge, or liability of any kind whatsoever and that the entire property is free and marketable. We further confirm that we have a clear legal and marketable title to the said property and every part thereof.</p>
            
            <p>We have no objection to your giving a loan of <strong>Rs.{format_inr(loan_amount)}/-</strong> ({loan_words}) to said <strong>{customer_names}</strong> owner/s of the said flat and his/their mortgaging the said flat with you by way of security for repayment notwithstanding anything to the contrary contained in our agreement dated {agreement_display} with {customer_names}.</p>
            
            <p>We have taken the construction finance from Bajaj Housing Finance Limited.</p>
            
            <p>We also undertake to inform and give proper notice to the Co-operative Housing Society as and when formed, about the flat being mortgaged. We hereby undertake to forward the original title deed for the undivided share in the land duly registered directly to HDFC without parting the same with the allotee of the flat during the pendency of the loan under intimation to the borrower.</p>
        </div>
        
        <div class="signature">
            <p class="signature-line">Authorized Signatory</p>
            <p style="margin-top: 50px;"><strong>For RRL Builders and Developers Private Limited</strong></p>
        </div>
    </body>
    </html>
    '''
    return html


def generate_noc_bob_html(customer: dict) -> str:
    """Generate Bank of Baroda (BOB) NOC for disbursement"""
    
    def format_inr(amount):
        amount = float(amount) if amount else 0
        return "{:,.0f}".format(amount).replace(",", ",")
    
    def number_to_words(num):
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
                'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if num == 0:
            return 'Zero'
        num = int(num)
        if num < 20:
            return ones[num]
        if num < 100:
            return tens[num // 10] + ('' if num % 10 == 0 else ' ' + ones[num % 10])
        if num < 1000:
            return ones[num // 100] + ' Hundred' + ('' if num % 100 == 0 else ' ' + number_to_words(num % 100))
        if num < 100000:
            return number_to_words(num // 1000) + ' Thousand' + ('' if num % 1000 == 0 else ' ' + number_to_words(num % 1000))
        if num < 10000000:
            return number_to_words(num // 100000) + ' Lakh' + ('' if num % 100000 == 0 else ' ' + number_to_words(num % 100000))
        return number_to_words(num // 10000000) + ' Crore' + ('' if num % 10000000 == 0 else ' ' + number_to_words(num % 10000000))
    
    name = customer.get('name', '')
    co_applicant_name = customer.get('co_applicant_name', '')
    customer_names = f"Mr. {name} and Mrs. {co_applicant_name}" if co_applicant_name else f"Mr. {name}"
    
    flat_no = customer.get('unit_number', '')
    tower = customer.get('tower', '1')
    floor = customer.get('floor', '')
    floor_text = f"{floor}th" if floor else ""
    
    total_price = customer.get('total_price', 0) or 0
    booking_amount = customer.get('booking_amount', 0) or 0
    balance = total_price - booking_amount
    loan_amount = customer.get('loan_amount', 0) or balance
    
    total_price_words = f"Rupees {number_to_words(total_price)} Only"
    booking_words = f"Rupees {number_to_words(booking_amount)} Only"
    balance_words = f"Rupees {number_to_words(balance)} Only"
    loan_words = f"Rupees {number_to_words(loan_amount)} Only"
    
    today_date = datetime.now().strftime("%d-%m-%Y")
    agreement_date = customer.get('agreement_date', customer.get('booking_date', ''))
    if agreement_date and '-' in str(agreement_date):
        try:
            dt = datetime.strptime(str(agreement_date), "%Y-%m-%d")
            agreement_display = dt.strftime("%d-%m-%Y")
        except:
            agreement_display = today_date
    else:
        agreement_display = today_date
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            @page {{ size: A4; margin: 25mm 20mm 25mm 20mm; }}
            body {{ font-family: 'Roboto', sans-serif; font-size: 12px; line-height: 1.8; color: #1A1A1A; }}
            .header {{ text-align: right; margin-bottom: 20px; }}
            .header-title {{ font-size: 16px; font-weight: 700; }}
            .date {{ text-align: right; margin-bottom: 20px; }}
            .addressee {{ margin-bottom: 20px; }}
            .addressee p {{ margin: 0; }}
            .salutation {{ margin-bottom: 15px; }}
            .content {{ text-align: justify; margin-bottom: 15px; }}
            .signature {{ margin-top: 40px; }}
            .signature-line {{ margin-top: 30px; font-weight: 500; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-title">Builder NOC</div>
        </div>
        
        <div class="date">Date: {today_date}</div>
        
        <div class="addressee">
            <p>To,</p>
            <p><strong>The Manager</strong></p>
            <p><strong>Bank of Baroda</strong></p>
            <p>Bangalore</p>
        </div>
        
        <div class="salutation">Dear Sir / Madam,</div>
        
        <div class="content">
            <p>This is to confirm that we have sold Flat No.{flat_no}, Tower-{tower}, {floor_text} Floor in the building called <strong>RRL PALM ALTEZZE</strong> situated at RRL Palm Altezze, SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087, to <strong>{customer_names}</strong> for a total consideration of <strong>Rs.{format_inr(total_price)}/-</strong> ({total_price_words}) out of which <strong>Rs.{format_inr(booking_amount)}/-</strong> ({booking_words}) has been received by us and balance <strong>Rs.{format_inr(balance)}/-</strong> ({balance_words}) is due on {agreement_display}.</p>
            
            <p>We further confirm that we have a clear legal and marketable title to the said property and every part thereof. We have no objection to your giving a loan of <strong>Rs.{format_inr(loan_amount)}/-</strong> ({loan_words}) to said <strong>{customer_names}</strong> owner/s of the said flat and his/their mortgaging the said flat with you by way of security for repayment notwithstanding anything to the contrary contained in our agreement dated {agreement_display} with {customer_names}.</p>
        </div>
        
        <div class="signature">
            <p class="signature-line">Authorized Signatory</p>
            <p style="margin-top: 50px;"><strong>For RRL Builders and Developers Private Limited</strong></p>
        </div>
    </body>
    </html>
    '''
    return html


def generate_noc_tata_html(customer: dict) -> str:
    """Generate TATA Capital Housing Finance NOC for disbursement"""
    
    def format_inr(amount):
        amount = float(amount) if amount else 0
        return "{:,.0f}".format(amount).replace(",", ",")
    
    def number_to_words(num):
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten',
                'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        if num == 0:
            return 'Zero'
        num = int(num)
        if num < 20:
            return ones[num]
        if num < 100:
            return tens[num // 10] + ('' if num % 10 == 0 else ' ' + ones[num % 10])
        if num < 1000:
            return ones[num // 100] + ' Hundred' + ('' if num % 100 == 0 else ' ' + number_to_words(num % 100))
        if num < 100000:
            return number_to_words(num // 1000) + ' Thousand' + ('' if num % 1000 == 0 else ' ' + number_to_words(num % 1000))
        if num < 10000000:
            return number_to_words(num // 100000) + ' Lakh' + ('' if num % 100000 == 0 else ' ' + number_to_words(num % 100000))
        return number_to_words(num // 10000000) + ' Crore' + ('' if num % 10000000 == 0 else ' ' + number_to_words(num % 10000000))
    
    name = customer.get('name', '')
    age = customer.get('age', '')
    co_applicant_name = customer.get('co_applicant_name', '')
    co_applicant_age = customer.get('co_applicant_age', '')
    
    # Build customer names with ages
    customer_parts = []
    if name:
        age_text = f" aged about {age} years" if age else ""
        customer_parts.append(f"Mr. {name}{age_text}")
    if co_applicant_name:
        co_age_text = f" aged about {co_applicant_age} years" if co_applicant_age else ""
        customer_parts.append(f"Mr. {co_applicant_name}{co_age_text}")
    customer_names = " and ".join(customer_parts) if customer_parts else "Customer"
    
    flat_no = customer.get('unit_number', '')
    tower = customer.get('tower', '1')
    floor = customer.get('floor', '')
    floor_text = f"{floor}th" if floor else ""
    
    today_date = datetime.now().strftime("%d-%m-%Y")
    agreement_date = customer.get('agreement_date', customer.get('booking_date', ''))
    if agreement_date and '-' in str(agreement_date):
        try:
            dt = datetime.strptime(str(agreement_date), "%Y-%m-%d")
            agreement_display = dt.strftime("%d %B %Y")
        except:
            agreement_display = datetime.now().strftime("%d %B %Y")
    else:
        agreement_display = datetime.now().strftime("%d %B %Y")
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            @page {{ size: A4; margin: 25mm 20mm 25mm 20mm; }}
            body {{ font-family: 'Roboto', sans-serif; font-size: 12px; line-height: 1.8; color: #1A1A1A; }}
            .header {{ text-align: right; margin-bottom: 20px; }}
            .header-title {{ font-size: 16px; font-weight: 700; }}
            .date {{ text-align: right; margin-bottom: 20px; }}
            .addressee {{ margin-bottom: 20px; }}
            .addressee p {{ margin: 0; }}
            .salutation {{ margin-bottom: 15px; }}
            .content {{ text-align: justify; margin-bottom: 15px; }}
            .re-section {{ margin-bottom: 20px; padding: 10px; background: #f5f5f5; }}
            .signature {{ margin-top: 40px; }}
            .signature-line {{ margin-top: 30px; font-weight: 500; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-title">Builder NOC</div>
        </div>
        
        <div class="date">Date: {today_date}</div>
        
        <div class="addressee">
            <p>To,</p>
            <p><strong>M/S TATA CAPITAL HOUSING FINANCE LIMITED</strong></p>
            <p>Bangalore.</p>
        </div>
        
        <div class="salutation">Dear Sirs,</div>
        
        <div class="re-section">
            <strong>Re:</strong> No Objection Certificate for Mortgaging Flat No.{flat_no}, Tower-{tower}, {floor_text} Floor in the building called RRL PALM ALTEZZE situated at SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087.
        </div>
        
        <div class="content">
            <p>This is to confirm that {customer_names}, is the bonafide owner/s of Flat No.{flat_no}, Tower-{tower}, {floor_text} Floor of the building known as <strong>RRL PALM ALTEZZE</strong> situated at SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087. hereinafter referred to as "Said Property") pursuant to an Agreement of Sale / Conveyance Deed dated {agreement_display}.</p>
            
            <p>We confirm that we have obtained necessary permissions/approvals/sanctions for construction of the said Building from all the concerned competent authorities and the construction of the building as well as flat is in accordance with the approved plans. We assure that the said flat as well as the said building and the land appurtenant thereto are not subject to any encumbrance, charge or liability of any kind whatsoever and that the entire property is free and marketable. We have a clear, legal and marketable title to the Said Property and every part thereof.</p>
            
            <p>We confirm that possession of the said property has been given/shall be given in due course to (i) {customer_names}. We are aware that {customer_names}, has approached Tata Capital Housing Finance Ltd for a loan against the Said Property and Tata Capital Housing Finance Ltd. has agreed to sanction/grant the loan/Overdraft facility ("said Loan") to {customer_names}, to purchase the Said Property and have agreed to mortgage the Said Property in your favour/in favour of your security trustee as security for due repayment of the dues under the said Loan. We hereby confirm that we have no objection to the said {customer_names}, mortgaging the Said Property to your Company/in favour of your security trustee as a security for due repayment of the said Loan.</p>
            
            <p>We hereby agree to note the aforesaid charge in our books in respect of the Said Property and {customer_names}, will not be permitted to transfer, assign, sell off/cancel or in any other way/manner deal with the Said Property prejudicial to your rights/interest as the mortgagee without your prior written consent.</p>
            
            <p>We agree to inform and give proper notice to the Co-operative Society as and when formed, about the Said Property being mortgaged to your Company and to issue the Share certificate directly to your Company.</p>
            
            <p>We have taken construction finance from Bajaj Housing Finance Limited.</p>
        </div>
        
        <div class="signature">
            <p>Yours faithfully</p>
            <p style="margin-top: 50px;"><strong>For RRL Builders and Developers Private Limited</strong></p>
        </div>
    </body>
    </html>
    '''
    return html


def generate_booking_form_preview_html(customer: dict) -> str:
    """Generate a PDF preview of the submitted booking form with all customer data"""
    
    # Format dates
    booking_date = customer.get('booking_date', '')
    if booking_date and '-' in str(booking_date):
        try:
            dt = datetime.strptime(str(booking_date), "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    
    dob = customer.get('date_of_birth', '')
    if dob and '-' in str(dob):
        try:
            dt = datetime.strptime(str(dob), "%Y-%m-%d")
            dob = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    
    # Format amounts
    def format_currency(amount):
        try:
            return f"₹ {float(amount or 0):,.2f}"
        except (ValueError, TypeError):
            return "₹ 0.00"
    
    # Get gender display
    gender = customer.get('gender', '')
    if gender == 'male':
        gender_display = 'Male (S/o)'
    elif gender == 'female':
        gender_display = 'Female (D/o)'
    elif gender == 'spouse':
        gender_display = 'Spouse (W/o)'
    else:
        gender_display = gender or '-'
    
    # Finance type display
    finance_type = customer.get('finance_type', 'self')
    finance_display = {
        'self': 'Self Funded',
        'loan': 'Bank Loan',
        'mixed': 'Mixed (Self + Loan)'
    }.get(finance_type, finance_type)
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #fff;
                padding: 20px 30px;
                margin: 0;
                color: #1A1A1A;
                font-size: 11px;
                line-height: 1.4;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 15px;
                border-bottom: 3px solid #D4AF37;
                margin-bottom: 20px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .logo {{
                width: 45px;
                height: 45px;
                background: linear-gradient(135deg, #1A1A1A 0%, #333 100%);
                color: #D4AF37;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 16px;
                border-radius: 6px;
            }}
            
            .company-name {{
                font-size: 16px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 9px;
                color: #D4AF37;
                font-style: italic;
            }}
            
            .document-title {{
                font-size: 18px;
                font-weight: 700;
                color: #1A1A1A;
                text-align: right;
            }}
            
            .document-subtitle {{
                font-size: 10px;
                color: #666;
                text-align: right;
            }}
            
            .section {{
                margin-bottom: 15px;
                background: #fafafa;
                padding: 12px;
                border-radius: 6px;
                border: 1px solid #eee;
            }}
            
            .section-title {{
                font-size: 12px;
                font-weight: 700;
                color: #1A1A1A;
                border-bottom: 2px solid #D4AF37;
                padding-bottom: 6px;
                margin-bottom: 10px;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 8px;
            }}
            
            .info-grid-2 {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 8px;
            }}
            
            .info-item {{
                padding: 4px 0;
            }}
            
            .info-label {{
                color: #666;
                font-size: 9px;
                display: block;
                margin-bottom: 2px;
            }}
            
            .info-value {{
                font-weight: 500;
                color: #1A1A1A;
                font-size: 11px;
            }}
            
            .highlight {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .price-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 8px;
            }}
            
            .price-table th, .price-table td {{
                padding: 8px;
                text-align: left;
                font-size: 10px;
            }}
            
            .price-table th {{
                background: #1A1A1A;
                color: #D4AF37;
                font-weight: 500;
            }}
            
            .price-table td {{
                border-bottom: 1px solid #e0e0e0;
            }}
            
            .price-table .total-row {{
                background: #1A1A1A !important;
                color: #D4AF37;
                font-weight: 700;
            }}
            
            .price-table .amount {{
                text-align: right;
            }}
            
            .footer {{
                margin-top: 20px;
                padding-top: 10px;
                border-top: 2px solid #D4AF37;
                font-size: 9px;
                color: #666;
            }}
            
            .signature-section {{
                margin-top: 30px;
                display: flex;
                justify-content: space-between;
            }}
            
            .signature-box {{
                text-align: center;
                width: 200px;
            }}
            
            .signature-line {{
                border-top: 1px solid #333;
                margin-top: 40px;
                padding-top: 5px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-section">
                <div class="logo">RRL</div>
                <div>
                    <div class="company-name">RRL Builders and Developers</div>
                    <div class="company-tagline">Beyond homes. A lifestyle</div>
                </div>
            </div>
            <div>
                <div class="document-title">Booking Form Preview</div>
                <div class="document-subtitle">Customer ID: {customer.get('customer_id', '-')}</div>
            </div>
        </div>
        
        <!-- Primary Applicant Details -->
        <div class="section">
            <div class="section-title">Primary Applicant Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Full Name</span>
                    <span class="info-value">{customer.get('name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Father's/Husband's Name</span>
                    <span class="info-value">{customer.get('father_name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Gender</span>
                    <span class="info-value">{gender_display}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Date of Birth</span>
                    <span class="info-value">{dob or '-'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Phone Number</span>
                    <span class="info-value">{customer.get('phone', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Email Address</span>
                    <span class="info-value">{customer.get('email', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">PAN Number</span>
                    <span class="info-value">{customer.get('pan_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Aadhaar Number</span>
                    <span class="info-value">{customer.get('aadhar_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Nationality</span>
                    <span class="info-value">{customer.get('nationality', 'Indian')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Company</span>
                    <span class="info-value">{customer.get('company', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Designation</span>
                    <span class="info-value">{customer.get('designation', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Profession</span>
                    <span class="info-value">{customer.get('profession', '-')}</span>
                </div>
            </div>
            <div class="info-grid-2" style="margin-top: 8px;">
                <div class="info-item">
                    <span class="info-label">Permanent Address</span>
                    <span class="info-value">{customer.get('address', '-')}</span>
                </div>
            </div>
        </div>
        
        <!-- Co-Applicant Details (if exists) -->
        {f"""
        <div class="section">
            <div class="section-title">Co-Applicant Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Full Name</span>
                    <span class="info-value">{customer.get('co_applicant_name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Father's/Husband's Name</span>
                    <span class="info-value">{customer.get('co_applicant_father_name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Phone Number</span>
                    <span class="info-value">{customer.get('co_applicant_phone', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Email Address</span>
                    <span class="info-value">{customer.get('co_applicant_email', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">PAN Number</span>
                    <span class="info-value">{customer.get('co_applicant_pan', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Aadhaar Number</span>
                    <span class="info-value">{customer.get('co_applicant_aadhar', '-')}</span>
                </div>
            </div>
            <div class="info-grid-2" style="margin-top: 8px;">
                <div class="info-item">
                    <span class="info-label">Address</span>
                    <span class="info-value">{customer.get('co_applicant_address', '-')}</span>
                </div>
            </div>
        </div>
        """ if customer.get('co_applicant_name') else ''}
        
        <!-- Property Details -->
        <div class="section">
            <div class="section-title">Property Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Project</span>
                    <span class="info-value highlight">{customer.get('project', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Tower</span>
                    <span class="info-value">{customer.get('tower', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Unit Number</span>
                    <span class="info-value highlight">{customer.get('unit_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">BHK Type</span>
                    <span class="info-value">{customer.get('bhk_type', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Floor</span>
                    <span class="info-value">{customer.get('floor', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Saleable Area</span>
                    <span class="info-value">{customer.get('saleable_area', 0)} sq.ft</span>
                </div>
                <div class="info-item">
                    <span class="info-label">UDS</span>
                    <span class="info-value">{customer.get('uds', '-')} sq.ft</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Parking</span>
                    <span class="info-value">{customer.get('parking', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Additional Parking</span>
                    <span class="info-value">{customer.get('additional_parking', 0)}</span>
                </div>
            </div>
        </div>
        
        <!-- Price Details -->
        <div class="section">
            <div class="section-title">Price Details</div>
            <table class="price-table">
                <tr>
                    <th>Description</th>
                    <th class="amount">Amount</th>
                </tr>
                <tr>
                    <td>Rate per sq.ft</td>
                    <td class="amount">{format_currency(customer.get('rate_per_sqft', 0))}</td>
                </tr>
                <tr>
                    <td>Base Price ({customer.get('saleable_area', 0)} sq.ft × {format_currency(customer.get('rate_per_sqft', 0))})</td>
                    <td class="amount">{format_currency(customer.get('base_price', 0))}</td>
                </tr>
                <tr>
                    <td>Floor Rise Total</td>
                    <td class="amount">{format_currency(customer.get('floor_rise_total', 0))}</td>
                </tr>
                <tr>
                    <td>Club House Charges</td>
                    <td class="amount">{format_currency(customer.get('club_house_charges', 200000))}</td>
                </tr>
                <tr>
                    <td>Additional Charges</td>
                    <td class="amount">{format_currency(customer.get('additional_charges', 0))}</td>
                </tr>
                <tr>
                    <td>Labour Cess (0.70%)</td>
                    <td class="amount">{format_currency(customer.get('labour_cess', 0))}</td>
                </tr>
                <tr>
                    <td>GST (5%)</td>
                    <td class="amount">{format_currency(customer.get('gst_amount', 0))}</td>
                </tr>
                <tr class="total-row">
                    <td><strong>Total Flat Value</strong></td>
                    <td class="amount"><strong>{format_currency(customer.get('total_price', 0))}</strong></td>
                </tr>
            </table>
        </div>
        
        <!-- Booking & Finance Details -->
        <div class="section">
            <div class="section-title">Booking & Finance Details</div>
            <div class="info-grid">
                <div class="info-item">
                    <span class="info-label">Booking Date</span>
                    <span class="info-value">{booking_date or '-'}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Booking Amount</span>
                    <span class="info-value highlight">{format_currency(customer.get('booking_amount', 0))}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Finance Type</span>
                    <span class="info-value">{finance_display}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Finance Bank</span>
                    <span class="info-value">{customer.get('finance_bank', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Transaction Reference</span>
                    <span class="info-value">{customer.get('transaction_details', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Transaction Bank</span>
                    <span class="info-value">{customer.get('transaction_bank', '-')}</span>
                </div>
            </div>
            {f'<div class="info-item" style="margin-top: 8px;"><span class="info-label">Remarks</span><span class="info-value">{customer.get("remarks", "-")}</span></div>' if customer.get('remarks') else ''}
        </div>
        
        <!-- Signature Section -->
        <div class="signature-section">
            <div class="signature-box">
                <div class="signature-line">Customer Signature</div>
            </div>
            <div class="signature-box">
                <div class="signature-line">For RRL Builders</div>
            </div>
        </div>
        
        <div class="footer">
            <p>This is a system-generated booking form preview. Please verify all details are correct.</p>
            <p><strong>RRL Builders and Developers Pvt. Ltd.</strong> | www.rrlbuilders.in</p>
        </div>
    </body>
    </html>
    '''
    return html


def generate_terms_and_conditions_html(customer: dict) -> str:
    """Generate a Terms and Conditions PDF with the allotment letter terms"""
    
    project = customer.get('project', 'RRL Palm Altezze')
    customer_name = customer.get('name', 'Customer')
    unit_number = customer.get('unit_number', '')
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #fff;
                padding: 20px 35px;
                margin: 0;
                color: #1A1A1A;
                font-size: 10px;
                line-height: 1.5;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding-bottom: 15px;
                border-bottom: 3px solid #D4AF37;
                margin-bottom: 20px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .logo {{
                width: 40px;
                height: 40px;
                background: linear-gradient(135deg, #1A1A1A 0%, #333 100%);
                color: #D4AF37;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 14px;
                border-radius: 6px;
            }}
            
            .company-name {{
                font-size: 14px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 8px;
                color: #D4AF37;
                font-style: italic;
            }}
            
            .document-title {{
                font-size: 16px;
                font-weight: 700;
                color: #1A1A1A;
                text-align: right;
            }}
            
            .intro {{
                margin-bottom: 15px;
                padding: 10px;
                background: #f9f9f9;
                border-left: 3px solid #D4AF37;
            }}
            
            .terms-list {{
                counter-reset: term-counter;
            }}
            
            .term-item {{
                margin-bottom: 10px;
                padding: 8px 10px;
                background: #fafafa;
                border-radius: 4px;
                border-left: 2px solid #e0e0e0;
            }}
            
            .term-item:hover {{
                border-left-color: #D4AF37;
            }}
            
            .term-number {{
                display: inline-block;
                width: 20px;
                height: 20px;
                background: #1A1A1A;
                color: #D4AF37;
                border-radius: 50%;
                text-align: center;
                line-height: 20px;
                font-weight: 600;
                font-size: 9px;
                margin-right: 8px;
            }}
            
            .term-text {{
                display: inline;
            }}
            
            .highlight {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .bank-details {{
                margin: 10px 0;
                padding: 8px;
                background: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }}
            
            .bank-details p {{
                margin: 3px 0;
            }}
            
            .acceptance {{
                margin-top: 20px;
                padding: 12px;
                background: #1A1A1A;
                color: #fff;
                border-radius: 6px;
            }}
            
            .acceptance .highlight {{
                color: #D4AF37;
            }}
            
            .signature-section {{
                margin-top: 30px;
                display: flex;
                justify-content: space-between;
            }}
            
            .signature-box {{
                text-align: center;
                width: 180px;
            }}
            
            .signature-line {{
                border-top: 1px solid #333;
                margin-top: 35px;
                padding-top: 5px;
                font-size: 9px;
            }}
            
            .footer {{
                margin-top: 15px;
                padding-top: 10px;
                border-top: 2px solid #D4AF37;
                font-size: 8px;
                color: #666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo-section">
                <div class="logo">RRL</div>
                <div>
                    <div class="company-name">RRL Builders and Developers</div>
                    <div class="company-tagline">Beyond homes. A lifestyle</div>
                </div>
            </div>
            <div class="document-title">Terms & Conditions</div>
        </div>
        
        <div class="intro">
            <p>The following Terms and Conditions govern the allotment of <span class="highlight">Unit No. {unit_number}</span> 
            in project <span class="highlight">{project}</span> to <span class="highlight">Mr./Mrs. {customer_name}</span>. 
            Please read carefully and acknowledge your understanding and acceptance.</p>
        </div>
        
        <div class="terms-list">
            <div class="term-item">
                <span class="term-number">1</span>
                <span class="term-text">In consideration of and subject to the Allottee(s) complying with the terms and conditions of this letter, executing and registering necessary documents and agreements under applicable law, and agreeing to make and making timely payment of amounts due, the developer allots the Flat in the project "{project}" in the favour of <span class="highlight">Mr./Mrs. {customer_name}</span>.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">2</span>
                <span class="term-text">All payments to be made by A/c Payee Cheque/Banker Cheque/Pay order/Demand Draft at Bangalore only or through Electronic Fund Transfer (EFT) mode drawn in favor of/to the account of <strong>"RRL BUILDERS AND DEVELOPERS PVT LTD"</strong></span>
                <div class="bank-details">
                    <p><strong>Bank:</strong> Axis Bank</p>
                    <p><strong>Account No:</strong> 922020009963054</p>
                    <p><strong>IFSC:</strong> UTIB0001504</p>
                    <p><strong>Branch:</strong> Kudlu Gate, Bangalore</p>
                </div>
            </div>
            
            <div class="term-item">
                <span class="term-number">3</span>
                <span class="term-text">The Allottee shall be liable to pay the total sale consideration (more fully described in the cost sheet) and other charges as specified herein together with the applicable government taxes and levies as per the payment plan annexed herewith, time being of the essence.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">4</span>
                <span class="term-text">The Allottee has applied for booking and allotment of Flat being fully aware of the cost of the Flat, and also of the tax regime of GST. The Applicant also confirms that he/she shall not claim any GST credit and/or claim any reduction in price of the Flat due to application of GST.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">5</span>
                <span class="term-text">To avoid penal consequences under the Income Tax Act 1961, the Allottee is required to comply with provisions of section 194IA of the Income Tax Act, 1961, by deduction Tax at Source (TDS) at the prevailing rate from installment/payment. The Allottee shall be required to submit TDS Certificate and challan showing proof of deposition of the same within 7 (Seven) days from the date of tax so deposited to the Developer.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">6</span>
                <span class="term-text">Taxation particulars of Developer: PAN - AADCR1969A | GST - 29AADCR1969A1ZW</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">7</span>
                <span class="term-text">If the upfront advance is paid by cheque, the confirmation of allotment is conditional upon realization of the cheque and funds being credited to the developer's account within 7 (Seven) days. In the event the cheque is dishonored, penalty charges will apply as per company policy.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">8</span>
                <span class="term-text">In the event of cancellation and/or termination, the Allottee agrees to forfeit, in the Developer's favor, the application amount paid plus an amount equal to 5% (Five percent) of the Total Sale Consideration and GST amounts paid. The balance amount shall be refunded within 60 days from the resale of the unit.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">9</span>
                <span class="term-text">Stamp duty and registration charges on actuals and as per prevailing rates shall be payable by the Allottee over and above the Total Sale Consideration.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">10</span>
                <span class="term-text">In the event any amount by the Allottee is prepaid, the Developer is entitled to retain and adjust the balance/excess amounts received against the next installment due, without paying any interest on such additional amounts.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">11</span>
                <span class="term-text">For this Project, the schedule of payments is linked to stage-wise completion of the Flat. The payment schedule will also be included as an annexure to the agreement of sale.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">12</span>
                <span class="term-text">Any delay or default in payment by the Allottee will attract penal interest as per the Rules on the Outstanding amount calculated from the applicable due dates till the date of actual receipt.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">13</span>
                <span class="term-text">This Letter is neither transferable nor assignable, without the Developer's prior written consent and upon payment of administrative charges as may be specified.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">14</span>
                <span class="term-text">Pre EMI (Interest Only) will be paid by the builder till the completion of the flat or ready for interior. Rate of interest will be calculated considering 30-year tenure irrespective of client's tenure period.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">15</span>
                <span class="term-text"><strong>Guidelines for External Vendors:</strong> Should you choose to engage a service provider other than the In-House Team, please be advised that a Security Deposit of Rs.2,00,000 (Two Lakhs) must be maintained. The flat owner remains fully liable for any damages caused by their vendor to the premises.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">16</span>
                <span class="term-text">Maintenance will be collected for 12 months at Rs. 3 Per sqft per month, payable before registration along with GST 18%. Corpus fund collected for 12 months at Rs. 2.5 Per sqft per month. Car parking will be allotted on sequential basis.</span>
            </div>
            
            <div class="term-item">
                <span class="term-number">17</span>
                <span class="term-text">These terms and conditions shall be deemed to be an integral part of the duly executed agreement for sale. Any disputes shall be referred exclusively to the jurisdictional Real Estate Regulatory Authority (RERA Karnataka).</span>
            </div>
        </div>
        
        <div class="acceptance">
            <p>I/We, <span class="highlight">Mr./Mrs. {customer_name}</span> have fully read and understood the terms and conditions as set out in this document. I/We undertake to abide by such terms and conditions including any amendment therein from time to time. I/We further declare that the details/information provided are true and correct.</p>
        </div>
        
        <div class="signature-section">
            <div class="signature-box">
                <div class="signature-line">Customer Signature</div>
            </div>
            <div class="signature-box">
                <div class="signature-line">Co-Applicant Signature</div>
            </div>
            <div class="signature-box">
                <div class="signature-line">For RRL Builders</div>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>RRL Builders and Developers Pvt. Ltd.</strong></p>
            <p>RERA No: PRM/KA/RERA/1251/308/PR/141025/008167 | CIN: U70109KA2015PTC081706</p>
            <p>www.rrlbuilders.in</p>
        </div>
    </body>
    </html>
    '''
    return html


def generate_welcome_email_html(customer: dict) -> str:
    """Generate the welcome email HTML with black and gold theme"""
    
    booking_date = customer.get('booking_date', datetime.now().strftime("%d/%m/%Y"))
    if booking_date and '-' in booking_date:
        try:
            dt = datetime.strptime(booking_date, "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except (ValueError, TypeError):
            pass
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #f5f5f5;
                padding: 30px;
                margin: 0;
                color: #1A1A1A;
            }}
            
            .email-container {{
                background: #fff;
                border: 2px solid #D4AF37;
                border-radius: 8px;
                padding: 35px 45px;
                max-width: 700px;
                margin: 0 auto;
                line-height: 1.8;
            }}
            
            .header {{
                display: flex;
                align-items: center;
                gap: 15px;
                padding-bottom: 20px;
                border-bottom: 3px solid #D4AF37;
                margin-bottom: 25px;
            }}
            
            .logo {{
                width: 50px;
                height: 50px;
                background: #1A1A1A;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #D4AF37;
                font-weight: bold;
                font-size: 18px;
            }}
            
            .company-info {{
                flex: 1;
            }}
            
            .company-name {{
                font-size: 18px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 11px;
                color: #666;
            }}
            
            .greeting {{
                font-size: 18px;
                color: #1A1A1A;
                margin-bottom: 20px;
            }}
            
            .greeting span {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .flat-highlight {{
                color: #D4AF37;
                font-weight: 600;
            }}
            
            .residence-details {{
                margin: 25px 0;
                padding: 20px 25px;
                background: #fafafa;
                border-left: 4px solid #D4AF37;
                border-radius: 0 8px 8px 0;
            }}
            
            .residence-details-title {{
                display: block;
                margin-bottom: 18px;
                color: #1A1A1A;
                font-size: 15px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                padding-bottom: 10px;
                border-bottom: 1px solid #e0e0e0;
            }}
            
            .detail-row {{
                display: table;
                width: 100%;
                margin: 12px 0;
                font-size: 14px;
            }}
            
            .detail-label {{
                display: table-cell;
                width: 40%;
                color: #666;
                padding: 8px 0;
            }}
            
            .detail-value {{
                display: table-cell;
                width: 60%;
                font-weight: 500;
                color: #D4AF37;
                padding: 8px 0;
                text-align: right;
            }}
            
            p {{
                margin-bottom: 18px;
                color: #333;
                font-size: 14px;
            }}
            
            .signature-section {{
                margin-top: 30px;
                padding: 20px;
                background: #fafafa;
                border-radius: 8px;
            }}
            
            .signature-name {{
                font-size: 15px;
                font-weight: 600;
                color: #1A1A1A;
                margin-bottom: 3px;
            }}
            
            .signature-title {{
                font-size: 12px;
                color: #D4AF37;
                font-weight: 500;
                margin-bottom: 12px;
            }}
            
            .signature-contact {{
                font-size: 12px;
                color: #666;
                line-height: 1.6;
            }}
            
            .signature-contact a {{
                color: #D4AF37;
                text-decoration: none;
            }}
            
            .footer {{
                margin-top: 25px;
                padding-top: 20px;
                border-top: 2px solid #D4AF37;
                text-align: center;
                font-size: 12px;
                color: #666;
            }}
            
            .footer-link {{
                color: #D4AF37;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="logo">RRL</div>
                <div class="company-info">
                    <div class="company-name">RRL Builders and Developers</div>
                    <div class="company-tagline">Beyond homes. A lifestyle</div>
                </div>
            </div>
            
            <p class="greeting">Dear <span>{customer.get('name', 'Valued Customer')}</span>,</p>
            
            <p><strong>Greetings From RRL Builders and Developers Pvt Ltd.</strong></p>
            
            <p>It is our distinct pleasure to welcome you to {customer.get('project', 'RRL Palm Altezze')} and to congratulate you on the acquisition of your Residence <span class="flat-highlight">Flat No. {customer.get('unit_number', '')}</span>.</p>
            
            <p>Your decision reflects a refined appreciation for exceptional design, uncompromising quality, and a lifestyle that goes beyond the ordinary. At RRL Builders and Developers Pvt Ltd, we create homes not merely as living spaces, but as enduring legacies—crafted with precision, discretion, and timeless elegance.</p>
            
            <p>{customer.get('project', 'RRL Palm Altezze')} has been envisioned for a select few who value privacy, sophistication, and exclusivity. Every element of your residence—from architecture and materials to amenities and services—has been thoughtfully curated to offer a living experience of rare distinction.</p>
            
            <div class="residence-details">
                <span class="residence-details-title">Residence Details</span>
                
                <div class="detail-row">
                    <span class="detail-label">Project</span>
                    <span class="detail-value">{customer.get('project', 'RRL PALM ALTEZZE').upper()}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">Residence</span>
                    <span class="detail-value">Flat No. {customer.get('unit_number', '')}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">Configuration</span>
                    <span class="detail-value">{customer.get('bhk_type', '').upper()}</span>
                </div>
                
                <div class="detail-row">
                    <span class="detail-label">Booking Date</span>
                    <span class="detail-value">{booking_date}</span>
                </div>
            </div>
            
            <p>Your dedicated Relationship Director will connect with you personally to ensure that every interaction with us is seamless and tailored to your expectations. We remain committed to delivering not only an exceptional home, but also an ownership experience defined by transparency, attention to detail, and quiet excellence.</p>
            
            <p>Please find attached the Price Breakup document for your reference.</p>
            
            <div class="signature-section">
                <div class="signature-name">John</div>
                <div class="signature-title">CRM MANAGER</div>
                <div class="signature-contact">
                    <strong>P:</strong> 9606579135<br>
                    <strong>E:</strong> <a href="mailto:crm@rrlbuildersanddevelopers.com">crm@rrlbuildersanddevelopers.com</a><br>
                    <strong>A:</strong> 4TH Floor, RRL Tower, Sompura gate, Sarjapura Bengaluru - 562125<br><br>
                    <a href="https://www.rrlbuildersanddevelopers.com">www.rrlbuildersanddevelopers.com</a>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>RRL Builders and Developers Pvt. Ltd.</strong></p>
                <p><a href="https://www.rrlbuildersanddevelopers.com" class="footer-link">www.rrlbuildersanddevelopers.com</a></p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html
def generate_document_email_html(customer: dict, subject: str, body: str) -> str:
    """Generate email HTML with black and gold theme - same format as welcome mail"""
    
    # Convert body with line breaks to HTML
    body_html = body.replace('\n', '<br>')
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
        </style>
    </head>
    <body style="font-family: 'Roboto', Arial, sans-serif; background: #f5f5f5; padding: 30px; margin: 0; color: #1A1A1A;">
        <div style="background: #fff; border: 2px solid #D4AF37; border-radius: 8px; max-width: 700px; margin: 0 auto; overflow: hidden;">
            <!-- Header -->
            <div style="background: #1A1A1A; padding: 20px; display: flex; align-items: center;">
                <div style="background: #D4AF37; color: #1A1A1A; padding: 10px 15px; border-radius: 6px; font-weight: bold; font-size: 18px; margin-right: 15px;">RRL</div>
                <div>
                    <div style="color: #D4AF37; font-size: 18px; font-weight: 700;">RRL Builders and Developers</div>
                    <div style="color: #999; font-size: 11px;">Beyond homes. A lifestyle</div>
                </div>
            </div>
            
            <!-- Content -->
            <div style="padding: 30px 35px; line-height: 1.8;">
                <div style="font-size: 14px; color: #333;">{body_html}</div>
                
                <!-- Signature -->
                <div style="margin-top: 30px; padding: 20px; background: #fafafa; border-radius: 8px;">
                    <div style="font-size: 15px; font-weight: 600; color: #1A1A1A; margin-bottom: 3px;">John</div>
                    <div style="font-size: 12px; color: #D4AF37; font-weight: 500; margin-bottom: 12px;">CRM MANAGER</div>
                    <div style="font-size: 12px; color: #666; line-height: 1.6;">
                        <strong>P:</strong> 9606579135<br>
                        <strong>E:</strong> <a href="mailto:crm@rrlbuildersanddevelopers.com" style="color: #D4AF37;">crm@rrlbuildersanddevelopers.com</a><br>
                        <strong>A:</strong> 4TH Floor, RRL Tower, Sompura gate, Sarjapura Bengaluru - 562125<br><br>
                        <a href="https://www.rrlbuildersanddevelopers.com" style="color: #D4AF37;">www.rrlbuildersanddevelopers.com</a>
                    </div>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background: #fafafa; padding: 15px; text-align: center; font-size: 11px; color: #888; border-top: 1px solid #e0e0e0;">
                <p style="margin: 0;">RRL Builders and Developers Pvt. Ltd. | <a href="https://www.rrlbuildersanddevelopers.com" style="color: #D4AF37;">www.rrlbuildersanddevelopers.com</a></p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

def generate_sales_agreement_html(customer: dict, schedule_items: list, transactions: list = None) -> str:
    """Generate Sales Agreement HTML with customer data filled in"""
    
    # Helper function to convert year to words
    def year_to_words(year):
        """Convert year like 2026 to 'Two Thousand and Twenty Six'"""
        ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
                'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
                'Seventeen', 'Eighteen', 'Nineteen']
        tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']
        
        year = int(year)
        thousands = year // 1000
        hundreds = (year % 1000) // 100
        remainder = year % 100
        
        result = []
        if thousands == 2:
            result.append("Two Thousand")
        elif thousands == 1:
            result.append("One Thousand")
        
        if hundreds > 0:
            result.append(ones[hundreds] + " Hundred")
        
        if remainder > 0:
            if result:
                result.append("and")
            if remainder < 20:
                result.append(ones[remainder])
            else:
                tens_word = tens[remainder // 10]
                ones_word = ones[remainder % 10]
                if ones_word:
                    result.append(tens_word + " " + ones_word)
                else:
                    result.append(tens_word)
        
        return " ".join(result)
    
    # Format dates - "14th Day of February, Two Thousand and Twenty Six- (14-02-2026)"
    agreement_date = datetime.now()
    day_ordinal = str(agreement_date.day) + get_ordinal_suffix(agreement_date.day)
    month_name = agreement_date.strftime("%B")
    year_words = year_to_words(agreement_date.year)
    date_numeric = agreement_date.strftime("%d-%m-%Y")
    agreement_date_text = f"{day_ordinal} Day of {month_name}, {year_words}- ({date_numeric})"
    
    possession_date = "30-09-2030"  # Fixed possession date for all agreements
    
    # Format currency amounts
    def fmt(amount):
        return format_indian_currency(amount)
    
    # Calculate age from date_of_birth
    age = ""
    dob = customer.get('date_of_birth')
    if dob:
        try:
            if isinstance(dob, str):
                dob_date = datetime.strptime(dob, "%Y-%m-%d")
            else:
                dob_date = dob
            today = datetime.now()
            age = str(today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day)))
        except:
            age = ""
    
    # Generate salutation based on gender
    # S/o for male, D/o for female, W/o for spouse
    gender = customer.get('gender', '').lower() if customer.get('gender') else 'male'
    if gender == 'female':
        salutation = "D/o"
    elif gender == 'spouse':
        salutation = "W/o"
    else:
        salutation = "S/o"
    
    # Generate floor ordinal (1st, 2nd, 3rd, etc.)
    floor = customer.get('floor', 0) or 0
    floor_int = int(floor) if floor else 0
    floor_ordinal = str(floor_int) + get_ordinal_suffix(floor_int) if floor_int > 0 else "Ground"
    
    # Additional parking text
    additional_parking = customer.get('additional_parking', 0) or 0
    additional_parking_text = f" + {additional_parking} additional parking space(s)" if additional_parking > 0 else ""
    
    # Get AADHAAR number from top-level field (not custom_fields)
    aadhaar_number = customer.get('aadhar_number', '') or customer.get('aadhaar_number', '') or ''
    
    # ==================== PAYMENT SCHEDULE (Milestones from Payment Schedule Tab) ====================
    payment_schedule_rows = ""
    total = customer.get('total_price', 0) or 0
    booking_amount = customer.get('booking_amount', 0) or 0
    cumulative_pct = 0  # Track cumulative percentage
    
    # Use schedule_items from Payment Schedule tab (the 13-point milestone schedule)
    if schedule_items and len(schedule_items) > 0:
        for i, item in enumerate(schedule_items, 1):
            milestone_name = item.get('installment_name', '') or item.get('milestone', '')
            percentage = item.get('percentage', 0) or 0
            amount = item.get('amount', 0) or 0
            cumulative_pct += percentage  # Add to cumulative
            
            # If amount is 0 but we have percentage and total, calculate
            if amount == 0 and percentage > 0 and total > 0:
                amount = total * percentage / 100
            
            payment_schedule_rows += f'''
            <tr>
                <td style="text-align: center;">{i}</td>
                <td>{milestone_name}</td>
                <td style="text-align: center;">{percentage}%</td>
                <td style="text-align: center;">{cumulative_pct}%</td>
                <td class="amount">{fmt(amount)}</td>
            </tr>
            '''
    else:
        # Use default 13-point payment schedule if no schedule_items
        default_milestones = [
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
        cumulative_pct = 0
        for i, (name, pct) in enumerate(default_milestones, 1):
            cumulative_pct += pct
            amount = total * pct / 100 if total > 0 else 0
            payment_schedule_rows += f'''
            <tr>
                <td style="text-align: center;">{i}</td>
                <td>{name}</td>
                <td style="text-align: center;">{pct}%</td>
                <td style="text-align: center;">{cumulative_pct}%</td>
                <td class="amount">{fmt(amount)}</td>
            </tr>
            '''
    
    # ==================== TRANSACTION DETAILS (Booking + Agreement Payments) ====================
    transaction_rows = ""
    total_received_amount = 0
    row_num = 1
    
    # Build transaction rows from actual transaction records
    if transactions and len(transactions) > 0:
        for txn in transactions:
            # Check both legacy 'transaction_type' and new 'transaction_stage' fields
            stage = (txn.get('transaction_stage', '') or txn.get('transaction_type', '') or '').lower()
            # Include booking and agreement stage transactions
            if stage in ['booking', 'booking_amount', 'agreement', 'agreement_amount', 'post_agreement']:
                amount = txn.get('amount', 0) or 0
                total_received_amount += amount
                stage_display = 'Booking' if 'booking' in stage else 'Agreement'
                txn_date = txn.get('transaction_date', '')
                bank = txn.get('bank_name', '') or ''
                txn_no = txn.get('transaction_number', '') or ''
                bank_ref = f"{bank} - {txn_no}" if bank or txn_no else stage_display + " Payment"
                
                transaction_rows += f'''
                <tr>
                    <td style="text-align: center;">{row_num}</td>
                    <td>{txn_date}</td>
                    <td>{stage_display}</td>
                    <td>{bank_ref}</td>
                    <td class="amount">{fmt(amount)}</td>
                </tr>
                '''
                row_num += 1
    
    # Fallback: if no booking transactions found but customer has booking_amount, add it
    if booking_amount > 0 and not any(
        (txn.get('transaction_stage', '') or txn.get('transaction_type', '') or '').lower() in ['booking', 'booking_amount']
        for txn in (transactions or [])
    ):
        total_received_amount += booking_amount
        booking_date_val = customer.get('booking_date', '')
        txn_bank = customer.get('transaction_bank', '') or ''
        txn_ref = customer.get('transaction_details', '') or ''
        bank_ref = f"{txn_bank} - {txn_ref}" if txn_bank or txn_ref else "Booking Payment"
        
        transaction_rows = f'''
        <tr>
            <td style="text-align: center;">1</td>
            <td>{booking_date_val}</td>
            <td>Booking</td>
            <td>{bank_ref}</td>
            <td class="amount">{fmt(booking_amount)}</td>
        </tr>
        ''' + transaction_rows
        # Re-number remaining rows
        row_num += 1
    
    # If no transactions and no booking amount
    if not transaction_rows:
        transaction_rows = '''
        <tr>
            <td colspan="5" style="text-align: center; color: #666; padding: 15px;">No payments received yet</td>
        </tr>
        '''
    
    # Get template and fill in values using string replacement to avoid CSS conflicts
    template = generate_sales_agreement_template()
    
    replacements = {
        '{agreement_date_text}': agreement_date_text,
        '{customer_name}': customer.get('name', ''),
        '{age}': age,
        '{salutation}': salutation,
        '{father_name}': customer.get('father_name', ''),
        '{address}': customer.get('address', ''),
        '{aadhaar_number}': aadhaar_number,
        '{pan_number}': customer.get('pan_number', ''),
        '{phone}': customer.get('phone', ''),
        '{project}': customer.get('project', 'RRL PALM ALTEZZE'),
        '{tower}': customer.get('tower', ''),
        '{unit_number}': customer.get('unit_number', ''),
        '{floor}': str(customer.get('floor', '')),
        '{floor_ordinal}': floor_ordinal,
        '{bhk_type}': customer.get('bhk_type', ''),
        '{saleable_area}': str(customer.get('saleable_area', 0)),
        '{uds}': str(customer.get('uds', 0)),
        '{additional_parking}': str(customer.get('additional_parking', 0)),
        '{additional_parking_text}': additional_parking_text,
        '{base_price_formatted}': fmt(customer.get('base_price', 0)),
        '{club_house_formatted}': fmt(customer.get('club_house_charges', 200000)),
        '{parking_charges_formatted}': fmt(customer.get('additional_parking_charges', 0)),
        '{labour_cess_formatted}': fmt(customer.get('labour_cess', 0)),
        '{gst_formatted}': fmt(customer.get('gst_amount', 0)),
        '{total_price_formatted}': fmt(customer.get('total_price', 0)),
        '{total_price_words}': number_to_indian_words(customer.get('total_price', 0)),
        '{booking_amount_formatted}': fmt(customer.get('booking_amount', 0)),
        '{booking_amount_words}': number_to_indian_words(customer.get('booking_amount', 0)),
        '{booking_date}': customer.get('booking_date', ''),
        '{possession_date}': possession_date,
        '{payment_schedule_rows}': payment_schedule_rows,
        '{transaction_rows}': transaction_rows,
        '{total_received_formatted}': fmt(total_received_amount),
        '{date}': datetime.now().strftime("%d/%m/%Y"),
        '{customer_id}': customer.get('customer_id', '')
    }
    
    filled_html = template
    for placeholder, value in replacements.items():
        filled_html = filled_html.replace(placeholder, str(value))
    
    return filled_html

def generate_allotment_letter_html(customer: dict) -> str:
    """Generate Allotment Letter HTML with customer data filled in"""
    
    # Format booking date
    booking_date = customer.get('booking_date', datetime.now().strftime("%d/%m/%Y"))
    if booking_date and '-' in booking_date:
        try:
            dt = datetime.strptime(booking_date, "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except:
            pass
    
    # Get the allotment letter template
    template = get_default_template(DocumentType.ALLOTMENT_LETTER)
    
    # Use string replacement to avoid CSS brace conflicts
    replacements = {
        '{customer_name}': customer.get('name', ''),
        '{phone}': customer.get('phone', ''),
        '{email}': customer.get('email', ''),
        '{pan_number}': customer.get('pan_number', ''),
        '{booking_date}': booking_date,
        '{unit_number}': customer.get('unit_number', ''),
        '{project}': customer.get('project', 'RRL PALM ALTEZZE'),
        '{tower}': customer.get('tower', ''),
        '{uds}': str(customer.get('uds', 0)),
        '{saleable_area}': str(customer.get('saleable_area', 0)),
        '{total_price_formatted}': format_indian_currency(customer.get('total_price', 0)),
        '{date}': datetime.now().strftime("%d/%m/%Y"),
        '{customer_id}': customer.get('customer_id', '')
    }
    
    filled_html = template
    for placeholder, value in replacements.items():
        filled_html = filled_html.replace(placeholder, str(value))
    
    return filled_html


def generate_payment_schedule_pdf_html(customer: dict, transactions: list = None) -> str:
    """Generate Payment Schedule PDF HTML with customer data and transactions"""
    
    def fmt(amount):
        """Format amount in Indian Rupee style"""
        amount = float(amount) if amount else 0
        int_part = int(amount)
        decimal_part = f"{amount:.2f}".split('.')[1]
        
        s = str(int_part)
        if len(s) > 3:
            result = s[-3:]
            s = s[:-3]
            while s:
                result = s[-2:] + ',' + result
                s = s[:-2]
        else:
            result = s
        
        return f"₹{result}.{decimal_part}"
    
    # Build transactions table
    transactions_rows = ""
    total_received = 0
    
    if transactions and len(transactions) > 0:
        for i, txn in enumerate(transactions, 1):
            amount = txn.get('amount', 0) or 0
            total_received += amount
            txn_date = txn.get('transaction_date', '-')
            bank = txn.get('bank_name', '-') or '-'
            txn_no = txn.get('transaction_number', '-') or '-'
            stage = (txn.get('transaction_stage', '-') or 'Payment').replace('_', ' ').title()
            
            transactions_rows += f'''
            <tr>
                <td style="text-align: center; padding: 10px; border: 1px solid #ddd;">{i}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{txn_date}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{stage}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{bank}</td>
                <td style="padding: 10px; border: 1px solid #ddd;">{txn_no}</td>
                <td style="text-align: right; padding: 10px; border: 1px solid #ddd;">{fmt(amount)}</td>
            </tr>
            '''
    
    total_price = customer.get('total_price', 0) or 0
    balance = total_price - total_received
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; color: #1A1A1A; }}
            .header {{ text-align: center; border-bottom: 3px solid #D4AF37; padding-bottom: 20px; margin-bottom: 20px; }}
            .header h1 {{ color: #1A1A1A; margin: 0; font-size: 24px; }}
            .header p {{ color: #666; margin: 5px 0; }}
            .customer-info {{ background: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            .customer-info h3 {{ color: #D4AF37; margin-top: 0; }}
            .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            .info-item {{ padding: 5px 0; }}
            .info-label {{ color: #666; font-size: 12px; }}
            .info-value {{ font-weight: bold; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #1A1A1A; color: #D4AF37; padding: 12px; text-align: left; }}
            .summary {{ margin-top: 20px; background: #1A1A1A; color: white; padding: 15px; border-radius: 8px; }}
            .summary-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #333; }}
            .summary-row:last-child {{ border-bottom: none; }}
            .summary-label {{ color: #D4AF37; }}
            .summary-value {{ font-weight: bold; }}
            .balance {{ color: #ff6b6b; font-size: 1.2em; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>RRL BUILDERS AND DEVELOPERS</h1>
            <p>Beyond homes. A lifestyle</p>
            <h2 style="margin-top: 15px; color: #D4AF37;">PAYMENT SCHEDULE</h2>
        </div>
        
        <div class="customer-info">
            <h3>Customer Details</h3>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">Customer Name</div>
                    <div class="info-value">{customer.get('name', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Customer ID</div>
                    <div class="info-value">{customer.get('customer_id', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Project</div>
                    <div class="info-value">{customer.get('project', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Unit Number</div>
                    <div class="info-value">{customer.get('tower', '')}-{customer.get('unit_number', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Phone</div>
                    <div class="info-value">{customer.get('phone', '-')}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Email</div>
                    <div class="info-value">{customer.get('email', '-')}</div>
                </div>
            </div>
        </div>
        
        <h3>Payment Transactions</h3>
        <table>
            <thead>
                <tr>
                    <th style="width: 5%;">#</th>
                    <th style="width: 15%;">Date</th>
                    <th style="width: 20%;">Type</th>
                    <th style="width: 20%;">Bank</th>
                    <th style="width: 20%;">Reference</th>
                    <th style="width: 20%; text-align: right;">Amount</th>
                </tr>
            </thead>
            <tbody>
                {transactions_rows if transactions_rows else '<tr><td colspan="6" style="text-align: center; padding: 20px; color: #666;">No transactions recorded</td></tr>'}
            </tbody>
        </table>
        
        <div class="summary">
            <div class="summary-row">
                <span class="summary-label">Total Unit Value</span>
                <span class="summary-value">{fmt(total_price)}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Total Received</span>
                <span class="summary-value" style="color: #4CAF50;">{fmt(total_received)}</span>
            </div>
            <div class="summary-row">
                <span class="summary-label">Balance Pending</span>
                <span class="summary-value balance">{fmt(balance)}</span>
            </div>
        </div>
        
        <p style="text-align: center; margin-top: 30px; color: #666; font-size: 12px;">
            Generated on {datetime.now().strftime("%d/%m/%Y at %H:%M")} | RRL Builders CRM
        </p>
    </body>
    </html>
    '''
    
    return html
def generate_payment_schedule_html(customer: dict, schedule_items: list) -> str:
    """Generate HTML for Payment Schedule PDF with black and gold theme"""
    
    def format_inr(amount):
        """Format amount in Indian Rupee style without L/Cr abbreviations"""
        amount = float(amount) if amount else 0
        int_part = int(amount)
        decimal_part = f"{amount:.2f}".split('.')[1]
        
        # Format with Indian comma system
        s = str(int_part)
        if len(s) > 3:
            result = s[-3:]
            s = s[:-3]
            while s:
                result = s[-2:] + ',' + result
                s = s[:-2]
        else:
            result = s
        
        return f"₹{result}.{decimal_part}"
    
    booking_date = customer.get('booking_date', datetime.now().strftime("%d/%m/%Y"))
    if booking_date and '-' in booking_date:
        try:
            dt = datetime.strptime(booking_date, "%Y-%m-%d")
            booking_date = dt.strftime("%d/%m/%Y")
        except:
            pass
    
    # Generate schedule rows
    schedule_rows = ""
    cumulative_amount = 0
    cumulative_pct = 0
    for i, item in enumerate(schedule_items, 1):
        cumulative_amount += item.get('amount', 0)
        cumulative_pct += item.get('percentage', 0)
        status_color = "#28a745" if item.get('payment_status') == 'paid' else "#dc3545" if item.get('payment_status') == 'overdue' else "#D4AF37"
        schedule_rows += f'''
        <tr>
            <td style="text-align: center;">{i}</td>
            <td>{item.get('installment_name', '')}</td>
            <td style="text-align: center;">{item.get('percentage', 0)}%</td>
            <td style="text-align: center;">{cumulative_pct}%</td>
            <td style="text-align: right;">{format_inr(item.get('amount', 0))}</td>
            <td style="text-align: right; color: #D4AF37; font-weight: bold;">{format_inr(cumulative_amount)}</td>
            <td style="text-align: center;">{item.get('due_date', '-')}</td>
            <td style="text-align: center; color: {status_color}; font-weight: bold;">{item.get('payment_status', 'pending').upper()}</td>
        </tr>
        '''
    
    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{
                font-family: 'Roboto', sans-serif;
                background: #f5f5f5;
                padding: 30px;
                color: #1A1A1A;
            }}
            
            .container {{
                background: #fff;
                border: 2px solid #D4AF37;
                border-radius: 8px;
                padding: 30px;
                max-width: 900px;
                margin: 0 auto;
            }}
            
            .header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 3px solid #D4AF37;
                padding-bottom: 20px;
                margin-bottom: 25px;
            }}
            
            .logo-section {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .logo {{
                width: 60px;
                height: 60px;
                background: #1A1A1A;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #D4AF37;
                font-weight: bold;
                font-size: 24px;
            }}
            
            .company-name {{
                font-size: 22px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            
            .company-tagline {{
                font-size: 12px;
                color: #666;
            }}
            
            .document-title {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 14px;
            }}
            
            .customer-info {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
                margin-bottom: 25px;
                padding: 15px;
                background: #fafafa;
                border-radius: 8px;
                border-left: 4px solid #D4AF37;
            }}
            
            .info-item {{
                display: flex;
                justify-content: space-between;
            }}
            
            .info-label {{
                color: #666;
                font-size: 12px;
            }}
            
            .info-value {{
                font-weight: 500;
                color: #1A1A1A;
            }}
            
            .schedule-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            
            .schedule-table th {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 12px 10px;
                font-weight: 500;
                font-size: 12px;
                text-transform: uppercase;
            }}
            
            .schedule-table td {{
                padding: 10px;
                border-bottom: 1px solid #e0e0e0;
                font-size: 11px;
            }}
            
            .schedule-table tr:nth-child(even) {{
                background: #fafafa;
            }}
            
            .totals-section {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-top: 25px;
            }}
            
            .total-box {{
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }}
            
            .total-box.received {{
                background: #e8f5e9;
                border: 1px solid #28a745;
            }}
            
            .total-box.pending {{
                background: #fff3e0;
                border: 1px solid #D4AF37;
            }}
            
            .total-box.total {{
                background: #1A1A1A;
                color: #D4AF37;
            }}
            
            .total-label {{
                font-size: 11px;
                text-transform: uppercase;
            }}
            
            .total-value {{
                font-size: 18px;
                font-weight: 700;
                margin-top: 5px;
            }}
            
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e0e0e0;
                text-align: center;
                font-size: 10px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo-section">
                    <div class="logo">RRL</div>
                    <div>
                        <div class="company-name">RRL Builders and Developers</div>
                        <div class="company-tagline">Beyond homes. A lifestyle</div>
                    </div>
                </div>
                <div class="document-title">PAYMENT SCHEDULE</div>
            </div>
            
            <div class="customer-info">
                <div class="info-item">
                    <span class="info-label">Customer Name</span>
                    <span class="info-value">{customer.get('name', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Customer ID</span>
                    <span class="info-value">{customer.get('customer_id', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Project</span>
                    <span class="info-value">{customer.get('project', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Unit Number</span>
                    <span class="info-value">{customer.get('unit_number', '-')}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Total Value</span>
                    <span class="info-value">{format_inr(customer.get('total_price', 0))}</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Booking Date</span>
                    <span class="info-value">{booking_date}</span>
                </div>
            </div>
            
            <table class="schedule-table">
                <thead>
                    <tr>
                        <th style="width: 5%;">#</th>
                        <th style="width: 28%;">Particulars</th>
                        <th style="width: 7%;">%</th>
                        <th style="width: 10%;">Cumulative %</th>
                        <th style="width: 14%;">Amount</th>
                        <th style="width: 14%;">Cumulative Amt</th>
                        <th style="width: 12%;">Due Date</th>
                        <th style="width: 10%;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    {schedule_rows}
                </tbody>
            </table>
            
            <div class="totals-section">
                <div class="total-box received">
                    <div class="total-label">Total Received</div>
                    <div class="total-value" style="color: #28a745;">{format_inr(customer.get('total_received', 0))}</div>
                </div>
                <div class="total-box pending">
                    <div class="total-label">Balance Pending</div>
                    <div class="total-value" style="color: #D4AF37;">{format_inr(customer.get('balance_amount', 0))}</div>
                </div>
                <div class="total-box total">
                    <div class="total-label">Total Property Value</div>
                    <div class="total-value">{format_inr(customer.get('total_price', 0))}</div>
                </div>
            </div>
            
            <div class="footer">
                <p>RRL Builders and Developers Pvt Ltd | www.rrlbuildersanddevelopers.com</p>
                <p>This is a computer-generated document. Generated on {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html



def generate_demand_letter_html(customer: dict, transactions: list = None, stage_info: dict = None) -> str:
    """Generate Demand Letter / Installment Call Letter HTML with customer and payment data."""
    from datetime import datetime

    transactions = transactions or []
    stage_info = stage_info or {}

    # --- Customer Details ---
    customer_name = customer.get('name', '').upper()
    co_applicant = customer.get('co_applicant_name', '')
    if co_applicant:
        recipient_name = f"{customer_name} AND {co_applicant.upper()}"
    else:
        recipient_name = customer_name

    address = customer.get('address', '') or ''
    phone = customer.get('phone', '')
    email = customer.get('email', '')

    # --- Property Details ---
    project = customer.get('project', 'RRL Palm Altezze')
    tower = customer.get('tower', '')
    unit_number = customer.get('unit_number', '')
    floor_num = customer.get('floor', 0)

    def get_ordinal(n):
        n = int(n)
        if n == 0:
            return "Ground"
        suffix = 'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return f"{n}{suffix}"

    floor_display = get_ordinal(floor_num) + " Floor" if floor_num else "Ground Floor"
    flat_ref = f"Flat no. {unit_number}, Tower- {tower}, {floor_display}"

    # --- Financial Calculations ---
    total_basic_cost = float(customer.get('total_price', 0) or 0)
    booking_amount = float(customer.get('booking_amount', 0) or 0)

    # Current stage info
    stage_name = stage_info.get('name', 'As per schedule')
    stage_percentage = float(stage_info.get('percentage', 0) or 0)
    cumulative_percentage = float(stage_info.get('cumulative', 0) or 0)

    # Demand raised till date = cumulative % of total basic cost
    demand_raised = round((total_basic_cost * cumulative_percentage) / 100, 2) if cumulative_percentage else 0

    # Current due = stage % of total basic cost (this stage's individual share)
    current_due = round((total_basic_cost * stage_percentage) / 100, 2) if stage_percentage else 0

    # Amount paid till date from transactions
    txn_total = sum(float(t.get('amount', 0) or 0) for t in transactions)
    amount_paid = txn_total if txn_total >= booking_amount else booking_amount + txn_total

    # Outstanding
    total_outstanding = max(0, round(demand_raised - amount_paid, 2))

    # TDS (default 0)
    tds_payable = 0
    tds_paid = 0
    tds_to_be_paid = 0

    # Net amount payable
    net_amount_payable = max(0, round(total_outstanding - tds_payable, 2))

    # Amount in words
    net_amount_words = number_to_indian_words(int(net_amount_payable)).replace(" Rupees", "")
    amount_in_words = f"Rupees {net_amount_words} Only"

    # Format currency helper
    def fmt(amount):
        return format_indian_currency(amount, decimals=False)

    # Date
    today = datetime.now()
    date_str = today.strftime("%d-%m-%Y")

    html = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
            @page {{
                size: A4;
                margin: 15mm 15mm 20mm 15mm;
            }}
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                font-family: 'Roboto', Arial, sans-serif;
                font-size: 12px;
                line-height: 1.6;
                color: #1a1a1a;
                background: #fff;
            }}
            .page {{
                max-width: 210mm;
                margin: 0 auto;
                padding: 15mm;
            }}
            .header-bar {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 14px 24px;
                display: flex;
                align-items: center;
                border-radius: 4px 4px 0 0;
                margin-bottom: 0;
            }}
            .header-logo {{
                background: #D4AF37;
                color: #1A1A1A;
                font-weight: 700;
                font-size: 20px;
                padding: 8px 14px;
                border-radius: 4px;
                margin-right: 16px;
            }}
            .header-text {{
                flex: 1;
            }}
            .header-text h1 {{
                font-size: 16px;
                font-weight: 700;
                color: #D4AF37;
                margin: 0;
            }}
            .header-text p {{
                font-size: 10px;
                color: #999;
                margin: 2px 0 0;
            }}
            .title-bar {{
                background: #D4AF37;
                color: #1A1A1A;
                text-align: center;
                padding: 8px;
                font-size: 14px;
                font-weight: 700;
                letter-spacing: 2px;
            }}
            .content {{
                border: 1px solid #ddd;
                border-top: none;
                padding: 24px;
                border-radius: 0 0 4px 4px;
            }}
            .date-line {{
                text-align: right;
                font-weight: 500;
                margin-bottom: 16px;
                font-size: 12px;
            }}
            .recipient {{
                margin-bottom: 14px;
                line-height: 1.7;
            }}
            .recipient strong {{
                font-size: 13px;
            }}
            .ref-box {{
                background: #f8f8f4;
                border-left: 3px solid #D4AF37;
                padding: 10px 14px;
                margin-bottom: 14px;
                font-size: 11.5px;
                line-height: 1.6;
            }}
            .ref-box strong {{
                color: #1A1A1A;
            }}
            .subject {{
                margin-bottom: 12px;
                font-size: 12px;
            }}
            .subject strong {{
                color: #1A1A1A;
            }}
            .body-text {{
                margin-bottom: 12px;
                font-size: 12px;
                line-height: 1.7;
            }}
            .stage-label {{
                background: #1A1A1A;
                color: #D4AF37;
                padding: 8px 14px;
                font-weight: 600;
                font-size: 11.5px;
                border-radius: 3px;
                margin-bottom: 10px;
            }}
            .payment-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 12px;
                font-size: 11px;
            }}
            .payment-table th {{
                background: #f5f5f0;
                border: 1px solid #ccc;
                padding: 8px 10px;
                text-align: left;
                font-weight: 600;
                font-size: 10.5px;
                color: #333;
            }}
            .payment-table td {{
                border: 1px solid #ccc;
                padding: 8px 10px;
                text-align: right;
                font-weight: 500;
                font-size: 11px;
            }}
            .payment-table tr.highlight td {{
                background: #fffbe6;
                font-weight: 700;
                color: #1A1A1A;
            }}
            .amount-words {{
                font-style: italic;
                font-weight: 600;
                color: #333;
                margin-bottom: 14px;
                font-size: 12px;
                padding: 6px 0;
                border-bottom: 1px dashed #ccc;
            }}
            .bank-details {{
                background: #fafaf6;
                border: 1px solid #e0dcd0;
                border-radius: 4px;
                padding: 14px 18px;
                margin: 14px 0;
            }}
            .bank-details h4 {{
                font-size: 12px;
                color: #1A1A1A;
                margin-bottom: 8px;
                font-weight: 600;
            }}
            .bank-details table {{
                font-size: 11.5px;
            }}
            .bank-details td {{
                padding: 3px 8px 3px 0;
            }}
            .bank-details td:first-child {{
                font-weight: 600;
                color: #555;
                white-space: nowrap;
            }}
            .closing {{
                margin-top: 20px;
                font-size: 12px;
                line-height: 1.8;
            }}
            .signature {{
                margin-top: 40px;
            }}
            .signature .for {{
                font-size: 11px;
                color: #666;
            }}
            .signature .company {{
                font-size: 13px;
                font-weight: 700;
                color: #1A1A1A;
            }}
            .footer {{
                margin-top: 24px;
                border-top: 2px solid #D4AF37;
                padding-top: 10px;
                text-align: center;
                font-size: 9.5px;
                color: #888;
            }}
            .footer a {{
                color: #D4AF37;
                text-decoration: none;
            }}
        </style>
    </head>
    <body>
        <div class="page">
            <!-- Header -->
            <div class="header-bar">
                <div class="header-logo">RRL</div>
                <div class="header-text">
                    <h1>RRL Builders and Developers</h1>
                    <p>Beyond homes. A lifestyle</p>
                </div>
            </div>

            <!-- Title -->
            <div class="title-bar">DEMAND LETTER</div>

            <!-- Content -->
            <div class="content">
                <div class="date-line">Date: {date_str}</div>

                <div class="recipient">
                    <strong>{recipient_name}</strong><br>
                    {address.replace(chr(10), "<br>") if address else "Address on file"}<br>
                    Ph. {phone}
                </div>

                <div class="ref-box">
                    <strong>Ref:</strong> {flat_ref} at &ldquo;{project}&rdquo; situated at SY NO: 73/6, Janthagondanahalli Village, Sarjapura Hobli, Anekal Taluk, Bengaluru Urban District, PIN - 560087
                </div>

                <div class="subject">
                    <strong>Subject:</strong> Installment Call Letter
                </div>

                <p class="body-text">Dear Sir/Madam,</p>
                <p class="body-text">
                    Thank you for partnering with us. We are pleased to inform you that the following installments are due as per the payment schedule.
                </p>

                <!-- Payment Stage -->
                <div class="stage-label">
                    Payment Stage: {stage_name} &mdash; {int(cumulative_percentage)}% Total Basic Cost
                </div>

                <!-- Payment Table -->
                <table class="payment-table">
                    <tr>
                        <th>Total Basic Cost</th>
                        <td>{fmt(total_basic_cost)}</td>
                    </tr>
                    <tr>
                        <th>Demand Raised Till Date (A)</th>
                        <td>{fmt(demand_raised)}</td>
                    </tr>
                    <tr>
                        <th>Current Due (B)</th>
                        <td>{fmt(current_due)}</td>
                    </tr>
                    <tr>
                        <th>Installment Amount Paid Till Date (C)</th>
                        <td>{fmt(amount_paid)}</td>
                    </tr>
                    <tr>
                        <th>Interest (D)</th>
                        <td>0</td>
                    </tr>
                    <tr class="highlight">
                        <th>Total Outstanding as on date (A)-(C)</th>
                        <td>{fmt(total_outstanding)}</td>
                    </tr>
                    <tr>
                        <th>TDS Payable</th>
                        <td>{tds_payable}</td>
                    </tr>
                    <tr>
                        <th>TDS Paid</th>
                        <td>{tds_paid}</td>
                    </tr>
                    <tr>
                        <th>TDS To be Paid</th>
                        <td>{tds_to_be_paid}</td>
                    </tr>
                    <tr class="highlight">
                        <th>Net Amount Payable<br><small>(Total Outstanding - TDS Payable)</small></th>
                        <td style="font-size: 13px;">{fmt(net_amount_payable)}</td>
                    </tr>
                </table>

                <div class="amount-words">{amount_in_words}</div>

                <p class="body-text">We hereby request you to release this payment towards your flat.</p>
                <p class="body-text">Please remit payments via NEFT/RTGS to the bank details below:</p>

                <!-- Bank Details -->
                <div class="bank-details">
                    <h4>Bank Details for Payment</h4>
                    <table>
                        <tr><td>Account Name</td><td>: RRL BUILDERS AND DEVELOPERS PRIVATE LIMITED</td></tr>
                        <tr><td>Account Number</td><td>: 57500001802063</td></tr>
                        <tr><td>Bank Name</td><td>: HDFC BANK</td></tr>
                        <tr><td>IFSC</td><td>: HDFC0009590</td></tr>
                        <tr><td>Branch Name</td><td>: SOMPURA</td></tr>
                    </table>
                </div>

                <div class="closing">
                    <p>Thanking you,</p>
                    <div class="signature">
                        <div class="for">For</div>
                        <div class="company">RRL Builders and Developers Private Limited</div>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="footer">
                <p>4TH Floor, RRL Tower, Sompura Gate, Sarjapura, Bengaluru - 562125</p>
                <p><a href="https://www.rrlbuildersanddevelopers.com">www.rrlbuildersanddevelopers.com</a> | crm@rrlbuildersanddevelopers.com</p>
            </div>
        </div>
    </body>
    </html>
    '''
    return html
