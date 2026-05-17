"""
Find correct Google Play package names for Ethiopian banking apps
"""

try:
    from google_play_scraper import search
    import time
    
    print("🔍 Searching for Ethiopian banking apps on Google Play...")
    print("="*50)
    
    banks_to_search = [
        "Commercial Bank of Ethiopia",
        "Bank of Abyssinia", 
        "Dashen Bank",
        "CBE Birr",
        "Amole",
        "Hellocash"
    ]
    
    for bank in banks_to_search:
        print(f"\n📱 Searching: {bank}")
        try:
            results = search(bank, n_hits=5)
            
            found = False
            for result in results:
                if any(word.lower() in result['title'].lower() for word in ['bank', 'birr', 'mobile']):
                    print(f"   ✅ Found: {result['title']}")
                    print(f"      Package: {result['appId']}")
                    print(f"      Score: {result.get('score', 'N/A')}")
                    found = True
            
            if not found:
                print(f"   ❌ No banking app found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)
    
    print("\n" + "="*50)
    print("💡 Use these package names in your scraper")
    
except ImportError:
    print("❌ google-play-scraper not installed")
    print("Run: pip install google-play-scraper")