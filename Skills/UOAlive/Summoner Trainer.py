import API

CHECK_INTERVAL = 0.5
TARGET_TIMEOUT = 2.5
Goal = 100
VERSION = "1.7.0"

def centered_label(text, size, color="#FFFFFF"):
    return API.Gumps.CreateGumpTTFLabel(
        text,
        size,
        color,
        aligned="center",
    )

def add_tiled_part(gump, graphic, x, y, width, height, hue=0):
    part = API.Gumps.CreateTiledGumpPic(
        graphic,
        max(1, width),
        max(1, height),
        hue,
    )
    part.SetX(x)
    part.SetY(y)
    gump.Add(part)


def get_size(control, default_w=24, default_h=24):
    width = control.GetWidth() if hasattr(control, "GetWidth") else default_w
    height = control.GetHeight() if hasattr(control, "GetHeight") else default_h
    return (
        width if width > 0 else default_w,
        height if height > 0 else default_h,
    )


def add_popup_background(gump, width, height):
    # Use the nine-piece scroll frame while preserving each popup's dimensions.
    top_left = API.Gumps.CreateGumpPic(0x2436, 0, 0)
    top_right = API.Gumps.CreateGumpPic(0x2438, 0, 0)
    bottom_left = API.Gumps.CreateGumpPic(0x243C, 0, 0)
    bottom_right = API.Gumps.CreateGumpPic(0x243E, 0, 0)

    left_width, top_height = get_size(top_left, 24, 24)
    right_width, _ = get_size(top_right, 24, 24)
    _, bottom_height = get_size(bottom_left, 24, 24)

    top_right.SetX(width - right_width)
    top_right.SetY(0)
    bottom_left.SetX(0)
    bottom_left.SetY(height - bottom_height)
    bottom_right.SetX(width - right_width)
    bottom_right.SetY(height - bottom_height)

    inner_width = max(1, width - left_width - right_width)
    inner_height = max(1, height - top_height - bottom_height)

    # Add the tiled center and four edges first so the corners sit above them.
    add_tiled_part(gump, 0x243A, left_width, top_height, inner_width, inner_height)
    add_tiled_part(gump, 0x2437, left_width, 0, inner_width, top_height)
    add_tiled_part(
        gump,
        0x243D,
        left_width,
        height - bottom_height,
        inner_width,
        bottom_height,
    )
    add_tiled_part(gump, 0x2439, 0, top_height, left_width, inner_height)
    add_tiled_part(
        gump,
        0x243B,
        width - right_width,
        top_height,
        right_width,
        inner_height,
    )

    gump.Add(top_left)
    gump.Add(top_right)
    gump.Add(bottom_left)
    gump.Add(bottom_right)

BASE_SKILLS = [
    ("Magery", "Magery"),
    ("Evaluating Intelligence", "Eval"),
    ("Mysticism", "Mysticism"),
    ("Spellweaving", "Spellweaving"),
    ("Meditation", "Meditation"),
    ("Focus", "Focus"),
]

def add_milestone_skill_status(gump, width, y, required_skills):
    necromancy = API.GetSkill("Necromancy")
    spirit_speak = API.GetSkill("Spirit Speak")
    current_values = {}
    value_parts = []
    unmet = []

    for skill_name, short_name in BASE_SKILLS:
        skill = API.GetSkill(skill_name)
        if skill:
            current_values[skill_name] = skill.Value
            value_parts.append(short_name + " " + str(skill.Value))
        else:
            current_values[skill_name] = None
            value_parts.append(short_name + " ?")

    for skill_name, minimum in required_skills:
        skill_value = current_values.get(skill_name)
        if skill_value is None:
            unmet.append(skill_name + " unreadable")
        elif skill_value < minimum:
            unmet.append(skill_name + " below " + str(minimum))

    if not necromancy or not spirit_speak:
        necro_text = str(necromancy.Value) if necromancy else "?"
        spirit_text = str(spirit_speak.Value) if spirit_speak else "?"
        unmet.append("Necromancy/Spirit Speak unreadable")
    else:
        necro_text = str(necromancy.Value)
        spirit_text = str(spirit_speak.Value)
        if necromancy.Value != 0 or spirit_speak.Value != 0:
            unmet.append("Necromancy and Spirit Speak must both be 0")

    status_color = "#FF77FF77" if not unmet else "#FFFF5555"
    status_lines = [
        "Base skills: " + " | ".join(value_parts),
        "Necromancy: " + necro_text + " | Spirit Speak: " + spirit_text,
    ]
    if unmet:
        status_lines.append("Benefits unavailable: " + "; ".join(unmet))
    else:
        status_lines.append("Milestone requirements met; benefits are available.")

    for index, text in enumerate(status_lines):
        status_label = centered_label(text, 14, status_color)
        status_label.SetRect(15, y + index * 23, width - 30, 22)
        gump.Add(status_label)

def heal_if_needed():
    if API.Player.HitsMax <= 0:
        return False

    if API.Player.Hits * 100 >= API.Player.HitsMax * 75:
        return False

    if API.Player.Mana < 11:
        wait_for_full_mana()

    if not API.StopRequested and API.Player.Mana >= 11:
        cast_on_self("Greater Heal", "beneficial")

    return True

def wait_for_full_mana():
    regen_gump = API.Gumps.CreateGump(False, False, False)
    regen_gump.SetRect(0, 0, 360, 90)
    add_popup_background(regen_gump, 360, 90)
    regen_gump.CenterXInViewPort()
    regen_gump.CenterYInViewPort()

    regen_message = centered_label(
        "Regenerating mana...",
        20,
        "#FFFFFF",
    )
    regen_message.SetRect(10, 25, 340, 32)
    regen_gump.Add(regen_message)
    API.Gumps.AddGump(regen_gump)

    while API.Player.Mana < API.Player.ManaMax and not API.StopRequested:
        API.ProcessCallbacks()
        API.Pause(CHECK_INTERVAL)

    regen_gump.Dispose()

def cast_on_self(spell_name, target_type):
    API.PreTarget(API.Player.Serial, target_type)
    API.CastSpell(spell_name)

    if API.WaitForTarget("any", timeout=TARGET_TIMEOUT):
        API.TargetSelf()
    else:
        API.CancelPreTarget()

