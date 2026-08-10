import os
import PyPDF2
import docx

def extract_text(file_path):
    """
    Extracts text from a given file path based on its extension.
    Supports .txt, .pdf, and .docx.
    """
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    try:
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
        elif ext == '.pdf':
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num in range(len(reader.pages)):
                    page_text = reader.pages[page_num].extract_text()
                    if page_text:
                        text += page_text + "\n"
                        
        elif ext == '.docx':
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
                
        else:
            return None, "Unsupported file format. Please upload PDF, DOCX, or TXT."
            
        if not text.strip():
            return None, "Document appears to be empty or contains unreadable text."
            
        return text, None
        
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return None, f"An error occurred while reading the file: {str(e)}"
