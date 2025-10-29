# Just hit play! Or create a macro and click the button. Will use shovels or pickaxes to mine at your feet.

import API

tools = [0x0F39, 0x0E86, 0x66F7, 0x6485]

def get_chunk_bounds(chunk_x, chunk_y, grid_size=8):
    """
    Return the starting and ending (x, y) tile coordinates for a chunk.
    Returns (start_x, start_y, end_x, end_y)
    """
    start_x = chunk_x * grid_size
    start_y = chunk_y * grid_size
    end_x = start_x + grid_size - 1
    end_y = start_y + grid_size - 1
    return start_x, start_y, end_x, end_y

def get_chunk_outline_tiles(chunk_x, chunk_y, grid_size=8):
    """
    Given a chunk coordinate, return all (x, y) tile positions that form the outline (perimeter) of the chunk.
    """
    tiles = []
    start_x = chunk_x * grid_size
    start_y = chunk_y * grid_size
    end_x = start_x + grid_size - 1
    end_y = start_y + grid_size - 1
    # Top and bottom edges
    for x in range(start_x, end_x + 1):
        tiles.append((x, start_y))      # Top edge
        tiles.append((x, end_y))        # Bottom edge
    # Left and right edges (excluding corners, already added)
    for y in range(start_y + 1, end_y):
        tiles.append((start_x, y))      # Left edge
        tiles.append((end_x, y))        # Right edge
    return tiles

def get_nearby_chunks(x, y, radius, grid_size=8):
    """
    Given any x, y position (tile coordinates), return all chunk coordinates (chunk_x, chunk_y)
    within the given radius (in chunks) in all directions, based on 8x8 chunk grid.
    
    Args:
        x: X tile coordinate
        y: Y tile coordinate
        radius: How many chunks away to include (in chunk units)
        grid_size: Size of each chunk (default 8x8)
    Returns:
        List of (chunk_x, chunk_y) tuples representing nearby chunk coordinates
    """
    # Find the chunk coordinate for the given x, y
    center_chunk_x = x // grid_size
    center_chunk_y = y // grid_size
    chunks = set()
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            chunk_x = center_chunk_x + dx
            chunk_y = center_chunk_y + dy
            chunks.add((chunk_x, chunk_y))
    # Always ensure the center chunk is included
    chunks.add((center_chunk_x, center_chunk_y))
    result = sorted(list(chunks))
    return result

tool = None

tool = API.FindLayer("onehanded")
#API.SysMsg(f"Tool in onehanded: {tool}")
if tool and tool.Graphic not in tools:
    tool = None

tool = API.FindLayer("twohanded")
#API.SysMsg(f"Tool in twohanded: {tool}")
if tool and tool.Graphic not in tools:
    tool = None

if not tool:
    for t in tools:
        tool = API.FindType(t, API.Backpack)
        if tool:
            break

if not tool:
    API.Stop()
else:
    x = API.Player.X
    y = API.Player.Y
    nearby_chunks = []
    nearby_chunks.extend(get_nearby_chunks(x, y, 1))
    #API.SysMsg(f"Nearby chunks: {nearby_chunks}, {len(nearby_chunks)} total")
    outline_tiles = []
    c = 1
    for chunk_x, chunk_y in nearby_chunks:
        color = 34 * c
        c+=1
        outline_tiles.extend(get_chunk_outline_tiles(chunk_x, chunk_y))
        # Get correct bounds for this chunk
        startx, starty, endx, endy = get_chunk_bounds(chunk_x, chunk_y)
        allStats = API.GetStaticsInArea(startx, starty, endx, endy)
        for static in allStats:
            if (static.X, static.Y) in get_chunk_outline_tiles(chunk_x, chunk_y):
                static.Hue = color

    API.UseObject(tool)
    API.WaitForTarget()
    API.TargetLandRel(0, 0)