def train_spellweaving_band(stop_at, spell_name, min_mana, target_self=False):
    while not API.StopRequested:
        spellweaving = API.GetSkill("Spellweaving")
        if not spellweaving:
            API.SysMsg("Could not read Spellweaving skill.")
            break

        current_spellweaving = spellweaving.Value
        if current_spellweaving >= 50:
            show_spellweaving_50_milestone()
        if current_spellweaving >= 100:
            show_spellweaving_100_milestone()
        if current_spellweaving >= 120:
            show_spellweaving_120_milestone()

        if current_spellweaving >= min(stop_at, Goal):
            API.SysMsg("Spellweaving reached " + str(min(stop_at, Goal)) + ".0.")
            break

        if heal_if_needed():
            API.Pause(CHECK_INTERVAL)
            continue
        elif API.Player.Mana < min_mana:
            wait_for_full_mana()
        elif target_self:
            cast_on_self(spell_name, "harmful")
        else:
            API.CastSpell(spell_name)

        API.Pause(CHECK_INTERVAL)

spellweaving_50_milestone = {"shown": False}

def show_spellweaving_50_milestone():
    if spellweaving_50_milestone["shown"] or API.StopRequested:
        return

    spellweaving_50_milestone["shown"] = True
    milestone_notice = {"acknowledged": False}

    def acknowledge_milestone():
        milestone_notice["acknowledged"] = True

    milestone_gump = API.Gumps.CreateGump(True, True, False)
    milestone_gump.SetRect(0, 0, 900, 390)
    add_popup_background(milestone_gump, 900, 390)
    milestone_gump.CenterXInViewPort()
    milestone_gump.CenterYInViewPort()

    milestone_title = centered_label(
        "Milestone Achievement: Developing Summoner",
        22,
        "#FFFFFF",
    )
    milestone_title.SetRect(15, 15, 870, 34)
    milestone_gump.Add(milestone_title)

    milestone_tier = centered_label(
        "Mysticism & Spellweaving: 50–99",
        19,
        "#FFFFFF",
    )
    milestone_tier.SetRect(15, 55, 870, 30)
    milestone_gump.Add(milestone_tier)

    milestone_line1 = centered_label(
        "Rising Colossus drops from 5 slots to 3 slots.",
        18,
        "#FFFFFF",
    )
    milestone_line1.SetRect(15, 100, 870, 28)
    milestone_gump.Add(milestone_line1)

    milestone_line2 = centered_label(
        "Magery Elementals and Daemon drop from 4 slots to 2 slots.",
        18,
        "#FFFFFF",
    )
    milestone_line2.SetRect(15, 135, 870, 28)
    milestone_gump.Add(milestone_line2)

    milestone_line3 = centered_label(
        "Animated Weapon uses Mysticism instead of Tactics and Anatomy",
        18,
        "#FFFFFF",
    )
    milestone_line3.SetRect(15, 170, 870, 28)
    milestone_gump.Add(milestone_line3)

    milestone_line4 = centered_label(
        "for its scaling, and uses 4 follower slots.",
        18,
        "#FFFFFF",
    )
    milestone_line4.SetRect(15, 202, 870, 28)
    milestone_gump.Add(milestone_line4)

    milestone_reminder = centered_label(
        "Mysticism should already be at your selected goal.",
        18,
        "#FFFFFF",
    )
    milestone_reminder.SetRect(15, 242, 870, 28)
    milestone_gump.Add(milestone_reminder)

    add_milestone_skill_status(
        milestone_gump,
        900,
        270,
        [("Mysticism", 50), ("Spellweaving", 50)],
    )

    milestone_button = API.Gumps.CreateSimpleButton("Continue", 140, 32)
    milestone_button.SetPos(380, 350)
    milestone_button.SetBackgroundColor(35, 110, 45)
    milestone_gump.Add(milestone_button)
    API.Gumps.AddControlOnClick(milestone_button, acknowledge_milestone)
    API.Gumps.AddGump(milestone_gump)

    while not milestone_notice["acknowledged"] and not API.StopRequested:
        API.ProcessCallbacks()
        API.Pause(0.1)

    milestone_gump.Dispose()

spellweaving_100_milestone = {"shown": False}

def show_spellweaving_100_milestone():
    if spellweaving_100_milestone["shown"] or API.StopRequested:
        return

    spellweaving_100_milestone["shown"] = True
    milestone_notice = {"acknowledged": False}

    def acknowledge_milestone():
        milestone_notice["acknowledged"] = True

    milestone_gump = API.Gumps.CreateGump(True, True, False)
    milestone_gump.SetRect(0, 0, 940, 430)
    add_popup_background(milestone_gump, 940, 430)
    milestone_gump.CenterXInViewPort()
    milestone_gump.CenterYInViewPort()

    milestone_title = centered_label(
        "Milestone Achievement: Grandmaster Summoner",
        22,
        "#FFFFFF",
    )
    milestone_title.SetRect(15, 15, 910, 34)
    milestone_gump.Add(milestone_title)

    milestone_tier = centered_label(
        "Grandmaster: 100–119 in all six skills",
        19,
        "#FFFFFF",
    )
    milestone_tier.SetRect(15, 55, 910, 30)
    milestone_gump.Add(milestone_tier)

    milestone_line1 = centered_label(
        "Summon Creature drops from 5 slots to 2 slots",
        18,
        "#FFFFFF",
    )
    milestone_line1.SetRect(15, 100, 910, 28)
    milestone_gump.Add(milestone_line1)

    milestone_line2 = centered_label(
        "at 100+ Mysticism and Spellweaving.",
        18,
        "#FFFFFF",
    )
    milestone_line2.SetRect(15, 132, 910, 28)
    milestone_gump.Add(milestone_line2)

    milestone_line3 = centered_label(
        "Animated Weapon drops from 4 slots to 2 and gains Armor Pierce",
        18,
        "#FFFFFF",
    )
    milestone_line3.SetRect(15, 172, 910, 28)
    milestone_gump.Add(milestone_line3)

    milestone_line4 = centered_label(
        "at 100+ Magery, Mysticism, and Spellweaving.",
        18,
        "#FFFFFF",
    )
    milestone_line4.SetRect(15, 204, 910, 28)
    milestone_gump.Add(milestone_line4)

    milestone_line5 = centered_label(
        "Unlocks flexible 5-slot army combinations, such as a 3-slot Colossus",
        18,
        "#FFFFFF",
    )
    milestone_line5.SetRect(15, 244, 910, 28)
    milestone_gump.Add(milestone_line5)

    milestone_line6 = centered_label(
        "with a 2-slot Summon Creature, Elemental, or Animated Weapon.",
        18,
        "#FFFFFF",
    )
    milestone_line6.SetRect(15, 276, 910, 28)
    milestone_gump.Add(milestone_line6)

    add_milestone_skill_status(
        milestone_gump,
        940,
        310,
        [(skill_name, 100) for skill_name, _ in BASE_SKILLS],
    )

    milestone_button = API.Gumps.CreateSimpleButton("Continue", 140, 32)
    milestone_button.SetPos(400, 390)
    milestone_button.SetBackgroundColor(35, 110, 45)
    milestone_gump.Add(milestone_button)
    API.Gumps.AddControlOnClick(milestone_button, acknowledge_milestone)
    API.Gumps.AddGump(milestone_gump)

    while not milestone_notice["acknowledged"] and not API.StopRequested:
        API.ProcessCallbacks()
        API.Pause(0.1)

    milestone_gump.Dispose()

