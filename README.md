# gw2-trailblazer
Simulates inputs in Guild Wars 2 to traverse a route created with TacO markers

## Usage:
First have a TacO marker route suitable for GW2-Trailblazer and pass it as an argument.
e.g.: 
``gw2-trailblazer.exe "testroute.xml"``

To start traversing your route, press Pause while GW2 is the active window. If Pause is pressed again, the program will Pause sending inputs.
Similarly, if GW2 is not in focus, the program will pause sending inputs.
Pressing Escape will exit the program at any point.
If the player is not within the same map as the route file, the program will close.

A demo of GW2-Trailblazer in action can be found here: https://youtu.be/uLd5JCpLF-M

## Creating a route for GW2-Trailblazer:
Using TacO, place markers in the order you want your character to traverse. Currently, for interacting purposes, different marker types relate to different interaction times.

``(taco): "TacO Base Markers" - Basic pathing``

``(taco.chest): "TacO Base Markers - Chests" - Chests and Wintersday Tree``

``(resourcenode.wood): "Resource Nodes - Wood" - Wood cutting``

``(resourcenode.ore): "Resource Nodes - Ore" - Mining ``

``(resourcenode.plant): "Resource Nodes - Plant" - Foraging``

``(resourcenode.unboundmagic): "Resource Nodes - Unbound Magic" - Instant Harvest Items Leather/Fabric/Kourna Cache/Enchanted Chest``

Finally, export markers to a file. Pass the resultant xml file to GW2-trailblazer and press Pause to start trailblazing.

A video tutorial can be found here: https://youtu.be/HT_WsJlQRc8


## Compile:
``pyinstaller.exe --name gw2-trailblazer --onefile trailblazer.py``
