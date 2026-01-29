import API

"""
Champion City Code's Butcher Bot
Version: 1.0.0
Last Updated: 2026-01-29

Features:
- In-game gump with Enable/Disable toggle and loot options menu.
- Scans nearby corpses, carves them with the best available tool (prefers Harvester's Blade).
- Auto-loots configurable resources/meats from carved corpses.
- Cuts hides in the backpack with scissors.
- Pauses when disabled but still processes gump callbacks.
"""

# --- Settings ---
SCAN_RANGE = 2
CARVE_TOOL_GRAPHICS = [
    0x2D20,  # harvesters blade
    0x0F52,  # dagger
    0x0EC4,  # skinning knife
    0x0EC3,  # butchers cleaver
    0x13F6,  # butchers knife
    0x13B6,  # butchers knife
]
SCISSORS_GRAPHICS = [
    0x0F9F,  # scissors
]

LOOT_LEATHER_GRAPHICS = [
    0x1081,  # leather
    0x1079,  # hide
]
LOOT_MEAT_GRAPHICS = [
    0x09F1,  # meat
    0x2DB9,  # rotworm meat
    0x09B9,  # poultry
    0x1609,  # lamb leg
]
LOOT_RESOURCE_GRAPHICS = [
    0x1BD1,  # feathers
    0x0DF8,  # wool
    0x26B4,  # dragonscale
    0x4077,  # dragonblood
]

PAUSE_SHORT = 0.2  # Small delay between quick actions (target/use).
PAUSE_CARVE = 1.0  # Delay before carving so auto-loot can process.
PAUSE_MOVE = 0.3  # Delay before moving items to backpack.
PAUSE_LOOT_SETTLE = 0.6  # Allow auto-loot to land items before cutting.

SEEN_CORPSES = set()
RUNNING = False
CONTROL_GUMP = None
CONTROL_BUTTON = None
OPTIONS_GUMP = None

LOOT_ITEM_CONFIG = {
    0x1079: {"name": "Hide", "enabled": True},
    0x1081: {"name": "Leather", "enabled": True},
    0x26B4: {"name": "Dragonscale", "enabled": True},
    0x4077: {"name": "Dragonblood", "enabled": True},
    0x09F1: {"name": "Meat", "enabled": True},
    0x09B9: {"name": "Poultry", "enabled": True},
    0x1609: {"name": "Lamb Leg", "enabled": True},
    0x1BD1: {"name": "Feathers", "enabled": True},
    0x0DF8: {"name": "Wool", "enabled": True},
    0x2DB9: {"name": "Rotworm Meat", "enabled": True},
}
LOOT_ITEM_ORDER = [
    0x1079,  # Hide
    0x1081,  # Leather
    0x26B4,  # Dragonscale
    0x4077,  # Dragonblood
    0x09F1,  # Meat
    0x09B9,  # Poultry
    0x1609,  # Lamb Leg
    0x2DB9,  # Rotworm Meat
    0x1BD1,  # Feathers
    0x0DF8,  # Wool
]


def _find_first_in_backpack(graphics):
    # Return the first item in backpack (recursive) matching any graphic.
    items = API.ItemsInContainer(API.Backpack, True)
    if not items:
        return None
    # Always prefer Harvester's Blade if we're searching for carving tools.
    if 0x2D20 in graphics:
        for item in items:
            if item.Graphic == 0x2D20:
                return item
    for item in items:
        if item.Graphic in graphics:
            return item
    return None


def _open_corpse(corpse):
    # Ensure the corpse is opened so items can be read.
    API.UseObject(corpse.Serial)
    API.Pause(PAUSE_SHORT)


def _carve_corpse(corpse):
    # Use a carving tool and target the corpse.
    tool = _find_first_in_backpack(CARVE_TOOL_GRAPHICS)
    if not tool:
        API.HeadMsg("No carving tool found.", API.Player)
        return False
    API.Pause(PAUSE_CARVE)
    API.UseObject(tool.Serial)
    if API.WaitForTarget("any", 2):
        API.Target(corpse.Serial)
        API.Pause(PAUSE_SHORT)
        return True
    return False


def _should_loot(graphic):
    config = LOOT_ITEM_CONFIG.get(graphic)
    if not config:
        return False
    return bool(config.get("enabled"))


def _loot_corpse_items(corpse):
    # Move configured resources/meats from corpse to backpack.
    _open_corpse(corpse)
    items = API.ItemsInContainer(corpse.Serial, True)
    if not items:
        return
    for item in items:
        if _should_loot(item.Graphic):
            API.Pause(PAUSE_MOVE)
            API.MoveItem(item.Serial, API.Backpack)


