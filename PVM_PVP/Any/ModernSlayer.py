"""
Modern SlayerBar Script.

Purpose: Creates a modern gump interface for quickly switching between slayer weapons
Author: Modern version of Dorana's original script using ModernGumps
"""

import re
from enum import IntEnum

import API


# Global variables
modern_gump = None
slayer_items = []
slayer_buttons = []
current_equipped = None

# Gump ID for cleanup
GUMP_ID = 0x11102010


# -----------------------------
# Custom Weapon Configuration
# -----------------------------
# Add custom non-slayer weapons here for quick switching
# Format: Serial numbers of weapons you want to include
CUSTOM_WEAPON_SERIALS = [
    # Example: 0x12345678, 0x87654321
    # Add your weapon serials here
    # Examples (uncomment and modify as needed):
    # 0x12345678,  # Your Katana
    # 0x87654321,  # Your Broadsword
    # 0x11111111,  # Your War Hammer
    0x77474195,  # hitlit khaldun
    0x58AA9AB6,  # all around whip
]


# -----------------------------
# Slayer Definitions
# -----------------------------
class SlayerType(IntEnum):
    """Enumeration of slayer types with their corresponding values."""
    
    NONE = 20744
    REPOND = 2277
    UNDEAD = 20486
    REPTILE = 21282
    DRAGON = 21010
    ARACHNID = 20993
    SPIDER = 20994
    ELEMENTAL = 24014
    AIR_ELEMENTAL = 2299
    FIRE_ELEMENTAL = 2302
    WATER_ELEMENTAL = 2303
    EARTH_ELEMENTAL = 2301
    BLOOD_ELEMENTAL = 20995
    DEMON = 2300
    FEY = 23006
    EODON = 24011
    UNKNOWN = 24015
    CUSTOM = 99999  # Special identifier for custom non-slayer weapons


SLAYER_ORDER = [
    SlayerType.REPOND,
    SlayerType.UNDEAD,
    SlayerType.REPTILE,
    SlayerType.DRAGON,
    SlayerType.ARACHNID,
    SlayerType.ELEMENTAL,
    SlayerType.AIR_ELEMENTAL,
    SlayerType.FIRE_ELEMENTAL,
    SlayerType.WATER_ELEMENTAL,
    SlayerType.EARTH_ELEMENTAL,
    SlayerType.BLOOD_ELEMENTAL,
    SlayerType.DEMON,
    SlayerType.FEY,
    SlayerType.EODON,
    SlayerType.UNKNOWN,
    SlayerType.CUSTOM,
]


IGNORED_CONTAINER_NAMES = [
    "bag of sending",
    "magical trapped pouch 30 charges",
    "bento lunch box",
    "runebook strap"
]


# -----------------------------
# Helper Functions
# -----------------------------
def get_weapon_serial(weapon_name):
    """
    Helper function to get weapon serial by name.
    
    Useful for finding serials to add to CUSTOM_WEAPON_SERIALS.
    
    Args:
        weapon_name (str): Name or partial name of the weapon to find
        
    Returns:
        int or None: Serial number of the weapon if found, None otherwise
    """
    backpack = API.FindLayer("Backpack")
    if not backpack:
        API.SysMsg("No backpack found!", 33)
        return None
        
    def find_weapon_recursive(container, target_name):
        """Recursively search containers for weapons."""
        try:
            contents = API.ItemsInContainer(container.Serial)
        except Exception:
            return None
            
        for item in contents:
            if target_name.lower() in item.Name.lower():
                # Check if it's a weapon
                weapon_keywords = [
                    "sword", "axe", "mace", "bow", "crossbow", "dagger", 
                    "spear", "staff", "club", "hammer", "katana", "scimitar", 
                    "broadsword", "longsword", "shortsword", "warhammer", 
                    "battleaxe", "halberd", "pike", "glaive", "scythe", 
                    "whip", "fist", "fists", "spellbook", "compendium", 
                    "grimoire"
                ]
                if any(keyword in item.Name.lower() for keyword in weapon_keywords):
                    return item.Serial
            
            # Check if it's a container and search recursively
            try:
                API.ItemsInContainer(item.Serial)
                result = find_weapon_recursive(item, target_name)
                if result:
                    return result
            except Exception:
                # Skip items that can't be checked (e.g., locked containers)
                continue
                
        return None
    
    serial = find_weapon_recursive(backpack, weapon_name)
    if serial:
        API.SysMsg(f"Found {weapon_name}: Serial = 0x{serial:X}", 68)
        return serial
    else:
        API.SysMsg(f"Weapon '{weapon_name}' not found!", 33)
        return None


