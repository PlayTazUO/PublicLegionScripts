import API

class SpellEntry:
    graphic = None
    hotkey = None
    onCast = None
    def __init__(self, graphic, hotkey, onCast):
        self.graphic = graphic
        self.hotkey = hotkey
        self.onCast = onCast
        pass

# EDIT THINGS HERE
COLUMNS = 2

#Graphic, HotKey, On cast
SPELLS = [SpellEntry(0x1B58 - 0x1298, "CTRL+1", lambda: API.CastSpell("Clumsy")), 
          SpellEntry(0x1B58 - 0x1298, "CTRL+2", lambda: API.CastSpell("Greater Heal")), 
          SpellEntry(0x1B58 - 0x1298, "CTRL+3", lambda: API.CastSpell("Fireball")), ]

# STOP EDITING THINGS BELOW HERE
gump = None

def SetupHotkeys():
    for spell in SPELLS:
        API.OnHotKey(spell.hotkey, spell.onCast)

def CreateGump():
    global gump
    gump = API.Gumps.CreateGump()

    #For each spell, then after max columns, move to next column
    col = 0
    x = 0
    y = 0
    maxx = 0
    maxy = 0
    for spell in SPELLS:
        spellControl = API.Gumps.CreateGumpPic(spell.graphic, x, y)
        API.Gumps.AddControlOnClick(spellControl, spell.onCast)
        w = spellControl.GetWidth()
        h = spellControl.GetHeight()
        if maxx < w:
            maxx = w
        if maxy < h:
            maxy = h

        col+=1

        x += maxx

        if col >= COLUMNS:
            x = 0
            y += maxy
        
        gump.Add(spellControl)
    
    API.Gumps.AddGump(gump)

SetupHotkeys()
CreateGump()

while not API.StopRequested:
    API.Pause(0.5)
    API.ProcessCallbacks()
