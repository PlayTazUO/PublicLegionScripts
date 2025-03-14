import API
import time

player = API.Player
delay = 8
diffhits = 10

while True:
    if player.HitsMax - player.Hits > diffhits or player.IsPoisoned:
        if API.BandageSelf():
            API.CreateCooldownBar(delay, "Bandaging...", 21)
            time.sleep(delay)
        else:
            API.SysMsg("WARNING: No bandages!", 32)
            break
    time.sleep(0.5)
