# This script will monitor your stats and adjust them as desired until all of them are locked.
import API

#Set your desired stats here
STR = 75
INT = 125
DEX = 25

while True:
    locked = 0

    if API.Player.Strength > STR:
        API.SetStatLock("str", "down")
    elif API.Player.Strength < STR:
        API.SetStatLock("str", "up")
    else:
        API.SetStatLock("str", "locked")
        locked += 1

    if API.Player.Intelligence > INT:
        API.SetStatLock("int", "down")
    elif API.Player.Intelligence < INT:
        API.SetStatLock("int", "up")
    else:
        API.SetStatLock("int", "locked")
        locked += 1

    if API.Player.Dexterity > DEX:
        API.SetStatLock("dex", "down")
    elif API.Player.Dexterity < DEX:
        API.SetStatLock("dex", "up")
    else:
        API.SetStatLock("dex", "locked")
        locked += 1

    if locked == 3:
        break

    API.Pause(5)