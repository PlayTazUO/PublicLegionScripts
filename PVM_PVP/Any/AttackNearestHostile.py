# Make sure to set Options->TazUO->Mobiles->Follow Distance to 1
# Did your radius indicator stay on? Just type `-radius` in game.
MAX_DISTANCE = 10
SHOW_RADIUS_INDICATOR = True

Player = API.Player
while True:
    if SHOW_RADIUS_INDICATOR:
        API.DisplayRange(10, 32)    
    enemy = API.NearestMobile([API.Notoriety.Gray, API.Notoriety.Criminal, API.Notoriety.Murderer], MAX_DISTANCE)
    if enemy:
        if SHOW_RADIUS_INDICATOR:
            API.DisplayRange(0)
        API.AutoFollow(enemy)
        API.Attack(enemy)
        while enemy and not enemy.IsDead and enemy.Distance < MAX_DISTANCE:
            enemy.Hue = 32
            API.HeadMsg("Current Target", enemy)
            API.Pause(0.3)
            enemy = API.FindMobile(enemy.Serial)
    else:
        API.HeadMsg("No enemies found", Player)
        
    API.Pause(0.5)
