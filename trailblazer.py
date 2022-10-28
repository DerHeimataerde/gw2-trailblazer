import ctypes
import mmap
from platform import java_ver
import time
import xmltodict
import win32.win32gui
import re
import numpy as np
import sys
from pynput.keyboard import Key, Controller, Listener
import os
from os import path

class WindowMgr:
    """Encapsulates some calls to the winapi for window management"""

    def __init__ (self):
        """Constructor"""
        self._handle = None

    def find_window(self, class_name, window_name=None):
        """find a window by its class_name"""
        self._handle = win32.win32gui.FindWindow(class_name, window_name)

    def _window_enum_callback(self, hwnd, wildcard):
        """Pass to win32gui.EnumWindows() to check all the opened windows"""
        if re.match(wildcard, str(win32.win32gui.GetWindowText(hwnd))) is not None:
            self._handle = hwnd

    def find_window_wildcard(self, wildcard):
        """find a window whose title matches the wildcard regex"""
        self._handle = None
        win32.win32gui.EnumWindows(self._window_enum_callback, wildcard)

    def set_foreground(self):
        """put the window in the foreground"""
        win32.win32gui.SetForegroundWindow(self._handle)
    
    def get_foreground():
        """returns active window name"""
        return(win32.win32gui.GetWindowText(win32.win32gui.GetForegroundWindow()))

class Vector:

    def cart2pol(vector):
        """Converts coordinate vector into polar coordinate theta"""
        rho = np.sqrt(vector[0]**2 + vector[1]**2)
        phi = np.arctan2(vector[1], vector[0])
        return(phi)

    def unit_vector(vector):
        """ Returns the unit vector of the vector.  """
        return vector / np.linalg.norm(vector)

    def angle_between(v1, v2):
        """ Returns the angle in degrees between vectors 'v1' and 'v2'::
        """
        v1_2d = [v1[0],v1[1]]
        v2_2d = [v2[0],v2[1]]
        v1_angle = Vector.cart2pol(v1_2d) #np.arctan(v1_u[1]/v1_u[0])
        v2_angle = Vector.cart2pol(v2_2d) #np.arctan(v2_u[1]/v2_u[0])
        theta = (v1_angle - v2_angle)

        if (np.degrees(theta) < 0):
            angle = 360 + np.degrees(theta)
        else:
            angle = np.degrees(theta)
        return (angle)

class Link(ctypes.Structure):
    _fields_ = [
        ("uiVersion", ctypes.c_uint32),           # 4 bytes
        ("uiTick", ctypes.c_ulong),               # 4 bytes
        ("fAvatarPosition", ctypes.c_float * 3),  # 3*4 bytes
        ("fAvatarFront", ctypes.c_float * 3),     # 3*4 bytes
        ("fAvatarTop", ctypes.c_float * 3),       # 3*4 bytes
        ("name", ctypes.c_wchar * 256),           # 512 bytes
        ("fCameraPosition", ctypes.c_float * 3),  # 3*4 bytes
        ("fCameraFront", ctypes.c_float * 3),     # 3*4 bytes
        ("fCameraTop", ctypes.c_float * 3),       # 3*4 bytes
        ("identity", ctypes.c_wchar * 256),       # 512 bytes
        ("context_len", ctypes.c_uint32),         # 4 bytes
        # ("context", ctypes.c_ubyte * 256),      # 256 bytes, see below
        # ("description", ctypes.c_wchar * 2048), # 4096 bytes, always empty
    ]


class Context(ctypes.Structure):
    _fields_ = [
        ("serverAddress", ctypes.c_ubyte * 28),   # 28 bytes
        ("mapId", ctypes.c_uint32),               # 4 bytes
        ("mapType", ctypes.c_uint32),             # 4 bytes
        ("shardId", ctypes.c_uint32),             # 4 bytes
        ("instance", ctypes.c_uint32),            # 4 bytes
        ("buildId", ctypes.c_uint32),             # 4 bytes
        ("uiState", ctypes.c_uint32),             # 4 bytes
        ("compassWidth", ctypes.c_uint16),        # 2 bytes
        ("compassHeight", ctypes.c_uint16),       # 2 bytes
        ("compassRotation", ctypes.c_float),      # 4 bytes
        ("playerX", ctypes.c_float),              # 4 bytes
        ("playerY", ctypes.c_float),              # 4 bytes
        ("mapCenterX", ctypes.c_float),           # 4 bytes
        ("mapCenterY", ctypes.c_float),           # 4 bytes
        ("mapScale", ctypes.c_float),             # 4 bytes
        ("processId", ctypes.c_uint32),           # 4 bytes
        ("mountIndex", ctypes.c_uint8),           # 1 byte
    ]


