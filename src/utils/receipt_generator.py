"""
Receipt Generator for LKS POS System
"""

import os
from datetime import datetime
from typing import List, Dict
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

class ReceiptGenerator:
    """Generates receipts for completed sales"""
    
    def __init__(self, receipts_dir: str = "data/receipts"):
        self.receipts_dir = receipts_dir
        os.makedirs(receipts_dir, exist_ok=True)
    
    def generate_text_receipt(self, sale_id: int, sale_data: Dict, sale_items: List[Dict], 
                             payment_info: Dict, company_info: Dict) -> str:
        """Generate a text receipt file"""
        timestamp = datetime.now()
        filename = f"receipt_{sale_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.txt"
        file_path = os.path.join(self.receipts_dir, filename)
        
        # Generate receipt content
        receipt_content = self._format_text_receipt(
            sale_data, sale_items, payment_info, company_info, timestamp
        )
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(receipt_content)
        
        return file_path
    
    def generate_pdf_receipt(self, sale_id: int, sale_data: Dict, sale_items: List[Dict], 
                            payment_info: Dict, company_info: Dict) -> str:
        """Generate a PDF receipt file"""
        timestamp = datetime.now()
        filename = f"receipt_{sale_id}_{timestamp.strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(self.receipts_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Company header
        company_name = company_info.get('name', 'LKS POS System')
        story.append(Paragraph(f"<b>{company_name}</b>", styles['Title']))
        
        if company_info.get('address'):
            story.append(Paragraph(company_info['address'], styles['Normal']))
        if company_info.get('phone'):
            story.append(Paragraph(f"Phone: {company_info['phone']}", styles['Normal']))
        if company_info.get('email'):
            story.append(Paragraph(f"Email: {company_info['email']}", styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("="*50, styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        
        # Receipt details
        story.append(Paragraph(f"<b>Receipt #:</b> {sale_data['sale_number']}", styles['Normal']))
        story.append(Paragraph(f"<b>Date:</b> {timestamp.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"<b>Payment:</b> {payment_info.get('method', 'Cash').title()}", styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Items table
        table_data = [['Item', 'Qty', 'Price', 'Total']]
        for item in sale_items:
            table_data.append([
                item['name'][:20],
                str(item['quantity']),
                f"{item['unit_price']:.2f} DZD",
                f"{item['total_price']:.2f} DZD"
            ])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        # Totals
        story.append(Paragraph(f"<b>Total: {sale_data['total_amount']:.2f} DZD</b>", styles['Heading2']))
        
        if payment_info.get('cash_received'):
            story.append(Paragraph(f"Cash Received: {payment_info['cash_received']:.2f} DZD", styles['Normal']))
            story.append(Paragraph(f"Change: {payment_info.get('change', 0):.2f} DZD", styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("="*50, styles['Normal']))
        
        # Footer
        footer_text = company_info.get('receipt_footer', 'Thank you for your business!')
        story.append(Paragraph(f"<i>{footer_text}</i>", styles['Normal']))
        
        # Build PDF
        doc.build(story)
        
        return file_path
    
    def _format_text_receipt(self, sale_data: Dict, items: List[Dict], payment_info: Dict, 
                           company_info: Dict, timestamp: datetime) -> str:
        """Format the text receipt content"""
        receipt = []
        receipt.append("=" * 50)
        receipt.append(f"           {company_info.get('name', 'LKS POS System')}")
        receipt.append("         Point of Sale Receipt")
        receipt.append("=" * 50)
        
        if company_info.get('address'):
            receipt.append(f"Address: {company_info['address']}")
        if company_info.get('phone'):
            receipt.append(f"Phone: {company_info['phone']}")
        if company_info.get('email'):
            receipt.append(f"Email: {company_info['email']}")
        
        receipt.append("-" * 50)
        receipt.append(f"Receipt #: {sale_data['sale_number']}")
        receipt.append(f"Date: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        receipt.append(f"Payment: {payment_info.get('method', 'Cash').title()}")
        receipt.append("-" * 50)
        receipt.append("ITEMS:")
        receipt.append("-" * 50)
        
        for item in items:
            name = item['name'][:20]
            qty = item['quantity']
            price = item['unit_price']
            item_total = item['total_price']
            
            receipt.append(f"{name:&lt;20} {qty:>3} x {price:>6.2f} = {item_total:>8.2f} DZD")
        
        receipt.append("-" * 50)
        receipt.append(f"{'TOTAL:':&lt;30} {sale_data['total_amount']:>15.2f} DZD")
        
        if payment_info.get('cash_received'):
            receipt.append(f"{'Cash Received:':&lt;30} {payment_info['cash_received']:>15.2f} DZD")
            receipt.append(f"{'Change:':&lt;30} {payment_info.get('change', 0):>15.2f} DZD")
        
        receipt.append("=" * 50)
        receipt.append("")
        receipt.append(company_info.get('receipt_footer', 'Thank you for your business!'))
        receipt.append("Please come again!")
        receipt.append("=" * 50)
        
        return "\n".join(receipt)
