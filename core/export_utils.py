"""Export utilities for generating PDF and CSV reports of cryptography results."""

import io
import csv
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_pdf_report(session_state, filename="CryptoLab_Report"):
    """
    Generate a professional PDF report of the encryption comparison.
    
    Args:
        session_state: Streamlit session state object with crypto results
        filename: Name for the PDF file (without extension)
    
    Returns:
        bytes: PDF content as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#00e5ff'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#00e5ff'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=6
    )
    
    story = []
    
    # Title
    story.append(Paragraph("🔐 CryptoLab Comparison Report", title_style))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Input Information
    story.append(Paragraph("📄 Input Information", heading_style))
    input_data = [
        ['Filename', session_state.get('filename', 'N/A')],
        ['Original Size', f"{len(session_state.get('plaintext', b'')):,} bytes"],
    ]
    input_table = Table(input_data, colWidths=[2.5*inch, 3.5*inch])
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(input_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Encryption Results
    story.append(Paragraph("🔒 Encryption Results", heading_style))
    enc_data = [
        ['Metric', 'AES', 'DES'],
        ['Key Size', f"{session_state.get('aes_key_size', 256)} bits", "56 bits (eff.)"],
        ['Block Size', "128 bits", "64 bits"],
        ['Mode', session_state.get('aes_mode', 'N/A'), session_state.get('des_mode', 'N/A')],
        ['Ciphertext Size', f"{len(session_state.get('aes_enc', b'')):,} bytes", f"{len(session_state.get('des_enc', b'')):,} bytes"],
        ['Encryption Time', f"{session_state.get('aes_enc_t', 0):.6f} seconds", f"{session_state.get('des_enc_t', 0):.6f} seconds"],
    ]
    enc_table = Table(enc_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
    enc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#00e5ff')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    story.append(enc_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Decryption Results
    story.append(Paragraph("🔓 Decryption Results", heading_style))
    dec_data = [
        ['Metric', 'AES', 'DES'],
        ['Decryption Time', f"{session_state.get('aes_dec_t', 0):.6f} seconds", f"{session_state.get('des_dec_t', 0):.6f} seconds"],
        ['Decrypted Size', f"{len(session_state.get('aes_dec', b'')):,} bytes", f"{len(session_state.get('des_dec', b'')):,} bytes"],
    ]
    dec_table = Table(dec_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
    dec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff6b35')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    story.append(dec_table)
    story.append(Spacer(1, 0.15*inch))
    
    # Verification Results
    story.append(Paragraph("✅ Verification Results", heading_style))
    aes_ok = session_state.get('aes_ok', False)
    des_ok = session_state.get('des_ok', False)
    verify_data = [
        ['Algorithm', 'Status', 'Result'],
        ['AES', '✓ PASSED' if aes_ok else '✗ FAILED', 'Original data correctly recovered' if aes_ok else 'Data mismatch detected'],
        ['DES', '✓ PASSED' if des_ok else '✗ FAILED', 'Original data correctly recovered' if des_ok else 'Data mismatch detected'],
    ]
    verify_table = Table(verify_data, colWidths=[1.5*inch, 1.5*inch, 3.5*inch])
    verify_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#39ff14')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
    ]))
    story.append(verify_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Comparison Summary
    story.append(Paragraph("📊 Comparison Summary", heading_style))
    comparison_data = [
        ['Criterion', 'AES', 'DES'],
        ['Security Status', '✓ Secure (NIST Standard)', '⚠ Deprecated (Not Secure)'],
        ['Key Space', f"2^{session_state.get('aes_key_size', 256)}", '2^56 (Brute-forceable)'],
        ['Faster Encryption', '✓ AES' if session_state.get('aes_enc_t', 0) < session_state.get('des_enc_t', 0) else '✓ DES', '—'],
        ['Authenticated Encryption', '✓ Yes (GCM)' if session_state.get('aes_mode') == 'GCM' else '✗ No', '✗ No'],
        ['Use in Production', '✓ Recommended', '✗ Not Recommended'],
    ]
    comparison_table = Table(comparison_data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
    comparison_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#663399')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9f9f9')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
    ]))
    story.append(comparison_table)
    story.append(Spacer(1, 0.2*inch))
    
    # Security Notes
    story.append(Paragraph("🔐 Security Notes", heading_style))
    story.append(Paragraph(
        f"<b>AES-{session_state.get('aes_mode', 'CBC')}:</b> Industry standard encryption algorithm, approved by NIST. "
        f"{session_state.get('aes_key_size', 256)}-bit key provides strong security against brute-force attacks. "
        f"{'GCM mode provides authenticated encryption and tamper detection.' if session_state.get('aes_mode') == 'GCM' else 'Consider using GCM mode for authenticated encryption in production.'}",
        normal_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        f"<b>DES-{session_state.get('des_mode', 'CBC')}:</b> Legacy algorithm with 56-bit key. "
        "No longer considered secure due to small key space and vulnerability to brute-force attacks. "
        "Included for educational comparison only. Use AES or 3DES for production systems.",
        normal_style
    ))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_csv_report(session_state, filename="CryptoLab_Report"):
    """
    Generate a CSV report of the encryption comparison.
    
    Args:
        session_state: Streamlit session state object with crypto results
        filename: Name for the CSV file (without extension)
    
    Returns:
        str: CSV content as string
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['CryptoLab Comparison Report'])
    writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
    writer.writerow([])
    
    # Input Information
    writer.writerow(['INPUT INFORMATION'])
    writer.writerow(['Filename', session_state.get('filename', 'N/A')])
    writer.writerow(['Original Size (bytes)', len(session_state.get('plaintext', b''))])
    writer.writerow([])
    
    # Encryption Results
    writer.writerow(['ENCRYPTION RESULTS'])
    writer.writerow(['Metric', 'AES', 'DES'])
    writer.writerow(['Key Size', f"{session_state.get('aes_key_size', 256)} bits", '56 bits (eff.)'])
    writer.writerow(['Block Size', '128 bits', '64 bits'])
    writer.writerow(['Mode', session_state.get('aes_mode', 'N/A'), session_state.get('des_mode', 'N/A')])
    writer.writerow(['Ciphertext Size (bytes)', len(session_state.get('aes_enc', b'')), len(session_state.get('des_enc', b''))])
    writer.writerow(['Encryption Time (seconds)', f"{session_state.get('aes_enc_t', 0):.6f}", f"{session_state.get('des_enc_t', 0):.6f}"])
    writer.writerow([])
    
    # Decryption Results
    writer.writerow(['DECRYPTION RESULTS'])
    writer.writerow(['Metric', 'AES', 'DES'])
    writer.writerow(['Decryption Time (seconds)', f"{session_state.get('aes_dec_t', 0):.6f}", f"{session_state.get('des_dec_t', 0):.6f}"])
    writer.writerow(['Decrypted Size (bytes)', len(session_state.get('aes_dec', b'')), len(session_state.get('des_dec', b''))])
    writer.writerow([])
    
    # Verification Results
    writer.writerow(['VERIFICATION RESULTS'])
    writer.writerow(['Algorithm', 'Status', 'Result'])
    writer.writerow(['AES', 'PASSED' if session_state.get('aes_ok') else 'FAILED', 
                     'Original data correctly recovered' if session_state.get('aes_ok') else 'Data mismatch'])
    writer.writerow(['DES', 'PASSED' if session_state.get('des_ok') else 'FAILED',
                     'Original data correctly recovered' if session_state.get('des_ok') else 'Data mismatch'])
    writer.writerow([])
    
    # Comparison Summary
    writer.writerow(['COMPARISON SUMMARY'])
    writer.writerow(['Criterion', 'AES', 'DES'])
    writer.writerow(['Security Status', 'Secure (NIST Standard)', 'Deprecated (Not Secure)'])
    writer.writerow(['Key Space', f"2^{session_state.get('aes_key_size', 256)}", '2^56'])
    writer.writerow(['Faster Encryption', 'AES' if session_state.get('aes_enc_t', 0) < session_state.get('des_enc_t', 0) else 'DES', '—'])
    writer.writerow(['Authenticated Encryption', 'Yes (GCM)' if session_state.get('aes_mode') == 'GCM' else 'No', 'No'])
    writer.writerow(['Recommended for Production', 'Yes', 'No'])
    writer.writerow([])
    
    # Security Notes
    writer.writerow(['SECURITY NOTES'])
    writer.writerow(['AES Notes', f"Industry standard encryption algorithm. {session_state.get('aes_key_size', 256)}-bit key provides strong security."])
    writer.writerow(['DES Notes', 'Legacy algorithm with 56-bit key. No longer secure. Included for educational comparison only.'])
    
    content = output.getvalue()
    output.close()
    return content
