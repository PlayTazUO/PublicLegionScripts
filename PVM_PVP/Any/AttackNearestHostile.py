# Make sure to set Options->TazUO->Mobiles->Follow Distance to 1
# Did your radius indicator stay on? Just type `-radius` in game.
import API

# Adjust these settings as desired
MAX_DISTANCE = 5
SHOW_RADIUS_INDICATOR = True
# End user settings.

auto_follow = False
lastHonored = 0
enabled = False
honorTargets = True

def enable_follow():
    global auto_follow
    auto_follow = True
    
def disable_follow():
    global auto_follow
    auto_follow = False

def stop():
    API.DisplayRange(0)
    gump.Dispose()
    API.Stop()

def enable_honor():
    global honorTargets
    honorTargets = True

def disable_honor():
    global honorTargets
    honorTargets = False

def pause():
    global enabled
    enabled = not enabled
    playbutton.SetText("[PAUSE]" if enabled else "[UN-PAUSE]")
    playbutton.SetBackgroundHue(172 if enabled else 53)
    API.DisplayRange(0)

def Honor(mob):
    global lastHonored
    if mob:
        if mob.Serial != lastHonored and mob.HitsDiff == 0 and mob.Distance < 6:
            API.Virtue("honor")
            API.WaitForTarget()
            API.Target(mob)
            lastHonored = mob.Serial
            API.CancelTarget()

gump = API.CreateGump()
gump.SetRect(100, 100, 400, 150)
bg = API.CreateGumpColorBox(0.7, "#212121")
bg.SetRect(0, 0, 400, 150)
gump.Add(bg)
label = API.CreateGumpTTFLabel("AutoAttack Script", 24, "#FF8800", aligned="center", maxWidth=400)
gump.Add(label)

button1 = API.CreateGumpRadioButton("Enable auto follow")
button1.SetRect(25, 50, 100, 50)
gump.Add(button1)
API.AddControlOnClick(button1, enable_follow)

button2 = API.CreateGumpRadioButton("Disable auto follow")
button2.IsChecked = True
button2.SetRect(200, 50, 100, 50)
gump.Add(button2)
API.AddControlOnClick(button2, disable_follow)

honorOn = API.CreateGumpRadioButton("Enable honor targets", 1)
honorOn.IsChecked = True
honorOn.SetRect(25, 75, 100, 50)
gump.Add(honorOn)
API.AddControlOnClick(honorOn, enable_honor)

honorOff = API.CreateGumpRadioButton("Disable honor targets", 1)
honorOff.SetRect(200, 75, 100, 50)
gump.Add(honorOff)
API.AddControlOnClick(honorOff, disable_honor)

stopbutton = API.CreateSimpleButton("[STOP]", 100, 25)
stopbutton.SetPos(100, 100)
stopbutton.SetBackgroundHue(32)
gump.Add(stopbutton)
API.AddControlOnClick(stopbutton, stop)

playbutton = API.CreateSimpleButton("[UN-PAUSE]", 100, 25)
playbutton.SetBackgroundHue(53)
playbutton.SetPos(200, 100)
gump.Add(playbutton)
API.AddControlOnClick(playbutton, pause)


API.AddGump(gump)

Player = API.Player
while True:
    API.ProcessCallbacks()
    if not enabled:
        API.Pause(0.5)
        continue

    if SHOW_RADIUS_INDICATOR:
        API.DisplayRange(MAX_DISTANCE, 32)    
    enemy = API.NearestMobile([API.Notoriety.Gray, API.Notoriety.Criminal, API.Notoriety.Murderer], MAX_DISTANCE)
    if enemy:
        if SHOW_RADIUS_INDICATOR:
            API.DisplayRange(0)

        if auto_follow:
            API.AutoFollow(enemy)

        while enemy and not enemy.IsDead and enemy.Distance < MAX_DISTANCE:
            if not enabled:
                break
            API.ProcessCallbacks()
            API.Attack(enemy)
            enemy.Hue = 32
            if honorTargets:
                Honor(enemy)
            API.Pause(0.5)
            enemy = API.NearestMobile([API.Notoriety.Gray, API.Notoriety.Criminal, API.Notoriety.Murderer], MAX_DISTANCE)
        
    API.Pause(0.5)
