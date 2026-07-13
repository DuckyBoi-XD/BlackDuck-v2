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
CHIPS = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
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
        self.dark_blue = (62, 72, 161)
        self.light_blue = (110, 177, 255)
        self.bright_green = (109, 255, 108)
        self.yellow_green = (183, 255, 0)
        self.bright_red = (255, 49, 49)
        self.highlight_yellow = (249, 203, 26)

        self.darkgreen_colour = (18, 78, 49)
        self.darkred_colour = (115, 20, 28)
        self.darkblue_colour = (13, 23, 67)
        self.darkorange_colour = (239, 142, 0)

        self._running = True

        self.chipRadius = 40
        self.smallChipRadius = 20
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

        self.threeCharFontSmall = pygame.font.Font("assets/fonts/chiptext.ttf", 16)
        self.fourCharFontSmall = pygame.font.Font("assets/fonts/chiptext.ttf", 13)
        self.fiveCharFontSmall = pygame.font.Font("assets/fonts/chiptext.ttf", 10)
        self.sixCharFontSmall = pygame.font.Font("assets/fonts/chiptext.ttf", 8)

        self.exchangeFontFull = pygame.font.Font("assets/fonts/tableFont.ttf", 30)

        self.exchangeChipAmmount = pygame.font.Font("assets/fonts/tableFont.ttf", 20)
        self.betFunctionBetFont = pygame.font.Font("assets/fonts/tableFont.ttf", 30)
        self.betFunctionStandFont = pygame.font.Font("assets/fonts/tableFont.ttf", 20)
        self.betFunctionDoubleDownFont = pygame.font.Font("assets/fonts/tableFont.ttf", 15)
        self.betFunctionSplitFont = pygame.font.Font("assets/fonts/tableFont.ttf", 25)

        self.chipFontList = (self.threeCharFont, self.fourCharFont, self.fiveCharFont, self.sixCharFont)
        self.chipFontListSmall = (self.threeCharFontSmall, self.fourCharFontSmall, self.fiveCharFontSmall, self.sixCharFontSmall)

        self.chipExchangeFunctionPosChords = []
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

        self.exchangeConfirmation = False

        self.chipBet1 = []
        self.chipBet2 = []
        self.betFuncOutline1 = False
        self.betFuncOutline2 = False
        self.betFuncOutline3 = False
        self.betFuncOutline4 = False
        self.betChipOverride = False

        self.cardDeck = {}

        self.spadesCards = (("assets/Carddeck/Spades/2.png"), ("assets/Carddeck/Spades/3.png"), ("assets/Carddeck/Spades/4.png"),
                            ("assets/Carddeck/Spades/5.png"), ("assets/Carddeck/Spades/6.png"), ("assets/Carddeck/Spades/7.png"),
                            ("assets/Carddeck/Spades/8.png"), ("assets/Carddeck/Spades/9.png"), ("assets/Carddeck/Spades/10.png"),
                            ("assets/Carddeck/Spades/J.png"), ("assets/Carddeck/Spades/Q.png"), ("assets/Carddeck/Spades/K.png"),
                            ("assets/Carddeck/Spades/A.png"))
        
        self.heartsCards = (("assets/Carddeck/Hearts/2.png"), ("assets/Carddeck/Hearts/3.png"), ("assets/Carddeck/Hearts/4.png"),
                            ("assets/Carddeck/Hearts/5.png"), ("assets/Carddeck/Hearts/6.png"), ("assets/Carddeck/Hearts/7.png"),
                            ("assets/Carddeck/Hearts/8.png"), ("assets/Carddeck/Hearts/9.png"), ("assets/Carddeck/Hearts/10.png"),
                            ("assets/Carddeck/Hearts/J.png"), ("assets/Carddeck/Hearts/Q.png"), ("assets/Carddeck/Hearts/K.png"),
                            ("assets/Carddeck/Hearts/A.png"))
        
        self.diamondsCards = (("assets/Carddeck/Diamonds/2.png"), ("assets/Carddeck/Diamonds/3.png"), ("assets/Carddeck/Diamonds/4.png"),
                            ("assets/Carddeck/Diamonds/5.png"), ("assets/Carddeck/Diamonds/6.png"), ("assets/Carddeck/Diamonds/7.png"),
                            ("assets/Carddeck/Diamonds/8.png"), ("assets/Carddeck/Diamonds/9.png"), ("assets/Carddeck/Diamonds/10.png"),
                            ("assets/Carddeck/Diamonds/J.png"), ("assets/Carddeck/Diamonds/Q.png"), ("assets/Carddeck/Diamonds/K.png"),
                            ("assets/Carddeck/Diamonds/A.png"))
        
        self.clubsCards = (("assets/Carddeck/Clubs/2.png"), ("assets/Carddeck/Clubs/3.png"), ("assets/Carddeck/Clubs/4.png"),
                            ("assets/Carddeck/Clubs/5.png"), ("assets/Carddeck/Clubs/6.png"), ("assets/Carddeck/Clubs/7.png"),
                            ("assets/Carddeck/Clubs/8.png"), ("assets/Carddeck/Clubs/9.png"), ("assets/Carddeck/Clubs/10.png"),
                            ("assets/Carddeck/Clubs/J.png"), ("assets/Carddeck/Clubs/Q.png"), ("assets/Carddeck/Clubs/K.png"),
                            ("assets/Carddeck/Clubs/A.png"))
        
        self.CardFiles = (self.spadesCards, self.heartsCards, self.diamondsCards, self.clubsCards)
        
        self.CardSuits = ("Spades0", "Hearts1", "Diamonds2", "Clubs3")
        for suit in self.CardSuits:
            for value in range(2, 11):
                self.cardDeck[f"{suit[-1]}{value}"] = value
            self.cardDeck[f"{suit[-1]}J"] =  self.cardDeck[f"{suit[-1]}Q"] =  self.cardDeck[f"{suit[-1]}K"] = 10
            self.cardDeck[f"{suit[-1]}A"] = 11 

        self.gameCHIPS1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.gameCHIPS2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.gameChipPos1 = []
        self.gameChipPos2 = []
        self.gameBet = [0, 0]
        self.bettingGame = False

        self.chipStartPositions = {}
        for index, i in enumerate(self.chipValues): # Starting value of chips
            startingx = index * 100 + (index+1)*(200/11) + 50
            self.chipStartPositions[i] = (startingx, 650)

        for index, i in enumerate(CHIPS): # Start of game setup
            if i != 0:
                self.offset = 5
                self.offsetreal = 0
                self.sideOffset = 0
                for self.chipID in range(0, i):
                    self.sideOffset = int(str(self.offset/350)[0]) * 5
                    self.offset = self.offset - int(str(self.offset/350)[0]) * 350
                    self.chipPositions[index].append([((self.chipStartPositions)[self.chipValues[index]])[0] - self.sideOffset, ((self.chipStartPositions[self.chipValues[index]])[1] - self.offset)])
                    self.offset += 10
                    self.offsetreal += 10
        
        for indexa, lista in enumerate(self.chipPositions):
            for indexb, value in enumerate(lista):
                self.chipDisplayPriority.append((indexa, indexb))

