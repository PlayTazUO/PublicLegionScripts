"""
SlayerBar Script
Purpose: Creates a gump interface for quickly switching between slayer weapons
Author: Ported from Dorana's original script by ChatGPT to Legion
"""

import API
import re

# Global variables
last_gem = None
current_gump = None
slayer_items = []
slayer_button_map = []

# -----------------------------
# Slayer Definitions
# -----------------------------
class SlayerType:
    None_ = 20744
    Repond = 2277
    Undead = 20486
    Reptile = 21282
    Dragon = 21010
    Arachnid = 20994
    Spider = 20994
    Elemental = 24014
    AirElemental = 2299
    FireElemental = 2302
    WaterElemental = 2303
    EarthElemental = 2301
    BloodElemental = 20993
    Demon = 2300
    Fey = 23006
    Eodon = 24011
    Unknown = 24015

SLAYER_ORDER = [
    SlayerType.None_,
    SlayerType.Repond,
    SlayerType.Undead,
    SlayerType.Reptile,
    SlayerType.Dragon,
    SlayerType.Arachnid,
    SlayerType.Spider,
    SlayerType.Elemental,
    SlayerType.AirElemental,
    SlayerType.FireElemental,
    SlayerType.WaterElemental,
    SlayerType.EarthElemental,
    SlayerType.BloodElemental,
    SlayerType.Demon,
    SlayerType.Fey,
    SlayerType.Eodon,
]

IGNORED_CONTAINER_NAMES = [
    "bag of sending",
    "magical trapped pouch 30 charges",
    "bento lunch box",
    "runebook strap"
]

# -----------------------------
# Core Utilities
# -----------------------------

def should_continue():
    """Check if the script should continue running."""
    try:
        # This will raise an exception if the thread has been interrupted
        # or if the script has been stopped
        return not API.Player.IsDead
    except:
        return False

def detect_active_skill():
    raw_skills = {
        "Swordsmanship": API.GetSkill("Swordsmanship"),
        "Macefighting": API.GetSkill("Macefighting"),
        "Fencing": API.GetSkill("Fencing"),
        "Archery": API.GetSkill("Archery"),
        "Throwing": API.GetSkill("Throwing"),
        "Magery": API.GetSkill("Magery"),
    }

    skill_values = {name: skill.Value for name, skill in raw_skills.items() if skill is not None}

    if not skill_values:
        API.SysMsg("No valid skills found.", 33)
        API.Stop()

    highest_skill = max(skill_values, key=skill_values.get)
    return highest_skill

def find_equipped_weapon():
    """Find the currently equipped weapon (not shield)."""
    two_handed = API.FindLayer("TwoHanded")
    one_handed = API.FindLayer("OneHanded")
    
    # Check if the equipped item is actually a weapon, not a shield
    for weapon in [two_handed, one_handed]:
        if weapon:
            weapon_name = weapon.Name.lower()
            
            # Skip if it's clearly a shield
            if "shield" in weapon_name or "buckler" in weapon_name:
                continue
            
            # Check if it's a weapon by looking for weapon keywords in the name
            weapon_keywords = ["sword", "axe", "mace", "bow", "crossbow", "dagger", "spear", "staff", "club", "hammer", "katana", "scimitar", "broadsword", "longsword", "shortsword", "warhammer", "battleaxe", "halberd", "pike", "glaive", "scythe", "whip", "fist", "fists", "spellbook", "compendium", "grimoire"]
            
            if any(keyword in weapon_name for keyword in weapon_keywords):
                return weapon
            
            # Additional check: look at item properties for weapon-related properties
            try:
                props = API.ItemNameAndProps(weapon.Serial, wait=True)
                if props:
                    props_lower = props.lower()
                    # Check for weapon-related properties
                    if any(prop in props_lower for prop in ["slayer", "damage", "durability", "weapon", "swing", "thrust", "shoot"]):
                        return weapon
            except:
                pass
    
    return None

def is_container(item):
    try:
        API.ItemsInContainer(item.Serial)
        return True
    except:
        return False

def is_spellbook(name):
    name = name.lower()
    return any(term in name for term in ["spellbook", "scrapper's compendium", "juo'nar's grimoire"])

