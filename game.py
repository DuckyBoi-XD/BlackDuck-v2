import pygame
import random
import json
import base64
import os
import codecs
import math
from pygame.locals import *
from importlib import resources

def to_binary_str(s):
    '''binary encoder'''
    return ''.join(format(ord(c), '08b') for c in s)

def from_binary_str(b):
    '''binary decoder'''
    if len(b) % 8 != 0:
        raise ValueError("Binary string length must be divisible by 8")
    if not all(c in '01' for c in b):
        raise ValueError("Binary string must only contain 0s and 1s")
    
    chars = [chr(int(b[i:i+8], 2)) for i in range(0, len(b), 8)]
    return ''.join(chars)

def encode_save(json_str):
    '''encodes using method under'''
    # Base64 encode
    b64 = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    # Reverse
    rev = b64[::-1]
    # ROT13 encode
    rot = codecs.encode(rev, 'rot_13')
    # Binary encode
    binary = to_binary_str(rot)
    return binary.encode('utf-8')

def decode_save(encoded_bytes):
    '''decodes using method under'''
    # grabs code
    binary_str = encoded_bytes.decode('utf-8')
    # Binary decode
    rot = from_binary_str(binary_str)
    # ROT13 decode
    rev = codecs.decode(rot, 'rot_13')
    # Reverse
    b64 = rev[::-1]
    # Base64 decode
    json_str = base64.b64decode(b64).decode('utf-8')
    return json_str


def get_config_dir():
    '''Return platform-appropriate config directory'''
    return os.path.expanduser("~/.config/BlackDuck-v2")

