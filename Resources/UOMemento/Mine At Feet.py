# Just hit play! Or create a macro and click the button. Will use shovels or pickaxes to mine at your feet.

import API

tools = [0x0F39, 0x0E86]

tool = None
for t in tools:
    tool = API.FindType(t, API.Backpack)
    if tool:
        break
    tool = API.FindLayer("onehanded")
    if tool and tool.Graphic == t:
        break
    tool = API.FindLayer("twohanded")
    if tool and tool.Graphic == t:
        break

if not tool:
    API.Stop()
else:
    API.UseObject(tool)
    API.WaitForTarget()
    API.TargetLandRel(0, 0)