spellweaving_120_milestone = {"shown": False}

def show_spellweaving_120_milestone():
    if spellweaving_120_milestone["shown"] or API.StopRequested:
        return

    spellweaving_120_milestone["shown"] = True
    milestone_notice = {"acknowledged": False}

    def acknowledge_milestone():
        milestone_notice["acknowledged"] = True

    milestone_gump = API.Gumps.CreateGump(True, True, False)
    milestone_gump.SetRect(0, 0, 940, 490)
    add_popup_background(milestone_gump, 940, 490)
    milestone_gump.CenterXInViewPort()
    milestone_gump.CenterYInViewPort()

    milestone_title = centered_label(
        "Milestone Achievement: Legendary Summoner",
        22,
        "#FFFFFF",
    )
    milestone_title.SetRect(15, 15, 910, 34)
    milestone_gump.Add(milestone_title)

    milestone_tier = centered_label(
        "Legendary: 120 in all six base skills",
        19,
        "#FFFFFF",
    )
    milestone_tier.SetRect(15, 55, 910, 30)
    milestone_gump.Add(milestone_tier)

    milestone_line1 = centered_label(
        "Greater Elementals and Greater Daemon unlock with upgraded stats",
        18,
        "#FFFFFF",
    )
    milestone_line1.SetRect(15, 100, 910, 28)
    milestone_gump.Add(milestone_line1)

    milestone_line2 = centered_label(
        "and special attacks.",
        18,
        "#FFFFFF",
    )
    milestone_line2.SetRect(15, 132, 910, 28)
    milestone_gump.Add(milestone_line2)

    milestone_line3 = centered_label(
        "Elemental Colossus mutations: Physical, Magma, Energy, Frozen, and Poisonous;",
        18,
        "#FFFFFF",
    )
    milestone_line3.SetRect(15, 170, 910, 28)
    milestone_gump.Add(milestone_line3)

    milestone_line4 = centered_label(
        "Colossus duration is about 3 minutes.",
        18,
        "#FFFFFF",
    )
    milestone_line4.SetRect(15, 202, 910, 28)
    milestone_gump.Add(milestone_line4)

    milestone_line5 = centered_label(
        "Arcane Fey / Fiend groups can summon up to 5 allies per cast,",
        18,
        "#FFFFFF",
    )
    milestone_line5.SetRect(15, 238, 910, 28)
    milestone_gump.Add(milestone_line5)

    milestone_line6 = centered_label(
        "depending on Arcane Focus.",
        18,
        "#FFFFFF",
    )
    milestone_line6.SetRect(15, 270, 910, 28)
    milestone_gump.Add(milestone_line6)

    milestone_line7 = centered_label(
        "Ethereal Form: 8% Hit Mana Drain; Ethereal Burst: 5-minute cooldown.",
        18,
        "#FFFFFF",
    )
    milestone_line7.SetRect(15, 302, 910, 28)
    milestone_gump.Add(milestone_line7)

    milestone_line8 = centered_label(
        "Pocket Colossus stores a spell trigger; Summon Creature lasts about 5 minutes.",
        18,
        "#FFFFFF",
    )
    milestone_line8.SetRect(15, 334, 910, 28)
    milestone_gump.Add(milestone_line8)

    add_milestone_skill_status(
        milestone_gump,
        940,
        370,
        [(skill_name, 120) for skill_name, _ in BASE_SKILLS],
    )

    milestone_button = API.Gumps.CreateSimpleButton("Continue", 140, 32)
    milestone_button.SetPos(400, 450)
    milestone_button.SetBackgroundColor(35, 110, 45)
    milestone_gump.Add(milestone_button)
    API.Gumps.AddControlOnClick(milestone_button, acknowledge_milestone)
    API.Gumps.AddGump(milestone_gump)

    while not milestone_notice["acknowledged"] and not API.StopRequested:
        API.ProcessCallbacks()
        API.Pause(0.1)

    milestone_gump.Dispose()

SPELL_MIN_MANA = {
    "Wall of Stone": 9,
    "Fire Field": 11,
    "Poison Field": 14,
    "Paralyze Field": 20,
    "Energy Field": 40,
    "Earthquake": 50,
}

# Startup safety and skill disclaimer.
safety_notice = {"acknowledged": False}

def acknowledge_safety_notice():
    safety_notice["acknowledged"] = True

title_gump = API.Gumps.CreateGump(False, False, False)
viewport = API.GetViewportBounds()
title_gump.SetRect(
    viewport.X + (viewport.Width - 700) // 2,
    viewport.Y + 15,
    700,
    90,
)
add_popup_background(title_gump, 700, 90)

title_label = centered_label("Pure Summoner Trainer", 23, "#FFFFFF")
title_label.SetRect(10, 8, 680, 32)
title_gump.Add(title_label)

version_label = API.Gumps.CreateGumpTTFLabel(
    "Version " + VERSION,
    16,
    "#FFFFFF",
    aligned="left",
)
version_label.SetRect(18, 52, 300, 24)
title_gump.Add(version_label)

author_label = API.Gumps.CreateGumpTTFLabel(
    "Written by Oruchi",
    16,
    "#FFFFFF",
    aligned="right",
)
author_label.SetRect(382, 52, 300, 24)
title_gump.Add(author_label)
API.Gumps.AddGump(title_gump)

safety_gump = API.Gumps.CreateGump(True, True, False)
safety_gump.SetRect(0, 0, 850, 250)
add_popup_background(safety_gump, 850, 250)
safety_gump.CenterXInViewPort()
safety_gump.CenterYInViewPort()

