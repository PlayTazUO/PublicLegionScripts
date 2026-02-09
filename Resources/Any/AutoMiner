import API
import json
import ast
import os

# Debug log gump state (define early to avoid NameError in IronPython).
LOG_GUMP = None
LOG_TEXT = ""
LOG_LINES = []
LOG_EXPORT_BASE = None
LOG_PATH_TEXTBOX = None
"""
AutoMiner
Last Updated: 2026-02-09

Features:
- Runebook-driven mining loop (home rune in slot 1, mining runes in slots 2-15).
- Auto-mines nearby tiles and advances when the area is depleted.
- Overweight handling: smelt (optional) then recall home to unload and restock.
- Auto-unload: ore, ingots, gems, and blackrock to drop container.
- Tooling automation: optionally crafts tools or pulls shovels from drop container.
- Persistent settings for runebook, drop container, travel, tooling, smelt, debug, and shard.
- Debug log gump with export and toggleable debug messaging.

Updates:
2026-02-09
- Added Shard selector (OSI/UOAlive) that controls targeting order for mining.
- Added UOAlive tinker crafting flow (Tools category + shard-specific shovel/tinker buttons).
- Added debug toggle on the control gump with persisted state.
- Added debug log gump and export with a dedicated Log button.
- Improved mine targeting to use land/static targeting based on tile graphics.
- Limited mining to a 3x3 grid per recall center and reused that center until depleted.
- Added caching for non-mineable tiles and "cannot see location" tiles.
- Fixed journal logging order so cache decisions are based on intact journal entries.
- Updated gump layout (Debug row, Log/Start row, uniform button alignment).
- Fixed tooling pre-check to separate crafting vs. pull paths and guard tinker-tool usage.
- Fixed overweight flow to avoid duplicate logs and recall only after drop/smelt attempts.
- Corrected mountain mineable tile list (restored contiguous sequences; removed duplicates).
2026-02-07
- Added Auto Tooling toggle to choose between crafting tools or pulling shovels from drop container.
- Persisted Auto Tooling setting.
- Added shovel pull fallback and pause/recall logic when shovels are missing.
- Added Travel selection (Mage/Chiv) with alternate runebook button ranges (75-90).
- Persisted Fire Beetle smelt setting.
- Moved Start/Pause button to the bottom of the gump.
- Updated mining auto-targeting to use mineable tile graphics for reliable digging.

Controls (Gump):
- Start/Pause: start/stop mining loop.
- Use Fire Beetle: smelt at a nearby fire beetle when overweight.
- Auto Tooling: craft tools + shovels when enabled; otherwise pull shovels from drop container.
- Travel: Mage (Recall buttons 50-65) or Chiv (Sacred Journey buttons 75-90).
- Runebook: set/unset the runebook used for recalls.
- Drop Container: set/unset the container for ore/ingot/gem dropoff.

Setup (first run):
1) Runebook: Home recall rune must be in slot 1 (gump button 50).
2) Mining runes: Slots 2-15 (gump buttons 51-65) are mining locations.
3) If using Travel: Chiv, set home at button 75 and mining at buttons 76-90 instead.
4) Set Travel, Runebook, and Drop Container from the gump.
5) Set Auto Tooling ON if you want the script to craft tools and shovels.
6) If Auto Tooling is ON: start with two tinker's tools in your backpack and keep hue-0 ingots in the drop container.
7) If Auto Tooling is OFF: start with two shovels in your backpack and keep extra shovels in the drop container.
"""

# Journal texts that mark tiles as depleted.
NO_ORE_CACHE_TEXTS = [
    "There is no metal here to mine.",
    "You cannot see that location.",
    "Target cannot be seen.",
]
# Journal texts that indicate a mining tool broke.
TOOL_WORN_TEXTS = [
    "You have worn out your tool!",
    "You destroyed the item : pickaxe",
    "You destroyed the item : shovel",
]
# Journal texts to capture in the debug log.
JOURNAL_LOG_TEXTS = [
    "Where do you wish to dig?",
    "You can't mine there.",
    "You cannot see that location.",
    "Target cannot be seen.",
]
# Journal text when ore is lost due to full backpack.
OVERWEIGHT_TEXTS = [
    "Your backpack is full, so the ore you mined is lost.",
]
# Journal text for hard encumbrance (can't move).
ENCUMBERED_TEXTS = [
    "Thou art too encumbered to move.",
]

# Tool and resource graphics.
SHOVEL_GRAPHICS = [0x0F3A, 0x0F39]  # Shovel item graphics (0x0F39 for UOAlive).
PICKAXE_GRAPHIC = 0x0E86  # Pickaxe item graphic.
ORE_GRAPHICS = [0x19B9, 0x19B8, 0x19BA]  # Ore piles.
ORE_GRAPHIC_MIN2 = 0x19B7  # Ore that requires 2+ to smelt.
INGOT_GRAPHICS = [0x1BF2]  # Base ingot graphic.
GEM_GRAPHICS = [0x3198, 0x3197, 0x3194, 0x3193, 0x3192, 0x3195]  # Gems to deposit.
BLACKSTONE_GRAPHICS = [0x0F2A, 0x0F2B, 0x0F28, 0x0F26]  # Blackrock to deposit.

