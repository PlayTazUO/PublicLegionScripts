import API
import time

# Multi Pet Bandage Healer
# Automatically heals multiple pets with bandages

# Initialize pet list
my_pets = []

# Prompt user to select up to 5 pets
API.SysMsg("Please target up to 5 pets to heal...", 88)

for i in range(5):
    API.SysMsg(f"Target pet #{i + 1} (or wait to skip)...", 88)
    pet_serial = API.RequestTarget(timeout=5)

    if pet_serial and pet_serial > 0:
        pet = API.FindMobile(pet_serial)
        if pet:
            my_pets.append(pet_serial)
            API.HeadMsg("Oi! Keep me healed boss!", pet_serial, 88)
        else:
            API.SysMsg("Invalid target, skipping...", 32)
    else:
        API.SysMsg("No target selected, moving on...", 88)
        break

if len(my_pets) == 0:
    API.SysMsg("No pets selected! Script stopping.", 32)
    API.Stop()

API.SysMsg(f"Monitoring {len(my_pets)} pets for healing.", 88)

last_bandage_time = 0
BANDAGE_COOLDOWN = 4.0  # seconds

while not API.StopRequested:
    player = API.Player

    # Check if player is dead
    if player.IsDead:
        API.SysMsg("You are dead! Script stopping.", 32)
        break

    current_time = time.time()

    # Check each pet for healing needs
    for pet_serial in my_pets:
        pet = API.FindMobile(pet_serial)

        # Check if pet exists and needs healing
        if pet and not pet.IsDead:
            hits_missing = pet.HitsMax - pet.Hits

            # If pet needs healing and cooldown expired
            if hits_missing > 15 and (current_time - last_bandage_time >= BANDAGE_COOLDOWN):
                API.HeadMsg("Oi! Me hurt!!", pet_serial, 32)

                # Find bandages
                bandage = API.FindType(0x0E21, API.Backpack)

                if bandage:
                    API.UseObject(bandage.Serial, True)
                    # Wait up to 7 seconds for target cursor (original: waitfortarget '2' '7000')
                    if API.WaitForTarget(timeout=7):
                        API.Target(pet_serial)
                        last_bandage_time = current_time
                        API.CreateCooldownBar(BANDAGE_COOLDOWN, f"Healing {pet.Name}", 88)
                        break  # Only heal one pet per iteration
                else:
                    API.SysMsg("No bandages found!", 32)
                    break

    # Wait before next check (original: pause '2000')
    API.Pause(2)
