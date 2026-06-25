import io
import re
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import logging

logger = logging.getLogger(__name__)

# Running header & footer canvas
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        # Suppress headers/footers on page 1 (cover page)
        if self._pageNumber == 1:
            return
            
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#9CA3AF")) # Gray-400
        
        # Header
        self.drawString(54, 750, "FoundrAI — Startup Analysis Report")
        self.setStrokeColor(colors.HexColor("#374151")) # Gray-700
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer
        self.line(54, 55, 558, 55)
        self.drawString(54, 40, f"Generated on {datetime.now().strftime('%B %d, %Y')} | Confidential")
        self.drawRightString(558, 40, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()

def clean_markdown_for_pdf(text):
    """
    Converts standard Markdown formatting into ReportLab's basic HTML tags.
    """
    # Remove markdown table structures entirely to avoid formatting conflicts (handled separately)
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        if line.strip().startswith("|") or line.strip().startswith("+-"):
            continue
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)
    
    # Escape standard XML characters
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # Restore HTML-like markup we need
    text = text.replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")
    text = text.replace("&lt;i&gt;", "<i>").replace("&lt;/i&gt;", "</i>")
    text = text.replace("&lt;br/&gt;", "<br/>")
    
    # Format Headings
    text = re.sub(r'^###\s+(.*)$', r'<font size="12" color="#10B981"><b>\1</b></font><br/>', text, flags=re.MULTILINE)
    text = re.sub(r'^####\s+(.*)$', r'<font size="10" color="#38BDF8"><b>\1</b></font><br/>', text, flags=re.MULTILINE)
    text = re.sub(r'^##\s+(.*)$', r'<font size="14" color="#10B981"><b>\1</b></font><br/>', text, flags=re.MULTILINE)
    text = re.sub(r'^#\s+(.*)$', r'<font size="18" color="#10B981"><b>\1</b></font><br/>', text, flags=re.MULTILINE)
    
    # Bold format (**text** -> <b>text</b>)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    
    # Bullet points (- or • -> bullet unicode)
    text = re.sub(r'^[•\-\*]\s+(.*)$', r'&bull; \1', text, flags=re.MULTILINE)
    
    # Clean up double line breaks and empty lines
    text = text.replace("\n", "<br/>")
    # Replace repeated linebreaks
    text = re.sub(r'(<br/>\s*){3,}', '<br/><br/>', text)
    
    return text

