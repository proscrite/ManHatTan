import pandas as pd
import numpy as np
import docx
import os
import sys
import codecs
import bs4
from bs4 import BeautifulSoup

## KRAHTOS:
##    Kindle Raw Array of HTml Original Source  ###

def load_html(krahtos : str, DEBUG : bool = False) -> bs4.BeautifulSoup:
    """Check input file extension (krahtos) and load whole soup
    Use DEBUG flag to print whole raw text
    KRAHTOS:
        Kindle Raw Array of HTml Original Source"""

    if '.html' in krahtos:
        f = codecs.open(krahtos, 'r')
        soup = BeautifulSoup(f.read(), features="lxml")
        if DEBUG:
            print("Raw html data: \n", f.read())

        return soup

    else:
        print('load_html: File extension not supported')
        return []

def find_words_headings(soup : bs4.BeautifulSoup, DEBUG : bool = False):
    """Extract all words/sentences (class: "noteText") and its corresponding
    color labels (class: "noteHeading" -> subclass: "highlight_col")
    Input: html soup
    Output:
    -------
    mWords: list of marked words (filter out user notes and position markers)
    labels: list of maker header containing the color highlight_col"""

    words0 = soup.findAll("div", {"class": "noteText"})
    words = [w.string.replace('\n', '') for w in words0] ## Format words

    labels = soup.findAll("div", {"class": "noteHeading"})

    if DEBUG:
        print('Found %i words: ' %len(words), words)
        print('\nFound %i labels: ' %len(labels), labels)

    userNotes = []
    mWords = []
    marks = []

    for w,lb in zip(words, labels):
        if 'Markierung' in lb.text:    # Using german version of kindle App
            marks.append(lb)
            mWords.append(w)
        elif 'Mark' in lb.text:    # Using english version of kindle App
            marks.append(lb)
            mWords.append(w)
        elif 'Surligner' in lb.text:    # Using french version of kindle App
            marks.append(lb)
            mWords.append(w)
        elif 'Subrayado' in lb.text: # Using spanish version of kindle App
            marks.append(lb)
            mWords.append(w)
    #     elif 'Note' in lb.text:# or 'Signet' in lb.text:
    #         userNotes.append(i)
    #         labels.pop(i)

    labels = marks
    ### Crosscheck number of found words and color labels:
    if len(labels) == len(mWords):
        print('Successfully extracted %i highlighted entries' %len(words))
        return mWords, labels

    else:
        print('find_words_headings Error: Parsing failed: unequal number of entries and color labels.')
        return 0

def make_cadera(mWords: list, labels : list, DEBUG = False) -> pd.DataFrame:
    """Take marked words mwords and labels and classify by colors into CADERA """
    ### Classify by colors:
    blueEntries, pinkEntries, orangeEntries, yellowEntries = [], [], [], []

    for (w, lb) in zip(mWords, labels):
        if len(lb.findAll("span", {"class": "highlight_blue"})):
            blueEntries.append(w)
        if len(lb.findAll("span", {"class": "highlight_pink"})):
            pinkEntries.append(w)
        if len(lb.findAll("span", {"class": "highlight_orange"})):
            orangeEntries.append(w)
        if len(lb.findAll("span", {"class": "highlight_yellow"})):
            yellowEntries.append(w)

        if DEBUG:
            print('Entries arrays: ', blueEntries, pinkEntries, orangeEntries, yellowEntries)

    cadera = pd.DataFrame([blueEntries, pinkEntries, orangeEntries, yellowEntries]).T
    cadera.columns = ['blue', 'pink', 'orange', 'yellow']
    return cadera

def clean_filename(filename : str)->str:
    """Remove automatically added "Notes from..." string from filename"""
    filename = filename.replace(' ', '_')
    filename = filename.replace('_-_Bloc-notes', '')
    filename = filename.replace('_-_Bloc_de_notas', '')
    filename = filename.replace('_-_Notizbuch', '')

    filename = filename.replace('Notes_from__', '')
    filename = filename.replace('Notizen_aus__', '')

    return filename

def write_cadera(krahtos : str, cadera : pd.DataFrame):
    """Convert krahtos (full) basename into '.cder' extension and flush CADERA df"""
    pathname = os.path.splitext(os.path.abspath(krahtos))[0]
    path, filename = os.path.split(pathname)

    filename = clean_filename(filename)

    dirPath, _ = os.path.split(path)
    fpath = os.path.join(dirPath, 'CADERAs', filename+'.cder')
    cadera.to_csv(fpath)
    print('Created CADERA file %s' %fpath)
    return fpath

def krahtos_main(krahtos):
    #krahtos = sys.argv[1]

    print('Loading file ', krahtos)
    soup = load_html(krahtos)

    mWords, labels = find_words_headings(soup = soup, DEBUG = False)

    cadera = make_cadera(mWords, labels)

    cadera_path = write_cadera(krahtos, cadera)
    return cadera_path

######### Main #########
if __name__ == "__main__":
    krahtos_main(sys.argv[1])
