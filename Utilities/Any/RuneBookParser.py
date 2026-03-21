# Target, open, parse, and display a runebook recall/gate UI.
# Simple press play, target your runebook!

WIN_W = 310
ROW_H = 30
HEADER_H = 42
COL_HDR_H = 20
MAX_VISIBLE_ROWS = 6


def _use_runebook_and_wait(book_serial):
    API.UseObject(book_serial)
    API.Pause(0.15)
    while not API.HasGump():
        API.Pause(0.1)


def RecallToRune(rune_num, book_serial):
    _use_runebook_and_wait(book_serial)
    API.ReplyGump(5 + rune_num * 6)


def GateToRune(rune_num, book_serial):
    _use_runebook_and_wait(book_serial)
    API.ReplyGump(6 + rune_num * 6)


def parse_rune_names(raw_text):
    """
    PacketGumpText lines:
      [0]  metadata
      [1]  metadata
      [2..17] rune slot names (slots 0-15)
    Returns list of (slot_index, name) for non-empty slots.
    """
    lines = [l.strip() for l in raw_text.split("\n")]
    runes = []
    for i in range(16):
        idx = 2 + i
        if idx < len(lines):
            name = lines[idx]
            if name and name.lower() != "empty":
                runes.append((i, name))
    return runes


def build_ui(runes, book_serial):
    visible_rows = min(len(runes), MAX_VISIBLE_ROWS)
    scroll_h = visible_rows * ROW_H
    win_h = HEADER_H + COL_HDR_H + scroll_h + 8

    gump = API.Gumps.CreateGump(keepOpen=True)
    gump.SetWidth(WIN_W)
    gump.SetHeight(win_h)
    gump.CenterXInViewPort()
    gump.CenterYInViewPort()

    # Background
    bg = API.Gumps.CreateGumpColorBox(0.88, "#111827")
    bg.SetWidth(WIN_W)
    bg.SetHeight(win_h)
    gump.Add(bg)

    # Header bar
    header_bg = API.Gumps.CreateGumpColorBox(0.95, "#1E3A5F")
    header_bg.SetRect(0, 0, WIN_W, HEADER_H)
    gump.Add(header_bg)

    title_lbl = API.Gumps.CreateGumpTTFLabel("Runebook", 16, "#A8D8FF")
    title_lbl.SetPos(10, 12)
    gump.Add(title_lbl)

    count_lbl = API.Gumps.CreateGumpTTFLabel(f"{len(runes)} rune(s)", 12, "#7AAAC8")
    count_lbl.SetPos(WIN_W - 80, 15)
    gump.Add(count_lbl)

    # Column headers
    col_header_bg = API.Gumps.CreateGumpColorBox(0.7, "#0D2137")
    col_header_bg.SetRect(0, HEADER_H, WIN_W, COL_HDR_H)
    gump.Add(col_header_bg)

    name_hdr = API.Gumps.CreateGumpTTFLabel("Rune", 11, "#88AACC")
    name_hdr.SetPos(10, HEADER_H + 3)
    gump.Add(name_hdr)

    recall_hdr = API.Gumps.CreateGumpTTFLabel("Recall", 11, "#88AACC")
    recall_hdr.SetPos(174, HEADER_H + 3)
    gump.Add(recall_hdr)

    gate_hdr = API.Gumps.CreateGumpTTFLabel("Gate", 11, "#88AACC")
    gate_hdr.SetPos(240, HEADER_H + 3)
    gump.Add(gate_hdr)

    # Scroll area — fixed height, scrolls when runes exceed MAX_VISIBLE_ROWS
    scroll = API.Gumps.CreateGumpScrollArea(0, HEADER_H + COL_HDR_H, WIN_W, scroll_h)
    gump.Add(scroll)

    for i, (slot, name) in enumerate(runes):
        y = i * ROW_H

        # Alternating row background
        row_color = "#162032" if i % 2 == 0 else "#0F1922"
        row_bg = API.Gumps.CreateGumpColorBox(0.65, row_color)
        row_bg.SetRect(0, y, WIN_W - 16, ROW_H - 1)
        scroll.Add(row_bg)

        # Rune name
        lbl = API.Gumps.CreateGumpTTFLabel(name, 13, "#E0E8FF")
        lbl.SetPos(10, y + 7)
        scroll.Add(lbl)

        # Recall button
        rb = API.Gumps.CreateSimpleButton("Recall", 62, 22)
        rb.SetPos(165, y + 4)
        scroll.Add(rb)
        API.Gumps.AddControlOnClick(rb, lambda s=slot: RecallToRune(s, book_serial))

        # Gate button
        gb = API.Gumps.CreateSimpleButton("Gate", 55, 22)
        gb.SetPos(233, y + 4)
        scroll.Add(gb)
        API.Gumps.AddControlOnClick(gb, lambda s=slot: GateToRune(s, book_serial))

    API.Gumps.AddGump(gump)
    return gump


# ── Main ────────────────────────────────────────────────────────────────────

API.HeadMsg("Target a runebook", API.Player)
book_serial = API.RequestTarget(30)

if not book_serial:
    API.SysMsg("No target selected.")
else:
    # Open the runebook and wait for its gump
    API.UseObject(book_serial)
    API.Pause(0.2)
    if not API.WaitForGump():
        API.SysMsg("Gump did not open. Is that a runebook?")
    else:
        gump_data = API.GetGump()
        raw_text = gump_data.PacketGumpText

        runes = parse_rune_names(raw_text)

        # Close the runebook gump
        API.CloseGump()
        API.Pause(0.15)

        if not runes:
            API.SysMsg("No named runes found in this runebook.")
        else:
            ui = build_ui(runes, book_serial)

            while not API.StopRequested and not ui.IsDisposed:
                API.ProcessCallbacks()
                API.Pause(0.25)
