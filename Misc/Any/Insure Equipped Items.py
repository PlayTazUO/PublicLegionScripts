import API

# A simple script to check and insure items in your backpack.

API.ClearIgnoreList()
API.HeadMsg('Checking for insured items', API.Player.Serial)

# Open context menu and select insurance option (option 6 = Toggle Item Insurance)
API.ContextMenu(API.Player.Serial, 6)

# Wait for target cursor to appear
if not API.WaitForTarget(timeout=10):
    API.SysMsg('Timed out waiting for target', 32)
else:
    # Find all items in backpack
    while True:
        # Find any item type (0 = all types) in backpack
        item = API.FindType(4294967295, API.Backpack.Serial)

        if not item:
            break

        # Request and get item properties
        API.RequestOPLData([item.Serial])
        props = API.ItemNameAndProps(item.Serial, wait=True, timeout=2)

        # Check if item is not already insured
        if 'Insured' not in props:
            # Wait for target cursor and target this item
            if API.WaitForTarget(timeout=10):
                API.Target(item.Serial)
                API.Pause(0.5)

        # Ignore this item so we don't find it again
        API.IgnoreObject(item.Serial)

API.CancelTarget()
