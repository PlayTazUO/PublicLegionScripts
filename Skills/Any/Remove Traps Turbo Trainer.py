## Remove Traps Turbo Trainer
## This scripts resolves the Remove Traps mini-game automatically.
## 
## Copyright Caporale Simone - 2024
##
## This version of the script is inspired from the UOAlive Discord Thread of Thomasthorun (Thanks).
## I copied some ideas like the clicloc search for the gump and the gump size calculation.
## I call it "Turbo Trainer" because it tries to match the actual path with known solutions to speed up the resolution.
##
## My benchmarks:
##  Trap 3x3:  average 27 seconds on 356 tries
##  Trap 4x4:  average 33 seconds om 100 tries
##  Trap 5x5:  average 35 seconds om 245 tries

# Script by ThomasThorun. The Turbo Solver was SimonSoft (https://github.com/caporalesimone/) idea.

# Translated to TazUO Iron Python/GUI by Daennabis.

import API
import re
#import os
import time
import sys #for debug

# SETUP AND KNOWN SOLUTIONS
DEBUG = False
STORE_UNKNOWN_SOLUTIONS_ON_FILE = False
        
class Dir:
    Invalid = 0
    Up = 1
    Right = 2
    Down = 3
    Left = 4

class MoveResult:
    Disarmed = 0
    WrongTry = 1
    ValidTry = 2
    SomethingWentWrong = 3
    
# CIRCUIT UI
class CircuitUI:
    def __init__(self, gump_id):
        gump = API.GetGump(gump_id)

        w = 629
        h = 415 

        self.gump1 = API.CreateGump(True, True)  
        self.gump1.SetWidth(w)  
        self.gump1.SetHeight(h)  

        bg = API.CreateGumpColorBox(.25, "#575757FF")  
        bg.SetWidth(w)  
        bg.SetHeight(h)  
        self.gump1.SetX(gump.GetX())
        self.gump1.SetY(gump.GetY())
        self.gump1.Add(bg)  

        self.textlist= []
        self.boxlist = []
        for y in range(0,5):
            for x in range(0,5):
                box = API.CreateGumpColorBox(1, "#FFFFFF")
                box.SetHeight(40)
                box.SetWidth(40)
                box.SetX(105 + x*40)
                box.SetY(130 + y*40)
                box.Hue = 1
                self.boxlist.append(box)
                self.gump1.Add(self.boxlist[x+y*5])
                text = API.CreateGumpTTFLabel("?", 24, "#FFFFFF", "alagard",)
                text.SetX(119 + x*40)
                text.SetY(138 + y*40)
                self.textlist.append(text)
                self.gump1.Add(self.textlist[x+y*5])

        #    0,  1,   2,  3,  4
        #    5,  6,   7,  8,  9
        #    10, 11, 12, 13, 14
        #    15, 16, 17, 18, 19
        #    20, 21, 22, 23, 24

        self.gump1.LayerOrder = self.gump1.LayerOrder.__class__.Over
        API.AddGump(self.gump1)

    def updateBox(self, index, BHue=None, text=None, THue=None):
        """
        Updates Box and Text
        
        Args:
            index (int): Box/Text index.
            BHue (int): Box hue from color picker.
            text (str): Desired Text
            THue (int): Text hue from color picker.
        """
        if BHue is not None:
            self.boxlist[index].Hue = BHue
        if text is not None:
            self.textlist[index].SetText(text)
        if THue is not None:
            self.textlist[index].Hue = THue

    def reset(self):
        for i in range(25):
            self.updateBox(i, BHue=1, text="?", THue = 931)


# Solutions
known_solutions_3x3 = [
    [Dir.Down, Dir.Right, Dir.Right, Dir.Down],
    [Dir.Down, Dir.Right, Dir.Down, Dir.Right],
    [Dir.Down, Dir.Down, Dir.Right, Dir.Right],
    [Dir.Down, Dir.Down, Dir.Right, Dir.Up, Dir.Up, Dir.Right, Dir.Down, Dir.Down],
    [Dir.Right, Dir.Right, Dir.Down, Dir.Down],
    [Dir.Right, Dir.Down, Dir.Left, Dir.Down, Dir.Right, Dir.Right],
    [Dir.Right, Dir.Down, Dir.Right, Dir.Down],
    [Dir.Right, Dir.Down, Dir.Down, Dir.Right],
]

