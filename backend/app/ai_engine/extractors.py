"""Date and amount extractors"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from dateutil import parser
import re
import structlog

logger = structlog.get_logger()


class DateExtractor:
    """Extract and parse dates from text"""
    
    def extract_dates(self, text: str, timezone: str = "UTC") -> List[Dict[str, Any]]:
        """Extract all dates from text"""
        dates = []
        
        # Common date patterns
        patterns = [
            (r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', 'MM/DD/YYYY'),
            (r'\d{4}[/-]\d{1,2}[/-]\d{1,2}', 'YYYY-MM-DD'),
            (r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}', 'DD Month YYYY'),
            (r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}', 'Month DD, YYYY'),
            (r'(today|tomorrow|yesterday|next week|next month)', 'relative'),
            (r'(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)', 'day_of_week'),
        ]
        
        for pattern, format_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_text = match.group()
                parsed_date = self._parse_date(date_text, format_type)
                
                if parsed_date:
                    dates.append({
                        "text": date_text,
                        "parsed": parsed_date.isoformat(),
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.8 if format_type != 'relative' else 0.6
                    })
        
        return dates
    
    def _parse_date(self, date_text: str, format_type: str) -> Optional[datetime]:
        """Parse date text to datetime object"""
        try:
            if format_type == 'relative':
                return self._parse_relative_date(date_text)
            elif format_type == 'day_of_week':
                return self._parse_day_of_week(date_text)
            else:
                return parser.parse(date_text, fuzzy=True)
        except Exception as e:
            logger.warning("Date parsing error", date_text=date_text, error=str(e))
            return None
    
    def _parse_relative_date(self, text: str) -> Optional[datetime]:
        """Parse relative dates like 'today', 'tomorrow'"""
        text_lower = text.lower()
        now = datetime.now()
        
        if 'today' in text_lower:
            return now
        elif 'tomorrow' in text_lower:
            from datetime import timedelta
            return now + timedelta(days=1)
        elif 'yesterday' in text_lower:
            from datetime import timedelta
            return now - timedelta(days=1)
        elif 'next week' in text_lower:
            from datetime import timedelta
            return now + timedelta(weeks=1)
        elif 'next month' in text_lower:
            from datetime import timedelta
            return now + timedelta(days=30)
        
        return None
    
    def _parse_day_of_week(self, text: str) -> Optional[datetime]:
        """Parse day of week to next occurrence"""
        from datetime import timedelta
        days_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        text_lower = text.lower()
        target_day = days_map.get(text_lower)
        
        if target_day is not None:
            now = datetime.now()
            days_ahead = target_day - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return now + timedelta(days=days_ahead)
        
        return None


class AmountExtractor:
    """Extract monetary amounts from text"""
    
    def extract_amounts(self, text: str) -> List[Dict[str, Any]]:
        """Extract all monetary amounts from text"""
        amounts = []
        
        patterns = [
            (r'\$[\d,]+\.?\d*', 'USD'),
            (r'[\d,]+\.?\d*\s*(dollars?|USD)', 'USD'),
            (r'[\d,]+\.?\d*\s*(euros?|EUR)', 'EUR'),
            (r'[\d,]+\.?\d*\s*(pounds?|GBP)', 'GBP'),
            (r'[\d,]+\.?\d*\s*(rupees?|INR)', 'INR'),
            (r'[\d,]+\.?\d*', 'UNKNOWN'),
        ]
        
        for pattern, currency in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_text = match.group()
                numeric_value = self._extract_numeric(amount_text)
                
                if numeric_value:
                    amounts.append({
                        "text": amount_text,
                        "value": numeric_value,
                        "currency": currency,
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.8
                    })
        
        return amounts
    
    def _extract_numeric(self, text: str) -> Optional[float]:
        """Extract numeric value from text"""
        # Remove currency symbols and text
        numeric_text = re.sub(r'[^\d.,]', '', text)
        numeric_text = numeric_text.replace(',', '')
        
        try:
            return float(numeric_text)
        except ValueError:
            return None


# Global extractor instances
date_extractor = DateExtractor()
amount_extractor = AmountExtractor()
