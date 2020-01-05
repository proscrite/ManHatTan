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
        soup = BeautifulSoup(f.read())
        if DEBUG:
            print("Raw html data: \n", f.read())

        return soup

    else:
        print('load_html: File extension not supported')
        return []

def find_words_headings(soup : bs4.BeautifulSoup, DEBUG : bool = False):
    """Extract all words/sentences (class: "noteText") and its corresponding
    color labels (class: "noteHeading" -> subclass: "highlight_col")
    and classify them into CADERA
    Input: html soup
    Output CADERA"""

    words0 = soup.findAll("div", {"class": "noteText"})
    words = [w.string.replace('\n', '') for w in words0] ## Format words

    labels = soup.findAll("div", {"class": "noteHeading"})

    ### Filter labels: keep only highlighted marks
    marks = []
    for lb in labels:
        if 'Markierung' in lb.text:
            marks.append(lb)
        elif 'Mark' in lb.text:
            marks.append(lb)
    labels = marks

    ### Crosscheck number of found words and color labels:
    if len(labels) == len(words):
        print('Successfully extracted %i highlighted entries' %len(words))
    else:
        print('find_words_headings Error: Parsing failed: unequal number of entries and color labels.')
        return 0
        exit

    if DEBUG:
        print('Found %i words: ' %len(words), words)
        print('\nFound %i labels: ' %len(labels), labels)

    ### Classify by colors:
    blueEntries, pinkEntries, orangeEntries, yellowEntries = [], [], [], []

    for (w, lb) in zip(words, labels):
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

def write_cadera(krahtos : str, cadera : pd.DataFrame):
    """Convert krahtos (full) basename into '.cder' extension and flush CADERA df"""
    pathname = os.path.splitext(os.path.abspath(krahtos))[0]
    path, filename = os.path.split(pathname)
    dirPath, _ = os.path.split(path)
    fpath = os.path.join(dirPath, 'CADERAs', filename+'.cder')
    cadera.to_csv(fpath)
    print('Created CADERA file %s' %fpath)

######### Main #########

krahtos = sys.argv[1]

soup = load_html(krahtos)

cadera = find_words_headings(soup = soup, DEBUG = False)

write_cadera(krahtos, cadera)
