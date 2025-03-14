import datetime
from mistralai import Mistral
import os

api_key = os.environ["MISTRAL_API_KEY"]

client = Mistral(api_key=api_key)

def ocr_to_markdown(ocr_response, output_filename=None):
    """
    Convert OCR response to a markdown file.
    
    Args:
        ocr_response: The OCR response object from the Mistral OCR API
        output_filename: Optional output filename, defaults to 'ocr_output_{timestamp}.md'
    
    Returns:
        str: Path to the created markdown file
    """
    if output_filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"ocr_output_{timestamp}.md"
    
    if hasattr(ocr_response, 'pages'):
        return pages_to_markdown(ocr_response.pages, output_filename)
    
    if isinstance(ocr_response, dict):
        text_content = ocr_response.get('text', '')
        
        metadata = ocr_response.get('metadata', {})
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        if 'title' in metadata:
            f.write(f"# {metadata['title']}\n\n")
        else:
            f.write("# OCR Document Output\n\n")
        
        f.write("## Document Metadata\n\n")
        
        if metadata:
            for key, value in metadata.items():
                if isinstance(value, (dict, list)):
                    f.write(f"### {key.capitalize()}\n")
                    f.write("```json\n")
                    f.write(json.dumps(value, indent=2))
                    f.write("\n```\n\n")
                else:
                    f.write(f"- **{key.capitalize()}**: {value}\n")
        else:
            f.write("*No metadata available*\n")
        
        f.write("\n## Document Content\n\n")
        f.write(text_content)
    
    print(f"Markdown file created: {output_filename}")
    return output_filename

def pages_to_markdown(pages, output_filename):
    """
    Convert OCR response pages to a markdown file.
    
    Args:
        pages: List of OCRPageObject objects
        output_filename: Output filename for the markdown file
    
    Returns:
        str: Path to the created markdown file
    """
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write("# OCR Document Output\n\n")
        
        f.write("## Document Metadata\n\n")
        f.write(f"- **Total Pages**: {len(pages)}\n\n")
        
        for i, page in enumerate(pages):
            f.write(f"## Page {i+1}\n\n")
            
            if hasattr(page, 'dimensions'):
                dims = page.dimensions
                f.write(f"- **Dimensions**: {dims.width}x{dims.height} pixels\n")
                if hasattr(dims, 'dpi') and dims.dpi:
                    f.write(f"- **DPI**: {dims.dpi}\n")
                f.write("\n")
            
            if hasattr(page, 'markdown') and page.markdown:
                f.write(page.markdown)
            else:
                f.write("*No content available for this page*")
            
            f.write("\n\n")
            
            if hasattr(page, 'images') and page.images:
                f.write(f"### Images on Page {i+1}\n\n")
                for j, img in enumerate(page.images):
                    f.write(f"#### Image {j+1}\n\n")
                f.write("\n")
    
    print(f"Markdown file created: {output_filename}")
    return output_filename

if __name__ == "__main__":
    uploaded_pdf = client.files.upload(
    file={
        "file_name": "filename",
        "content": open("path/filename.pdf", "rb"),
    },
    purpose="ocr"
    )  

    signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)

    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url.url,
        }
    )

    ocr_to_markdown(ocr_response, "document_extract.md")