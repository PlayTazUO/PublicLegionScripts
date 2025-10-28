import API

if API.HasTarget('beneficial'):
    API.Stop()
elif API.HasTarget('any'):
    API.CancelTarget()

player = API.Player
backpack = API.Backpack

useChivalry = API.GetSkill("Chivalry").Value >= 30
useMagery = API.GetSkill("Magery").Value >= 30
useBandages = API.GetSkill("Healing").Value > 30

chivalrySpell = None
magerySpell = None

dmg = player.HitsDiff

if useChivalry:
    if player.IsPoisoned:
        chivalrySpell = "Cleanse by Fire"
    else:
        chivalrySpell = "Close Wounds"

if useMagery:
    if player.IsPoisoned:
        magerySpell = "Cure"
    elif dmg >5 and dmg <= 15:
        magerySpell = "Heal"
    else:
        magerySpell = "Greater Heal"

if dmg > 5:
    API.PreTarget(player.Serial, "beneficial")

if useBandages:
    API.HeadMsg("Who do you want to bandage?", player, 66)
    API.UseObject(API.FindType(0x0E21, backpack))
elif useChivalry and chivalrySpell is not None:
    API.CastSpell(chivalrySpell)
elif useMagery and magerySpell is not None:
    API.CastSpell(magerySpell)
