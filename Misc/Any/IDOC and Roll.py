import API
import time

# House sign graphic ID
HOUSE_SIGN_GRAPHIC = 0xBD2

# Keywords indicating decay in house properties
DECAY_KEYWORDS = ["Slightly Worn", "Somewhat Worn", "Fairly Worn", "Greatly Worn"]

# Approximate magenta hue
MAGENTA_HUE = 0x4D

# Main scanning loop (runs indefinitely in background)
while True:
    # Get player position
    player = API.Player
    px = player.X
    py = player.Y
    
    # Get all house signs within 12 tiles
    signs = API.GetItemsOnGround(12, HOUSE_SIGN_GRAPHIC)
    
    if signs is not None:
        for sign in signs:
            # Request name and properties
            props = API.ItemNameAndProps(sign.Serial, True, 1000)  # Wait up to 1 second
            
            # Check for decay
            decaying = any(keyword in props for keyword in DECAY_KEYWORDS)
            
            if decaying:
                # Highlight the tile with magenta
                API.MarkTile(sign.X, sign.Y, MAGENTA_HUE, 0)
                
                # Calculate simple cardinal direction
                dx = sign.X - px
                dy = sign.Y - py
                if abs(dx) > abs(dy):
                    direction = "East" if dx > 0 else "West"
                else:
                    direction = "North" if dy > 0 else "South"
                
                # Post overhead message on the sign
                msg = f"Go {direction} to decaying house!"
                API.HeadMsg(msg, sign.Serial, 0x0026)  # Green text
    
    # Pause before next scan to avoid overload
    time.sleep(10)
