import API

API.SysMsg('Moving ores to your pack animal, target your pack animal')

# Prompt user to target their pack animal
packhorse = API.RequestTarget(timeout=30)

if not packhorse:
    API.SysMsg('No pack animal targeted, script cancelled', 32)
else:
    # Define ore graphics
    # May be missing some graphics here - add more as needed
    ores = [
        0x19B9,  # Ore graphic 1
        0x19B8   # Ore graphic 2
    ]

    for ore in ores:
        # Find and move all ore of this type from backpack to pack animal
        while not API.StopRequested:
            item = API.FindType(ore, API.Backpack.Serial)
            if not item:
                break

            API.MoveItem(item.Serial, packhorse)
            API.Pause(1.5)  # Wait 1.5 seconds between moves

    API.SysMsg('Done')
