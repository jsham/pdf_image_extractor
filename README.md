# Image Extractor from PDF File
## make image file ./images/
### file name : [pageNo]_[Heading 1]-[Heading 2]-[Heading 3]- ... _[image_index].webp
### Docker Build
docker build -t pdf-image-extractor .

### Docker Run
docker run --rm -v $(pwd)/images:/app/images pdf-image-extractor

### Directory Tree
project-directory/
│
├── Dockerfile
├── extract_images.py
├── requirements.txt
├── docs/
│   └── ... (PDF 파일들)
└── images/