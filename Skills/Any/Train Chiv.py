import API

# Configuration
USE_MEDITATION = False  # Set to False to disable auto-meditation

# Main training loop
while not API.StopRequested:
    # Get current Chivalry skill value
    skill = API.GetSkill('Chivalry').Value
    manaCost = 0

    # Cast appropriate chivalry spell based on skill level
    if skill < 40:
        API.CastSpell('Consecrate Weapon')
        manaCost = 10
        API.Pause(3)
    elif skill < 60.0:
        API.CastSpell('Divine Fury')
        manaCost = 15
        API.Pause(3)
    elif skill < 70.0:
        API.CastSpell('Enemy Of One')
        manaCost = 20
        API.Pause(3)
    elif skill < 90.0:
        API.CastSpell('Holy Light')
        manaCost = 10
        API.Pause(3)
    elif skill < 115.0:
        API.CastSpell('Noble Sacrifice')
        manaCost = 20
        API.Pause(3)

    # Check if player needs to meditate to restore mana
    if USE_MEDITATION and API.Player.Mana < manaCost:
        API.UseSkill('Meditation')
        API.Pause(10)

    # Small pause to prevent CPU overload
    API.Pause(0.1)
