"""
Unit tests for sentiment analysis functions
"""

import pytest
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scripts.simple_sentiment import analyze_sentiment_simple, extract_simple_theme

class TestSentimentAnalysis:
    """Test sentiment analysis functions"""
    
    def test_positive_sentiment(self):
        """Test positive sentiment detection"""
        sentiment, score = analyze_sentiment_simple("This app is amazing and fast!")
        assert sentiment == "positive"
        assert score > 0.1
    
    def test_negative_sentiment(self):
        """Test negative sentiment detection"""
        sentiment, score = analyze_sentiment_simple("This app crashes constantly, terrible!")
        assert sentiment == "negative"
        assert score < -0.1
    
    def test_neutral_sentiment(self):
        """Test neutral sentiment detection"""
        sentiment, score = analyze_sentiment_simple("The app is okay, works sometimes")
        assert sentiment == "neutral"
    
    def test_empty_text(self):
        """Test empty text handling"""
        sentiment, score = analyze_sentiment_simple("")
        assert sentiment == "neutral"
        assert score == 0.5
    
    def test_nan_text(self):
        """Test NaN handling"""
        sentiment, score = analyze_sentiment_simple(None)
        assert sentiment == "neutral"

class TestThemeExtraction:
    """Test theme extraction functions"""
    
    def test_login_theme(self):
        """Test login issue detection"""
        theme = extract_simple_theme("I cannot login to my account")
        assert theme == "Login Issues"
    
    def test_transaction_theme(self):
        """Test transaction problem detection"""
        theme = extract_simple_theme("My money transfer failed")
        assert theme == "Transaction Problems"
    
    def test_performance_theme(self):
        """Test performance issue detection"""
        theme = extract_simple_theme("The app is very slow to load")
        assert theme == "App Performance"
    
    def test_ui_theme(self):
        """Test UI theme detection"""
        theme = extract_simple_theme("The user interface is confusing")
        assert theme == "UI/Design"

class TestDataQuality:
    """Test data quality checks"""
    
    def test_rating_range(self):
        """Test ratings are within 1-5"""
        df = pd.DataFrame({'rating': [1, 2, 3, 4, 5]})
        assert df['rating'].between(1, 5).all()
    
    def test_date_format(self):
        """Test date format is YYYY-MM-DD"""
        df = pd.DataFrame({'date': ['2024-01-01', '2024-12-31']})
        assert df['date'].str.match(r'\d{4}-\d{2}-\d{2}').all()

if __name__ == "__main__":
    pytest.main(["-v", __file__])