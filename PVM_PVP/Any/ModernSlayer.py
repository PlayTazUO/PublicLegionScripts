"""
Modern SlayerBar Script
Purpose: Creates a modern gump interface for quickly switching between slayer weapons
Author: Modern version of Dorana's original script using ModernGumps
"""

import API
import re

# Global variables
modern_gump = None
slayer_items = []
slayer_buttons = []
current_equipped = None

# Gump ID for cleanup
GUMP_ID = 0x11102010

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
def detect_active_skill():
    """Detect the player's highest combat skill."""
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
        return None

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
    """Check if an item is a container."""
    try:
        API.ItemsInContainer(item.Serial)
        return True
    except:
        return False

def is_spellbook(name):
    """Check if an item is a spellbook."""
    name = name.lower()
    return any(term in name for term in ["spellbook", "scrapper's compendium", "juo'nar's grimoire"])

def slayer_type_from_props(props):
    """Extract slayer type from item properties."""
    props = props.lower()
    if props == "silver":
        props = "undead slayer"
    for s in SLAYER_ORDER:
        sname = re.sub(r'(?<!^)(?=[A-Z])', ' ', [k for k, v in SlayerType.__dict__.items() if v == s][0]).lower()
        if sname.replace(" ", "") in props.replace(" ", ""):
            return s
    return SlayerType.Unknown

def create_slayer_filter(skill):
    """Create a filter function for valid slayer items."""
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
    """Recursively find all valid slayer items in containers."""
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

def set_slayer_items(slayer_filter):
    """Find and categorize all slayer weapons."""
    global slayer_items
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
# Modern Gump Creation
# -----------------------------

def create_modern_slayer_gump():
    """Create the modern slayer gump with interactive buttons."""
    global modern_gump, slayer_buttons
    
    # Close any existing gump
    API.CloseGump(GUMP_ID)
    API.Pause(0.1)
    
    if not slayer_items:
        API.SysMsg("No slayer weapons found!", 33)
        return
    
    # Calculate gump dimensions
    num_items = len(slayer_items)
    buttons_per_row = 5
    rows = (num_items + buttons_per_row - 1) // buttons_per_row  # Ceiling division
    gump_width = max(600, min(buttons_per_row * 100 + 100, 900))  # Even wider buttons, max width
    gump_height = 200 + (rows - 1) * 50  # Adjust height based on rows
    
    # Create modern gump without resizing
    modern_gump = API.CreateModernGump(
        x=200, y=150, width=gump_width, height=gump_height,
        resizable=False, minWidth=300, minHeight=150
    )
    
    # Center the gump
    modern_gump.CenterXInViewPort()
    modern_gump.CenterYInViewPort()
    
    # Add background
    bg = API.CreateGumpColorBox(0.9, "#1a1a1a")
    bg.SetRect(0, 0, gump_width, gump_height)
    modern_gump.Add(bg)
    
    # Add title
    title = API.CreateGumpLabel("Modern Slayer Weapon Bar", 0x0481)  # Gold
    title.SetPos(20, 20)
    modern_gump.Add(title)
    
    # Add skill info
    active_skill = detect_active_skill()
    skill_label = API.CreateGumpTTFLabel(f"Active Skill: {active_skill}", 14, "#00FF00", "alagard")
    skill_label.SetPos(20, 45)
    modern_gump.Add(skill_label)
    
    # Add status label
    status_label = API.CreateGumpTTFLabel("Status: Ready", 14, "#FFFFFF", "alagard")  # White TTF
    status_label.SetPos(20, 70)
    modern_gump.Add(status_label)
    
    # Create slayer weapon buttons
    slayer_buttons.clear()
    button_x = 20
    button_y = 100
    buttons_per_row = 5
    current_row = 0
    
    for i, item in enumerate(slayer_items):
        # Calculate position
        if i > 0 and i % buttons_per_row == 0:
            current_row += 1
            button_x = 20
        
        x_pos = button_x + (i % buttons_per_row) * 100  # Increased spacing
        y_pos = button_y + current_row * 50
        
        # Create button background with different colors based on slayer type
        button_color = get_slayer_color(item.slayer)
        button_bg = API.CreateGumpColorBox(0.8, button_color)
        button_bg.SetRect(x_pos, y_pos, 90, 40)
        modern_gump.Add(button_bg)
        
        # Create button label with TTF (truncate long names)
        display_name = item.name[:18] + "..." if len(item.name) > 18 else item.name
        button_label = API.CreateGumpTTFLabel(display_name, 11, "#000000", "alagard")
        button_label.SetPos(x_pos + 5, y_pos + 20)
        modern_gump.Add(button_label)
        
        # Add slayer type indicator with TTF
        slayer_name = get_slayer_name(item.slayer)
        slayer_label = API.CreateGumpTTFLabel(slayer_name, 10, "#00FF00", "alagard")
        slayer_label.SetPos(x_pos + 5, y_pos + 5)
        modern_gump.Add(slayer_label)
        
        # Make the button background clickable
        API.AddControlOnClick(button_bg, lambda item=item: equip_slayer_weapon(item), True)
        
        # Store button reference for highlighting
        slayer_buttons.append((item, button_bg, button_label, slayer_label))
    
    # Add close button
    close_bg = API.CreateGumpColorBox(0.8, "#E74C3C")  # Red
    close_bg.SetRect(gump_width - 50, 20, 30, 30)
    modern_gump.Add(close_bg)
    
    close_label = API.CreateGumpTTFLabel("X", 14, "#FFFFFF", "alagard") 
    close_label.SetPos(gump_width - 40, 30)
    modern_gump.Add(close_label)
    
    API.AddControlOnClick(close_bg, close_gump, True)
    
    # Display the gump
    API.AddGump(modern_gump)
    API.SysMsg(f"Modern Slayer bar created with {len(slayer_items)} weapons!", 946)

