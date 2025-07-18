# This is an example of how to move all items with a specific type(graphic) to your bank.
import API

# Set your item types (graphics) here, for example [0x0EED, 0x0F7A] for gold coins and bandages
ITEM_GRAPHICS = [0x0EED, 0x0F7A]

# Get the player's backpack and bank serials
backpack = API.Backpack
bank = API.Bank

# Find all items of the specified types in your backpack
items = []
for graphic in ITEM_GRAPHICS:
    items.extend(API.FindTypeAll(graphic, backpack))

if not items:
    API.SysMsg("No items found.")
else:
    API.SysMsg(f"Moving {len(items)} items to bank...")
    for item in items:
        API.QueMoveItem(item.Serial, bank)
    
    # Wait until all items have been moved
    while API.IsProcessingMoveQue():
        API.Pause(0.2)
    
    API.SysMsg("All items moved to bank!")
