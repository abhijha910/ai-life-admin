"""NLP extractor using spaCy"""
import spacy
from typing import Dict, List, Any, Optional
from datetime import datetime
import re
import structlog

logger = structlog.get_logger()

# Lazy loading - don't load model at import time
_nlp_model = None
_nlp_model_loaded = False


def _load_spacy_model():
    """Load spaCy model lazily (only when needed)"""
    global _nlp_model, _nlp_model_loaded
    if not _nlp_model_loaded:
        try:
            _nlp_model = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded successfully")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            _nlp_model = None
        _nlp_model_loaded = True
    return _nlp_model


class NLPExtractor:
    """Extract entities and information from text using NLP"""
    
    def __init__(self):
        # Don't load model in __init__ - load lazily when first used
        self._nlp = None
    
    @property
    def nlp(self):
        """Lazy property to load spaCy model only when accessed"""
        if self._nlp is None:
            self._nlp = _load_spacy_model()
        return self._nlp
    
    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        
        entities = {
            "people": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "amounts": [],
        }
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["people"].append(ent.text)
            elif ent.label_ == "ORG":
                entities["organizations"].append(ent.text)
            elif ent.label_ == "GPE" or ent.label_ == "LOC":
                entities["locations"].append(ent.text)
            elif ent.label_ == "DATE":
                entities["dates"].append(ent.text)
        
        # Extract amounts
        amounts = self._extract_amounts(text)
        entities["amounts"] = amounts
        
        return entities
    
    def extract_dates(self, text: str) -> List[Dict[str, Any]]:
        """Extract dates from text"""
        dates = []
        
        # Use spaCy for date extraction
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "DATE":
                    dates.append({
                        "text": ent.text,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "confidence": 0.8
                    })
        
        # Also use regex for common date patterns
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
            r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}',
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}',
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                dates.append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.7
                })
        
        return dates
    
    def extract_amounts(self, text: str) -> List[Dict[str, Any]]:
        """Extract monetary amounts from text"""
        amounts = []
        
        # Pattern for currency amounts
        patterns = [
            r'\$[\d,]+\.?\d*',
            r'[\d,]+\.?\d*\s*(dollars?|USD|EUR|GBP|INR)',
            r'(dollars?|USD|EUR|GBP|INR)\s*[\d,]+\.?\d*',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amounts.append({
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.8
                })
        
        return amounts
    
    def extract_action_items(self, text: str) -> List[str]:
        """Extract potential action items from text"""
        action_items = []
        
        # Look for imperative verbs and action phrases
        if self.nlp:
            doc = self.nlp(text)
            sentences = [sent.text for sent in doc.sents]
            
            action_keywords = [
                "please", "need to", "should", "must", "required",
                "action", "task", "todo", "reminder", "follow up"
            ]
            
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in action_keywords):
                    # Check if sentence starts with imperative verb
                    sent_doc = self.nlp(sentence)
                    if sent_doc and sent_doc[0].pos_ == "VERB":
                        action_items.append(sentence.strip())
        
        return action_items
    
    def _extract_amounts(self, text: str) -> List[Dict[str, Any]]:
        """Internal method to extract amounts"""
        return self.extract_amounts(text)


# Global NLP extractor instance
nlp_extractor = NLPExtractor()
