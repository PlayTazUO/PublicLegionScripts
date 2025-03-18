import API

items = API.ItemsInContainer(API.Backpack)

API.SysMsg("Target your fish barrel", 32)
barrel = API.RequestTarget()


if len(items) > 0 and barrel:
    for item in items:
        data = API.ItemNameAndProps(item)
        if data and "An Exotic Fish" in data:
            API.MoveItem(item, barrel)
            API.Pause(0.75)
            
