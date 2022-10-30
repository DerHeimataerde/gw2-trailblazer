# gw2-trailblazer
Simulates inputs in Guild Wars 2 to traverse a route created with TacO markers, including environment interactions

## Usage:
NOTES: 
- Uses the pywin32 and pynput libraries. Because of this, running the program as administrator is necessary.
- Requires A and D set to Turn and not Strafe
- Is definitely against Anet TOS. Use at your own risk

First, have a TacO marker route suitable for GW2-Trailblazer and pass it as an argument or when prompted. An example file is included and a tutorial on route creation is found below.

e.g.: ``gw2-trailblazer.exe "testroute.xml"``


To start traversing your route, press Pause while GW2 is the active window. If Pause is pressed again, the program will Pause sending inputs.
Similarly, if GW2 is not in focus, the program will pause sending inputs.
Pressing Escape will exit the program at any point.
If the player is not within the same map as the route file, the program will close.

Two demos of GW2-Trailblazer in action can be found here: 
https://youtu.be/_8mUnIb4SJg
https://youtu.be/uLd5JCpLF-M

Extra Features:
- Will attempt to jump over an obstacle if player gets stuck after 5 attempts to navigate to a marker. After 10 attempts, player will backtrack to previous marker.
- Adjusts movement calculations depending on your average speed, determining which speed multiplier to use in calculation.
- If XML file is called "test.XML", there will be no interactions, allowing player to traverse the route without pause. Useful for pathing testing.
- Logs to console with info on current route and pathing.

## Creating a route for GW2-Trailblazer:
Using TacO, place markers in the order you want your character to traverse. Currently, for interacting purposes, different marker types relate to different interaction times. You can set your TacO marker placement keybind in TacO under: GW2 Taco Settings > Rebind Keys > Add New Marker (Default Category 1). You can also change what Type of marker Default Category 1 is within the Marker Editor. Simply enable the Marker Editor in TacO, and click on the "1" icon in the bottom right and select one of the following:

NOTE: If marker types are NOT VISIBLE, enable visibility by clicking: ``Filter Displayed Tactical Markers > X Categories Hidden >`` and enable any that are unchecked.
Note: To delete all current markers on the map, go to: ``Marker Utilities > Remove My Markers From This Map``

``(taco): "TacO Base Markers" - Basic pathing``

``(taco.chest): "TacO Base Markers - Chests" - Chests and Wintersday Tree``

``(resourcenode.wood): "Resource Nodes - Wood" - Wood cutting``

``(resourcenode.ore): "Resource Nodes - Ore" - Mining ``

``(resourcenode.plant): "Resource Nodes - Plant" - Foraging``

``(resourcenode.unboundmagic): "Resource Nodes - Unbound Magic" - Instant Harvest Items Leather/Fabric/Kourna Cache/Enchanted Chest``

``(taco.jumpingpuzzle): "Jump Marker" - Will attempt to jump and move to the next marker``

``(taco.tactical.adventure.floorislava): "Glide Marker" - Will attempt to glide and move to the next marker. Still in testing phase``

Finally, export markers to a file. Pass the resultant xml file to GW2-trailblazer and press Pause to start trailblazing.
The XML file can be opened and fine-tuned depending on your needs.

A video tutorial can be found here: https://youtu.be/HT_WsJlQRc8

## Todo:
- Better Gliding
- Optional pathing precision modulation

## Problems:
 - If you receive an alert from windows defender, read this: 
https://stackoverflow.com/questions/44377666/pyinstaller-exe-throws-windows-defender-no-publisher
You can also compile/analyze the source code here if you have any doubts.
- If program is not run as administrator, it cannot detect whether GW2 is in the foreground or not and will not run
- Program will close if a proper XML route file is not provided

## Compile:
``pyinstaller.exe --name gw2-trailblazer --onefile trailblazer.py``

## Credits:
- Stack Overflow 
- https://wiki.guildwars2.com/wiki/API:MumbleLink/Example_implementation_(Python)
