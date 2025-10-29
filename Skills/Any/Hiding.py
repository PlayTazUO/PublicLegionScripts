import API

# Continuously use hiding skill every 11 seconds
while not API.StopRequested:
    API.UseSkill("Hiding")
    API.Pause(11)
