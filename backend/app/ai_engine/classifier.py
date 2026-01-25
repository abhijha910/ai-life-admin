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
        """Classify document type with improved accuracy"""
        try:
            # Check if LLM is available
            llm_available = await llm_client.check_connection()
            
            if not llm_available:
                logger.warning("LLM not available, using keyword fallback")
                return self._fallback_classify(text, file_name)
            
            # Enhanced system prompt
            system_prompt = """You are an expert document classification system. Analyze documents and classify them accurately.

CATEGORIES:
- invoice: Bills requesting payment, with line items and totals
- receipt: Proof of payment, showing items purchased and payment confirmation
- contract: Legal agreements, terms and conditions, signed documents
- letter: Personal or business correspondence, formal letters
- form: Applications, forms to fill out, questionnaires
- report: Analysis reports, summaries, data presentations
- statement: Account statements, financial summaries, bank statements
- bill: Payment requests, utility bills, service bills
- other: Anything that doesn't fit the above categories

Return ONLY a JSON object with:
- "category": one of the categories above
- "confidence": a number between 0.0 and 1.0 indicating your confidence

Be accurate and consider both filename and content."""
            
            # Enhanced user prompt
            user_prompt = f"""Classify this document:

Filename: {file_name or 'unknown'}

Content (first 3000 characters):
{text[:3000]}

Analyze the document type based on both filename and content. Return JSON: {{"category": "...", "confidence": 0.0-1.0}}"""
            
            response = await llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                format="json",
                temperature=0.2  # Lower temperature for more consistent classification
            )
            
            # Parse response with improved error handling
            try:
                # Clean response - remove markdown code blocks if present
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                
                result = json.loads(cleaned_response)
                category = result.get("category", "other").lower().strip()
                confidence = float(result.get("confidence", 0.5))
                
                # Validate category
                if category not in self.CATEGORIES:
                    # Try to find similar category
                    category = self._find_similar_category(category)
                
                # Validate confidence
                confidence = max(0.0, min(1.0, confidence))
                
                logger.info(f"Document classified as '{category}' with confidence {confidence:.2f}")
                
                return {
                    "category": category,
                    "confidence": confidence
                }
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse classification response: {e}")
                logger.debug(f"LLM response was: {response[:500]}")
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
    
    def _find_similar_category(self, category: str) -> str:
        """Find similar category if exact match not found"""
        category_lower = category.lower()
        
        # Common variations
        variations = {
            "invoice": ["bill", "billing", "charge"],
            "receipt": ["payment confirmation", "purchase receipt"],
            "contract": ["agreement", "terms", "legal"],
            "letter": ["correspondence", "mail", "message"],
            "form": ["application", "questionnaire", "survey"],
            "report": ["analysis", "summary", "review"],
            "statement": ["account statement", "financial statement"],
            "bill": ["invoice", "payment due", "charge"]
        }
        
        for standard_category, variants in variations.items():
            if category_lower in variants or any(v in category_lower for v in variants):
                return standard_category
        
        return "other"


# Global classifier instance
document_classifier = DocumentClassifier()
