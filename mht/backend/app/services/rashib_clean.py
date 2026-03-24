import pandas as pd
import docx
import os
import sys

def classify_words_fillcolor(words: list) -> dict:
    """
    Extract and classify text runs by their background fill color into a DataFrame.
    """
    WPML_URI = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    tag_t = f"{WPML_URI}t"
    tag_fill = f"{WPML_URI}fill"
    
    # Map hex codes used by the highlights to readable color names
    color_map = {
        'fde096': 'gold',
        'ffb8a1': 'orange',
        '93e3ed': 'blue',
        'c5e1a5': 'green'
    }
    
    highlights = {color: [] for color in color_map.values()}

    for word in words:
        # Check all child <w:shd> tags within the run's properties (<w:rPr>)
        shades = word.xpath('.//w:shd')
        for shd in shades:
            fill_val = shd.get(tag_fill)
            if fill_val in color_map:
                text_node = word.find(tag_t)
                if text_node is not None and text_node.text:
                    # Clean and lowercase the text
                    highlights[color_map[fill_val]].append(text_node.text.strip().lower())

    total = sum(len(v) for v in highlights.values())
    print(f"Found {total} colorfilled words")
    
    return highlights

def make_cadera(highlights: dict) -> pd.DataFrame:
    """Convert the highlights dictionary into a structured CADERA DataFrame.
    Uses pandas to handle unequal column lengths by filling with NaNs."""
    # Use pandas to transpose, which will automatically handle padding unequal column lengths with NaNs
    cadera = pd.DataFrame.from_dict(highlights, orient='index').transpose()
    return cadera

def extract_highlights_docx(file_stream) -> pd.DataFrame:
    print(f"Loading file")
            
    document = docx.Document(file_stream)
    # Extract all run elements using lxml xpath
    words = document.element.xpath('//w:r')
    
    print("Classifying highlights...")
    highlight_dict = classify_words_fillcolor(words)

    cadera = make_cadera(highlight_dict)
    
    return cadera

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rashib_clean.py <path_to_docx>")
        sys.exit(1)
        
    extract_highlights_docx(sys.argv[1])