# -----------------------------
# Core Utilities
# -----------------------------
def detect_active_skill():
    """
    Detect the player's highest combat skill.
    
    Returns:
        str or None: Name of the highest combat skill, None if no valid skills
    """
    raw_skills = {
        "Swordsmanship": API.GetSkill("Swordsmanship"),
        "Macefighting": API.GetSkill("Macefighting"),
        "Fencing": API.GetSkill("Fencing"),
        "Archery": API.GetSkill("Archery"),
        "Throwing": API.GetSkill("Throwing"),
        "Magery": API.GetSkill("Magery"),
    }

    skill_values = {
        name: skill.Value 
        for name, skill in raw_skills.items() 
        if skill is not None
    }

    if not skill_values:
        API.SysMsg("No valid skills found.", 33)
        return None

    highest_skill = max(skill_values, key=skill_values.get)
    return highest_skill


def find_equipped_weapon():
    """
    Find the currently equipped weapon (not shield).
    
    Returns:
        Item or None: The equipped weapon if found, None otherwise
    """
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
            weapon_keywords = [
                "sword", "axe", "mace", "bow", "crossbow", "dagger", "spear", 
                "staff", "club", "hammer", "katana", "scimitar", "broadsword", 
                "longsword", "shortsword", "warhammer", "battleaxe", "halberd", 
                "pike", "glaive", "scythe", "whip", "fist", "fists", 
                "spellbook", "compendium", "grimoire"
            ]
            
            if any(keyword in weapon_name for keyword in weapon_keywords):
                return weapon
            
            # Additional check: look at item properties for weapon-related properties
            try:
                props = API.ItemNameAndProps(weapon.Serial, wait=True)
                if props:
                    props_lower = props.lower()
                    # Check for weapon-related properties
                    weapon_props = [
                        "slayer", "damage", "durability", "weapon", 
                        "swing", "thrust", "shoot"
                    ]
                    if any(prop in props_lower for prop in weapon_props):
                        return weapon
            except Exception:
                # Skip items that can't have properties checked
                continue
    
    return None


def is_container(item):
    """
    Check if an item is a container.
    
    Args:
        item: Item to check
        
    Returns:
        bool: True if item is a container, False otherwise
    """
    try:
        API.ItemsInContainer(item.Serial)
        return True
    except Exception:
        return False


def is_spellbook(name):
    """
    Check if an item is a spellbook.
    
    Args:
        name (str): Name of the item to check
        
    Returns:
        bool: True if item is a spellbook, False otherwise
    """
    name = name.lower()
    spellbook_terms = [
        "spellbook", "compendium", "grimoire", "tome", "ritual tome",
        "scrapper's compendium", "juo'nar's grimoire", "cultist's ritual tome",
        "necromancer spellbook", "mysticism spellbook", "spellweaving spellbook"
    ]
    
    
    return any(term in name for term in spellbook_terms)


def slayer_type_from_props(props):
    """
    Extract slayer type from item properties.
    
    Args:
        props (str): Item properties string
        
    Returns:
        SlayerType: The corresponding slayer type, or SlayerType.UNKNOWN
    """
    props = props.lower()
    
    # Handle special case for silver
    if props == "silver":
        return SlayerType.UNDEAD
    
    # Direct mapping of slayer names to enum values
    slayer_mappings = {
        "undead slayer": SlayerType.UNDEAD,
        "dragon slayer": SlayerType.DRAGON,
        "elemental slayer": SlayerType.ELEMENTAL,
        "demon slayer": SlayerType.DEMON,
        "repond slayer": SlayerType.REPOND,
        "reptile slayer": SlayerType.REPTILE,
        "arachnid slayer": SlayerType.ARACHNID,
        "spider slayer": SlayerType.SPIDER,
        "fey slayer": SlayerType.FEY,
        "eodon slayer": SlayerType.EODON,
        "air elemental slayer": SlayerType.AIR_ELEMENTAL,
        "fire elemental slayer": SlayerType.FIRE_ELEMENTAL,
        "water elemental slayer": SlayerType.WATER_ELEMENTAL,
        "earth elemental slayer": SlayerType.EARTH_ELEMENTAL,
        "blood elemental slayer": SlayerType.BLOOD_ELEMENTAL,
    }
    
    # Check for exact matches first
    for slayer_name, slayer_type in slayer_mappings.items():
        if slayer_name in props:
            return slayer_type
    
    # Fallback to partial matching
    for slayer_name, slayer_type in slayer_mappings.items():
        # Remove spaces and check if the slayer type is contained in props
        slayer_clean = slayer_name.replace(" ", "")
        props_clean = props.replace(" ", "")
        if slayer_clean in props_clean:
            return slayer_type
    
    return SlayerType.UNKNOWN


