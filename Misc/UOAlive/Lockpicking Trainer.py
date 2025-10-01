import API
import time
# Intended for UOAlive training boxes at the community center.

API.HeadMsg("Select the lockpick training box.", API.Player, 32)
trainingBox = API.RequestTarget(15)
if not trainingBox:
    API.HeadMsg("No box selected, aborting.", API.Player, 32)
    API.Stop()
    
lastTrainingBoxUpdate = 0

def useLockpick():
    lockpick = API.FindType(5372, API.Backpack)
    if lockpick:
        API.UseObject(lockpick)
        API.Pause(0.25)
    else:
        API.HeadMsg("Out of lockpicks, stopping.", API.Player, 32)
        API.Stop()

while not API.StopRequested:
    if time.time() > lastTrainingBoxUpdate:
        API.UseObject(trainingBox)
        lastTrainingBoxUpdate = time.time() + 300
        API.Pause(0.75)
        
    useLockpick()
    if API.WaitForTarget():
        API.Target(trainingBox)
        API.Pause(0.25)
    API.Pause(0.25)
