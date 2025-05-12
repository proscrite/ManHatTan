import pandas as pd
import numpy as np
import sys
import datetime
import os

def test_rashib(cadscript_path : str):
    """Test whether rashib produces the same cadera as in reference file (Siddhartha)"""

    cadref_path = '/Users/pabloherrero/Documents/ManHatTan/CADERAs/Siddhartha__eine_indische_Dichtung_(German_Edition)_.cder'
    cadref = pd.read_csv(cadref_path, index=False)
    cadscript = pd.read_csv(cadscript_path, index=False)

    compare_series = []
    for col, colr in zip(cadref, cadscript):
        compare_series.append((cadref[col].dropna() == cadref[colr].dropna()))