def get_slayer_color(slayer_type):
    """Get color for slayer type."""
    colors = {
        SlayerType.Undead: "#8E44AD",      # Purple
        SlayerType.Dragon: "#E74C3C",      # Red
        SlayerType.Elemental: "#3498DB",   # Blue
        SlayerType.Demon: "#2C3E50",      # Dark blue
        SlayerType.Repond: "#F39C12",     # Orange
        SlayerType.Reptile: "#27AE60",    # Green
        SlayerType.Arachnid: "#8B4513",   # Brown
        SlayerType.Spider: "#8B4513",     # Brown
        SlayerType.Fey: "#FF69B4",        # Pink
        SlayerType.Eodon: "#00CED1",      # Dark turquoise
    }
    return colors.get(slayer_type, "#95A5A6")  # Default gray

def get_slayer_name(slayer_type):
    """Get display name for slayer type."""
    names = {
        SlayerType.Undead: "Undead",
        SlayerType.Dragon: "Dragon",
        SlayerType.Elemental: "Elemental",
        SlayerType.Demon: "Demon",
        SlayerType.Repond: "Repond",
        SlayerType.Reptile: "Reptile",
        SlayerType.Arachnid: "Arachnid",
        SlayerType.Spider: "Spider",
        SlayerType.Fey: "Fey",
        SlayerType.Eodon: "Eodon",
    }
    return names.get(slayer_type, "Unknown")

# -----------------------------
# Button Handlers
# -----------------------------
def equip_slayer_weapon(item):
    """Equip the selected slayer weapon."""
    global current_equipped
    
    held = find_equipped_weapon()
    if held and held.Serial == item.serial:
        API.SysMsg(f"{item.name} is already equipped!", 68)
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
    
    # Update current equipped
    current_equipped = item.serial
    
    # Update button highlighting
    update_button_highlighting()
    
    API.SysMsg(f"Equipped {item.name}!", 68)

def close_gump():
    """Close the gump and stop the script."""
    global modern_gump
    if modern_gump:
        modern_gump.Dispose()
        modern_gump = None
    API.Stop()
    API.SysMsg("Slayer bar closed!", 946)



def update_button_highlighting():
    """Update button highlighting to show currently equipped weapon."""
    global current_equipped
    
    # Find currently equipped weapon
    current_weapon = find_equipped_weapon()
    if current_weapon:
        current_equipped = current_weapon.Serial
    else:
        current_equipped = None
    
    # Update button highlighting by changing text content instead of color
    for item, button_bg, button_label, slayer_label in slayer_buttons:
        if current_equipped and item.serial == current_equipped:
            # Highlight equipped weapon with star prefix
            button_label.Text = f"* {item.name[:16]}{'...' if len(item.name) > 16 else ''}"  # Add star and truncate
        else:
            # Normal text
            button_label.Text = f"{item.name[:18]}{'...' if len(item.name) > 18 else ''}"

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
    global modern_gump
    
    try:
        # Detect active skill and setup
        active_skill = detect_active_skill()
        if not active_skill:
            API.SysMsg("No valid combat skills found!", 33)
            return
            
        slayer_filter = create_slayer_filter(active_skill)
        set_slayer_items(slayer_filter)
        
        if not slayer_items:
            API.SysMsg("No slayer weapons found for your skill!", 33)
            return
            
        # Create and display the modern gump
        create_modern_slayer_gump()
        
        # Main loop
        while not API.StopRequested:
            try:
                # Process UI callbacks for button interactions
                API.ProcessCallbacks()
                
                # Update highlighting periodically
                update_button_highlighting()
                
                API.Pause(0.1)  # Required pause
                
            except Exception as e:
                API.SysMsg(f"Script error: {str(e)}", 33)
                API.Pause(1)
                
    except KeyboardInterrupt:
        # Handle script stop request gracefully
        API.SysMsg("Modern Slayer script stopped by user", 946)
    except SystemExit:
        # Handle API.Stop() calls
        API.SysMsg("Modern Slayer script stopped", 946)
    except Exception as e:
        # Handle any other unexpected errors
        API.SysMsg(f"Fatal script error: {str(e)}", 33)
    finally:
        # Clean up
        if modern_gump:
            try:
                modern_gump.Dispose()
                modern_gump = None
            except:
                pass

# Start the script
main()
