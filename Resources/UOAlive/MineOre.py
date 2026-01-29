import API
"""
Champion City Code's Mining Bot
Version: 1.0.0
Last Updated: 2026-01-29

Controls:
- Start/Stop via an in-game gump (Enable/Disable button).
- Auto-targets mineable land/static tiles within 1 tile of the player.
- Mines repeatedly, handles depleted nodes, and prompts to move.
- Detects tool breakage and switches to the next tool.
- Manages weight: drops ore by priority, smelts at nearby forges.
- Smelts ore types in backpack (with min-stack rules for 0x19B7).
"""

# Journal messages that indicate the node is empty on most UO shards.
ORE_DEPLETED_TEXTS = [
    "There is no metal here to mine.",
    "You dig up no usable ore.",
    "The vein is depleted.",
    "You can't mine there.",
    "Target cannot be seen.",
]
TOOL_WORN_TEXTS = [
    "You have worn out your tool!",
]

SHOVEL_GRAPHIC = 0x0F39  # Set this to your shovel's item id (graphic).
PICKAXE_GRAPHIC = 0x0E86  # Set this to your pickaxe item id (graphic).
ORE_GRAPHICS = [0x19B9, 0x19B8, 0x19BA]  # UOAlive ore graphics; add/remove as needed.
ORE_GRAPHIC_MIN2 = 0x19B7  # Only smelt if stack size >= 2.
DROP_PRIORITY = [0x19B7, 0x19BA, 0x19B8, 0x19B9]
FORGE_GRAPHICS = [0x0FB1, 0x0E58]  # Common forge graphic; add/remove as needed.
FORGE_RANGE = 2
DEBUG_STATICS = False
DEBUG_STATICS_LIMIT = 20
DEBUG_SMELT = False
AUTO_TARGET_MINE = True
HEADMSG_HUE = 1285  # Purple hue for overhead messages.
RUNNING = False
CONTROL_GUMP = None
CONTROL_BUTTON = None
MINEABLE_LAND_GRAPHICS = [
    0x00DC, 0x00DD, 0x00DE, 0x00DF, 0x00E0, 0x00E1, 0x00E2, 0x00E3, 0x00E4, 0x00E5,
    0x00E6, 0x00E7, 0x00E8, 0x00E9, 0x00EA, 0x00EB, 0x00EC, 0x00ED, 0x00EE, 0x00EF,
    0x00F0, 0x00F1, 0x00F2, 0x00F3, 0x00F4, 0x00F6, 0x00F7, 0x010C, 0x010D, 0x010E,
    0x010F, 0x0110, 0x0111, 0x0112, 0x0113, 0x0114, 0x0115, 0x0116, 0x0117, 0x01AF,
    0x01B0, 0x01D3, 0x01D4, 0x01D5, 0x01D6, 0x01D7, 0x01D8, 0x01DA, 0x01DC, 0x01DD,
    0x01DE, 0x01DF, 0x01E0, 0x01E1, 0x01E2, 0x01E3, 0x01EC, 0x01ED, 0x01EE, 0x01EF,
    0x022C, 0x022D, 0x022E, 0x022F, 0x0230, 0x0231, 0x0232, 0x0233, 0x0234, 0x0235,
    0x0236, 0x0237, 0x0238, 0x0239, 0x023A, 0x023B, 0x023C, 0x023D, 0x023E, 0x023F,
    0x0240, 0x0241, 0x0242, 0x0243, 0x0245, 0x0246, 0x0247, 0x0248, 0x0249, 0x024A,
    0x024B, 0x024C, 0x024D, 0x024E, 0x024F, 0x0250, 0x0251, 0x0252, 0x0253, 0x0254,
    0x0255, 0x0256, 0x0257, 0x0258, 0x0259, 0x025A, 0x025B, 0x025C, 0x025D, 0x025E,
    0x025F, 0x0260, 0x0261, 0x0262, 0x0263, 0x0264, 0x0265, 0x0266, 0x026B, 0x026C,
    0x026D, 0x02BC, 0x02BD, 0x02BE, 0x02BF, 0x02C0, 0x02C1, 0x02C2, 0x02C3, 0x02C4,
    0x02C5, 0x02C6, 0x02C7, 0x02C8, 0x02C9, 0x02CA, 0x02CB, 0x0623, 0x0624, 0x0625,
    0x0626, 0x0627, 0x0628, 0x0629, 0x062A, 0x062B, 0x062F, 0x0630, 0x0631, 0x0632,
    0x0633, 0x0634, 0x0635, 0x0636, 0x0637, 0x0638, 0x0639, 0x063A, 0x063B, 0x063C,
    0x063D, 0x063E, 0x08C1, 0x08C2, 0x08C3, 0x08C4, 0x08C5, 0x086C, 0x0AE9, 0x0AEA,
    0x0AEB, 0x0AEC, 0x0AED, 0x0AEE, 0x0AEF, 0x0AF0, 0x0AF1, 0x0AF2, 0x0AF3, 0x0AF4,
]  # UOAlive mineable land tiles.
MINEABLE_STATIC_GRAPHICS = []  # TODO: add static rock/mountain ids that are mineable.
SMELT_SUCCESS_TEXTS = [
    "You smelt the ore into ingots",
]
SMELT_FAIL_TEXTS = [
    "That is too far away",
    "You can't smelt",
    "You cannot smelt",
    "You must be near",
]

