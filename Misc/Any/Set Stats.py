# This script will monitor your stats and adjust them as desired until all of them are locked.
import API

#Set your desired stats here
str = 75
int = 125
dex = 25

while True:
    locked = 0

    if API.Player.Strength > str:
        API.SetStatLock("str", "down")
    elif API.Player.Strength < str:
        API.SetStatLock("str", "up")
    else:
        API.SetStatLock("str", "locked")
        locked += 1

    if API.Player.Intelligence > int:
        API.SetStatLock("int", "down")
    elif API.Player.Intelligence < int:
        API.SetStatLock("int", "up")
    else:
        API.SetStatLock("int", "locked")
        locked += 1

    if API.Player.Dexterity > dex:
        API.SetStatLock("dex", "down")
    elif API.Player.Dexterity < dex:
        API.SetStatLock("dex", "up")
    else:
        API.SetStatLock("dex", "locked")
        locked += 1

    if locked == 3:
        break

    API.Pause(5)
