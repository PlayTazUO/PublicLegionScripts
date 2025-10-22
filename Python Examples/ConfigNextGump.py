import API

# This demonstrates the use of ConfigNextGump

testObj = 1073748526 #Hammer for crafting gump
DELAY = 2

API.ConfigNextGump() #Ensure it's reset

API.SysMsg("Testing location...")
API.ConfigNextGump(x=400, y=400)
API.UseObject(testObj)

API.Pause(DELAY)
API.CloseGump()

API.SysMsg("Testing invis...")
API.ConfigNextGump(isVisible=False)
API.UseObject(testObj)

API.Pause(DELAY)
API.SysMsg("Invis gump exists!" if API.HasGump() else "No gump", 63)
API.CloseGump()

API.SysMsg("Testing auto close...")
API.ConfigNextGump(autoClose=True)
API.UseObject(testObj)

API.Pause(DELAY)
API.CloseGump()

API.SysMsg("Testing auto reply...")
API.ConfigNextGump(autoRespondButton=1)
API.UseObject(testObj)
