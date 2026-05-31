#!/usr/bin/env python3
"""Scrape CPNS TWK questions from Indonesian educational websites."""

import json
import re
import subprocess
import sys

def fetch_url(url):
    """Fetch URL content using curl."""
    try:
        result = subprocess.run(
            ['curl', '-sL', '--max-time', '30', '-A', 
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
             url],
            capture_output=True, text=True, timeout=35
        )
        return result.stdout
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def parse_html_text(html):
    """Basic HTML tag removal."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL|re.IGNORECASE)
    text = re.sub(r'<[^>]+>', '\n', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&#\d+;', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def main():
    urls = [
        "https://www.detik.com/edu/soal-tryout/detikpedia-6737792/kumpulan-soal-twk-cpns-2024-materi-pancasila-lengkap-jawaban",
        "https://www.gramedia.com/best-seller/soal-twk-cpns/",
        "https://pendidikanpedia.com/kumpulan-soal-twk-cpns-pancasila/"
    ]
    
    all_questions = []
    
    for i, url in enumerate(urls):
        print(f"\n=== Fetching URL {i+1}: {url} ===")
        html = fetch_url(url)
        if not html:
            print(f"  Failed to fetch URL {i+1}")
            continue
        
        print(f"  Got {len(html)} bytes")
        
        # Save raw HTML for inspection
        with open(f'/root/cpns/raw_html_{i+1}.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        # Extract text content
        text = parse_html_text(html)
        with open(f'/root/cpns/raw_text_{i+1}.txt', 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"  Text length: {len(text)} chars")
        print(f"  First 500 chars: {text[:500]}")
    
    print("\nDone fetching. Check raw files for content inspection.")

if __name__ == '__main__':
    main()
