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
CHIPS = [3, 1, 3, 1, 1, 1, 1, 1, 1, 10]
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
        self.bright_red = (255, 49, 49)

        self._running = True

        self.chipRadius = 40
        self.smallChipRadius = 30
        self.chipPos = [600, 350]
        self.chipCurrentPos = [600, 350]
        self.chipArcAngles = (270, 330, 30, 90, 150, 210)
        self.chipValues = ("1", "5", "10", "25", "100", "500", "1000", "5000", "25000", "100000")
        self.chipValuePositions = ((0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0))
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

        self.threeCharFont = pygame.font.Font("assets/fonts/chiptext.ttf", 40)
        self.fourCharFont = pygame.font.Font("assets/fonts/chiptext.ttf", 30)
        self.fiveCharFont = pygame.font.Font("assets/fonts/chiptext.ttf", 25)
        self.sixCharFont = pygame.font.Font("assets/fonts/chiptext.ttf", 23)

        self.tableFont = pygame.font.Font("assets/fonts/tableFont.ttf", 40)

        self.threeCharFontSmall = pygame.font.Font("assets/fonts/chiptext.ttf", 25)
        self.fourCharFontSmall = pygame.font.Font("assets/fonts/chiptext.ttf", 20)
        self.fiveCharFontSmall = pygame.font.Font("assets/fonts/chiptext.ttf", 18)
        self.sixCharFontSmall = pygame.font.Font("assets/fonts/chiptext.ttf", 15)

        self.exchangeFontFull = pygame.font.Font("assets/fonts/tableFont.ttf", 50)
        self.exchangeFontSemi = pygame.font.Font("assets/fonts/tableFont.ttf", 30)

        self.exchangeChipAmmount = pygame.font.Font("assets/fonts/tableFont.ttf", 20)

        self.chipFontList = (self.threeCharFont, self.fourCharFont, self.fiveCharFont, self.sixCharFont)
        self.chipFontListSmall = (self.threeCharFontSmall, self.fourCharFontSmall, self.fiveCharFontSmall, self.sixCharFontSmall)

        self.chipBettingGame = []
        self.chipBettingPosChords = []

        self.chipExchange = []
        self.chipExchangePosChords = []


        self.chipExchangeOn = False
        self.chipExchangehighlightOn = False
        self.chipExchangeList = []
        self.chipExchangeValue1 = 0
        self.chipExchangeValue2 = 0
        self.chipExchangeStr1 = "0"
        self.chipExchangeStr2 = "0"
        self.chipExchangeHighlight = None
        self.exchangeChipPos = []
        self.exchangeChipSelection = 0
        self.chipSmallExchangeList = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.chipSmallExchangeListtemp = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]


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
    def __init__(self):
        GV.chipExchangePosChords.append((1102.1419140888395, 0))
        GV.chipExchangePosChords.append((636.8793960430015, 0))

        for delta in range(272, 296, 1):
            GV.chipExchangePosChords.append(
                ((cosd(delta) * 1200) + 595, 
                -1003 - (sind(delta) * 1200))
            )

        GV.chipBettingPosChords.append((553.120603956999, 0))
        GV.chipBettingPosChords.append((87.85808591116103, 0))

        for delta in range(245, 269, 1):
            GV.chipBettingPosChords.append(
                ((cosd(delta) * 1200) + 595, 
                -1003 - (sind(delta) * 1200))
            )
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

        self.chipCirclePointsSmall1 = []
        self.chipCirclePointsSmall2 = []
        self.chipCirclePointsSmall3 = []
        self.chipCirclePointsSmall4 = []
        self.chipCirclePointsSmall5 = []
        self.chipCirclePointsSmall6 = []
        self.chipCirclePointsListSmall = (self.chipCirclePoints1, self.chipCirclePoints2, self.chipCirclePoints3, 
                                     self.chipCirclePoints4, self.chipCirclePoints5, self.chipCirclePoints6)
        self.chipCirclePointsReverseSmall = []

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
            pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-40, pos[1]-40, 80, 80), math.radians(0), math.radians(180), width=1)
            pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-40, pos[1]-40, 80, 80), math.radians(180), math.radians(0), width=1)
            pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-41, pos[1]-41, 82, 82), math.radians(0), math.radians(180), width=1)
            pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-41, pos[1]-41, 82, 82), math.radians(180), math.radians(0), width=1)
            if chipOutlineWidth == 2:
                pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-42, pos[1]-42, 84, 84), math.radians(0), math.radians(180), width=1)
                pygame.draw.arc(GV.display, chipOutlineColour, (pos[0]-42, pos[1]-42, 84, 84), math.radians(180), math.radians(0), width=1)
                
    def game_space(self):
        tBTWidth, tBTLength = GV.tableFont.size("BETTING")
        tETWidth, tETLength = GV.tableFont.size("EXCHANGE") 

        if GV.chipExchangeOn:

            widthSpacing = 150/11
            GV.chipExchangeValue2 = 0
            for item in GV.chipDisplayPriority:
                if item in GV.chipExchange:
                    GV.chipExchangeValue2 += int(GV.chipValues[item[0]])
            GV.chipExchangeStr2 = (f"{GV.chipExchangeValue2:,}")

            GV.exchangeChipPos = []
            for chipIndexSelection in GV.chipValuePositions:
                for listpostions in self.chipCirclePointsListSmall:
                    listpostions.clear()

                # Circle Positions
                widthSpacing = (chipIndexSelection[0] * 25) + ((100/10) * (chipIndexSelection[0] + 2)) + 148
                smallChipPos = (widthSpacing, 125)

                GV.exchangeChipPos.append(smallChipPos)

                # Base circle
                pygame.draw.circle(GV.display, GV.chipValueColours[chipIndexSelection[0]], smallChipPos, GV.smallChipRadius)

                # Chip font
                chip = GV.chipValues[chipIndexSelection[0]]
                if len(chip) <= 3:
                    chipFontSmall = GV.chipFontListSmall[0]
                elif len(chip) >= 4:
                    chipFontSmall = GV.chipFontListSmall[len(chip) - 3]

                if GV.chipValueColours[chipIndexSelection[0]] == GV.white_colour:
                    chipText = chipFontSmall.render(GV.chipValues[chipIndexSelection[0]], True, GV.blue_colour)
                else:
                    chipText = chipFontSmall.render(GV.chipValues[chipIndexSelection[0]], True, GV.white_colour)
                chipTextRect = chipText.get_rect(center=(smallChipPos))
                GV.display.blit(chipText, chipTextRect)

                # Calculating small chip accent
                for b, value in enumerate(GV.chipArcAngles):
                    self.chipCirclePointsReverseSmall = []
                    for delta in range (value-10, value+11, 2):
                        self.chipCirclePointsListSmall[b].append([
                            (cosd(delta) * (GV.smallChipRadius)) + (smallChipPos)[0], 
                            (sind(delta) * (GV.smallChipRadius)) + (smallChipPos)[1]
                        ])
                        self.chipCirclePointsReverseSmall.append([
                            (cosd(delta) * (GV.smallChipRadius - 4)) + (smallChipPos)[0], 
                            (sind(delta) * (GV.smallChipRadius - 4)) + (smallChipPos)[1]
                        ])
                    self.chipCirclePointsReverseSmall.reverse()
                    for c in self.chipCirclePointsReverseSmall:
                        self.chipCirclePointsListSmall[b].append(c)

                # prints accent
                for i in self.chipCirclePointsList:
                    if GV.chipValueColours[chipIndexSelection[0]] == GV.white_colour:
                        pygame.draw.polygon(GV.display, GV.blue_colour, i)
                    else:
                        pygame.draw.polygon(GV.display, GV.white_colour, i)

                # sets outline colour
                if int(GV.chipValues[chipIndexSelection[0]]) >= GV.chipExchangeValue2 or int(GV.chipValues[chipIndexSelection[0]]) > GV.chipExchangeValue2-GV.chipExchangeValue1:
                    chipOutlineColour = GV.bright_red
                elif GV.exchangeChipPos[chipIndexSelection[0]] == GV.chipExchangeHighlight:
                    chipOutlineColour = GV.bright_green
                elif GV.chipValueColours[chipIndexSelection[0]] == GV.black_colour or GV.chipValueColours[chipIndexSelection[0]] == GV.blue_colour:
                    chipOutlineColour = GV.white_colour
                else:
                    chipOutlineColour = GV.black_colour

                # draws chip outline
                pygame.draw.arc(GV.display, chipOutlineColour, (smallChipPos[0]-30, smallChipPos[1]-30, 60, 60), math.radians(0), math.radians(180), width=1)
                pygame.draw.arc(GV.display, chipOutlineColour, (smallChipPos[0]-30, smallChipPos[1]-30, 60, 60), math.radians(180), math.radians(0), width=1)    
                pygame.draw.arc(GV.display, chipOutlineColour, (smallChipPos[0]-31, smallChipPos[1]-31, 62, 62), math.radians(0), math.radians(180), width=1)
                pygame.draw.arc(GV.display, chipOutlineColour, (smallChipPos[0]-31, smallChipPos[1]-31, 62, 62), math.radians(180), math.radians(0), width=1)

                # Chip ammount indicator
                chipAmmountIndicator = GV.exchangeChipAmmount.render(str(GV.chipSmallExchangeListtemp[chipIndexSelection[0]]), True, GV.white_colour)
                CAIrect = chipAmmountIndicator.get_rect(center=(smallChipPos[0], 170))
                GV.display.blit(chipAmmountIndicator, CAIrect)

            # prints table stuff
            pygame.draw.rect(GV.display, GV.table_colour, (125, 20, 180, 60))
            pygame.draw.rect(GV.display, GV.table_colour, (345, 20, 180, 60))
            pygame.draw.lines(GV.display, GV.white_colour, True, ((125, 20), (125, 80), (305, 80), (305, 20)), width=2)
            pygame.draw.lines(GV.display, GV.white_colour, True, ((345, 20), (345, 80), (525, 80), (525, 20)), width=2)



            if len(str(GV.chipExchangeValue2)) > 6:
                exchangeValueText = GV.exchangeFontSemi.render(GV.chipExchangeStr2, True, GV.white_colour)
            else:
                exchangeValueText = GV.exchangeFontFull.render(GV.chipExchangeStr2, True, GV.white_colour)
            exchangeValueTextRect = exchangeValueText.get_rect(center=(435, 50))
            GV.display.blit(exchangeValueText, exchangeValueTextRect)

            if len(str(GV.chipExchangeValue1)) > 6:
                exchangeValueText = GV.exchangeFontSemi.render(GV.chipExchangeStr1, True, GV.white_colour)
            else:
                exchangeValueText = GV.exchangeFontFull.render(GV.chipExchangeStr1, True, GV.white_colour)
            exchangeValueTextRect = exchangeValueText.get_rect(center=(215, 50))
            GV.display.blit(exchangeValueText, exchangeValueTextRect)


        else:
            # Betting area
            tableBettingText = GV.tableFont.render("BETTING", True, GV.white_colour)
            GV.display.blit(tableBettingText, ((450/2) - (tBTWidth/2) + 100, (250/2) - (tBTLength/2)))

        pygame.draw.polygon(GV.display, GV.red_colour, GV.chipExchangePosChords)
        pygame.draw.polygon(GV.display, GV.white_colour, GV.chipExchangePosChords, width=5)

        pygame.draw.polygon(GV.display, GV.red_colour, GV.chipBettingPosChords)
        pygame.draw.polygon(GV.display, GV.white_colour, GV.chipBettingPosChords, width=5)

        tableExchangeText = GV.tableFont.render("EXCHANGE", True, GV.white_colour)
        GV.display.blit(tableExchangeText, ((450/2) - (tETWidth/2) + 650, (190/2) - (tETLength/2)))
        
        # table colour inside arcs
        pygame.draw.arc(GV.display, GV.table_colour, (-605, -2100, 2400, 2400), math.radians(210), math.radians(350), width=90)
        pygame.draw.arc(GV.display, GV.table_colour, (-605, -2099, 2400, 2400), math.radians(210), math.radians(350), width=90)
        pygame.draw.arc(GV.display, GV.table_colour, (-605, -2190, 2400, 2400), math.radians(210), math.radians(350), width=10)
        pygame.draw.arc(GV.display, GV.table_colour, (-605, -2191, 2400, 2400), math.radians(210), math.radians(350), width=10)

        # top arc
        pygame.draw.arc(GV.display, GV.white_colour, (-605, -2200, 2400, 2400), math.radians(240), math.radians(310), width=2)
        pygame.draw.arc(GV.display, GV.white_colour, (-605, -2201, 2400, 2400), math.radians(240), math.radians(310), width=2)

        # bottom arc
        pygame.draw.arc(GV.display, GV.white_colour, (-605, -2100, 2400, 2400), math.radians(240), math.radians(310), width=2)
        pygame.draw.arc(GV.display, GV.white_colour, (-605, -2099, 2400, 2400), math.radians(240), math.radians(310), width=2)


