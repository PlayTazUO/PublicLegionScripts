import API
import re

# This script lets you see all your gear's stats in one screen, or copy it to a spreadsheet program.

# List of layer names
layer_names = [
    "OneHanded","TwoHanded","Shoes",
    "Pants","Shirt","Helmet",
    "Gloves","Ring","Talisman",
    "Necklace","Waist","Torso",
    "Bracelet","Tunic","Earrings",
    "Arms","Cloak","Robe",
    "Skirt","Legs"
]

ignore = ["Strength Requirement", "Durability", "Self Repair"]

# Dictionary to store layer items and their properties
layer_item_properties = {}

# Dictionary to store combined properties
combined_properties = {}

# Iterate through each layer
for layer in layer_names:
    # Attempt to find the item on the current layer
    item = API.FindLayer(layer)

    # Check if the item exists
    if item is not None:
        # Get the item's name and properties
        item_data = API.ItemNameAndProps(item.Serial, True)  # True to wait for props
        if item_data:
            item_name, *item_props = item_data.split('\n')  # Separate by new lines
            props_dict = {}
            for prop in item_props:
                match = re.match(r"^(.*?)(\d+(?:\.\d+)?(?:%|s)?)(?:\D+(\d+(?:\.\d+)?))?$", prop)
                if match:
                    name = match.group(1).rstrip("/cd").strip()
                    value1 = float(match.group(2).rstrip('%').rstrip('s')) if match.group(2) else None
                    value2 = float(match.group(3)) if match.group(3) else None
                    props_dict[name] = (value1, value2) if value2 else value1

                    if name in ignore:
                        continue
                    # Update combined properties
                    if name in combined_properties:
                        if isinstance(combined_properties[name], tuple):
                            combined_properties[name] = (
                                combined_properties[name][0] + (value1 or 0),
                                combined_properties[name][1] + (value2 or 0) if value2 else combined_properties[name][1]
                            )
                        else:
                            combined_properties[name] += value1 or 0
                    else:
                        combined_properties[name] = (value1, value2) if value2 else value1
                else:
                    props_dict[prop.strip()] = None

            # Add to the dictionary
            layer_item_properties[layer] = {
                "ItemName": item_name,
                "Properties": props_dict
            }

w = 550
h = 0

gump = API.CreateGump(True, True)

bg = API.CreateGumpColorBox(0.4, "#D4202020")
gump.Add(bg)

output = "Attribute,Value,Value2\n"
y = 15
for name, value in combined_properties.items():
    n = API.CreateGumpLabel(name)
    n.SetY(y)
    n.SetX(15)
    gump.Add(n)
    h = 22 + y
        
    output += f"{name},"
    if isinstance(value, tuple):
        output += f"{value[0]},{value[1]}"
        v1 = API.CreateGumpLabel(str(value[0]), 44)
        v1.SetX(165)
        v1.SetY(y)
        gump.Add(v1)
        
        v2 = API.CreateGumpLabel(str(value[1]), 54)
        v2.SetX(215)
        v2.SetY(y)
        gump.Add(v2)
        
    else:
        output += str(value) + ","
        v1 = API.CreateGumpLabel(str(value), 44)
        v1.SetX(165)
        v1.SetY(y)
        gump.Add(v1)
    output += "\n"
    y += 22


textbox = API.CreateGumpTextBox(output, 235, h - 15, True)
textbox.SetX(300)
textbox.SetY(15)
gump.Add(textbox)

bg.SetWidth(w)
bg.SetHeight(h + 15)
gump.SetWidth(w)
gump.SetHeight(h)
gump.CenterXInViewPort()
gump.CenterYInViewPort()
API.AddGump(gump)