known_solutions_4x4 = [
    [Dir.Down, Dir.Right, Dir.Down, Dir.Right, Dir.Right, Dir.Down],
    [Dir.Down, Dir.Right, Dir.Right, Dir.Up, Dir.Right, Dir.Down, Dir.Down, Dir.Down],
    [Dir.Down, Dir.Right, Dir.Right, Dir.Right, Dir.Down, Dir.Down],
    [Dir.Down, Dir.Down, Dir.Right, Dir.Right, Dir.Up, Dir.Up, Dir.Right, Dir.Down, Dir.Down, Dir.Down],
    [Dir.Down, Dir.Down, Dir.Right, Dir.Up, Dir.Right, Dir.Right, Dir.Down, Dir.Down],
    [Dir.Down, Dir.Down, Dir.Down, Dir.Right, Dir.Right, Dir.Right],
    [Dir.Right, Dir.Down, Dir.Right, Dir.Right, Dir.Down, Dir.Down],
    [Dir.Right, Dir.Down, Dir.Left, Dir.Down, Dir.Right, Dir.Right, Dir.Down, Dir.Right],
    [Dir.Right, Dir.Down, Dir.Left, Dir.Down, Dir.Down, Dir.Right, Dir.Right, Dir.Right],
    [Dir.Right, Dir.Right, Dir.Down, Dir.Right, Dir.Down, Dir.Down],
    [Dir.Right, Dir.Right, Dir.Right, Dir.Down, Dir.Down, Dir.Down],
    [Dir.Right, Dir.Right, Dir.Right, Dir.Down, Dir.Left, Dir.Left, Dir.Left, Dir.Down, Dir.Right, Dir.Right, Dir.Right, Dir.Down],
]

known_solutions_5x5 = [
    [Dir.Down, Dir.Down, Dir.Down, Dir.Down, Dir.Right, Dir.Right, Dir.Right, Dir.Right],
    [Dir.Down, Dir.Down, Dir.Right, Dir.Right, Dir.Right, Dir.Up, Dir.Left, Dir.Left, Dir.Up, Dir.Right, Dir.Right, Dir.Right, Dir.Down, Dir.Down, Dir.Down, Dir.Down],
    [Dir.Down, Dir.Down, Dir.Right, Dir.Down, Dir.Right, Dir.Right, Dir.Down, Dir.Right],
    [Dir.Down, Dir.Right, Dir.Down, Dir.Down, Dir.Down, Dir.Right, Dir.Up, Dir.Up, Dir.Up, Dir.Right, Dir.Right, Dir.Down, Dir.Down, Dir.Down],
    [Dir.Down, Dir.Right, Dir.Down, Dir.Right, Dir.Right, Dir.Down, Dir.Right, Dir.Down],
    [Dir.Down, Dir.Right, Dir.Right, Dir.Up, Dir.Right, Dir.Right, Dir.Down, Dir.Down, Dir.Down, Dir.Down],
    [Dir.Right, Dir.Down, Dir.Left, Dir.Down, Dir.Down, Dir.Right, Dir.Right, Dir.Up, Dir.Up, Dir.Right, Dir.Right, Dir.Down, Dir.Down, Dir.Down],
    [Dir.Right, Dir.Down, Dir.Left, Dir.Down, Dir.Right, Dir.Right, Dir.Down, Dir.Right, Dir.Right, Dir.Down],
    [Dir.Right, Dir.Down, Dir.Right, Dir.Right, Dir.Down, Dir.Left, Dir.Down, Dir.Right, Dir.Right, Dir.Down],
    [Dir.Right, Dir.Right, Dir.Right, Dir.Right, Dir.Down, Dir.Down, Dir.Down, Dir.Down],
    [Dir.Right, Dir.Right, Dir.Right, Dir.Right, Dir.Down, Dir.Down, Dir.Left, Dir.Left, Dir.Down, Dir.Down, Dir.Right, Dir.Right],
    [Dir.Right, Dir.Right, Dir.Down, Dir.Right, Dir.Right, Dir.Down, Dir.Left, Dir.Left, Dir.Left, Dir.Left, Dir.Down, Dir.Down, Dir.Right, Dir.Right, Dir.Right, Dir.Right],
]

def debug_here(msg="", line=None):
    if DEBUG:
        frame = sys._getframe(1)
        func = frame.f_code.co_name
        shown_line = line if line else "?"
        API.SysMsg(f"[DEBUG] {func}() @ Line {shown_line} — {msg}")

# OPENING THE TRAP GUMP AND GETTING GRID SIZE
def dir_to_str(direction):  #Unicode doesn't work for some reason
    debug_here("")
    if direction == Dir.Up:
        return "^"
    if direction == Dir.Right:
        return ">"
    if direction == Dir.Down:
        return "v"
    if direction == Dir.Left:
        return "<"
    else:
        return "Unknown"

def dir_list_to_str(directions):
    debug_here("")
    return ''.join([dir_to_str(d) for d in directions])

def dir_to_box(direction):
    if direction == Dir.Up:
        return (-5)
    if direction == Dir.Right:
        return (1)
    if direction == Dir.Down:
        return (5)
    if direction == Dir.Left:
        return (-1)
    else:
        return (0)

