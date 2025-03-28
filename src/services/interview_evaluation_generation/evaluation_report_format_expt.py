import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import inch
from reportlab.platypus import Image
from src.schemas.interview_evaluation import PDFLayoutTest, PDFSpacingConfig, PDFStyleConfig
def get_interview_evaluation_format_expt() -> PDFLayoutTest:
    # Use full path to Windows Fonts directory
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Windows Fonts directory path
    WINDOWS_FONTS_PATH = r'C:\Windows\Fonts'

    # Function to get full font path
    def get_font_path(font_filename):
        return os.path.join(WINDOWS_FONTS_PATH, font_filename)

    # Register Windows system fonts with full paths
    pdfmetrics.registerFont(TTFont('Arial', get_font_path('arial.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Bold', get_font_path('arialbd.ttf')))
    pdfmetrics.registerFont(TTFont('Calibri', get_font_path('calibri.ttf')))
    pdfmetrics.registerFont(TTFont('Calibri-Bold', get_font_path('calibrib.ttf')))

    # Get base styles
    styles = getSampleStyleSheet()

    # Create custom styles with system fonts
    title_style = ParagraphStyle(
        'Title', 
        parent=styles['Title'], 
        fontName='Arial-Bold',
        fontSize=18, 
        textColor=colors.darkblue,
        alignment=TA_CENTER, 
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        'Heading', 
        parent=styles['Heading2'], 
        fontName='Arial-Bold',
        fontSize=14, 
        textColor=colors.darkblue,
        spaceAfter=12
    )

    normal_style = ParagraphStyle(
        'Normal', 
        parent=styles['Normal'], 
        fontName='Calibri',
        fontSize=12, 
        textColor=colors.black,
        spaceAfter=6,
        leading=15  # Set line height to match PDFLayout's line_height
    )

    code_style = ParagraphStyle(
        'Code', 
        parent=styles['Code'], 
        fontName='Courier', 
        fontSize=10, 
        leftIndent=10, 
        rightIndent=10, 
        backColor=colors.lightgrey
    )

    # Create header configuration
    def create_header(canvas, doc):
        try:
            # Placeholder logo - replace with your actual logo path
            logo_path = "C:/Users/kunwa/Downloads/image (3).png"  
            
            # Check if logo exists before trying to draw
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=2*inch, height=1*inch)
                logo.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin)
            
            # Add report generation date
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Draw date
            canvas.saveState()
            canvas.setFont('Calibri', 10)
            canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.topMargin + 20, current_date)
            canvas.restoreState()
        except Exception as e:
            print(f"Error in header creation: {e}")

    # Create style configuration
    style_config = PDFStyleConfig(
        title_style=title_style, 
        heading_style=heading_style, 
        normal_style=normal_style, 
        code_style=code_style
    )
    
    # Create spacing configuration
    spacing_config = PDFSpacingConfig()

    # Create and return PDFLayout with custom configurations
    return PDFLayoutTest(
        page_size=letter,  # Use letter size as specified in the dataclass
        margin=50,  # Use 50-point margin as specified
        line_height=15,  # Use 15-point line height
        styles=style_config, 
        spacing=spacing_config,
        header_func=create_header
    )