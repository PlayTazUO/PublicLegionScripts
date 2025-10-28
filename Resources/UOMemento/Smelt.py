# See examples at
#   https://github.com/PlayTazUO/PublicLegionScripts/
# Or documentation at
#   https://github.com/PlayTazUO/TazUO/wiki/TazUO.Legion-Scripting
import API

ORES = [6585]
FORGES = [0x0FB1, 0x197E, 0x1982, 0x198A, 0x198E]

Forge = None
px = API.Player.X
py = API.Player.Y

stats = API.GetStaticsInArea(px - 2, py - 2, px + 2, py + 2)

if stats:
    for static in stats:
        if static.Graphic in FORGES:
            Forge = static
            break

if not Forge:
    API.HeadMsg("TARGET A FORGE", API.Player, 32)
    Forge = API.RequestAnyTarget()

if not Forge:
    API.HeadMsg("NO FORGE TARGETED", API.Player, 32)
    API.Stop()

for ore in ORES:
    if API.FindType(ore):
        API.UseObject(API.Found)
        API.WaitForTarget()
        API.Target(Forge.X, Forge.Y, Forge.Z, Forge.Graphic)