# Mineable tile graphics (land/statics). Derived from provided decimal lists.
CAVE_MINEABLE = [
    0x053B, 0x053C, 0x053D, 0x053E, 0x053F, 0x0540, 0x0541, 0x0542, 0x0543, 0x0544,
    0x0545, 0x0546, 0x0547, 0x0548, 0x0549, 0x054A, 0x054B, 0x054C, 0x054D, 0x054E,
    0x054F, 0x0551, 0x0552, 0x0553, 0x056A,
]
MOUNTAIN_MINEABLE = [
    0x00DC, 0x00DD, 0x00DE, 0x00DF, 0x00E0, 0x00E1, 0x00E2, 0x00E3, 0x00E4, 0x00E5,
    0x00E6, 0x00E7, 0x00EC, 0x00ED, 0x00EE, 0x00EF, 0x00F0, 0x00F1, 0x00F2, 0x00F3,
    0x00F4, 0x00F5, 0x00F6, 0x00F7, 0x00FC, 0x00FD, 0x00FE, 0x00FF, 0x0100, 0x0101,
    0x0102, 0x0103, 0x0104, 0x0105, 0x0106, 0x0107, 0x010C, 0x010D, 0x010E, 0x010F,
    0x0110, 0x0111, 0x0112, 0x0113, 0x0114, 0x0115, 0x0116, 0x0117, 0x011E, 0x011F,
    0x0120, 0x0121, 0x0122, 0x0123, 0x0124, 0x0125, 0x0126, 0x0127, 0x0128, 0x0129,
    0x0141, 0x0142, 0x0143, 0x0144, 0x01D3, 0x01D4, 0x01D5, 0x01D6, 0x01D7, 0x01D8,
    0x01D9, 0x01DA, 0x01DB, 0x01DC, 0x01DD, 0x01DE, 0x01DF, 0x01E0, 0x01E1, 0x01E2, 0x01E3,
    0x01E4, 0x01E5, 0x01E6, 0x01E7, 0x01EC, 0x01ED, 0x01EE, 0x01EF, 0x021F, 0x0220,
    0x0221, 0x0222, 0x0223, 0x0224, 0x0225, 0x0226, 0x0227, 0x0228, 0x0229, 0x022A,
    0x022B, 0x022C, 0x022D, 0x022E, 0x022F, 0x0230, 0x0231, 0x0232, 0x0233, 0x0234,
    0x0235, 0x0236, 0x0237, 0x0238, 0x0239, 0x023A, 0x023B, 0x023C, 0x023D, 0x023E,
    0x023F, 0x0240, 0x0241, 0x0242, 0x0243, 0x0244, 0x0245, 0x0246, 0x0247, 0x0248,
    0x0249, 0x024A, 0x024B, 0x024C, 0x024D, 0x024E, 0x024F, 0x0250, 0x0251, 0x0252,
    0x0253, 0x0254, 0x0255, 0x0256, 0x0257, 0x0258, 0x0259, 0x025A, 0x025B, 0x025C,
    0x025D, 0x025E, 0x025F, 0x0260, 0x0261, 0x0262, 0x0263, 0x0264, 0x0265, 0x0266,
    0x0267, 0x0268, 0x0269, 0x026A, 0x026B, 0x026C, 0x026D, 0x026E, 0x026F, 0x0270,
    0x0271, 0x0272, 0x0273, 0x0274, 0x0275, 0x0276, 0x0277, 0x0278, 0x0279, 0x027A,
    0x027B, 0x027C, 0x027D, 0x027E, 0x027F, 0x0280, 0x0281, 0x0282, 0x0283, 0x0284,
    0x0285, 0x0286, 0x0287, 0x0288, 0x0289, 0x028A, 0x028B, 0x028C, 0x028D, 0x028E,
    0x028F, 0x0290, 0x0291, 0x0292, 0x0293, 0x0294, 0x0295, 0x0296, 0x0297, 0x0298,
    0x0299, 0x029A, 0x029B, 0x029C, 0x029D, 0x029E, 0x02E2, 0x02E3, 0x02E4, 0x02E5,
    0x02E6, 0x02E7, 0x02E8, 0x02E9, 0x02EA, 0x02EB, 0x02EC, 0x02ED, 0x02EE, 0x02EF,
    0x02F0, 0x02F1, 0x02F2, 0x02F3, 0x02F4, 0x02F5, 0x02F6, 0x02F7, 0x02F8, 0x02F9,
    0x02FA, 0x02FB, 0x02FC, 0x02FD, 0x02FE, 0x02FF, 0x0300, 0x0301, 0x0302, 0x0303,
    0x0304, 0x0305, 0x0306, 0x0307, 0x0308, 0x0309, 0x030A, 0x030B, 0x030C, 0x030D,
    0x030E, 0x030F, 0x0310, 0x0311, 0x0312, 0x0313, 0x0314, 0x0315, 0x0316, 0x0317,
    0x0318, 0x0319, 0x031A, 0x031B, 0x031C, 0x031D, 0x031E, 0x031F, 0x0320, 0x0321,
    0x0322, 0x0323, 0x0324, 0x0325, 0x0326, 0x0327, 0x0328, 0x0329, 0x032A, 0x032B,
    0x032C, 0x032D, 0x032E, 0x032F, 0x0330, 0x0331, 0x0332, 0x0333, 0x0334, 0x0335,
    0x0336, 0x0337, 0x0338, 0x0339, 0x033A, 0x033B, 0x033C, 0x033D, 0x033E, 0x033F,
    0x0340, 0x0341, 0x0342, 0x0343, 0x03F2, 0x06CD, 0x06CE, 0x06CF, 0x06D0, 0x06D1,
    0x06D2, 0x06D3, 0x06D4, 0x06D5, 0x06D6, 0x06D7, 0x06D8, 0x06D9, 0x06DA, 0x06DB,
    0x06DC, 0x06ED, 0x06EE, 0x06EF, 0x06F0, 0x06F1, 0x06F2, 0x06F3, 0x06F4, 0x06F5,
    0x06F6, 0x06F7, 0x06F8, 0x06F9, 0x06FA, 0x06FB, 0x06FC, 0x06FD, 0x06FE, 0x06FF,
    0x0700, 0x0709, 0x070A, 0x070B, 0x070C, 0x070D, 0x070E, 0x070F, 0x0710, 0x0711,
    0x0712, 0x0713, 0x0714, 0x0715, 0x0716, 0x0717, 0x0718, 0x0719, 0x071A, 0x071B,
    0x071C, 0x071D, 0x071E, 0x071F, 0x0720, 0x0721, 0x0722, 0x0723, 0x0724, 0x0725,
    0x0726, 0x0727, 0x0728, 0x0729, 0x072A, 0x072B, 0x072C, 0x072D, 0x072E, 0x072F,
    0x0730, 0x0731, 0x0732, 0x0733, 0x0734, 0x0735, 0x0736, 0x0737, 0x0738, 0x0739,
    0x073A, 0x073B, 0x073C, 0x073D, 0x073E, 0x073F, 0x0740, 0x0741, 0x0742, 0x0743,
    0x0744, 0x0745, 0x0746, 0x0747, 0x0748, 0x0749, 0x074A, 0x074B, 0x074C, 0x074D,
    0x074E, 0x074F, 0x0750, 0x0751, 0x0752, 0x0753, 0x0754, 0x0755, 0x0756, 0x0757,
    0x0758, 0x0759, 0x075A, 0x075B, 0x075C, 0x075D, 0x075E, 0x075F, 0x0760, 0x0761,
    0x0762, 0x0763, 0x0764, 0x0765, 0x0766, 0x0767, 0x0768, 0x0769, 0x076A, 0x076B,
    0x076C, 0x076D, 0x076E, 0x076F, 0x0770, 0x0771, 0x0772, 0x0773, 0x0774, 0x0775,
    0x0776, 0x0777, 0x0778, 0x0779, 0x077A, 0x077B, 0x077C, 0x077D, 0x077E, 0x077F,
    0x0780, 0x0781, 0x0782, 0x0783, 0x0784, 0x0785, 0x0786, 0x0787, 0x0788, 0x0789,
    0x078A, 0x078B, 0x078C, 0x078D, 0x078E, 0x078F, 0x0790, 0x0791, 0x0792, 0x0793,
    0x0794, 0x0795, 0x0796, 0x0797, 0x0798, 0x0799, 0x079A, 0x079B, 0x079C, 0x079D,
    0x079E, 0x079F, 0x07A0, 0x07A1, 0x07A2, 0x07A3, 0x07A4, 0x07A5, 0x083C, 0x083D,
    0x083E, 0x083F, 0x0840, 0x0841, 0x0842, 0x0843, 0x0844, 0x0845, 0x0846, 0x0847,
    0x0848, 0x0849, 0x084A, 0x084B, 0x084C, 0x084D, 0x084E, 0x084F, 0x0850, 0x0851,
    0x0852, 0x0853, 0x0854, 0x0855, 0x0856, 0x0857, 0x0858, 0x0859, 0x085A, 0x085B,
    0x085C, 0x085D, 0x085E, 0x085F, 0x0860, 0x0861, 0x0862, 0x0863, 0x0864, 0x0865,
    0x0866, 0x0867, 0x0868, 0x0869, 0x086A, 0x086B, 0x086C, 0x086D, 0x086E, 0x086F,
    0x0870, 0x0871, 0x0872, 0x0873, 0x0874, 0x0875, 0x0876, 0x0877, 0x0878, 0x0879,
    0x087A, 0x087B, 0x087C, 0x087D, 0x087E, 0x087F, 0x0880, 0x0881, 0x0882, 0x0883,
    0x0884, 0x0885, 0x0886, 0x0887, 0x0888, 0x0889, 0x088A, 0x088B, 0x088C, 0x088D,
    0x088E, 0x088F, 0x0890, 0x0891, 0x0892, 0x0893, 0x0894, 0x0895, 0x0896, 0x0897,
    0x0898, 0x0899, 0x089A, 0x089B, 0x089C, 0x089D, 0x089E, 0x089F, 0x08A0, 0x08A1,
    0x08A2, 0x08A3, 0x08A4, 0x08A5, 0x08A6, 0x08A7, 0x08A8, 0x08A9, 0x08AA, 0x08AB,
    0x08AC, 0x08AD, 0x08AE, 0x08AF, 0x08B0, 0x08B1, 0x08B2, 0x08B3, 0x08B4, 0x08B5,
    0x08B6, 0x08B7, 0x08B8, 0x08B9, 0x08BA, 0x08BB, 0x08BC, 0x08BD, 0x08BE, 0x08BF,
    0x08C0, 0x08C1, 0x08C2, 0x08C3, 0x08C4, 0x08C5, 0x08C6, 0x08C7, 0x08C8, 0x08C9,
    0x08CA, 0x08CB, 0x08CC, 0x08CD, 0x08CE, 0x08CF, 0x08D0, 0x08D1, 0x08D2, 0x08D3,
    0x08D4, 0x08D5, 0x08D6, 0x08D7, 0x08D8, 0x08D9, 0x08DA, 0x08DB, 0x08DC, 0x08DD,
    0x08DE, 0x08DF, 0x08E0, 0x08E1, 0x08E2, 0x08E3, 0x08E4, 0x08E5, 0x08E6, 0x08E7,
    0x08E8, 0x08E9, 0x08EA, 0x08EB, 0x08EC, 0x08ED, 0x08EE, 0x08EF, 0x08F0, 0x08F1,
    0x08F2, 0x08F3, 0x08F4, 0x08F5, 0x08F6, 0x08F7, 0x08F8, 0x08F9, 0x08FA, 0x08FB,
    0x08FC, 0x08FD, 0x08FE, 0x08FF, 0x0900, 0x0901, 0x0902, 0x0903, 0x0904, 0x0905,
    0x0906, 0x0907, 0x0908, 0x0909, 0x090A, 0x090B, 0x090C, 0x090D, 0x090E, 0x090F,
    0x0910, 0x0911, 0x0912, 0x0913, 0x0914, 0x0915, 0x0916, 0x0917, 0x0918, 0x0919,
    0x091A, 0x091B, 0x091C, 0x091D, 0x091E, 0x091F, 0x0920, 0x0921, 0x0922, 0x0923,
    0x0924, 0x0925, 0x0926, 0x0927, 0x0928, 0x0929, 0x092A, 0x092B, 0x092C, 0x092D,
    0x092E, 0x092F, 0x0930, 0x0931, 0x0932, 0x0933, 0x0934, 0x0935, 0x0936, 0x0937,
    0x0938, 0x0939, 0x093A, 0x093B, 0x093C, 0x093D, 0x093E, 0x093F, 0x0940, 0x0941,
    0x0942, 0x0943, 0x0944, 0x0945, 0x0946, 0x0947, 0x0948, 0x0949, 0x094A, 0x094B,
    0x094C, 0x094D, 0x094E, 0x094F, 0x0950, 0x0951, 0x0952, 0x0953, 0x0954, 0x0955,
    0x0956, 0x0957, 0x0958, 0x0959, 0x095A, 0x095B, 0x095C, 0x095D, 0x095E, 0x095F,
    0x0960, 0x0961, 0x0962, 0x0963, 0x0964, 0x0965, 0x0966, 0x0967, 0x0968, 0x0969,
    0x096A, 0x096B, 0x096C, 0x096D, 0x096E, 0x096F, 0x0970, 0x0971, 0x0972, 0x0973,
    0x0974, 0x0975, 0x0976, 0x0977, 0x0978, 0x0979, 0x097A, 0x097B, 0x097C, 0x097D,
    0x097E, 0x097F, 0x0980, 0x0981, 0x0982, 0x0983, 0x0984, 0x0985, 0x0986, 0x0987,
    0x0988, 0x0989, 0x098A, 0x098B, 0x098C, 0x098D, 0x098E, 0x098F, 0x0990, 0x0991,
    0x0992, 0x0993, 0x0994, 0x0995, 0x0996, 0x0997, 0x0998, 0x0999, 0x099A, 0x099B,
    0x099C, 0x099D, 0x099E, 0x099F, 0x09A0, 0x09A1, 0x09A2, 0x09A3, 0x09A4, 0x09A5,
    0x09A6, 0x09A7, 0x09A8, 0x09A9, 0x09AA, 0x09AB, 0x09AC, 0x09AD, 0x09AE, 0x09AF,
    0x09B0, 0x09B1, 0x09B2, 0x09B3, 0x09B4, 0x09B5, 0x09B6, 0x09B7, 0x09B8, 0x09B9,
    0x09BA, 0x09BB, 0x09BC, 0x09BD, 0x09BE, 0x09BF, 0x09C0, 0x09C1, 0x09C2, 0x09C3,
    0x09C4, 0x09C5, 0x09C6, 0x09C7, 0x09C8, 0x09C9, 0x09CA, 0x09CB, 0x09CC, 0x09CD,
    0x09CE, 0x09CF, 0x09D0, 0x09D1, 0x09D2, 0x09D3, 0x09D4, 0x09D5, 0x09D6, 0x09D7,
    0x09D8, 0x09D9, 0x09DA, 0x09DB, 0x09DC, 0x09DD, 0x09DE, 0x09DF, 0x09E0, 0x09E1,
    0x09E2, 0x09E3, 0x09E4, 0x09E5, 0x09E6, 0x09E7, 0x09E8, 0x09E9, 0x09EA, 0x09EB,
    0x09EC, 0x09ED, 0x09EE, 0x09EF, 0x09F0, 0x09F1, 0x09F2, 0x09F3, 0x09F4, 0x09F5,
    0x09F6, 0x09F7, 0x09F8, 0x09F9, 0x09FA, 0x09FB, 0x09FC, 0x09FD, 0x09FE, 0x09FF,
    0x0A00, 0x0A01, 0x0A02, 0x0A03, 0x0A04, 0x0A05, 0x0A06, 0x0A07, 0x0A08, 0x0A09,
    0x0A0A, 0x0A0B, 0x0A0C, 0x0A0D, 0x0A0E, 0x0A0F, 0x0A10, 0x0A11, 0x0A12, 0x0A13,
    0x0A14, 0x0A15, 0x0A16, 0x0A17, 0x0A18, 0x0A19, 0x0A1A, 0x0A1B, 0x0A1C, 0x0A1D,
    0x0A1E, 0x0A1F, 0x0A20, 0x0A21, 0x0A22, 0x0A23, 0x0A24, 0x0A25, 0x0A26, 0x0A27,
    0x0A28, 0x0A29, 0x0A2A, 0x0A2B, 0x0A2C, 0x0A2D, 0x0A2E, 0x0A2F, 0x0A30, 0x0A31,
    0x0A32, 0x0A33, 0x0A34, 0x0A35, 0x0A36, 0x0A37, 0x0A38, 0x0A39, 0x0A3A, 0x0A3B,
    0x0A3C, 0x0A3D, 0x0A3E, 0x0A3F, 0x0A40, 0x0A41, 0x0A42, 0x0A43, 0x0A44, 0x0A45,
    0x0A46, 0x0A47, 0x0A48, 0x0A49, 0x0A4A, 0x0A4B, 0x0A4C, 0x0A4D, 0x0A4E, 0x0A4F,
    0x0A50, 0x0A51, 0x0A52, 0x0A53, 0x0A54, 0x0A55, 0x0A56, 0x0A57, 0x0A58, 0x0A59,
    0x0A5A, 0x0A5B, 0x0A5C, 0x0A5D, 0x0A5E, 0x0A5F, 0x0A60, 0x0A61, 0x0A62, 0x0A63,
    0x0A64, 0x0A65, 0x0A66, 0x0A67, 0x0A68, 0x0A69, 0x0A6A, 0x0A6B, 0x0A6C, 0x0A6D,
    0x0A6E, 0x0A6F, 0x0A70, 0x0A71, 0x0A72, 0x0A73, 0x0A74, 0x0A75, 0x0A76, 0x0A77,
    0x0A78, 0x0A79, 0x0A7A, 0x0A7B, 0x0A7C, 0x0A7D, 0x0A7E, 0x0A7F, 0x0A80, 0x0A81,
    0x0A82, 0x0A83, 0x0A84, 0x0A85, 0x0A86, 0x0A87, 0x0A88, 0x0A89, 0x0A8A, 0x0A8B,
    0x0A8C, 0x0A8D, 0x0A8E, 0x0A8F, 0x0A90, 0x0A91, 0x0A92, 0x0A93, 0x0A94, 0x0A95,
    0x0A96, 0x0A97, 0x0A98, 0x0A99, 0x0A9A, 0x0A9B, 0x0A9C, 0x0A9D, 0x0A9E, 0x0A9F,
    0x0AA0, 0x0AA1, 0x0AA2, 0x0AA3, 0x0AA4, 0x0AA5, 0x0AA6, 0x0AA7, 0x0AA8, 0x0AA9,
]
ROCK_MINEABLE = [
    0x453B, 0x453C, 0x453D, 0x453E, 0x453F, 0x4540, 0x4541, 0x4542, 0x4543, 0x4544,
    0x4545, 0x4546, 0x4547, 0x4548, 0x4549, 0x454A, 0x454B, 0x454C, 0x454D, 0x454E,
    0x454F,
]
MINEABLE_GRAPHICS = set(CAVE_MINEABLE + MOUNTAIN_MINEABLE + ROCK_MINEABLE)

