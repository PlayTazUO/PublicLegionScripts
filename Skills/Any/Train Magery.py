import API
import time
# See examples at
#   https://github.com/bittiez/PublicLegionScripts/
# Or documentation at
#   https://github.com/bittiez/TazUO/wiki/TazUO.Legion-Scripting

# Converted from: https://github.com/matsamilla/Razor-Enhanced/blob/master/Skills/train_Magery.py

# --- SETTINGS ---
resistTrain = True # Use spells that will train your resist
useMeditation = False
meditationDelay = 10 # Delay between meditation uses
useSpiritSpeak = True # Use Spirit Speak to heal
# --- END SETTINGS ---


Player = API.Player
Magery = API.GetSkill("Magery")

def minSkillCheck():
    if Magery.Value < 35:
        API.HeadMsg('Train magery from a vendor first', Player)
        API.Stop()
        
def manaCheck():
    nextMeditation = time.time()
    
    if Player.Mana < 40:
        while Player.Mana < Player.ManaMax:
            label.SetText("Status: Regenerating mana...")
            if (not API.BuffExists('Meditation') and useMeditation and time.time() >= nextMeditation):
                API.UseSkill('Meditation')
                nextMeditation = time.time() + meditationDelay
            API.Pause(0.2)

def trainMage():
    while Player.HitsDiff > 15:
        label.SetText("Status: Healing...")
        if useSpiritSpeak and Player.ManaDiff < 10:
            API.UseSkill('Spirit Speak')
            API.Pause(5)
        API.Pause(0.2)
    
    minSkillCheck()

    label.SetText("Status: Casting...")
    
    if Magery.Value < 60:
        API.CastSpell('Mind Blast')
        spell.SetText("Casting Mind Blast")
    elif Magery.Value < 85:
        API.CastSpell('Energy Bolt')
        spell.SetText("Casting Energy Bolt")
    elif Magery.Value < 100:
        API.CastSpell("Flamestrike")
        spell.SetText("Casting Flamestrike")

    API.WaitForTarget()
    API.TargetSelf()
    mageval.SetText(f"Magery: {Magery.Value}")
    API.Pause(2.5)
    manaCheck()
    

def trainMageryNoResist():
    minSkillCheck()
    
    label.SetText("Status: Casting...")

    if Magery.Value < 55:
        API.CastSpell('Mana Drain')
        spell.SetText("Casting Mana Drain")
    elif Magery.Value < 75:
        API.CastSpell('Invisibility')
        spell.SetText("Casting Invisibility")
    elif Magery.Value < 100:
        API.CastSpell('Mana Vampire')
        spell.SetText("Casting Mana Vampire")

    API.WaitForTarget()
    API.TargetSelf()
    mageval.SetText(f"Magery: {Magery.Value}")
    API.Pause(2.5)  
    manaCheck()

gump = API.CreateGump()
gump.SetRect(100, 100, 400, 100)
bg = API.CreateGumpColorBox(0.7, "#212121")
bg.SetRect(0, 0, 400, 100)
gump.Add(bg)

label = API.CreateGumpTTFLabel("", 24, "#FF8800", aligned="center", maxWidth=400)
gump.Add(label)
API.AddGump(gump)

spell = API.CreateGumpTTFLabel("Training Magery...", 24, "#FF8800", aligned="center", maxWidth=400)
spell.SetY(35)
gump.Add(spell)

mageval = API.CreateGumpTTFLabel(f"Magery: {Magery.Value}", 24, "#FF8800", aligned="center", maxWidth=400)
mageval.SetY(70)
gump.Add(mageval)

gump.CenterXInViewPort()
gump.CenterYInViewPort()

while Magery.Value  < 100:
    if resistTrain:
        trainMage()
    else:       
        trainMageryNoResist()
API.HeadMsg("You GMed magery!", Player)
