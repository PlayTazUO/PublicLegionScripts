import API
# See examples at
#   https://github.com/bittiez/PublicLegionScripts/
# Or documentation at
#   https://github.com/bittiez/TazUO/wiki/TazUO.Legion-Scripting

# Converted from https://github.com/matsamilla/Razor-Enhanced/blob/master/Skills/train_Musicianship.py

musicianshipDelay = 6.5
instruments = [0xe9e, 0x2805, 0xe9c, 0xeb3, 0xeb1, 0x0eb2 , 0x0E9D]
Player = API.Player
Musicianship = API.GetSkill("Musicianship")

def FindInstrument():
    for item in instruments:
        instrument = API.FindType(item, API.Backpack)
        if instrument:
            return instrument
    return None


def TrainMusicianship():  
    instrument = FindInstrument()
    
    if not instrument:
        API.SysMsg("No sintrument found!")
        API.Stop()
        return
    
    while instrument and Musicianship.Value < 100 and not Player.IsDead:
        API.UseObject(instrument)
        API.Pause(musicianshipDelay)
        instrument = FindInstrument()

    if not instrument:
        API.SysMsg('Ran out of instruments to train with', 1100)


TrainMusicianship()
