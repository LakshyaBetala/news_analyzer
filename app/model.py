"""
News Credibility Analyzer - Model Logic
Keyword-based credibility scoring with extensible architecture.
"""

import re
from typing import Dict, List, Tuple


class NewsCredibilityAnalyzer:
    """
    Analyzes news articles for credibility using keyword-based heuristics.
    
    Designed to be easily extended with transformer models.
    """
    
    def __init__(self):
        """Initialize credibility analyzer with keyword patterns."""
        # High credibility indicators
        self.credible_keywords = [
            'verified', 'fact-checked', 'peer-reviewed', 'official',
            'confirmed', 'evidence', 'research', 'study', 'data',
            'expert', 'authoritative', 'transparent', 'cited',
            'journal', 'published', 'analysis', 'report', 'findings',
            'investigation', 'according to', 'sources', 'statement'
        ]
        
        # Low credibility indicators
        self.suspicious_keywords = [
            'shocking', 'you won\'t believe', 'secret',
            'doctors hate', 'one weird trick', 'miracle cure',
            'conspiracy', 'cover-up', 'they don\'t want you to know',
            'act now', 'limited time', 'clickbait', 'viral',
            'amazing discovery', 'guaranteed', 'instant'
        ]
        
        # Emotional manipulation patterns (check original text, not lowercase)
        self.emotional_patterns = [
            r'!{2,}',  # Multiple exclamation marks
            r'\b[A-Z]{5,}\b',  # ALL CAPS words (5+ letters)
        ]
        
        # Source credibility (simple mapping - can be extended)
        self.credible_sources = [
            'reuters', 'ap news', 'associated press', 'bbc',
            'the guardian', 'new york times', 'washington post',
            'npr', 'pbs', 'propublica'
        ]
        
        self.suspicious_sources = [
            'unknown', 'anonymous', 'unverified'
        ]
    
    def analyze(self, title: str, content: str, source: str = '') -> Dict:
        """
        Analyze news article for credibility.
        
        Args:
            title: Article title
            content: Article content
            source: Source name (optional)
        
        Returns:
            Dictionary with credibility score, risk factors, and recommendations
        """
        # Combine text for analysis (keep original for emotional patterns)
        text_original = f"{title} {content}"
        text = text_original.lower()
        
        # Calculate scores
        credible_score = self._count_keywords(text, self.credible_keywords)
        suspicious_score = self._count_keywords(text, self.suspicious_keywords)
        emotional_score = self._detect_emotional_manipulation(text_original)
        source_score = self._evaluate_source(source)
        
        # Calculate text length factor (longer articles tend to be more credible)
        text_length_factor = min(1.0, len(content.split()) / 100)  # Normalize to 100 words
        
        # Weighted scoring with improved algorithm
        base_score = 50.0  # Neutral starting point
        
        # Positive adjustments (more generous)
        base_score += credible_score * 6  # Increased from 5
        base_score += source_score * 15  # Increased from 10
        base_score += text_length_factor * 10  # Reward longer articles
        
        # Negative adjustments (less harsh)
        base_score -= suspicious_score * 6  # Reduced from 8
        base_score -= emotional_score * 8  # Reduced from 10
        
        # Ensure minimum score for normal articles (unless very suspicious)
        if suspicious_score == 0 and emotional_score == 0:
            base_score = max(base_score, 40.0)  # Minimum 40 for clean articles
        
        # Clamp to 0-100
        credibility_score = max(0.0, min(100.0, base_score))
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(
            text, source, suspicious_score, emotional_score
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            credibility_score, risk_factors, source
        )
        
        return {
            'credibility_score': round(credibility_score, 2),
            'risk_factors': risk_factors,
            'recommendations': recommendations,
            'analysis_details': {
                'credible_indicators': credible_score,
                'suspicious_indicators': suspicious_score,
                'emotional_manipulation': emotional_score,
                'source_credibility': source_score
            }
        }
    
    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        """Count occurrences of keywords in text."""
        count = 0
        for keyword in keywords:
            count += len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
        return count
    
    def _detect_emotional_manipulation(self, text: str) -> int:
        """Detect emotional manipulation patterns in original case text."""
        score = 0
        for pattern in self.emotional_patterns:
            matches = re.findall(pattern, text)
            score += len(matches)
        # Cap the emotional score to prevent over-penalization
        return min(score, 5)
    
    def _evaluate_source(self, source: str) -> float:
        """Evaluate source credibility."""
        if not source:
            return 0.0
        
        source_lower = source.lower().strip()
        
        # Check for credible sources
        for credible in self.credible_sources:
            if credible in source_lower:
                return 1.0
        
        # Check for suspicious sources
        for suspicious in self.suspicious_sources:
            if suspicious in source_lower:
                return -1.0
        
        # Known news sources get slight positive boost
        known_sources = ['times', 'news', 'post', 'tribune', 'herald', 'chronicle', 'gazette']
        if any(known in source_lower for known in known_sources):
            return 0.3  # Small positive boost for known news sources
        
        return 0.0
    
    def _identify_risk_factors(
        self, text: str, source: str, suspicious_score: int, emotional_score: int
    ) -> List[str]:
        """Identify specific risk factors."""
        risks = []
        
        if suspicious_score > 2:
            risks.append('Multiple suspicious keywords detected')
        elif suspicious_score > 0:
            risks.append('Some suspicious keywords detected')
        
        if emotional_score > 2:
            risks.append('Emotional manipulation patterns detected')
        elif emotional_score > 0:
            risks.append('Some emotional language detected')
        
        if source and source.lower() in self.suspicious_sources:
            risks.append('Unverified or suspicious source')
        elif not source:
            risks.append('Source information not provided')
        
        if 'conspiracy' in text:
            risks.append('Conspiracy-related content')
        
        if 'click' in text and 'bait' in text:
            risks.append('Potential clickbait')
        
        if not risks:
            risks.append('No significant risk factors identified')
        
        return risks
    
    def _generate_recommendations(
        self, score: float, risk_factors: List[str], source: str
    ) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if score < 30:
            recommendations.append('⚠️ Low credibility - Verify from multiple sources')
            recommendations.append('Check fact-checking websites')
        elif score < 60:
            recommendations.append('⚠️ Moderate credibility - Exercise caution')
            recommendations.append('Cross-reference with established news sources')
        else:
            recommendations.append('✓ Relatively high credibility')
            recommendations.append('Still recommended to verify with multiple sources')
        
        if not source:
            recommendations.append('Source information missing - verify article origin')
        
        if 'suspicious keywords' in str(risk_factors):
            recommendations.append('Review article for sensationalist language')
        
        return recommendations