def slayer_type_from_props(props):
    props = props.lower()
    if props == "silver":
        props = "undead slayer"
    for s in SLAYER_ORDER:
        sname = re.sub(r'(?<!^)(?=[A-Z])', ' ', [k for k, v in SlayerType.__dict__.items() if v == s][0]).lower()
        if sname.replace(" ", "") in props.replace(" ", ""):
            return s
    return SlayerType.Unknown

def create_slayer_filter(skill):
    skill_lower = skill.lower()
    def is_valid(item):
        # Only check items that might be weapons or spellbooks
        item_name = item.Name.lower()
        weapon_keywords = ["sword", "axe", "mace", "bow", "crossbow", "dagger", "spear", "staff", "club", "hammer", "katana", "scimitar", "broadsword", "longsword", "shortsword", "warhammer", "battleaxe", "halberd", "pike", "glaive", "scythe", "whip", "fist", "fists", "spellbook", "compendium", "grimoire"]
        
        if not any(keyword in item_name for keyword in weapon_keywords):
            return False
            
        props = API.ItemNameAndProps(item.Serial, wait=True)
        if not props:
            return False
        props = props.lower()
        if "slayer" not in props and "silver" not in props:
            return False
        is_valid_item = is_spellbook(item.Name) if skill == "Magery" else skill_lower in props
        return is_valid_item
    return is_valid

def find_all_valid_slayer_items(container, slayer_filter, slayer_list=None):
    if slayer_list is None:
        slayer_list = []
    try:
        contents = API.ItemsInContainer(container.Serial)
    except:
        return slayer_list
    for item in contents:
        if slayer_filter(item):
            slayer_list.append(item)
        if is_container(item):
            name = item.Name.lower()
            if all(ignored not in name for ignored in IGNORED_CONTAINER_NAMES):
                find_all_valid_slayer_items(item, slayer_filter, slayer_list)
    return slayer_list

# -----------------------------
# Slayer List Setup
# -----------------------------
def set_slayer_items(slayer_filter):
    slayer_items.clear()
    
    # Get the backpack object properly
    backpack = API.FindLayer("Backpack")
    if not backpack:
        API.SysMsg("No backpack found!", 33)
        return
        
    all_sources = find_all_valid_slayer_items(backpack, slayer_filter)
    
    held = find_equipped_weapon()
    if held and slayer_filter(held):
        all_sources.append(held)

    for item in all_sources:
        props = API.ItemNameAndProps(item.Serial, wait=True)
        if not props:
            continue
        for line in props.splitlines():
            if "slayer" in line.lower() or "silver" in line.lower():
                stype = slayer_type_from_props(line)
                slayer_items.append(SlayerItem(item.Name, item.Serial, stype))
                break

# -----------------------------
# Gump Rendering
# -----------------------------
def draw_gem_for_active():
    """Draw a gem indicator for the currently equipped weapon."""
    global last_gem
    if last_gem:
        try:
            last_gem.Dispose()
        except:
            pass  # Silently handle disposal errors
        last_gem = None
    
    active = find_equipped_weapon()
    if not active:
        return
        
    for i, item in enumerate(slayer_items):
        if item.serial == active.Serial:
            gem = API.CreateGumpItemPic(10542, 13, 13)
            gem.SetX(i * 60 + 23)
            gem.SetY(0)
            current_gump.Add(gem)
            last_gem = gem
            break

