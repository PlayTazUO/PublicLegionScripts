import API
import time
# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------
CONFIG = {
    # Offensive buffs
    "use_eoo": False,
    "use_df": True,
    "use_cw": True,
    "use_onslaught": True,

    # Single-target special moves
    "use_lightningstrike": False,
    "use_momentumstrike": False,

    # Defensive abilities
    "use_evasion": False,
    "use_confidence": False,

    # Healing & status
    "use_closewounds": False,
    "use_removepoison": False,
    "use_removecurse": False,
    "use_vampiricembrace": False,

    # Utility
    "use_messages": True
}

# Script control
script_running = True

USE_MESSAGES = CONFIG["use_messages"]

# --------------------------------------------------
# WEAPON TRAITS
# --------------------------------------------------
WEAPON_TRAITS = {
    0x0F4B: {"name": "Double Axe", "primary": "Double Strike", "aoe": "Whirlwind"},
    0x0F61: {"name": "Longsword", "primary": "Armor Ignore"},
    0xA28B: {"name": "Bladed Whip", "primary": "Bleed Attack", "aoe": "Whirlwind"},
    0x26BD: {"name": "Bladed Staff", "primary": "Armor Ignore"},
    0x0F5E: {"name": "Broadsword", "secondary": "Armor Ignore"},
    0x2D33: {"name": "Radiant Scimitar", "secondary": "Bladeweave", "aoe": "Whirlwind"},
    0xA289: {"name": "Barbed Whip", "primary": "Concussion Blow", "aoe": "Whirlwind"},
    0x143D: {"name": "Hammerpick", "primary": "Armor Ignore"},
    0x1439: {"name": "War Axe", "primary": "Armor Ignore"},
    0x48C0: {"name": "Gargish War Hammer", "primary": "Whirlwind"},
    0x13F8: {"name": "Gnarled Staff", "secondary": "Force of Nature"},
    0x48BC: {"name": "Gargish Kryss", "primary": "Armor Ignore"},
    0x0907: {"name": "Shortblade", "primary": "Armor Ignore"},
    0x08FE: {"name": "Bloodblade", "secondary": "Paralyzing Blow"},
    0x26C2: {"name": "Composite Bow", "primary": "Armor Ignore"},
    0x090A: {"name": "Soul Glaive", "primary": "Armor Ignore"},
    0x26C3: {"name": "Repeating Crossbow", "primary": "Double Strike"},
    0x27A5: {"name": "Yumi", "secondary": "Double Shot"}
}

# --------------------------------------------------
# FILTERING TARGETS
# --------------------------------------------------
summons_to_ignore = ["a reaper", "a rising colossus", "a nature's fury", "a blade spirit"]
mobs_to_ignore = ["addnameshere", "addnameshere2"]
ids_to_ignore = [0x00CB, 0x00CF]

ENEMY_NOTORIETY = [
    API.Notoriety.Gray,
    API.Notoriety.Criminal,
    API.Notoriety.Enemy,
    API.Notoriety.Murderer
]

# --------------------------------------------------
# DETECT CURRENT WEAPON
# --------------------------------------------------
equipped_weapon = {
    "graphic": None,
    "name": "Unknown",
    "primary": None,
    "secondary": None,
    "aoe": None
}

cooldowns = {}

weapon = API.FindLayer("OneHanded") or API.FindLayer("TwoHanded")

if weapon:
    graphic = weapon.Graphic
    traits = WEAPON_TRAITS.get(graphic)
    if traits:
        equipped_weapon.update({"graphic": graphic, **traits})
        if USE_MESSAGES:
            API.HeadMsg(f"Using {traits['name']} ({traits.get('primary', '')} {traits.get('aoe', '')})", API.Player, 946)
    else:
        equipped_weapon["graphic"] = graphic
        if USE_MESSAGES:
            API.HeadMsg("Weapon equipped, but unknown type.", API.Player, 946)
else:
    if USE_MESSAGES:
        API.HeadMsg("No weapon equipped!", API.Player, 33)

# --------------------------------------------------
# FUNCTION DEFINITIONS
# --------------------------------------------------

