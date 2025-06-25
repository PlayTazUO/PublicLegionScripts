import API
import time

def waitForGump():
    timeout = time.time() + 3
    while not API.HasGump():
        API.Pause(0.3)
        if time.time() > timeout:
            break

while True:
    API.UseSkill("Tracking")
    waitForGump()
    API.ReplyGump(3)
    waitForGump()
    API.ReplyGump(0)
    API.Pause(11)
