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
from django.utils.html import escape
from django.contrib.staticfiles import finders
import os
from datetime import datetime
import base64
import logging

logger = logging.getLogger(__name__)

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
    # Use Django's static file finders for proper static file resolution (MED-06)
    logo_path = finders.find('yourapp/images/SafeLetStays-New.png')
    if not logo_path and settings.STATIC_ROOT:
        # Fallback to STATIC_ROOT in production
        logo_path = os.path.join(settings.STATIC_ROOT, 'yourapp/images/SafeLetStays-New.png')
        if not os.path.exists(logo_path):
            logo_path = None

    logo_img = None
    if logo_path and os.path.exists(logo_path):
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
        Paragraph("<br/>daniel@webflare.studio<br/>+44 114 123 4567", styles['Normal'])
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
    
    # Add company details if business booking
    if booking.is_company_booking and booking.company_name:
        bill_to.append(Spacer(1, 10))
        bill_to.append(Paragraph("<b>BUSINESS DETAILS:</b>", styles['SectionHeader']))
        bill_to.append(Paragraph(f"{booking.company_name}", styles['Normal']))
        if booking.company_address:
            # Replace newlines with <br/> for proper rendering
            address_formatted = booking.company_address.replace('\n', '<br/>')
            bill_to.append(Paragraph(f"{address_formatted}", styles['Normal']))
        if booking.company_vat:
            bill_to.append(Paragraph(f"VAT: {booking.company_vat}", styles['Normal']))
        
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
        [Paragraph("<b>Property</b>", styles['Normal']), Paragraph(booking.booked_property.title, styles['Normal'])],
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
        f"Accommodation - {booking.booked_property.title}",
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

from mailjet_rest import Client
import base64

def send_receipt_email(booking):
    """
    Send the receipt email to the guest using Mailjet API.
    """
    logger.debug(f"send_receipt_email called for Booking ID {booking.id}")

    if not booking.receipt_pdf:
        logger.debug(f"PDF missing for booking {booking.id}, generating...")
        try:
            generate_receipt_pdf(booking)
            logger.debug(f"PDF generated successfully for booking {booking.id}")
        except Exception as e:
            logger.error(f"PDF generation failed for booking {booking.id}: {e}")
            raise
    
    # Escape user-provided content for HTML safety
    safe_guest_name = escape(booking.guest_name)
    safe_property_title = escape(booking.booked_property.title)
    
    subject = f"Booking Confirmation - Reference #{booking.id}"
    body_text = f"Dear {booking.guest_name},\n\nThank you for booking with Safe Let Stays!\n\nYour booking for {booking.booked_property.title} has been confirmed.\nPlease find your receipt and invoice attached to this email.\n\nBooking Reference: BOOK-{booking.id}\nCheck-in: {booking.check_in.strftime('%d %b %Y')}\nCheck-out: {booking.check_out.strftime('%d %b %Y')}\n\nWe look forward to hosting you.\n\nBest regards,\nThe Safe Let Stays Team"
    
    body_html = f"""
    <h3>Booking Confirmation</h3>
    <p>Dear {safe_guest_name},</p>
    <p>Thank you for booking with Safe Let Stays!</p>
    <p>Your booking for <strong>{safe_property_title}</strong> has been confirmed.<br>
    Please find your receipt and invoice attached to this email.</p>
    <p><strong>Booking Reference:</strong> BOOK-{booking.id}<br>
    <strong>Check-in:</strong> {booking.check_in.strftime('%d %b %Y')}<br>
    <strong>Check-out:</strong> {booking.check_out.strftime('%d %b %Y')}</p>
    <p>We look forward to hosting you.</p>
    <p>Best regards,<br>
    The Safe Let Stays Team</p>
    """
    
    # Read PDF content
    try:
        logger.debug(f"Reading PDF file for booking {booking.id}")
        booking.receipt_pdf.open('rb')
        pdf_content = booking.receipt_pdf.read()
        booking.receipt_pdf.close()
        logger.debug(f"PDF read successfully ({len(pdf_content)} bytes)")
    except Exception as e:
        logger.error(f"Error reading PDF for booking {booking.id}: {e}")
        raise

    logger.debug(f"Preparing to send email to {booking.guest_email} via Mailjet API")
    
    api_key = settings.MAILJET_API_KEY
    api_secret = settings.MAILJET_API_SECRET
    
    if not api_key or not api_secret:
        logger.error("Mailjet API Key or Secret is missing in settings")
        raise ValueError("Mailjet API credentials missing")

    try:
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        encoded_pdf = base64.b64encode(pdf_content).decode('utf-8')
        
        data = {
          'Messages': [
            {
              "From": {
                "Email": settings.DEFAULT_FROM_EMAIL,
                "Name": "Safe Let Stays"
              },
              "To": [
                {
                  "Email": booking.guest_email,
                  "Name": booking.guest_name
                }
              ],
              "Subject": subject,
              "TextPart": body_text,
              "HTMLPart": body_html,
              "Attachments": [
                {
                  "ContentType": "application/pdf",
                  "Filename": f"receipt_{booking.id}.pdf",
                  "Base64Content": encoded_pdf
                }
              ]
            }
          ]
        }
        
        logger.debug(f"Sending request to Mailjet for booking {booking.id}")
        result = mailjet.send.create(data=data)
        logger.debug(f"Mailjet Response Status: {result.status_code}")
        
        if result.status_code != 200:
            logger.error(f"Mailjet API Error for booking {booking.id}: {result.json()}")
            raise Exception(f"Mailjet API Error: {result.json()}")
             
        logger.info(f"Email sent successfully to {booking.guest_email} for booking {booking.id}")
        
    except Exception as e:
        logger.error(f"Failed to send email for booking {booking.id}: {e}", exc_info=True)
        raise

