import API
import time

"""
Caster Training (LegionScript port)
Based on RazorEnhanced script by Dorana.
Source: https://github.com/dorana/RazorEnhancedScripts

Features:
- Supports Magery, Necromancy, Chivalry, Mysticism, and Spellweaving.
- Auto-selects spells based on current skill level.
- Heals and meditates as needed during training.
- Optional weapon prompts for Chivalry/Spellweaving training ranges.

Setup:
1) Open the gump and enter target skill caps for the schools you want to train.
2) Press Start; the script will loop spells until each cap is reached.
3) If prompted, target a weapon in your backpack for Chivalry/Spellweaving.
4) Keep reagents, mana, and bandages available for smooth training.
"""

# Gump constants.
GUMP_ID = 1239862396  # Reserved id (informational; not used by CreateGump).
GUMP_X = 500  # Gump X position.
GUMP_Y = 500  # Gump Y position.
GUMP_WIDTH = 240  # Gump width.
ROW_HEIGHT = 26  # Row height for layout.

# Spell schools supported by this trainer.
SPELL_SCHOOLS = [
    "Magery",
    "Necromancy",
    "Chivalry",
    "Mysticism",
    "Spellweaving",
]

# Runtime state containers.
SPELL_CAPS = {name: 0 for name in SPELL_SCHOOLS}  # Target caps per school.
CAST_HOLDER = {}  # Spell rotations per school.
RUNNING = False  # Training loop state.
PLAYER = None  # Player reference.
TARGET_WEAPON = None  # Weapon for Chivalry/Spellweaving training.
TEXT_INPUTS = {}  # Gump text boxes per school.
CONTROL_GUMP = None  # Current gump reference.
STATUS_LABELS = []  # Active status labels for tracking progress.


# Get a skill's current value.
def _get_skill_value(name):
    skill = API.GetSkill(name)
    if not skill or skill.Value is None:
        return 0.0
    return float(skill.Value)


# Determine if a weapon is needed for Chivalry training.
def _needs_weapon_for_chivalry():
    return SPELL_CAPS["Chivalry"] > 0 and _get_skill_value("Chivalry") < 45


# Determine if a weapon is needed for Spellweaving training.
def _needs_weapon_for_spellweaving():
    return SPELL_CAPS["Spellweaving"] > 20 and _get_skill_value("Spellweaving") < 44


# Prompt the user to target a weapon in the backpack.
def _prompt_weapon():
    API.SysMsg("Target a weapon in your backpack for training.")
    serial = API.RequestTarget()
    if not serial:
        return None
    return API.FindItem(serial)


# Equip a training weapon when required for the school.
def _equip_weapon_if_needed(school):
    global TARGET_WEAPON
    if school == "Chivalry" and _get_skill_value("Chivalry") >= 45:
        return
    if school == "Spellweaving" and _get_skill_value("Spellweaving") >= 44:
        return
    if TARGET_WEAPON:
        API.EquipItem(TARGET_WEAPON.Serial)
        API.Pause(0.5)