def load_game(): # access save file -JSON
    '''loading save file - returns pat game data'''
    global savefile_value
    config_dir = get_config_dir()
    save_path = os.path.join(config_dir, "BlackDuck-v2.bin")
    try:
        with open(save_path, "rb") as f:
            encoded_bytes = f.read()
            json_str = decode_save(encoded_bytes)
            data = json.loads(json_str)
            savefile_value = 1
            return (data.get("Money", 0),
                    data.get("Chips", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                    )# 1, 5, 10, 25, 100, 500, 1.000, 5.000, 10.000, 25.000, 100.000
                    
    except FileNotFoundError:
        savefile_value = 2
        return 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    except (ValueError, json.JSONDecodeError) as error:
        print(f"Corrupted save file - using defaults. Error: {error}")
        savefile_value = 3  
        return 0, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

def save_game(money_value = None, chip_info = None):
    '''saving game data'''
    if money_value is None:
        money_value = MONEY
    if chip_info is None:
        chip_info = CHIPS

    data = {
        "Money": money_value,
        "Chips": chip_info
    }
    json_str = json.dumps(data)
    encoded_bytes = encode_save(json_str)
    config_dir = get_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    save_path = os.path.join(config_dir, "BlackDuck-v2.bin")
    with open(save_path, "wb") as f:
        f.write(encoded_bytes)

MONEY, CHIPS = load_game()
CHIPS = [3, 1, 3, 1, 1, 1, 1, 1, 1, 1]
debug_var = True

def cosd(x):
    return math.cos(math.radians(x))
def sind(x):
    return math.sin(math.radians(x))

class game_variable: # Game variables
    def __init__(self):
        pygame.init()
        self.displayWidth, self.displayHeight = 1200, 700
        self.display = pygame.display.set_mode((self.displayWidth, self.displayHeight), pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.table_colour = (20, 86, 62)
        self.table_colour_accent = (37, 64, 64)

        self.white_colour = (255, 255, 255)
        self.red_colour = (159, 27, 39)
        self.blue_colour = (21, 38, 110)
        self.green_colour = (27, 120, 75)
        self.black_colour = (9, 14, 18)
        self.bright_purple_colour = (127, 101, 227)
        self.yellow_colour = (241, 208, 93)
        self.orange_colour = (255, 176, 60)
        self.dark_blue = (42, 52, 161)
        self.light_blue = (110, 177, 255)
        self.bright_green = (109, 255, 108)
        self.yellow_green = (183, 255, 0)

        self._running = True

        self.chipRadius = 50
        self.chipPos = [600, 350]
        self.chipCurrentPos = [600, 350]
        self.chipArcAngles = (270, 330, 30, 90, 150, 210)
        self.chipValues = ("1", "5", "10", "25", "100", "500", "1000", "5000", "25000", "100000")
        self.chipValuePositions = ("chipPositions1", "chipPositions5", "chipPositions10", "chipPositions25", "chipPositions100", "chipPositions500",
                                   "chipPositions1000", "chipPositions5000", "chipPositions25000", "chipPositions100000")
        chipPositions1 = []
        chipPositions5 = []
        chipPositions10 = []
        chipPositions25 = []
        chipPositions100 = []
        chipPositions500 = []
        chipPositions1000 = []
        chipPositions5000 = []
        chipPositions25000 = []
        chipPositions100000 = []

        self.chipPositions = (chipPositions1, chipPositions5, chipPositions10, chipPositions25, chipPositions100, chipPositions500,
                            chipPositions1000, chipPositions5000, chipPositions25000, chipPositions100000)
        self.chipValueColours = (self.white_colour, self.red_colour, self.blue_colour, self.green_colour, self.black_colour, 
                                 self.bright_purple_colour, self.yellow_colour, self.orange_colour, self.dark_blue, self.light_blue)
        self.chipDisplayPriority = []

        self.mouseStartPos = None
        self.mousePosChange = False

        self.threeCharFont = pygame.font.Font("assets/fonts/chiptext.ttf", 50)
        self.fourCharFont = pygame.font.Font("assets/fonts/chiptext.ttf", 40)
        self.fiveCharFont = pygame.font.Font("assets/fonts/chiptext.ttf", 30)
        self.sixCharFont = pygame.font.Font("assets/fonts/chiptext.ttf", 28)

        self.tableFont = pygame.font.Font("assets/fonts/tableFont.ttf", 40)

        self.chipFontList = (self.threeCharFont, self.fourCharFont, self.fiveCharFont, self.sixCharFont)

        self.chipBettingGame = []
        self.chipExchange = []

        self.chipExchangeOn = False
        self.chipExchangeList = []

        self.chipStartPositions = {}
        for index, i in enumerate(self.chipValues): # Starting value of chips
            startingx = index * 100 + (index+1)*(200/11) + 50
            self.chipStartPositions[i] = (startingx, 650)

        for index, i in enumerate(CHIPS): # Start of game setup
            if i != 0:
                offset = 5
                for self.chipID in range(0, i):
                    self.chipPositions[index].append([((self.chipStartPositions)[self.chipValues[index]])[0], ((self.chipStartPositions[self.chipValues[index]])[1] - offset)])
                    offset += 10
        
        for indexa, list in enumerate(self.chipPositions):
            for indexb, value in enumerate(list):
                self.chipDisplayPriority.append((indexa, indexb))

GV = game_variable()

class game_objects:
    def on_init(self):
        self.chipCirclePoints1 = []
        self.chipCirclePoints2 = []
        self.chipCirclePoints3 = []
        self.chipCirclePoints4 = []
        self.chipCirclePoints5 = []
        self.chipCirclePoints6 = []
        self.chipCirclePointsList = (self.chipCirclePoints1, self.chipCirclePoints2, self.chipCirclePoints3, 
                                     self.chipCirclePoints4, self.chipCirclePoints5, self.chipCirclePoints6)
        self.chipCirclePointsReverse = []

    def chip_object(self):
        self.chipPosLocation = None
        for index_var in GV.chipDisplayPriority:
            for listpostions in self.chipCirclePointsList:
                listpostions.clear()
            pos = (GV.chipPositions[index_var[0]])[index_var[1]]

            # Chip Accents Positions
            for b, value in enumerate(GV.chipArcAngles):
                self.chipCirclePointsReverse = []
                for delta in range (value-10, value+11, 2):
                    self.chipCirclePointsList[b].append([
                        (cosd(delta) * (GV.chipRadius)) + (pos)[0], 
                        (sind(delta) * (GV.chipRadius)) + (pos)[1]
                    ])
                    self.chipCirclePointsReverse.append([
                        (cosd(delta) * (GV.chipRadius - 7)) + (pos)[0], 
                        (sind(delta) * (GV.chipRadius - 7)) + (pos)[1]
                    ])
                self.chipCirclePointsReverse.reverse()
                for c in self.chipCirclePointsReverse:
                    self.chipCirclePointsList[b].append(c)

            # Base Cricle
            pygame.draw.circle(GV.display, GV.chipValueColours[index_var[0]], pos, GV.chipRadius) # base chip

            # Chip Accent Creation
            for i in self.chipCirclePointsList:
                
                if GV.chipValueColours[index_var[0]] == GV.white_colour:
                    pygame.draw.polygon(GV.display, GV.blue_colour, i)
                else:
                    pygame.draw.polygon(GV.display, GV.white_colour, i)

            # Font Creation
            chip = GV.chipValues[index_var[0]]
            if len(chip) <= 3: # Grabs the font depending on value
                chipFontFont = GV.chipFontList[0]
            elif len(chip) >= 4:
                chipFontFont = GV.chipFontList[len(chip) - 3]

            if GV.chipValueColours[index_var[0]] == GV.white_colour:
                chipText = chipFontFont.render(GV.chipValues[index_var[0]], True, GV.blue_colour)
            else:
                chipText = chipFontFont.render(GV.chipValues[index_var[0]], True, GV.white_colour)
            chipTextRect = chipText.get_rect(center=(pos))
            GV.display.blit(chipText, chipTextRect)

            # Chip Outline
 
            chipOutlineColour = None
            chipOutlineWidth = None
            if GV.mousePosChange and index_var == GV.chipDisplayPriority[-1]:
                if index_var in GV.chipBettingGame or index_var in GV.chipExchange:
                    chipOutlineColour = GV.yellow_green
                    chipOutlineWidth = 2
                elif GV.chipValueColours[index_var[0]] == GV.yellow_colour:
                    chipOutlineColour = GV.orange_colour
                    chipOutlineWidth = 2
                else:
                    chipOutlineColour = GV.yellow_colour
                    chipOutlineWidth = 2
            elif index_var in GV.chipBettingGame or index_var in GV.chipExchange:
                chipOutlineColour = GV.bright_green
                chipOutlineWidth = 2
            elif GV.chipValueColours[index_var[0]] == GV.black_colour or GV.chipValueColours[index_var[0]] == GV.blue_colour:
                chipOutlineColour = GV.white_colour
                chipOutlineWidth = 1
            else:
                chipOutlineColour = GV.black_colour
                chipOutlineWidth = 1
            pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-50, pos[1]-50, 100, 100), math.radians(0), math.radians(180), width=1)
            pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-50, pos[1]-50, 100, 100), math.radians(180), math.radians(0), width=1)
            pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-51, pos[1]-51, 102, 102), math.radians(0), math.radians(180), width=1)
            pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-51, pos[1]-51, 102, 102), math.radians(180), math.radians(0), width=1)
            if chipOutlineWidth == 2:
                pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-52, pos[1]-52, 104, 104), math.radians(0), math.radians(180), width=1)
                pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-52, pos[1]-52, 104, 104), math.radians(180), math.radians(0), width=1)
                
    def game_space(self):
        tBTWidth, tBTLength = GV.tableFont.size("BETTING")
        tETWidth, tETLength = GV.tableFont.size("EXCHANGE")

        if GV.chipExchangeOn:
            pass
        else:
            # Betting area
            pygame.draw.lines(GV.display, GV.white_colour, False, ((100, 0), (100, 250), (550, 250), (550, 0)), width=5)
            pygame.draw.rect(GV.display, GV.table_colour_accent, (100, 0, 450, 250))
            tableBettingText = GV.tableFont.render("BETTING", True, GV.white_colour)
            GV.display.blit(tableBettingText, ((450/2) - (tBTWidth/2) + 100, (250/2) - (tBTLength/2)))


        # Exchanging area
        pygame.draw.lines(GV.display, GV.white_colour, False, ((650, 0), (650, 250), (1100, 250), (1100, 0)), width=5)
        pygame.draw.rect(GV.display, GV.table_colour_accent, (650, 0, 450, 250))
        tableExchangeText = GV.tableFont.render("EXCHANGE", True, GV.white_colour)
        GV.display.blit(tableExchangeText, ((450/2) - (tETWidth/2) + 650, (250/2) - (tETLength/2)))