def create_pdf_report(startup_name, industry, description, audience, report_results):
    """
    Generates a professional PDF report containing the inputs and analysis from all 12 agents.
    Returns the PDF as raw bytes.
    """
    buffer = io.BytesIO()
    
    # Margins: Left/Right 0.75 in (54 pt), Top 1.0 in (72 pt), Bottom 1.0 in (72 pt)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom colors
    primary_color = colors.HexColor("#10B981") # Emerald-500
    text_color = colors.HexColor("#1F2937") # Gray-800
    bg_dark = colors.HexColor("#0B0F19") # Dark slate
    
    # Custom paragraph styles
    body_style = ParagraphStyle(
        'PDFBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=text_color,
        spaceAfter=8
    )
    
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=32,
        leading=38,
        textColor=primary_color,
        alignment=0, # Left-aligned
        spaceAfter=10
    )
    
    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=16,
        leading=22,
        textColor=colors.HexColor("#9CA3AF"),
        spaceAfter=40
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#4B5563")
    )
    
    meta_value_style = ParagraphStyle(
        'MetaValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=text_color
    )
    
    h1_style = ParagraphStyle(
        'PDFH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    story = []
    
    # --- PAGE 1: COVER PAGE ---
    story.append(Spacer(1, 1.5 * inch))
    
    # Top Accent Bar
    accent_bar = Table([[""]], colWidths=[504], rowHeights=[6])
    accent_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), primary_color),
        ('PADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(accent_bar)
    story.append(Spacer(1, 15))
    
    # Title & Subtitle
    story.append(Paragraph("FoundrAI", cover_title_style))
    story.append(Paragraph("Comprehensive Co-Founder Feasibility & Execution Report", cover_subtitle_style))
    
    story.append(Spacer(1, 1.0 * inch))
    
    # Metadata Block
    meta_data = [
        [Paragraph("Startup Name:", meta_label_style), Paragraph(startup_name, meta_value_style)],
        [Paragraph("Industry Vertical:", meta_label_style), Paragraph(industry, meta_value_style)],
        [Paragraph("Target Audience:", meta_label_style), Paragraph(audience, meta_value_style)],
        [Paragraph("Generated Date:", meta_label_style), Paragraph(datetime.now().strftime('%B %d, %Y'), meta_value_style)],
        [Paragraph("System Mode:", meta_label_style), Paragraph("Dual Multi-Agent Intelligence Platform", meta_value_style)],
    ]
    meta_table = Table(meta_data, colWidths=[130, 374])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor("#E5E7EB")),
    ]))
    story.append(meta_table)
    
    story.append(Spacer(1, 0.8 * inch))
    
    # Description block
    desc_label = Paragraph("<b>Executive Summary:</b>", body_style)
    desc_p = Paragraph(description, body_style)
    story.append(KeepTogether([desc_label, Spacer(1, 5), desc_p]))
    
    story.append(PageBreak())
    
    # --- PAGE 2 ONWARD: AGENT RESULTS ---
    agents_info = [
        ("validator", "1. Startup Idea Validation"),
        ("market_research", "2. Market Research & Sizing"),
        ("competitor_analysis", "3. Competitor Landscape"),
        ("swot", "4. SWOT Analysis"),
        ("business_model", "5. Business Model Design"),
        ("revenue_strategy", "6. Monetization & Revenue Strategy"),
        ("mvp_planner", "7. MVP Development Plan"),
        ("gtm_strategy", "8. Go-To-Market Strategy"),
        ("financial_forecast", "9. 3-Year Financial Forecast"),
        ("funding_strategy", "10. Funding & Capital Plan"),
        ("risk_assessment", "11. Risk & Mitigation Plan"),
        ("pitch_generator", "12. Investor Pitch & Deck Structure"),
    ]
    
    for key, label in agents_info:
        if key not in report_results:
            continue
            
        agent_data = report_results[key]
        agent_text = agent_data.get("text", "")
        agent_mode = agent_data.get("mode", "Demo")
        
        # Add heading
        story.append(Paragraph(label, h1_style))
        
        # Print Mode Info
        mode_style = ParagraphStyle(
            'ModeLabel',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            textColor=colors.HexColor("#10B981") if agent_mode == "Gemini" else colors.HexColor("#6B7280"),
            spaceAfter=10
        )
        story.append(Paragraph(f"Analyzed by: FoundrAI {label.split('.')[1].strip()} ({agent_mode} Mode)", mode_style))
        
        # Special layout for SWOT
        if key == "swot" and agent_data.get("structured_data"):
            swot = agent_data["structured_data"]
            try:
                # Custom Table for SWOT
                swot_data = [
                    [
                        Paragraph("<b>STRENGTHS (S)</b><br/>" + "<br/>".join([f"• {x}" for x in swot.get("s", [])]), body_style),
                        Paragraph("<b>WEAKNESSES (W)</b><br/>" + "<br/>".join([f"• {x}" for x in swot.get("w", [])]), body_style),
                    ],
                    [
                        Paragraph("<b>OPPORTUNITIES (O)</b><br/>" + "<br/>".join([f"• {x}" for x in swot.get("o", [])]), body_style),
                        Paragraph("<b>THREATS (T)</b><br/>" + "<br/>".join([f"• {x}" for x in swot.get("t", [])]), body_style),
                    ]
                ]
                swot_table = Table(swot_data, colWidths=[246, 246])
                swot_table.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 1, colors.HexColor("#D1D5DB")),
                    ('BACKGROUND', (0,0), (0,0), colors.HexColor("#ECFDF5")), # Emerald-50 light
                    ('BACKGROUND', (1,0), (1,0), colors.HexColor("#FEF2F2")), # Red-50 light
                    ('BACKGROUND', (0,1), (0,1), colors.HexColor("#EFF6FF")), # Blue-50 light
                    ('BACKGROUND', (1,1), (1,1), colors.HexColor("#FFFBEB")), # Yellow-50 light
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('TOPPADDING', (0,0), (-1,-1), 10),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                    ('LEFTPADDING', (0,0), (-1,-1), 10),
                    ('RIGHTPADDING', (0,0), (-1,-1), 10),
                ]))
                story.append(swot_table)
                story.append(Spacer(1, 15))
            except Exception as swot_err:
                logger.error(f"Error drawing SWOT Table: {swot_err}")
                
        # Special layout for Financials
        elif key == "financial_forecast" and agent_data.get("structured_data"):
            fin = agent_data["structured_data"]
            try:
                rev = fin.get("revenue", [0, 0, 0])
                exp = fin.get("expenses", [0, 0, 0])
                prof = fin.get("profit", [0, 0, 0])
                
                fin_data = [
                    ["Metric", "Year 1", "Year 2", "Year 3"],
                    ["Gross Revenue", f"${rev[0]:,}", f"${rev[1]:,}", f"${rev[2]:,}"],
                    ["Total Expenses", f"${exp[0]:,}", f"${exp[1]:,}", f"${exp[2]:,}"],
                    ["Net Profit / (Loss)", f"${prof[0]:,}", f"${prof[1]:,}", f"${prof[2]:,}"],
                    ["Profit Margin (%)", 
                     f"{int(prof[0]/rev[0]*100) if rev[0] else 0}%", 
                     f"{int(prof[1]/rev[1]*100) if rev[1] else 0}%", 
                     f"{int(prof[2]/rev[2]*100) if rev[2] else 0}%"]
                ]
                
                fin_table = Table(fin_data, colWidths=[150, 118, 118, 118])
                fin_table.setStyle(TableStyle([
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#10B981")),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                    ('ALIGN', (0,1), (0,-1), 'LEFT'), # Metric names left
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTNAME', (0,-2), (-1,-2), 'Helvetica-Bold'), # Bold net profit
                    ('BACKGROUND', (0,-2), (-1,-2), colors.HexColor("#F3F4F6")),
                    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                ]))
                story.append(fin_table)
                story.append(Spacer(1, 15))
            except Exception as fin_err:
                logger.error(f"Error drawing Financial Table: {fin_err}")
                
        # Main text rendering
        cleaned_html = clean_markdown_for_pdf(agent_text)
        para = Paragraph(cleaned_html, body_style)
        story.append(para)
        
        story.append(Spacer(1, 15))
        story.append(PageBreak()) # Clean break for each agent
        
    # Remove last pagebreak if exists to avoid trailing blank page
    if story and isinstance(story[-1], PageBreak):
        story.pop()
        
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    
    buffer.seek(0)
    return buffer.getvalue()
