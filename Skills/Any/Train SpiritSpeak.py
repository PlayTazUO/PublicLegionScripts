# Extremely simple, use spirit speak if you have less than 30 missing mana.
import API

while True:
    if API.Player.ManaDiff < 30:
        API.UseSkill('Spirit Speak')
        API.Pause(6)
