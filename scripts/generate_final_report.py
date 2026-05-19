"""
Generate final report visualizations for Task 4
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# Create figures directory
os.makedirs('figures', exist_ok=True)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_data():
    """Load processed review data"""
    try:
        df = pd.read_csv('data/processed/reviews_analyzed.csv')
        print(f"Loaded {len(df)} reviews")
        return df
    except:
        df = pd.read_csv('data/raw/bank_reviews.csv')
        # Add sentiment if missing
        from textblob import TextBlob
        def get_sentiment(text):
            blob = TextBlob(str(text))
            if blob.sentiment.polarity > 0.1:
                return 'positive'
            elif blob.sentiment.polarity < -0.1:
                return 'negative'
            return 'neutral'
        df['sentiment'] = df['review'].apply(get_sentiment)
        print(f"Loaded {len(df)} reviews (sentiment added)")
        return df

def create_visualization_1_sentiment_distribution(df):
    """Figure 1: Sentiment distribution by bank"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sentiment_by_bank = pd.crosstab(df['bank'], df['sentiment'], normalize='index') * 100
    colors = {'positive': '#2ecc71', 'neutral': '#95a5a6', 'negative': '#e74c3c'}
    
    sentiment_by_bank[['negative', 'neutral', 'positive']].plot(
        kind='bar', 
        stacked=True, 
        ax=ax,
        color=[colors['negative'], colors['neutral'], colors['positive']],
        edgecolor='black',
        linewidth=0.5
    )
    
    ax.set_title('Figure 1: Sentiment Distribution by Bank', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Bank', fontsize=12)
    ax.set_ylabel('Percentage (%)', fontsize=12)
    ax.legend(title='Sentiment', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.tick_params(axis='x', rotation=0)
    
    # Add value labels
    for c in ax.containers:
        ax.bar_label(c, fmt='%.1f%%', label_type='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('figures/figure1_sentiment_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 1 created: sentiment_distribution.png")

def create_visualization_2_rating_distribution(df):
    """Figure 2: Rating distribution histogram"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    banks = df['bank'].unique()
    colors_map = {'CBE': '#3498db', 'BOA': '#e74c3c', 'Dashen': '#2ecc71'}
    
    for bank in banks:
        bank_df = df[df['bank'] == bank]
        ax.hist(bank_df['rating'], alpha=0.5, label=bank, bins=5, range=(0.5, 5.5), 
                edgecolor='black', color=colors_map.get(bank, '#95a5a6'))
    
    ax.set_title('Figure 2: Rating Distribution by Bank', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Rating (Stars)', fontsize=12)
    ax.set_ylabel('Number of Reviews', fontsize=12)
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('figures/figure2_rating_distribution.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 2 created: rating_distribution.png")

def create_visualization_3_top_themes(df):
    """Figure 3: Top themes across all banks"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Extract themes or use categories
    if 'theme' in df.columns:
        theme_counts = df['theme'].value_counts().head(8)
    else:
        # Create theme categories from review text
        themes_keywords = {
            'Transaction Problems': ['transfer', 'payment', 'transaction', 'failed', 'send'],
            'Login Issues': ['login', 'password', 'otp', 'access', 'authentication'],
            'App Performance': ['slow', 'crash', 'freeze', 'loading', 'speed'],
            'UI/Design': ['ui', 'interface', 'design', 'navigation'],
            'Customer Support': ['support', 'help', 'service', 'complaint'],
            'Security': ['secure', 'security', 'fraud', 'safe']
        }
        
        theme_list = []
        for review in df['review']:
            review_lower = str(review).lower()
            assigned = 'General'
            for theme, keywords in themes_keywords.items():
                if any(k in review_lower for k in keywords):
                    assigned = theme
                    break
            theme_list.append(assigned)
        df['theme'] = theme_list
        theme_counts = df['theme'].value_counts().head(8)
    
    colors = plt.cm.viridis(np.linspace(0, 0.8, len(theme_counts)))
    bars = ax.barh(range(len(theme_counts)), theme_counts.values, color=colors, edgecolor='black')
    
    ax.set_yticks(range(len(theme_counts)))
    ax.set_yticklabels(theme_counts.index)
    ax.set_xlabel('Number of Reviews', fontsize=12)
    ax.set_title('Figure 3: Top 8 Themes Across All Banks', fontsize=16, fontweight='bold', pad=20)
    ax.invert_yaxis()
    
    # Add value labels
    for i, (bar, count) in enumerate(zip(bars, theme_counts.values)):
        ax.text(count + 5, bar.get_y() + bar.get_height()/2, str(count), 
                va='center', fontsize=10, fontweight='bold')
    
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig('figures/figure3_top_themes.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 3 created: top_themes.png")

def create_visualization_4_average_rating(df):
    """Figure 4: Average rating comparison"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    avg_ratings = df.groupby('bank')['rating'].mean().sort_values()
    colors = ['#e74c3c' if x < 3.5 else '#f39c12' if x < 4.0 else '#2ecc71' for x in avg_ratings.values]
    bars = ax.barh(range(len(avg_ratings)), avg_ratings.values, color=colors, edgecolor='black')
    
    ax.set_yticks(range(len(avg_ratings)))
    ax.set_yticklabels(avg_ratings.index)
    ax.set_xlabel('Average Rating (1-5 stars)', fontsize=12)
    ax.set_title('Figure 4: Average Rating by Bank', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlim(0, 5)
    
    # Add value labels
    for bar, rating in zip(bars, avg_ratings.values):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2, 
                f'{rating:.2f}', va='center', fontsize=11, fontweight='bold')
    
    ax.axvline(x=3.5, color='red', linestyle='--', alpha=0.5, label='Below Average (3.5)')
    ax.axvline(x=4.0, color='green', linestyle='--', alpha=0.5, label='Good (4.0)')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig('figures/figure4_avg_rating.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 4 created: avg_rating.png")

def create_visualization_5_sentiment_timeline(df):
    """Figure 5: Sentiment trend over time"""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Convert date and group by week
    df['date'] = pd.to_datetime(df['date'])
    df['week'] = df['date'].dt.to_period('W').astype(str)
    
    # Calculate weekly sentiment scores (positive %)
    weekly_sentiment = df.groupby(['week', 'bank']).apply(
        lambda x: (x['sentiment'] == 'positive').sum() / len(x) * 100
    ).reset_index(name='positive_pct')
    
    # Pivot for plotting
    pivot_data = weekly_sentiment.pivot(index='week', columns='bank', values='positive_pct')
    
    colors_map = {'CBE': '#3498db', 'BOA': '#e74c3c', 'Dashen': '#2ecc71'}
    for bank in pivot_data.columns:
        ax.plot(pivot_data.index, pivot_data[bank], marker='o', label=bank, 
                color=colors_map.get(bank), linewidth=2, markersize=6)
    
    ax.set_title('Figure 5: Sentiment Trend Over Time (% Positive Reviews)', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Week', fontsize=12)
    ax.set_ylabel('Positive Reviews (%)', fontsize=12)
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.axhline(y=50, color='green', linestyle='--', alpha=0.5, label='Target (50%)')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('figures/figure5_sentiment_timeline.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ Figure 5 created: sentiment_timeline.png")

def generate_summary_statistics(df):
    """Generate summary statistics table"""
    print("\n" + "="*70)
    print("SUMMARY STATISTICS")
    print("="*70)
    
    summary = []
    for bank in df['bank'].unique():
        bank_df = df[df['bank'] == bank]
        summary.append({
            'Bank': bank,
            'Total Reviews': len(bank_df),
            'Avg Rating': f"{bank_df['rating'].mean():.2f}/5",
            'Positive %': f"{(bank_df['sentiment'] == 'positive').sum() / len(bank_df) * 100:.1f}%",
            'Negative %': f"{(bank_df['sentiment'] == 'negative').sum() / len(bank_df) * 100:.1f}%",
            'Top Theme': bank_df['theme'].mode().iloc[0] if 'theme' in bank_df.columns else 'N/A'
        })
    
    summary_df = pd.DataFrame(summary)
    print(summary_df.to_string(index=False))
    summary_df.to_csv('figures/summary_statistics.csv', index=False)
    return summary_df

def main():
    """Generate all final report visualizations"""
    print("\n" + "="*70)
    print("📊 TASK 4: GENERATING FINAL REPORT VISUALIZATIONS")
    print("="*70)
    
    # Load data
    print("\n📁 Loading data...")
    df = load_data()
    
    # Clean bank names
    df['bank'] = df['bank'].replace({
        'Commercial Bank of Ethiopia': 'CBE',
        'Commercial Bank of Ethiopia (CBE)': 'CBE',
        'Bank of Abyssinia': 'BOA',
        'Bank of Abyssinia (BOA)': 'BOA'
    })
    
    # Generate all 5 visualizations
    print("\n📈 Creating visualizations...")
    create_visualization_1_sentiment_distribution(df)
    create_visualization_2_rating_distribution(df)
    create_visualization_3_top_themes(df)
    create_visualization_4_average_rating(df)
    create_visualization_5_sentiment_timeline(df)
    
    # Generate summary
    summary = generate_summary_statistics(df)
    
    print("\n" + "="*70)
    print("✅ TASK 4 COMPLETE!")
    print("="*70)
    print("\n📁 Output files:")
    print("   - figures/figure1_sentiment_distribution.png")
    print("   - figures/figure2_rating_distribution.png")
    print("   - figures/figure3_top_themes.png")
    print("   - figures/figure4_avg_rating.png")
    print("   - figures/figure5_sentiment_timeline.png")
    print("   - figures/summary_statistics.csv")
    
    return df

if __name__ == "__main__":
    df = main()