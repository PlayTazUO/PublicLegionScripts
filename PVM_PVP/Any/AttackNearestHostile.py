# Make sure to set Options->TazUO->Mobiles->Follow Distance to 1
# Did your radius indicator stay on? Just type `-radius` in game.
import API

# Adjust these settings as desired
MAX_DISTANCE = 10
SHOW_RADIUS_INDICATOR = True
# End user settings.

auto_follow = False
lastHonored = 0
enabled = False
honorTargets = True
newTarget = False
enableAbility = True
lastGroup = 0

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

def enable_ability():
    global enableAbility
    enableAbility = True

def disable_ability():
    global enableAbility
    enableAbility = False

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

def new_target():
    global newTarget
    newTarget = True

def useAbility():
    if not enableAbility:
        return
    if API.Player.ManaDiff < 10 and not API.PrimaryAbilityActive():
        API.ToggleAbility("primary")

def createEnableDisable(text, onEnable, onDisable, gump, x, y, firstChecked):
    global lastGroup
    label = API.CreateGumpTTFLabel(text, 16, "#FFFFFF", aligned="right", maxWidth=98)
    label.SetPos(x, y)
    gump.Add(label)

    button = API.CreateGumpRadioButton("Enable", lastGroup)
    button.IsChecked = firstChecked
    button.SetRect(x + 100, y, 100, 50)
    API.AddControlOnClick(button, onEnable)
    gump.Add(button)

    button2 = API.CreateGumpRadioButton("Disable", lastGroup)
    button2.IsChecked = not firstChecked
    button2.SetRect(x + 200, y, 100, 50)
    API.AddControlOnClick(button2, onDisable)
    gump.Add(button2)
    lastGroup += 1

gump = API.CreateGump()
gump.SetRect(100, 100, 400, 175)
bg = API.CreateGumpColorBox(0.7, "#212121").SetRect(0, 0, 400, 175)
gump.Add(bg)
label = API.CreateGumpTTFLabel("AutoAttack Script", 24, "#FF8800", aligned="center", maxWidth=400)
gump.Add(label)

createEnableDisable("Auto Follow", enable_follow, disable_follow, gump, 25, 50, auto_follow)
createEnableDisable("Honor Targets", enable_honor, disable_honor, gump, 25, 75, honorTargets)
createEnableDisable("Use Abilities", enable_ability, disable_ability, gump, 25, 100, enableAbility)

stopbutton = API.CreateSimpleButton("[STOP]", 100, 25)
stopbutton.SetPos(100, 125)
stopbutton.SetBackgroundHue(32)
gump.Add(stopbutton)
API.AddControlOnClick(stopbutton, stop)

playbutton = API.CreateSimpleButton("[UN-PAUSE]", 100, 25)
playbutton.SetBackgroundHue(53)
playbutton.SetPos(200, 125)
gump.Add(playbutton)
API.AddControlOnClick(playbutton, pause)

targButton = API.CreateSimpleButton("[NEW TARGET]", 100, 25)
targButton.SetPos(150, 150)
targButton.SetBackgroundHue(12)
gump.Add(targButton)
API.AddControlOnClick(targButton, new_target)


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
        enemy_serial = enemy.Serial
        if SHOW_RADIUS_INDICATOR:
            API.DisplayRange(0)

        if auto_follow:
            API.AutoFollow(enemy)

        while enemy and not enemy.IsDead and enemy.Distance < MAX_DISTANCE:
            if not enabled:
                break
            if newTarget:
                newTarget = False
                break
            API.ProcessCallbacks()
            API.Attack(enemy)
            enemy.Hue = 32
            if honorTargets:
                Honor(enemy)
            useAbility()
            API.Pause(0.5)
            enemy = API.FindMobile(enemy_serial)
            #enemy = API.NearestMobile([API.Notoriety.Gray, API.Notoriety.Criminal, API.Notoriety.Murderer], MAX_DISTANCE)
        
    API.Pause(0.5)
