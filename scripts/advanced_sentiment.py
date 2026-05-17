"""
Advanced Sentiment Analysis using Transformers
For richer NLP compared to basic TextBlob
"""

import pandas as pd
from transformers import pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class AdvancedNLPAnalyzer:
    def __init__(self):
        """Initialize advanced NLP models"""
        print("Loading DistilBERT for sentiment...")
        self.sentiment_model = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english"
        )
        
        print("Loading zero-shot classifier for themes...")
        self.theme_classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Define candidate themes for Ethiopian banking
        self.candidate_themes = [
            "login and authentication",
            "transaction processing",
            "app speed and performance",
            "user interface design",
            "customer support quality",
            "security and privacy",
            "feature availability",
            "app crashes and bugs"
        ]
    
    def analyze_sentiment_batch(self, texts):
        """Batch sentiment analysis with confidence scores"""
        results = []
        for text in texts:
            try:
                result = self.sentiment_model(text[:512])[0]
                label = result['label'].lower()
                score = result['score']
                
                # Convert to 3-class
                if label == 'positive':
                    sentiment = 'positive'
                elif label == 'negative':
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                
                results.append({
                    'sentiment': sentiment,
                    'confidence': score
                })
            except:
                results.append({'sentiment': 'neutral', 'confidence': 0.5})
        
        return results
    
    def extract_themes_zeroshot(self, texts):
        """Extract themes using zero-shot classification"""
        themes = []
        for text in texts:
            try:
                result = self.theme_classifier(
                    text[:512],
                    self.candidate_themes,
                    multi_label=False
                )
                themes.append(result['labels'][0])
            except:
                themes.append("general feedback")
        
        return themes
    
    def extract_keywords_tfidf(self, df, n_keywords=10):
        """Extract important keywords per bank using TF-IDF"""
        keywords_by_bank = {}
        
        for bank in df['bank'].unique():
            bank_texts = df[df['bank'] == bank]['review'].tolist()
            
            if len(bank_texts) > 10:
                vectorizer = TfidfVectorizer(
                    max_features=50,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
                
                tfidf_matrix = vectorizer.fit_transform(bank_texts)
                feature_names = vectorizer.get_feature_names_out()
                
                # Get average TF-IDF scores
                avg_scores = tfidf_matrix.mean(axis=0).A1
                top_indices = avg_scores.argsort()[-n_keywords:][::-1]
                
                keywords_by_bank[bank] = [feature_names[i] for i in top_indices]
        
        return keywords_by_bank
    
    def cluster_reviews(self, df, n_clusters=5):
        """Cluster similar reviews using TF-IDF"""
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(df['review'].tolist())
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        clusters = kmeans.fit_predict(tfidf_matrix)
        
        return clusters

def main():
    """Run advanced NLP analysis"""
    print("="*60)
    print("ADVANCED NLP ANALYSIS (Richer than TextBlob)")
    print("="*60)
    
    # Load data
    df = pd.read_csv('data/raw/bank_reviews.csv')
    print(f"\nLoaded {len(df)} reviews")
    
    # Initialize analyzer
    analyzer = AdvancedNLPAnalyzer()
    
    # Run advanced sentiment
    print("\n📊 Running advanced sentiment analysis...")
    sentiment_results = analyzer.analyze_sentiment_batch(df['review'].tolist()[:100])  # Limit for speed
    
    # Extract keywords per bank
    print("\n🔑 Extracting important keywords per bank...")
    keywords = analyzer.extract_keywords_tfidf(df)
    
    print("\n📈 KEYWORD EXTRACTION RESULTS:")
    print("="*60)
    for bank, words in keywords.items():
        print(f"\n🏦 {bank}:")
        print(f"   Top keywords: {', '.join(words[:5])}")
    
    print("\n💡 This advanced NLP provides richer analysis than basic TextBlob")
    print("   - Transformer-based sentiment (DistilBERT)")
    print("   - Zero-shot theme classification")
    print("   - TF-IDF keyword extraction")
    print("   - Review clustering")

if __name__ == "__main__":
    main()