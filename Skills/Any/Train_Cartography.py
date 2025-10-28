"""
Cartography Training Script for TazUO
Converted from RazorEnhanced format

Requirements:
1. A large supply of blank scrolls (NOT blank maps) - approximately 1000-1200 to go from 30-99.5
2. Multiple Mapmaker's Pens
3. A nearby trash can or container for disposal

Usage:
- Position yourself within reach of a trash can or disposal container
- The script will prompt you to select your container with scrolls and pens
- Then it will prompt you to select the trash can/disposal container

WARNING: Do NOT have any treasure maps in your inventory as they may be accidentally discarded
"""

import API

# Configuration
CARTOGRAPHY_SKILL_CAP = 99.5  # Maximum skill level to train to
MAPMAKER_PEN_ID = 0x0FBF      # Mapmaker's pen graphic ID
BLANK_SCROLL_ID = 0x0EF3      # Blank scroll graphic ID
CRAFTED_MAP_ID = 0x14EC       # Crafted map graphic ID
CRAFT_GUMP_ID = 0x380624cd    # Cartography crafting gump ID

# Initialize variables
player = API.Player
backpack = API.Backpack

def get_cartography_skill():
    """Get current cartography skill level."""
    skill = API.GetSkill('Cartography')
    return skill.Value if skill else 0

def find_mapmaker_pen_in_backpack():
    """Find a mapmaker's pen in the backpack."""
    return API.FindType(MAPMAKER_PEN_ID, backpack)

def find_blank_scrolls_in_backpack():
    """Count blank scrolls in the backpack."""
    return API.FindType(BLANK_SCROLL_ID, backpack)

def find_mapmaker_pen_in_container():
    """Find a mapmaker's pen in the storage container."""
    return API.FindType(MAPMAKER_PEN_ID, container_id)

def find_blank_scrolls_in_container():
    """Find blank scrolls in the storage container."""
    return API.FindType(BLANK_SCROLL_ID, container_id)

def restock_mapmaker_pen():
    """Move a mapmaker's pen from container to backpack if needed."""
    # Check if we have a pen in backpack
    backpack_pen = find_mapmaker_pen_in_backpack()
    if backpack_pen:
        return True  # Already have a pen
    
    # Look for pen in container
    container_pen = find_mapmaker_pen_in_container()
    if container_pen:
        API.MoveItem(container_pen, backpack)
        API.Pause(1)  # Wait for move to complete
        API.SysMsg("Restocked mapmaker's pen from container", 88)
        return True
    
    return False  # No pens available

def restock_blank_scrolls(batch_size=100):
    """Move blank scrolls from container to backpack in batches."""
    # Check current backpack scroll count
    backpack_scrolls = find_blank_scrolls_in_backpack()
    backpack_count = backpack_scrolls.Amount if backpack_scrolls else 0
    
    # If we have enough scrolls, don't restock
    if backpack_count >= 50:  # Keep at least 50 in backpack
        return True
    
    # Find scrolls in container
    container_scrolls = find_blank_scrolls_in_container()
    if not container_scrolls:
        return False  # No scrolls in container
    
    # Calculate how many scrolls to move
    moved_count = min(batch_size - backpack_count, container_scrolls.Amount)
    
    # Move scrolls from container to backpack
    API.MoveItem(container_scrolls, backpack, moved_count)

    API.Pause(1)  # Wait for all moves to complete
    API.SysMsg(f"Restocked {moved_count} blank scrolls from container", 88)
    return True

def craft_maps():
    """Craft maps based on current skill level."""
    pen = find_mapmaker_pen_in_backpack()
    if pen is None:
        API.SysMsg("No mapmaker's pen found in backpack!", 33)
        return False
    
    # Use the mapmaker's pen
    API.UseObject(pen)
    API.Pause(0.2)
    
    # Wait for crafting gump
    if not API.WaitForGump(CRAFT_GUMP_ID, 3):
        API.SysMsg("Crafting gump not found!", 33)
        return False
    
    # Send the initial gump response
    API.ReplyGump(1, CRAFT_GUMP_ID)
    API.Pause(0.2)
    
    # Wait for the map selection gump
    if not API.WaitForGump(CRAFT_GUMP_ID, 3):
        API.SysMsg("Map selection gump not found!", 33)
        return False
    
    # Select appropriate map type based on skill level
    current_skill = get_cartography_skill()
    
    if current_skill < 50:
        # Local map
        API.ReplyGump(2, CRAFT_GUMP_ID)
    elif current_skill < 65:
        # City map  
        API.ReplyGump(22, CRAFT_GUMP_ID)
    elif current_skill < 70:
        # Sea chart
        API.ReplyGump(42, CRAFT_GUMP_ID)
    elif current_skill < CARTOGRAPHY_SKILL_CAP:
        # World map
        API.ReplyGump(62, CRAFT_GUMP_ID)
    
    API.Pause(2)
    
    # Look for crafted map and dispose of it
    crafted_map = API.FindType(CRAFTED_MAP_ID, backpack)
    if crafted_map:
        API.MoveItem(crafted_map, trash_container_id)
        API.Pause(2)
        API.SysMsg("Map crafted and disposed", 66)
        return True
    else:
        API.SysMsg("No crafted map found to dispose", 55)
        return False

def main():
    """Main training loop."""
    global container_id, trash_container_id
    
    API.SysMsg("Cartography Training Script Started", 66)
    API.SysMsg("WARNING: Remove all treasure maps from inventory!", 33)
    
    # Get container for materials
    API.SysMsg("Select your container for scrolls and pens", 66)
    API.HeadMsg("Select your container for scrolls and pens", player, 66)
    container_id = API.RequestTarget(10)
    
    if not container_id:
        API.SysMsg("No container selected. Stopping script.", 33)
        return
    
    # Get trash container
    API.SysMsg("Select your trash can or disposal container", 66)
    API.HeadMsg("Select your trash can or disposal container", player, 66)
    trash_container_id = API.RequestTarget(10)
    
    if not trash_container_id:
        API.SysMsg("No trash container selected. Stopping script.", 33)
        return
    
    API.SysMsg("Starting cartography training...", 66)
    
    # Main training loop
    while not API.StopRequested:
        current_skill = get_cartography_skill()
        
        # Check if we've reached the skill cap
        if current_skill >= CARTOGRAPHY_SKILL_CAP:
            API.SysMsg(f"Cartography skill cap reached: {current_skill}", 66)
            break
        
        # Restock materials if needed
        if not restock_mapmaker_pen():
            API.SysMsg("No mapmaker's pens available in container or backpack!", 33)
            break
        
        if not restock_blank_scrolls():
            # Check if we have any scrolls in backpack as fallback
            backpack_scrolls = find_blank_scrolls_in_backpack()
            if backpack_scrolls == 0:
                API.SysMsg("No blank scrolls available in container or backpack!", 33)
                break
        
        # Get current material counts for display
        backpack_scrolls = find_blank_scrolls_in_backpack()
        container_scrolls = find_blank_scrolls_in_container()
        container_scrolls_count = container_scrolls.Amount if container_scrolls else 0
        backpack_scrolls_count = backpack_scrolls.Amount if backpack_scrolls else 0

        # Display current status
        API.HeadMsg(f"Cartography: {current_skill:.1f} | BP Scrolls: {backpack_scrolls_count} | Container: {container_scrolls_count}", player, 88)

        # Craft a map
        if not craft_maps():
            API.SysMsg("Failed to craft map, pausing...", 33)
            API.Pause(1)
        
        # Brief pause between crafting attempts
        API.Pause(0.5)
    
    API.SysMsg("Cartography training complete!", 66)

# Start the script
main()