safety_line1 = centered_label(
    "Make sure you are in a safe spot like your house or a non-guard-zone area",
    21,
    "#FFFFFF",
)
safety_line1.SetRect(15, 20, 820, 34)
safety_gump.Add(safety_line1)

safety_line2 = centered_label(
    "so area-of-effect damage does not flag you with guards.",
    21,
    "#FFFFFF",
)
safety_line2.SetRect(15, 58, 820, 34)
safety_gump.Add(safety_line2)

safety_line3 = centered_label(
    "Reminder: You must have ZERO Necromancy and ZERO Spirit Speak,",
    20,
    "#FFFFFF",
)
safety_line3.SetRect(15, 115, 820, 32)
safety_gump.Add(safety_line3)

safety_line4 = centered_label(
    "including skill bonuses from armor or weapons.",
    20,
    "#FFFFFF",
)
safety_line4.SetRect(15, 152, 820, 32)
safety_gump.Add(safety_line4)

safety_button = API.Gumps.CreateSimpleButton("Continue", 150, 36)
safety_button.SetPos(350, 195)
safety_button.SetBackgroundColor(35, 110, 45)
safety_gump.Add(safety_button)
API.Gumps.AddControlOnClick(safety_button, acknowledge_safety_notice)
API.Gumps.AddGump(safety_gump)

while not safety_notice["acknowledged"] and not API.StopRequested:
    API.ProcessCallbacks()
    API.Pause(0.1)

safety_gump.Dispose()
title_gump.Dispose()
# Ask which Magery goal to use when the script starts.
goal_selection = {"value": None}

def on_begin_clicked():
    selected_index = goal_dropdown.GetSelectedIndex()
    if selected_index == 0:
        goal_selection["value"] = 100
    elif selected_index == 1:
        goal_selection["value"] = 120

goal_gump = API.Gumps.CreateGump(True, True, False)
goal_gump.SetRect(0, 0, 680, 205)
add_popup_background(goal_gump, 680, 205)
goal_gump.CenterXInViewPort()
goal_gump.CenterYInViewPort()

goal_heading = centered_label("CHOOSE YOUR PATH", 18, "#FFFFFF")
goal_heading.SetRect(10, 10, 650, 28)
goal_gump.Add(goal_heading)

grandmaster_label = centered_label(
    "GrandMaster Pure Summoner (Skill cap 100)",
    18,
    "#FFFFFF",
)
grandmaster_label.SetRect(10, 45, 650, 28)
goal_gump.Add(grandmaster_label)

legendary_label = centered_label(
    "Legendary Pure Summoner (skill cap 120)",
    18,
    "#FFFFFF",
)
legendary_label.SetRect(10, 80, 650, 28)
goal_gump.Add(legendary_label)

goal_dropdown = API.Gumps.CreateDropDown(120, ["100", "120"], 0)
goal_dropdown.SetPos(200, 130)
goal_gump.Add(goal_dropdown)

begin_button = API.Gumps.CreateSimpleButton("Begin", 120, 30)
begin_button.SetPos(330, 130)
begin_button.SetBackgroundColor(138, 3, 3, 220)
begin_button.AlwaysShowBackground = True
goal_gump.Add(begin_button)
API.Gumps.AddControlOnClick(begin_button, on_begin_clicked)

API.Gumps.AddGump(goal_gump)

while goal_selection["value"] is None and not API.StopRequested:
    API.ProcessCallbacks()
    API.Pause(0.1)

goal_gump.Dispose()
if goal_selection["value"] is not None:
    Goal = goal_selection["value"]

# Explain the scroll requirement when the selected goal is 120.
if Goal == 120 and not API.StopRequested:
    scroll_notice = {"acknowledged": False}

    def acknowledge_scroll_notice():
        scroll_notice["acknowledged"] = True

    scroll_gump = API.Gumps.CreateGump(True, True, False)
    scroll_gump.SetRect(0, 0, 760, 170)
    add_popup_background(scroll_gump, 760, 170)
    scroll_gump.CenterXInViewPort()
    scroll_gump.CenterYInViewPort()

    scroll_line1 = centered_label(
        "In order to get to 120 in all 6 skills, you will need to consume",
        18,
        "#FFFFFF",
    )
    scroll_line1.SetRect(10, 10, 740, 28)
    scroll_gump.Add(scroll_line1)

    scroll_line2 = centered_label(
        "PowerScrolls(120) for Evaluating Intelligence, Focus, Magery, Meditation,",
        18,
        "#FFFFFF",
    )
    scroll_line2.SetRect(10, 45, 740, 28)
    scroll_gump.Add(scroll_line2)

    scroll_line3 = centered_label(
        "Mysticism and Spellweaving.",
        18,
        "#FFFFFF",
    )
    scroll_line3.SetRect(10, 80, 740, 28)
    scroll_gump.Add(scroll_line3)

    acknowledge_button = API.Gumps.CreateSimpleButton("Continue", 140, 32)
    acknowledge_button.SetPos(310, 120)
    acknowledge_button.SetBackgroundColor(35, 110, 45)
    scroll_gump.Add(acknowledge_button)
    API.Gumps.AddControlOnClick(acknowledge_button, acknowledge_scroll_notice)

    API.Gumps.AddGump(scroll_gump)

    while not scroll_notice["acknowledged"] and not API.StopRequested:
        API.ProcessCallbacks()
        API.Pause(0.1)

    scroll_gump.Dispose()

if goal_selection["value"] is not None and not API.StopRequested:
    API.SysMsg("Training has Begun. We will start with Magery... Lets Begin")

magery_goal_reached = False
threshold_prompted = False

