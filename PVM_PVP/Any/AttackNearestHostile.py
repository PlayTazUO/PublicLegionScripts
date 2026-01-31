# Make sure to set Options->TazUO->Mobiles->Follow Distance to 1
# Did your radius indicator stay on? Just type `-radius` in game.
import API

# Adjust these settings as desired
MAX_DISTANCE = 10
SHOW_RADIUS_INDICATOR = True
# End user settings.

c_afollowsave = "aas_autofollow"
c_honort = "aas_honortargets"
c_abilituse = "aas_abilityuse"
c_abilit = "aas_ability"
c_meleemode = "aas_meleemode"

auto_follow = False
lastHonored = 0
enabled = False
honorTargets = True
newTarget = False
enableAbility = True
ability = True # True = primary, False = secondary
meleeMode = False
lastGroup = 0
status_label = None
status_text = "Paused..."

def load_settings():
    global auto_follow, honorTargets, enableAbility, ability, meleeMode
    af = API.GetPersistentVar(c_afollowsave, "False", API.PersistentVar.Char)
    if af == "True":
        auto_follow = True
    
    ht = API.GetPersistentVar(c_honort, "True", API.PersistentVar.Char)
    if ht == "False":
        honorTargets = False
    
    ub = API.GetPersistentVar(c_abilituse, "True", API.PersistentVar.Char)
    if ub == "False":
        enableAbility = False
    
    ab = API.GetPersistentVar(c_abilit, "True", API.PersistentVar.Char)
    if ab == "False":
        ability = False

    mm = API.GetPersistentVar(c_meleemode, "False", API.PersistentVar.Char)
    if mm == "True":
        meleeMode = True

def save_settings():
    global auto_follow, honorTargets, enableAbility, ability, meleeMode
    API.SavePersistentVar(c_afollowsave, "True" if auto_follow else "False", API.PersistentVar.Char)
    API.SavePersistentVar(c_honort, "True" if honorTargets else "False", API.PersistentVar.Char)
    API.SavePersistentVar(c_abilituse, "True" if enableAbility else "False", API.PersistentVar.Char)
    API.SavePersistentVar(c_abilit, "True" if ability else "False", API.PersistentVar.Char)
    API.SavePersistentVar(c_meleemode, "True" if meleeMode else "False", API.PersistentVar.Char)

def set_status(text):
    global status_label, status_text
    update_label = status_text != text
    status_text = text

    if update_label and status_label:
        status_label.SetText(status_text)

def stop():
    API.SavePersistentVar("AAXY", f"{gump.GetX()},{gump.GetY()}", API.PersistentVar.Char)
    save_settings()
    API.DisplayRange(0)
    gump.Dispose()
    API.SetWarMode(False)
    API.Stop()

def enable_follow():
    global auto_follow
    auto_follow = True
    save_settings()
    
def disable_follow():
    global auto_follow
    auto_follow = False
    save_settings()

def enable_honor():
    global honorTargets
    honorTargets = True
    save_settings()

def disable_honor():
    global honorTargets
    honorTargets = False
    save_settings()

def enable_ability():
    global enableAbility
    enableAbility = True
    save_settings()

def disable_ability():
    global enableAbility
    enableAbility = False
    save_settings()

def enable_melee():
    global meleeMode
    meleeMode = True
    save_settings()

def disable_melee():
    global meleeMode
    meleeMode = False
    save_settings()

def enable_primary():
    global ability
    ability = True
    save_settings()

def enable_secondary():
    global ability
    ability = False
    save_settings()

def pause():
    global enabled
    enabled = not enabled
    playbutton.SetText("[PLAYING]" if enabled else "[PAUSED]")
    playbutton.SetBackgroundHue(172 if enabled else 53)
    set_status("Playing" if enabled else "Paused")
    API.DisplayRange(0)
    API.SetWarMode(enabled)

def Honor(mob):
    global lastHonored
    if mob:
        if API.HasTarget():
            return
        
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
    if API.Player.ManaDiff < 10:
        if ability and not API.PrimaryAbilityActive():
            API.ToggleAbility("primary")
        else:
            if not ability and not API.SecondaryAbilityActive():
                API.ToggleAbility("secondary")

