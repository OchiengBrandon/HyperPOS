# pos_app/utils.py
import io
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_receipt_pdf(business, sale):
    """Generate a PDF receipt for a sale"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Add business information
    if business.logo:
        # Add logo if exists
        logo_path = business.logo.path
        elements.append(Image(logo_path, width=2*inch, height=1*inch))
    
    # Business name
    elements.append(Paragraph(f"<b>{business.name}</b>", styles['Title']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Business address and contact
    if business.address:
        elements.append(Paragraph(business.address, styles['Normal']))
    if business.phone:
        elements.append(Paragraph(f"Phone: {business.phone}", styles['Normal']))
    if business.email:
        elements.append(Paragraph(f"Email: {business.email}", styles['Normal']))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Receipt header
    if business.settings.receipt_header:
        elements.append(Paragraph(business.settings.receipt_header, styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
    
    # Sale information
    elements.append(Paragraph(f"<b>RECEIPT</b>", styles['Heading2']))
    elements.append(Paragraph(f"Invoice: {sale.invoice_number}", styles['Normal']))
    elements.append(Paragraph(f"Date: {sale.created_at.strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    
    # Customer information
    if sale.customer:
        elements.append(Paragraph(f"Customer: {sale.customer.full_name}", styles['Normal']))
        if sale.customer.phone:
            elements.append(Paragraph(f"Phone: {sale.customer.phone}", styles['Normal']))
    else:
        elements.append(Paragraph("Customer: Walk-in Customer", styles['Normal']))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Items table
    items_data = [['Item', 'Qty', 'Price', 'Total']]
    for item in sale.items.all():
        items_data.append([
            item.product.name,
            str(item.quantity),
            f"{business.currency_symbol}{item.unit_price}",
            f"{business.currency_symbol}{item.subtotal}"
        ])
    
    # Add summary rows
    items_data.append(['', '', 'Subtotal', f"{business.currency_symbol}{sale.subtotal}"])
    if sale.tax_amount > 0:
        items_data.append(['', '', 'Tax', f"{business.currency_symbol}{sale.tax_amount}"])
    if sale.discount_amount > 0:
        items_data.append(['', '', 'Discount', f"{business.currency_symbol}{sale.discount_amount}"])
    items_data.append(['', '', '<b>TOTAL</b>', f"<b>{business.currency_symbol}{sale.total_amount}</b>"])
    
    # Create table
    table = Table(items_data, colWidths=[3*inch, 0.5*inch, 1*inch, 1*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -len(items_data)), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Payment information
    elements.append(Paragraph(f"Payment Method: {sale.get_payment_method_display()}", styles['Normal']))
    if sale.payment_reference:
        elements.append(Paragraph(f"Reference: {sale.payment_reference}", styles['Normal']))
    
    # Loyalty points
    if business.settings.enable_customer_loyalty and sale.customer:
        if sale.loyalty_points_earned > 0:
            elements.append(Paragraph(f"Points Earned: {sale.loyalty_points_earned}", styles['Normal']))
        if sale.loyalty_points_used > 0:
            elements.append(Paragraph(f"Points Used: {sale.loyalty_points_used}", styles['Normal']))
        elements.append(Paragraph(f"Current Points Balance: {sale.customer.loyalty_points}", styles['Normal']))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Receipt footer
    if business.settings.receipt_footer:
        elements.append(Paragraph(business.settings.receipt_footer, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf

def get_date_range(period):
    """Get date range based on period"""
    today = timezone.now().date()
    
    if period == 'today':
        start_date = today
        end_date = today
    elif period == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = start_date
    elif period == 'this_week':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif period == 'last_week':
        start_date = today - timedelta(days=today.weekday() + 7)
        end_date = start_date + timedelta(days=6)
    elif period == 'this_month':
        start_date = today.replace(day=1)
        end_date = today
    elif period == 'last_month':
        last_month = today.month - 1 if today.month > 1 else 12
        last_month_year = today.year if today.month > 1 else today.year - 1
        last_month_days = 31  # Approximate
        start_date = today.replace(year=last_month_year, month=last_month, day=1)
        end_date = today.replace(year=last_month_year, month=last_month, day=last_month_days)
    elif period == 'this_year':
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif period == 'last_year':
        start_date = today.replace(year=today.year-1, month=1, day=1)
        end_date = today.replace(year=today.year-1, month=12, day=31)
    else:  # Default to last 30 days
        start_date = today - timedelta(days=30)
        end_date = today
    
    return start_date, end_date