class MumbleLink:
    data = Link
    context = Context
    
    def __init__(self):
        self.size_link = ctypes.sizeof(Link)
        self.size_context = ctypes.sizeof(Context)
        size_discarded = 256 - self.size_context + 4096 # empty areas of context and description
        
        # GW2 won't start sending data if memfile isn't big enough so we have to add discarded bits too
        memfile_length = self.size_link + self.size_context + size_discarded
        
        self.memfile = mmap.mmap(fileno=-1, length=memfile_length, tagname="MumbleLink")
    
    def read(self):
        self.memfile.seek(0)
        
        self.data = self.unpack(Link, self.memfile.read(self.size_link))
        self.context = self.unpack(Context, self.memfile.read(self.size_context))
    
    def close(self):
        self.memfile.close()
    
    @staticmethod
    def unpack(ctype, buf):
        cstring = ctypes.create_string_buffer(buf)
        ctype_instance = ctypes.cast(ctypes.pointer(cstring), ctypes.POINTER(ctype)).contents
        return ctype_instance

class Movement:
    filepath = ""
    interactflag = 1
    route = []
    markerPos = []
    markerVec = []
    prevPos = []
    currentPos = []
    currentVec = []
    theta = 0
    distance = 0
    moveTime = 0
    speed = 0
    speedAvg = 0
    speedMult = 1
    speedPrevList = []
    hasJumped = 0

    state = {
        "gliding":0,
        "jumping":0,
        "correctionoverride":0
    }

    ml = MumbleLink()
    k = Controller()
    w = WindowMgr()
    pause = True

    def __init__(self,file):
        with open(file) as xml_file:
            data_dict = xmltodict.parse(xml_file.read())
        self.filepath = file
        self.route = list(data_dict['OverlayData']['POIs']['POI'])
        if (path.splitext(path.basename(self.filepath))[0] == "test"):
            self.interactflag = 0

    def read(self, index):
        #populates variables with respect to next marker from route list
        self.ml.read()
        self.markerPos = [float(self.route[index]['@xpos']), float(self.route[index]['@zpos']), float(self.route[index]['@ypos'])]
        self.currentPos = [self.ml.data.fAvatarPosition[0], self.ml.data.fAvatarPosition[2], self.ml.data.fAvatarPosition[1]]
        self.currentVec = [self.ml.data.fAvatarFront[0], self.ml.data.fAvatarFront[2]]
        self.markerVec = Vector.unit_vector([(self.markerPos[0] - self.currentPos[0]), (self.markerPos[1] - self.currentPos[1])])
        self.theta = Vector.angle_between(self.currentVec, self.markerVec)
        self.distance = np.linalg.norm(np.array(self.currentPos) - np.array(self.markerPos))

        if not(self.moveTime == 0) and ((np.linalg.norm(np.array(self.currentPos) - np.array(self.prevPos))) > 5): # Calculates speed and speed multiplier
            self.speed = (np.linalg.norm(np.array(self.currentPos) - np.array(self.prevPos)))/(self.moveTime)/10
            self.speedPrevList.insert(0,self.speed)
            if (len(self.speedPrevList) == 5):
                self.speedAvg = sum(self.speedPrevList)/len(self.speedPrevList)
                self.speedPrevList.pop()
                '''
                if (np.abs((0.5357 - self.speedAvg)) < .02): # In Combat at Normal Speed
                    self.speedMult = 1.0 / .5357
                '''
                if (np.abs((0.75 - self.speedAvg)) < .02) and (np.abs((0.75 - self.speed)) < .025): # Normal Speed
                    self.speedMult = 1.0 / .75
                elif (np.abs((0.9375 - self.speedAvg)) < .02) and (np.abs((0.9375 - self.speed)) < .025): # +25% Speed Buff
                    self.speedMult = 1.0 / .9375
                else:
                    self.speedMult = 1.0 # +33% Speed Buff
            else:
                    self.speedMult = 1.0 # Default if enough speed measurements not taken
        self.prevPos = self.currentPos
    
    def rotate(self):
        #rotates player towards next marker

        if (self.theta < 180):
            key = "d"
            angle = self.theta
        else:
            key = "a"
            angle = 360 - self.theta

        rotationTime = angle/120
        self.k.press(key)
        #print("rotation time:",rotationTime)
        time.sleep(rotationTime)
        self.k.release(key)

    def move(self):
        #moves player towards next marker

        key = "w"
        self.moveTime = self.distance*self.speedMult/10

        self.k.press(key)
        time.sleep(self.moveTime)
        self.k.release(key)
    
    def glide(self, index):
        #glides player towards next marker

        key = "w"
        self.moveTime = self.distance/10

        if not(self.route[index]['@type'] == "taco.tactical.adventure.floorislava"): #prevent glider redeployment mid air 
            self.k.press(Key.space) 
        self.k.press(key)
        time.sleep(self.moveTime)
        self.k.release(key)
        self.k.release(Key.space) 

    def interact(self, index):
        #checks if marker is to be interacted with or not, then does so

        key = "f"
        interaction = self.route[index]['@type'] # Type of interaction
        interactTime = 0 # Time to wait until interaction is compelete

        if (interaction == "taco"):
            interactTime = 0
        elif (interaction == "resourcenode.ore"):
            interactTime = 6
        elif (interaction == "resourcenode.wood"):
            interactTime = 6
        elif (interaction == "resourcenode.plant"):
            interactTime = 3
        elif (interaction == "resourcenode.unboundmagic"):
            interactTime = 1
        elif (interaction == "taco.chest"):
            interactTime = 4

        if (interactTime > 0):
            if self.interactflag:
                if self.hasJumped:
                    self.hasJumped = 0
                    time.sleep(2)
                self.k.press(key)
                self.k.release(key)
                time.sleep(interactTime)

    def setstate(self, index):
        """Sets the movement state"""
        if (self.state["jumping"]): # If jumpflag was turned on, this turns it off
            self.state["jumping"] = 0 
        if (self.state["gliding"]): # If glideflag was turned on, this turns it off
            self.state["gliding"] = 0 
        if (self.route[index]['@type'] == "taco.jumpingpuzzle"): # Starts jumpflag to jump once from current marker to next one
            self.state["jumping"] = 1
        if (self.route[index]['@type'] == "taco.tactical.adventure.floorislava"): # Starts glideflag to start gliding
            self.state["gliding"] = 1
            
    def traverse(self):
        #Starts player movement routine
        print("Press PAUSE to start/pause. ESC to exit.")

        while(True):
            i = 0
            self.state["jumping"] = 0
            self.state["gliding"] = 0
            while (i < len(self.route))and(i>-1):
            #for i in range(len(self.route)):
                self.read(i)
                count = 0
                jumpflag = 0
                if (self.state["jumping"]):
                    jumpflag = 1

                while ((self.distance > 1)):
                    while (not(WindowMgr.get_foreground() == "Guild Wars 2")): # Auto pauses inputs if GW2 is not in focus
                        time.sleep(1)
                    while (self.pause): # pauses movement if pause key pressed
                        time.sleep(1)
                    if count < 1:
                        if i < 1:
                            print("Route START")
                        print("Moving to "+path.splitext(path.basename(self.filepath))[0]+"["+str(i)+"]["+self.route[i]['@type']+"]"+str(self.markerPos)+"[Speed: "+str(self.speed)+", SpeedAvg: "+str(self.speedAvg)+", SpeedMult: "+str(self.speedMult)+"]")

                    self.read(i)
                    
                    self.rotate()
                    if self.state["gliding"]:
                        if not(self.route[i]['@type'] == "taco.tactical.adventure.floorislava"): # Double verify angle only glider deployment and not during gliding
                            time.sleep(.1)
                            self.read(i)
                            self.rotate()
                        self.speedMult = 1.0
                        self.glide(i)
                    else:
                        time.sleep(.1)
                        self.read(i)
                        self.rotate() # Double verify angle

                        if ((count > 4)or jumpflag): # If character stuck on geometry, attempts to jump "over"
                            self.k.press(Key.space) 
                            self.k.release(Key.space)
                            self.speedMult = 1.0
                            jumpflag = 0    
                            self.hasJumped = 1
                        if (count > 10): # If character can't jump over geometry, backtrack to previous node
                            i-=1
                            count=0
                            print("BACKTRACKING")
                        self.move()

                    count += 1
                    self.read(i)
                    self.moveTime = 0
                    if (self.state["gliding"] and (self.route[i]['@type'] == "taco.tactical.adventure.floorislava")): 
                        # Prevents a glide loop on the same marker if marker is a "glide" marker
                        break

                self.interact(i) # Player interaction

                self.setstate(i) # movement state

                i+=1
            if not(self.route[len(self.route)-1]['@type'] == "wvw.resource"):
                break    #Loop if last marker is wvw.resource
            print("Route LOOP")
        self.k.press(Key.space) # Jump at the end to signal route end
        self.k.release(Key.space)
        print("Route END")
    
    def map(self):
        #Returns true if player is in correct map with respect to route file
        self.ml.read()

        currentMap = float(self.ml.context.mapId)
        routeMap = float(self.route[0]['@MapID'])
        if (currentMap == routeMap):
            return True
        else:
            return False

