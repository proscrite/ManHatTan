from __future__ import annotations

import time
import numpy as np
from functools import partial
from pathlib import Path
from mac_notifications import client

import sys
ROOT_PATH = '/Users/pabloherrero/Documents/ManHatTan'
sys.path.append(ROOT_PATH+'/gui/')
import subprocess

def random_game(nreps : int = 4) -> None:
    num_ex = 1
    while num_ex <= nreps:
        gameKeys = {0: 'madte.py', 1: 'marte.py', 2: 'widte.py', 3: 'wirte.py'}
        rndInt = np.random.randint(4)
        rndGame = gameKeys[rndInt]
        gameScriptPath = f"{ROOT_PATH}/gui/{rndGame}"
        # currentDb = '/Users/pabloherrero/Documents/ManHatTan/data/processed/LIPSTICK/hebrew_db.lip'
        currentDb = '/Users/pabloherrero/Documents/ManHatTan/data/processed/LIPSTICK/hebrew_db_team.lip'
        try:
            subprocess.run(['/usr/bin/python3', gameScriptPath, currentDb], check=True)
            print(f"Successfully ran {rndGame}")
        except subprocess.CalledProcessError as e:
            print(f"Error running {rndGame}: {e}")
        
        num_ex += 1

if __name__ == "__main__":
    nInterval = 1
    while nInterval <= 5:
        print("You have to press the notification within 30 seconds for it to work.")
        client.create_notification(
            title="Want to play a quick Manhattan round?",
            subtitle="It will take 2 minutes",
            icon="/Users/pabloherrero/Documents/ManHatTan/gui/Graphics/Transitions/vsBar1.png",
            # icon=Path(__file__).parent.parent.parent / "gui" / "Graphics" / "Transitions" / "vsBar1.png",
            action_button_str="Play!",
            action_callback=partial(random_game),
        )
        time.sleep(60 * 60)
        nInterval += 1    
    client.stop_listening_for_callbacks()