def should_continue():
    """Check if the script should continue running."""
    global script_running
    
    try:
        # Check if script_running flag is False
        if not script_running:
            return False
        
        # Check if player is dead
        if API.Player.IsDead:
            API.SysMsg("Player is dead - stopping attack script", 33)
            script_running = False
            return False
        
        # Check if we can still access the API (thread not interrupted)
        # This will raise an exception if the thread has been interrupted
        _ = API.Player.Hits  # Simple API call to test connectivity
        return True
    except Exception as e:
        API.SysMsg(f"Debug - should_continue() exception: {str(e)}", 33)
        script_running = False
        return False

def timer_exists(name):
    return name in cooldowns and cooldowns[name] > time.time()

def start_timer(name, seconds):
    cooldowns[name] = time.time() + seconds

def stop_script():
    """Stop the script gracefully."""
    global script_running
    script_running = False
    API.SysMsg("Attack script stopped", 946)


def is_valid_target(mob):
    name = (mob.Name or "").lower()
    if name in mobs_to_ignore:
        return False
    if name in summons_to_ignore:
        return False  # Ignore all summons regardless of notoriety
    if mob.Graphic in ids_to_ignore:
        return False
    # Only ignore human players, not human NPCs/mobs
    # Human NPCs will be included since they're already filtered by notoriety
    return True

def get_valid_enemies(max_range=10):
    all_mobs = API.NearestMobiles(ENEMY_NOTORIETY, max_range)
    return [mob for mob in all_mobs if is_valid_target(mob)]

def get_nearest_enemy(max_range=10):
    enemies = get_valid_enemies(max_range)
    return enemies[0] if enemies else None

def combat_controller(target, nearby_count, lmc=0.0):
    if not target:
        return

    API.Attack(target)
    if CONFIG["use_messages"]:
        API.HeadMsg("▼", target, 62)

    # Check if we're on global cooldown before casting spells
    if API.IsGlobalCooldownActive():
        return

    if CONFIG["use_eoo"] and not API.BuffExists("Enemy Of One") and API.Player.Mana >= 12:
        API.CastSpell("Enemy of One")
        API.Pause(0.5)

    if CONFIG["use_df"] and not API.BuffExists("Divine Fury") and API.Player.Mana >= 8:
        API.CastSpell("Divine Fury")
        API.Pause(0.5)

    if CONFIG["use_cw"] and not API.BuffExists("Consecrate") and API.Player.Mana >= 6:
        API.CastSpell("Consecrate Weapon")
        API.Pause(0.5)

    if CONFIG["use_onslaught"] and not timer_exists("onslaught"):
        if not API.PrimaryAbilityActive():
            if API.Player.Hits >= API.Player.HitsMax * 0.5 and API.Player.Mana >= (20 - (20 * lmc)):
                API.CastSpell("Onslaught")
                API.Pause(0.2)
                API.CreateCooldownBar(6.5, "Onslaught", 38)
                start_timer("onslaught", 6.5)

    if nearby_count >= 5:
        if not API.SecondaryAbilityActive() and API.Player.Mana >= (30 - (30 * lmc)):
            aoe = equipped_weapon.get("aoe")
            if aoe:
                API.HeadMsg(f"{aoe}!", target, 946)
                API.ToggleAbility("secondary")
                API.Pause(0.2)
            elif CONFIG.get("use_momentumstrike"):
                if not API.BuffExists("Momentum Strike") and API.Player.Mana >= 10:
                    API.HeadMsg("Momentum Strike", target, 946)
                    API.CastSpell("Momentum Strike")
                    API.Pause(0.2)
        return

    if not API.PrimaryAbilityActive() and API.Player.Mana >= (30 - (30 * lmc)):
        move = equipped_weapon.get("primary")
        if move:
            API.HeadMsg(move + "!", target, 946)
            API.ToggleAbility("primary")
            API.Pause(0.2)

    if CONFIG["use_lightningstrike"] and not API.BuffExists("Lightning Strike") and API.Player.Mana >= (10 - (10 * lmc)):
        API.CastSpell("Lightning Strike")
        API.Pause(0.2)

