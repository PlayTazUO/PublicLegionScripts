# ======================================================================
#  GRID FISHER – LEGION VERSION WITH ADVANCED FISH CHOPPING
#  UOAlive Edition
# ======================================================================

# ---------------- CONFIG ----------------

# Grouped common fish entry (top)
commonFish = {
    "name": "common fish",
    "matchName": "fish",
    "ids": [0x09CC, 0x09CE, 0x09CD, 0x09CF],
    "color": 0x0000
}

# Specialty fish list (Amberjack color corrected)
specialFish = [
    {"name": "amberjack", "matchName": "amberjack", "id": 0x44C6, "color": 0x0842},
    {"name": "black seabass", "matchName": "black seabass", "id": 0x09CE, "color": 0x0000},
    {"name": "blue grouper", "matchName": "blue grouper", "id": 0x4306, "color": 0x07b3},
    {"name": "bluefish", "matchName": "bluefish", "id": 0x09CC, "color": 0x0000},
    {"name": "bonefish", "matchName": "bonefish", "id": 0x44C3, "color": 0x0000},
    {"name": "bonito", "matchName": "bonito", "id": 0x4303, "color": 0x0562},
    {"name": "cape cod", "matchName": "cape cod", "id": 0x4306, "color": 0x0000},
    {"name": "captain snook", "matchName": "captain snook", "id": 0x44C5, "color": 0x0845},
    {"name": "cobia", "matchName": "cobia", "id": 0x4303, "color": 0x055a},
    {"name": "crag snapper", "matchName": "crag snapper", "id": 0x44C4, "color": 0x0841},
    {"name": "cutthroat trout", "matchName": "cutthroat trout", "id": 0x4303, "color": 0x07bd},
    {"name": "darkfish", "matchName": "darkfish", "id": 0x4307, "color": 0x0497},
    {"name": "demon trout", "matchName": "demon trout", "id": 0x4302, "color": 0x05b5},
    {"name": "drake fish", "matchName": "drake fish", "id": 0x44C5, "color": 0x0852},
    {"name": "dungeon chub", "matchName": "dungeon chub", "id": 0x4306, "color": 0x0474},
    {"name": "gray snapper", "matchName": "gray snapper", "id": 0x4307, "color": 0x0000},
    {"name": "grim cisco", "matchName": "grim cisco", "id": 0x44C3, "color": 0x0000},
    {"name": "haddock", "matchName": "haddock", "id": 0x09CC, "color": 0x0000},
    {"name": "infernal tuna", "matchName": "infernal tuna", "id": 0x4307, "color": 0x0496},
    {"name": "lurker fish", "matchName": "lurker fish", "id": 0x09CE, "color": 0x0000},
    {"name": "mahi-mahi", "matchName": "mahi-mahi", "id": 0x44C6, "color": 0x0000},
    {"name": "orc bass", "matchName": "orc bass", "id": 0x09CC, "color": 0x0000},
    {"name": "red drum", "matchName": "red drum", "id": 0x4307, "color": 0x0485},
    {"name": "red grouper", "matchName": "red grouper", "id": 0x4307, "color": 0x0000},
    {"name": "red snook", "matchName": "red snook", "id": 0x09CD, "color": 0x0000},
    {"name": "shad", "matchName": "shad", "id": 0x4307, "color": 0x0a99},
    {"name": "snaggletooth bass", "matchName": "snaggletooth bass", "id": 0x09CF, "color": 0x0000},
    {"name": "tarpon", "matchName": "tarpon", "id": 0x44C3, "color": 0x0000},
    {"name": "tormented pike", "matchName": "tormented pike", "id": 0x44C3, "color": 0x0777},
    {"name": "yellowfin tuna", "matchName": "yellowfin tuna", "id": 0x44C4, "color": 0x084d},
]

# Combine with common fish at top, rest alphabetical
fishTypes = [commonFish] + sorted(specialFish, key=lambda f: f["name"])

# Shared variable keys
sharedFishChopperId = "fishChopper"
sharedFishingActive = "fishingActive"
sharedFishingStatus = "fishingStatus"
sharedFishPrefs = "fishChopPrefs"

# ---------------- INITIAL PREFS ----------------

if API.GetSharedVar(sharedFishPrefs) is None:
    prefs = {f["name"]: True for f in fishTypes}
    API.SetSharedVar(sharedFishPrefs, prefs)

