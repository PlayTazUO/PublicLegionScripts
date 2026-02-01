import API
import os
import json
import ast

"""
TileDataExporter
Version: 1.0
Last Updated: 2026-02-01

Features:
- Target a tile and display its attributes.
- Export tile data to a text file in TileDataExport.
- Results persist in the gump until you scan another tile.

How to use:
1) (Optional) Enter a folder path in "Save Path".
2) Click "Target Tile" and select a tile in-game.
3) Review the results in the scroll area.
4) Click "Export" to save the data to a file.
   - If Save Path is blank, the current working directory is used.
"""

# Gump layout.
GUMP_X = 300
GUMP_Y = 200
GUMP_WIDTH = 300
GUMP_HEIGHT = 440

# Runtime state.
CONTROL_GUMP = None
RESULT_LINES = ["No tile scanned yet."]
LAST_TARGET = None
EXPORT_BASE = None
PATH_TEXTBOX = None
DATA_KEY = "tile_data_exporter_config"


def _target_tile():
    # Request a tile target and update the results.
    global RESULT_LINES, LAST_TARGET
    API.SysMsg("Target a tile to scan.")
    API.RequestTarget()
    pos = API.LastTargetPos
    graphic = API.LastTargetGraphic
    if not pos:
        RESULT_LINES = ["No tile targeted."]
        LAST_TARGET = None
        _update_gump()
        return
    x = int(pos.X)
    y = int(pos.Y)
    z = int(pos.Z)
    LAST_TARGET = (x, y, z)
    tile = API.GetTile(x, y)
    statics = API.GetStaticsAt(x, y) or []

    lines = [
        f"X: {x}  Y: {y}  Z: {z}",
        f"TargetGraphic: 0x{int(graphic):04X}",
    ]
    if tile:
        lines.append(f"LandGraphic: 0x{int(tile.Graphic):04X}")
        try:
            lines.append(f"LandZ: {int(tile.Z)}")
        except Exception:
            pass
        # Dump land tile attributes.
        land_attrs = [a for a in dir(tile) if not a.startswith('_')]
        for name in land_attrs:
            if name in ("Graphic", "X", "Y", "Z"):
                continue
            try:
                value = getattr(tile, name)
            except Exception:
                continue
            if callable(value):
                continue
            text = str(value)
            if len(text) > 60:
                text = text[:57] + "..."
            lines.append(f"Land {name}: {text}")
    else:
        lines.append("LandGraphic: (none)")

    if statics:
        lines.append(f"Statics: {len(statics)}")
        # Show statics on the targeted tile with expanded attributes.
        for s in statics:
            try:
                lines.append(f"- 0x{int(s.Graphic):04X} z{int(s.Z)}")
            except Exception:
                lines.append("- (static)")
            # Dump a subset of attributes if present.
            attr_names = [a for a in dir(s) if not a.startswith('_')]
            for name in attr_names:
                if name in ("Graphic", "X", "Y", "Z"):
                    continue
                try:
                    value = getattr(s, name)
                except Exception:
                    continue
                # Skip callables and overly long values.
                if callable(value):
                    continue
                text = str(value)
                if len(text) > 60:
                    text = text[:57] + "..."
                lines.append(f"  {name}: {text}")
    else:
        lines.append("Statics: none")

    RESULT_LINES = lines
    _update_gump()


def _get_export_dir():
    global EXPORT_BASE
    if EXPORT_BASE:
        return EXPORT_BASE
    try:
        base = os.path.dirname(__file__)
    except Exception:
        base = os.getcwd()
    EXPORT_BASE = os.path.join(base, "TileDataExport")
    return EXPORT_BASE


def _load_config():
    global EXPORT_BASE
    raw = API.GetPersistentVar(DATA_KEY, "", API.PersistentVar.Char)
    if not raw:
        return
    try:
        try:
            data = json.loads(raw)
        except Exception:
            data = ast.literal_eval(raw)
        path = data.get("export_path", "")
        if path:
            EXPORT_BASE = path
    except Exception:
        pass


def _save_config():
    data = {"export_path": EXPORT_BASE or ""}
    API.SavePersistentVar(DATA_KEY, json.dumps(data), API.PersistentVar.Char)


def _export_to_file():
    # Export the current results to a text file.
    if not LAST_TARGET:
        API.SysMsg("No tile data to export.")
        return
    x, y, _ = LAST_TARGET
    export_dir = _get_export_dir()
    if PATH_TEXTBOX and PATH_TEXTBOX.Text.strip():
        export_dir = PATH_TEXTBOX.Text.strip()
        global EXPORT_BASE
        EXPORT_BASE = export_dir
        _save_config()
    try:
        os.makedirs(export_dir, exist_ok=True)
        filename = f"TileData_{x}_{y}.txt"
        path = os.path.join(export_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(RESULT_LINES))
        API.SysMsg(f"Saved: {filename}")
    except Exception:
        API.SysMsg("Failed to export tile data.")


def _update_gump():
    # Build/refresh the gump UI.
    global CONTROL_GUMP
    if CONTROL_GUMP:
        CONTROL_GUMP.Dispose()
        CONTROL_GUMP = None

    g = API.CreateGump(True, True, False)
    g.SetRect(GUMP_X, GUMP_Y, GUMP_WIDTH, GUMP_HEIGHT)
    bg = API.CreateGumpColorBox(0.7, "#1B1B1B")
    bg.SetRect(0, 0, GUMP_WIDTH, GUMP_HEIGHT)
    g.Add(bg)

    title = API.CreateGumpTTFLabel("TileDataExporter", 14, "#FFFFFF", "alagard", "center", GUMP_WIDTH)
    title.SetPos(0, 6)
    g.Add(title)

    btn = API.CreateSimpleButton("Target Tile", 90, 20)
    btn.SetPos(10, 34)
    g.Add(btn)
    API.AddControlOnClick(btn, _target_tile)

    path_label = API.CreateGumpTTFLabel("Save Path:", 12, "#FFFFFF", "alagard", "left", 120)
    path_label.SetPos(10, 34 + 22)
    g.Add(path_label)
    path_box = API.CreateGumpTextBox(EXPORT_BASE or "", GUMP_WIDTH - 110, 18, False)
    path_box.SetPos(90, 34 + 20)
    g.Add(path_box)
    global PATH_TEXTBOX
    PATH_TEXTBOX = path_box

    exp = API.CreateSimpleButton("Export", 70, 20)
    exp.SetPos(200, 34)
    g.Add(exp)
    API.AddControlOnClick(exp, _export_to_file)

    scroll = API.CreateGumpScrollArea(10, 62 + 22, GUMP_WIDTH - 20, GUMP_HEIGHT - 94)
    g.Add(scroll)
    y = 0
    for line in RESULT_LINES:
        label = API.CreateGumpTTFLabel(line, 12, "#FFFFFF", "alagard", "left", GUMP_WIDTH - 30)
        label.SetRect(0, y, GUMP_WIDTH - 30, 16)
        scroll.Add(label)
        y += 18

    API.AddGump(g)
    CONTROL_GUMP = g


def _main():
    _load_config()
    _update_gump()
    API.SysMsg("TileDataExporter loaded. Press 'Target Tile'.")
    while True:
        API.ProcessCallbacks()
        API.Pause(0.2)


_main()
