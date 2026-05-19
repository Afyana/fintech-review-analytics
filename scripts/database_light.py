"""
Lightweight PostgreSQL Database Setup
No heavy ML models needed
"""

import pandas as pd
from sqlalchemy import create_engine, text
import os

# Update with your PostgreSQL credentials
DB_CONFIG = {
    'host': 'localhost',
    'user': 'postgres',
    'password': 'postgres',  # Change to your password
    'database': 'bank_reviews_db',
    'port': '5432'
}

def setup_database():
    """Complete database setup without heavy ML"""
    
    print("🚀 Setting up database...")
    
    # Check if data exists
    if not os.path.exists('data/raw/bank_reviews.csv'):
        print("❌ No data found. Run scraper first.")
        return False
    
    # Load data
    df = pd.read_csv('data/raw/bank_reviews.csv')
    print(f"✅ Loaded {len(df)} reviews")
    
    # Add simple sentiment (no heavy models)
    from textblob import TextBlob
    
    def simple_sentiment(text):
        blob = TextBlob(str(text))
        if blob.sentiment.polarity > 0.1:
            return 'positive'
        elif blob.sentiment.polarity < -0.1:
            return 'negative'
        return 'neutral'
    
    df['sentiment'] = df['review'].apply(simple_sentiment)
    df['sentiment_score'] = df['review'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    
    # Create database connection
    try:
        engine = create_engine(
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        )
        
        # Create tables
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS banks (
                    bank_id SERIAL PRIMARY KEY,
                    bank_name VARCHAR(100) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS reviews (
                    review_id SERIAL PRIMARY KEY,
                    bank_id INTEGER REFERENCES banks(bank_id),
                    review_text TEXT,
                    rating INTEGER,
                    review_date DATE,
                    sentiment VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
        
        # Insert banks
        banks = pd.DataFrame({'bank_name': df['bank'].unique()})
        banks.to_sql('banks', engine, if_exists='replace', index=False)
        
        # Get bank IDs
        bank_ids = pd.read_sql("SELECT bank_id, bank_name FROM banks", engine)
        bank_map = dict(zip(bank_ids['bank_name'], bank_ids['bank_id']))
        df['bank_id'] = df['bank'].map(bank_map)
        
        # Insert reviews
        reviews_df = df[['bank_id', 'review', 'rating', 'date', 'sentiment']]
        reviews_df.columns = ['bank_id', 'review_text', 'rating', 'review_date', 'sentiment']
        reviews_df.to_sql('reviews', engine, if_exists='replace', index=False)
        
        print("✅ Database setup complete!")
        
        # Verify
        result = pd.read_sql("""
            SELECT b.bank_name, COUNT(r.review_id) as count, AVG(r.rating) as avg_rating
            FROM reviews r JOIN banks b ON r.bank_id = b.bank_id
            GROUP BY b.bank_name
        """, engine)
        print("\n📊 Verification:")
        print(result.to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("\n💡 If PostgreSQL not installed, skip Task 3 for now")
        return False

if __name__ == "__main__":
    setup_database()