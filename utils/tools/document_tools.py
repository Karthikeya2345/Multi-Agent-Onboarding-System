# utils/tools/document_tools.py

import os
import json # <-- Make sure json is imported
from pypdf import PdfReader

def read_pdf_file(file_path: str) -> str:
    """
    Reads the text content from a PDF file given its path.
    ALWAYS returns a JSON string (either with data or with an error).
    """
    print(f"--- Tool: Reading PDF at {file_path} ---")
    try:
        if not os.path.exists(file_path):
            # Return JSON error
            return json.dumps({"error": f"File not found at path: {file_path}"})
        
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
        
        if not text:
            # Return JSON error
            return json.dumps({"error": "Could not extract any text from the PDF. The file might be empty or an image."})
        
        # Return JSON success
        return json.dumps({"extracted_text": text})

    except Exception as e:
        # Return JSON error
        return json.dumps({"error": f"Error reading PDF: {e}"})