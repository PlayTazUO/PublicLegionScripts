import API

items = API.ItemsInContainer(API.Backpack)

API.SysMsg("Target a forge", 32)
forge = API.RequestTarget()


if len(items) > 0 and forge:
    for item in items:
        data = API.ItemNameAndProps(item)
        if data and "Scrap Metal" in data:
            API.UseObject(item)
            API.WaitForTarget()
            API.Target(forge)
            API.Pause(0.75)
            