GV = game_variable()

class game_objects:
    def __init__(self):
        GV.chipExchangePosChords.append((636.8793960430015, 0))

        for delta in range(272, 296, 1):
            GV.chipExchangePosChords.append(
                ((cosd(delta) * 1200) + 595, 
                -1003 - (sind(delta) * 1200))
            )
        GV.chipExchangePosChords.append((1102.1419140888395, 0))

        GV.chipExchangeFunctionPosChords.append((87.85808591116103, 0))

        for delta in range(245, 269, 1):
            GV.chipExchangeFunctionPosChords.append(
                ((cosd(delta) * 1200) + 595, 
                -1003 - (sind(delta) * 1200))
            )
        GV.chipExchangeFunctionPosChords.append((553.120603956999, 0))
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
                if index_var in GV.chipBet1 or index_var in GV.chipBet2 or index_var in GV.chipExchange:
                    chipOutlineColour = GV.yellow_green
                    chipOutlineWidth = 2
                elif GV.chipValueColours[index_var[0]] == GV.yellow_colour:
                    chipOutlineColour = GV.orange_colour
                    chipOutlineWidth = 2
                else:
                    chipOutlineColour = GV.yellow_colour
                    chipOutlineWidth = 2
            elif index_var in GV.chipBet1 or index_var in GV.chipBet2 or index_var in GV.chipExchange:
                chipOutlineColour = GV.bright_green
                chipOutlineWidth = 2
            elif GV.chipValueColours[index_var[0]] == GV.black_colour or GV.chipValueColours[index_var[0]] == GV.blue_colour:
                chipOutlineColour = GV.white_colour
                chipOutlineWidth = 1
            else:
                chipOutlineColour = GV.black_colour
                chipOutlineWidth = 1

            if chipOutlineWidth == 2:
                pygame.draw.circle(GV.display, chipOutlineColour, (pos[0], pos[1]), 42, width=3)
            else:
                pygame.draw.circle(GV.display, chipOutlineColour, (pos[0], pos[1]), 42, width=2)
                
    def game_space(self):
        tETWidth, tETLength = GV.tableFont.size("EXCHANGE") 

        # Printing areas of the table
        pygame.draw.polygon(GV.display, GV.table_colour_accent, GV.chipExchangePosChords)
        pygame.draw.lines(GV.display, GV.white_colour, False, GV.chipExchangePosChords, width=5)

        pygame.draw.polygon(GV.display, GV.table_colour_accent, GV.chipExchangeFunctionPosChords)
        pygame.draw.lines(GV.display, GV.white_colour, False, GV.chipExchangeFunctionPosChords, width=5)

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
                widthSpacing = (chipIndexSelection[0] * 35) + ((100/10) * (chipIndexSelection[0] + 2)) + 97
                smallChipPos = (widthSpacing, 20)

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
                if int(GV.chipValues[chipIndexSelection[0]]) > GV.chipExchangeValue2 or int(GV.chipValues[chipIndexSelection[0]]) > GV.chipExchangeValue2-GV.chipExchangeValue1 or int(GV.chipValues[chipIndexSelection[0]]) == int(GV.chipValues[GV.chipExchange[0][0]]):
                    chipOutlineColour = GV.bright_red
                elif GV.exchangeChipPos[chipIndexSelection[0]] == GV.chipExchangeHighlight:
                    chipOutlineColour = GV.bright_green
                elif GV.chipValueColours[chipIndexSelection[0]] == GV.black_colour or GV.chipValueColours[chipIndexSelection[0]] == GV.blue_colour:
                    chipOutlineColour = GV.white_colour
                else:
                    chipOutlineColour = GV.black_colour

                # draws chip outline
                pygame.draw.circle(GV.display, chipOutlineColour, (smallChipPos[0], smallChipPos[1]), 21, width=1)   

                # Chip ammount indicator
                chipAmmountIndicator = GV.exchangeChipAmmount.render(str(GV.chipSmallExchangeListtemp[chipIndexSelection[0]]), True, GV.white_colour)
                CAIrect = chipAmmountIndicator.get_rect(center=(smallChipPos[0], 50))
                GV.display.blit(chipAmmountIndicator, CAIrect)

            # Exchange values box
            pygame.draw.rect(GV.display, GV.table_colour, (350, 65, 180, 40))
            pygame.draw.rect(GV.display, GV.white_colour, (350, 65, 180, 40), width=2)

            pygame.draw.rect(GV.display, GV.table_colour, (350, 115, 180, 40))
            pygame.draw.rect(GV.display, GV.white_colour, (350, 115, 180, 40), width=2)

            exchangeValueText = GV.exchangeFontFull.render(GV.chipExchangeStr2, True, GV.white_colour)
            exchangeValueTextRect = exchangeValueText.get_rect(center=(440, 135))
            GV.display.blit(exchangeValueText, exchangeValueTextRect)

            exchangeValueText = GV.exchangeFontFull.render(GV.chipExchangeStr1, True, GV.white_colour)
            exchangeValueTextRect = exchangeValueText.get_rect(center=(440, 85))
            GV.display.blit(exchangeValueText, exchangeValueTextRect)

            if GV.chipExchangeValue1 == GV.chipExchangeValue2:
                pygame.draw.circle(GV.display, GV.bright_green, (305, 105), 30)
            else:
                pygame.draw.circle(GV.display, GV.red_colour, (305, 105), 30)
            pygame.draw.circle(GV.display, GV.white_colour, (305, 105), 30, width=2)


        tableExchangeText = GV.tableFont.render("EXCHANGE", True, GV.white_colour)

        GV.display.blit(tableExchangeText, ((450/2) - (tETWidth/2) + 650, 20))


        # Betting outline

        # betting chip space outline
        rect_surface = pygame.Surface((152, 202), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, GV.highlight_yellow, (0, 0, 152, 202), width=2)
        betArea = pygame.transform.rotate(rect_surface, -5)
        rect = betArea.get_rect(center=(470, 425))
        GV.display.blit(betArea, rect)

        rect_surface = pygame.Surface((152, 202), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, GV.highlight_yellow, (0, 0, 152, 202), width=2)
        betArea = pygame.transform.rotate(rect_surface, 5)
        rect = betArea.get_rect(center=(725, 425))
        GV.display.blit(betArea, rect)
        #--------#

        # Bet Functions
        box_surface = pygame.Surface((76, 50.5), pygame.SRCALPHA)
        if GV.betFuncOutline1:
            pygame.draw.rect(box_surface, GV.green_colour, (0, 0, 76, 50.5))
        else:
            pygame.draw.rect(box_surface, GV.darkgreen_colour, (0, 0, 76, 50.5))
        rect = box_surface.get_rect(center=(598, 508.75))
        GV.display.blit(box_surface, rect)

        if not GV.bettingGame:
            bettext = GV.betFunctionBetFont.render("BET", True, GV.white_colour)
        else:
            bettext = GV.betFunctionBetFont.render("HIT", True, GV.white_colour)
        bettextrect = bettext.get_rect(center=(598, 508.75))
        GV.display.blit(bettext, bettextrect)

        rect_surface = pygame.Surface((76, 50.5), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, GV.highlight_yellow, (0, 0, 76, 59), width=2)
        rect = rect_surface.get_rect(center=(598, 508.75))
        GV.display.blit(rect_surface, rect)



        box_surface = pygame.Surface((76, 50.5), pygame.SRCALPHA)
        if GV.betFuncOutline2 and GV.bettingGame:
            pygame.draw.rect(box_surface, GV.red_colour, (0, 0, 76, 50.5))
        else:
            pygame.draw.rect(box_surface, GV.darkred_colour, (0, 0, 76, 50.5))
        rect = box_surface.get_rect(center=(598, 458.5))
        GV.display.blit(box_surface, rect)

        bettext = GV.betFunctionStandFont.render("STAND", True, GV.white_colour)
        bettextrect = bettext.get_rect(center=(598, 458.5))
        GV.display.blit(bettext, bettextrect)

        rect_surface = pygame.Surface((76, 50.5), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, GV.highlight_yellow, (0, 0, 76, 52), width=2)
        rect = rect_surface.get_rect(center=(598, 458.5))
        GV.display.blit(rect_surface, rect)



        box_surface = pygame.Surface((76, 50.5), pygame.SRCALPHA)
        if GV.betFuncOutline3 and GV.bettingGame:
            pygame.draw.rect(box_surface, GV.blue_colour, (0, 0, 76, 50.5))
        else:
            pygame.draw.rect(box_surface, GV.darkblue_colour, (0, 0, 76, 50.5))
        rect = box_surface.get_rect(center=(598, 407.75))
        GV.display.blit(box_surface, rect)

        bettext1 = GV.betFunctionDoubleDownFont.render(f"DOULBE", True, GV.white_colour)
        bettext2 = GV.betFunctionDoubleDownFont.render(f"DOWN", True, GV.white_colour)
        bettextrect1 = bettext1.get_rect(center=(598, 399.75))
        bettextrect2 = bettext2.get_rect(center=(598, 415.75))
        GV.display.blit(bettext1, bettextrect1)
        GV.display.blit(bettext2, bettextrect2)

        rect_surface = pygame.Surface((76, 50.5), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, GV.highlight_yellow, (0, 0, 76, 52), width=2)
        rect = rect_surface.get_rect(center=(598, 407.75))
        GV.display.blit(rect_surface, rect)

        

        box_surface = pygame.Surface((76, 51), pygame.SRCALPHA)
        if GV.betFuncOutline4 and GV.bettingGame:
            pygame.draw.rect(box_surface, GV.orange_colour, (0, 0, 76, 51))
        else:
            pygame.draw.rect(box_surface, GV.darkorange_colour, (0, 0, 76, 51))
        rect = box_surface.get_rect(center=(598, 357.25))
        GV.display.blit(box_surface, rect)

        bettext = GV.betFunctionStandFont.render("SPLIT", True, GV.white_colour)
        bettextrect = bettext.get_rect(center=(598, 357.25))
        GV.display.blit(bettext, bettextrect)


        rect_surface = pygame.Surface((76, 202), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, GV.highlight_yellow, (0, 0, 76, 202), width=2)
        rect = rect_surface.get_rect(center=(598, 433))
        GV.display.blit(rect_surface, rect)

        card = pygame.transform.smoothscale(pygame.image.load(GV.CardFiles[0][0]), (105, 140)).convert_alpha()
        rect = card.get_rect(center=(500, 250))
        GV.display.blit(card, rect)

        card = pygame.transform.smoothscale(pygame.image.load(GV.CardFiles[3][9]), (105, 140)).convert_alpha()
        rect = card.get_rect(center=(689, 250))
        GV.display.blit(card, rect)