def open_trap(serial):
    debug_here("",100)
    while True:
        API.UseSkill("Remove Trap")
        if API.WaitForTarget("Neutral",1):
            break
        API.Pause(1)
    API.Target(serial)

    return wait_for_remove_trap_gump()

def wait_for_remove_trap_gump():
    debug_here("",112)
    trap_open_time = time.time()
    while True:
        current_time = time.time()
        gump_id = API.HasGump()  #Grab the first gump
        if API.GumpContains("Trap",gump_id): #verify this is trap gump
            API.SysMsg("Gump found: " + str(gump_id))
            return gump_id
        if current_time - trap_open_time > 5:   # Timer to break loop
            API.SysMsg("Gump not found.", 33)
            return 0
        API.Pause(.10)


def calculate_trap_size(gump_id):
    debug_here("",129)
    raw = API.GetGump(gump_id).PacketGumpText
    #if DEBUG: API.SysMsg(str(raw))
    diamond_count = len(re.findall(r"9720", raw))  # Gray Diamond ID

    if diamond_count <= 7:
        return 3
    elif diamond_count < 23:
        return 4
    else:
        return 5

# CORE GAME LOGIC + MOVE EXECUTION
def play_game(gump_id, size, trap_serial, ui):
    debug_here("",136)
    path = []
    failedDirections = []
    currentbox = 0
    ui.updateBox(currentbox, 69, "S", 1)
    ui.updateBox(24, 68, "E", 1)
    attempt = MoveResult.ValidTry #First try is always valid/This shows the status of the current attempt
    TryDirection = Dir.Invalid
    for SafeCounter in range(0,50):
        API.SysMsg("Attempt #" + str(SafeCounter), 149)
        solutionFitness, foundSolution = calculate_path_fitness(size,path)
        if DEBUG: API.SysMsg("Fitness: " + str(solutionFitness) + " Found Solution: " + str(foundSolution))
        if solutionFitness > 0:
            if DEBUG: API.SysMsg("Found a match in solution database with "+ str(solutionFitness) + "% match", 33);
            # I continue with the missing steps of the solution
            for i in range(len(path), len(foundSolution)):
                TryDirection = foundSolution[i]
                attempt = move_to(gump_id, TryDirection, ui)
                currentbox = currentbox + dir_to_box(TryDirection)
                ui.updateBox(currentbox, 68, "")

                #Check if the step is valid. Expected result should be always valid.
                if attempt == (MoveResult.WrongTry or MoveResult.SomethingWentWrong):
                    ui.updateBox(currentbox, 1000, "")
                    currentbox = currentbox - dir_to_box(TryDirection)
                    API.SysMsg("The found solution is not valid!!", 33)
                    break #The found solution isn't valid.
        
        else:
            if attempt == MoveResult.WrongTry:
                for step in path:
                    check = move_to(gump_id, step, ui)
                    if check == (MoveResult.WrongTry or MoveResult.SomethingWentWrong):
                        return False # Something went wrong
            TryDirection = next_direction(size, path, failedDirections)
            if DEBUG: API.SysMsg("Try: " + dir_to_str(TryDirection), 149)

            attempt = move_to(gump_id, TryDirection, ui)
            currentbox = currentbox + dir_to_box(TryDirection)
            

        pathString = dir_list_to_str(path)
        API.SysMsg("Path: " + pathString + " | Next: " + dir_to_str(TryDirection), 149)

        if attempt == MoveResult.Disarmed:
            path.append(TryDirection)
            #if STORE_UNKNOWN_SOLUTIONS_ON_FILE == True: store_solution(size, path)
            currentbox = 0
            ui.reset()
            return True
        if attempt == MoveResult.WrongTry:
            if DEBUG: API.SysMsg("Wrong: " + dir_to_str(TryDirection), 149)
            failedDirections.append(TryDirection)
            ui.updateBox(currentbox, 33, "X")
            currentbox = currentbox - dir_to_box(TryDirection)
            if open_trap(trap_serial) != gump_id: 
                return False
            continue
        if attempt == MoveResult.ValidTry:
            path.append(TryDirection)
            failedDirections.clear()
            ui.updateBox(currentbox, 68, "")
            continue
        if attempt == MoveResult.SomethingWentWrong:
            return False
    API.SysMsg("Failed: Too many tries.", 33)
    return True

