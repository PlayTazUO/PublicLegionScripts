# Just press play near some blue's

import time
import API

DELAY = 13

nextScan = time.time()
nextMsg = 0

beggedHash = set() 
beggedMobs = {}

class InfoGump:
    gump : API.ApiUiGump
    label : API.ApiUiTextBox

    def create(self):
        self.gump = API.Gumps.CreateModernGump(300, 300, 500, 40, False)
        self.label = API.Gumps.CreateGumpTTFLabel("Get close to a beggable target", 18, aligned="center", maxWidth=500)
        self.label.SetRect(10, 10, 500, 40)
        self.gump.Add(self.label)
        API.AddGump(self.gump)
    
    def update_status(self, text):
        self.label.Text = text

infoGump : InfoGump = InfoGump()
infoGump.create()


def beg(mob):
    global nextScan
    global beggedHash
    global beggedMobs
    global infoGump

    if time.time() < nextScan:
        return

    API.UseSkill("Begging")
    API.WaitForTarget()
    if API.HasTarget():
        API.Target(mob)
        nextScan = time.time() + DELAY
        beggedHash.add(mob.Serial)
        beggedMobs[mob.Serial] = time.time()
        mob.SetOutlineColor(None)


while not API.StopRequested:
    now = time.time()
    if time.time() >= nextScan:
        infoGump.update_status("Searching for rich clients...")
        mobs = API.NearestMobiles([API.Notoriety.Innocent], 15)
        sendMessages = False
        if nextMsg < now:
            sendMessages = True
            nextMsg = now + 3

        if mobs:
            for m in mobs:
                if m.Serial not in beggedHash:
                    if sendMessages:
                        API.HeadMsg("POTENTIAL TARGET", m.Serial, 32)
                        m.SetOutlineColor("#229933")
                    if m.Distance < 3:
                        beg(m)
                        break
                    else:
                        API.PathfindEntity(m, 2, True, 5)
                        beg(m)
                        break
    else:
        infoGump.update_status(f"Waiting {(nextScan - time.time()):.1f} more seconds to try again...")

    clear = time.time() - 60
    pop = []

    if beggedHash:
        for mobSerial, timestamp in beggedMobs.items():
            if timestamp < clear:
                pop.append(mobSerial)

        for mobSerial in pop:
            beggedMobs.pop(mobSerial)
            beggedHash.remove(mobSerial)

    API.Pause(0.5)