def create_slayer_filter(skill):
    """
    Create a filter function for valid slayer items and custom weapons.
    
    Args:
        skill (str): Combat skill to filter by
        
    Returns:
        function: Filter function that takes an item and returns bool
    """
    skill_lower = skill.lower()
    
    def is_valid(item):
        """Check if item is a valid slayer weapon or custom weapon."""
        # Only check items that might be weapons or spellbooks
        item_name = item.Name.lower()
        weapon_keywords = [
            "sword", "axe", "mace", "bow", "crossbow", "dagger", "spear", 
            "staff", "club", "hammer", "katana", "scimitar", "broadsword", 
            "longsword", "shortsword", "warhammer", "battleaxe", "halberd", 
            "pike", "glaive", "scythe", "whip", "fist", "fists", 
            "spellbook", "compendium", "grimoire", "tome"
        ]
        
        
        if not any(keyword in item_name for keyword in weapon_keywords):
            return False
        
        # Check if this is a custom weapon first (by serial)
        if item.Serial in CUSTOM_WEAPON_SERIALS:
            return True
        
        # For Magery, check if it's a spellbook first
        if skill == "Magery":
            is_spell = is_spellbook(item.Name)
            if not is_spell:
                return False
            
            # Only accept spellbooks with slayer properties
            props = API.ItemNameAndProps(item.Serial, wait=True)
            if not props:
                return False
            props = props.lower()
            # Only accept spellbooks that have slayer properties
            return "slayer" in props or "silver" in props
            
        # For other skills, check for slayer properties
        props = API.ItemNameAndProps(item.Serial, wait=True)
        if not props:
            return False
        props = props.lower()
        if "slayer" not in props and "silver" not in props:
            return False
        
        # Check if the skill matches the weapon properties
        return skill_lower in props
    
    return is_valid


