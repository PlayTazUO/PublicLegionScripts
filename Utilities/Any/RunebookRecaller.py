import API


# You can copy this function into your own script file
def RecallRunebook(runeNum, runeBook):
    """
    Recall to a specific rune in a runebook.
    The first rune is 0, second is 1, and so on.
    :param runeNum: The index of the rune to recall to (0-based).
    :param runeBook: The runebook object to use for recalling.
    """
    if not runeBook:
        API.HeadMsg("No rune book specified.", API.Player, 32)
        return
    
    if not runeNum or runeNum < 0:
        API.HeadMsg("Invalid rune number.", API.Player, 32)
        return
    
    API.UseObject(runeBook)
    API.Pause(0.1)
    while not API.HasGump():
        API.Pause(0.1)
    
    API.ReplyGump(5 + runeNum * 6)

# Example:
RecallRunebook(1, 0x4000168C) # Recall to the second rune in your runebook