# Drop and hue priorities (smaller graphic first, then hue order).
DROP_PRIORITY = [0x19B7, 0x19BA, 0x19B8, 0x19B9]
ORE_HUE_PRIORITY = [0, 2419, 2406, 2413, 2418, 2213, 2425, 2207, 2219]

# Tinkering and smelting helpers.
TINKER_TOOL_GRAPHICS = [0x1EB9, 0x1EB8]  # Tinker's tool graphics (UOAlive uses 0x1EB8).
FORGE_GRAPHICS = [0x0FB1, 0x0E58]  # Common forges.
FORGE_RANGE = 2  # Search radius for forges and beetles.
FIRE_BEETLE_GRAPHIC = 0x00A9  # Fire beetle graphic.

# Behavior flags and UI.
DEBUG_STATICS = False  # Enable static debug output near forges.
DEBUG_STATICS_LIMIT = 20  # Max statics to print when debugging.
DEBUG_SMELT = False  # Enable smelt debug output.
DEBUG_TARGETING = True  # Enable mining target debug output.
AUTO_TARGET_Z_SCAN = False  # Try Z-scan targeting when LastTargetGraphic is 0.
AUTO_TARGET_Z_SCAN_RANGE = 20  # Z scan range (+/-) when enabled.
DEBUG_LOG_MAX_CHARS = 5000
LOG_DATA_KEY = "mining_bot_log_config"
AUTO_TARGET_MINE = True  # Use auto-target mining offsets.
HEADMSG_HUE = 1285  # Hue for overhead messages.
RUNNING = False  # Script run state.
CONTROL_GUMP = None  # Root gump reference.
CONTROL_BUTTON = None  # Enable/Disable button reference.
CONTROL_CONTROLS = []  # Strong refs to gump controls.
USE_FIRE_BEETLE_SMELT = False  # Toggle smelting on beetle.
USE_TOOL_CRAFTING = True  # Toggle auto tool crafting.
USE_SACRED_JOURNEY = False  # Toggle sacred journey button ranges.
USE_UOALIVE_SHARD = False  # Toggle shard targeting order (UOAlive vs OSI).

# Debug log gump state.

# Persisted serials.
RUNBOOK_SERIAL = 0  # Runebook serial.
SECURE_CONTAINER_SERIAL = 0  # Drop container serial.

# Recall loop and cache state.
USE_RECALL_ON_OVERWEIGHT = True  # Permanent: recall on overweight.
NO_ORE_TILE_CACHE = set()  # Cached depleted tiles at current spot.
NON_MINEABLE_TILE_CACHE = set()  # Cached non-mineable tiles at current spot.
LAST_PLAYER_POS = None  # Last known player position.
MINE_CENTER = None  # Anchor position for the current mining spot.
LAST_MINE_PASS_POS = None  # Last position where a full 3x3 pass was attempted.
HOME_RECALL_BUTTON = 50  # Default home button (recall).
MINING_RUNES = list(range(51, 66))  # Default mining buttons (recall).
CURRENT_MINING_INDEX = 0  # Current mining rune index.
NEEDS_TOOL_CHECK = False  # Deferred tooling check flag.
NEEDS_INITIAL_RECALL = False  # Deferred first recall flag.

# Round-robin drop offsets around the player.
DROP_OFFSETS = [
    (-1, -1),
    (0, -1),
    (1, -1),
    (-1, 0),
    (1, 0),
    (-1, 1),
    (0, 1),
    (1, 1),
]
DROP_OFFSET_INDEX = 0

# Smelting feedback texts.
SMELT_SUCCESS_TEXTS = [
    "You smelt the ore into ingots",
]
SMELT_FAIL_TEXTS = [
    "That is too far away",
    "You can't smelt",
    "You cannot smelt",
    "You must be near",
]
# Persistent storage key.
DATA_KEY = "mining_bot_config"

def _default_config():
    # Default persisted settings.
    return {
        "runebook_serial": 0,
        "drop_container_serial": 0,
        "use_fire_beetle_smelt": False,
        "use_tool_crafting": True,
        "use_sacred_journey": False,
        "debug_targeting": True,
        "use_uoalive_shard": False,
    }

def _load_config():
    # Load persisted settings for runebook/drop.
    global RUNBOOK_SERIAL, SECURE_CONTAINER_SERIAL, USE_TOOL_CRAFTING, USE_FIRE_BEETLE_SMELT, USE_SACRED_JOURNEY, DEBUG_TARGETING, USE_UOALIVE_SHARD
    raw = API.GetPersistentVar(DATA_KEY, "", API.PersistentVar.Char)
    if raw:
        try:
            try:
                data = json.loads(raw)
            except Exception:
                data = ast.literal_eval(raw)
            RUNBOOK_SERIAL = int(data.get("runebook_serial", 0) or 0)
            SECURE_CONTAINER_SERIAL = int(data.get("drop_container_serial", 0) or 0)
            USE_FIRE_BEETLE_SMELT = bool(data.get("use_fire_beetle_smelt", False))
            USE_TOOL_CRAFTING = bool(data.get("use_tool_crafting", True))
            USE_SACRED_JOURNEY = bool(data.get("use_sacred_journey", False))
            DEBUG_TARGETING = bool(data.get("debug_targeting", True))
            USE_UOALIVE_SHARD = bool(data.get("use_uoalive_shard", False))
            _refresh_recall_buttons()
            return
        except Exception:
            pass
    data = _default_config()
    RUNBOOK_SERIAL = data["runebook_serial"]
    SECURE_CONTAINER_SERIAL = data["drop_container_serial"]
    USE_SACRED_JOURNEY = data["use_sacred_journey"]
    DEBUG_TARGETING = data["debug_targeting"]
    USE_UOALIVE_SHARD = data["use_uoalive_shard"]
    _refresh_recall_buttons()

