from mht.scripts.LLM_scripts.multilanguage_generation.generate_multilang_mGPT import gen_multilang_sentence
from mht.scripts.LLM_scripts.english_generation.generate_english_gpt2_medium import gen_en_sentence
from mht.scripts.LLM_scripts.post_processing import claw_english_processing, claw_hebrew_processing
from bidi.algorithm import get_display
import pandas as pd
import asyncio

#############################################
### CLAW: Cloze Lexeme Answer Word  #########
#############################################

def sample_lip_entry(lip: pd.DataFrame) -> pd.DataFrame:
    """
    Sample a random entry from the lip DataFrame.
    """
    if lip.empty:
        raise ValueError("The lip DataFrame is empty.")
    return lip.sample(1)

def claw_exercise(lippath: str, word_ll: str = None, word_ul: str = None) -> tuple[str, str]:
    """
    Example function to demonstrate the use of the lip DataFrame.
    It generates sentences in English and Hebrew using the sampled word.
    Args:
        lippath (str): Path to the lipstick DataFrame.
        word_ll (str, optional): The lower-level word to use. If None, a random entry will be sampled.
        word_ul (str, optional): The upper-level word to use. If None, a random entry will be sampled.
    Returns:
        tuple: A tuple containing the cloze sentence, sampled entry, and translation.
    """
    lip = pd.read_csv(lippath)
    lip = lip.set_index('word_ll', drop=False) 

    if word_ll is None:
        # Sample a random entry from the lip DataFrame
        sampled_entry = sample_lip_entry(lip)
        word_ll = sampled_entry['word_ll'].values[0]
        word_ul = sampled_entry['word_ul'].values[0]
        lexeme_string = sampled_entry['lexeme_string']

    #Try generating the sentence in Hebrew
    # he_sentence = gen_multilang_sentence(word_ll, lang='he', max_attempts=5, max_new_tokens=30)
    # if '(Model did not use the phrase. Try again.)' in he_sentence:
    #     print("Failed to generate a Hebrew sentence. Attempting to generate in English and translating instead.")
        # en_sentence = gen_en_sentence(word_ul)
        # print(f"Generated English sentence: {en_sentence}")
        # flag_success, cloze_sentence, translation = claw_english_processing(word_ll, word_ul, en_sentence, lip)
    # else:
        # print(f"Generated Hebrew sentence: {he_sentence}")
        # Process the Hebrew sentence
        # flag_success, cloze_sentence, translation = claw_hebrew_processing(word_ll, word_ul, he_sentence, lip)

    print(f"Generating sentence in English with word: {word_ul}")
    en_sentence = gen_en_sentence(word_ul)
    print(f"Generated English sentence: {en_sentence}")
    flag_success, cloze_sentence, translation = claw_english_processing(word_ll, word_ul, en_sentence, lip)
 
    # Process the sentences
    if flag_success:
        print(f"Successfully processed the sentence: {cloze_sentence}")
        return cloze_sentence, translation
    else:
        print("Failed to process the sentence.")
        return None

if __name__ == "__main__":
    # Example usage
    lippath = '/Users/pabloherrero/Documents/ManHatTan/mht/data/processed/LIPSTICK/hebrew_db_team.lip'
    result = claw_exercise(lippath)
    if result:
        cloze_sentence, sampled_entry, translation = result
        print(f"Cloze Sentence: {cloze_sentence}")
        print(f"Sampled Entry: {sampled_entry}")
        print(f"Translation: {translation}")
    else:
        print("No valid sentence generated.")