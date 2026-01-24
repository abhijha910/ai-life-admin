"""Document classifier using LLM"""
from typing import Dict, Any, Optional
from app.ai_engine.llm_client import llm_client
import json
import structlog

logger = structlog.get_logger()


class DocumentClassifier:
    """Classify documents into categories using AI"""
    
    # Document categories
    CATEGORIES = [
        "invoice",
        "receipt",
        "contract",
        "letter",
        "form",
        "report",
        "statement",
        "receipt",
        "bill",
        "other"
    ]
    
    async def classify(self, text: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """Classify document type"""
        try:
            system_prompt = """You are a document classification system. 
            Classify the given document into one of these categories: invoice, receipt, contract, letter, form, report, statement, bill, or other.
            Return only a JSON object with 'category' and 'confidence' (0-1) fields."""
            
            user_prompt = f"""Document filename: {file_name or 'unknown'}
            
Document content (first 2000 characters):
{text[:2000]}

Classify this document. Return JSON: {{"category": "...", "confidence": 0.0-1.0}}"""
            
            response = await llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                format="json"
            )
            
            # Parse response
            try:
                result = json.loads(response)
                category = result.get("category", "other").lower()
                confidence = float(result.get("confidence", 0.5))
                
                # Validate category
                if category not in self.CATEGORIES:
                    category = "other"
                
                return {
                    "category": category,
                    "confidence": confidence
                }
            except json.JSONDecodeError:
                # Fallback classification
                return self._fallback_classify(text, file_name)
                
        except Exception as e:
            logger.error("Document classification error", error=str(e))
            return self._fallback_classify(text, file_name)
    
    def _fallback_classify(self, text: str, file_name: Optional[str] = None) -> Dict[str, Any]:
        """Fallback classification using keyword matching"""
        text_lower = text.lower()
        file_lower = (file_name or "").lower()
        combined = f"{text_lower} {file_lower}"
        
        keywords = {
            "invoice": ["invoice", "bill to", "amount due"],
            "receipt": ["receipt", "thank you for your purchase", "payment received"],
            "contract": ["contract", "agreement", "terms and conditions"],
            "letter": ["dear", "sincerely", "yours truly"],
            "form": ["form", "application", "please fill"],
            "report": ["report", "summary", "analysis"],
            "statement": ["statement", "account statement", "balance"],
            "bill": ["bill", "amount due", "payment due"],
        }
        
        scores = {}
        for category, category_keywords in keywords.items():
            score = sum(1 for keyword in category_keywords if keyword in combined)
            if score > 0:
                scores[category] = score
        
        if scores:
            category = max(scores, key=scores.get)
            confidence = min(scores[category] / 3.0, 0.8)  # Cap at 0.8 for fallback
            return {"category": category, "confidence": confidence}
        
        return {"category": "other", "confidence": 0.5}


# Global classifier instance
document_classifier = DocumentClassifier()
