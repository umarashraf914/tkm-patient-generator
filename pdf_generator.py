"""
═══════════════════════════════════════════════════════════════════════════════
TKM Patient Generator - PDF Export Utility
한의 임상 가상환자 시나리오 PDF 내보내기
═══════════════════════════════════════════════════════════════════════════════
"""

import io
from datetime import datetime
from fpdf import FPDF


class KoreanPDF(FPDF):
    """PDF class with Korean font support."""
    
    def __init__(self):
        super().__init__()
        # Use built-in font that supports more characters
        # For full Korean support, we'll use unicode mode
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        """Add header to each page."""
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'TKM Patient Generator', align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(5)
    
    def footer(self):
        """Add footer with page number."""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')


def generate_patient_pdf(summary: str, scenario: str, patient_info: dict = None) -> bytes:
    """
    Generate a PDF document for the patient scenario.
    
    Args:
        summary: Patient summary text
        scenario: Full patient scenario text
        patient_info: Optional dictionary with patient metadata
    
    Returns:
        PDF file as bytes
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Title
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Virtual Patient Case Report', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.cell(0, 10, '(Han-ui Clinical Scenario Generator)', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)
    
    # Generation timestamp
    pdf.set_font('Helvetica', 'I', 10)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 8, f'Generated: {timestamp}', align='R', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)
    
    # Divider line
    pdf.set_draw_color(100, 100, 100)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Patient info section (if provided)
    if patient_info:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, 'Patient Information', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('Helvetica', '', 10)
        
        info_items = [
            ('Disease', patient_info.get('disease', 'N/A')),
            ('Pattern', patient_info.get('pattern', 'N/A')),
            ('Age/Sex', f"{patient_info.get('age', 'N/A')} / {patient_info.get('sex', 'N/A')}"),
            ('Height/Weight', f"{patient_info.get('height', 'N/A')}cm / {patient_info.get('weight', 'N/A')}kg"),
            ('Vitals', f"BP {patient_info.get('sbp', 'N/A')}/{patient_info.get('dbp', 'N/A')} mmHg, "
                      f"HR {patient_info.get('pulse_rate', 'N/A')}/min, "
                      f"Temp {patient_info.get('temp', 'N/A')}C"),
        ]
        
        for label, value in info_items:
            pdf.cell(40, 6, f'{label}:', new_x='RIGHT')
            pdf.cell(0, 6, str(value), new_x='LMARGIN', new_y='NEXT')
        
        pdf.ln(5)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
    
    # Summary section
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Summary', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 10)
    
    # Handle Korean text by encoding/replacing unsupported characters
    safe_summary = _make_safe_text(summary)
    pdf.multi_cell(0, 6, safe_summary)
    pdf.ln(5)
    
    # Scenario section
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Patient Scenario', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 10)
    
    # Process scenario text - handle Korean characters
    safe_scenario = _make_safe_text(scenario)
    
    # Split into paragraphs and add each
    paragraphs = safe_scenario.split('\n')
    for para in paragraphs:
        para = para.strip()
        if para:
            # Check if this is a section header (starts with special chars)
            if para.startswith('[') or para.startswith('【') or para.startswith('-'):
                pdf.set_font('Helvetica', 'B', 10)
                pdf.multi_cell(0, 6, para)
                pdf.set_font('Helvetica', '', 10)
            else:
                pdf.multi_cell(0, 6, para)
            pdf.ln(2)
    
    # Output as bytes (convert bytearray to bytes for Streamlit)
    output = pdf.output()
    if isinstance(output, bytearray):
        return bytes(output)
    elif isinstance(output, bytes):
        return output
    else:
        return output.encode('latin-1') if isinstance(output, str) else bytes(output)


def _make_safe_text(text: str) -> str:
    """
    Convert Korean text to a safe format for PDF.
    Since basic FPDF doesn't support Korean well, we'll create a 
    transliteration/replacement approach for common patterns.
    
    For full Korean support, consider using fonts like NanumGothic.
    """
    if not text:
        return ""
    
    # Common Korean medical terms mapping to romanization/English
    replacements = {
        # Section markers
        '【': '[',
        '】': ']',
        '→': '->',
        '°': ' deg ',
        
        # Common medical terms (한의학)
        '환자정보': '[Patient Info]',
        '주소증': '[Chief Complaint]',
        '현병력': '[Present Illness]',
        '과거력': '[Past History]',
        '가족력': '[Family History]',
        '사회력': '[Social History]',
        '계통적 문진': '[Review of Systems]',
        '신체검진 소견': '[Physical Exam]',
        '설진 소견': '[Tongue Exam]',
        '맥진 소견': '[Pulse Exam]',
        '활력징후': 'Vital Signs',
        
        # Common symptoms
        '발열': 'Fever',
        '오한': 'Chills',
        '두통': 'Headache',
        '기침': 'Cough',
        '콧물': 'Runny nose',
        '인후통': 'Sore throat',
        '몸살': 'Body ache',
        '요통': 'Low back pain',
        '소화불량': 'Dyspepsia',
        '복통': 'Abdominal pain',
        '오심': 'Nausea',
        '구토': 'Vomiting',
        '설사': 'Diarrhea',
        '변비': 'Constipation',
        
        # Demographics
        '남': 'M',
        '여': 'F',
        '세': 'y/o',
        
        # Common descriptors
        '없음': 'None',
        '있음': 'Present',
        '경미': 'Mild',
        '중등도': 'Moderate', 
        '심함': 'Severe',
        '정상': 'Normal',
        '보통': 'Normal',
        
        # Vitals
        '수축기혈압': 'SBP',
        '이완기혈압': 'DBP',
        '맥박': 'HR',
        '체온': 'Temp',
        '호흡': 'RR',
        
        # Time
        '일 전': ' days ago',
        '주 전': ' weeks ago',
        '개월 전': ' months ago',
        '시간': 'hours',
        '분': 'min',
        '회': 'times',
        
        # Pattern names
        '풍한형': 'Wind-Cold',
        '풍열형': 'Wind-Heat',
        '풍조형': 'Wind-Dryness',
        '한증형': 'Cold Pattern',
        '열증형': 'Heat Pattern',
        '기허형': 'Qi Deficiency',
        '양허형': 'Yang Deficiency',
        '음허형': 'Yin Deficiency',
        '담음형': 'Phlegm-Fluid',
        '식적형': 'Food Stagnation',
        '어혈형': 'Blood Stasis',
        '기체형': 'Qi Stagnation',
        
        # Tongue/Pulse
        '설질': 'Tongue body',
        '설태': 'Tongue coating',
        '부맥': 'Floating pulse',
        '침맥': 'Sinking pulse',
        '세맥': 'Thin pulse',
        '홍맥': 'Flooding pulse',
        '유력': 'Strong',
        '무력': 'Weak',
        '활맥': 'Slippery pulse',
        '삽맥': 'Rough pulse',
        '담백': 'Pale',
        '담홍': 'Pale red',
        '홍설': 'Red',
        '백태': 'White coating',
        '황태': 'Yellow coating',
        '박태': 'Thin coating',
        '후태': 'Thick coating',
    }
    
    result = text
    for korean, english in replacements.items():
        result = result.replace(korean, english)
    
    # Remove any remaining non-ASCII characters that FPDF can't handle
    # This is a fallback - ideally we'd use a Korean-supporting font
    result = result.encode('ascii', 'replace').decode('ascii')
    
    return result


def generate_patient_pdf_korean(summary: str, scenario: str, patient_info: dict = None) -> bytes:
    """
    Generate a PDF document with better Korean support using Unicode.
    
    This version attempts to use a Unicode font if available.
    Falls back to ASCII transliteration if Korean fonts aren't available.
    
    Args:
        summary: Patient summary text  
        scenario: Full patient scenario text
        patient_info: Optional dictionary with patient metadata
    
    Returns:
        PDF file as bytes
    """
    try:
        # Try to create PDF with Unicode support
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Try to add Korean font (NanumGothic is commonly available)
        # If this fails, we'll fall back to the ASCII version
        try:
            import os
            # Common Korean font paths
            font_paths = [
                "C:/Windows/Fonts/malgun.ttf",  # Windows Malgun Gothic
                "C:/Windows/Fonts/NanumGothic.ttf",
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",  # Linux
                "/System/Library/Fonts/AppleSDGothicNeo.ttc",  # macOS
            ]
            
            font_added = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdf.add_font("Korean", "", font_path, uni=True)
                    pdf.set_font("Korean", "", 12)
                    font_added = True
                    break
            
            if not font_added:
                # No Korean font found, use fallback
                raise FileNotFoundError("No Korean font found")
                
        except Exception:
            # Fall back to ASCII version
            return generate_patient_pdf(summary, scenario, patient_info)
        
        # Title
        pdf.set_font('Korean', '', 16)
        pdf.cell(0, 10, '한의 임상 가상환자 시나리오', align='C', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(5)
        
        # Timestamp
        pdf.set_font('Korean', '', 10)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.cell(0, 8, f'생성일시: {timestamp}', align='R', new_x='LMARGIN', new_y='NEXT')
        pdf.ln(5)
        
        # Line
        pdf.set_draw_color(100, 100, 100)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Patient info
        if patient_info:
            pdf.set_font('Korean', '', 12)
            pdf.cell(0, 8, '환자 기본정보', new_x='LMARGIN', new_y='NEXT')
            pdf.set_font('Korean', '', 10)
            
            info_items = [
                ('질환명', patient_info.get('disease', 'N/A')),
                ('변증/처방', patient_info.get('pattern', 'N/A')),
                ('나이/성별', f"{patient_info.get('age', 'N/A')}세 / {patient_info.get('sex', 'N/A')}"),
                ('신장/체중', f"{patient_info.get('height', 'N/A')}cm / {patient_info.get('weight', 'N/A')}kg"),
                ('활력징후', f"BP {patient_info.get('sbp', 'N/A')}/{patient_info.get('dbp', 'N/A')} mmHg, "
                          f"맥박 {patient_info.get('pulse_rate', 'N/A')}/분, "
                          f"체온 {patient_info.get('temp', 'N/A')}°C"),
            ]
            
            for label, value in info_items:
                pdf.cell(40, 6, f'{label}:', new_x='RIGHT')
                pdf.cell(0, 6, str(value), new_x='LMARGIN', new_y='NEXT')
            
            pdf.ln(5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)
        
        # Summary
        pdf.set_font('Korean', '', 12)
        pdf.cell(0, 8, '요약', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('Korean', '', 10)
        pdf.multi_cell(0, 6, summary)
        pdf.ln(5)
        
        # Scenario
        pdf.set_font('Korean', '', 12)
        pdf.cell(0, 8, '환자 시나리오', new_x='LMARGIN', new_y='NEXT')
        pdf.set_font('Korean', '', 10)
        
        paragraphs = scenario.split('\n')
        for para in paragraphs:
            para = para.strip()
            if para:
                pdf.multi_cell(0, 6, para)
                pdf.ln(2)
        
        # Convert bytearray to bytes for Streamlit
        output = pdf.output()
        if isinstance(output, bytearray):
            return bytes(output)
        elif isinstance(output, bytes):
            return output
        else:
            # Handle string output (older fpdf versions)
            return output.encode('latin-1') if isinstance(output, str) else bytes(output)
        
    except Exception as e:
        # If anything fails, use ASCII fallback
        print(f"Korean PDF failed, using fallback: {e}")
        return generate_patient_pdf(summary, scenario, patient_info)