def _find_ore_in_backpack():
    # Find the next smeltable ore in the backpack, honoring special min-stack rules.
    # Special case: only smelt 0x19B7 when stack is 2+ (check recursively).
    items = API.ItemsInContainer(API.Backpack, True)
    if items:
        for item in items:
            if item.Graphic == ORE_GRAPHIC_MIN2 and int(item.Amount) >= 2:
                return item
    for graphic in ORE_GRAPHICS:
        ore = API.FindType(graphic, API.Backpack)
        if ore:
            return ore
    return None

def _find_item_by_graphic(graphic):
    # Return the first item in the backpack (recursive) matching the graphic.
    items = API.ItemsInContainer(API.Backpack, True)
    if not items:
        return None
    for item in items:
        if item.Graphic == graphic:
            return item
    return None

def _toggle_running():
    # Toggle the main run state and refresh the gump button text.
    global RUNNING
    RUNNING = not RUNNING
    state = "ON" if RUNNING else "OFF"
    API.SysMsg(f"Mining: {state}")
    _update_control_gump()

def _update_control_gump():
    # Refresh the gump button label to reflect current run state.
    if not CONTROL_BUTTON:
        return
    CONTROL_BUTTON.Text = "Disable" if RUNNING else "Enable"

def _pause_if_needed():
    # Block execution while paused, still processing gump callbacks.
    while not RUNNING:
        API.ProcessCallbacks()
        API.Pause(0.1)

def _sleep(seconds):
    # Pause in small steps so the pause button is responsive.
    elapsed = 0.0
    step = 0.1
    while elapsed < seconds:
        _pause_if_needed()
        API.ProcessCallbacks()
        API.Pause(step)
        elapsed += step

def _wait_for_target(seconds):
    # Wait for a target cursor while respecting pause state.
    elapsed = 0.0
    step = 0.1
    while elapsed < seconds:
        _pause_if_needed()
        if API.HasTarget():
            return True
        API.Pause(step)
        elapsed += step
    return False

def _create_control_gump():
    # Build the in-game gump for enabling/disabling the script.
    global CONTROL_GUMP, CONTROL_BUTTON
    if CONTROL_GUMP:
        return
    g = API.CreateGump(True, True, True)
    g.SetRect(100, 100, 180, 70)
    bg = API.CreateGumpColorBox(0.7, "#1B1B1B")
    bg.SetRect(0, 0, 180, 70)
    g.Add(bg)

    label = API.CreateGumpTTFLabel("Mining Bot Controller", 16, "#FFFFFF", "alagard", "center", 180)
    label.SetPos(0, 6)
    g.Add(label)

    button = API.CreateSimpleButton("Enable", 100, 20)
    button.SetPos(40, 35)
    g.Add(button)
    API.AddControlOnClick(button, _toggle_running)
    CONTROL_BUTTON = button

    API.AddGump(g)
    CONTROL_GUMP = g
    _update_control_gump()

def _drop_overweight_ore():
    # Drop ore by priority until weight is under max.
    while API.Player.Weight > API.Player.WeightMax:
        _pause_if_needed()
        dropped = False
        for graphic in DROP_PRIORITY:
            item = _find_item_by_graphic(graphic)
            if item:
                API.MoveItemOffset(item.Serial, 1, 0, 1, 0)
                _sleep(0.5)
                dropped = True
                break
        if not dropped:
            break

