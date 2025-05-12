import pandas as pd
import numpy as np
import sys
import datetime
import os

def test_init_lipstick(lipscript_path : str):
    """Test whether init_lipstick produces the same lipstick as in reference file (Siddhartha)
        and indicate what words differ"""

    lipref_path = '/Users/pabloherrero/Documents/ManHatTan/LIPSTICK/Siddhartha__eine_indische_Dichtung_(German_Edition)_.lip'
    lipref = pd.read_csv(lipref_path)
    lipscript = pd.read_csv(lipscript_path)

    compare_df = (lipscript == lipref)
    fails = np.where(compare_df == False)
    print('Found (%i,%i) row,cols replication fails at init_lipstick'%(len(fails[0]), len(fails[1]) ) )
    print('On reference file:')
    print(lipref.iloc[fails[0], fails[1]])
    print('On processed file:')
    print(lipscript.iloc[fails[0], fails[1]])
