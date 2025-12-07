from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.utils import ImageReader
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.mail import EmailMessage
import os
from datetime import datetime
import requests
import base64

def generate_receipt_pdf(booking):
    """
    Generate a PDF receipt for the given booking and save it to the booking model.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='RightAlign', parent=styles['Normal'], alignment=2))
    styles.add(ParagraphStyle(name='CenterAlign', parent=styles['Normal'], alignment=1))
    styles.add(ParagraphStyle(name='InvoiceTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=20, alignment=2, textColor=colors.HexColor('#333333')))
    styles.add(ParagraphStyle(name='SectionHeader', parent=styles['Heading3'], fontSize=12, spaceAfter=6, textColor=colors.HexColor('#555555')))
    
    normal_style = styles['Normal']
    
    elements = []
    
    # --- Header ---
    logo_path = os.path.join(settings.STATIC_ROOT, 'yourapp/images/SafeLetStays-New.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'static/yourapp/images/SafeLetStays-New.png')

    logo_img = None
    if os.path.exists(logo_path):
        try:
            img_reader = ImageReader(logo_path)
            img_width, img_height = img_reader.getSize()
            aspect = img_height / float(img_width)
            
            # Target width 2 inches
            display_width = 2 * inch
            display_height = display_width * aspect
            
            logo_img = Image(logo_path, width=display_width, height=display_height)
        except Exception:
            pass

    # Company Info
    company_info = [
        Paragraph("<b>Safe Let Stays</b>", styles['Heading2']),
        Paragraph("123 Sheffield Street<br/>Sheffield, S1 1AA<br/>United Kingdom", styles['Normal']),
        Paragraph("<br/>hello@safeletstays.co.uk<br/>+44 114 123 4567", styles['Normal'])
    ]

    # Construct Header Table
    if logo_img:
        header_data = [[company_info, logo_img]]
        col_widths = [4*inch, 2.5*inch]
    else:
        header_data = [[company_info, ""]]
        col_widths = [4*inch, 2.5*inch]

    header_table = Table(header_data, colWidths=col_widths)
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'), # Align logo to right
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 30))
    
    # --- Invoice Title & Meta ---
    invoice_date = datetime.now().strftime('%d %b %Y')
    
    bill_to = [
        Paragraph("<b>BILL TO:</b>", styles['SectionHeader']),
        Paragraph(f"{booking.guest_name}", styles['Normal']),
        Paragraph(f"{booking.guest_email}", styles['Normal']),
    ]
    if booking.guest_phone:
        bill_to.append(Paragraph(f"{booking.guest_phone}", styles['Normal']))
        
    invoice_details = [
        Paragraph("<b>RECEIPT DETAILS</b>", styles['SectionHeader']),
        Paragraph(f"<b>Receipt #:</b> {booking.id}", styles['Normal']),
        Paragraph(f"<b>Date:</b> {invoice_date}", styles['Normal']),
        Paragraph(f"<b>Booking Ref:</b> BOOK-{booking.id}", styles['Normal']),
        Paragraph(f"<b>Status:</b> {booking.get_status_display().upper()}", styles['Normal']),
    ]
    
    meta_table = Table([[bill_to, invoice_details]], colWidths=[3.5*inch, 3*inch])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 30))
    
    # --- Property & Stay Details ---
    elements.append(Paragraph("<b>STAY DETAILS</b>", styles['SectionHeader']))
    elements.append(Spacer(1, 5))
    
    stay_data = [
        [Paragraph("<b>Property</b>", styles['Normal']), Paragraph(booking.property.title, styles['Normal'])],
        [Paragraph("<b>Check-in</b>", styles['Normal']), Paragraph(booking.check_in.strftime('%A, %d %b %Y'), styles['Normal'])],
        [Paragraph("<b>Check-out</b>", styles['Normal']), Paragraph(booking.check_out.strftime('%A, %d %b %Y'), styles['Normal'])],
        [Paragraph("<b>Duration</b>", styles['Normal']), Paragraph(f"{booking.nights} Nights", styles['Normal'])],
        [Paragraph("<b>Guests</b>", styles['Normal']), Paragraph(str(booking.guests), styles['Normal'])],
    ]
    
    t_stay = Table(stay_data, colWidths=[1.5*inch, 5*inch])
    t_stay.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TEXTCOLOR', (0,0), (0,-1), colors.HexColor('#555555')),
    ]))
    elements.append(t_stay)
    elements.append(Spacer(1, 30))
    
    # --- Line Items ---
    items_data = [
        ["Description", "Quantity", "Rate", "Amount"]
    ]
    
    # Accommodation Item
    rate_val = booking.nightly_rate if booking.nightly_rate else 0
    rate_str = f"£{rate_val}" if booking.nightly_rate else "N/A"
    acc_total = rate_val * booking.nights
    
    items_data.append([
        f"Accommodation - {booking.property.title}",
        f"{booking.nights} nights",
        rate_str,
        f"£{acc_total:.2f}"
    ])
    
    # Cleaning Fee
    if booking.cleaning_fee and booking.cleaning_fee > 0:
        items_data.append([
            "Cleaning Fee",
            "1",
            f"£{booking.cleaning_fee}",
            f"£{booking.cleaning_fee:.2f}"
        ])
        
    # Total
    total_val = booking.total_price if booking.total_price else 0
    items_data.append(["", "", "Total", f"£{total_val}"])
    
    t_items = Table(items_data, colWidths=[3.5*inch, 1*inch, 1*inch, 1*inch])
    
    # Styling the table
    table_style = [
        # Header row
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#333333')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,0), 'LEFT'),
        ('ALIGN', (1,0), (-1,-1), 'RIGHT'), # Numbers right aligned
        ('PADDING', (0,0), (-1,-1), 10),
        
        # Rows
        ('GRID', (0,0), (-1,-2), 0.5, colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        
        # Total Row
        ('LINEABOVE', (0,-1), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f0f0f0')),
    ]
    t_items.setStyle(TableStyle(table_style))
    
    elements.append(t_items)
    elements.append(Spacer(1, 40))
    
    # --- Footer ---
    elements.append(Paragraph("Thank you for choosing Safe Let Stays!", styles['CenterAlign']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("If you have any questions about this receipt, please contact us at hello@safeletstays.co.uk", styles['CenterAlign']))
    
    doc.build(elements)
    
    # Save to model
    pdf_content = buffer.getvalue()
    buffer.close()
    
    filename = f"receipt_{booking.id}.pdf"
    booking.receipt_pdf.save(filename, ContentFile(pdf_content), save=True)
    
    return booking.receipt_pdf

def send_receipt_email(booking):
    """
    Send the receipt email to the guest and a copy to admin using MailerSend.
    """
    if not booking.receipt_pdf:
        generate_receipt_pdf(booking)
        
    subject = f"Booking Confirmation - Reference #{booking.id}"
    body_text = f"""