GO = game_objects()

class game_functions:
    def move_chip(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GV._running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                cursorPosx, cursorPosy = pygame.mouse.get_pos()
                for self.index_var in reversed(GV.chipDisplayPriority):
                    CursorPos_CirclePosx = cursorPosx - ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[0]
                    CursorPos_CirclePosy = cursorPosy - ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[1]

                    CursorPos_CirclePos = CursorPos_CirclePosx**2 + CursorPos_CirclePosy**2
                    if CursorPos_CirclePos <= GV.chipRadius**2:
                        pass # for some reason fixes double click glitch
                        GV.mouseStartPos = pygame.mouse.get_pos()
                        GV.mousePosChange = True
                        GV.chipCurrentPos[0] = ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[0]
                        GV.chipCurrentPos[1] = ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[1]

                        GV.chipDisplayPriority.remove(self.index_var)
                        GV.chipDisplayPriority.append(self.index_var)
                        break
                    else:
                        pass
                if GV.mousePosChange == True:
                    break
            if event.type == pygame.MOUSEBUTTONUP and GV.mousePosChange == True:
                GV.mousePosChange = False
                GV.chipCurrentPos[0] = ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[0]
                GV.chipCurrentPos[1] = ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[1]
            if GV.mousePosChange == True:
                ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[0] = pygame.mouse.get_pos()[0] - GV.mouseStartPos[0] + GV.chipCurrentPos[0]
                ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[1] = pygame.mouse.get_pos()[1] - GV.mouseStartPos[1] + GV.chipCurrentPos[1]

    def betting_area(self):
        for self.indexChipPosition in reversed(GV.chipDisplayPriority):
            chipPositionx = ((GV.chipPositions[self.indexChipPosition[0]])[self.indexChipPosition[1]])[0]
            chipPositiony = ((GV.chipPositions[self.indexChipPosition[0]])[self.indexChipPosition[1]])[1]

            if 100 <= chipPositionx <= 550 and 0 <= chipPositiony <= 250 and GV.chipExchangeOn is False:
                if self.indexChipPosition not in GV.chipBettingGame:
                    GV.chipBettingGame.append(self.indexChipPosition)

            elif 650 <= chipPositionx <= 1100 and 0 <= chipPositiony <= 250:
                if self.indexChipPosition not in GV.chipExchange:
                    GV.chipExchange.append(self.indexChipPosition)
                    GV.chipExchangeOn = True

            else:
                if self.indexChipPosition in GV.chipExchange:
                    GV.chipExchange.remove(self.indexChipPosition)

                if self.indexChipPosition in GV.chipBettingGame:
                    GV.chipBettingGame.remove(self.indexChipPosition)

            if not GV.chipExchange:
                GV.chipExchangeOn = False
    
    def chip_exchange(self):
        pass

GF = game_functions()

class pygame_function:
    def __init__(self):
        self.fps = 60
        self.FPS = pygame.time.Clock()
        self.display = None

        GV._running = True
    def on_init(self):
        pygame.init()
        
        pygame.display.set_caption("BlackDuck v2")
        GV._running = True
    def starting_game(self):
        pass
    def game_starting(self):
        pass
    def on_event(self, event):
        if event.type == pygame.QUIT:
            GV._running = False
    def on_render(self):
        GV.display.fill(GV.table_colour)
        game_objects.game_space(self)
        game_objects.on_init(self)
        game_objects.chip_object(self)
    def on_loop(self):
        pass
    def on_cleanup(self):
        pygame.quit()
    def on_execute(self):
        if self.on_init() == False:
            GV._running = False 
        while(GV._running):
            self.FPS.tick(self.fps)
            GF.move_chip()
            GF.betting_area()
            self.on_loop()
            self.on_render()
            pygame.display.flip()

def main():
    Game = pygame_function()
    Game.on_execute()

if __name__ == "__main__":
    main()