def cast_evasion_if_needed(lmc=0.0):
    if CONFIG.get("use_evasion") and not API.BuffExists("Evasion") and not API.BuffExists("Confidence") and API.Player.Hits < API.Player.HitsMax * 0.6:
        if API.Player.Mana >= (10 - (10 * lmc)) and not API.IsGlobalCooldownActive():
            API.CastSpell("Evasion")
            API.CreateCooldownBar(20, "Evasion", 65)
            API.Pause(0.2)

def cast_confidence_if_needed(lmc=0.0):
    if CONFIG.get("use_confidence") and not API.BuffExists("Evasion") and not API.BuffExists("Confidence"):
        if API.Player.Hits < API.Player.HitsMax * 0.85 and not API.IsGlobalCooldownActive():
            API.CastSpell("Confidence")
            API.Pause(0.2)

def remove_poison():
    if CONFIG.get("use_removepoison") and API.Player.IsPoisoned and not API.IsGlobalCooldownActive():
        API.CastSpell("Cleanse by fire")
        if API.WaitForTarget("Beneficial", 2):
            API.TargetSelf()
        API.Pause(0.2)

def remove_curse():
    if CONFIG.get("use_removecurse") and not API.IsGlobalCooldownActive():
        for curse in ["Curse", "Clumsy", "Weaken", "Strangle", "Blood Oath"]:
            if API.BuffExists(curse):
                API.CastSpell("Remove Curse")
                if API.WaitForTarget("Beneficial", 3):
                    API.TargetSelf()
                API.Pause(0.2)
                break

def heal_close_wounds():
    if CONFIG.get("use_closewounds") and API.Player.Hits < API.Player.HitsMax * 0.7 and not API.IsGlobalCooldownActive():
        API.CastSpell("Close Wounds")
        if API.WaitForTarget("Beneficial", 2):
            API.TargetSelf()
        API.Pause(0.2)

def break_paralyze():
    if API.BuffExists("Paralyze"):
        pouch = API.FindType(0x0E79, API.Backpack)
        if pouch:
            API.UseObject(pouch)
            API.Pause(0.3)
        else:
            API.HeadMsg("No trapped pouch!", API.Player, 33)

def check_vampiric_embrace():
    if not CONFIG.get("use_vampiricembrace"):
        return

    necro = API.GetSkill("Necromancy")
    if not necro or necro.Value < 99:
        return

    #if not API.BuffExists("Vampiric Embrace"):
        #API.HeadMsg("No Vampiric Embrace!", API.Player)
        

# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------
def main():
    """Main script execution with proper thread interruption handling."""
    global script_running
    
    try:
        API.SysMsg("Attack script started", 946)
        script_running = True
        API.SysMsg(f"Debug - script_running set to: {script_running}", 946)
        
        while should_continue():
            try:
                lmc = API.Player.LowerManaCost / 100.0
                cast_evasion_if_needed(lmc)
                cast_confidence_if_needed(lmc)
                remove_poison()
                remove_curse()
                heal_close_wounds()
                break_paralyze()
                check_vampiric_embrace()

                target = get_nearest_enemy(10)
                if target:
                    all_enemies = get_valid_enemies(10)
                    combat_controller(target, len(all_enemies), lmc)
                else:
                    heal_close_wounds()
                    remove_poison()
                    remove_curse()

                API.Pause(0.5)

            except Exception as e:
                API.SysMsg(f"Script Error: {str(e)}", 33)
                API.Pause(1)
        
        API.SysMsg(f"Debug - Exited while loop. script_running: {script_running}", 33)
        if script_running:
            API.SysMsg("Attack script stopped - should_continue() returned False", 33)
        else:
            API.SysMsg("Attack script stopped by user", 946)
                
    except KeyboardInterrupt:
        # Handle script stop request gracefully
        stop_script()
    except SystemExit:
        # Handle API.Stop() calls
        stop_script()
    except Exception as e:
        # Handle any other unexpected errors
        API.SysMsg(f"Fatal script error: {str(e)}", 33)
        stop_script()
        API.Stop()

# Run the main function

main()
