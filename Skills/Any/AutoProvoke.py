import API

# Settings
MaxDistance = 7
ProvokeDelay = 11 # Delay between provokes in seconds
Instruments = [0xe9e, 0x2805, 0xe9c, 0xeb3, 0xeb1, 0x0eb2 , 0x0E9D]
# End Settings

def FindInstrument():
    for item in Instruments:
        instrument = API.FindType(item, API.Backpack)
        if instrument:
            return instrument
    return None

while True:
    instrument = FindInstrument()
    if not instrument:
        API.SysMsg("No instrument found in backpack.", 32)
        break
    
    target1 = API.NearestMobile([API.Notoriety.Gray, API.Notoriety.Criminal, API.Notoriety.Enemy], MaxDistance)
    if not target1:
        API.SysMsg("No valid targets found.", 32)
        break
    
    API.HeadMsg("Target 1", target1)
    API.IgnoreObject(target1)
    
    target2 = API.NearestMobile([API.Notoriety.Gray, API.Notoriety.Criminal, API.Notoriety.Enemy], MaxDistance)
    if not target2:
        API.SysMsg("No valid targets found.", 32)
        break
    
    API.IgnoreObject(target2)
    API.HeadMsg("Target 2", target2)
    

    API.UseSkill("Provocation")
    API.WaitForTarget()
    
    if API.InJournal("What instrument"):
        API.Target(instrument)
        API.WaitForTarget()
    
    API.Target(target1)
    API.WaitForTarget()
    API.Target(target2)
    API.Pause(ProvokeDelay)
    API.ClearIgnoreList()
    API.ClearJournal()
