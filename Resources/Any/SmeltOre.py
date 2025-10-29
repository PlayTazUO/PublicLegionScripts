import API

# Prompt user to target a forge
API.SysMsg('Target a forge')
forge = API.RequestTarget()

if not forge:
    API.SysMsg('Unable to find your forge')
else:
    # Ore types
    ores = [
        0x19B8,
        0x19B7,
        0x19B9,
        0x19BA
    ]

    while not API.StopRequested:
        # Find any ore type in backpack
        found_ore = None
        for ore_type in ores:
            found_ore = API.FindType(ore_type, API.Backpack)
            if found_ore:
                break

        if not found_ore:
            break

        # Use the ore
        API.UseObject(found_ore)

        # Wait for targeting cursor
        if API.WaitForTarget():
            # Target the forge
            API.Target(forge)

            API.Pause(0.5)

            # Check if smelting failed due to insufficient metal
            if API.InJournal('There is not enough metal'):
                # Move the small ore pile away (offset by 1, 1)
                API.MoveItemOffset(found_ore, 0, 1, 1, 0)
                API.ClearJournal()
                API.Pause(0.5)
        else:
            # Timeout waiting for target
            break

    API.SysMsg('Smelting complete!')
