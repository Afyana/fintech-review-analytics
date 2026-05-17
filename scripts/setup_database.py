"""
PostgreSQL Database Setup for Banking Reviews
"""

import psycopg2
import pandas as pd
from sqlalchemy import create_engine, text
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DB_CONFIG = {
    'host': 'localhost',
    'database': 'bank_reviews',
    'user': 'Afyana',     
    'password': 'KAIMtraining101'  
}

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_CONFIG['database']}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            logger.info(f"✅ Database '{DB_CONFIG['database']}' created")
        else:
            logger.info(f"Database '{DB_CONFIG['database']}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create database: {e}")
        logger.info("Make sure PostgreSQL is installed and running")
        return False

def create_tables():
    """Create tables schema"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create banks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS banks (
                bank_id SERIAL PRIMARY KEY,
                bank_name VARCHAR(100) NOT NULL UNIQUE,
                app_name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                review_id SERIAL PRIMARY KEY,
                bank_id INTEGER REFERENCES banks(bank_id),
                review_text TEXT NOT NULL,
                rating INTEGER CHECK (rating >= 1 AND rating <= 5),
                review_date DATE,
                sentiment_label VARCHAR(20),
                sentiment_score FLOAT,
                identified_theme VARCHAR(100),
                source VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        logger.info("✅ Tables created successfully")
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        return False

def insert_data():
    """Insert processed data into database"""
    try:
        # Load processed data
        input_file = 'data/processed/reviews_with_sentiment.csv'
        if not os.path.exists(input_file):
            logger.error(f"❌ {input_file} not found. Run sentiment_analysis.py first")
            return False
        
        df = pd.read_csv(input_file)
        logger.info(f"Loaded {len(df)} reviews for insertion")
        
        # Create connection engine
        engine = create_engine(
            f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}/{DB_CONFIG['database']}"
        )
        
        # Insert banks
        banks_df = pd.DataFrame({
            'bank_name': df['bank'].unique(),
            'app_name': df['bank'].unique()
        })
        banks_df.to_sql('banks', engine, if_exists='append', index=False)
        logger.info(f"✅ Inserted {len(banks_df)} banks")
        
        # Get bank_id mapping
        with engine.connect() as conn:
            bank_mapping = pd.read_sql("SELECT bank_id, bank_name FROM banks", conn)
        
        # Map bank names to IDs
        bank_id_map = dict(zip(bank_mapping['bank_name'], bank_mapping['bank_id']))
        df['bank_id'] = df['bank'].map(bank_id_map)
        
        # Prepare reviews for insertion
        reviews_df = df[[
            'bank_id', 'review', 'rating', 'date', 
            'sentiment_label', 'sentiment_score', 'identified_theme', 'source'
        ]].rename(columns={
            'review': 'review_text',
            'date': 'review_date'
        })
        
        # Insert reviews
        reviews_df.to_sql('reviews', engine, if_exists='append', index=False)
        logger.info(f"✅ Inserted {len(reviews_df)} reviews")
        
        # Verification
        verify_data(engine)
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to insert data: {e}")
        return False

def verify_data(engine):
    """Verify data was inserted correctly"""
    print("\n" + "="*50)
    print("DATABASE VERIFICATION")
    print("="*50)
    
    with engine.connect() as conn:
        # Count reviews per bank
        result = conn.execute(text("""
            SELECT b.bank_name, COUNT(r.review_id) as review_count,
                   AVG(r.rating) as avg_rating,
                   COUNT(CASE WHEN r.sentiment_label = 'positive' THEN 1 END) as positive_count
            FROM reviews r
            JOIN banks b ON r.bank_id = b.bank_id
            GROUP BY b.bank_name
        """))
        
        for row in result:
            print(f"\n🏦 {row[0]}")
            print(f"   Reviews: {row[1]}")
            print(f"   Avg Rating: {float(row[2]):.2f}")
            print(f"   Positive Reviews: {row[3]}")

if __name__ == "__main__":
    print("🚀 Setting up PostgreSQL Database...")
    
    if create_database():
        if create_tables():
            insert_data()
            print("\n✅ Database setup complete!")
        else:
            print("\n❌ Table creation failed")
    else:
        print("\n❌ Database creation failed")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure PostgreSQL is installed")
        print("   2. Update DB_CONFIG with your credentials")
        print("   3. Run: sudo service postgresql start (Linux)")
        print("   4. Or start PostgreSQL from Applications (Mac/Windows)")