import API
import time

BANDAGE = 3617
FOLLOW_PET = True
VET_DELAY = 4
USEBUFF = True
USE_MAGERY = False

# Don't edit below here
usemag = API.GetPersistentVar("PetHealer.py USE_MAGERY", "False", API.PersistentVar.Char)
if usemag == "True":
    USE_MAGERY = True

usemag = API.GetPersistentVar("PetHealer.py USE_BUFF", "True", API.PersistentVar.Char)
if usemag == "True":
    USEBUFF = True

PETS = [0x0010A52B, 0x000B81BD]

def useBang():
    if API.FindType(BANDAGE):
        if FOLLOW_PET:
            API.AutoFollow(pet)
            while mob.Distance > 1:
                API.Pause(0.1)
        API.UseObject(API.Found)

def useMagery():
    API.CastSpell("Greater Heal")

def enableMagery():
    global USE_MAGERY
    USE_MAGERY = True
    API.SavePersistentVar("PetHealer.py USE_MAGERY", "True", API.PersistentVar.Char)
    API.SysMsg("Using Magery for healing", 66)

def enableBandies():
    global USE_MAGERY
    USE_MAGERY = False
    API.SavePersistentVar("PetHealer.py USE_MAGERY", "False", API.PersistentVar.Char)
    API.SysMsg("Using Bandages for healing", 66)

def onClosed():
    API.SavePersistentVar("PetHealer.py XY", f"{lastX},{lastY}", API.PersistentVar.Char)
    API.Stop()

savedX = API.GetPersistentVar("PetHealer.py XY", "100,100", API.PersistentVar.Char)
split = savedX.split(',')
lastX = int(split[0])
lastY = int(split[1])

gump = API.Gumps.CreateGump()
API.Gumps.AddControlOnDisposed(gump, onClosed)
gump.SetRect(lastX, lastY, 300, 100)

bg = API.Gumps.CreateGumpColorBox(0.7, "#212121")
bg.SetRect(0, 0, 300, 100)
gump.Add(bg)

label = API.Gumps.CreateGumpTTFLabel("Pet Healer Script", 24, "#FF8800", aligned="center", maxWidth=300)
gump.Add(label)

button = API.Gumps.CreateGumpRadioButton("Magery")
button.IsChecked = USE_MAGERY
button.SetRect(50, 50, 100, 25)

API.Gumps.AddControlOnClick(button, enableMagery)
gump.Add(button)

button = API.Gumps.CreateGumpRadioButton("Bandies")
button.IsChecked = not USE_MAGERY
button.SetRect(150, 50, 100, 25)

API.Gumps.AddControlOnClick(button, enableBandies)
gump.Add(button)

API.Gumps.AddGump(gump)


next = time.time() + 5

while not API.StopRequested:
    API.ProcessCallbacks()

    if time.time() > next and gump:
        lastX = gump.GetX()
        lastY = gump.GetY()
        next = time.time() + 10

    for pet in PETS:
        mob = API.FindMobile(pet)
        if mob and mob.HitsDiff > 2:
            API.HeadMsg("Healing pet: " + mob.Name, pet)
            if not USE_MAGERY:
                useBang()
            else:
                useMagery()
            API.WaitForTarget()
            API.Target(pet)
            API.Pause(0.5)
            if USEBUFF and not USE_MAGERY:
                while API.BuffExists("Veterinary"):
                    API.ProcessCallbacks()
                    API.Pause(0.1)
                API.Pause(0.1)
            else:
                API.Pause(VET_DELAY)
            if FOLLOW_PET:
                API.CancelAutoFollow()
            #API.HeadMsg(f"{mob.Hits}/{mob.HitsMax} - {mob.HitsDiff}", pet, 32)
    API.Pause(0.5)