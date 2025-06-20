📄 PDF Content Extractor – Text & Image Parser for Complex PDFs
Description:
This project is designed to automatically extract and classify text and images from complex PDF documents, including both standard and scanned/image-based files. It intelligently processes headers, footers, text blocks, and embedded images—leveraging OCR for non-searchable content—and outputs results in a structured JSON format. All images are saved in organized folders by page, enabling easy access and further processing.

✅ Features
Extracts text blocks, headers, footers, and images from standard PDFs

Uses OCR to extract text from scanned/image-based PDFs

Saves all images in organized folders by page

Removes duplicate and unwanted content

Outputs all data in a clean, structured JSON file

🛠 Technologies Used
PyMuPDF (fitz)

pytesseract (Tesseract OCR)

OpenCV

Pillow (PIL)

🚀 How to Run/Use the Project
Install Tesseract OCR

Download and install from: Tesseract OCR (UB Mannheim)

Add it to your system's PATH after installation.

Install Python dependencies
Run the following command in your terminal:

pip install pymupdf pytesseract opencv-python pillow

Prepare your PDF file

Place your PDF file in the project directory.

Configure the script

Open app1.py

Set the pdf_path variable to your PDF file name:

pdf_path = "yourfile.pdf"

Open a terminal in the project directory and run:

python app1.py

Check output
View the pdf_data.json file for structured extracted data.

Browse the images/ folder to access saved images, organized by page.