# Build the per-school spell rotation list.
def _setup_spells():
    if SPELL_CAPS["Magery"] > 0:
        CAST_HOLDER["Magery"] = [
            {"skill": 45, "spell": "Fireball", "wait": 4000},
            {"skill": 55, "spell": "Lightning", "wait": 4000},
            {"skill": 65, "spell": "Paralyze", "wait": 4000},
            {"skill": 75, "spell": "Reveal", "wait": 4000},
            {"skill": 90, "spell": "Flame Strike", "wait": 4000},
            {"skill": 120, "spell": "Earthquake", "wait": 5000},
        ]
    if SPELL_CAPS["Mysticism"] > 0:
        CAST_HOLDER["Mysticism"] = [
            {"skill": 60, "spell": "Stone Form", "wait": 4000},
            {"skill": 80, "spell": "Cleansing Winds", "wait": 4000},
            {"skill": 95, "spell": "Hail Storm", "wait": 4000},
            {"skill": 120, "spell": "Nether Cyclone", "wait": 4000},
        ]
    if SPELL_CAPS["Necromancy"] > 0:
        CAST_HOLDER["Necromancy"] = [
            {"skill": 50, "spell": "Pain Spike", "wait": 4000},
            {"skill": 70, "spell": "Horrific Beast", "wait": 4000, "buff": "Horrific Beast"},
            {"skill": 90, "spell": "Wither", "wait": 4000},
            {"skill": 95, "spell": "Lich Form", "wait": 4000, "buff": "Lich Form"},
            {"skill": 120, "spell": "Vampiric Embrace", "wait": 4000},
        ]
    if SPELL_CAPS["Chivalry"] > 0:
        CAST_HOLDER["Chivalry"] = [
            {"skill": 45, "spell": "Consecrate Weapon", "wait": 4000},
            {"skill": 60, "spell": "Divine Fury", "wait": 4000},
            {"skill": 70, "spell": "Enemy of One", "wait": 4000},
            {"skill": 90, "spell": "Holy Light", "wait": 4000},
            {"skill": 120, "spell": "Noble Sacrifice", "wait": 4000},
        ]
    if SPELL_CAPS["Spellweaving"] > 0:
        CAST_HOLDER["Spellweaving"] = [
            {"skill": 20, "spell": "Arcane Circle", "wait": 4000},
            {"skill": 33, "spell": "Immolating Weapon", "wait": 9000},
            {"skill": 52, "spell": "Reaper Form", "wait": 4000, "buff": "Reaper Form"},
            {"skill": 74, "spell": "Essence of Wind", "wait": 4000},
            {"skill": 90, "spell": "Wildfire", "wait": 3000},
            {"skill": 120, "spell": "Word of Death", "wait": 4000},
        ]


# Ensure sufficient mana via Meditation when needed.
def _check_mana():
    if API.Player.Mana >= 30:
        return
    while API.Player.Mana < API.Player.ManaMax:
        if API.BuffExists("Meditation"):
            API.Pause(1.0)
        else:
            API.UseSkill("Meditation")
            API.Pause(3.0)


# Heal the player using available magic or bandages.
def _heal_if_needed():
    if API.Player.Hits >= 30:
        return
    while API.Player.Hits < API.Player.HitsMax:
        magery = _get_skill_value("Magery")
        if magery >= 50:
            _check_mana()
            API.CastSpell("Greater Heal")
            API.Pause(4.0)
            continue
        if magery >= 30:
            _check_mana()
            API.CastSpell("Heal")
            API.Pause(4.0)
            continue
        chiv = _get_skill_value("Chivalry")
        if chiv >= 30:
            _check_mana()
            API.CastSpell("Close Wounds")
            API.Pause(4.0)
            continue
        spirit = _get_skill_value("Spirit Speak")
        if spirit >= 30:
            API.UseSkill("Spirit Speak")
            API.Pause(7.0)
            continue
        weaving = _get_skill_value("Spellweaving")
        if weaving >= 24 and not API.BuffExists("Gift of Renewal"):
            API.CastSpell("Gift of Renewal")
            API.Pause(7.0)
            continue
        bandage = API.FindType(0x0E21, API.Backpack)
        if bandage:
            API.UseObject(bandage.Serial)
            if API.WaitForTarget("any", 2):
                API.TargetSelf()
            API.Pause(7.0)
            continue
        API.Pause(2.0)


# Cast a spell by name.
def _cast_spell(spell_name):
    API.CastSpell(spell_name)


# Train a specific school until the target cap is reached.
def _train_skill(school):
    skill_cap = SPELL_CAPS[school]
    skill_val = _get_skill_value(school)
    if skill_val >= skill_cap:
        return
    cast_list = CAST_HOLDER.get(school, [])
    max_tier_skill = max((s["skill"] for s in cast_list), default=skill_cap)
    while skill_val <= skill_cap:
        API.ProcessCallbacks()
        skill_cap = SPELL_CAPS[school]
        effective_cap = min(skill_cap, max_tier_skill)
        skill_val = _get_skill_value(school)
        if skill_val >= skill_cap:
            break

        _heal_if_needed()
        _update_gump()
        _check_mana()

        casted = False
        for spell in cast_list:
            if skill_val < spell["skill"] and skill_val < effective_cap:
                if "buff" in spell and spell["buff"] and API.BuffExists(spell["buff"]):
                    API.Pause(2.0)
                    casted = True
                    break
                _cast_spell(spell["spell"])
                API.Pause(spell["wait"] / 1000.0)
                _update_gump()
                casted = True
                break
        if not casted:
            API.Pause(0.25)
            break