def _find_static_forge():
    # Scan nearby statics for a forge graphic and return the closest match.
    x = int(API.Player.X)
    y = int(API.Player.Y)
    statics = API.GetStaticsInArea(x - FORGE_RANGE, y - FORGE_RANGE, x + FORGE_RANGE, y + FORGE_RANGE) or []
    # Some shards report statics inconsistently; fallback to per-tile scan.
    if not statics:
        for tx in range(x - FORGE_RANGE, x + FORGE_RANGE + 1):
            for ty in range(y - FORGE_RANGE, y + FORGE_RANGE + 1):
                tile_statics = API.GetStaticsAt(tx, ty)
                if tile_statics:
                    statics.extend(tile_statics)
    if not statics:
        return None
    if DEBUG_STATICS:
        shown = 0
        for s in statics:
            API.SysMsg(f"Static: 0x{int(s.Graphic):04X} at {int(s.X)},{int(s.Y)} z{int(s.Z)}")
            shown += 1
            if shown >= DEBUG_STATICS_LIMIT:
                break
    best = None
    best_dist = 999999
    for s in statics:
        if s.Graphic not in FORGE_GRAPHICS:
            continue
        dx = int(s.X) - x
        dy = int(s.Y) - y
        dist = (dx * dx) + (dy * dy)
        if dist < best_dist:
            best = s
            best_dist = dist
    return best

def _find_item_forge():
    # Scan nearby ground items for a forge graphic.
    items = API.GetItemsOnGround(FORGE_RANGE)
    if not items:
        return None
    for item in items:
        if item.Graphic in FORGE_GRAPHICS:
            return item
    return None

def _find_forge():
    # Prefer static forge; fallback to item forge.
    static_forge = _find_static_forge()
    if static_forge:
        return ("static", static_forge)
    item_forge = _find_item_forge()
    if item_forge:
        return ("item", item_forge)
    return (None, None)

def _smelt_ore():
    # Smelt all eligible ore in the backpack at the nearest forge.
    if DEBUG_SMELT:
        API.SysMsg("Smelt: starting...")
    forge_type, forge = _find_forge()
    while not forge:
        _pause_if_needed()
        API.HeadMsg("No forge nearby. Move closer...", API.Player, HEADMSG_HUE)
        _sleep(2.0)
        forge_type, forge = _find_forge()
    # Cache a forge item serial if possible; targeting items tends to be more reliable than statics.
    forge_item = _find_item_forge()
    while True:
        _pause_if_needed()
        ore = _find_ore_in_backpack()
        if not ore:
            if DEBUG_SMELT:
                API.SysMsg("Smelt: no ore found in backpack.")
            break
        if DEBUG_SMELT:
            API.SysMsg(f"Smelt ore: 0x{int(ore.Graphic):04X} serial {int(ore.Serial)}")
        API.ClearJournal()
        API.UseObject(ore.Serial)
        _sleep(0.2)
        got_target = _wait_for_target(2)
        if not got_target:
            # Fallback: use by graphic from backpack in case serial use fails.
            try:
                API.UseType(int(ore.Graphic), 1337, API.Backpack)
            except Exception:
                pass
            got_target = _wait_for_target(2)
        if got_target:
            for _ in range(3):
                if forge_item:
                    API.Target(forge_item.Serial)
                elif forge_type == "static":
                    API.Target(int(forge.X), int(forge.Y), int(forge.Z), int(forge.Graphic))
                else:
                    API.Target(forge.Serial)
                _sleep(0.2)
                if not API.HasTarget():
                    break
            _sleep(0.8)
            if DEBUG_SMELT and API.InJournalAny(SMELT_SUCCESS_TEXTS, True):
                API.SysMsg("Smelt: success message detected.")
        else:
            if DEBUG_SMELT:
                API.SysMsg("Smelt: no target cursor received (ore -> forge).")
            # Alternate flow: use forge then target ore.
            API.ClearJournal()
            if forge_item:
                API.UseObject(forge_item.Serial)
            elif forge_type == "static":
                API.Target(int(forge.X), int(forge.Y), int(forge.Z), int(forge.Graphic))
            else:
                API.UseObject(forge.Serial)
            _sleep(0.2)
            if _wait_for_target(2):
                for _ in range(3):
                    API.Target(ore.Serial)
                    _sleep(0.2)
                    if not API.HasTarget():
                        break
            elif DEBUG_SMELT:
                API.SysMsg("Smelt: no target cursor received (forge -> ore).")
        # Smelt cooldown to reduce spam.
        _sleep(1.2)

