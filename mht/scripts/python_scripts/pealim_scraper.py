import sys
import requests
from bs4 import BeautifulSoup
from hebrew import Hebrew
import random

conjugation_key_map = {
	"AP": "Present",
	"PERF": "Past",
	"IMPF": "Future",
	"IMP": "Imperative",
	"INF": "Infinitive",
	"ms": "masculine singular",
	"fs": "feminine singular",
	"mp": "masculine plural",
	"fp": "feminine plural",
	"1s": "1st person singular",
	"1p": "1st person plural",
	"2ms": "2nd person masculine singular",
	"2fs": "2nd person feminine singular",
	"2mp": "2nd person masculine plural",
	"2fp": "2nd person feminine plural",
	"3ms": "3rd person masculine singular",
	"3fs": "3rd person feminine singular",
	"3mp": "3rd person masculine plural",
	"3fp": "3rd person feminine plural",
    "3p": "3rd person plural",
	"L": "long form"
}

def get_verb_link(hebrew_verb):
    search_url = f"https://www.pealim.com/search/?q={hebrew_verb}"
    r = requests.get(search_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # Extract all verb entries from the soup
    verb_entries = []

    for entry in soup.select('.verb-search-result'):
        lemma = entry.select_one('.verb-search-lemma a')
        binyan = entry.select_one('.verb-search-binyan')
        if 'verb' in binyan.get_text(strip=True).lower():
        
            if lemma:
                text = lemma.get_text(strip=True)
                url = lemma['href']
                verb_entries.append({'text': text, 'url': url})

    first_url = verb_entries[0]['url'] if verb_entries else None
    return "https://www.pealim.com" + first_url if first_url else None

def get_conjugation_dict(verb_url):
    if not verb_url:
        return {}
    r = requests.get(verb_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    conjugation_entries = soup.select('.conj-td')

    conjug_dict = {}
    for entry in conjugation_entries:
        for div in entry.find_all('div', id=True):
            menukad = div.find('span', class_='menukad')
            if menukad:
                conjugated_verb_nikkud = menukad.get_text(strip=True)
                verb_noniqqud = Hebrew(conjugated_verb_nikkud).no_niqqud()
                conjug_dict[div['id']] = verb_noniqqud
    return conjug_dict

def parse_conjugation_key(key, key_map):
    """Split the key by dash and map each part using key_map if possible."""
    parts = key.split('-')
    mapped_parts = [key_map.get(part, part) for part in parts]
    return " - ".join(mapped_parts)

def get_conj_dict(hebrew_verb):
    """Scrape conjugation data for a Hebrew verb from Pealim."""
    verb_url = get_verb_link(hebrew_verb)
    conjugation_dict = get_conjugation_dict(verb_url)

    if not conjugation_dict:
        print(f"No conjugation data found for {hebrew_verb}")
        return {}
    
    conjugation_dict = {k: v for k, v in conjugation_dict.items() if 'IMP-' not in k}

    return conjugation_dict

def get_random_conjugation(hebrew_verb):
    """Get a random conjugation of a Hebrew verb."""
    conjugation_dict = get_conj_dict(hebrew_verb)
    if not conjugation_dict:
        return None, None

    # Randomly select a key from the conjugation dictionary
    random_key = random.choice(list(conjugation_dict.keys()))
    conjugated_verb = conjugation_dict[random_key]
    
    # Parse the key to get a human-readable form
    parsed_key = parse_conjugation_key(random_key, conjugation_key_map)
    
    return parsed_key, conjugated_verb

if __name__ == "__main__":
    hebrew_verb = sys.argv[1] if len(sys.argv) > 1 else "לכתוב"
    parsed_key, conjugated_verb = get_random_conjugation(hebrew_verb)
    if parsed_key and conjugated_verb:
        print(f"Random conjugation for '{hebrew_verb}':")
        print(f"Key: {parsed_key}")
        print(f"Conjugated Verb: {conjugated_verb}")
    else:
        print(f"No conjugation found for '{hebrew_verb}'.")
