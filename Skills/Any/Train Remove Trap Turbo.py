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
## (https://github.com/caporalesimone)

# Script by ThomasThorun(https://github.com/ThomasThorun). The Turbo Solver was SimonSoft (https://github.com/caporalesimone/) idea.

# Translated to TazUO Iron Python/GUI by Daennabis. Most of the code remains the same with minor changes for python.

import API
import re
#import os #This is leftover from the unknown solution importer
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

        bg = API.CreateGumpColorBox(0, "#575757FF")  
        bg.SetWidth(w)  
        bg.SetHeight(h)  
        self.gump1.SetX(gump.GetX())
        self.gump1.SetY(gump.GetY())
        self.gump1.Add(bg)  

        #    0,  1,   2,  3,  4
        #    5,  6,   7,  8,  9
        #    10, 11, 12, 13, 14
        #    15, 16, 17, 18, 19
        #    20, 21, 22, 23, 24
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
                text = API.CreateGumpTTFLabel("?", 24, "#FFFFFF", "alagard")
                text.SetX(119 + x*40)
                text.SetY(138 + y*40)
                self.textlist.append(text)
                self.gump1.Add(self.textlist[x+y*5])

        # info box
        infobox = API.CreateGumpColorBox(1, "#000000")
        infobox.SetWidth(250)
        infobox.SetHeight(325)
        infobox.SetX(350)
        infobox.SetY(50)
        self.gump1.Add(infobox)
        
        titlebox = API.CreateGumpColorBox(1, "#292929") 
        titlebox.SetWidth(250)
        titlebox.SetHeight(50)
        titlebox.SetX(350)
        titlebox.SetY(20)
        self.gump1.Add(titlebox)

        title1 = API.CreateGumpTTFLabel("Remove Trap", 24, "#FFFFFF", "alagard")
        title1.SetX(355)
        title1.SetY(25)
        self.gump1.Add(title1)

        title2 = API.CreateGumpTTFLabel("Turbo Trainer", 18, "#FFFFFF", "avadonian")
        title2.SetX(420)
        title2.SetY(50)
        self.gump1.Add(title2)

        self.l_size = API.CreateGumpTTFLabel("", 18, "#FFFFFF", "alagard")
        self.l_size.SetX(365)
        self.l_size.SetY(75)
        self.gump1.Add(self.l_size)

        self.l_attempt = API.CreateGumpTTFLabel("Attempt #", 18, "#FFFFFF", "alagard")
        self.l_attempt.SetX(365)
        self.l_attempt.SetY(100)
        self.gump1.Add(self.l_attempt)

        self.l_path = API.CreateGumpTTFLabel("Path:", 18, "#FFFFFF", "alagard")
        self.l_path.SetX(365)
        self.l_path.SetY(125)
        self.gump1.Add(self.l_path)

        self.l_move = API.CreateGumpTTFLabel("Moving:", 18, "#FFFFFF", "alagard")
        self.l_move.SetX(365)
        self.l_move.SetY(150)
        self.gump1.Add(self.l_move)

        self.l_skill = API.CreateGumpTTFLabel("", 18, "#FFFFFF", "alagard") #Skill time remaining
        self.l_skill.SetX(365)
        self.l_skill.SetY(200)
        self.gump1.Add(self.l_skill)

        self.skillbar = API.CreateGumpSimpleProgressBar(200, 5, "#666666", "#0059FF", int(API.GetSkill("Remove Trap").Value), int(API.GetSkill("Remove Trap").Cap))
        self.skillbar.SetX(365)
        self.skillbar.SetY(220)
        self.gump1.Add(self.skillbar)

        self.l_skillfraction = API.CreateGumpTTFLabel(f"{float(API.GetSkill('Remove Trap').Value):.1f}" + "/" + str(API.GetSkill("Remove Trap").Cap), 18, "#FFFFFF", "alagard") 
        self.l_skillfraction.SetX(425)
        self.l_skillfraction.SetY(240)
        self.gump1.Add(self.l_skillfraction)

        self.l_ttime = API.CreateGumpTTFLabel("Time Elapsed:", 18, "#FFFFFF", "alagard")
        self.l_ttime.SetX(365)
        self.l_ttime.SetY(300)
        self.gump1.Add(self.l_ttime)

        self.l_tdisarm = API.CreateGumpTTFLabel("Disarmed Trap #0 in 0s", 18, "#FFFFFF", "alagard")
        self.l_tdisarm.SetX(365)
        self.l_tdisarm.SetY(325)
        self.gump1.Add(self.l_tdisarm)

        self.l_mean = API.CreateGumpTTFLabel("Avg disarm time:", 18, "#FFFFFF", "alagard")
        self.l_mean.SetX(365)
        self.l_mean.SetY(350)
        self.gump1.Add(self.l_mean)

        self.gump1.LayerOrder = self.gump1.LayerOrder.__class__.Over
        API.AddGump(self.gump1)

    def updateBox(self, index, BHue=None, text=None, THue=None, BAlpha=None):
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
        if BAlpha is not None:
            self.boxlist[index].Alpha = BAlpha

    def updateText(self, size=None, attempt=None, path=None, move=None, skilltime=None, 
                   timeelapsed=None, disarm_count=None, disarm_time=None, mean=None):
        """
        Updates Box and Text
        
        Args:
            size (int): Size of the table - 3x3...
            attempt (int): Attempt #
            path (int): Set of validated moves.
            move (int): Next Move
            skill (int): Not sure yet
            timeelapsed (int): Total time elapsed.
            disarm_count (int): Number of last trap that was disarmed.
            disarm_time (int): Time it took to disarm last trap.
            mean (int): Avg time taken to disarm all traps.
        """
        if size is not None:
            self.l_size.SetText(str(size) + "x" + str(size))
        if attempt is not None:
            self.l_attempt.SetText("Attempt #" + str(attempt))
        if path is not None:
            self.l_path.SetText("Path: " + str(path))
        if move is not None:
            self.l_move.SetText("Moving: " + str(move))
        if skilltime is not None:
            h = round(float(skilltime) // 3600)
            m = round((float(skilltime) % 3600) // 60)
            s = round(float(skilltime) % 60)
            self.l_skill.SetText("Time to Max: " + str(h) + "h " + str(m) + "m " + str(s) + "s")
        if timeelapsed is not None:
            h = timeelapsed // 3600
            m = (timeelapsed % 3600) // 60
            s = timeelapsed % 60
            self.l_ttime.SetText("Time Elapsed: " + str(h) + "h " + str(m) + "m " + str(s) + "s")
        if (disarm_count and disarm_time) is not None:
            self.l_tdisarm.SetText("Disarmed Trap #" + str(disarm_count) +" in " + str(disarm_time) + "s")
        if mean is not None:
            self.l_mean.SetText(f"Avg disarm time: {mean:.2f}s")
        self.l_skillfraction.SetText(f"{float(API.GetSkill('Remove Trap').Value):.1f}" + "/" + str(API.GetSkill("Remove Trap").Cap))
        self.skillbar.SetProgress(API.GetSkill("Remove Trap").Value, API.GetSkill("Remove Trap").Cap)
        




    def reset(self, size):
        if size == 5:
            for i in range(25):
                self.updateBox(i, BHue=1, text="?", THue = 931)
        if size == 4:
            for i in range(25):
                self.updateBox(i, BHue=1, text="?", THue = 931)
            for i in range(0, 5):
                self.updateBox(20 + 1*i, None, "", BAlpha = 0)
                self.updateBox(4 + 5*i, None, "", BAlpha = 0)
        if size == 3:
            for i in range(25):
                self.updateBox(i, BHue=1, text="?", THue = 931)
            for i in range(0, 5):
                for i2 in range (0, 2):
                    self.updateBox(15 + 5*i2 + 1*i, None, "", BAlpha = 0)
                    self.updateBox(3 + 1*i2 + 5*i, None, "", BAlpha = 0)

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
        if API.GumpContains("Trap", gump_id): #verify this is trap gump
            if DEBUG: API.SysMsg("Gump found: " + str(gump_id))
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
    
    if size == 5:
        ui.updateBox(currentbox, 69, "S", 1)
        ui.updateBox(24, 69, "E", 1)
    if size == 4:
        for i in range(0, 5):
            ui.updateBox(20 + 1*i, None, "", BAlpha = 0)
            ui.updateBox(4 + 5*i, None, "", BAlpha = 0)
        ui.updateBox(currentbox, 69, "S", 1)
        ui.updateBox(18, 69, "E", 1)
    if size == 3:
        for i in range(0, 5):
            for i2 in range (0, 2):
                ui.updateBox(15 + 5*i2 + 1*i, None, "", BAlpha = 0)
                ui.updateBox(3 + 1*i2 + 5*i, None, "", BAlpha = 0)
        ui.updateBox(currentbox, 69, "S", 1)
        ui.updateBox(12, 69, "E", 1)
    attempt = MoveResult.ValidTry #First try is always valid/This shows the status of the current attempt
    TryDirection = Dir.Invalid
    for SafeCounter in range(0,50):
        ui.updateText(attempt = str(SafeCounter))
        solutionFitness, foundSolution = calculate_path_fitness(size, path)
        if DEBUG: API.SysMsg("Fitness: " + str(solutionFitness) + " Found Solution: " + str(foundSolution))
        if solutionFitness > 0:
            if DEBUG: API.SysMsg("Found a match in solution database with "+ str(solutionFitness) + "% match", 33);
            #Continue with the missing steps of the solution
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
        ui.updateText(path = pathString)
        if DEBUG: API.SysMsg("Path: " + pathString + " | Next: " + dir_to_str(TryDirection), 149)

        if attempt == MoveResult.Disarmed:
            path.append(TryDirection)
            #if STORE_UNKNOWN_SOLUTIONS_ON_FILE == True: store_solution(size, path)
            currentbox = 0
            ui.reset(size)
            return True
        if attempt == MoveResult.WrongTry:
            if DEBUG: API.SysMsg("Wrong: " + dir_to_str(TryDirection), 149)
            failedDirections.append(TryDirection)
            ui.updateBox(currentbox, 33, "X", 1)
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
    ui.updateText(move = dir_to_str(direction))
    #API.SysMsg("Moving: " + dir_to_str(direction), 149)
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

# # LOGGING UNKNOWN SOLUTIONS
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

#MAIN LOOP
def run():
    debug_here("",307)
    trap_serial = API.RequestTarget(10)
    API.SysMsg("Select the trap to disarm.")

    ui = None
    counter = 0
    start_time = time.time()
    starting_skill = API.GetSkill("Remove Trap").Value
    skill_time_remaining = None
    while True:
        debug_here("",315)
        trap_time = time.time()
        
        gump_id = open_trap(trap_serial)
        if not gump_id:
            continue

        size = calculate_trap_size(gump_id)
        if ui is None:
            ui = CircuitUI(gump_id)
        ui.updateText(size = calculate_trap_size(gump_id)) # Clear unused squares
        play_game(gump_id, size, trap_serial, ui)
        
        elapsed = (time.time() - trap_time)
        total_time = (time.time() - start_time)
        
        counter += 1    #Trap counter
        avg = round(total_time / counter, 2)

        #Skill and skill rate calculations
        current_skill = API.GetSkill("Remove Trap").Value
        gain_rate = (current_skill - starting_skill) / int(total_time)
        if gain_rate != 0:
            skill_time_remaining = (API.GetSkill("Remove Trap").Cap - current_skill) / gain_rate


        ui.updateText(None, None, None, None, skill_time_remaining, int(total_time), counter, int(elapsed), avg)

run()
