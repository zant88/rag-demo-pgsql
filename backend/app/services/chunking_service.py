"""Chunking service for Indonesian language text processing."""

import re
from typing import List
import tiktoken


class ChunkingService:
    """Service for chunking text with Indonesian language considerations."""
    
    DEFAULT_CHUNK_SIZE = 1000  # Original chunk size
    DEFAULT_CHUNK_OVERLAP = 200

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size if chunk_size is not None else self.DEFAULT_CHUNK_SIZE
        self.chunk_overlap = chunk_overlap if chunk_overlap is not None else self.DEFAULT_CHUNK_OVERLAP
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
    
    async def chunk_text(self, text: str) -> List[str]:
        """Chunk text using semantic coherence for Indonesian language."""
        if not text or not text.strip():
            return []
        
        # First, split by major sections (double newlines)
        sections = self._split_by_sections(text)
        
        chunks = []
        for section in sections:
            if not section.strip():
                continue
            
            # Check if section is small enough to be a single chunk
            if self._count_tokens(section) <= self.chunk_size:
                chunks.append(section.strip())
            else:
                # Split large sections into smaller chunks
                section_chunks = self._chunk_section(section)
                chunks.extend(section_chunks)
        
        # Apply overlap between chunks
        overlapped_chunks = self._apply_overlap(chunks)

        return overlapped_chunks
    
    def _split_by_sections(self, text: str) -> List[str]:
        """Split text by major sections and by explicit section headers (e.g., 'Business Scope', 'Produk', 'Layanan')."""
        # Define section header keywords (case-insensitive, Indonesian and English)
        header_keywords = [
            r'Business Scope', r'Produk', r'Layanan', r'Product & Service', r'Product and Service',
            r'Services', r'Service', r'Scope', r'Lingkup Usaha', r'Bidang Usaha', r'Jasa', r'Layanan'
        ]
        # Build a regex pattern to match section headers at line start
        header_pattern = r'(^|\n)\s*(' + '|'.join(header_keywords) + r')\s*:?\s*(\n|$)'
        # Split text at each header occurrence
        matches = list(re.finditer(header_pattern, text, flags=re.IGNORECASE | re.MULTILINE))
        if not matches:
            # Fallback to splitting by double newlines
            sections = re.split(r'\n\s*\n', text)
            return [section.strip() for section in sections if section.strip()]
        sections = []
        last_idx = 0
        for match in matches:
            start = match.start()
            if start > last_idx:
                prev_section = text[last_idx:start].strip()
                if prev_section:
                    sections.append(prev_section)
            header = match.group(0).strip()
            # Find the end of this section (start of next header or end of text)
            next_idx = match.end()
            next_match = next((m for m in matches if m.start() > start), None)
            end_idx = next_match.start() if next_match else len(text)
            section_content = text[next_idx:end_idx].strip()
            if section_content:
                # Prefix with header for context
                sections.append(f"{header}\n{section_content}")
            last_idx = end_idx
        return [section for section in sections if section.strip()]
    
    def _chunk_section(self, section: str) -> List[str]:
        """Chunk a large section into smaller pieces."""
        # Try to split by sentences first
        sentences = self._split_sentences(section)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)
            
            # If adding this sentence would exceed chunk size, finalize current chunk
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_tokens = 0
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens
        
        # Add remaining sentences as final chunk
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences with Indonesian language considerations."""
        # Indonesian sentence endings
        sentence_endings = r'[.!?]'
        
        # Split by sentence endings, but be careful with abbreviations
        sentences = re.split(f'({sentence_endings})', text)
        
        # Recombine sentences with their endings
        combined_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i]
            if i + 1 < len(sentences):
                ending = sentences[i + 1]
                combined_sentence = (sentence + ending).strip()
                if combined_sentence:
                    combined_sentences.append(combined_sentence)
        
        # Handle case where text doesn't end with punctuation
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            combined_sentences.append(sentences[-1].strip())
        
        # Filter out very short sentences (likely artifacts)
        filtered_sentences = []
        for sentence in combined_sentences:
            if len(sentence.strip()) > 10:  # Minimum sentence length
                filtered_sentences.append(sentence.strip())
        
        return filtered_sentences
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        try:
            return len(self.encoding.encode(text))
        except Exception:
            # Fallback to word count approximation
            return len(text.split()) * 1.3  # Rough approximation
    
    def _apply_overlap(self, chunks: List[str]) -> List[str]:
        """Apply overlap between consecutive chunks."""
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            if i == 0:
                # First chunk - no previous overlap needed
                overlapped_chunks.append(chunk)
            else:
                # Add overlap from previous chunk
                prev_chunk = chunks[i - 1]
                overlap_text = self._get_overlap_text(prev_chunk, self.chunk_overlap)
                
                if overlap_text:
                    overlapped_chunk = overlap_text + " " + chunk
                else:
                    overlapped_chunk = chunk
                
                overlapped_chunks.append(overlapped_chunk)
        
        return overlapped_chunks
    
    def _get_overlap_text(self, text: str, max_overlap_tokens: int) -> str:
        """Get the last part of text for overlap, respecting sentence boundaries."""
        sentences = self._split_sentences(text)
        
        if not sentences:
            return ""
        
        # Start from the end and add sentences until we reach the overlap limit
        overlap_sentences = []
        overlap_tokens = 0
        
        for sentence in reversed(sentences):
            sentence_tokens = self._count_tokens(sentence)
            
            if overlap_tokens + sentence_tokens > max_overlap_tokens:
                break
            
            overlap_sentences.insert(0, sentence)
            overlap_tokens += sentence_tokens
        
        return ' '.join(overlap_sentences)