GO = game_objects()

class game_functions:
    def move_chip(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GV._running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if int(list(reversed(GV.chipValues))[GV.exchangeChipSelection]) < GV.chipExchangeValue2 and int(list(reversed(GV.chipValues))[GV.exchangeChipSelection]) <= GV.chipExchangeValue2-GV.chipExchangeValue1:
                    if event.button == 1:
                        if GV.chipExchangehighlightOn:
                            GV.chipSmallExchangeListtemp.reverse()
                            GV.chipSmallExchangeListtemp[GV.exchangeChipSelection] += 1
                            GV.chipSmallExchangeListtemp.reverse()
                            GV.chipExchangeValue1 = 0

                            for indexexclist, value in enumerate(reversed(GV.chipSmallExchangeListtemp)):
                                if value > 0:
                                    GV.chipExchangeValue1 += value * int(list(reversed(GV.chipValues))[indexexclist])
                            GV.chipExchangeStr1 = (f"{GV.chipExchangeValue1:,}")

                if event.button == 3:
                    if GV.chipExchangehighlightOn:
                        GV.chipSmallExchangeListtemp.reverse()
                        print(GV.chipSmallExchangeListtemp[GV.exchangeChipSelection])
                        if GV.chipSmallExchangeListtemp[GV.exchangeChipSelection] > 0:
                            GV.chipSmallExchangeListtemp[GV.exchangeChipSelection] -= 1
                            GV.chipExchangeValue1 = 0

                            for indexexclist, value in enumerate(GV.chipSmallExchangeListtemp):
                                if value > 0:
                                    GV.chipExchangeValue1 += value * int(list(reversed(GV.chipValues))[indexexclist])
                            GV.chipExchangeStr1 = (f"{GV.chipExchangeValue1:,}")
                        GV.chipSmallExchangeListtemp.reverse()
                if event.button == 1:
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
            for indexexchange, self.smallExchangeChipPos in enumerate(reversed(GV.exchangeChipPos)):

                cursorPosx, cursorPosy = pygame.mouse.get_pos()

                CursorPos_CirclePosx = cursorPosx - self.smallExchangeChipPos[0]
                CursorPos_CirclePosy = cursorPosy - self.smallExchangeChipPos[1]

                CursorPos_CirclePos = CursorPos_CirclePosx**2 + CursorPos_CirclePosy**2
                if CursorPos_CirclePos <= GV.smallChipRadius**2:
                    GV.chipExchangeHighlight = self.smallExchangeChipPos 
                    GV.chipExchangehighlightOn = True
                    GV.exchangeChipSelection = indexexchange
                    break
                else:
                    GV.chipExchangeHighlight = None
                    GV.chipExchangehighlightOn = False

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
                GV.chipExchangeValue1 = 0
                GV.chipExchangeStr1 = None
                GV.chipSmallExchangeListtemp = list(GV.chipSmallExchangeList)


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
        game_objects.on_init(self)
        game_objects.game_space(self)
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
