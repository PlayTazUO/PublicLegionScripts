import re
import API
import time
import csv
import os

# Debug toggle
DEBUG = False

##################################################
######              Introduction            ######
# Script created by: Daennabis
#
# Hello! This script will scan all Runic Atlas in
# range 1 and output to a CSV file in your client
# directory. You can move around and it will keep
# auto-scanning. A few things to be aware of:
#
# 1. There is no duplicate Runic Atlas check
#
# 2. Runic Atlas will reload and be rescannable
#    if you walk out of range(50?).
#
# 3. This was created to scan a Rune Library to
#    help make a navigation system.
#
# 4. The error check only checks to make sure all
#    48 Runes have been scanned, then exports csv.
#
# 5. Feel free to reuse any part of this code, no
#    credit required.


def pause(id):
    if DEBUG: 
        n = 0
        API.SysMsg("Has Gump: " + str(bool(API.HasGump(id))))
    while API.HasGump(id) == False:
        API.Pause(.025)
        if DEBUG: API.SysMsg("Opening Pause: " + str(n) + "  Has Gump: " + str(bool(API.HasGump(id))))
        if DEBUG: n+=1
    while API.GetGump(id) == None:
        API.Pause(.025)

def pauseclose(id):
    if DEBUG: 
        n = 0
        API.SysMsg("Has Gump: " + str(bool(API.HasGump(id))))
    while API.HasGump(id) == True:
        API.Pause(.025)
        if DEBUG: API.SysMsg("Closing Pause: " + str(n) + "  Has Gump: " + str(bool(API.HasGump(id))))
        if DEBUG: n+=1

def nextpage(page,id):
    if page > 0:
        for i in range(1,1+page):
            API.ReplyGump(1150,id)
            pause(id)

def findBook(range1):
    bookList = API.FindTypeAll(0X9C16,range = range1) + (API.FindTypeAll(0X9C17,range = range1))
    bookList = [book for book in bookList if book.Hue != 0x1000]
    return bookList

if DEBUG:
    API.SysMsg("Start of Debug.")
gumpid = 498 #atlas gump id 498