def _save_config():
    # Save persisted settings for runebook/drop.
    data = {
        "runebook_serial": int(RUNBOOK_SERIAL or 0),
        "drop_container_serial": int(SECURE_CONTAINER_SERIAL or 0),
        "use_fire_beetle_smelt": bool(USE_FIRE_BEETLE_SMELT),
        "use_tool_crafting": bool(USE_TOOL_CRAFTING),
        "use_sacred_journey": bool(USE_SACRED_JOURNEY),
        "debug_targeting": bool(DEBUG_TARGETING),
        "use_uoalive_shard": bool(USE_UOALIVE_SHARD),
    }
    API.SavePersistentVar(DATA_KEY, json.dumps(data), API.PersistentVar.Char)
# Tinker gump + button ids.
TINKER_GUMP_ID_OSI = 0x1CC  # Tinker gump id (OSI).
TINKER_BTN_SHOVEL_OSI = 18  # Craft shovel button (OSI).
TINKER_BTN_TINKER_TOOL_OSI = 11  # Craft tinker tool button (OSI).
TINKER_GUMP_ID_UOALIVE = 0xD466EA9C  # Tinker gump id (UOAlive).
TINKER_BTN_TOOLS_UOALIVE = 41  # Tools category (UOAlive).
TINKER_BTN_TINKER_TOOL_UOALIVE = 62  # Tinker tool button (UOAlive).
TINKER_BTN_SHOVEL_UOALIVE = 202  # Shovel button (UOAlive).

def _find_ore_in_backpack():
    # Find the next smeltable ore in the backpack, honoring special min-stack rules.
    # Special case: only smelt 0x19B7 when stack is 2+ (check recursively).
    items = API.ItemsInContainer(API.Backpack, True)
    if items:
        for item in items:
            if item.Graphic == ORE_GRAPHIC_MIN2 and int(item.Amount) >= 2:
                return item
    for graphic in ORE_GRAPHICS:
        ore = API.FindType(graphic, API.Backpack)
        if ore:
            return ore
    return None

def _find_item_by_graphic(graphic):
    # Return the first item in the backpack (recursive) matching the graphic.
    items = API.ItemsInContainer(API.Backpack, True)
    if not items:
        return None
    for item in items:
        if item.Graphic == graphic:
            return item
    return None

def _get_items_by_graphic(graphic):
    # Return all items in backpack matching the graphic.
    items = API.ItemsInContainer(API.Backpack, True)
    if not items:
        return []
    if isinstance(graphic, (list, tuple, set)):
        return [i for i in items if i.Graphic in graphic]
    return [i for i in items if i.Graphic == graphic]

def _count_ingots_in_backpack():
    # Count hue-0 ingots in the backpack.
    total = 0
    items = API.ItemsInContainer(API.Backpack, True) or []
    for item in items:
        if item.Graphic in INGOT_GRAPHICS and int(item.Hue) == 0:
            total += int(item.Amount)
    return total

def _count_shovels_in_backpack():
    # Count shovels in the backpack.
    items = API.ItemsInContainer(API.Backpack, True) or []
    return sum(1 for i in items if i.Graphic in SHOVEL_GRAPHICS)

def _count_tinker_tools_in_backpack():
    # Count tinker's tools in the backpack.
    items = API.ItemsInContainer(API.Backpack, True) or []
    return sum(1 for i in items if i.Graphic in TINKER_TOOL_GRAPHICS)

def _has_tinker_tool():
    # Check for a tinker's tool in the backpack.
    return _find_tinker_tool() is not None

def _find_tinker_tool():
    # Find the first tinker's tool in the backpack.
    for graphic in TINKER_TOOL_GRAPHICS:
        tool = API.FindType(graphic, API.Backpack)
        if tool:
            return tool
    return None

def _tinker_tool_near_break():
    # Check if any tinker's tool has 1 use remaining.
    items = _get_items_by_graphic(TINKER_TOOL_GRAPHICS)
    for item in items:
        try:
            props = item.NameAndProps(True, 2) or ""
        except Exception:
            props = ""
        if "Uses remaining: 1" in props:
            return True
    return False

def _craft_with_tinker(button_id):
    # Craft an item using the tinker's tool gump.
    tool = _find_tinker_tool()
    if not tool:
        return False
    API.UseObject(tool.Serial)
    gump_id = TINKER_GUMP_ID_UOALIVE if USE_UOALIVE_SHARD else TINKER_GUMP_ID_OSI
    if not API.WaitForGump(gump_id, 3):
        API.SysMsg("Tinker gump not found.")
        return False
    _sleep(0.5)
    API.ReplyGump(int(button_id), gump_id)
    _sleep(0.5)
    API.CloseGump(gump_id)
    API.CloseGump()
    return True

def _craft_with_tinker_uoalive(button_id):
    # Craft an item using the UOAlive tools category flow.
    tool = _find_tinker_tool()
    if not tool:
        return False
    API.UseObject(tool.Serial)
    if not API.WaitForGump(TINKER_GUMP_ID_UOALIVE, 3):
        API.SysMsg("Tinker gump not found.")
        return False
    _sleep(0.5)
    API.ReplyGump(int(TINKER_BTN_TOOLS_UOALIVE), TINKER_GUMP_ID_UOALIVE)
    _sleep(0.5)
    API.ReplyGump(int(button_id), TINKER_GUMP_ID_UOALIVE)
    _sleep(0.5)
    API.CloseGump(TINKER_GUMP_ID_UOALIVE)
    API.CloseGump()
    return True

def _craft_tinker_tool():
    # Craft a spare tinker's tool (OSI only unless UOAlive button is known).
    if USE_UOALIVE_SHARD:
        return _craft_with_tinker_uoalive(TINKER_BTN_TINKER_TOOL_UOALIVE)
    return _craft_with_tinker(TINKER_BTN_TINKER_TOOL_OSI)

def _craft_shovel():
    # Craft a shovel using the shard-appropriate button flow.
    if USE_UOALIVE_SHARD:
        return _craft_with_tinker_uoalive(TINKER_BTN_SHOVEL_UOALIVE)
    return _craft_with_tinker(TINKER_BTN_SHOVEL_OSI)

def _ensure_tooling_in_backpack():
    # Ensure required tools exist before mining.
    if USE_TOOL_CRAFTING:
        tinker_count = _count_tinker_tools_in_backpack()
        if tinker_count == 0:
            API.HeadMsg("No tinker's tool in backpack.", API.Player, HEADMSG_HUE)
            API.HeadMsg("You forgot to bring your tinker's tool", API.Player, HEADMSG_HUE)
            _stop_running_with_message()
            return
        if tinker_count == 1:
            _craft_tinker_tool()
        if _count_shovels_in_backpack() == 0:
            _craft_shovel()
        return
    if _count_shovels_in_backpack() == 0:
        _ensure_shovels_from_drop_container()


def _ensure_shovels_from_drop_container():
    # Pull shovels from the drop container when auto tooling is disabled.
    count = _count_shovels_in_backpack()
    if count == 0:
        API.SysMsg("No shovels in backpack. Recalling home and pausing.")
        _recall_home()
        _stop_running_with_message()
        return
    if count >= 2:
        return
    if not SECURE_CONTAINER_SERIAL:
        API.SysMsg("Drop container not set. Pausing.")
        _stop_running_with_message()
        return
    items = API.ItemsInContainer(SECURE_CONTAINER_SERIAL, True) or []
    for item in items:
        if item.Graphic in SHOVEL_GRAPHICS and _count_shovels_in_backpack() < 2:
            API.MoveItem(item.Serial, API.Backpack, 1)
            _sleep(0.6)
    if _count_shovels_in_backpack() == 0:
        API.SysMsg("No shovels available in drop container. Recalling home and pausing.")
        _recall_home()
        _stop_running_with_message()

def _find_drop_item():
    # Drop by smallest graphic, then by hue priority (iron -> hued), then by lowest hue value.
    items = API.ItemsInContainer(API.Backpack, True) or []
    if not items:
        return None
    for graphic in sorted(set(DROP_PRIORITY)):
        candidates = [i for i in items if i.Graphic == graphic]
        if not candidates:
            continue
        for hue in ORE_HUE_PRIORITY:
            for item in candidates:
                try:
                    if int(item.Hue) == int(hue):
                        return item
                except Exception:
                    continue
        try:
            return sorted(candidates, key=lambda i: int(i.Hue))[0]
        except Exception:
            return candidates[0]
    return None

def _toggle_running():
    # Toggle the main run state and refresh the gump button text.
    global RUNNING, NEEDS_TOOL_CHECK, NEEDS_INITIAL_RECALL
    RUNNING = not RUNNING
    state = "ON" if RUNNING else "OFF"
    if RUNNING:
        API.Dismount()
        API.ToggleFly()
        NEEDS_TOOL_CHECK = True
        if RUNBOOK_SERIAL:
            NEEDS_INITIAL_RECALL = True
    API.SysMsg(f"Mining: {state}")
    _update_control_gump()

def _toggle_fire_beetle():
    # Toggle fire beetle smelting.
    global USE_FIRE_BEETLE_SMELT
    USE_FIRE_BEETLE_SMELT = not USE_FIRE_BEETLE_SMELT
    _save_config()

def _toggle_tool_crafting():
    # Toggle auto tool crafting.
    global USE_TOOL_CRAFTING
    USE_TOOL_CRAFTING = not USE_TOOL_CRAFTING
    _save_config()

def _refresh_recall_buttons():
    global HOME_RECALL_BUTTON, MINING_RUNES
    if USE_SACRED_JOURNEY:
        HOME_RECALL_BUTTON = 75
        MINING_RUNES = list(range(76, 91))
    else:
        HOME_RECALL_BUTTON = 50
        MINING_RUNES = list(range(51, 66))

def _set_travel_chiv():
    global USE_SACRED_JOURNEY
    USE_SACRED_JOURNEY = True
    _refresh_recall_buttons()
    _save_config()
    _rebuild_control_gump()