def find_all_valid_slayer_items(container, slayer_filter, slayer_list=None):
    """
    Recursively find all valid slayer items in containers.
    
    Args:
        container: Container to search
        slayer_filter: Filter function for valid items
        slayer_list: List to append found items to
        
    Returns:
        list: List of valid slayer items found
    """
    if slayer_list is None:
        slayer_list = []
    try:
        contents = API.ItemsInContainer(container.Serial)
    except Exception:
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
    """
    Find and categorize all slayer weapons.
    
    Args:
        slayer_filter: Filter function for valid slayer items
    """
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
        # Check if this is a custom weapon first (by serial)
        if item.Serial in CUSTOM_WEAPON_SERIALS:
            slayer_items.append(
                SlayerItem(item.Name, item.Serial, SlayerType.CUSTOM)
            )
            continue
        
        # Check if this is a spellbook (for Magery skill)
        if is_spellbook(item.Name):
            # Check if the spellbook has slayer properties
            props = API.ItemNameAndProps(item.Serial, wait=True)
            if props:
                slayer_found = False
                for line in props.splitlines():
                    if "slayer" in line.lower() or "silver" in line.lower():
                        stype = slayer_type_from_props(line)
                        slayer_items.append(
                            SlayerItem(item.Name, item.Serial, stype)
                        )
                        slayer_found = True
                        break
                
                # If no slayer properties found, skip this regular spellbook
                # (only slayer spellbooks should make it through the filter now)
            continue
            
        # Process slayer weapons
        props = API.ItemNameAndProps(item.Serial, wait=True)
        if not props:
            continue
        for line in props.splitlines():
            if "slayer" in line.lower() or "silver" in line.lower():
                stype = slayer_type_from_props(line)
                slayer_items.append(
                    SlayerItem(item.Name, item.Serial, stype)
                )
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
    skill_label = API.CreateGumpTTFLabel(
        f"Active Skill: {active_skill}", 14, "#00FF00", "alagard"
    )
    skill_label.SetPos(20, 45)
    modern_gump.Add(skill_label)
    
    # Add status label
    status_label = API.CreateGumpTTFLabel(
        "Status: Ready", 14, "#FFFFFF", "alagard"
    )  # White TTF
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
        display_name = (
            item.name[:18] + "..." if len(item.name) > 18 else item.name
        )
        button_label = API.CreateGumpTTFLabel(
            display_name, 11, "#000000", "alagard"
        )
        button_label.SetPos(x_pos + 5, y_pos + 20)
        modern_gump.Add(button_label)
        
        # Add slayer type indicator with TTF
        slayer_name = get_slayer_name(item.slayer)
        slayer_label = API.CreateGumpTTFLabel(
            slayer_name, 10, "#00FF00", "alagard"
        )
        slayer_label.SetPos(x_pos + 5, y_pos + 5)
        modern_gump.Add(slayer_label)
        
        # Make the button background clickable
        API.AddControlOnClick(
            button_bg, lambda item=item: equip_slayer_weapon(item), True
        )
        
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
    """
    Get color for slayer type.
    
    Args:
        slayer_type (SlayerType): The slayer type
        
    Returns:
        str: Hex color code for the slayer type
    """
    colors = {
        SlayerType.UNDEAD: "#8E44AD",      # Purple
        SlayerType.DRAGON: "#E74C3C",      # Red
        SlayerType.ELEMENTAL: "#3498DB",   # Blue
        SlayerType.DEMON: "#2C3E50",      # Dark blue
        SlayerType.REPOND: "#F39C12",     # Orange
        SlayerType.REPTILE: "#27AE60",    # Green
        SlayerType.ARACHNID: "#8B4513",   # Brown
        SlayerType.SPIDER: "#8B4514",     # Brown
        SlayerType.FEY: "#FF69B4",        # Pink
        SlayerType.EODON: "#00CED1",      # Dark turquoise
        SlayerType.CUSTOM: "#FFD700",     # Gold for custom weapons
    }
    return colors.get(slayer_type, "#95A5A6")  # Default gray


def get_slayer_name(slayer_type):
    """
    Get display name for slayer type.
    
    Args:
        slayer_type (SlayerType): The slayer type
        
    Returns:
        str: Display name for the slayer type
    """
    names = {
        SlayerType.UNDEAD: "Undead",
        SlayerType.DRAGON: "Dragon",
        SlayerType.ELEMENTAL: "Elemental",
        SlayerType.DEMON: "Demon",
        SlayerType.REPOND: "Repond",
        SlayerType.REPTILE: "Reptile",
        SlayerType.ARACHNID: "Arachnid",
        SlayerType.SPIDER: "Spider",
        SlayerType.FEY: "Fey",
        SlayerType.EODON: "Eodon",
        SlayerType.CUSTOM: "Custom",
    }
    return names.get(slayer_type, "Unknown")


# -----------------------------
# Button Handlers
# -----------------------------
def equip_slayer_weapon(item):
    """
    Equip the selected slayer weapon.
    
    Args:
        item (SlayerItem): The slayer item to equip
    """
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
            truncated_name = (
                item.name[:16] + "..." if len(item.name) > 16 else item.name
            )
            button_label.Text = f"* {truncated_name}"  # Add star and truncate
        else:
            # Normal text
            truncated_name = (
                item.name[:18] + "..." if len(item.name) > 18 else item.name
            )
            button_label.Text = truncated_name


# -----------------------------
# SlayerItem Class
# -----------------------------
class SlayerItem:
    """Represents a slayer weapon item."""
    
    def __init__(self, name, serial, slayer_type):
        """
        Initialize a SlayerItem.
        
        Args:
            name (str): Name of the weapon
            serial (int): Serial number of the weapon
            slayer_type (SlayerType): Type of slayer weapon
        """
        self.name = name
        self.serial = serial
        self.slayer = slayer_type


# -----------------------------
# Main Script Function
# -----------------------------
def main():
    """Main script execution with proper error handling."""
    global modern_gump
    
    # Helper: To find weapon serials for CUSTOM_WEAPON_SERIALS, uncomment and run:
    # get_weapon_serial("Your Weapon Name Here")
    
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
            except Exception:
                # Gump disposal failed, but continue cleanup
                modern_gump = None


# Start the script

main()
