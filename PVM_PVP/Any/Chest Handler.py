# This will let you target a chest, move to it, unlock and untrap it, open it and use autoloot on it.

import API

PICKS = 5372
SUCCESS_LOCKPICKING = ["The lock quickly yields", "This does not appear to be locked"]
SUCCESS_REMOVE_TRAP = ["You successfully render the trap", "That doesn't appear to be trapped"]

def Unlock(what):
    if API.FindType(PICKS, API.Backpack):
        API.UseObject(API.Found)
        API.WaitForTarget()
        API.Target(what)
        API.Pause(3)
        if not API.InJournalAny(SUCCESS_LOCKPICKING):
            API.Pause(9)
            Unlock(what) 

def UnTrap(what):
    API.UseSkill("Remove Trap")
    API.WaitForTarget()
    API.Target(what)
    API.Pause(3)
    if not API.InJournalAny(SUCCESS_REMOVE_TRAP):
        API.Pause(9)
        UnTrap(what)
    pass

player = API.Player

API.HeadMsg("Target a chest to open and loot", player)
targ = API.RequestTarget()

if targ:
    item = API.FindItem(targ)
    if item and item.Distance > 1:
        API.Pathfind(item.X, item.Y, item.Z, 1)
        while API.Pathfinding():
            API.Pause(0.1)
    Unlock(targ)
    UnTrap(targ)
    API.UseObject(targ)
    API.Pause(1)
    API.AutoLootContainer(targ)