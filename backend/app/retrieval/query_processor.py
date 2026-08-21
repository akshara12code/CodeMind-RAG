"""
Query processing: understand and expand user queries
"""

import logging
import re
from typing import List, Dict, Tuple, Optional
from enum import Enum

from app.core.models import QueryType, QueryAnalysis

logger = logging.getLogger(__name__)


class QueryClassifier:
    """Classify query type"""
    
    # Keywords for each query type
    KEYWORDS = {
        QueryType.CODE_SEARCH: [
            "where", "find", "located", "location", "search",
            "look for", "implemented", "defined", "source"
        ],
        QueryType.ARCHITECTURE: [
            "how", "interact", "relationship", "flow", "structure",
            "communication", "integration", "connect", "connected"
        ],
        QueryType.IMPLEMENTATION: [
            "explain", "how does", "what", "implementation",
            "mechanism", "process", "works", "do", "did", "describe"
        ],
        QueryType.DEBUGGING: [
            "why", "debug", "error", "problem", "issue", "fail",
            "null", "exception", "crash", "break"
        ],
        QueryType.DEPENDENCY: [
            "depend", "require", "import", "use", "call", "reference",
            "who", "which file", "calls", "uses"
        ],
        QueryType.MODIFICATION: [
            "modify", "change", "add", "implement", "feature",
            "where should", "implement", "extend"
        ]
    }
    
    @classmethod
    def classify(cls, query: str) -> Tuple[QueryType, float]:
        """
        Classify query type
        Returns: (query_type, confidence)
        """
        query_lower = query.lower()
        scores = {}
        
        for query_type, keywords in cls.KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in query_lower)
            scores[query_type] = score
        
        if max(scores.values()) == 0:
            # Default to code search
            return QueryType.CODE_SEARCH, 0.3
        
        best_type = max(scores, key=scores.get)
        confidence = scores[best_type] / max(len(v) for v in cls.KEYWORDS.values())
        
        return best_type, min(confidence, 1.0)


