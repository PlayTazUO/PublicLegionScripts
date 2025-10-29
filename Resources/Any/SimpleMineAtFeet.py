import API

# Mining tools - Edit your tools here
tools = [
    0x0E86,  # Pickaxe
    0x0F39   # Shovel
]

for tool in tools:
    while not API.StopRequested:
        # Find tool in backpack
        found_tool = API.FindType(tool, API.Backpack)

        if not found_tool:
            break

        # Use the tool
        API.UseObject(found_tool)

        # Wait for targeting cursor
        if API.WaitForTarget(timeout=7):
            # Target tile at player's feet (relative position 0, 0)
            API.TargetTileRel(0, 0)
            # If targeting is not working use TargetLandRel instead, depends on the server

            # Delay after mining attempt
            API.Pause(1.5)  # Adjust delay here
        else:
            # Timeout waiting for target
            break
