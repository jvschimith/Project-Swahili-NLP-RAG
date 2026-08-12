"""
Application Layer - URL News Analyzer

Fetch and analyze news from URLs.
"""
import ipaddress
import socket
from urllib.parse import urljoin, urlsplit
from typing import Dict, Optional

import requests
from bs4 import BeautifulSoup
from loguru import logger

from src.application.services.text_processor import SwahiliTextProcessor
from src.domain.value_objects import SentimentScore
from src.domain.entities import NewsArticle


class URLNewsAnalyzer:
    """
    Analyze news articles from URLs.
    
    Features:
    - Fetch content from URL
    - Extract text from HTML
    - Analyze sentiment
    - Extract key terms
    - Identify entities
    
    Examples:
        >>> analyzer = URLNewsAnalyzer()
        >>> result = analyzer.analyze_url("https://example.com/news")
    """
    
    MAX_REDIRECTS = 5
    MAX_RESPONSE_BYTES = 5 * 1024 * 1024
    ALLOWED_CONTENT_TYPES = ("text/html", "application/xhtml+xml")

    def __init__(self):
        """Initialize analyzer with text processor."""
        self.processor = SwahiliTextProcessor()
        self.headers = {
            "User-Agent": "SwahiliLinguisticIntelligence/2.0 (+local research toolkit)"
        }

    @staticmethod
    def validate_public_url(url: str) -> str:
        """Validate an HTTP(S) URL and reject non-public network targets.

        Hostnames are resolved before fetching so loopback, private,
        link-local, multicast, reserved, and unspecified destinations are
        refused. Redirect targets are validated separately by ``fetch_url``.
        """
        parsed = urlsplit(url)
        if parsed.scheme.lower() not in {"http", "https"}:
            raise ValueError("Only http and https URLs are supported")
        if not parsed.hostname:
            raise ValueError("URL must include a hostname")
        if parsed.username or parsed.password:
            raise ValueError("Credentials in URLs are not supported")

        hostname = parsed.hostname.rstrip(".").lower()
        if hostname == "localhost" or hostname.endswith(".localhost") or hostname.endswith(".local"):
            raise ValueError("Local network hostnames are not allowed")

        try:
            addresses = {item[4][0] for item in socket.getaddrinfo(hostname, parsed.port)}
        except socket.gaierror as exc:
            raise ValueError("Hostname could not be resolved") from exc
        if not addresses:
            raise ValueError("Hostname did not resolve to an address")

        for address in addresses:
            ip = ipaddress.ip_address(address)
            if not ip.is_global:
                raise ValueError("URL resolves to a non-public network address")
        return url
    
    def fetch_url(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch HTML content from URL.
        
        Args:
            url: URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            HTML content or None if failed
        """
        try:
            current_url = self.validate_public_url(url)
            for redirect_count in range(self.MAX_REDIRECTS + 1):
                response = requests.get(
                    current_url,
                    headers=self.headers,
                    timeout=(min(timeout, 5), timeout),
                    allow_redirects=False,
                )
                if response.status_code in {301, 302, 303, 307, 308}:
                    if redirect_count >= self.MAX_REDIRECTS:
                        raise ValueError("Too many redirects")
                    location = response.headers.get("Location")
                    if not location:
                        raise ValueError("Redirect response has no Location header")
                    current_url = self.validate_public_url(urljoin(current_url, location))
                    continue

                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "").lower()
                if not any(kind in content_type for kind in self.ALLOWED_CONTENT_TYPES):
                    raise ValueError("URL did not return HTML content")
                content = response.content
                if len(content) > self.MAX_RESPONSE_BYTES:
                    raise ValueError("HTML response exceeds the size limit")
                response.encoding = response.encoding or response.apparent_encoding or "utf-8"
                return response.text
            return None
        except (requests.RequestException, ValueError) as e:
            logger.error(f"Failed to fetch URL {url}: {e}")
            return None
    
    def extract_text(self, html: str) -> str:
        """
        Extract main text content from HTML.
        
        Args:
            html: HTML content
            
        Returns:
            Extracted text
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header']):
                script.decompose()
            
            # Get text from paragraphs
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text() for p in paragraphs])
            
            # Fallback: get all text
            if not text.strip():
                text = soup.get_text()
            
            # Clean text
            lines = (line.strip() for line in text.splitlines())
            text = ' '.join(line for line in lines if line)
            
            return text
        except Exception as e:
            logger.error(f"Failed to extract text: {e}")
            return ""
    
    def analyze_url(self, url: str) -> Dict:
        """
        Analyze news article from URL.
        
        Args:
            url: News article URL
            
        Returns:
            Analysis results dictionary
        """
        logger.info(f"Analyzing URL: {url}")
        
        # Fetch content
        html = self.fetch_url(url)
        if not html:
            return {
                "success": False,
                "error": "Failed to fetch URL"
            }
        
        # Extract text
        text = self.extract_text(html)
        if not text or len(text) < 50:
            return {
                "success": False,
                "error": "Could not extract sufficient text from URL"
            }
        
        # Analyze text
        analysis = self.analyze_text(text)
        analysis["url"] = url
        analysis["success"] = True
        
        return analysis
    
    def analyze_text(self, text: str) -> Dict:
        """
        Perform comprehensive text analysis.
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis results
        """
        # Basic statistics
        word_count = self.processor.count_words(text)
        sentences = self.processor.extract_sentences(text)
        
        # Tokenization
        tokens = self.processor.tokenize(text)
        filtered_tokens = self.processor.remove_stopwords(tokens)
        
        # Word frequency
        word_freq = self.processor.get_word_frequency(text)
        
        # Top keywords (excluding stopwords)
        top_keywords = sorted(
            [(word, count) for word, count in word_freq.items() 
             if word in filtered_tokens],
            key=lambda x: x[1],
            reverse=True
        )[:20]
        
        # Transparent lexicon-based sentiment baseline.
        sentiment = self._analyze_sentiment(text, word_freq)
        
        # Language statistics
        unique_words = len(set(filtered_tokens))
        avg_word_length = sum(len(word) for word in tokens) / len(tokens) if tokens else 0
        
        return {
            "text_preview": text[:300] + "..." if len(text) > 300 else text,
            "full_text": text,
            "word_count": word_count,
            "sentence_count": len(sentences),
            "unique_words": unique_words,
            "vocabulary_richness": round(unique_words / word_count, 2) if word_count > 0 else 0,
            "avg_word_length": round(avg_word_length, 2),
            "top_keywords": [{"word": word, "count": count} for word, count in top_keywords[:10]],
            "sentiment": sentiment,
            "language_stats": {
                "total_tokens": len(tokens),
                "filtered_tokens": len(filtered_tokens),
                "stopwords_removed": len(tokens) - len(filtered_tokens)
            }
        }
    
    def _analyze_sentiment(self, text: str, word_freq: Dict) -> Dict:
        """
        Simple sentiment analysis based on keyword matching.
        
        Args:
            text: Text to analyze
            word_freq: Word frequency dictionary
            
        Returns:
            Sentiment analysis result
        """
        # Small, auditable sentiment lexicon. Context-dependent topic words
        # (for example ``uchumi`` / economy) must not carry sentiment merely
        # because they frequently occur in negative-news examples.
        positive_words = {
            'furaha', 'nzuri', 'vizuri', 'mzuri', 'safi', 'bora', 'pongezi',
            'fanaka', 'stahiki', 'amani', 'upendo', 'faida', 'afya',
            'ushindi', 'mafanikio', 'maendeleo', 'ustawi'
        }
        
        negative_words = {
            'mbaya', 'vibaya', 'hasara', 'hatari', 'adui', 'vita', 'mauaji',
            'uhalifu', 'mgogoro', 'matatizo', 'kasoro', 'ugonjwa',
            'kifo', 'msiba', 'huzuni', 'dhiki'
        }
        
        # Count sentiment words
        positive_count = sum(word_freq.get(word, 0) for word in positive_words)
        negative_count = sum(word_freq.get(word, 0) for word in negative_words)
        total_sentiment = positive_count + negative_count
        
        # Calculate polarity
        if total_sentiment == 0:
            polarity = 0.0
            label = "neutral"
            confidence = 0.5
        else:
            polarity = (positive_count - negative_count) / total_sentiment
            confidence = min(total_sentiment / 10, 1.0)  # Simple confidence metric
            
            if polarity > 0.2:
                label = "positive"
            elif polarity < -0.2:
                label = "negative"
            else:
                label = "neutral"
        
        return {
            "polarity": round(polarity, 2),
            "confidence": round(confidence, 2),
            "label": label,
            "positive_words_found": positive_count,
            "negative_words_found": negative_count
        }
    
    def batch_analyze_urls(self, urls: list) -> list:
        """
        Analyze multiple URLs.
        
        Args:
            urls: List of URLs to analyze
            
        Returns:
            List of analysis results
        """
        results = []
        for url in urls:
            result = self.analyze_url(url)
            results.append(result)
        return results


# Usage example
if __name__ == "__main__":
    analyzer = URLNewsAnalyzer()
    
    # Test with a URL
    test_url = "https://www.bbc.com/swahili"
    result = analyzer.analyze_url(test_url)
    
    if result.get("success"):
        print(f"✓ Successfully analyzed: {test_url}")
        print(f"  Word count: {result['word_count']}")
        print(f"  Sentiment: {result['sentiment']['label']}")
        print(f"  Top keywords: {[kw['word'] for kw in result['top_keywords'][:5]]}")
    else:
        print(f"✗ Failed: {result.get('error')}")