# Repeatedly cast the selected Magery spell on yourself. Stop the Legion script to exit.
while not API.StopRequested:
    magery = API.GetSkill("Magery")
    current_magery = magery.Value if magery else 0

    if current_magery <= 40:
        API.SysMsg(
            "Your skill is too low. Go see an NPC Trainer in New Haven or any other city. "
            "You need at least 40 skill to begin training."
        )
        break

    if current_magery >= Goal:
        API.SysMsg("Magery goal reached.")
        magery_goal_reached = True
        break

    if current_magery >= 105 and not threshold_prompted:
        threshold_prompted = True
        threshold_choice = {"value": None}

        def choose_stop():
            threshold_choice["value"] = "stop"

        def choose_continue():
            threshold_choice["value"] = "continue"

        threshold_gump = API.Gumps.CreateGump(True, True, False)
        threshold_gump.SetRect(100, 100, 460, 190)
        add_popup_background(threshold_gump, 460, 190)

        message1 = centered_label(
            "You have reached a threshold where skill gain has slowed down.",
            16,
        )
        message1.SetRect(10, 10, 440, 28)
        threshold_gump.Add(message1)

        message2 = centered_label(
            "We recommend equipping a mage weapon with a -25 to Magery.",
            16,
        )
        message2.SetRect(10, 40, 440, 28)
        threshold_gump.Add(message2)

        message3 = centered_label(
            "Do you wish to stop the script or continue as it is?",
            16,
        )
        message3.SetRect(10, 70, 440, 28)
        threshold_gump.Add(message3)

        stop_button = API.Gumps.CreateSimpleButton("Stop Script", 150, 32)
        stop_button.SetPos(20, 120)
        stop_button.SetBackgroundColor(138, 3, 3)
        threshold_gump.Add(stop_button)
        API.Gumps.AddControlOnClick(stop_button, choose_stop)

        continue_button = API.Gumps.CreateSimpleButton("Continue", 150, 32)
        continue_button.SetPos(250, 120)
        continue_button.SetBackgroundColor(35, 110, 45)
        threshold_gump.Add(continue_button)
        API.Gumps.AddControlOnClick(continue_button, choose_continue)

        API.Gumps.AddGump(threshold_gump)

        while threshold_choice["value"] is None and not API.StopRequested:
            API.ProcessCallbacks()
            API.Pause(0.1)

        threshold_gump.Dispose()
        if threshold_choice["value"] == "stop":
            API.SysMsg("Training stopped at the 105 Magery threshold.")
            break

    if current_magery <= 45:
        spell_to_cast = "Wall of Stone"
    elif current_magery <= 55:
        spell_to_cast = "Fire Field"
    elif current_magery <= 65:
        spell_to_cast = "Poison Field"
    elif current_magery <= 75:
        spell_to_cast = "Paralyze Field"
    elif current_magery <= 90:
        spell_to_cast = "Energy Field"
    else:
        spell_to_cast = "Earthquake"

    MIN_MANA = SPELL_MIN_MANA[spell_to_cast]
    if heal_if_needed():
        pass
    elif API.Player.Mana < MIN_MANA:
        wait_for_full_mana()
    else:
        API.PreTarget(API.Player.Serial, "harmful")
        API.CastSpell(spell_to_cast)

        # Catch any target cursor in case the spell presents a different type.
        if API.WaitForTarget("any", timeout=TARGET_TIMEOUT):
            API.TargetSelf()
        else:
            API.CancelPreTarget()

    API.Pause(CHECK_INTERVAL)
# Show the Reactive Armor phase notice only if Evaluating Intelligence still needs training.
if magery_goal_reached and not API.StopRequested:
    eval_int_before_training = API.GetSkill("Evaluating Intelligence")
    if eval_int_before_training and eval_int_before_training.Value < Goal:
        eval_intro = {"acknowledged": False}

        def acknowledge_eval_intro():
            eval_intro["acknowledged"] = True

        eval_intro_gump = API.Gumps.CreateGump(True, True, False)
        eval_intro_gump.SetRect(0, 0, 700, 190)
        add_popup_background(eval_intro_gump, 700, 190)
        eval_intro_gump.CenterXInViewPort()
        eval_intro_gump.CenterYInViewPort()

        eval_intro_line1 = centered_label(
            "Congratulations! You have achieved your Magery goal.",
            18,
            "#FFFFFF",
        )
        eval_intro_line1.SetRect(10, 10, 680, 28)
        eval_intro_gump.Add(eval_intro_line1)

        eval_intro_line2 = centered_label(
            "Now we need to raise your Evaluating Intelligence.",
            18,
            "#FFFFFF",
        )
        eval_intro_line2.SetRect(10, 45, 680, 28)
        eval_intro_gump.Add(eval_intro_line2)

        eval_intro_line3 = centered_label(
            "Reactive Armor will be cast repeatedly until the goal is reached.",
            18,
            "#FFFFFF",
        )
        eval_intro_line3.SetRect(10, 80, 680, 28)
        eval_intro_gump.Add(eval_intro_line3)

        eval_intro_button = API.Gumps.CreateSimpleButton("Begin Reactive Armor", 210, 32)
        eval_intro_button.SetPos(245, 125)
        eval_intro_button.SetBackgroundColor(35, 110, 45)
        eval_intro_gump.Add(eval_intro_button)
        API.Gumps.AddControlOnClick(eval_intro_button, acknowledge_eval_intro)

        API.Gumps.AddGump(eval_intro_gump)

        while not eval_intro["acknowledged"] and not API.StopRequested:
            API.ProcessCallbacks()
            API.Pause(0.1)

        eval_intro_gump.Dispose()
# Train Evaluating Intelligence with Reactive Armor after Magery reaches the selected goal.
if magery_goal_reached and not API.StopRequested:
    while not API.StopRequested:
        if heal_if_needed():
            API.Pause(CHECK_INTERVAL)
            continue

        eval_int = API.GetSkill("Evaluating Intelligence")

        if not eval_int:
            API.SysMsg("Could not read Evaluating Intelligence skill.")
            break

        current_eval_int = eval_int.Value
        if current_eval_int >= Goal:
            API.SysMsg("Evaluating Intelligence goal reached.")

            if Goal == 100:
                summoner_rank = "GrandMaster Mage"
            else:
                summoner_rank = "Legendary Mage"

            completion_popup = {"acknowledged": False}

            def acknowledge_completion():
                completion_popup["acknowledged"] = True

            completion_gump = API.Gumps.CreateGump(True, True, False)
            completion_gump.SetRect(0, 0, 650, 175)
            add_popup_background(completion_gump, 650, 175)
            completion_gump.CenterXInViewPort()
            completion_gump.CenterYInViewPort()

            completion_message = centered_label(
                "Congratulations! You are a " + summoner_rank + "!",
                20,
                "#FFFFFF",
            )
            completion_message.SetRect(10, 20, 630, 36)
            completion_gump.Add(completion_message)

            mysticism_message = centered_label(
                "Okay, now let's move on to Mysticism.",
                18,
                "#FFFFFF",
            )
            mysticism_message.SetRect(10, 60, 630, 32)
            completion_gump.Add(mysticism_message)

            completion_button = API.Gumps.CreateSimpleButton("Continue", 140, 32)
            completion_button.SetPos(255, 115)
            completion_button.SetBackgroundColor(35, 110, 45)
            completion_gump.Add(completion_button)
            API.Gumps.AddControlOnClick(
                completion_button,
                acknowledge_completion,
            )

            API.Gumps.AddGump(completion_gump)

            while not completion_popup["acknowledged"] and not API.StopRequested:
                API.ProcessCallbacks()
                API.Pause(0.1)

            completion_gump.Dispose()
            break

        if API.Player.Mana <= 4:
            wait_for_full_mana()
        else:
            API.CastSpell("Reactive Armor")
            API.Pause(CHECK_INTERVAL)
