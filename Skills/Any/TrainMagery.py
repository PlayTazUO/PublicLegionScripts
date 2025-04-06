import API
import time
# See examples at
#   https://github.com/bittiez/PublicLegionScripts/
# Or documentation at
#   https://github.com/bittiez/TazUO/wiki/TazUO.Legion-Scripting

# Converted from: https://github.com/matsamilla/Razor-Enhanced/blob/master/Skills/train_Magery.py

# --- SETTINGS ---
resistTrain = True # Use spells that will train your resist
useMeditation = True
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
            if (not API.BuffExists('Meditation') and useMeditation and nextMeditation >= time.time()):
                API.UseSkill('Meditation')
                nextMeditation = time.time()
            API.Pause(0.2)

def trainMage():
    while Player.Hits < 45:
        API.Pause(0.2)
    
    minSkillCheck()
    
    if Magery.Value < 65:
        API.CastSpell('Mind Blast')
    elif Magery.Value < 85:
        API.CastSpell('Energy Bolt')
    elif Magery.Value < 100:
        API.CastSpell("Flamestrike")
        
    API.WaitForTarget()
    API.TargetSelf()
    API.Pause(2.5)
    manaCheck()
    

def trainMageryNoResist():
    minSkillCheck()
    
    if Magery.Value < 55:
        API.CastSpell('Mana Drain')
    elif Magery.Value < 75:
        API.CastSpell('Invisibility')
    elif Magery.Value < 100:
        API.CastSpell('Mana Vampire')
          
    API.WaitForTarget()
    API.TargetSelf()
    API.Pause(2.5)  
    manaCheck()

while Magery.Value  < 100:
    if resistTrain:
        trainMage()
    else:       
        trainMageryNoResist()
API.HeadMsg("You GMed magery!", Player)
