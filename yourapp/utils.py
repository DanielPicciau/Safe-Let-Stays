from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from django.core.mail import EmailMessage
import os
from datetime import datetime

def generate_receipt_pdf(booking):
    """
    Generate a PDF receipt for the given booking and save it to the booking model.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1 # Center
    
    normal_style = styles['Normal']
    
    elements = []
    
    # Logo
    logo_path = os.path.join(settings.STATIC_ROOT, 'yourapp/images/logo.webp')
    # Fallback to static source if static root not populated or dev mode
    if not os.path.exists(logo_path):
        logo_path = os.path.join(settings.BASE_DIR, 'static/yourapp/images/logo.webp')
        
    if os.path.exists(logo_path):
        try:
            # ReportLab might have issues with webp, let's try. If not, we skip.
            # Actually ReportLab 4.x supports more formats via Pillow.
            im = Image(logo_path, width=2*inch, height=0.75*inch)
            im.hAlign = 'LEFT'
            elements.append(im)
        except Exception:
            pass
            
    elements.append(Spacer(1, 12))
    
    # Header Info
    elements.append(Paragraph("Safe Let Stays", styles['Heading2']))
    elements.append(Paragraph("123 Sheffield Street, Sheffield, S1 1AA", normal_style))
    elements.append(Paragraph("hello@safeletstays.co.uk | +44 114 123 4567", normal_style))
    
    elements.append(Spacer(1, 24))
    
    # Title
    elements.append(Paragraph(f"INVOICE / RECEIPT #{booking.id}", title_style))
    elements.append(Spacer(1, 12))
    
    # Booking Details Table
    data = [
        ["Reference:", f"BOOK-{booking.id}"],
        ["Date Issued:", datetime.now().strftime('%d %b %Y')],
        ["Guest Name:", booking.guest_name],
        ["Email:", booking.guest_email],
        ["Property:", booking.property.title],
        ["Check-in:", booking.check_in.strftime('%d %b %Y')],
        ["Check-out:", booking.check_out.strftime('%d %b %Y')],
        ["Nights:", str(booking.nights)],
        ["Guests:", str(booking.guests)],
        ["Status:", booking.get_status_display().upper()],
    ]
    
    t = Table(data, colWidths=[2*inch, 4*inch])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t)
    
    elements.append(Spacer(1, 24))
    
    # Payment Summary
    elements.append(Paragraph("Payment Summary", styles['Heading3']))
    
    payment_data = [
        [f"Accommodation ({booking.nights} nights)", f"£{booking.total_price}"],
        ["Total Paid", f"£{booking.total_price}"]
    ]
    
    t_payment = Table(payment_data, colWidths=[4*inch, 2*inch])
    t_payment.setStyle(TableStyle([
        ('LINEABOVE', (0,1), (-1,1), 1, colors.black),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,1), (-1,1), 8),
    ]))
    elements.append(t_payment)
    
    elements.append(Spacer(1, 48))
    
    # Footer
    elements.append(Paragraph("Thank you for choosing Safe Let Stays!", normal_style))
    elements.append(Paragraph("This document serves as a formal invoice and receipt of payment.", styles['Italic']))
    
    # Build
    doc.build(elements)
    
    # Save to model
    pdf_content = buffer.getvalue()
    buffer.close()
    
    filename = f"receipt_{booking.id}.pdf"
    booking.receipt_pdf.save(filename, ContentFile(pdf_content), save=True)
    
    return booking.receipt_pdf

def send_receipt_email(booking):
    """
    Send the receipt email to the guest and a copy to admin.
    """
    if not booking.receipt_pdf:
        generate_receipt_pdf(booking)
        
    subject = f"Booking Confirmation - Reference #{booking.id}"
    body = f"""
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
    
    email = EmailMessage(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        [booking.guest_email],
        bcc=[settings.SERVER_EMAIL] # Send copy to admin for filing
    )
    
    # Attach PDF
    if booking.receipt_pdf:
        email.attach(booking.receipt_pdf.name, booking.receipt_pdf.read(), 'application/pdf')
        
    email.send()

