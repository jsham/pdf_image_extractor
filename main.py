import pdfplumber
import fitz
import os
import io
from PIL import Image
import re

PDF_PATH = "./docs/Knox Meeting_user_manual.pdf"
OUTPUT_IMAGES_DIR = "images"

def sanitize_text(text):
    """Sanitize and truncate text for use in filenames."""
    if not text:
        return "unknown"
    text = re.sub(r'[\\/*?:"<>|]', "", text)
    text = ''.join([c for c in text if c.isprintable() and not c.isspace()])
    return text[:50]

def resize_image(image):
    """Resize the image to a maximum size of 70% of the larger dimension."""
    max_size = int(max(image.width, image.height) * 0.7)
    if image.width > max_size or image.height > max_size:
        if image.width > image.height:
            aspect_ratio = image.height / image.width
            new_width = max_size
            new_height = int(max_size * aspect_ratio)
        else:
            aspect_ratio = image.width / image.height
            new_height = max_size
            new_width = int(max_size * aspect_ratio)
        image = image.resize((new_width, new_height), Image.BICUBIC)
    return image

def generate_unique_filename(directory, base_filename, extension):
    """Generate a unique filename if a file already exists."""
    counter = 1
    unique_filename = f"{base_filename}{extension}"
    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base_filename}({counter}){extension}"
        counter += 1
    return unique_filename

def save_images_from_page(document, page_number, headings):
    """Extract and save images from a specific page of the PDF document."""
    saved_images = []
    pagina = document.load_page(page_number)
    imagens = pagina.get_images(full=True)
    heading_str = '-'.join(headings)
    img_index = 1

    for img in imagens:
        try:
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]
            image = Image.open(io.BytesIO(image_bytes))
            if image.width < 500 or image.height < 500:
                continue
            image = resize_image(image)
            base_filename = f"{page_number + 1}_{heading_str}_{img_index:04}"
            extension = ".webp"
            os.makedirs(OUTPUT_IMAGES_DIR, exist_ok=True)
            image_filename = generate_unique_filename(OUTPUT_IMAGES_DIR, base_filename, extension)
            full_image_path = os.path.join(OUTPUT_IMAGES_DIR, image_filename)
            image.save(full_image_path, "WEBP", quality=85)
            saved_images.append(full_image_path)
            img_index += 1
        except Exception as e:
            print(f"Error saving image on page {page_number + 1}: {e}")

    return saved_images

def extract_headings_from_text(text):
    """Extract all levels of headings from text, skipping possible page numbers."""
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    headings = re.findall(r'\d+(?:\.\d+)*', text)
    return headings if headings else ["0"]

def process_pdf(pdf_path):
    """Process the PDF to extract text and images."""
    document = fitz.open(pdf_path)
    print("[document]: ", document)
    
    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages
        total_images = 0
        previous_heading_str = ""
        
        for index, pagina in enumerate(pages):
            texto = pagina.extract_text() or ""
            print(f"Text on Page {index + 1}:")
            headings = extract_headings_from_text(texto)
            heading_str = '-'.join(headings)

            if heading_str != previous_heading_str:
                img_index = 1
                previous_heading_str = heading_str

            imagens = save_images_from_page(document, index, headings)
            print(f"Images Extracted from Page {index + 1}: {len(imagens)} heading:{headings}")
            total_images += len(imagens)
            for img in imagens:
                print(f"Image Saved: {img}")
            print("=" * 50)
        
        print(f"Total Images Extracted: {total_images}")
        print("Extraction Done!")
    
    document.close()

if __name__ == "__main__":
    process_pdf(PDF_PATH)
