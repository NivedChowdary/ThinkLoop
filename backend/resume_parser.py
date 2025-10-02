import PyPDF2
import docx
import io

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_bytes)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        return None

def extract_text_from_docx(file_bytes):
    """Extract text from Word document"""
    try:
        doc_file = io.BytesIO(file_bytes)
        doc = docx.Document(doc_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    except Exception as e:
        return None

def parse_resume_file(filename, file_bytes):
    """Parse resume based on file type"""
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.pdf'):
        return extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith('.docx') or filename_lower.endswith('.doc'):
        return extract_text_from_docx(file_bytes)
    else:
        return None