def createEnableDisable(text, onEnable, onDisable, gump, x, y, firstChecked, buttonTxt="Enable", button2Txt="Disable"):
    global lastGroup
    label = API.Gumps.CreateGumpTTFLabel(text, 16, "#FFFFFF", aligned="right", maxWidth=98)
    label.SetPos(x, y)
    gump.Add(label)

    button = API.Gumps.CreateGumpRadioButton(buttonTxt, lastGroup)
    button.IsChecked = firstChecked
    button.SetRect(x + 100, y, 100, 50)
    API.Gumps.AddControlOnClick(button, onEnable)
    gump.Add(button)

    button2 = API.Gumps.CreateGumpRadioButton(button2Txt, lastGroup)
    button2.IsChecked = not firstChecked
    button2.SetRect(x + 200, y, 100, 50)
    API.Gumps.AddControlOnClick(button2, onDisable)
    gump.Add(button2)
    lastGroup += 1

load_settings()

gump = API.Gumps.CreateGump()
savedX = API.GetPersistentVar("AAXY", "100,100", API.PersistentVar.Char)
split = savedX.split(',')

gheight = 225

gump.SetRect(int(split[0]), int(split[1]), 400, gheight)
bg = API.Gumps.CreateGumpColorBox(0.7, "#212121").SetRect(0, 0, 400, gheight)
gump.Add(bg)
label = API.Gumps.CreateGumpTTFLabel("AutoAttack Script", 24, "#FF8800", aligned="center", maxWidth=400)
gump.Add(label)

status_label = API.Gumps.CreateGumpTTFLabel(status_text, 14, "#00FFFF", aligned="center", maxWidth=400)
status_label.SetPos(0, 25)
gump.Add(status_label)

lasty = 50
createEnableDisable("Melee Mode", enable_melee, disable_melee, gump, 25, lasty, meleeMode)
lasty = lasty + 25
createEnableDisable("Auto Follow", enable_follow, disable_follow, gump, 25, lasty, auto_follow)
lasty = lasty + 25
createEnableDisable("Honor Targets", enable_honor, disable_honor, gump, 25, lasty, honorTargets)
lasty = lasty + 25
createEnableDisable("Use Abilities", enable_ability, disable_ability, gump, 25, lasty, enableAbility)
lasty = lasty + 25
createEnableDisable(" |_____", enable_primary, enable_secondary, gump, 25, lasty, ability, "Primary", "Secondary")
lasty = lasty + 25

stopbutton = API.Gumps.CreateSimpleButton("[STOP]", 100, 25)
stopbutton.SetPos(100, lasty)
stopbutton.SetBackgroundHue(32)
gump.Add(stopbutton)
API.Gumps.AddControlOnClick(stopbutton, stop)

playbutton = API.Gumps.CreateSimpleButton("[PAUSED]", 100, 25)
playbutton.SetBackgroundHue(53)
playbutton.SetPos(200, lasty)
gump.Add(playbutton)
API.Gumps.AddControlOnClick(playbutton, pause)
lasty = lasty + 25

targButton = API.Gumps.CreateSimpleButton("[NEW TARGET]", 100, 25)
targButton.SetPos(150, lasty)
targButton.SetBackgroundHue(12)
gump.Add(targButton)
API.Gumps.AddControlOnClick(targButton, new_target)

API.Gumps.AddGump(gump)

Player = API.Player
while True:
    API.ProcessCallbacks()
    if not enabled:
        API.Pause(0.5)
        continue

    dist = (MAX_DISTANCE if not meleeMode else 1)

    if SHOW_RADIUS_INDICATOR:
        API.DisplayRange(dist, 32)    
    enemy = API.NearestMobile([API.Notoriety.Gray, API.Notoriety.Criminal, API.Notoriety.Murderer], dist)

    if enemy:
        enemy_serial = enemy.Serial
        set_status(f"Enemy found.. {enemy.Name}")
        if SHOW_RADIUS_INDICATOR:
            API.DisplayRange(0)

        if auto_follow:
            API.AutoFollow(enemy)

        while enemy and not enemy.IsDead:
            if not enabled or enemy.Distance > dist:
                break
            if newTarget:
                newTarget = False
                enemy = None
                set_status("Selecting new target..")
                API.Pause(0.1)
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
    else:
        set_status("Searching...")
    API.Pause(0.5)