class QueryProcessor:
    """
    Process and enhance user queries
    """
    
    # Common abbreviations and expansions
    ABBREVIATIONS = {
        "jwt": "java web token",
        "auth": "authentication authorization",
        "db": "database",
        "api": "application programming interface",
        "http": "hypertext transfer protocol",
        "rest": "representational state transfer",
        "crud": "create read update delete",
        "orm": "object relational mapping",
        "sql": "structured query language",
        "xml": "extensible markup language",
        "json": "javascript object notation",
        "ui": "user interface",
        "ux": "user experience",
        "cpu": "central processing unit",
        "ram": "random access memory",
        "io": "input output",
        "os": "operating system",
        "git": "version control system",
        "ci": "continuous integration",
        "cd": "continuous deployment",
    }
    
    # Synonyms for semantic expansion
    SYNONYMS = {
        "login": ["authenticate", "signin", "sign in", "user auth"],
        "logout": ["signout", "sign out", "disconnect"],
        "password": ["credentials", "secret", "passphrase"],
        "token": ["bearer", "jwt", "session"],
        "user": ["account", "profile", "person"],
        "database": ["db", "storage", "persistence"],
        "file": ["document", "resource", "content"],
        "error": ["exception", "failure", "problem", "bug"],
        "generate": ["create", "produce", "build", "make"],
        "retrieve": ["fetch", "get", "obtain", "load"],
        "store": ["save", "persist", "write"],
        "delete": ["remove", "destroy", "erase"],
        "modify": ["change", "update", "edit", "alter"],
    }
    
    def __init__(self):
        self.classifier = QueryClassifier()
    
    async def process(self, query: str) -> QueryAnalysis:
        """
        Process a query and return analysis
        """
        # Normalize
        normalized = self._normalize(query)
        
        # Extract keywords and entities
        keywords = self._extract_keywords(normalized)
        entities = self._extract_entities(normalized)
        
        # Classify
        query_type, confidence = self.classifier.classify(normalized)
        
        # Expand (generate subqueries)
        subqueries = self._expand_query(normalized, query_type)
        
        analysis = QueryAnalysis(
            original_query=query,
            processed_query=normalized,
            query_type=query_type,
            keywords=keywords,
            entities=entities,
            subqueries=subqueries
        )
        
        logger.info(f"Query classified as {query_type} (confidence: {confidence:.2f})")
        
        return analysis
    
    def _normalize(self, query: str) -> str:
        """Normalize query text"""
        # Lowercase
        query = query.lower().strip()
        
        # Remove extra whitespace
        query = " ".join(query.split())
        
        # Expand abbreviations
        for abbr, expansion in self.ABBREVIATIONS.items():
            query = re.sub(r'\b' + abbr + r'\b', expansion, query)
        
        # Remove punctuation except meaningful ones
        query = re.sub(r'[?!]', '', query)
        
        return query
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract important keywords from query
        """
        # Split into tokens
        tokens = query.split()
        
        # Filter stopwords
        stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "by", "is", "are", "was",
            "be", "been", "being", "have", "has", "had", "do",
            "does", "did", "will", "would", "could", "should",
            "may", "might", "must", "can", "this", "that", "it"
        }
        
        keywords = [
            token for token in tokens
            if token not in stopwords and len(token) > 2
        ]
        
        return keywords
    
    def _extract_entities(self, query: str) -> List[str]:
        """
        Extract named entities (likely code symbols, classes, functions)
        Heuristic: capitalized words or common symbol names
        """
        entities = []
        
        # Pattern: CamelCase or PascalCase (likely class/function names)
        camel_pattern = r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b'
        entities.extend(re.findall(camel_pattern, query))
        
        # Pattern: snake_case (likely function/variable names)
        snake_pattern = r'\b[a-z]+(?:_[a-z]+)+\b'
        entities.extend(re.findall(snake_pattern, query))
        
        # Remove duplicates while preserving order
        seen = set()
        unique = []
        for e in entities:
            if e not in seen:
                unique.append(e)
                seen.add(e)
        
        return unique
    
    def _expand_query(
        self,
        query: str,
        query_type: QueryType
    ) -> List[str]:
        """
        Generate expanded subqueries for multi-hop retrieval
        """
        subqueries = []
        
        if query_type == QueryType.ARCHITECTURE:
            # For architecture questions, decompose into components
            # "How do A and B interact?"
            # Subqueries:
            # - A implementation
            # - B implementation
            # - A B integration/communication
            
            # Extract nouns (likely components)
            words = query.split()
            for word in words:
                if len(word) > 3 and not any(sw in word for sw in ["how", "does", "and"]):
                    subqueries.append(f"{word} implementation")
                    subqueries.append(f"{word} definition")
            
            if "and" in query:
                subqueries.append("integration between components")
        
        elif query_type == QueryType.IMPLEMENTATION:
            # For implementation questions
            # "Explain how X works"
            # Subqueries:
            # - X entry point
            # - X core logic
            # - X dependencies
            
            keywords = self._extract_keywords(query)
            if keywords:
                main_term = keywords[0]
                subqueries.extend([
                    f"{main_term} implementation",
                    f"{main_term} entry point",
                    f"{main_term} main logic",
                    f"{main_term} dependencies"
                ])
        
        elif query_type == QueryType.DEBUGGING:
            # For debugging questions
            # "Why might X return null?"
            # Subqueries:
            # - X return value handling
            # - null checks
            # - error conditions
            
            keywords = self._extract_keywords(query)
            if keywords:
                main_term = keywords[0]
                subqueries.extend([
                    f"{main_term} return handling",
                    f"{main_term} null check",
                    f"{main_term} error condition",
                    f"{main_term} validation"
                ])
        
        elif query_type == QueryType.DEPENDENCY:
            # For dependency questions
            # "Which files use X?"
            # Subqueries:
            # - X definition
            # - X references
            # - X import statements
            
            keywords = self._extract_keywords(query)
            if keywords:
                main_term = keywords[0]
                subqueries.extend([
                    f"{main_term} definition",
                    f"{main_term} imports",
                    f"uses of {main_term}",
                    f"references to {main_term}"
                ])
        
        # Add synonym expansion
        for keyword in self._extract_keywords(query):
            if keyword in self.SYNONYMS:
                for synonym in self.SYNONYMS[keyword]:
                    subqueries.append(
                        query.replace(keyword, synonym)
                    )
        
        # Remove duplicates
        subqueries = list(set(subqueries))
        
        # Limit to top subqueries
        return subqueries[:5]


class ConversationContextManager:
    """
    Manage conversation context for follow-up questions
    """
    
    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = {}
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        entities: Optional[List[str]] = None
    ):
        """Add message to conversation"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = []
        
        self.conversations[conversation_id].append({
            "role": role,
            "content": content,
            "entities": entities or []
        })
    
    def get_context(
        self,
        conversation_id: str,
        window_size: int = 3
    ) -> str:
        """
        Get recent conversation context
        """
        if conversation_id not in self.conversations:
            return ""
        
        messages = self.conversations[conversation_id][-window_size:]
        context_parts = []
        
        for msg in messages:
            context_parts.append(f"{msg['role']}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def get_previous_entities(self, conversation_id: str) -> List[str]:
        """Get entities mentioned in conversation"""
        if conversation_id not in self.conversations:
            return []
        
        all_entities = []
        for msg in self.conversations[conversation_id]:
            all_entities.extend(msg.get("entities", []))
        
        return list(set(all_entities))
    
    def resolve_pronouns(
        self,
        current_query: str,
        conversation_id: str
    ) -> str:
        """
        Resolve pronouns (that, it, etc.) to previous entities
        """
        entities = self.get_previous_entities(conversation_id)
        
        if not entities:
            return current_query
        
        # Simple pronoun resolution
        pronouns = {
            "that": entities[-1] if entities else "that",
            "it": entities[-1] if entities else "it",
            "this": entities[-1] if entities else "this",
        }
        
        resolved = current_query
        for pronoun, replacement in pronouns.items():
            resolved = re.sub(
                r'\b' + pronoun + r'\b',
                replacement,
                resolved,
                flags=re.IGNORECASE
            )
        
        return resolved
