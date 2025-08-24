# See examples at
#   https://github.com/PlayTazUO/PublicLegionScripts/
# Or documentation at
#   https://github.com/PlayTazUO/TazUO/wiki/TazUO.Legion-Scripting

# A simple script to smelt ores at a forge

import API

ORES = [6585]

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