# ---------------- HELPERS ----------------

def SetStatus(text):
    API.SetSharedVar(sharedFishingStatus, text)

def GetStatus():
    return API.GetSharedVar(sharedFishingStatus) or "Idle"

def IsFishing():
    return bool(API.GetSharedVar(sharedFishingActive))

def GetFishPrefs():
    return API.GetSharedVar(sharedFishPrefs)

def SaveFishPrefs(prefs):
    API.SetSharedVar(sharedFishPrefs, prefs)

def CountItemByID(itemID):
    return sum(item.Amount for item in API.ItemsInContainer(API.Backpack) if item.Graphic == itemID)

def CheckForPoleAndEquip():
    pole = API.FindType(0x0DC0, API.Backpack)
    if pole is None:
        return API.FindType(0x0DC0)
    API.EquipItem(pole.Serial)
    API.Pause(700)
    return pole

def GetGatherGridCoordinates():
    coords = []
    px, py, pz = API.Player.X, API.Player.Y, API.Player.Z
    offsets = [(-6,-6),(-6,0),(-6,6),(2,-6),(2,0),(2,6),(6,-6),(6,0),(6,6)]
    for dx, dy in offsets:
        coords.append({"x": px+dx, "y": py+dy, "z": pz})
    return coords

def ClearFishingJournal():
    API.ClearJournal()

def JournalContains(text):
    return API.InJournal(text, False)

def JournalContainsAny(listOfTexts):
    return API.InJournalAny(listOfTexts, False)

# ---------------- CHOP FISH ----------------

def ChopFish():
    prefs = GetFishPrefs()
    chopper_serial = API.GetSharedVar(sharedFishChopperId)
    if not chopper_serial:
        return

    if API.Player.Weight <= (API.Player.WeightMax * 0.3):
        return

    chopper = API.FindItem(int(chopper_serial))
    if not chopper:
        return

    for item in API.ItemsInContainer(API.Backpack):
        # Normalize name: handle "2 fish", "3 bonefish", etc.
        itemName = item.Name.lower().strip()
        parts = itemName.split(" ", 1)
        if parts[0].isdigit() and len(parts) > 1:
            itemName = parts[1]

        for f in fishTypes:

            # Grouped common fish: multiple IDs
            if "ids" in f:
                match = (
                    itemName == f["matchName"]
                    and item.Hue == f["color"]
                    and item.Graphic in f["ids"]
                )
            else:
                match = (
                    itemName == f["matchName"]
                    and item.Hue == f["color"]
                    and item.Graphic == f["id"]
                )

            if not match:
                continue

            if not prefs.get(f["name"], False):
                continue

            # PRE‑CHOP: clear stale cursor
            if API.HasTarget():
                API.CancelTarget()
                API.Pause(0.1)

            API.UseObject(chopper.Serial)

            if not API.WaitForTarget("any", 1.5):
                API.CancelTarget()
                API.Pause(0.15)
                API.UseObject(chopper.Serial)

                if not API.WaitForTarget("any", 1.5):
                    continue

            API.Target(item.Serial)
            API.Pause(1.2)

            # POST‑CHOP: clear cursor
            if API.HasTarget():
                API.CancelTarget()

            API.Pause(0.1)

# ---------------- FISHING LOGIC ----------------

def DoFishing():
    global castCounter

    SetStatus("Equipping pole...")

    pole = CheckForPoleAndEquip()
    if not pole:
        SetStatus("No pole")
        API.SetSharedVar(sharedFishingActive, False)
        return

    spots = GetGatherGridCoordinates()
    if not spots:
        SetStatus("No spots")
        API.SetSharedVar(sharedFishingActive, False)
        return

    SetStatus("Fishing...")
    API.Dismount()

    for spot in spots:
        API.ProcessCallbacks()
        if not IsFishing():
            break

        ClearFishingJournal()
        API.TrackingArrow(spot["x"], spot["y"])

        while not JournalContains("seem to be biting here."):
            API.ProcessCallbacks()
            if not IsFishing():
                break

            # Clear stale cursor
            if API.HasTarget():
                API.CancelTarget()

            # Cast
            API.UseObject(pole.Serial)
            if not API.WaitForTarget("any", 1.9):
                API.Pause(0.9)
                continue

            API.Target(spot["x"], spot["y"], spot["z"])
            API.Pause(0.9)

            # --- Every cast: update counters + refresh gump ---
            UpdateSessionCounters()
            RefreshGump()

            # Journal checks
            if JournalContainsAny(["cannot be seen.", "need to be closer"]):
                break

            # Chop fish after each cast
            ChopFish()

            # If still fishable, wait for bite
            if not JournalContains("seem to be biting here."):
                API.Pause(9.0)

    API.TrackingArrow(-1, -1)
    SetStatus("Complete")
    API.SetSharedVar(sharedFishingActive, False)