def draw_slayer_gump():
    """Create and display the slayer weapon selection gump."""
    global current_gump, slayer_button_map
    slayer_button_map.clear()

    if not slayer_items:
        API.SysMsg("No slayer weapons found!", 33)
        return

    current_gump = API.CreateGump(True, True, False)  # acceptMouseInput, canMove, keepOpen
    gump_width = len(slayer_items) * 60 + 30  # Extra space for close button
    current_gump.SetWidth(gump_width)
    current_gump.SetHeight(55)
    current_gump.SetX(500)
    current_gump.SetY(500)

    # Background
    bg = API.CreateGumpColorBox(0.8, "#000000")
    bg.SetWidth(gump_width)
    bg.SetHeight(55)
    current_gump.Add(bg)

    # Create buttons for each slayer weapon
    for i, item in enumerate(slayer_items):
        btn = API.CreateGumpButton("", normal=item.slayer, pressed=item.slayer, hover=item.slayer)
        btn.SetX(i * 60 + 5)
        btn.SetY(5)
        btn.SetWidth(50)
        btn.SetHeight(45)
        current_gump.Add(btn)
        slayer_button_map.append((item, btn))

    # Add close button
    close_btn = API.CreateGumpButton("X", hue=946, normal=0x00EF, pressed=0x00F0, hover=0x00EE)
    close_btn.SetX(len(slayer_items) * 60 + 5)
    close_btn.SetY(5)
    close_btn.SetWidth(20)
    close_btn.SetHeight(20)
    current_gump.Add(close_btn)
    slayer_button_map.append((None, close_btn))  # None item means close button

    draw_gem_for_active()
    API.AddGump(current_gump)
    API.SysMsg(f"Slayer bar created with {len(slayer_items)} weapons. Click X to close.", 946)

# -----------------------------
# Equip Logic
# -----------------------------
def equip_slayer(item):
    """Equip the selected slayer weapon by moving current weapon to backpack first."""
    held = find_equipped_weapon()
    if held and held.Serial == item.serial:
        return
    
    # Check if the target item is still available
    target_item = API.FindItem(item.serial)
    if not target_item:
        API.SysMsg(f"Item {item.name} not found!", 33)
        return
    
    # If we have a weapon equipped, move it to backpack first
    if held:
        # Get backpack reference
        backpack = API.FindLayer("Backpack")
        if not backpack:
            API.SysMsg("No backpack found!", 33)
            return
        
        # Move current weapon to backpack
        API.MoveItem(held.Serial, backpack.Serial, 1)
        API.Pause(0.5)
    
    # Now equip the new weapon
    API.EquipItem(item.serial)
    API.Pause(0.5)
    
    draw_gem_for_active()

# -----------------------------
# Main Loop
# -----------------------------
def run_click_loop():
    """Main loop to handle button clicks and update the gump."""
    while should_continue():
        try:
            # Process UI callbacks for button interactions
            API.ProcessCallbacks()
            
            # Check for button clicks
            for item, button in slayer_button_map:
                if button.HasBeenClicked():  # Use HasBeenClicked() instead of IsClicked
                    if item is None:  # Close button clicked
                        return  # Exit the loop to stop the script
                    else:
                        equip_slayer(item)
                    break  # Only handle one click per loop iteration
            
            API.Pause(0.1)
            
        except Exception as e:
            API.SysMsg(f"Click loop error: {str(e)}", 33)
            API.Pause(1)

# -----------------------------
# SlayerItem Class
# -----------------------------
class SlayerItem:
    def __init__(self, name, serial, slayer_type):
        self.name = name
        self.serial = serial
        self.slayer = slayer_type

# -----------------------------
# Main Script Function
# -----------------------------
def main():
    """Main script execution with proper error handling."""
    try:
        # Clean up any existing gump
        API.CloseGump(0xFADED123)
        
        # Detect active skill and setup
        active_skill = detect_active_skill()
        slayer_filter = create_slayer_filter(active_skill)
        set_slayer_items(slayer_filter)
        
        if not slayer_items:
            API.SysMsg("No slayer weapons found for your skill!", 33)
            return
            
        # Create and display the gump
        draw_slayer_gump()
        
        # Run the main click loop
        run_click_loop()
        
    except KeyboardInterrupt:
        # Handle script stop request gracefully
        API.SysMsg("SlayerBar script stopped by user", 946)
    except SystemExit:
        # Handle API.Stop() calls
        API.SysMsg("SlayerBar script stopped", 946)
    except Exception as e:
        # Handle any other unexpected errors
        API.SysMsg(f"Fatal script error: {str(e)}", 33)
        API.Stop()
    finally:
        # Clean up
        if current_gump:
            try:
                current_gump.Dispose()
            except:
                pass

# Run the main function
main()