mysticism_goal_reached = False
# Train Mysticism after Evaluating Intelligence reaches the selected goal.
if magery_goal_reached and not API.StopRequested:
    eval_int_final = API.GetSkill("Evaluating Intelligence")
    if eval_int_final and eval_int_final.Value >= Goal:
        API.SysMsg("Now training Mysticism.")

        while not API.StopRequested:
            mysticism = API.GetSkill("Mysticism")
            current_mysticism = mysticism.Value if mysticism else 0

            if not mysticism:
                API.SysMsg("Could not read Mysticism skill.")
                break

            if current_mysticism < 40:
                API.SysMsg(
                    "Mysticism is too low to begin scripted training. "
                    "Visit a Mystic vendor in Ter Mur, such as the Royal City, "
                    "and train to at least 40 skill."
                )
                break

            if current_mysticism >= Goal:
                mysticism_goal_reached = True
                API.SysMsg("Mysticism goal reached.")

                if Goal == 100:
                    mystic_rank = "GrandMaster Mystic"
                else:
                    mystic_rank = "Legendary Mystic"

                mysticism_completion = {"acknowledged": False}

                def acknowledge_mysticism_completion():
                    mysticism_completion["acknowledged"] = True

                mysticism_completion_gump = API.Gumps.CreateGump(
                    True,
                    True,
                    False,
                )
                mysticism_completion_gump.SetRect(0, 0, 650, 140)
                add_popup_background(mysticism_completion_gump, 650, 140)
                mysticism_completion_gump.CenterXInViewPort()
                mysticism_completion_gump.CenterYInViewPort()

                mysticism_completion_message = centered_label(
                    "Congratulations! You are a " + mystic_rank + "!",
                    20,
                    "#FFFFFF",
                )
                mysticism_completion_message.SetRect(10, 25, 630, 36)
                mysticism_completion_gump.Add(mysticism_completion_message)

                mysticism_completion_button = API.Gumps.CreateSimpleButton(
                    "Continue",
                    140,
                    32,
                )
                mysticism_completion_button.SetPos(255, 85)
                mysticism_completion_button.SetBackgroundColor(35, 110, 45)
                mysticism_completion_gump.Add(mysticism_completion_button)
                API.Gumps.AddControlOnClick(
                    mysticism_completion_button,
                    acknowledge_mysticism_completion,
                )

                API.Gumps.AddGump(mysticism_completion_gump)

                while (
                    not mysticism_completion["acknowledged"]
                    and not API.StopRequested
                ):
                    API.ProcessCallbacks()
                    API.Pause(0.1)

                mysticism_completion_gump.Dispose()
                break

            if current_mysticism < 63:
                spell_to_cast = "Stone Form"
                min_mana = 11
                target_type = None
            elif current_mysticism < 80:
                spell_to_cast = "Cleansing Winds"
                min_mana = 20
                target_type = "beneficial"
            elif current_mysticism < 95:
                spell_to_cast = "Hail Storm"
                min_mana = 40
                target_type = "harmful"
            else:
                spell_to_cast = "Rising Colossus"
                min_mana = 50
                target_type = None

            if heal_if_needed():
                API.Pause(CHECK_INTERVAL)
                continue

            if API.Player.Mana < min_mana:
                wait_for_full_mana()
            elif spell_to_cast == "Rising Colossus":
                existing_colossi = API.GetAllMobiles(name="Rising Colossus")
                existing_colossus_serials = set(
                    mobile.Serial for mobile in existing_colossi
                )

                API.CastSpell(spell_to_cast)
                if API.WaitForTarget("any", timeout=TARGET_TIMEOUT):
                    facing_offsets = {
                        "north": (0, -1),
                        "northeast": (1, -1),
                        "east": (1, 0),
                        "southeast": (1, 1),
                        "south": (0, 1),
                        "southwest": (-1, 1),
                        "west": (-1, 0),
                        "northwest": (-1, -1),
                    }
                    front_x, front_y = facing_offsets.get(
                        API.Player.Direction.lower(),
                        (0, -1),
                    )
                    API.TargetLandRel(front_x, front_y)
                    API.Pause(0.5)

                    current_colossi = API.GetAllMobiles(name="Rising Colossus")
                    summon = None
                    for mobile in current_colossi:
                        if mobile.Serial not in existing_colossus_serials:
                            summon = mobile
                            break

                    if summon:
                        API.ContextMenu(summon.Serial, "Release")
                        API.Pause(0.5)
                else:
                    API.CancelTarget()
            else:
                if target_type:
                    API.PreTarget(API.Player.Serial, target_type)

                API.CastSpell(spell_to_cast)

                if target_type:
                    if API.WaitForTarget("any", timeout=TARGET_TIMEOUT):
                        API.TargetSelf()
                    else:
                        API.CancelPreTarget()

            API.Pause(CHECK_INTERVAL)