# ---------------- CONTROL GUMP ----------------

gump = None
lblStatus = None
castCounter = 0
fishCheckboxes = []
btnStart = None
btnStop = None

# Session counters (never decrease)
sessionMiBs = 0
sessionNets = 0
sessionTMaps = 0
sessionPearls = 0
sessionScales = 0

# Last-known backpack counts
lastMiBs = 0
lastNets = 0
lastTMaps = 0
lastPearls = 0
lastScales = 0

# Counter labels
lblMiBs = None
lblNets = None
lblTMaps = None
lblPearls = None
lblScales = None

GUMP_WIDTH = 540
GUMP_HEIGHT = 480


# --- Helper: detect new items entering backpack ---
def CountNewItems(itemID, lastCount):
    current = sum(item.Amount for item in API.ItemsInContainer(API.Backpack) if item.Graphic == itemID)
    gained = max(0, current - lastCount)
    return gained, current


# --- Update session counters (called every 5 casts) ---
def UpdateSessionCounters():
    global sessionMiBs, sessionNets, sessionTMaps, sessionPearls, sessionScales
    global lastMiBs, lastNets, lastTMaps, lastPearls, lastScales

    gained, lastMiBs = CountNewItems(0xA30C, lastMiBs)
    sessionMiBs += gained

    gained, lastNets = CountNewItems(0x0DCA, lastNets)
    sessionNets += gained

    gained, lastTMaps = CountNewItems(0x14EC, lastTMaps)
    sessionTMaps += gained

    gained, lastPearls = CountNewItems(0x3196, lastPearls)
    sessionPearls += gained

    gained, lastScales = CountNewItems(0x573A, lastScales)
    sessionScales += gained


def RefreshGump():
    global lblStatus, lblMiBs, lblNets, lblTMaps, lblPearls, lblScales

    if not gump or gump.IsDisposed:
        return

    # Status
    if lblStatus:
        lblStatus.Text = f"Status: {GetStatus()}"

    # Fish prefs / checkboxes
    prefs = GetFishPrefs()
    for chk, fishName in fishCheckboxes:
        chk.IsChecked = prefs.get(fishName, False)

    # Session counters (never decrease)
    if lblMiBs:
        lblMiBs.Text = f"MiBs: {sessionMiBs}"
    if lblNets:
        lblNets.Text = f"Nets: {sessionNets}"
    if lblTMaps:
        lblTMaps.Text = f"TMaps: {sessionTMaps}"
    if lblPearls:
        lblPearls.Text = f"Pearls: {sessionPearls}"
    if lblScales:
        lblScales.Text = f"Scales: {sessionScales}"


