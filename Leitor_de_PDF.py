import fitz  # PyMuPDF
from PyPDF2 import PdfReader
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re
from collections import Counter
import os

# Configure o caminho do executável do Tesseract se necessário
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Atualize este caminho conforme necessário

def preprocess_image(image):
    # Converte para tons de cinza
    gray_image = image.convert('L')
    # Aumenta o contraste
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2)
    # Filtra a imagem para melhor detecção de bordas
    filtered_image = enhanced_image.filter(ImageFilter.MedianFilter())
    return filtered_image

def extract_text_from_pdf(file_path):
    text = ""
    try:
        # Tenta ler o PDF como texto usando PyPDF2 com PdfReader
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"Não foi possível extrair texto com PyPDF2: {e}")
    
    if not text:
        print("Tentando extração com PyMuPDF...")
        try:
            pdf_document = fitz.open(file_path)
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                page_text = page.get_text()
                if page_text:
                    text += page_text
        except Exception as e:
            print(f"Não foi possível extrair texto com PyMuPDF: {e}")
    
    if not text:
        print("Tentando OCR em imagens...")
        try:
            pdf_document = fitz.open(file_path)
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                preprocessed_img = preprocess_image(img)
                ocr_text = pytesseract.image_to_string(preprocessed_img, lang='por', config='--psm 6')
                if ocr_text:
                    text += ocr_text
        except Exception as e:
            print(f"Não foi possível extrair texto com OCR: {e}")
    
    return text

def find_specific_keywords(text, search_keywords):
    text_lower = text.lower()
    word_counts = Counter(re.findall(r'\b\w+\b', text_lower))
    found_keywords = {}
    
    for word in search_keywords:
        word_lower = word.lower()
        if word_lower in word_counts:
            found_keywords[word] = word_counts[word_lower]
        else:
            found_keywords[word] = 0
    
    return found_keywords

def list_all_words(text):
    text_lower = text.lower()
    all_words = re.findall(r'\b\w+\b', text_lower)
    unique_words = sorted(set(all_words))  # Remove duplicatas e ordena
    return unique_words

def process_pdf(pdf_path, search_keywords):
    print(f"Processando {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        print("Nenhum texto foi extraído.")
        return
    
    # Contar e listar palavras-chave
    found_keywords = find_specific_keywords(text, search_keywords)
    
    # Listar todas as palavras encontradas
    unique_words = list_all_words(text)
    
    for word, count in found_keywords.items():
        if count > 0:
            print(f"A palavra '{word}' foi encontrada {count} vez(es).")
        else:
            print(f"A palavra '{word}' não foi encontrada no texto.")
    
    print("\nTodas as palavras encontradas no texto:")
    print(", ".join(unique_words))


pdf_path = '/content/matricula1.pdf'
#pdf_path = '/content/FolMen_202406_51420240719180236.pdf'
#pdf_path = '/content/pdf_rg.pdf'  # Substitua este caminho pelo caminho do seu arquivo PDF
search_keywords = ['Apartamento', 'palavra2', 'palavra3']  # Substitua pelas palavras que você deseja procurar
process_pdf(pdf_path, search_keywords)
