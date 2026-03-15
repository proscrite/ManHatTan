import sys
import requests
from bs4 import BeautifulSoup
from hebrew import Hebrew
import random

conjugation_key_map = {
    "AP": ("Present", "היום"),
    "PERF": ("Past", "אתמול"),
    "IMPF": ("Future", "מחר"),
    "IMP": ("Imperative", ""),
    "INF": ("Infinitive", "ל..."),
    "ms": ("masculine singular", "הוא"),
    "fs": ("feminine singular", "היא"),
    "mp": ("masculine plural", "הם"),
    "fp": ("feminine plural", "הן"),
    "1s": ("1st person singular", "אני"),
    "1p": ("1st person plural", "אנחנו"),
    "2ms": ("2nd person masculine singular", "אתה"),
    "2fs": ("2nd person feminine singular", "את"),
    "2mp": ("2nd person masculine plural", "אתם"),
    "2fp": ("2nd person feminine plural", "אתן"),
    "3ms": ("3rd person masculine singular", "הוא"),
    "3fs": ("3rd person feminine singular", "היא"),
    "3mp": ("3rd person masculine plural", "הם"),
    "3fp": ("3rd person feminine plural", "הן"),
    "3p": ("3rd person plural", "הם/הן"),
    "L": ("long form", " "),
    "passive": ("passive", "(passive)"),
}

def scrap_verb_link(hebrew_verb):
    search_url = f"https://www.pealim.com/search/?q={hebrew_verb}"
    r = requests.get(search_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Extract all verb entries from the soup
    verb_entries = []

    for entry in soup.select('.verb-search-result'):
        lemma = entry.select_one('.verb-search-lemma a')
        binyan = entry.select_one('.verb-search-binyan')
        pos_string = binyan.get_text(strip=True).lower()  # Get the Parts of Speech string
        if ':verb' in pos_string:   # The colon : is used to prevent "adverb" to be matched
            if lemma:
                text = lemma.get_text(strip=True)
                url = lemma['href']
                verb_entries.append({'text': text, 'url': url})

    first_url = verb_entries[0]['url'] if verb_entries else None
    return "https://www.pealim.com" + first_url if first_url else None

def scrap_conjugation_dict(verb_url):
    if not verb_url:
        return {}
    r = requests.get(verb_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    conjugation_entries = soup.select('.conj-td')

    conjug_dict = {}
    for entry in conjugation_entries:
        for div in entry.find_all('div', id=True):
            div_classes = div.get('class', [])
            menukad = div.find('span', class_='menukad')   # Short spelling with niqqud (no yuds or vavs)
            chaser = div.find('span', class_='chaser')     # Long spelling (with yuds and vavs)
            # Check if this div is a popover-host
            if 'popover-host' in div_classes:   # Popover-hosts are used for "auxiliary" forms which are the common in modern Hebrew 
                aux_forms = div.find('div', class_='aux-forms hidden')
                if aux_forms:
                    menukad_spans = aux_forms.find_all('span', class_='menukad')
                    if menukad_spans:
                        conjugated_verb_nikkud = menukad_spans[-1].get_text(strip=True)
                        verb_noniqqud = Hebrew(conjugated_verb_nikkud).no_niqqud()
                        verb_noniqqud = str(verb_noniqqud).replace('~', '').replace(' ', '')
                        conjug_dict[div['id']] = verb_noniqqud
                        continue  # Skip to next div after handling aux-forms
                    
            if chaser:
                conjugated_verb_nikkud = chaser.get_text(strip=True)
                verb_noniqqud = Hebrew(conjugated_verb_nikkud).no_niqqud()
                verb_noniqqud = str(verb_noniqqud).replace('~', '').replace(' ', '')
                conjug_dict[div['id']] = verb_noniqqud
            elif menukad:
                conjugated_verb_nikkud = menukad.get_text(strip=True)
                verb_noniqqud = Hebrew(conjugated_verb_nikkud).no_niqqud()
                verb_noniqqud = str(verb_noniqqud).replace('~', '').replace(' ', '')
                conjug_dict[div['id']] = verb_noniqqud
    return conjug_dict

def parse_conjugation_key(key):
    """
    Split the key by dash and map each part using combined_conjugation_map.
    Returns two strings: one for English, one for Hebrew hints.
    """
    parts = key.split('-')
    english_parts = []
    hebrew_parts = []
    for part in parts:
        eng, heb = conjugation_key_map.get(part, (part, part))
        english_parts.append(eng)
        hebrew_parts.append(heb)
    parsed_english = " - ".join(english_parts)
    parsed_english = parsed_english.replace("passive - ", "passive, ")
    parsed_hebrew = " ,".join(hebrew_parts)
    return parsed_english, parsed_hebrew

def get_conj_dict(hebrew_verb):
    """Scrape conjugation data for a Hebrew verb from Pealim."""
    verb_url = scrap_verb_link(hebrew_verb)
    conjugation_dict = scrap_conjugation_dict(verb_url)

    if not conjugation_dict:
        print(f"No conjugation data found for {hebrew_verb}")
        return {}
    
    conjugation_dict = {k: v for k, v in conjugation_dict.items() if 'IMP-' not in k} # Exclude imperative forms

    return conjugation_dict

def get_random_conjugation(hebrew_verb):
    """Get a random conjugation of a Hebrew verb."""
    conjugation_dict = get_conj_dict(hebrew_verb)
    if not conjugation_dict:
        return None, None, None, None

    # Randomly select a key from the conjugation dictionary
    random_key = random.choice(list(conjugation_dict.keys()))
    conjugated_verb = conjugation_dict[random_key]
    infinitive_form = conjugation_dict['INF-L']
    # Parse the key to get a human-readable form
    parsed_english, parsed_hebrew = parse_conjugation_key(random_key)
    return parsed_english, parsed_hebrew, conjugated_verb, infinitive_form

if __name__ == "__main__":
    hebrew_verb = sys.argv[1] if len(sys.argv) > 1 else "לכתוב"
    parsed_english, parsed_hebrew, conjugated_verb, infinitive_form = get_random_conjugation(hebrew_verb)
    if parsed_english and conjugated_verb:
        print(f"Random conjugation for '{hebrew_verb}':")
        print(f"Key: {parsed_english}")
        print(f"Conjugated Verb: {conjugated_verb}")
    else:
        print(f"No conjugation found for '{hebrew_verb}'.")
