import API

# Keep Primary Ability Active
# Keeps your primary weapon ability active if you have at least 50 mana

while not API.StopRequested:
    player = API.Player

    # Check if primary ability is not active and we have enough mana
    if not API.PrimaryAbilityActive() and player.Mana >= 50:
        API.ToggleAbility("primary")

    # Wait 1 second before checking again (original used 1000ms pause + replay)
    API.Pause(1)