def _set_travel_mage():
    global USE_SACRED_JOURNEY
    USE_SACRED_JOURNEY = False
    _refresh_recall_buttons()
    _save_config()
    _rebuild_control_gump()

def _unset_runebook():
    # Clear the runebook serial.
    global RUNBOOK_SERIAL
    RUNBOOK_SERIAL = 0
    API.SysMsg("Runebook unset.")
    _save_config()
    _rebuild_control_gump()

def _unset_secure_container():
    # Clear the drop container serial.
    global SECURE_CONTAINER_SERIAL
    SECURE_CONTAINER_SERIAL = 0
    API.SysMsg("Drop container unset.")
    _save_config()
    _rebuild_control_gump()

def _set_runebook():
    # Target and set the runebook.
    global RUNBOOK_SERIAL
    API.SysMsg("Target your runebook.")
    serial = API.RequestTarget()
    if serial:
        RUNBOOK_SERIAL = int(serial)
        API.SysMsg("Runebook set.")
        _save_config()
        _rebuild_control_gump()

def _set_secure_container():
    # Target and set the drop container.
    global SECURE_CONTAINER_SERIAL
    API.SysMsg("Target your secure container.")
    serial = API.RequestTarget()
    if serial:
        SECURE_CONTAINER_SERIAL = int(serial)
        API.SysMsg("Drop container set.")
        _save_config()
        _rebuild_control_gump()

def _set_shard_osi():
    # Use OSI targeting order.
    global USE_UOALIVE_SHARD
    USE_UOALIVE_SHARD = False
    API.SysMsg("Shard set to OSI.")
    _save_config()
    _rebuild_control_gump()

def _set_shard_uoalive():
    # Use UOAlive targeting order.
    global USE_UOALIVE_SHARD
    USE_UOALIVE_SHARD = True
    API.SysMsg("Shard set to UOAlive.")
    _save_config()
    _rebuild_control_gump()

def _set_debug_on():
    # Enable debug system messages.
    global DEBUG_TARGETING
    DEBUG_TARGETING = True
    API.SysMsg("Debug messages enabled.")
    _save_config()
    _rebuild_control_gump()

def _set_debug_off():
    # Disable debug system messages.
    global DEBUG_TARGETING
    DEBUG_TARGETING = False
    API.SysMsg("Debug messages disabled.")
    _save_config()
    _rebuild_control_gump()

def _update_control_gump():
    # Refresh the gump button label to reflect current run state.
    if not CONTROL_BUTTON:
        return
    CONTROL_BUTTON.Text = "Pause" if RUNNING else "Start"

def _stop_running_with_message():
    # Stop the run loop without closing the gump.
    global RUNNING, NEEDS_TOOL_CHECK, NEEDS_INITIAL_RECALL
    RUNNING = False
    NEEDS_TOOL_CHECK = False
    NEEDS_INITIAL_RECALL = False
    _update_control_gump()

def _rebuild_control_gump():
    # Rebuild the gump to reflect updated settings.
    global CONTROL_GUMP, CONTROL_BUTTON, CONTROL_CONTROLS
    if CONTROL_GUMP:
        CONTROL_GUMP.Dispose()
        CONTROL_GUMP = None
    CONTROL_BUTTON = None
    CONTROL_CONTROLS = []
    _create_control_gump()

def _pause_if_needed():
    # Block execution while paused, still processing gump callbacks.
    while not RUNNING:
        API.ProcessCallbacks()
        API.Pause(0.1)

def _sleep(seconds):
    # Pause in small steps so the pause button is responsive.
    elapsed = 0.0
    step = 0.1
    while elapsed < seconds:
        _pause_if_needed()
        API.ProcessCallbacks()
        API.Pause(step)
        elapsed += step

def _wait_for_target(seconds):
    # Wait for a target cursor while respecting pause state.
    elapsed = 0.0
    step = 0.1
    while elapsed < seconds:
        _pause_if_needed()
        if API.HasTarget():
            return True
        API.Pause(step)
        elapsed += step
    return False

def _debug(msg):
    if not DEBUG_TARGETING:
        return
    API.SysMsg(msg, HEADMSG_HUE)
    _append_log(msg)


def _append_log(msg):
    global LOG_TEXT, LOG_LINES
    LOG_TEXT = (LOG_TEXT + msg + "\n")[-DEBUG_LOG_MAX_CHARS:]
    LOG_LINES = LOG_TEXT.splitlines() or ["(log empty)"]
    if LOG_GUMP:
        _update_log_gump()


def _get_log_export_dir():
    global LOG_EXPORT_BASE
    if LOG_EXPORT_BASE:
        return LOG_EXPORT_BASE
    try:
        base = os.path.dirname(__file__)
    except Exception:
        base = os.getcwd()
    LOG_EXPORT_BASE = os.path.join(base, "AutoMinerLogs")
    return LOG_EXPORT_BASE


def _load_log_config():
    global LOG_EXPORT_BASE
    raw = API.GetPersistentVar(LOG_DATA_KEY, "", API.PersistentVar.Char)
    if not raw:
        return
    try:
        try:
            data = json.loads(raw)
        except Exception:
            data = ast.literal_eval(raw)
        path = data.get("export_path", "")
        if path:
            LOG_EXPORT_BASE = path
    except Exception:
        pass


def _save_log_config():
    data = {"export_path": LOG_EXPORT_BASE or ""}
    API.SavePersistentVar(LOG_DATA_KEY, json.dumps(data), API.PersistentVar.Char)