def on_press(key, movement):
        if key == Key.pause: # Key to start/pause movement
            movement.pause = not(movement.pause)
        elif key == Key.esc: # Quit program if Esc is pressed
            os._exit(1)

def main():
    #check if run as admin
    if not(ctypes.windll.shell32.IsUserAnAdmin()):
        print("Application requires running as Admin to function")
        os.system('pause')
        os._exit(1)
    #check if xml path exists
    if len(sys.argv) < 2:
        file = input('Enter XML path: ')
    else:
        file = sys.argv[1]
    if not(path.exists(file)):
        print("Path does not exist")
        os.system('pause')
        os._exit(1)

    mv = Movement(file)
    l = Listener(on_press=lambda event: on_press(event, movement=mv))
    l.start()
    
    """
    # Loop until data could be read.
    ml.read()
    while not ml.data.uiTick:
        time.sleep(1)
        ml.read()
    """
    
    # do stuff ...

    #Check if map is correct
    if not(mv.map()):
        print("Wrong map")
        os.system('pause')
        exit()

    #Set GW2 to active window
    #w.find_window_wildcard(".*Guild Wars.*")
    #w.set_foreground()

    #Begin route trailblazing
    mv.traverse()
    mv.ml.close()
    #l.join()
    os.system('pause')

if __name__ == "__main__":
    main()