Dear {booking.guest_name},

Thank you for booking with Safe Let Stays!

Your booking for {booking.property.title} has been confirmed.
Please find your receipt and invoice attached to this email.

Booking Reference: BOOK-{booking.id}
Check-in: {booking.check_in.strftime('%d %b %Y')}
Check-out: {booking.check_out.strftime('%d %b %Y')}

We look forward to hosting you.

Best regards,
The Safe Let Stays Team
    """
    
    # Convert PDF to base64
    try:
        booking.receipt_pdf.open('rb')
        pdf_content = booking.receipt_pdf.read()
        pdf_base64 = base64.b64encode(pdf_content).decode('utf-8')
        booking.receipt_pdf.close()
    except Exception as e:
        print(f"Error reading PDF for email: {e}")
        return

    # MailerSend API configuration
    api_key = getattr(settings, 'MAILERSEND_API_KEY', None)
    
    # Fallback to environment variable directly if settings fails (common in some deployment setups)
    if not api_key:
        api_key = os.environ.get('MAILERSEND_API_KEY')

    if not api_key:
        # Fallback to Django's default email backend (SMTP, Console, etc.)
        print("MAILERSEND_API_KEY not found. Falling back to Django EmailBackend.")
        try:
            email = EmailMessage(
                subject=subject,
                body=body_text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[booking.guest_email],
                bcc=[settings.SERVER_EMAIL] if hasattr(settings, 'SERVER_EMAIL') and settings.SERVER_EMAIL else None,
            )
            email.attach(f"receipt_{booking.id}.pdf", pdf_content, 'application/pdf')
            email.send()
            print(f"Email sent successfully via Django Backend to {booking.guest_email}")
        except Exception as e:
            print(f"Error sending email via Django Backend: {e}")
        return

    url = "https://api.mailersend.com/v1/email"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }
    
    # Parse DEFAULT_FROM_EMAIL
    from_email = settings.DEFAULT_FROM_EMAIL
    from_name = "Safe Let Stays"
    if '<' in from_email and '>' in from_email:
        parts = from_email.split('<')
        from_name = parts[0].strip()
        from_email = parts[1].strip('>')
        
    payload = {
        "from": {
            "email": from_email,
            "name": from_name
        },
        "to": [
            {
                "email": booking.guest_email,
                "name": booking.guest_name
            }
        ],
        "subject": subject,
        "text": body_text,
        "html": body_text.replace('\n', '<br>'),
        "attachments": [
            {
                "filename": f"receipt_{booking.id}.pdf",
                "content": pdf_base64,
                "disposition": "attachment"
            }
        ]
    }
    
    # Add BCC to admin
    if hasattr(settings, 'SERVER_EMAIL') and settings.SERVER_EMAIL:
         payload["bcc"] = [
             {"email": settings.SERVER_EMAIL, "name": "Admin"}
         ]

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 202:
            print(f"MailerSend Error: {response.status_code} - {response.text}")
            if response.status_code == 422:
                 print("Tip: Check if you have reached your plan limits or if the data is invalid.")
            print(f"Please ensure the sender email '{from_email}' is verified in MailerSend.")
        else:
            print(f"Email sent successfully to {booking.guest_email}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending email via MailerSend: {e}")

