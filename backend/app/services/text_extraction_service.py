"""Text extraction service for processing different document types."""

import os
import re
from typing import Optional
import pdfplumber
import pytesseract
from PIL import Image
from docx import Document as DocxDocument

from app.core.config import settings


class TextExtractionService:
    """Service for extracting text from various document formats."""
    
    def __init__(self):
        # Set Tesseract command path if configured
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
    
    async def extract_text(self, file_path: str, mime_type: str) -> Optional[str]:
        """Extract text from a document based on its type."""
        try:
            if mime_type == "application/pdf":
                return await self._extract_from_pdf(file_path)
            elif mime_type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                return await self._extract_from_docx(file_path)
            elif mime_type.startswith("image/"):
                return await self._extract_from_image(file_path)
            else:
                # Try to read as plain text
                return await self._extract_from_text(file_path)
        except Exception as e:
            print(f"Error extracting text from {file_path}: {str(e)}")
            return None
    
    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        text_content = []
        
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Try text extraction first
                page_text = page.extract_text()
                
                if page_text and page_text.strip():
                    text_content.append(f"[Page {page_num + 1}]\n{page_text}")
                else:
                    # If no text found, try OCR on the page image
                    try:
                        page_image = page.to_image(resolution=300)
                        ocr_text = pytesseract.image_to_string(page_image.original)
                        if ocr_text.strip():
                            text_content.append(f"[Page {page_num + 1} - OCR]\n{ocr_text}")
                    except Exception as e:
                        print(f"OCR failed for page {page_num + 1}: {str(e)}")
                        continue
        
        return "\n\n".join(text_content)
    
    async def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX files."""
        doc = DocxDocument(file_path)
        text_content = []
        
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text)
        
        return "\n\n".join(text_content)
    
    async def _extract_from_image(self, file_path: str) -> str:
        """Extract text from images using OCR."""
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image, lang='eng+ind')  # English + Indonesian
            return text
        except Exception as e:
            print(f"OCR failed for image {file_path}: {str(e)}")
            return ""
    
    async def _extract_from_text(self, file_path: str) -> str:
        """Extract text from plain text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception:
                return ""
    
    async def clean_text(self, text: str) -> str:
        """Clean extracted text by removing unwanted elements."""
        if not text:
            return ""
        
        # Remove common watermarks and headers/footers patterns
        cleaned_text = self._remove_watermarks(text)
        cleaned_text = self._remove_headers_footers(cleaned_text)
        cleaned_text = self._remove_page_numbers(cleaned_text)
        cleaned_text = self._normalize_whitespace(cleaned_text)
        cleaned_text = self._remove_repetitive_content(cleaned_text)
        
        return cleaned_text
    
    def _remove_watermarks(self, text: str) -> str:
        """Remove common watermark patterns."""
        # Common watermark patterns
        watermark_patterns = [
            r'CONFIDENTIAL.*?\n',
            r'DRAFT.*?\n',
            r'PROPRIETARY.*?\n',
            r'COPYRIGHT.*?\n',
            r'©.*?\n',
            r'WATERMARK.*?\n',
        ]
        
        for pattern in watermark_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        return text
    
    def _remove_headers_footers(self, text: str) -> str:
        """Remove headers and footers that appear repeatedly."""
        lines = text.split('\n')
        
        # Find lines that appear frequently (likely headers/footers)
        line_counts = {}
        for line in lines:
            stripped_line = line.strip()
            if len(stripped_line) > 5 and len(stripped_line) < 100:  # Reasonable header/footer length
                line_counts[stripped_line] = line_counts.get(stripped_line, 0) + 1
        
        # Remove lines that appear more than 3 times (likely headers/footers)
        frequent_lines = {line for line, count in line_counts.items() if count > 3}
        
        filtered_lines = []
        for line in lines:
            if line.strip() not in frequent_lines:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _remove_page_numbers(self, text: str) -> str:
        """Remove standalone page numbers."""
        # Remove lines that are just page numbers
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            stripped_line = line.strip()
            # Check if line is just a number (page number)
            if not (stripped_line.isdigit() and len(stripped_line) <= 4):
                # Also check for patterns like "Page 1", "- 1 -", etc.
                if not re.match(r'^(page\s+)?\d+(\s+of\s+\d+)?$', stripped_line, re.IGNORECASE):
                    if not re.match(r'^[-\s]*\d+[-\s]*$', stripped_line):
                        filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in the text."""
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Replace multiple newlines with double newline
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        
        # Remove trailing whitespace from lines
        lines = [line.rstrip() for line in text.split('\n')]
        
        return '\n'.join(lines).strip()
    
    def _remove_repetitive_content(self, text: str) -> str:
        """Remove repetitive boilerplate content."""
        lines = text.split('\n')
        
        # Remove very short lines that might be artifacts
        filtered_lines = []
        for line in lines:
            stripped_line = line.strip()
            # Keep lines that are either empty, or have substantial content
            if not stripped_line or len(stripped_line) > 3:
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
