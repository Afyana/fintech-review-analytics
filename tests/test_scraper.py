"""
Unit tests for data scraping functions
"""

import pytest
import pandas as pd
from pathlib import Path

class TestFileStructure:
    """Test project file structure"""
    
    def test_data_directory_exists(self):
        """Test data directory exists"""
        assert Path('data').exists() or Path('data/raw').exists()
    
    def test_requirements_exists(self):
        """Test requirements.txt exists"""
        assert Path('requirements.txt').exists()
    
    def test_readme_exists(self):
        """Test README.md exists"""
        assert Path('README.md').exists()
    
    def test_gitignore_exists(self):
        """Test .gitignore exists"""
        assert Path('.gitignore').exists()

class TestDataFormat:
    """Test data format requirements"""
    
    def test_csv_columns(self):
        """Test CSV has required columns"""
        try:
            df = pd.read_csv('data/raw/bank_reviews.csv')
            required_columns = ['review', 'rating', 'date', 'bank', 'source']
            for col in required_columns:
                assert col in df.columns, f"Missing column: {col}"
        except FileNotFoundError:
            pytest.skip("Data file not found - run scraper first")
    
    def test_no_empty_reviews(self):
        """Test no empty reviews"""
        try:
            df = pd.read_csv('data/raw/bank_reviews.csv')
            assert not df['review'].isna().all()
        except FileNotFoundError:
            pytest.skip("Data file not found")

if __name__ == "__main__":
    pytest.main(["-v", __file__])