# Start button callback: read caps and begin training.
def _on_start():
    global RUNNING
    for name, tb in TEXT_INPUTS.items():
        try:
            SPELL_CAPS[name] = int(tb.Text.strip()) if tb.Text else 0
        except ValueError:
            SPELL_CAPS[name] = 0
    _update_gump()
    if any(v > 0 for v in SPELL_CAPS.values()):
        RUNNING = True


# Render or refresh the gump UI.
def _update_gump():
    global CONTROL_GUMP, TEXT_INPUTS, STATUS_LABELS
    if CONTROL_GUMP:
        CONTROL_GUMP.Dispose()
        CONTROL_GUMP = None
        TEXT_INPUTS = {}
        STATUS_LABELS = []

    g = API.CreateGump(True, True, True)
    g.SetRect(GUMP_X, GUMP_Y, GUMP_WIDTH, 100)
    bg = API.CreateGumpColorBox(0.7, "#1B1B1B")
    g.Add(bg.SetRect(0, 0, GUMP_WIDTH, 100))

    title = API.CreateGumpTTFLabel("Caster Training by Dorana", 14, "#FFFFFF", "alagard", "let", GUMP_WIDTH - 20)
    title.SetPos(10, 8)
    g.Add(title)

    to_train = [k for k, v in SPELL_CAPS.items() if v > 0]
    if to_train:
        height = 35 + (len(to_train) * 30)
        g.SetRect(GUMP_X, GUMP_Y, GUMP_WIDTH, height)
        bg.SetRect(0, 0, GUMP_WIDTH, height)
        y = 30
        for school in to_train:
            current_skill = _get_skill_value(school)
            cap = SPELL_CAPS[school]
            label = API.CreateGumpTTFLabel(f"{school} - {current_skill:.1f}/{cap}", 12, "#FFFFFF", "alagard", "let", GUMP_WIDTH - 20)
            label.SetPos(10, y)
            g.Add(label)
            STATUS_LABELS.append(label)
            y += 26
    else:
        height = 100 + (len(SPELL_SCHOOLS) * 30)
        g.SetRect(GUMP_X, GUMP_Y, GUMP_WIDTH, height)
        bg.SetRect(0, 0, GUMP_WIDTH, height)

        header = API.CreateGumpTTFLabel("Skill name", 12, "#FFFFFF", "alagard", "let", 90)
        header.SetPos(10, 30)
        g.Add(header)
        header2 = API.CreateGumpTTFLabel("Target Skill", 12, "#FFFFFF", "alagard", "let", 90)
        header2.SetPos(120, 30)
        g.Add(header2)

        y = 55
        idx = 0
        for school in SPELL_SCHOOLS:
            name_label = API.CreateGumpTTFLabel(school, 12, "#FFFFFF", "alagard", "let", 100)
            name_label.SetPos(10, y)
            g.Add(name_label)
            tb = API.CreateGumpTextBox("" if SPELL_CAPS[school] <= 0 else str(SPELL_CAPS[school]), 70, 18, False)
            tb.SetPos(120, y)
            tb.NumbersOnly = True
            g.Add(tb)
            TEXT_INPUTS[school] = tb
            y += 30
            idx += 1

        start_btn = API.CreateSimpleButton("Start", 80, 20)
        start_btn.SetPos(120, height - 35)
        g.Add(start_btn)
        API.AddControlOnClick(start_btn, _on_start)

    API.AddGump(g)
    CONTROL_GUMP = g


# Main loop for the script.
def _run():
    global PLAYER, TARGET_WEAPON, RUNNING
    _update_gump()
    PLAYER = API.Player

    while not RUNNING:
        API.ProcessCallbacks()
        API.Pause(0.5)

    _setup_spells()

    if _needs_weapon_for_chivalry() or _needs_weapon_for_spellweaving():
        TARGET_WEAPON = _prompt_weapon()

    for school in CAST_HOLDER.keys():
        _equip_weapon_if_needed(school)
        _train_skill(school)
        _update_gump()


_run()
