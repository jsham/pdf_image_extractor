import os
import fitz  # PyMuPDF
from PIL import Image
import io
import logging

# 설정
DOCS_DIR = './docs'
IMAGES_DIR = './images'

# 디렉토리 생성
os.makedirs(IMAGES_DIR, exist_ok=True)

# 시작 시 images 디렉토리의 모든 파일 삭제
for f in os.listdir(IMAGES_DIR):
    file_path = os.path.join(IMAGES_DIR, f)
    if os.path.isfile(file_path):
        os.remove(file_path)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# PDF 파일 목록 확인
pdf_files = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith('.pdf')]
if not pdf_files:
    logging.error('PDF 파일이 docs 디렉토리에 없습니다.')
    exit(1)

# 이미지 추출 및 저장 함수
def save_images_from_pdf(pdf_path, doc_name):
    document = fitz.open(pdf_path)
    image_count = 0

    for page_num in range(len(document)):
        page = document.load_page(page_num)
        images = page.get_images(full=True)
        
        # 이미지 정보를 y좌표를 기준으로 정렬
        image_infos = []
        for img in images:
            xref = img[0]
            base_image = document.extract_image(xref)
            image_bytes = base_image["image"]
            bbox = page.get_image_bbox(img)
            y_coord = bbox.y0  # 이미지의 상단 y좌표
            image_infos.append((xref, image_bytes, y_coord))
        
        image_infos.sort(key=lambda x: x[2])  # y좌표 기준으로 정렬

        line_num = 1
        image_index = 1

        for xref, image_bytes, y_coord in image_infos:
            image = Image.open(io.BytesIO(image_bytes))

            # 이미지 직전의 텍스트 라인 번호 계산
            text_instances = page.search_for(" ")  # 모든 텍스트 위치 검색
            previous_line_num = 0
            for inst in text_instances:
                if inst[3] <= y_coord:  # 텍스트의 하단 y좌표가 이미지의 y좌표보다 작거나 같을 때
                    previous_line_num = max(previous_line_num, int(inst[1] // 12) + 1)  # 12는 대략적인 라인 높이, 필요 시 조정

            line_num = previous_line_num + 1

            file_name = f"{doc_name}_{page_num+1}_{image_index}_{line_num}.webp"
            file_path = os.path.join(IMAGES_DIR, file_name)

            if os.path.exists(file_path):
                logging.info(f"덮어쓰기: {file_path}")

            image.save(file_path, "WEBP")
            print("Image saved: ", file_name)
            image_index += 1
            image_count += 1

    return image_count

# 각 PDF 파일에서 이미지 추출
for pdf_file in pdf_files:
    doc_name = pdf_file[:4]
    pdf_path = os.path.join(DOCS_DIR, pdf_file)
    extracted_image_count = save_images_from_pdf(pdf_path, doc_name)
    logging.info(f"{pdf_file}에서 {extracted_image_count}개의 이미지를 추출했습니다. 저장 위치: {IMAGES_DIR}")

logging.info("프로그램이 종료되었습니다.")