def _export_log_to_file():
    export_dir = _get_log_export_dir()
    if LOG_PATH_TEXTBOX and LOG_PATH_TEXTBOX.Text.strip():
        export_dir = LOG_PATH_TEXTBOX.Text.strip()
        global LOG_EXPORT_BASE
        LOG_EXPORT_BASE = export_dir
        _save_log_config()
    try:
        os.makedirs(export_dir, exist_ok=True)
        filename = "AutoMinerDebug.txt"
        path = os.path.join(export_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(LOG_TEXT)
        API.SysMsg(f"Saved: {filename}")
    except Exception:
        API.SysMsg("Failed to export debug log.")


def _open_log_gump():
    _update_log_gump()


def _update_log_gump():
    global LOG_GUMP, LOG_PATH_TEXTBOX
    if LOG_GUMP:
        LOG_GUMP.Dispose()
        LOG_GUMP = None

    g = API.CreateGump(True, True, False)
    g.SetRect(350, 140, 360, 420)
    bg = API.CreateGumpColorBox(0.7, "#1B1B1B")
    bg.SetRect(0, 0, 360, 420)
    g.Add(bg)

    title = API.CreateGumpTTFLabel("AutoMiner Debug Log", 14, "#FFFFFF", "alagard", "center", 360)
    title.SetPos(0, 6)
    g.Add(title)

    path_label = API.CreateGumpTTFLabel("Save Path:", 12, "#FFFFFF", "alagard", "left", 120)
    path_label.SetPos(10, 32)
    g.Add(path_label)
    path_box = API.CreateGumpTextBox(LOG_EXPORT_BASE or "", 230, 18, False)
    path_box.SetPos(90, 30)
    g.Add(path_box)
    LOG_PATH_TEXTBOX = path_box

    exp = API.CreateSimpleButton("Export", 70, 20)
    exp.SetPos(275, 52)
    g.Add(exp)
    API.AddControlOnClick(exp, _export_log_to_file)

    scroll = API.CreateGumpScrollArea(10, 76, 340, 330)
    g.Add(scroll)
    y = 0
    lines = LOG_LINES or ["(log empty)"]
    for line in lines:
        label = API.CreateGumpTTFLabel(line, 12, "#FFFFFF", "alagard", "left", 330)
        label.SetRect(0, y, 330, 16)
        scroll.Add(label)
        y += 18

    API.AddGump(g)
    LOG_GUMP = g

def _reset_mine_cache_if_moved():
    # Clear cached no-ore tiles when the player moves.
    global LAST_PLAYER_POS, NO_ORE_TILE_CACHE, NON_MINEABLE_TILE_CACHE
    pos = (int(API.Player.X), int(API.Player.Y), int(API.Player.Z))
    if LAST_PLAYER_POS is None:
        LAST_PLAYER_POS = pos
        return
    if pos != LAST_PLAYER_POS:
        NO_ORE_TILE_CACHE.clear()
        NON_MINEABLE_TILE_CACHE.clear()
        LAST_PLAYER_POS = pos

def _reset_mine_cache():
    # Force-clear cached no-ore tiles.
    global LAST_PLAYER_POS, NO_ORE_TILE_CACHE, NON_MINEABLE_TILE_CACHE, LAST_MINE_PASS_POS, MINE_CENTER
    NO_ORE_TILE_CACHE.clear()
    NON_MINEABLE_TILE_CACHE.clear()
    LAST_PLAYER_POS = (int(API.Player.X), int(API.Player.Y), int(API.Player.Z))
    LAST_MINE_PASS_POS = None
    MINE_CENTER = None

def _create_control_gump():
    # Build the in-game gump for enabling/disabling the script.
    global CONTROL_GUMP, CONTROL_BUTTON, CONTROL_CONTROLS
    if CONTROL_GUMP:
        return
    g = API.CreateGump(True, True, False)
    g.SetRect(100, 100, 320, 270)
    bg = API.CreateGumpColorBox(0.7, "#1B1B1B")
    bg.SetRect(0, 0, 320, 270)
    g.Add(bg)

    label = API.CreateGumpTTFLabel("Mining Bot Controller", 16, "#FFFFFF", "alagard", "center", 320)
    label.SetPos(0, 6)
    g.Add(label)

    shard_label = API.CreateGumpTTFLabel(
        f"Shard: {'UOAlive' if USE_UOALIVE_SHARD else 'OSI'}", 12, "#FFFFFF", "alagard", "left", 160
    )
    shard_label.SetPos(10, 60)
    g.Add(shard_label)
    shard_osi = API.CreateSimpleButton("OSI", 50, 18)
    shard_osi.SetPos(190, 58)
    g.Add(shard_osi)
    API.AddControlOnClick(shard_osi, _set_shard_osi)
    CONTROL_CONTROLS.append(shard_osi)
    shard_uoalive = API.CreateSimpleButton("UOAlive", 50, 18)
    shard_uoalive.SetPos(245, 58)
    g.Add(shard_uoalive)
    API.AddControlOnClick(shard_uoalive, _set_shard_uoalive)
    CONTROL_CONTROLS.append(shard_uoalive)

    beetle_cb = API.CreateGumpCheckbox("Use Fire Beetle", 996, USE_FIRE_BEETLE_SMELT)
    beetle_cb.SetPos(20, 82)
    g.Add(beetle_cb)
    API.AddControlOnClick(beetle_cb, _toggle_fire_beetle)
    CONTROL_CONTROLS.append(beetle_cb)

    tooling_cb = API.CreateGumpCheckbox("Auto Tooling", 996, USE_TOOL_CRAFTING)
    tooling_cb.SetPos(20, 102)
    g.Add(tooling_cb)
    API.AddControlOnClick(tooling_cb, _toggle_tool_crafting)
    CONTROL_CONTROLS.append(tooling_cb)

    travel_mode = "Chiv" if USE_SACRED_JOURNEY else "Mage"
    travel_label = API.CreateGumpTTFLabel(f"Travel: {travel_mode}", 12, "#FFFFFF", "alagard", "left", 160)
    travel_label.SetPos(10, 140)
    g.Add(travel_label)
    chiv_btn = API.CreateSimpleButton("Chiv", 50, 18)
    chiv_btn.SetPos(190, 138)
    g.Add(chiv_btn)
    API.AddControlOnClick(chiv_btn, _set_travel_chiv)
    CONTROL_CONTROLS.append(chiv_btn)
    mage_btn = API.CreateSimpleButton("Mage", 50, 18)
    mage_btn.SetPos(245, 138)
    g.Add(mage_btn)
    API.AddControlOnClick(mage_btn, _set_travel_mage)
    CONTROL_CONTROLS.append(mage_btn)

    runebook_status = "Set" if RUNBOOK_SERIAL else "Unset"
    runebook_label = API.CreateGumpTTFLabel(f"Runebook: {runebook_status}", 12, "#FFFFFF", "alagard", "left", 160)
    runebook_label.SetPos(10, 164)
    g.Add(runebook_label)
    runebook_btn = API.CreateSimpleButton("Set", 50, 18)
    runebook_btn.SetPos(190, 162)
    g.Add(runebook_btn)
    API.AddControlOnClick(runebook_btn, _set_runebook)
    CONTROL_CONTROLS.append(runebook_btn)
    runebook_unset = API.CreateSimpleButton("Unset", 50, 18)
    runebook_unset.SetPos(245, 162)
    g.Add(runebook_unset)
    API.AddControlOnClick(runebook_unset, _unset_runebook)
    CONTROL_CONTROLS.append(runebook_unset)

    secure_status = "Set" if SECURE_CONTAINER_SERIAL else "Unset"
    secure_label = API.CreateGumpTTFLabel(f"Drop Container: {secure_status}", 12, "#FFFFFF", "alagard", "left", 160)
    secure_label.SetPos(10, 190)
    g.Add(secure_label)
    secure_btn = API.CreateSimpleButton("Set", 50, 18)
    secure_btn.SetPos(190, 188)
    g.Add(secure_btn)
    API.AddControlOnClick(secure_btn, _set_secure_container)
    CONTROL_CONTROLS.append(secure_btn)
    secure_unset = API.CreateSimpleButton("Unset", 50, 18)
    secure_unset.SetPos(245, 188)
    g.Add(secure_unset)
    API.AddControlOnClick(secure_unset, _unset_secure_container)
    CONTROL_CONTROLS.append(secure_unset)

    debug_status = "On" if DEBUG_TARGETING else "Off"
    debug_label = API.CreateGumpTTFLabel(f"Debug: {debug_status}", 12, "#FFFFFF", "alagard", "left", 160)
    debug_label.SetPos(10, 214)
    g.Add(debug_label)
    debug_on = API.CreateSimpleButton("On", 50, 18)
    debug_on.SetPos(190, 212)
    g.Add(debug_on)
    API.AddControlOnClick(debug_on, _set_debug_on)
    CONTROL_CONTROLS.append(debug_on)
    debug_off = API.CreateSimpleButton("Off", 50, 18)
    debug_off.SetPos(245, 212)
    g.Add(debug_off)
    API.AddControlOnClick(debug_off, _set_debug_off)
    CONTROL_CONTROLS.append(debug_off)

    log_btn = API.CreateSimpleButton("Log", 60, 20)
    log_btn.SetPos(80, 236)
    g.Add(log_btn)
    API.AddControlOnClick(log_btn, _open_log_gump)
    CONTROL_CONTROLS.append(log_btn)

    button = API.CreateSimpleButton("Start", 100, 20)
    button.SetPos(130, 236)
    g.Add(button)
    API.AddControlOnClick(button, _toggle_running)
    CONTROL_BUTTON = button
    CONTROL_CONTROLS.append(button)

    API.AddGump(g)
    CONTROL_GUMP = g
    _update_control_gump()

def _drop_overweight_ore():
    # Drop ore by priority until weight is under max.
    while API.Player.Weight > API.Player.WeightMax:
        _pause_if_needed()
        dropped = False
        for _ in range(len(DROP_PRIORITY)):
            item = _find_drop_item()
            if item:
                _drop_item_round_robin(item)
                _sleep(1.0)
                dropped = True
                break
        if not dropped:
            break

def _drop_item_round_robin(item):
    # Drop a single item using round-robin offsets.
    dx, dy = _next_drop_offset()
    API.QueueMoveItemOffset(item.Serial, 1, dx, dy, 0)

def _next_drop_offset():
    # Get next offset for round-robin drops.
    global DROP_OFFSET_INDEX
    if not DROP_OFFSETS:
        return (0, 1)
    dx, dy = DROP_OFFSETS[DROP_OFFSET_INDEX % len(DROP_OFFSETS)]
    DROP_OFFSET_INDEX = (DROP_OFFSET_INDEX + 1) % len(DROP_OFFSETS)
    return (dx, dy)

def _drop_ore_until_weight(target_weight):
    # Drop ore by priority until under the target weight.
    API.SysMsg("Dropping ore to reduce weight.")
    while API.Player.Weight > target_weight:
        _pause_if_needed()
        dropped = False
        for _ in range(len(DROP_PRIORITY)):
            item = _find_drop_item()
            if item:
                for attempt in range(1, 4):
                    API.ClearJournal()
                    before_amt = int(item.Amount)
                    dx, dy = _next_drop_offset()
                    API.QueueMoveItemOffset(item.Serial, 1, dx, dy, 0)
                    _sleep(1.0)
                    refreshed = API.FindItem(item.Serial)
                    if refreshed and int(refreshed.Amount) == before_amt:
                        API.MoveItemOffset(item.Serial, 1, dx, dy, 0, True)
                        _sleep(1.0)
                    if API.InJournal("You must wait to perform another action", True):
                        _sleep(1.2)
                        continue
                    break
                dropped = True
                break
        if not dropped:
            break

def _handle_overweight():
    overweight_trigger = API.Player.Weight >= (API.Player.WeightMax - 50) or API.InJournalAny(OVERWEIGHT_TEXTS, True)
    encumbered_trigger = API.InJournalAny(ENCUMBERED_TEXTS, True)
    if not overweight_trigger and not encumbered_trigger:
        return False

    if overweight_trigger:
        API.SysMsg("Overweight detected.")
        if USE_RECALL_ON_OVERWEIGHT:
            if API.Player.Weight > API.Player.WeightMax:
                API.SysMsg("Overweight: dropping ore before recall.")
                _drop_ore_until_weight(API.Player.WeightMax - 50)
        else:
            _drop_overweight_ore()

    if encumbered_trigger:
        API.SysMsg("Encumbered: dropping ore.")
        _drop_ore_until_weight(API.Player.WeightMax - 50)

    if USE_RECALL_ON_OVERWEIGHT and API.Player.Weight >= (API.Player.WeightMax - 50):
        if USE_FIRE_BEETLE_SMELT:
            API.SysMsg("Overweight: smelting ore.")
            _smelt_ore()
        if API.Player.Weight >= (API.Player.WeightMax - 50):
            API.SysMsg("Overweight: recall to unload.")
            if _recall_home_and_unload():
                _advance_mining_spot()
                _sleep(1.0)
                _recall_mining_spot()
    return True

def _find_static_forge():
    # Scan nearby statics for a forge graphic and return the closest match.
    x = int(API.Player.X)
    y = int(API.Player.Y)
    statics = API.GetStaticsInArea(x - FORGE_RANGE, y - FORGE_RANGE, x + FORGE_RANGE, y + FORGE_RANGE) or []
    # Some shards report statics inconsistently; fallback to per-tile scan.
    if not statics:
        for tx in range(x - FORGE_RANGE, x + FORGE_RANGE + 1):
            for ty in range(y - FORGE_RANGE, y + FORGE_RANGE + 1):
                tile_statics = API.GetStaticsAt(tx, ty)
                if tile_statics:
                    statics.extend(tile_statics)
    if not statics:
        return None
    if DEBUG_STATICS:
        shown = 0
        for s in statics:
            API.SysMsg(f"Static: 0x{int(s.Graphic):04X} at {int(s.X)},{int(s.Y)} z{int(s.Z)}")
            shown += 1
            if shown >= DEBUG_STATICS_LIMIT:
                break
    best = None
    best_dist = 999999
    for s in statics:
        if s.Graphic not in FORGE_GRAPHICS:
            continue
        dx = int(s.X) - x
        dy = int(s.Y) - y
        dist = (dx * dx) + (dy * dy)
        if dist < best_dist:
            best = s
            best_dist = dist
    return best

def _find_item_forge():
    # Scan nearby ground items for a forge graphic.
    items = API.GetItemsOnGround(FORGE_RANGE)
    if not items:
        return None
    for item in items:
        if item.Graphic in FORGE_GRAPHICS:
            return item
    return None

def _find_forge():
    # Find the nearest forge (static or item).
    # Prefer static forge; fallback to item forge.
    static_forge = _find_static_forge()
    if static_forge:
        return ("static", static_forge)
    item_forge = _find_item_forge()
    if item_forge:
        return ("item", item_forge)
    return (None, None)

def _find_fire_beetle():
    # Find a nearby fire beetle for smelting.
    # Find a nearby fire beetle to use as a portable forge.
    mobs = API.GetAllMobiles(graphic=FIRE_BEETLE_GRAPHIC, distance=FORGE_RANGE) or []
    if not mobs:
        return None
    return mobs[0]

def _smelt_ore():
    # Smelt all eligible ore in the backpack at the nearest forge.
    if DEBUG_SMELT:
        API.SysMsg("Smelt: starting...")
    beetle = _find_fire_beetle() if USE_FIRE_BEETLE_SMELT else None
    forge_type, forge = _find_forge()
    while not forge and not beetle:
        _pause_if_needed()
        API.SysMsg("No forge nearby. Move closer...")
        _sleep(2.0)
        beetle = _find_fire_beetle() if USE_FIRE_BEETLE_SMELT else None
        forge_type, forge = _find_forge()
    # Cache a forge item serial if possible; targeting items tends to be more reliable than statics.
    forge_item = _find_item_forge()
    while True:
        _pause_if_needed()
        ore = _find_ore_in_backpack()
        if not ore:
            if DEBUG_SMELT:
                API.SysMsg("Smelt: no ore found in backpack.")
            break
        if DEBUG_SMELT:
            API.SysMsg(f"Smelt ore: 0x{int(ore.Graphic):04X} serial {int(ore.Serial)}")
        API.ClearJournal()
        API.UseObject(ore.Serial)
        _sleep(0.2)
        got_target = _wait_for_target(2)
        if not got_target:
            # Fallback: use by graphic from backpack in case serial use fails.
            try:
                API.UseType(int(ore.Graphic), 1337, API.Backpack)
            except Exception:
                pass
            got_target = _wait_for_target(2)
        if got_target:
            for _ in range(3):
                if beetle:
                    API.Target(beetle.Serial)
                elif forge_item:
                    API.Target(forge_item.Serial)
                elif forge_type == "static":
                    API.Target(int(forge.X), int(forge.Y), int(forge.Z), int(forge.Graphic))
                else:
                    API.Target(forge.Serial)
                _sleep(0.2)
                if not API.HasTarget():
                    break
            _sleep(0.8)
            if DEBUG_SMELT and API.InJournalAny(SMELT_SUCCESS_TEXTS, True):
                API.SysMsg("Smelt: success message detected.")
        else:
            if DEBUG_SMELT:
                API.SysMsg("Smelt: no target cursor received (ore -> forge).")
            # Alternate flow: use forge then target ore.
            API.ClearJournal()
            if beetle:
                API.UseObject(beetle.Serial)
            elif forge_item:
                API.UseObject(forge_item.Serial)
            elif forge_type == "static":
                API.Target(int(forge.X), int(forge.Y), int(forge.Z), int(forge.Graphic))
            else:
                API.UseObject(forge.Serial)
            _sleep(0.2)
            if _wait_for_target(2):
                for _ in range(3):
                    API.Target(ore.Serial)
                    _sleep(0.2)
                    if not API.HasTarget():
                        break
            elif DEBUG_SMELT:
                API.SysMsg("Smelt: no target cursor received (forge -> ore).")
        # Smelt cooldown to reduce spam.
        _sleep(1.2)

def _recall_home():
    # Recall to the home rune (button depends on travel mode).
    if not RUNBOOK_SERIAL:
        API.SysMsg("No runebook set.")
        return False
    for _ in range(3):
        API.ClearJournal()
        API.Pause(0.3)
        API.UseObject(RUNBOOK_SERIAL)
        if API.WaitForGump(0x59, 3):
            _sleep(1.5)
            API.ReplyGump(int(HOME_RECALL_BUTTON), 0x59)
            return True
        _sleep(0.6)
    API.SysMsg("Runebook gump not found.")
    return False

def _recall_to_button(button_id):
    # Recall using a specific runebook button id.
    if not RUNBOOK_SERIAL:
        API.SysMsg("No runebook set.")
        return False
    for _ in range(3):
        API.ClearJournal()
        API.Pause(0.3)
        API.UseObject(RUNBOOK_SERIAL)
        if API.WaitForGump(0x59, 3):
            _sleep(1.5)
            API.ReplyGump(int(button_id), 0x59)
            _reset_mine_cache()
            _sleep(2.0)
            global LAST_PLAYER_POS, MINE_CENTER
            LAST_PLAYER_POS = (int(API.Player.X), int(API.Player.Y), int(API.Player.Z))
            MINE_CENTER = None
            return True
        _sleep(0.6)
    API.SysMsg("Runebook gump not found.")
    return False

def _recall_mining_spot():
    # Recall to the current mining rune.
    if not MINING_RUNES:
        return False
    button_id = MINING_RUNES[CURRENT_MINING_INDEX]
    API.SysMsg(f"Recalling to mining rune {button_id}.")
    return _recall_to_button(button_id)

def _advance_mining_spot():
    # Advance to the next mining rune in the loop.
    global CURRENT_MINING_INDEX
    if not MINING_RUNES:
        return
    CURRENT_MINING_INDEX = (CURRENT_MINING_INDEX + 1) % len(MINING_RUNES)

def _recall_home_and_unload():
    # Recall home, unload, and restock.
    API.SysMsg("Recalling home to unload.")
    if _recall_home():
        _sleep(5.0)
        _unload_ore_and_ingots()
        return True
    return False

def _move_item_to_container(item, container_serial):
    # Move an item to a container with retry/backoff.
    for attempt in range(1, 4):
        API.ClearJournal()
        API.MoveItem(item.Serial, container_serial, int(item.Amount))
        _sleep(1.0)
        if API.InJournal("You must wait to perform another action", True):
            _sleep(1.2)
            continue
        return

def _drop_blackstone(item):
    # Move blackstone into the drop container.
    if SECURE_CONTAINER_SERIAL:
        _move_item_to_container(item, SECURE_CONTAINER_SERIAL)
        return
    API.MoveItemOffset(item.Serial, int(item.Amount), 1, 0, 0, True)
    _sleep(0.6)

def _target_mine_tile(dx, dy, tx, ty, tile):
    # Target mineable tile relative to player using the tile graphic.
    use_land = int(tile.Graphic) < 0x4000
    for _ in range(5):
        if not API.HasTarget():
            _wait_for_target(0.5)
        if DEBUG_TARGETING:
            _debug(
                f"MineTarget: rel=({dx},{dy}) graphic=0x{int(tile.Graphic):04X} land={use_land} has_target={API.HasTarget()}"
            )
        if USE_UOALIVE_SHARD:
            API.TargetTileRel(dx, dy, int(tile.Graphic))
            _sleep(0.2)
            if DEBUG_TARGETING:
                _debug(f"MineTarget: after TargetTileRel has_target={API.HasTarget()}")
            if not API.HasTarget():
                return True
            if use_land:
                if DEBUG_TARGETING:
                    _debug("MineTarget: tile rel still active; trying TargetLandRel fallback.")
                API.TargetLandRel(dx, dy)
                _sleep(0.2)
                if DEBUG_TARGETING:
                    _debug(f"MineTarget: after TargetLandRel has_target={API.HasTarget()}")
                if not API.HasTarget():
                    return True
        else:
            if use_land:
                API.TargetLandRel(dx, dy)
                _sleep(0.2)
                if DEBUG_TARGETING:
                    _debug(f"MineTarget: after TargetLandRel has_target={API.HasTarget()}")
                if not API.HasTarget():
                    return True
                if DEBUG_TARGETING:
                    _debug("MineTarget: land rel still active; trying TargetTileRel fallback.")
                API.TargetTileRel(dx, dy, int(tile.Graphic))
                _sleep(0.2)
                if DEBUG_TARGETING:
                    _debug(f"MineTarget: after TargetTileRel has_target={API.HasTarget()}")
                if not API.HasTarget():
                    return True
            else:
                API.TargetTileRel(dx, dy, int(tile.Graphic))
                _sleep(0.2)
                if DEBUG_TARGETING:
                    _debug(f"MineTarget: after TargetTileRel has_target={API.HasTarget()}")
                if not API.HasTarget():
                    return True
    if API.HasTarget():
        API.CancelTarget()
        return False
    return True

def _unload_ore_and_ingots():
    # Unload ores/ingots/gems/blackrock to the drop container.
    if not SECURE_CONTAINER_SERIAL:
        API.SysMsg("No drop container set.")
        return
    API.SysMsg("Unloading resources to containers.")
    items = API.ItemsInContainer(API.Backpack, True) or []
    API.SysMsg(f"Unload: {len(items)} items in backpack.")
    for item in items:
        if item.Graphic in BLACKSTONE_GRAPHICS:
            API.SysMsg(f"Unload: moving blackstone 0x{int(item.Graphic):04X}.")
            _drop_blackstone(item)
            continue
        if SECURE_CONTAINER_SERIAL and (item.Graphic in ORE_GRAPHICS or item.Graphic == ORE_GRAPHIC_MIN2 or item.Graphic in INGOT_GRAPHICS or item.Graphic in GEM_GRAPHICS):
            _move_item_to_container(item, SECURE_CONTAINER_SERIAL)
    _restock_ingots_from_container(22)
    _ensure_min_shovels_on_dropoff()

def _restock_ingots_from_container(target_amount):
    # Restock hue-0 ingots from the drop container.
    if not SECURE_CONTAINER_SERIAL:
        return
    API.UseObject(SECURE_CONTAINER_SERIAL)
    _sleep(0.5)
    current = _count_ingots_in_backpack()
    if current >= target_amount:
        return
    API.SysMsg("Restocking ingots from drop container.")
    need = target_amount - current
    items = API.ItemsInContainer(SECURE_CONTAINER_SERIAL, True) or []
    for item in items:
        if item.Graphic not in INGOT_GRAPHICS:
            continue
        if int(item.Hue) != 0:
            continue
        take = min(need, int(item.Amount))
        if take <= 0:
            continue
        for attempt in range(1, 4):
            API.ClearJournal()
            API.MoveItem(item.Serial, API.Backpack, int(take))
            _sleep(1.0)
            if API.InJournal("You must wait to perform another action", True):
                _sleep(1.2)
                continue
            break
        need -= take
        if need <= 0:
            break

def _ensure_min_shovels_on_dropoff():
    # Ensure at least two shovels after dropoff.
    if not SECURE_CONTAINER_SERIAL:
        return
    if not USE_TOOL_CRAFTING:
        return
    API.SysMsg("Ensuring at least two shovels.")
    if _count_tinker_tools_in_backpack() == 0:
        API.SysMsg("No tinker's tool available to craft shovels.")
        return
    if _count_tinker_tools_in_backpack() == 1:
        if not _craft_tinker_tool():
            API.SysMsg("Unable to craft a new tinker's tool.")
            return
    count = _count_shovels_in_backpack()
    if count >= 2:
        return
    _restock_ingots_from_container(22)
    attempts = 0
    while _count_shovels_in_backpack() < 2:
        if _count_ingots_in_backpack() < 8:
            API.SysMsg("Not enough ingots to craft shovels.")
            break
        if _count_tinker_tools_in_backpack() == 0:
            API.SysMsg("No tinker's tool available to craft shovels.")
            break
        if _count_tinker_tools_in_backpack() == 1:
            if not _craft_tinker_tool():
                API.SysMsg("Unable to craft a new tinker's tool.")
                break
        if not _craft_shovel():
            attempts += 1
        else:
            attempts = 0
        _sleep(0.5)
        if attempts >= 3:
            API.SysMsg("Crafting shovels failed repeatedly. Stopping attempt.")
            break

def _mine_adjacent_tiles(mine_tools):
    # Attempt mining 2 tiles in each cardinal direction. If all fail with "can't mine here", move on.
    global LAST_MINE_PASS_POS, MINE_CENTER
    if not mine_tools:
        return "tool_worn"
    if _handle_overweight():
        return "overweight"
    if MINE_CENTER is None:
        MINE_CENTER = (int(API.Player.X), int(API.Player.Y), int(API.Player.Z))
        if DEBUG_TARGETING:
            _debug(f"MineTarget: set center=({MINE_CENTER[0]},{MINE_CENTER[1]},{MINE_CENTER[2]})")
    px, py, pz = MINE_CENTER
    if LAST_MINE_PASS_POS == MINE_CENTER:
        if DEBUG_TARGETING:
            _debug(f"MineTarget: already attempted 3x3 at ({px},{py},{pz}).")
        return "no_ore"
    offsets = [
        (0, 0),
        (0, -1),
        (0, 1),
        (-1, 0),
        (1, 0),
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    ]
    no_ore_count = 0
    for dx, dy in offsets:
        if _handle_overweight():
            return "overweight"
        tx = px + dx
        ty = py + dy
        if (tx, ty) in NO_ORE_TILE_CACHE or (tx, ty) in NON_MINEABLE_TILE_CACHE:
            no_ore_count += 1
            continue
        _pause_if_needed()
        API.ClearJournal()
        API.UseObject(mine_tools)
        _sleep(0.2)
        tile = None
        tile_is_mineable = False
        tile_is_land = False
        relx = 0
        rely = 0
        if _wait_for_target(5):
            curx = int(API.Player.X)
            cury = int(API.Player.Y)
            relx = tx - curx
            rely = ty - cury
            tile = API.GetTile(int(tx), int(ty))
            tile_is_mineable = tile and getattr(tile, "Graphic", None) in MINEABLE_GRAPHICS
            tile_is_land = tile and getattr(tile, "Graphic", None) is not None and int(tile.Graphic) < 0x4000
            if DEBUG_TARGETING:
                _debug(f"MineTarget: attempt target=({int(tx)},{int(ty)},{int(API.Player.Z)}) rel=({relx},{rely})")
            if tile and getattr(tile, "Graphic", None) is not None and DEBUG_TARGETING:
                _debug(f"System: MineTarget: tile graphic=0x{int(tile.Graphic):04X} in_list={tile_is_mineable}")
            if tile_is_mineable:
                if not _target_mine_tile(relx, rely, tx, ty, tile):
                    API.SysMsg("Mining target failed; canceling cursor.")
                    API.CancelTarget()
            else:
                NON_MINEABLE_TILE_CACHE.add((tx, ty))
                if API.HasTarget():
                    if DEBUG_TARGETING:
                        _debug("MineTarget: non-mineable tile; canceling target.")
                    API.CancelTarget()
        elif DEBUG_TARGETING:
            _debug("MineTarget: wait_for_target timed out.")
        _sleep(2.2)
        if DEBUG_TARGETING:
            for text in JOURNAL_LOG_TEXTS:
                if API.InJournal(text, False):
                    _append_log(f"Journal: {text}")
        if API.InJournalAny(TOOL_WORN_TEXTS, True):
            return "tool_worn"
        no_ore_hit = API.InJournalAny(NO_ORE_CACHE_TEXTS, False)
        journal_prompt = API.InJournal("Where do you wish to dig?", False)
        if journal_prompt and tile_is_mineable and not no_ore_hit:
            # Retry with alternate targeting order for stubborn tiles (UOAlive/OSI differences).
            API.ClearJournal()
            API.UseObject(mine_tools)
            _sleep(0.2)
            if _wait_for_target(3):
                if USE_UOALIVE_SHARD:
                    if tile_is_land:
                        API.TargetLandRel(relx, rely)
                    else:
                        API.TargetTileRel(relx, rely, int(tile.Graphic))
                else:
                    API.TargetTileRel(relx, rely, int(tile.Graphic))
                _sleep(0.2)
                if DEBUG_TARGETING:
                    _debug(f"MineTarget: retry alt order rel=({relx},{rely})")
            # Re-check journal after retry to capture "Target cannot be seen." and other cache texts.
            no_ore_hit = API.InJournalAny(NO_ORE_CACHE_TEXTS, False)
        if no_ore_hit:
            no_ore_count += 1
            NO_ORE_TILE_CACHE.add((tx, ty))
            if DEBUG_TARGETING:
                _debug(f"MineTarget: cached no-ore tile ({tx},{ty}).")
            API.ClearJournal()
    if no_ore_count >= len(offsets):
        LAST_MINE_PASS_POS = MINE_CENTER
        API.SysMsg("No ore here... move.")
        _sleep(3)
        return "no_ore"
    return "ok"

_create_control_gump()
_load_config()
_load_log_config()
_rebuild_control_gump()

MineTools = API.FindType(PICKAXE_GRAPHIC, API.Backpack) or API.FindType(SHOVEL_GRAPHICS[0], API.Backpack) or API.FindType(SHOVEL_GRAPHICS[1], API.Backpack)
if not MineTools:
    API.SysMsg("You are out of mining equipment.")
    _stop_running_with_message()

API.SysMsg("AutoMiner loaded. Press Start on the gump to begin.")
_pause_if_needed()
API.SysMsg("Mining started...")

while True:
    API.ProcessCallbacks()
    _pause_if_needed()
    _reset_mine_cache_if_moved()
    if NEEDS_TOOL_CHECK:
        _ensure_tooling_in_backpack()
        API.SysMsg("Tooling check complete.")
        NEEDS_TOOL_CHECK = False
        MineTools = API.FindType(PICKAXE_GRAPHIC, API.Backpack) or API.FindType(SHOVEL_GRAPHICS[0], API.Backpack) or API.FindType(SHOVEL_GRAPHICS[1], API.Backpack)
        if NEEDS_INITIAL_RECALL and RUNBOOK_SERIAL:
            API.SysMsg("Recalling to first mining spot.")
            _recall_mining_spot()
            NEEDS_INITIAL_RECALL = False

    if _handle_overweight():
        continue

    if AUTO_TARGET_MINE:
        result = _mine_adjacent_tiles(MineTools)
        if result == "tool_worn":
            MineTools = API.FindType(PICKAXE_GRAPHIC, API.Backpack) or API.FindType(SHOVEL_GRAPHICS[0], API.Backpack) or API.FindType(SHOVEL_GRAPHICS[1], API.Backpack)
            if not MineTools:
                if _recall_home_and_unload():
                    _ensure_tooling_in_backpack()
                    MineTools = API.FindType(PICKAXE_GRAPHIC, API.Backpack) or API.FindType(SHOVEL_GRAPHICS[0], API.Backpack) or API.FindType(SHOVEL_GRAPHICS[1], API.Backpack)
                    _advance_mining_spot()
                    _sleep(1.0)
                    _recall_mining_spot()
            if not MineTools:
                API.SysMsg("Out of tools.")
                _stop_running_with_message()
        elif result == "no_ore":
            if _recall_home_and_unload():
                _advance_mining_spot()
                _sleep(1.0)
                _recall_mining_spot()
        continue

    API.SysMsg("Target a new ore tile/rock.")
    API.RequestTarget()
    tile_pos = API.LastTargetPos
    if not tile_pos:
        API.SysMsg("No mining tile targeted. Stopping.")
        API.Stop()
    API.ClearJournal()
    API.UseObject(MineTools)
    if _wait_for_target(5):
        if int(API.LastTargetGraphic or 0) != 0:
            API.Target(int(tile_pos.X), int(tile_pos.Y), int(tile_pos.Z), int(API.LastTargetGraphic))
        else:
            tile = API.GetTile(int(tile_pos.X), int(tile_pos.Y))
            if tile and getattr(tile, "Graphic", None) in MINEABLE_GRAPHICS:
                API.Target(int(tile_pos.X), int(tile_pos.Y), int(getattr(tile, "Z", tile_pos.Z)), int(tile.Graphic))
            else:
                API.Target(int(tile_pos.X), int(tile_pos.Y), int(tile_pos.Z), 0)
    _sleep(2.2)
