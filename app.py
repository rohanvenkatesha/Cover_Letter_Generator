from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.units import inch  # Import the 'inch' variable
from io import BytesIO
import json

app = Flask(__name__)

# Load templates from JSON file
def load_templates():
    with open('templates.json', 'r') as file:
        templates = json.load(file)
    return templates

@app.route('/')
def index():
    templates = load_templates()
    return render_template('index.html', templates=templates)

@app.route('/generate', methods=['POST'])
def generate():
    company_name = request.form['company_name']
    role_name = request.form['role_name']
    hiring_manager = request.form['hiring_manager']
    selected_template = request.form['template']
    custom_content = request.form.get('custom_content', '')

    # Load templates
    templates = load_templates()
    cover_letter_template = templates.get(selected_template, {}).get('content', '')

    # Replace placeholders with user input
    cover_letter = cover_letter_template.format(
        company_name=company_name,
        role_name=role_name,
        hiring_manager=hiring_manager
    )

    # If custom content is provided, use it instead
    if custom_content:
        cover_letter = custom_content.format(
            company_name=company_name,
            role_name=role_name,
            hiring_manager=hiring_manager
        )

    # Create a PDF with styling
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=1*inch, rightMargin=1*inch, topMargin=1*inch, bottomMargin=1*inch)
    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        name='Header',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        spaceAfter=6,
        textColor='#333333'
    )
    body_style = ParagraphStyle(
        name='Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=13,
        spaceAfter=6,
        textColor='#000000'
    )

    # Add content to the PDF
    content = []

    # Header (Your Name and Contact Info)
    header_text = f"""
    <b>Your Name</b><br/>
    <font size="10">Your Address | Your City, State ZIP | Your Email | Your Phone Number</font><br/><br/>
    """
    content.append(Paragraph(header_text, header_style))
    content.append(Spacer(1, 12))

    # Cover Letter Body
    content.append(Paragraph(cover_letter, body_style))

    # Build the PDF
    doc.build(content)

    # Return the PDF as a downloadable file
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='cover_letter.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)