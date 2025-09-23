import API

##Prompt user to select lockpick
API.SysMsg("Target the lockpick")
lockpick = API.RequestTarget()
API.Pause(0.25)

##Prompt user to select keychain
API.SysMsg("Target the keychain")
keychain = API.RequestTarget()
API.Pause(0.25)

##Prompt user to select up to 10 lockboxes
boxes = []
num_boxes = 0
API.SysMsg("Target lockboxes one by one, cancel target (e.g., press ESC or target nothing) when done (up to 10)")
for i in range(10):
    serial = API.RequestTarget()
    if serial == 0:
        break
    boxes.append(serial)
    num_boxes += 1
    API.SysMsg(f"Selected {num_boxes} boxes to process.")
    API.Pause(0.25)

API.SysMsg(f"Starting process with {num_boxes} boxes.")

##Main Loop
while True:
    # Unlock all boxes
    for box in boxes:
        API.ClearJournal()  
        # Clear journal before attempting this box
        while True:
            API.UseObject(lockpick)
            if API.WaitForTarget():
                API.Target(box)
            API.Pause(1.00)
            if API.InJournal("The lock quickly yields to your skill."):
                break
            elif API.InJournal("This does not appear to be locked."):
                break  
            # Already unlocked, proceed to next box
    # Relock all boxes
    API.SysMsg("All boxes processed. Now relocking...")
    API.ClearJournal()  
    # Clear before relock
    for box in boxes:
        API.UseObject(keychain)
        if API.WaitForTarget():
            API.Target(box)
        API.Pause(1.00)
        if API.InJournal("Unlocked : wooden box"):
            API.SysMsg("Accidentally unlocked, relocking immediately...")
            API.UseObject(keychain)
            if API.WaitForTarget():
                API.Target(box)
            API.Pause(1.00)
    API.Pause(0.1)
