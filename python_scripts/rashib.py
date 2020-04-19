import pandas as pd
import numpy as np
import docx
import os
import sys

def load_docx(rashib : str) -> list:
    """Check input file extension and load individual words, independent from fill color
    RASHIB:
        Raw Array of Sentences Highlighted In Book"""

    if '.docx' in rashib:
        document = docx.Document(rashib)
        words = document.element.xpath('//w:r')
        return words

    else:
        print('load_docx: File extension not supported')
        return []

def classify_words_fillcolor(words: str) -> pd.DataFrame:
    """Take raw xml words and classify them by fill color in CADERA df.
    CADERA:
        Color-Arranged Dataframe Extracted from RAshib"""

    WPML_URI = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    tag_rPr = WPML_URI + 'rPr'
    tag_highlight = 'w:shd'
    tag_val = WPML_URI + 'fill'
    tag_t = WPML_URI + 't'
    gold = []
    blue = []
    orange = []

    for word in words:
        for rPr in word.findall(tag_rPr):
            high=rPr.xpath(tag_highlight)
            for hi in high:

                if hi.attrib[tag_val] == 'fde096':
                    gold.append(word.find(tag_t).text.lower())
                elif hi.attrib[tag_val] == 'ffb8a1':
                    orange.append(word.find(tag_t).text.lower())
                elif hi.attrib[tag_val] == '93e3ed':
                    blue.append(word.find(tag_t).text.lower())

    print('Found %i colorfilled words' %(len(gold) + len(orange) + len(blue)))
    cadera = pd.DataFrame([gold, blue, orange]).T
    cadera.columns = ['gold', 'blue', 'orange']

    return cadera

def clean_filename(filename : str)->str:
    """Remove automatically added "Notes from..." string from filename"""
    filename = filename.replace(' ', '_')
    filename = filename.replace('_-_Bloc-notes', '')
    filename = filename.replace('_-_Notizbuch', '')

    filename = filename.replace('Notes_from__', '')
    filename = filename.replace('Notizen_aus__', '')

    return filename

def write_cadera(rashib : str, cadera : pd.DataFrame):
    """Convert rashib (full) basename into '.cder' extension and flush CADERA df"""

    pathname = os.path.splitext(os.path.abspath(rashib))[0]
    path, filename = os.path.split(pathname)
    dirPath, _ = os.path.split(path)
    fpath = os.path.join(dirPath, 'CADERAs', filename+'.cder')

    filename = clean_filename(filename)
    fpath = os.path.join(dirPath, 'CADERAs', filename+'.cder')
    cadera.to_csv(fpath)
    print('Created CADERA file %s' %fpath)
    return fpath

def rashib_main(rashib):

    words = load_docx(rashib)

    cadera = classify_words_fillcolor(words)

    cadera_path = write_cadera(rashib, cadera)
    return cadera_path


######### Main #########
if __name__ == "__main__":
    rashib_main(sys.argv[1])
