# This is intended to send gold to your bank via a bag of sending when you are at max weight or max gold
import API

WEIGHTLIMIT = API.Player.WeightMax
GOLDLIMIT = 27500
MINGOLD = 10000
BAG_OF_SENDING_GFX = 0x0E76


def is_bag_of_sending(item):
    if not item:
        return False

    API.ItemNameAndProps(item)

    return "sending" in item.Name.lower() and item.Hue >= 0x0400 and item.Graphic == BAG_OF_SENDING_GFX

gold = None
bos = None

while not API.StopRequested:
    if not gold or not API.FindItem(gold):
        gold = API.FindType(0x0EED, API.Backpack, minamount=MINGOLD)
    
    if not bos or not API.FindItem(bos):
        boss = API.FindTypeAll(BAG_OF_SENDING_GFX, API.Backpack)

        for bag in boss:
            if is_bag_of_sending(bag):
                bos = bag
                break

    if bos and gold and (API.Player.Weight >= WEIGHTLIMIT or API.Player.Gold >= GOLDLIMIT):
        API.HeadMsg("Executing W.E.A.K. protocol", API.Player, 86)
        API.PreTarget(gold.Serial)
        API.UseObject(bos)
        API.Pause(2)
    API.Pause(0.5)
