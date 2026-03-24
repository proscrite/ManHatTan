import pandas as pd
import io
import re
from deep_translator import GoogleTranslator
from typing import List, Dict
from .rashib_clean import extract_highlights_docx
from .krahtos_clean import extract_highlights_html
from .bulk_translate import find_language, bulk_translate 

def remove_nikud(text: str) -> str:
    """Removes all Hebrew Niqqud (vowels) and cantillation marks."""
    if not isinstance(text, str):
        return ""
    return re.sub(r'[\u0591-\u05C7]', '', text)

def parse_google_translate_csv(file_bytes: bytes) -> List[Dict[str, str]]:
    try:
        df = pd.read_csv(
            io.BytesIO(file_bytes), 
            header=None, 
            sep=None, 
            engine='python',
            usecols=[0, 1, 2, 3],
            names=['SL', 'TL', 'SW', 'TW']
        )
    except Exception as e:
        raise ValueError(f"Could not parse CSV format: {str(e)}")

    parsed_words = []
    
    for _, row in df.iterrows():
        sl = str(row.get('SL', '')).strip()
        tl = str(row.get('TL', '')).strip()
        sw = str(row.get('SW', '')).strip()
        tw = str(row.get('TW', '')).strip()
        
        if not sw or not tw or sw == 'nan' or tw == 'nan':
            continue
            
        word_ul = ""
        word_ll = ""
        
        if sl.lower() == 'english' and tl.lower() == 'hebrew':
            word_ul = sw
            word_ll = tw
        elif sl.lower() == 'hebrew' and tl.lower() == 'english':
            word_ll = sw
            word_ul = tw
        else:
            continue

        word_ll_clean = remove_nikud(word_ll)
            
        parsed_words.append({
            "word_ul": word_ul,
            "word_ll": word_ll_clean, 
            "source_type": "Google Translate"
        })
        
    return parsed_words

async def parse_highlighted_document(file_bytes: bytes, target_color: str, 
                               source_lang: str, target_lang: str,
                               platform: str) -> List[Dict[str, str]]:
    """
    Unified parser for both Kindle (HTML) and Play Books (DOCX) exports.
    """
    # 1. Route to the correct extraction engine
    if platform == 'playbooks':
        df = extract_highlights_docx(io.BytesIO(file_bytes))
        source_prefix = "Play Books"
    elif platform == 'kindle':
        df = extract_highlights_html(io.BytesIO(file_bytes))
        source_prefix = "Kindle"
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    # 2. Validate the color exists in the parsed DataFrame
    target_color = target_color.lower()
    if target_color not in df.columns:
        raise ValueError(f"Color '{target_color}' not found. Available colors: {list(df.columns)}")
        
    # 3. Extract, clean, and deduplicate
    words_series = df[target_color].dropna().astype(str).str.strip()
    words_series = words_series[words_series != '']
    unique_words = list(words_series.unique())

    # 4. Auto-detect source language if set to "auto"
    if source_lang == "auto":
        print("Auto-detecting source language...")
        detected_lang = await find_language(unique_words)
        source_lang = detected_lang if detected_lang else 'en' # Fallback
        print(f"Detected Language: {source_lang}")
    
    # 5. Translate via googletrans batching
    translations = await bulk_translate(unique_words, src_lang=source_lang, dest_lang=target_lang)
    
    # 6. Format for the router
    parsed_data = []
    for word_ll in unique_words:
        parsed_data.append({
            "word_ul": translations.get(word_ll, ""),
            "word_ll": remove_nikud(word_ll),
            "source_type": f"{source_prefix} ({target_color.capitalize()})"
        })
        
    return parsed_data