def move_to(gump_id, direction, ui):
    debug_here("",193)
    API.ClearJournal()
    API.SysMsg("Moving: " + dir_to_str(direction), 149)
    API.ReplyGump(direction, gump_id)
    for i in range(50):
        if API.InJournal("successfully disarm"):
            if DEBUG: API.SysMsg("Returned 0: Succesfully Disarmed")
            return 0  # Disarmed
        if API.InJournal("fail to disarm the trap"):
            if DEBUG: API.SysMsg("Returned 1: Wrong Try")
            return 1  # Wrong Try
        if  bool(API.HasGump(gump_id)):
            if DEBUG: API.SysMsg("Returned 2: Valid Try")
            return 2  # Valid Try
        API.Pause(.25)
    wait_for_remove_trap_gump()

    API.CloseGump(gump_id)
    if DEBUG: API.SysMsg("Something went wrong. Line 229")
    return 3  # Something went wrong


def next_direction(size, prev, failed):
    debug_here("",203)
    row, col = 0, 0
    for step in prev:
        if step == Dir.Up: row -= 1
        elif step == Dir.Down: row += 1
        elif step == Dir.Left: col -= 1
        elif step == Dir.Right: col += 1

        if row < 0 or row >= size or col < 0 or col >= size:
            API.SysMsg("NextDirection failed: out of bounds", 33)
            return Dir.Invalid

    last = prev[-1] if prev else Dir.Invalid
    options = []
    if col < size - 1 and last != Dir.Left: options.append(Dir.Right)
    if row < size - 1 and last != Dir.Up: options.append(Dir.Down)
    if col > 0 and last != Dir.Right: options.append(Dir.Left)
    if row > 0 and last != Dir.Down: options.append(Dir.Up)

    options = [d for d in options if d not in failed]
    if not options:
        return Dir.Invalid
    if len(options) == 2:
        if Dir.Up in options and Dir.Down in options: return Dir.Down
        if Dir.Left in options and Dir.Right in options: return Dir.Right

    return calculate_best_next(size, prev, options)

# FITNESS MATCHING AND DIRECT SOLUTION
def calculate_path_fitness(size, path):
    debug_here("",254)
    pathSolution = []
    available_solutions = []
    if size == 3:
        available_solutions = known_solutions_3x3
    elif size == 4:
        available_solutions = known_solutions_4x4
    elif size == 5:
        available_solutions = known_solutions_5x5

    cntMatch = 0
    strPath = dir_list_to_str(path)

    for solution in available_solutions:
        strSolution = dir_list_to_str(solution)
        if strSolution.startswith(strPath):
            cntMatch += 1
            pathSolution = solution
    
    if cntMatch == 0 : return 0, []
    if cntMatch > 1: return 0, []

    fitness = len(path) / len(pathSolution) * 100
    if DEBUG: API.SysMsg(str(fitness) + "% match. Steps: " + dir_list_to_str(pathSolution), 91)
    return fitness, pathSolution

def calculate_best_next(size, current_path, options):
    debug_here("",258)
    if len(current_path) < 2:
        return options[0]

    if size == 3:
        known = known_solutions_3x3
    elif size == 4:
        known = known_solutions_4x4
    elif size == 5:
        known = known_solutions_5x5
    else:
        return Dir.Invalid

    path_str = dir_list_to_str(current_path)

    for solution in known:
        if dir_list_to_str(solution).startswith(path_str):
            if len(solution) > len(current_path):
                next_dir = solution[len(current_path)]
                if next_dir in options:
                    return next_dir
            break

    return options[0]

# # LOGGING UNKNOWN SOLUTIONS & MAIN LOOP
# def store_solution(size, path):
#     debug_here("",285)
#     path_str = f"{size}:{dir_list_to_str(path)}"
#     data_dir = os.path.join(API.RootPath(), "Data")
#     path_file = os.path.join(data_dir, "RemoveTraps.txt")

#     # Avoid duplicates
#     if os.path.exists(path_file):
#         with open(path_file, "r") as f:
#             if path_str in f.read():
#                 return

#     with open(path_file, "a") as f:
#         f.write(path_str + "\n")

def run():
    debug_here("",307)
    trap_serial = API.RequestTarget(10)
    API.SysMsg("Select the trap to disarm.")

    ui = None
    counter = 0
    start_time = time.time()

    while True:
        debug_here("",315)
        trap_time = time.time()
        
        gump_id = open_trap(trap_serial)
        if not gump_id:
            continue


        size = calculate_trap_size(gump_id)
        API.SysMsg(f"Trap size: {size}x{size}", 149)

        if ui is None:
            ui = CircuitUI(gump_id)
        play_game(gump_id, size, trap_serial, ui)
        
        elapsed = (time.time() - trap_time)
        total_time = (time.time() - start_time)

        counter += 1
        avg = total_time / counter

        API.SysMsg("======================================", 149)
        API.SysMsg(f"Disarmed Trap #{counter:03} in {int(elapsed)} seconds", 149)
        API.SysMsg(f"Total elapsed time: {int(total_time)} seconds", 149)
        API.SysMsg(f"Average disarm time: {avg:.1f} seconds", 149)
        API.SysMsg("======================================", 149)
run()