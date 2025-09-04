import spacy
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
import re
from collections import Counter

class NLPTools:
    def __init__(self):
        try:
            # Load spaCy model (install with: python -m spacy download en_core_web_sm)
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Fallback if spaCy isn't available
            self.nlp = None
            print("Warning: spaCy model not available. Some NLP features will be limited.")
    
    def named_entity_recognition(self, text):
        """Extract named entities from text"""
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            })
        
        return entities
    
    def summarize_text(self, text, sentences_count=3, method='lsa'):
        """Summarize text using extractive summarization"""
        try:
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            
            if method == 'lsa':
                summarizer = LsaSummarizer()
            else:  # textrank
                summarizer = TextRankSummarizer()
            
            summary_sentences = summarizer(parser.document, sentences_count)
            summary = ' '.join(str(sentence) for sentence in summary_sentences)
            return summary
        except Exception as e:
            print(f"Summarization error: {e}")
            # Fallback: return first few sentences
            sentences = text.split('.')
            return '.'.join(sentences[:sentences_count]) + '.'
    
    def extract_keywords(self, text, max_keywords=10):
        """Extract important keywords from text"""
        if not self.nlp:
            # Simple regex-based fallback
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            return [word for word, count in Counter(words).most_common(max_keywords)]
        
        doc = self.nlp(text)
        
        # Filter for nouns, proper nouns, and adjectives
        keywords = []
        for token in doc:
            if (not token.is_stop and not token.is_punct and 
                token.pos_ in ['NOUN', 'PROPN', 'ADJ'] and len(token.text) > 2):
                keywords.append(token.lemma_.lower())
        
        # Count and rank keywords
        keyword_counts = Counter(keywords)
        return [keyword for keyword, count in keyword_counts.most_common(max_keywords)]
    
    def detect_language(self, text):
        """Simple language detection based on common words"""
        # Common words in different languages
        language_indicators = {
            'english': ['the', 'and', 'is', 'to', 'of'],
            'spanish': ['el', 'la', 'de', 'que', 'y'],
            'french': ['le', 'la', 'de', 'et', 'que'],
            'german': ['der', 'die', 'das', 'und', 'ist']
        }
        
        text_lower = text.lower()
        scores = {}
        
        for lang, words in language_indicators.items():
            scores[lang] = sum(1 for word in words if word in text_lower)
        
        # Return language with highest score
        return max(scores.items(), key=lambda x: x[1])[0] if scores else 'unknown'
    
    def calculate_readability(self, text):
        """Calculate simple readability score (Flesch-Kincaid approximation)"""
        sentences = text.split('.')
        words = text.split()
        
        if not sentences or not words:
            return 0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simple readability formula (lower = easier to read)
        readability_score = (avg_sentence_length * 0.39) + (avg_word_length * 11.8) - 15.59
        return max(0, min(100, readability_score))

# Create global NLP tools instance
nlp_tools = NLPTools()