def BuildControlGump():
    global gump, lblStatus, fishCheckboxes, btnStart, btnStop
    global lblMiBs, lblNets, lblTMaps, lblPearls, lblScales

    if gump and not gump.IsDisposed:
        gump.Dispose()

    gump = API.CreateGump(True, True)
    gump.SetRect(100, 100, GUMP_WIDTH, GUMP_HEIGHT)

    bg = API.CreateGumpColorBox(0.65, "#202020")
    bg.SetRect(0, 0, GUMP_WIDTH, GUMP_HEIGHT)
    gump.Add(bg)

    title = API.CreateGumpTTFLabel("Grid Fisher", 20, "#FFD700")
    title.SetRect(10, 5, 300, 25)
    gump.Add(title)

    lblStatus = API.CreateGumpTTFLabel(f"Status: {GetStatus()}", 20, "#FFFFFF")
    lblStatus.SetRect(10, 35, 300, 20)
    gump.Add(lblStatus)

    btnStart = API.CreateSimpleButton("Start", 80, 25)
    btnStart.SetRect(10, 65, 80, 25)
    gump.Add(btnStart)

    def onStart():
        if not API.GetSharedVar(sharedFishChopperId):
            API.SysMsg("Target your fish chopper.", 44)
            targ = API.RequestTarget()
            if targ:
                API.SetSharedVar(sharedFishChopperId, targ)

        API.SetSharedVar(sharedFishingActive, True)
        SetStatus("Starting...")

    API.AddControlOnClick(btnStart, onStart)

    btnStop = API.CreateSimpleButton("Stop", 80, 25)
    btnStop.SetRect(110, 65, 80, 25)
    gump.Add(btnStop)

    def onStop():
        API.SetSharedVar(sharedFishingActive, False)
        SetStatus("Stopped")
        RefreshGump()

    API.AddControlOnClick(btnStop, onStop)

    btnAll = API.CreateSimpleButton("Chop All", 100, 25)
    btnAll.SetRect(10, 105, 100, 25)
    gump.Add(btnAll)

    def onChopAll():
        prefs = {f["name"]: True for f in fishTypes}
        SaveFishPrefs(prefs)
        RefreshGump()

    API.AddControlOnClick(btnAll, onChopAll)

    btnNone = API.CreateSimpleButton("Skip All", 100, 25)
    btnNone.SetRect(120, 105, 100, 25)
    gump.Add(btnNone)

    def onSkipAll():
        prefs = {f["name"]: False for f in fishTypes}
        SaveFishPrefs(prefs)
        RefreshGump()

    API.AddControlOnClick(btnNone, onSkipAll)

    # --- Resource Counters (Upper Right, vertical stack) ---
    counterX = GUMP_WIDTH - 160
    counterY = 35
    counterSpacing = 20

    lblMiBs = API.CreateGumpTTFLabel(f"MiBs: {sessionMiBs}", 20, "#FFFFFF")
    lblMiBs.SetRect(counterX, counterY + 0 * counterSpacing, 140, 20)
    gump.Add(lblMiBs)

    lblNets = API.CreateGumpTTFLabel(f"Nets: {sessionNets}", 20, "#FFFFFF")
    lblNets.SetRect(counterX, counterY + 1 * counterSpacing, 140, 20)
    gump.Add(lblNets)

    lblTMaps = API.CreateGumpTTFLabel(f"TMaps: {sessionTMaps}", 20, "#FFFFFF")
    lblTMaps.SetRect(counterX, counterY + 2 * counterSpacing, 140, 20)
    gump.Add(lblTMaps)

    lblPearls = API.CreateGumpTTFLabel(f"Pearls: {sessionPearls}", 20, "#FFFFFF")
    lblPearls.SetRect(counterX, counterY + 3 * counterSpacing, 140, 20)
    gump.Add(lblPearls)

    lblScales = API.CreateGumpTTFLabel(f"Scales: {sessionScales}", 20, "#FFFFFF")
    lblScales.SetRect(counterX, counterY + 4 * counterSpacing, 140, 20)
    gump.Add(lblScales)

    # Fish checkboxes
    fishCheckboxes.clear()
    colWidth = 170
    startX = 10
    startY = 145
    rowHeight = 22

    currentPrefs = GetFishPrefs()

    for index, f in enumerate(fishTypes):
        col = index % 3
        row = index // 3

        x = startX + col * colWidth
        y = startY + row * rowHeight

        chk = API.CreateGumpCheckbox("", 0, currentPrefs.get(f["name"], True))
        chk.SetRect(x, y, 20, 20)
        gump.Add(chk)

        lbl = API.CreateGumpTTFLabel(f["name"], 20, "#FFFFFF")
        lbl.SetRect(x + 22, y, colWidth - 22, 20)
        gump.Add(lbl)

        def makeHandler(fishName):
            def handler():
                prefs = GetFishPrefs()
                prefs[fishName] = not prefs.get(fishName, True)
                SaveFishPrefs(prefs)
                RefreshGump()
            return handler

        API.AddControlOnClick(chk, makeHandler(f["name"]))
        fishCheckboxes.append((chk, f["name"]))

    API.AddGump(gump)

# ---------------- MAIN LOOP ----------------

BuildControlGump()

while True:
    API.ProcessCallbacks()
    RefreshGump()

    if API.GetSharedVar(sharedFishingActive):
        SetStatus("Fishing...")
        DoFishing()
        API.SetSharedVar(sharedFishingActive, False)
        SetStatus("Complete")

    API.Pause(0.2)