GO = game_objects()

class game_functions:
    def move_chip(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GV._running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if int(list(reversed(GV.chipValues))[GV.exchangeChipSelection]) < GV.chipExchangeValue2 or (int(list(reversed(GV.chipValues))[GV.exchangeChipSelection]) == GV.chipExchangeValue2 and len(GV.chipExchange)!= 1):
                    if int(list(reversed(GV.chipValues))[GV.exchangeChipSelection]) <= GV.chipExchangeValue2-GV.chipExchangeValue1:
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
                        print(GV.chipBet1)
                        print(GV.chipBet2)
                        if (self.index_var in GV.chipBet1 or self.index_var in GV.chipBet2) and GV.bettingGame:
                            GV.betChipOverride = True
                        if CursorPos_CirclePos <= GV.chipRadius**2 and GV.betChipOverride is False:
                            GV.mouseStartPos = pygame.mouse.get_pos()
                            GV.mousePosChange = True
                            GV.chipCurrentPos[0] = ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[0]
                            GV.chipCurrentPos[1] = ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[1]

                            GV.chipDisplayPriority.remove(self.index_var)
                            GV.chipDisplayPriority.append(self.index_var)
                            break
                        else:
                            GV.betChipOverride = False
                    if GV.mousePosChange == True:
                        break
                    CursorPos_CirclePosx = cursorPosx - 305
                    CursorPos_CirclePosy = cursorPosy - 105

                    CursorPos_CirclePos = CursorPos_CirclePosx**2 + CursorPos_CirclePosy**2
                    if CursorPos_CirclePos <= GV.chipRadius**2 and GV.chipExchangeValue1 == GV.chipExchangeValue2:
                        GV.exchangeConfirmation = True

                        for chips in GV.chipExchange:
                            CHIPS[chips[0]] -= 1
                        GV.chipExchange.clear()

                        for index, i in enumerate(GV.chipSmallExchangeListtemp):
                            CHIPS[index] += i

                        for value in GV.chipPositions:
                            value.clear()
                        for index, i in enumerate(CHIPS):
                            GV.offset = 5
                            GV.offsetreal = 0
                            GV.sideOffset = 0
                            for GV.chipID in range(0, i):
                                GV.sideOffset = int(str(GV.offset/350)[0]) * 5
                                GV.offsetreal = GV.offset - int(str(GV.offset/350)[0]) * 350
                                GV.chipPositions[index].append([((GV.chipStartPositions)[GV.chipValues[index]])[0] - GV.sideOffset, ((GV.chipStartPositions[GV.chipValues[index]])[1] - GV.offsetreal)])
                                GV.offset += 10

                        GV.chipDisplayPriority.clear()

                        for indexa, lista in enumerate(GV.chipPositions):
                            for indexb, value in enumerate(lista):
                                GV.chipDisplayPriority.append((indexa, indexb))

                        GV.chipExchangeValue1 = 0
                        
                        GV.chipSmallExchangeListtemp = list(GV.chipSmallExchangeList)
                        GV.chipExchangeStr1 = (f"{GV.chipExchangeValue1:,}")

                    else:
                        GV.exchangeConfirmation = False

                    print(GV.bettingGame)
                    if GV.betFuncOutline1 and GV.bettingGame is False:
                        print("WOK")
                        GV.gameCHIPS1 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        GV.gameCHIPS2 = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                        GV.gameChipPos1.clear()
                        GV.gameChipPos2.clear()
                        GV.gameBet = [0, 0]
                        if len(GV.chipBet1) != 0:
                            for chip in GV.chipBet1:
                                GV.gameCHIPS1[chip[0]] += 1
                                GV.gameChipPos1.append(GV.chipPositions[chip[0]][chip[1]])
                                GV.gameBet[0] += int(GV.chipValues[chip[0]])
                                GV.bettingGame = True
                        if len(GV.chipBet2) != 0:
                            for chip in GV.chipBet2:
                                GV.gameCHIPS2[chip[0]] += 1
                                GV.gameChipPos2.append(GV.chipPositions[chip[0]][chip[1]])
                                GV.gameBet[0] += int(GV.chipValues[chip[0]])
                                GV.bettingGame = True

                        print(GV.gameCHIPS1)
                        print(GV.gameCHIPS2)
                        print(GV.gameChipPos1)
                        print(GV.gameChipPos2)
                        print(GV.gameBet)

            if event.type == pygame.MOUSEBUTTONUP and GV.mousePosChange == True:
                GV.mousePosChange = False
                GV.chipCurrentPos[0] = ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[0]
                GV.chipCurrentPos[1] = ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[1]
            if GV.mousePosChange == True:
                ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[0] = pygame.mouse.get_pos()[0] - GV.mouseStartPos[0] + GV.chipCurrentPos[0]
                ((GV.chipPositions[self.index_var[0]])[self.index_var[1]])[1] = pygame.mouse.get_pos()[1] - GV.mouseStartPos[1] + GV.chipCurrentPos[1]
            
            cursorPosx, cursorPosy = pygame.mouse.get_pos()

            betFunctionPosListy = [508.75, 458.5, 407.75, 357.25]

            for indexed, i in enumerate(betFunctionPosListy):
                minusi = i - 25.25
                plusi = i + 25.25
                GV.betFuncOutline1 = False
                GV.betFuncOutline2 = False
                GV.betFuncOutline3 = False
                GV.betFuncOutline4 = False
                if 560 <= cursorPosx <= 636 and minusi <= cursorPosy <= plusi:
                    if indexed == 0:
                        GV.betFuncOutline1 = True
                        break
                    elif indexed == 1:
                        GV.betFuncOutline2 = True
                        break
                    elif indexed == 2:
                        GV.betFuncOutline3 = True
                        break
                    elif indexed == 3:
                        GV.betFuncOutline4 = True
                        break

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

            exchange_remove = True
            bet1_remove = True
            bet2_remove = True
            for position in GV.chipExchangePosChords:
                if 636.8793960430015 <= chipPositionx <= position[0] and -100 <= chipPositiony <= position[1]:
                    exchange_remove = False
                    if self.indexChipPosition not in GV.chipExchange:
                        GV.chipExchange.append(self.indexChipPosition)
                        GV.chipExchangeOn = True
                    break

            # betting space tracking
            rectCentrex1 = chipPositionx - 470
            rectCentrey1 = chipPositiony - 425

            rectCentrex2 = chipPositionx - 725
            rectCentrey2 = chipPositiony - 425

            rectRotatedx1 = rectCentrex1 * cosd(-5) - rectCentrey1 * sind(-5)
            rectRotatedy1 = rectCentrex1 * sind(-5) + rectCentrey1 * cosd(-5)

            rectRotatedx2 = rectCentrex2 * cosd(5) - rectCentrey2 * sind(5)
            rectRotatedy2 = rectCentrex2 * sind(5) + rectCentrey2 * cosd(5)

            if -75 <= rectRotatedx1 <= 75 and -100 <= rectRotatedy1 <= 100:
                bet1_remove = False
                if self.indexChipPosition not in GV.chipBet1 and GV.bettingGame is False:
                    GV.chipBet1.append(self.indexChipPosition)

                
            elif -75 <= rectRotatedx2 <= 75 and -100 <= rectRotatedy2 <= 100:
                bet2_remove = False
                if self.indexChipPosition not in GV.chipBet2 and GV.bettingGame is False:
                    GV.chipBet2.append(self.indexChipPosition)


            if exchange_remove:
                if self.indexChipPosition in GV.chipExchange: 
                    GV.chipExchange.remove(self.indexChipPosition)

                if not GV.chipExchange:
                    GV.chipExchangeOn = False
                    GV.chipExchangeValue1 = 0
                    GV.chipSmallExchangeListtemp = list(GV.chipSmallExchangeList)
                    GV.chipExchangeStr1 = None

            if bet1_remove == True:
                if self.indexChipPosition in GV.chipBet1: 
                    GV.chipBet1.remove(self.indexChipPosition)
            if bet2_remove == True:
                if self.indexChipPosition in GV.chipBet2: 
                    GV.chipBet2.remove(self.indexChipPosition)

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