def _cut_leather_in_backpack():
    # Use scissors on each leather stack in backpack, run twice to catch late loot.
    scissors = _find_first_in_backpack(SCISSORS_GRAPHICS)
    if not scissors:
        return
    for _ in range(2):
        items = API.ItemsInContainer(API.Backpack, True)
        if not items:
            return
        for item in items:
            if item.Graphic in LOOT_LEATHER_GRAPHICS:
                API.UseObject(scissors.Serial)
                if API.WaitForTarget("any", 2):
                    API.Target(item.Serial)
                    API.Pause(PAUSE_SHORT)
        API.Pause(1.0)


def _get_nearby_corpses():
    # Find corpses within scan range (processed filtering happens in the loop).
    corpses = []
    items = API.GetItemsOnGround(SCAN_RANGE)
    if not items:
        return corpses
    for item in items:
        if item.IsCorpse:
            corpses.append(item)
    return corpses


def _toggle_running():
    global RUNNING
    RUNNING = not RUNNING
    state = "ON" if RUNNING else "OFF"
    API.SysMsg(f"Butcher: {state}")
    _update_control_gump()


def _update_control_gump():
    if not CONTROL_BUTTON:
        return
    CONTROL_BUTTON.Text = "Disable" if RUNNING else "Enable"


def _on_options_closed():
    global OPTIONS_GUMP
    OPTIONS_GUMP = None


def _create_options_gump():
    global OPTIONS_GUMP
    if OPTIONS_GUMP:
        return
    g = API.CreateGump(True, True, True)
    row_h = 22
    width = 220
    height = 60 + (len(LOOT_ITEM_CONFIG) * row_h)
    g.SetRect(130, 130, width, height)
    bg = API.CreateGumpColorBox(0.7, "#1B1B1B")
    bg.SetRect(0, 0, width, height)
    g.Add(bg)

    label = API.CreateGumpTTFLabel("Butcher Loot Options", 16, "#FFFFFF", "alagard", "center", width)
    label.SetPos(0, 6)
    g.Add(label)

    y = 30
    for graphic in LOOT_ITEM_ORDER:
        data = LOOT_ITEM_CONFIG.get(graphic)
        if not data:
            continue
        cb = API.CreateGumpCheckbox(data["name"], 996, data["enabled"])
        cb.SetPos(10, y)
        g.Add(cb)
        API.AddControlOnClick(cb, lambda c=cb, g_id=graphic: _set_loot_enabled(g_id, c.IsChecked))
        y += row_h

    close_button = API.CreateSimpleButton("Close", 80, 20)
    close_button.SetPos(width - 90, height - 26)
    g.Add(close_button)
    API.AddControlOnClick(close_button, _close_options_gump)

    API.AddControlOnDisposed(g, _on_options_closed)
    API.AddGump(g)
    OPTIONS_GUMP = g


def _close_options_gump():
    global OPTIONS_GUMP
    if OPTIONS_GUMP:
        OPTIONS_GUMP.Dispose()
        OPTIONS_GUMP = None


def _set_loot_enabled(graphic, enabled):
    if graphic in LOOT_ITEM_CONFIG:
        LOOT_ITEM_CONFIG[graphic]["enabled"] = bool(enabled)


def _toggle_options_gump():
    if OPTIONS_GUMP:
        _close_options_gump()
    else:
        _create_options_gump()


def _create_control_gump():
    global CONTROL_GUMP, CONTROL_BUTTON
    if CONTROL_GUMP:
        return
    g = API.CreateGump(True, True, True)
    g.SetRect(100, 100, 200, 90)
    bg = API.CreateGumpColorBox(0.7, "#1B1B1B")
    bg.SetRect(0, 0, 200, 90)
    g.Add(bg)

    label = API.CreateGumpTTFLabel("Butcher Controller", 16, "#FFFFFF", "alagard", "center", 200)
    label.SetPos(0, 6)
    g.Add(label)

    button = API.CreateSimpleButton("Enable", 90, 20)
    button.SetPos(10, 55)
    g.Add(button)
    API.AddControlOnClick(button, _toggle_running)
    CONTROL_BUTTON = button

    options = API.CreateSimpleButton("Options", 90, 20)
    options.SetPos(100, 55)
    g.Add(options)
    API.AddControlOnClick(options, _toggle_options_gump)

    API.AddGump(g)
    CONTROL_GUMP = g
    _update_control_gump()


def _pause_if_needed():
    while not RUNNING:
        API.ProcessCallbacks()
        API.Pause(0.1)


_create_control_gump()

while True:
    _pause_if_needed()
    API.ProcessCallbacks()
    corpses = _get_nearby_corpses()
    if corpses:
        # Clean up processed list for corpses that are no longer on the ground.
        current_serials = set([c.Serial for c in corpses])
        SEEN_CORPSES.intersection_update(current_serials)
        for corpse in corpses:
            if corpse.Serial in SEEN_CORPSES:
                continue
            if _carve_corpse(corpse):
                API.Pause(PAUSE_SHORT)
            _loot_corpse_items(corpse)
            API.Pause(PAUSE_LOOT_SETTLE)
            _cut_leather_in_backpack()
            SEEN_CORPSES.add(corpse.Serial)
    API.Pause(0.5)