# API.HeadMsg("Select an Atlas to Decode",API.Player)
# atlas = API.RequestTarget()
last_msg_time = 0 #timer so we dont spam between books.
while True:

    current_time = time.time()
    if current_time - last_msg_time > 5:  # 5 seconds between messages
        count = len(findBook(50))
        API.SysMsg("There are " + str(count) + " Runic Atlases left to scan in range 50.")
        last_msg_time = current_time
    
    for atlas in findBook(1):
        API.SysMsg("There are " + str(len(findBook(1))) + " Runic Atlases left to scan in range 1.")
        atlasname = API.ItemNameAndProps(atlas).splitlines()
        atlasname = atlasname[len(atlasname)-1]
        API.SysMsg("Scanning Runic Atlas: " + str(atlasname))

        match1 = []
        match2 = []
        match3 = []

        for page in range(0,3):
            API.UseObject(atlas)
            pause(gumpid)
            nextpage(page,gumpid) #Next page if applicable
            API.ReplyGump(100+page*16,gumpid) # Rune 1
            pause(gumpid)
            gump = API.GetGump(gumpid)
            API.CloseGump(gumpid) #We do this because we want a CLEAR BASE PacketGumpText Dump with rune 1 selected.
            #pauseclose(gumpid)
            pauseclose(gumpid)

            API.UseObject(atlas) # Open book
            pause(gumpid)
            nextpage(page,gumpid) #Next page if applicable
            gump = API.GetGump(gumpid) #must update gump to get updated dump
            dump = gump.PacketGumpText.splitlines()

            API.SysMsg("Rune: " + str(page*16+1) + "/48")
            for i in range(len(dump)):
                if page == 0: 
                    if i in range(1, 17):
                        match1.append(dump[i])
                if page == 1:
                    if i in range(20, 36):
                        match1.append(dump[i])
                if page == 2:
                    if i in range(39, 55):
                        match1.append(dump[i])
                if "croppedtext" in dump[i]:
                    parts = dump[i].split()
                    if len(parts) >= 2:
                        match2.append(parts[-2]) 
            if "Nowhere" in dump[17]:
                match3.append(dump[17].replace("<center>", "").replace("</center>", ""))
            else:
                match3.append(
                re.sub(r"(\d+)([NSWE])", r"\1 \2",  # insert space between numbers and compass letters
                    dump[17]
                    .replace("<center>", "")
                    .replace("</center>", "")
                    .replace("o", "")  # split 44o55S → 44 55S
                    .replace(",", "")
                    .replace("'", "")
                    )
                    )

                
            # At this point we have a name list, filled color list. The first entry on color list is wrong,
            # because with the Rune selected, the color code changed to 331.
            # We can now loop through the rest of the entries for the sextant coords.
            for i in range(0,15):
                API.SysMsg("Rune: "+ str(i+2+page*16) + "/48")
                API.ReplyGump(101+i+page*16,gumpid)
                pause(gumpid)
                API.CloseGump(gumpid)
                pauseclose(gumpid)
                API.UseObject(atlas) # Open book
                pause(gumpid)
                nextpage(page,gumpid) #Next page if applicable
                gump = API.GetGump(gumpid) #must update gump to get updated dump
                dump = gump.PacketGumpText.splitlines()
                if "Nowhere" in dump[17]:
                    match3.append(dump[17].replace("<center>", "").replace("</center>", ""))
                else:
                    match3.append(
                    re.sub(r"(\d+)([NSWE])", r"\1 \2",  # insert space between numbers and compass letters
                    dump[17]
                    .replace("<center>", "")
                    .replace("</center>", "")
                    .replace("o", "")  # split 44o55S → 44 55S
                    .replace(",", "")
                    .replace("'", "")
                    )
                    )
            

            #This next part will fetch the correct color entry for Rune 1
            #Do this while Last Rune is selected so we get the correct color.
            for i in range(len(dump)):
                if "croppedtext" in dump[i]: #Retrieve list again to swap entry 1
                    parts = dump[i].split()
                    if len(parts) >= 2:
                        match2[0+page*16] = parts[-2]
                    break # Exit loop after finding the first match
            API.CloseGump(gumpid) #closing gump since the next loop will try to open the runic atlas
            pauseclose(gumpid)



        if DEBUG:
            for i in range(len(dump)):        
                API.SysMsg( str(i) + ": " + str(dump[i]))


        #Error Check
        if len(match1) != 48:
            API.SysMsg("Error, length != 48.")
            break
        elif len(match2) != 48:
            API.SysMsg("Error, length != 48.")
            break
        elif len(match3) != 48:
            API.SysMsg("Error, length != 48.")
            break
        else:
            API.SysMsg("Error check passed.")

        #Formatting

        #match1 is names we don't have to do anything to format it

        #match 2 is color we need to evaluate the values and convert them to map/fracet codes
        for i in range(len(match2)):
            if match2[i] == '81': #felucca/green
                match2[i] = "fel"
            elif match2[i] == '0': #ilshenar/black
                match2[i] = "ils"
            elif match2[i] == '1102': #malas/grey
                match2[i] = "mal"
            elif match2[i] == '10': #trammel/purple
                match2[i] = "tra"
            elif match2[i] == '1154': #tokuno/darkgreen
                match2[i] = "tok"
            elif match2[i] == '1645': #termur/lightred
                match2[i] = "ter"

        #match3 is the sextant coords, we need to convert them and split them into X and Y
        Xcoords = []
        Ycoords = []
        for i in range(len(match3)):
            if "Nowhere" in match3[i]:
                Xcoords.append(None)
                Ycoords.append(None)
                continue
            coords = match3[i].split(' ')
            
            normalized = [int(coords[0]) + int(coords[1])/60,
                            coords[2],
                            int(coords[3]) + int(coords[4])/60,
                            coords[5]]
            if normalized[1] == "N": #THIS IS Y
                normalized[0] = normalized[0]*-1
            if normalized[3] == "W": #THIS IS X
                normalized[2] = normalized[2]*-1
            converted0 = round(normalized[2]*5120/360 +1323)
            converted1 = round(normalized[0]*4096/360 +1624)
            if converted0 < 0:
                converted0 = converted0 + 5120
            if converted1 < 0:
                converted1 = converted1 + 4096
            Xcoords.append(converted0)
            Ycoords.append(converted1)

        #Finally, we make a rune count so that we can reference which page/location the rune is
        count = []
        for i in range(1,49):
            count.append(i)



        if DEBUG:
            API.SysMsg(str(atlasname))
            API.SysMsg(str(match1))
            API.SysMsg(str(match2))
            API.SysMsg(str(Xcoords))
            API.SysMsg(str(Ycoords))
            API.SysMsg(str(count))

        #Run names are from line 1 to 16
        #17 is the sextant coords
        #then page must be turned
        #all runic atlas' have 3 pages

        #my format ["runebookname", x, y, facet, "coordsname", rune#]

        ##################################################
        ######         Exporting Dictionary         ######

        # Choose a file path (adjust for your system)
        filepath = "atlas_export.csv"


        # Open and write the CSV
        write_header = not os.path.exists(filepath)
        with open(filepath, mode="a", newline="") as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(["BOOK", "X", "Y", "FACET", "TEXT", "RUNE"]) # header row

            for book, x, y, facet, text, rune in zip([atlasname] * len(count), Xcoords, Ycoords, match2, match1, count):
                writer.writerow([book, x, y, facet, text, rune])

        API.SysMsg(f"Exported CSV to: {filepath}")

        ##################################################
        atlas.Graphic = 0x1000
