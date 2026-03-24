import pandas as pd
import os
import sys
import codecs
from bs4 import BeautifulSoup

def extract_highlights(soup: BeautifulSoup) -> dict:
    """
    Extracts highlighted text by looking for the highlight color classes,
    ignoring language-specific text like 'Markierung', 'Surligner', etc.
    """
    highlights = {
        'blue': [],
        'pink': [],
        'orange': [],
        'yellow': []
    }
    
    # Iterate over all note headings
    for heading in soup.find_all('div', class_='noteHeading'):
        # Check if this heading indicates a highlight by looking for a color span
        color_span = heading.find('span', class_=lambda c: c and c.startswith('highlight_'))
        
        if color_span:
            # Extract the actual color name from the class (e.g., 'highlight_blue' -> 'blue')
            color_class = next((c for c in color_span['class'] if c.startswith('highlight_')), None)
            if not color_class:
                continue
                
            color = color_class.replace('highlight_', '')
            
            # The highlighted text is in the standard DOM structure 
            # exactly in the next div element with class "noteText"
            text_div = heading.find_next_sibling('div', class_='noteText')
            
            if text_div and color in highlights:
                text = text_div.get_text(strip=True).replace('\n', ' ')
                highlights[color].append(text)
                
    return highlights

def make_cadera(highlights_dict: dict) -> pd.DataFrame:
    """Convert the highlights dictionary into a structured CADERA DataFrame."""
    # Find the maximum length to pad lists properly 
    # (since pad using DataFrame directly fills with NaNs appropriately)
    cadera = pd.DataFrame.from_dict(highlights_dict, orient='index').transpose()
    return cadera


def extract_highlights_html(file_stream) -> pd.DataFrame:
    print(f"Loading file...")
    soup = BeautifulSoup(file_stream, features="lxml")
    
    print("Extracting highlights...")
    highlights_dict = extract_highlights(soup)
    total_found = sum(len(v) for v in highlights_dict.values())
    print(f"Successfully extracted {total_found} highlighted entries")
    
    cadera = make_cadera(highlights_dict)
    
    return cadera

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python krahtos_clean.py <path_to_html>")
        sys.exit(1)
        
    extract_highlights_html(sys.argv[1])
