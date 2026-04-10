"""Sales Agreement static template."""

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
            width: 120px;
        }
        
        .logo img {
            width: 120px;
            height: auto;
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
            <div class="logo">{logo_img}</div>
            <div>
                <div class="company-name">{company_name}</div>
                <div class="company-tagline">Beyond Homes. A Lifestyle</div>
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
            {applicant_details_block}
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
        
        <p class="clause"><span class="clause-number">(ii)</span> Accordingly, the PURCHASER/S as a token of acceptance, has paid a sum of <strong>Rs. <span class="highlight">{total_received_formatted}</span>/- (<span class="highlight">{total_received_words}</span> Only)</strong> vide payment details recorded separately. The receipt of which the VENDORS hereby accepts and acknowledges in the presence of the witnesses attesting hereunder.</p>
        
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
                        <p>Represented by its Managing Director Mr. Ram R</p>
                        <p>Authorized Signatory</p>
                    </div>
                </div>
                <div class="signature-box">
                    <p><strong>PURCHASER/S</strong></p>
                    <div class="signature-line">
                        <p>{customer_names}</p>
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
        <p><strong>{company_name}</strong></p>
        <p>4th Floor, RRL TOWERS, Sompura Gate, Sarjapura Road, Bengaluru – 562125</p>
        <p>www.rrlbuildersanddevelopers.com | RERA: PRM/KA/RERA/1251/308/PR/141025/008167</p>
        <p style="margin-top: 10px;">Document Generated: {date} | Ref: {customer_id}</p>
    </div>
</body>
</html>
"""