# Confirm the Spellweaving quest is complete before continuing.
if mysticism_goal_reached and not API.StopRequested:
    spellweaving_quest = {"completed": None}

    def on_spellweaving_quest_continue():
        selected_index = spellweaving_quest_dropdown.GetSelectedIndex()
        spellweaving_quest["completed"] = selected_index == 0

    spellweaving_quest_gump = API.Gumps.CreateGump(True, True, False)
    spellweaving_quest_gump.SetRect(0, 0, 850, 250)
    add_popup_background(spellweaving_quest_gump, 850, 250)
    spellweaving_quest_gump.CenterXInViewPort()
    spellweaving_quest_gump.CenterYInViewPort()

    spellweaving_quest_line1 = centered_label(
        "Time for Spellweaving!",
        21,
        "#FFFFFF",
    )
    spellweaving_quest_line1.SetRect(15, 15, 820, 34)
    spellweaving_quest_gump.Add(spellweaving_quest_line1)

    spellweaving_quest_line2 = centered_label(
        "To unlock Spellweaving, complete a 5-quest chain by choosing one of these paths:",
        18,
        "#FFFFFF",
    )
    spellweaving_quest_line2.SetRect(15, 65, 820, 30)
    spellweaving_quest_gump.Add(spellweaving_quest_line2)

    spellweaving_quest_line3 = centered_label(
        "Patience in Heartwood or Discipline in Sanctuary.",
        18,
        "#FFFFFF",
    )
    spellweaving_quest_line3.SetRect(15, 100, 820, 30)
    spellweaving_quest_gump.Add(spellweaving_quest_line3)

    spellweaving_quest_line4 = centered_label(
        "Have you completed this task?",
        18,
        "#FFFFFF",
    )
    spellweaving_quest_line4.SetRect(15, 140, 820, 30)
    spellweaving_quest_gump.Add(spellweaving_quest_line4)

    spellweaving_quest_dropdown = API.Gumps.CreateDropDown(
        130,
        ["YES", "NO"],
        1,
    )
    spellweaving_quest_dropdown.SetPos(15, 185)
    spellweaving_quest_gump.Add(spellweaving_quest_dropdown)

    spellweaving_quest_button = API.Gumps.CreateSimpleButton("Continue", 150, 36)
    spellweaving_quest_button.SetPos(350, 185)
    spellweaving_quest_button.SetBackgroundColor(35, 110, 45)
    spellweaving_quest_gump.Add(spellweaving_quest_button)
    API.Gumps.AddControlOnClick(
        spellweaving_quest_button,
        on_spellweaving_quest_continue,
    )

    API.Gumps.AddGump(spellweaving_quest_gump)

    while spellweaving_quest["completed"] is None and not API.StopRequested:
        API.ProcessCallbacks()
        API.Pause(0.1)

    spellweaving_quest_gump.Dispose()

    if spellweaving_quest["completed"] is False and not API.StopRequested:
        return_notice = {"acknowledged": False}

        def acknowledge_return_notice():
            return_notice["acknowledged"] = True

        return_gump = API.Gumps.CreateGump(True, True, False)
        return_gump.SetRect(0, 0, 620, 130)
        add_popup_background(return_gump, 620, 130)
        return_gump.CenterXInViewPort()
        return_gump.CenterYInViewPort()

        return_message = centered_label(
            "Please come back when this task is completed.",
            20,
            "#FFFFFF",
        )
        return_message.SetRect(10, 20, 600, 36)
        return_gump.Add(return_message)

        return_button = API.Gumps.CreateSimpleButton("Close", 140, 32)
        return_button.SetPos(240, 75)
        return_button.SetBackgroundColor(138, 3, 3)
        return_gump.Add(return_button)
        API.Gumps.AddControlOnClick(return_button, acknowledge_return_notice)
        API.Gumps.AddGump(return_gump)

        while not return_notice["acknowledged"] and not API.StopRequested:
            API.ProcessCallbacks()
            API.Pause(0.1)

        return_gump.Dispose()
    elif spellweaving_quest["completed"] is True:
        API.SysMsg("Spellweaving quest completion confirmed.")

        spellweaving = API.GetSkill("Spellweaving")
        current_spellweaving = spellweaving.Value if spellweaving else 0

        if current_spellweaving >= 50:
            show_spellweaving_50_milestone()
        if current_spellweaving >= 100:
            show_spellweaving_100_milestone()
        if current_spellweaving >= 120:
            show_spellweaving_120_milestone()

        if not spellweaving:
            API.SysMsg("Could not read Spellweaving skill.")
        elif current_spellweaving < 20 and not API.StopRequested:
            arcane_circle_notice = {"acknowledged": False}

            def acknowledge_arcane_circle_notice():
                arcane_circle_notice["acknowledged"] = True

            arcane_circle_gump = API.Gumps.CreateGump(True, True, False)
            viewport = API.GetViewportBounds()
            arcane_circle_gump.SetRect(
                viewport.X + (viewport.Width - 760) // 2,
                viewport.Y + viewport.Height // 4,
                760,
                170,
            )
            add_popup_background(arcane_circle_gump, 760, 170)

            arcane_circle_line1 = centered_label(
                "Arcane Circle requires you to stand on an Arcane Circle,",
                20,
                "#FFFFFF",
            )
            arcane_circle_line1.SetRect(10, 20, 740, 32)
            arcane_circle_gump.Add(arcane_circle_line1)

            arcane_circle_line2 = centered_label(
                "Pentagram, or Abattoir.",
                20,
                "#FFFFFF",
            )
            arcane_circle_line2.SetRect(10, 58, 740, 32)
            arcane_circle_gump.Add(arcane_circle_line2)

            arcane_circle_line3 = centered_label(
                "Click Continue when you are standing in position and ready.",
                18,
                "#FFFFFF",
            )
            arcane_circle_line3.SetRect(10, 96, 740, 30)
            arcane_circle_gump.Add(arcane_circle_line3)

            arcane_circle_button = API.Gumps.CreateSimpleButton(
                "Continue",
                140,
                32,
            )
            arcane_circle_button.SetPos(310, 130)
            arcane_circle_button.SetBackgroundColor(35, 110, 45)
            arcane_circle_gump.Add(arcane_circle_button)
            API.Gumps.AddControlOnClick(
                arcane_circle_button,
                acknowledge_arcane_circle_notice,
            )
            API.Gumps.AddGump(arcane_circle_gump)

            while (
                not arcane_circle_notice["acknowledged"]
                and not API.StopRequested
            ):
                API.ProcessCallbacks()
                API.Pause(0.1)

            arcane_circle_gump.Dispose()

            while not API.StopRequested:
                spellweaving = API.GetSkill("Spellweaving")
                current_spellweaving = spellweaving.Value if spellweaving else 0

                if not spellweaving:
                    API.SysMsg("Could not read Spellweaving skill.")
                    break

                if current_spellweaving >= 20:
                    API.SysMsg("Spellweaving reached 20.0.")
                    break

                # Arcane Circle costs 24 mana on UOAlive.
                if heal_if_needed():
                    API.Pause(CHECK_INTERVAL)
                    continue
                elif API.Player.Mana < 24:
                    wait_for_full_mana()
                else:
                    API.CastSpell("Arcane Circle")
                    API.Pause(CHECK_INTERVAL)

        if not API.StopRequested:
            spellweaving = API.GetSkill("Spellweaving")
            current_spellweaving = spellweaving.Value if spellweaving else 0

            if not spellweaving:
                API.SysMsg("Could not read Spellweaving skill.")
            elif 20 <= current_spellweaving < 33:
                weapon_notice = {"acknowledged": False}

                def acknowledge_weapon_notice():
                    weapon_notice["acknowledged"] = True

                weapon_gump = API.Gumps.CreateGump(True, True, False)
                weapon_gump.SetRect(0, 0, 500, 130)
                add_popup_background(weapon_gump, 500, 130)
                weapon_gump.CenterXInViewPort()
                weapon_gump.CenterYInViewPort()

                weapon_message = centered_label(
                    "Equip any melee weapon before training Immolating Weapon.",
                    19,
                    "#FFFFFF",
                )
                weapon_message.SetRect(10, 20, 480, 32)
                weapon_gump.Add(weapon_message)

                weapon_button = API.Gumps.CreateSimpleButton("Continue", 140, 32)
                weapon_button.SetPos(180, 75)
                weapon_button.SetBackgroundColor(35, 110, 45)
                weapon_gump.Add(weapon_button)
                API.Gumps.AddControlOnClick(
                    weapon_button,
                    acknowledge_weapon_notice,
                )
                API.Gumps.AddGump(weapon_gump)

                while not weapon_notice["acknowledged"] and not API.StopRequested:
                    API.ProcessCallbacks()
                    API.Pause(0.1)

                weapon_gump.Dispose()

                while not API.StopRequested:
                    spellweaving = API.GetSkill("Spellweaving")
                    current_spellweaving = spellweaving.Value if spellweaving else 0

                    if not spellweaving:
                        API.SysMsg("Could not read Spellweaving skill.")
                        break

                    if current_spellweaving >= 33:
                        API.SysMsg("Spellweaving reached 33.0.")
                        break

                    # Immolating Weapon costs 32 mana on UOAlive.
                    if heal_if_needed():
                        API.Pause(CHECK_INTERVAL)
                        continue
                    elif API.Player.Mana < 32:
                        wait_for_full_mana()
                    else:
                        API.CastSpell("Immolating Weapon")
                        API.Pause(CHECK_INTERVAL)

        if not API.StopRequested:
            spellweaving = API.GetSkill("Spellweaving")
            current_spellweaving = spellweaving.Value if spellweaving else 0

            if not spellweaving:
                API.SysMsg("Could not read Spellweaving skill.")
            elif 33 <= current_spellweaving < min(44, Goal):
                train_spellweaving_band(44, "Reaper Form", 34)

        if not API.StopRequested:
            spellweaving = API.GetSkill("Spellweaving")
            current_spellweaving = spellweaving.Value if spellweaving else 0

            if not spellweaving:
                API.SysMsg("Could not read Spellweaving skill.")
            elif 44 <= current_spellweaving < min(60, Goal):
                while not API.StopRequested:
                    spellweaving = API.GetSkill("Spellweaving")
                    if not spellweaving:
                        API.SysMsg("Could not read Spellweaving skill.")
                        break

                    current_spellweaving = spellweaving.Value
                    if current_spellweaving >= 50:
                        show_spellweaving_50_milestone()
                    if current_spellweaving >= 100:
                        show_spellweaving_100_milestone()
                    if current_spellweaving >= 120:
                        show_spellweaving_120_milestone()

                    if current_spellweaving >= min(60, Goal):
                        API.SysMsg(
                            "Spellweaving reached "
                            + str(min(60, Goal))
                            + ".0."
                        )
                        break

                    if heal_if_needed():
                        API.Pause(CHECK_INTERVAL)
                        continue
                    elif API.Player.Mana < 10:
                        wait_for_full_mana()
                    else:
                        existing_serials = set(
                            mobile.Serial
                            for mobile in API.GetAllMobiles()
                        )
                        API.CastSpell("Summon Fey")
                        API.Pause(0.5)

                        new_fey = []
                        for _ in range(10):
                            new_fey = []
                            for mobile in API.GetAllMobiles(
                                distance=1,
                                isGhost=False,
                            ):
                                if (
                                    mobile.Serial not in existing_serials
                                    and mobile.Distance <= 1
                                ):
                                    new_fey.append(mobile)

                            if new_fey or API.StopRequested:
                                break
                            API.Pause(0.2)

                        for summon in new_fey:
                            if API.StopRequested:
                                break

                            current_summon = API.FindMobile(summon.Serial)
                            if not current_summon:
                                continue

                            release_sent = API.ContextMenu(
                                current_summon.Serial,
                                "Release",
                            )
                            if not release_sent:
                                API.Pause(0.5)
                                release_sent = API.ContextMenu(
                                    current_summon.Serial,
                                    "Release",
                                )

                            if not release_sent:
                                API.SysMsg(
                                    "Could not find Release for summoned Fey "
                                    + "serial "
                                    + str(current_summon.Serial)
                                    + "."
                                )
                            API.Pause(0.5)

                    API.Pause(CHECK_INTERVAL)

        if not API.StopRequested:
            spellweaving = API.GetSkill("Spellweaving")
            current_spellweaving = spellweaving.Value if spellweaving else 0

            if not spellweaving:
                API.SysMsg("Could not read Spellweaving skill.")
            elif 60 <= current_spellweaving < min(74, Goal):
                train_spellweaving_band(74, "Essence of Wind", 40)

        if not API.StopRequested:
            spellweaving = API.GetSkill("Spellweaving")
            current_spellweaving = spellweaving.Value if spellweaving else 0

            if not spellweaving:
                API.SysMsg("Could not read Spellweaving skill.")
            elif 74 <= current_spellweaving < min(90, Goal):
                train_spellweaving_band(
                    90,
                    "Wildfire",
                    50,
                    target_self=True,
                )

        if not API.StopRequested:
            spellweaving = API.GetSkill("Spellweaving")
            current_spellweaving = spellweaving.Value if spellweaving else 0

            if not spellweaving:
                API.SysMsg("Could not read Spellweaving skill.")
            elif 90 <= current_spellweaving < Goal:
                train_spellweaving_band(
                    Goal,
                    "Word of Death",
                    50,
                    target_self=True,
                )