def _find_mineable_tile_nearby():
    # Find a mineable land or static tile in a 3x3 area around the player.
    px = int(API.Player.X)
    py = int(API.Player.Y)
    # Check the tile at feet and 8 surrounding tiles.
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            tx = px + dx
            ty = py + dy
            tile = API.GetTile(tx, ty)
            if tile and tile.Graphic in MINEABLE_LAND_GRAPHICS:
                return (tx, ty, int(tile.Z), int(tile.Graphic), True)
            statics = API.GetStaticsAt(tx, ty)
            if statics:
                for s in statics:
                    if s.Graphic in MINEABLE_STATIC_GRAPHICS:
                        return (int(s.X), int(s.Y), int(s.Z), int(s.Graphic), False)
    return None

def _retarget_mine_tile():
    # Select a new mining target (auto or manual depending on settings).
    global x, y, z, tile_graphic, tile_is_land
    if AUTO_TARGET_MINE:
        while True:
            _pause_if_needed()
            found = _find_mineable_tile_nearby()
            if found:
                x, y, z, tile_graphic, tile_is_land = found
                return
            API.HeadMsg("Ore Depleted Move...", API.Player, HEADMSG_HUE)
            _sleep(3)
    API.SysMsg("Target a new ore tile/rock.")
    API.RequestTarget()
    tile_pos = API.LastTargetPos
    if not tile_pos:
        API.SysMsg("No mining tile targeted. Stopping.")
        API.Stop()
    x = int(tile_pos.X)
    y = int(tile_pos.Y)
    z = int(tile_pos.Z)
    tile_graphic = API.LastTargetGraphic
    tile_is_land = False

_create_control_gump()

MineTools = API.FindType(PICKAXE_GRAPHIC, API.Backpack) or API.FindType(SHOVEL_GRAPHIC, API.Backpack)
if not MineTools:
    API.HeadMsg("You are out of mining equipment.", API.Player, HEADMSG_HUE)
    API.Stop()

API.HeadMsg(
    "Welcome to Champion City Code's Mining Bot. To begin mining press the Enable button on the Mining Bot Controller gump.",
    API.Player,
    HEADMSG_HUE,
)
_pause_if_needed()
_retarget_mine_tile()
API.SysMsg("Mining started...")

while True:
    API.ProcessCallbacks()
    _pause_if_needed()

    if API.Player.Weight > API.Player.WeightMax:
        _drop_overweight_ore()

    if API.Player.Weight >= (API.Player.WeightMax - 15):
        API.HeadMsg("Overweight: smelting ore.", API.Player, HEADMSG_HUE)
        _smelt_ore()
        _retarget_mine_tile()

    if AUTO_TARGET_MINE:
        found = _find_mineable_tile_nearby()
        if not found:
            API.HeadMsg("Ore Depleted Move...", API.Player, HEADMSG_HUE)
            _sleep(3)
            continue
        x, y, z, tile_graphic, tile_is_land = found

    API.ClearJournal()
    API.UseObject(MineTools)

    if _wait_for_target(5):
        if tile_is_land:
            dx = int(x) - int(API.Player.X)
            dy = int(y) - int(API.Player.Y)
            API.TargetLandRel(dx, dy)
        elif tile_graphic and int(tile_graphic) != 1337:
            API.Target(x, y, z, int(tile_graphic))
        else:
            API.Target(x, y, z)

    # Give the server time to respond with journal feedback.
    _sleep(2.2)

    if API.InJournalAny(TOOL_WORN_TEXTS, True):
        MineTools = API.FindType(PICKAXE_GRAPHIC, API.Backpack) or API.FindType(SHOVEL_GRAPHIC, API.Backpack)
        if not MineTools:
            API.HeadMsg("Out of Tools Fool!", API.Player, HEADMSG_HUE)
            API.Stop()

    if API.InJournalAny(ORE_DEPLETED_TEXTS, True):
        API.HeadMsg("Ore Depleted Move...", API.Player, HEADMSG_HUE)
        _sleep(3)
        API.SysMsg("Target a new ore tile/rock.")
        API.RequestTarget()
        tile_pos = API.LastTargetPos
        if not tile_pos:
            API.SysMsg("No mining tile targeted. Stopping.")
            API.Stop()
        x = int(tile_pos.X)
        y = int(tile_pos.Y)
        z = int(tile_pos.Z)
        tile_graphic = API.LastTargetGraphic
