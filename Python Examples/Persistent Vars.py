# Persistent Variables are variables that are saved in-between sessions. 
# You can store data and load it back after restarting or re-logging into the game.
# You can save them to only be acceissible by the account, character, server, or globally.
import API

# We add int() around this because all persistent variables are stored as strings, we want to convert it to a number(integer).
kills = int(API.GetPersistentVar("kills", "-1", API.PersistentVar.Account))  # Default value is -1 if "kills" does not exist
if kills == -1: # If kills is -1, it means it was not found
    kills = 1   # Initialize if it doesn't exist

# Here we are doubling the value of kills and saving it back.
# We must use str() to convert it back to a string for saving.
API.SavePersistentVar("kills", str(kills*2), API.PersistentVar.Account)

API.HeadMsg("You have " + str(kills*2) + " kills!", API.Player, 10)  # Display the updated kills count

if kills > 100:
    API.RemovePersistentVar("kills", API.PersistentVar.Account)  # Remove the variable if kills exceed 100
