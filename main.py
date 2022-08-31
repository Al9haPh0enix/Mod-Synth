import numpy as np
import pyaudio

import pygame
pygame.init()

screenWidth, screenHeight =  800, 800

w = pygame.display.set_mode([screenWidth, screenHeight])
c = pygame.time.Clock()

def lerp(a, b, k):
    return ((b-a)*k)+a

def nDimensionlerp(a, b, k):
    out = []
    
    for i in range(len(a)):
        out.append(lerp(a[i], b[i], k))
    
    return out

def cubic(points, k):
    p1 = points[0]
    p2 = points[1]
    p3 = points[2]
    p4 = points[3]

    pa = nDimensionlerp(p1, p2, k)
    pb = nDimensionlerp(p2, p3, k)
    pc = nDimensionlerp(p3, p4, k)

    pd = nDimensionlerp(pa, pb, k)
    pe = nDimensionlerp(pb, pc, k)

    return nDimensionlerp(pd, pe, k)

P = pyaudio.PyAudio()

fs = 44100
T = 3

class label:
    def __init__(self, x, y, size, text, font=None):
        self.pos = [x, y]

        self.size = size
        self.text = text

        self.font = pygame.font.Font(font, size)

        self.col1 = [50, 50, 50]
        self.col2 = [25, 25, 25]
        self.col3 = [100, 100, 100]
    
    def render(self, w):
        text = self.font.render(self.text, True, self.col3)
        rect = text.get_rect()
        rect.width += 10
        rect.height += 10
        rect.x = self.pos[0]-rect.width/2
        rect.y = self.pos[1]-rect.height/2
        pygame.draw.rect(w, self.col1, rect)
        pygame.draw.rect(w, self.col2, rect, 2)

        w.blit(text, [self.pos[0]-rect.width/2+5, self.pos[1]-rect.height/2+5])
    
    def update(self, mx, my, mouseState):
        pass

class slider:
    def __init__(self, x, y, width, height, sliderSize, numOptions):
        self.width = width
        self.height = height
        self.numOptions = numOptions
        self.pos = [x, y]
        self.sliderSize = sliderSize
        self.sliderPos = 0

        self.col1 = [50, 50, 50]
        self.col2 = [25, 25, 25]
        self.col3 = [100, 100, 100]
    
    def render(self, w):
        rect = pygame.Rect(self.pos[0]-(self.width/2), self.pos[1]-(self.height/2), self.width, self.height)
        slider = pygame.Rect(self.pos[0]+((self.sliderPos/self.numOptions)*self.width)-(self.width/2)-(self.sliderSize/2), self.pos[1]-self.sliderSize/2, self.sliderSize, self.sliderSize)

        pygame.draw.rect(w, self.col1, rect)
        pygame.draw.rect(w, self.col2, rect, 2)
        pygame.draw.ellipse(w, self.col3, slider)
    
    def update(self, mx, my, mouseState):
        pass
    
    def setPos(self, mx, my, mouseState):
        if pygame.Rect(self.pos[0]-(self.width/2), self.pos[1]-(self.height/2), self.width, self.height).collidepoint(mx, my) and mouseState[0]:
            self.sliderPos = self.numOptions-round((round((min(self.width/2, max(-self.width/2, self.pos[0]-mx))/(self.width/2))*self.numOptions)+self.numOptions)/2)

class window:
    def __init__(self, x, y, width, height, title, moveable = True):
        self.pos = [x, y]
        self.width = width
        self.height = height

        self.title = title
        self.font = pygame.font.Font(None, 16)

        self.moveable = moveable
        self.clickingLastFrame = False
        self.offset = []

        self.col1 = [50, 50, 50]
        self.col2 = [25, 25, 25]
        self.col3 = [75, 75, 75]
        self.col4 = [200, 200, 200]
    
    def getCols(self):
        return [
            self.col1,
            self.col2,
            self.col3,
            self.col4
        ]

    def get_clickingLastFrame(self):
        return self.clickingLastFrame
    
    def render(self, w):
        textSurf = self.font.render(self.title, True, self.col4)
        textRect = textSurf.get_rect()

        textRect.x = self.pos[0] - (self.width/2) + 4
        textRect.y = (self.pos[1] - (self.height/2)) + 4

        upper = pygame.Rect(self.pos[0]-self.width/2, self.pos[1]-self.height/2, self.width, 20)
        full = pygame.Rect(self.pos[0]-self.width/2, self.pos[1]-self.height/2, self.width, self.height)

        pygame.draw.rect(w, self.col3, full)
        pygame.draw.rect(w, self.col1, upper)
        pygame.draw.rect(w, self.col2, full, 2)

        w.blit(textSurf, textRect)
    
    def update(self, mx, my, mouseState):
        if self.moveable:
            upper = pygame.Rect(self.pos[0]-self.width/2, self.pos[1]-self.height/2, self.width, 20)

            if mouseState[0]:
                if upper.collidepoint(mx, my) and not self.clickingLastFrame:
                    self.clickingLastFrame = True
                    self.offset = [self.pos[0]-mx, (self.pos[1])-(my+(self.height/2)-10)]
            if not mouseState[0]:
                self.clickingLastFrame = False
                self.offset = [0, 0]
            
            if self.clickingLastFrame:
                self.pos = [mx + self.offset[0], self.offset[1]+ my+(self.height/2)-10]

class wave:
    def __init__(self, type, freq, amp):
        self.type = type
        self.freq = freq
        self.amp = amp
        self.useRaw = False
        self.raw = np.zeros(T*fs)
    
    def play(self):

        t = np.arange(0, T, 1.0/fs)
        
        if self.useRaw:
            return self.raw
        else:
            if self.type == "sin":
                if abs(self.amp) <= 1:# 1 is arbitrary to avoid clipping sound card DAC
                    return self.amp * np.sin(2*np.pi*self.freq*t)
                else:
                    return np.sin(2*np.pi*self.freq*t)
            if self.type == "square":
                val = np.sign(np.sin(2*np.pi*self.freq*t))

                if abs(self.amp) <= 1:# 1 is arbitrary to avoid clipping sound card DAC
                    return self.amp * val
                else:
                    return val
            if self.type == "tri":
                if abs(self.amp) <= 1:# 1 is arbitrary to avoid clipping sound
                    return ((2*self.amp)/np.pi) * np.arcsin(np.sin(2*np.pi*self.freq*t))
                else:
                    return (2/np.pi) * np.arcsin(np.sin(2*np.pi*self.freq*t))
        
class output(window):
    def __init__(self, deps=[]):

        width = 50
        height = 100
        x = screenWidth - (width/2)
        y = screenHeight - (height/2)

        super().__init__(x, y, width, height, "Output", False)
        self.inputNodes = 1
        self.outputNodes = 0

        self.canvas = [

        ]

        self.outputNodePoints = []
        self.inputNodePoints = []

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.filledInputs = []
        self.dependencies = deps # canvas index, output node index
        
        self.stream = P.open(rate=fs, format=pyaudio.paInt16, channels=1, output=True)
    
    def render(self, w):
        super().render(w)

        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)
    
    def play(self):
        print("outputed")
        if len(self.filledInputs) < 1:
            raise Exception("An input was not filled.")

        print(type(self.filledInputs[0]))
        x = self.filledInputs[0].play()
        x  = x*32768  # scale to int16 for sound card

        x = x.astype(np.int16)
        
        self.stream.write(x.tobytes())

class oscillator(window):
    def __init__(self, x, y, output = []):

        width = 100
        height = 50

        super().__init__(x, y, width, height, "Oscillator", True)
        self.inputNodes = 0
        self.outputNodes = 1

        self.output = output

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.canvas = [
            slider(x, y, 80, 20, 10, 80),
        ]

        self.canvas[0].sliderPos = int((440/3000)*80)

        self.filledInputs = []
        self.dependencies = [] # canvas index, output node index, input node index
    
    def render(self, w):
        super().render(w)

        for i in self.canvas:
            i.render(w)
        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
        for i in self.outputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)

        for i in self.canvas:
            i.update(mx, my, mouseState)
            if not super().get_clickingLastFrame():
                i.setPos(mx, my, mouseState)

            i.pos = [self.pos[0], self.pos[1]+9]
        
        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            i += 1
            self.outputNodePoints.append([self.pos[0]+50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
        for i in range(self.inputNodes):
            i += 1
            self.inputNodePoints.append([self.pos[0]-50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
                    
    def play(self):
        print("oscillated")

        return [wave("sin", ((self.canvas[0].sliderPos/80)*3000), .5)]

class variableOscillator(window):
    def __init__(self, x, y, deps = [], output = []):

        width = 100
        height = 50

        super().__init__(x, y, width, height, "Variable Oscillator", True)
        self.inputNodes = 2
        self.outputNodes = 1

        self.output = output

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.canvas = [
            
        ]

        self.filledInputs = []
        self.dependencies = deps # canvas index, output node index, input node index
    
    def render(self, w):
        super().render(w)

        for i in self.canvas:
            i.render(w)
        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
        for i in self.outputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)

        for i in self.canvas:
            i.update(mx, my, mouseState)
        
        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            i += 1
            self.outputNodePoints.append([self.pos[0]+50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
        for i in range(self.inputNodes):
            i += 1
            self.inputNodePoints.append([self.pos[0]-50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
                    
    def play(self):
        print("variably oscillated")

        freq = self.filledInputs[0]

        return [wave("sin", freq, self.filledInputs[1]/100)]

class curveGenerator(window):
    def __init__(self, x, y, deps = [], output = []):

        width = 100
        height = 50

        super().__init__(x, y, width, height, "Curve Generator", True)
        self.inputNodes = 0
        self.outputNodes = 1

        self.output = output

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.canvas = [
            slider(x, y, 80, 20, 10, 10),
        ]

        self.filledInputs = []
        self.dependencies = [] # canvas index, output node index, input node index
    
    def render(self, w):
        super().render(w)

        for i in self.canvas:
            i.render(w)
        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
        for i in self.outputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)

        for i in self.canvas:
            i.update(mx, my, mouseState)
            if type(i) == slider:
                if not super().get_clickingLastFrame():
                    i.setPos(mx, my, mouseState)

            i.pos = [self.pos[0], self.pos[1]+9]
        
        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            i += 1
            self.outputNodePoints.append([self.pos[0]+50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
        for i in range(self.inputNodes):
            i += 1
            self.inputNodePoints.append([self.pos[0]-50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
                    
    def play(self):
        print("curved")

        increaseFactor = self.canvas[0].sliderPos

        curve = np.power(np.arange(0, 1, 1/fs), increaseFactor)

        return [curve]

class toFrequency(window):
    def __init__(self, x, y, deps=[], output = []):

        width = 120
        height = 50

        super().__init__(x, y, width, height, "Curve to Frequency", True)
        self.inputNodes = 1
        self.outputNodes = 1

        self.output = output

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.start = 110
        self.end = 440

        self.canvas = [
            
        ]

        self.filledInputs = []
        self.dependencies = deps # canvas index, output node index, input node index
    
    def render(self, w):
        super().render(w)

        for i in self.canvas:
            i.render(w)
        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
        for i in self.outputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)

        for i in self.canvas:
            i.update(mx, my, mouseState)
        
        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            i += 1
            self.outputNodePoints.append([self.pos[0]+50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
        for i in range(self.inputNodes):
            i += 1
            self.inputNodePoints.append([self.pos[0]-50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
                     
    def play(self):
        print("frequencied")
        curve = self.filledInputs[0]
        if max(curve) == 0:
            return [np.repeat(self.start, len(curve))]
        freqRange = ((curve/max(curve)) * (self.end-self.start))+self.start
        return [freqRange]

class inverter(window):
    def __init__(self, x, y, deps=[], output = []):

        width = 120
        height = 50

        super().__init__(x, y, width, height, "Inverter", True)
        self.inputNodes = 1
        self.outputNodes = 1

        self.output = output

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.start = 110
        self.end = 440

        self.canvas = [
            
        ]

        self.filledInputs = []
        self.dependencies = deps # canvas index, output node index, input node index
    
    def render(self, w):
        super().render(w)

        for i in self.canvas:
            i.render(w)
        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
        for i in self.outputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)

        for i in self.canvas:
            i.update(mx, my, mouseState)
        
        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            i += 1
            self.outputNodePoints.append([self.pos[0]+50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
        for i in range(self.inputNodes):
            i += 1
            self.inputNodePoints.append([self.pos[0]-50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
                     
    def play(self):
        print("inverted")
        curve = self.filledInputs[0]
        return [max(curve)-curve]

class flipper(window):
    def __init__(self, x, y, deps=[], output = []):

        width = 120
        height = 50

        super().__init__(x, y, width, height, "Flipper", True)
        self.inputNodes = 1
        self.outputNodes = 1

        self.output = output

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.start = 110
        self.end = 440

        self.canvas = [
            
        ]

        self.filledInputs = []
        self.dependencies = deps # canvas index, output node index, input node index
    
    def render(self, w):
        super().render(w)

        for i in self.canvas:
            i.render(w)
        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
        for i in self.outputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)

        for i in self.canvas:
            i.update(mx, my, mouseState)
        
        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            i += 1
            self.outputNodePoints.append([self.pos[0]+50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
        for i in range(self.inputNodes):
            i += 1
            self.inputNodePoints.append([self.pos[0]-50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
                     
    def play(self):
        print("flipped")
        curve = self.filledInputs[0]
        return [np.flip(curve)]

class waveToSquare(window):
    def __init__(self, x, y, deps=[], output = []):

        width = 100
        height = 50

        super().__init__(x, y, width, height, "Sin to Square", True)
        self.inputNodes = 1
        self.outputNodes = 1

        self.output = output

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.canvas = [
            
        ]

        self.filledInputs = []
        self.dependencies = deps # canvas index, output node index, input node index
    
    def render(self, w):
        super().render(w)

        for i in self.canvas:
            i.render(w)
        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
        for i in self.outputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)

        for i in self.canvas:
            i.update(mx, my, mouseState)
        
        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            i += 1
            self.outputNodePoints.append([self.pos[0]+50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
        for i in range(self.inputNodes):
            i += 1
            self.inputNodePoints.append([self.pos[0]-50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
                     
    def play(self):
        print("squared")
        sin = self.filledInputs[0]
        return [wave("square", sin.freq, sin.amp)]

class waveToTriangle(window):
    def __init__(self, x, y, deps=[], output = []):

        width = 100
        height = 50

        super().__init__(x, y, width, height, "Sin to Triangle", True)
        self.inputNodes = 1
        self.outputNodes = 1

        self.output = output

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.canvas = [
            
        ]

        self.filledInputs = []
        self.dependencies = deps # canvas index, output node index, input node index
    
    def render(self, w):
        super().render(w)

        for i in self.canvas:
            i.render(w)
        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
        for i in self.outputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)

        for i in self.canvas:
            i.update(mx, my, mouseState)
        
        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            i += 1
            self.outputNodePoints.append([self.pos[0]+50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
        for i in range(self.inputNodes):
            i += 1
            self.inputNodePoints.append([self.pos[0]-50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
                     
    def play(self):
        print("triangled")
        sin = self.filledInputs[0]
        return [wave("tri", sin.freq, sin.amp)]

class amplifier(window):
    def __init__(self, x, y, deps=[], output = []):

        width = 100
        height = 50

        super().__init__(x, y, width, height, "Amplifier", True)
        self.inputNodes = 1
        self.outputNodes = 1

        self.output = output

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.canvas = [
            
        ]

        self.filledInputs = []
        self.dependencies = deps # canvas index, output node index, input node index
    
    def render(self, w):
        super().render(w)

        for i in self.canvas:
            i.render(w)
        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
        for i in self.outputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)

        for i in self.canvas:
            i.update(mx, my, mouseState)
        
        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            i += 1
            self.outputNodePoints.append([self.pos[0]+50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
        for i in range(self.inputNodes):
            i += 1
            self.inputNodePoints.append([self.pos[0]-50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
                     
    def play(self):
        print("Amplifier")
        val = self.filledInputs[0]

        if type(val) == wave:
            #Some kind of wave, set amp to highest possible value
            val.amp = .5
            return [val]
        elif hasattr(wave, "__len__"):
            #Curve, map to 0-1
            maximum = max(abs(val))
            curve = val/maximum
            curve += 1
            curve /= 4
            print(min(curve), max(curve))
            return [curve]

class expression(window):
    def __init__(self, x, y, output = []):

        width = 100
        height = 50

        super().__init__(x, y, width, height, "Expression", True)
        self.inputNodes = 0
        self.outputNodes = 1

        self.output = output

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.canvas = [
            slider(x, y, 80, 20, 10, 100),
        ]

        self.canvas[0].sliderPos = int((440/3000)*80)

        self.filledInputs = []
        self.dependencies = [] # canvas index, output node index, input node index
    
    def render(self, w):
        super().render(w)

        for i in self.canvas:
            i.render(w)
        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
        for i in self.outputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)

        for i in self.canvas:
            i.update(mx, my, mouseState)
            if not super().get_clickingLastFrame():
                i.setPos(mx, my, mouseState)

            i.pos = [self.pos[0], self.pos[1]+9]
        
        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            i += 1
            self.outputNodePoints.append([self.pos[0]+50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
        for i in range(self.inputNodes):
            i += 1
            self.inputNodePoints.append([self.pos[0]-50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
                    
    def play(self):
        print("expressioned")

        return [self.canvas[0].sliderPos]

class decay(window):
    def __init__(self, x, y, deps = [], output = []):

        width = 100
        height = 50

        super().__init__(x, y, width, height, "Decay", True)
        self.inputNodes = 2
        self.outputNodes = 1

        self.output = output

        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            percentDown = ((i+.5)/self.outputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.outputNodePoints.append([x+(width/2), y])
        for i in range(self.inputNodes):
            percentDown = ((i+.5)/self.inputNodes)
            y = ((y-(height/2)) + (percentDown*100))
            self.inputNodePoints.append([x-(width/2), y])

        self.canvas = [
        ]

        self.filledInputs = []
        self.dependencies = deps # canvas index, output node index, input node index
    
    def render(self, w):
        super().render(w)

        for i in self.canvas:
            i.render(w)
        for i in self.inputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
        for i in self.outputNodePoints:
            pygame.draw.circle(w, super().getCols()[0], i, 6)
    
    def update(self, mx, my, mouseState):
        super().update(mx, my, mouseState)

        for i in self.canvas:
            i.update(mx, my, mouseState)
            if not super().get_clickingLastFrame():
                i.setPos(mx, my, mouseState)

            i.pos = [self.pos[0], self.pos[1]+9]
        
        self.outputNodePoints = []
        self.inputNodePoints = []

        for i in range(self.outputNodes):
            i += 1
            self.outputNodePoints.append([self.pos[0]+50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
        for i in range(self.inputNodes):
            i += 1
            self.inputNodePoints.append([self.pos[0]-50, self.pos[1] + ((i/(self.outputNodes+1))*50) - 25])
                    
    def play(self):
        print("decayed")

        if type(self.filledInputs[0]) != wave:
            raise ValueError("Invalid type")

        oldWave = self.filledInputs[0]
        decay = (self.filledInputs[1]/500000)+1

        nWave = wave(oldWave.type, oldWave.freq, oldWave.amp)

        raw = nWave.play()

        falloff = []

        val = oldWave.amp

        for i in range(T*fs):
            falloff.append(val)
            val /= decay
            if val > 1:
                val = 1
        
        raw *= np.array(falloff)

        nWave.useRaw = True
        nWave.raw = raw

        return [nWave]


# canvas = [
#     output(                      deps=[[1, 0, 0]]                    ),
#     waveToTriangle(700, 500,     deps=[[2, 0, 0]],            output=[[0, 0, 0]]),
#     variableOscillator(550, 400, deps=[[3, 0, 0], [6, 0, 1]], output=[[1, 0, 0]]),
#     toFrequency(400, 300,        deps=[[4, 0, 0]],            output=[[2, 0, 0]]),
#     inverter(250, 200,           deps=[[5, 0, 0]],            output=[[3, 0, 0]]),
#     curveGenerator(100, 100, 0,                               output=[[4, 0, 0]]),
#     expression(400, 500,                                      output=[[2, 0, 1]])
# ]

canvas = [
    output(deps=[[1, 0, 0]]),
    decay(250, 200, deps=[[2, 0, 0], [3, 0, 1]], output=[[0, 0, 0]]),
    oscillator(100, 200, output=[[1, 0, 0]]),
    expression(200, 500, output=[[1, 0, 1]]),
]

# canvas = [
#     output(deps=[[1, 0, 0]]),
#     oscillator(100, 200, output=[[0, 0, 0]])
# ]

playImage = pygame.transform.rotate(pygame.image.load('play.png'), -90)

running = True
while running:

    playButtonRect = pygame.Rect(10, 10, 25, 25)

    dt = c.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mousePressed = pygame.mouse.get_pressed()
            if mousePressed[0]:
                if playButtonRect.collidepoint(mx, my):

                    while True:
                        ind = 0

                        toBreak = False
                        while (True):
                            print(ind)
                            if (len(canvas[ind].dependencies) == len(canvas[ind].filledInputs)):
                                print(ind, canvas[ind].dependencies, canvas[ind].filledInputs)
                                if (ind == 0):
                                    toBreak = True
                                    break
                                out = canvas[ind].play()

                                for i in canvas[ind].output:
                                    print(i, out)
                                    canvas[i[0]].filledInputs.append(out[i[1]])
                                break
                            else:
                                ind = canvas[ind].dependencies[len(canvas[ind].filledInputs)][0]
                        if toBreak:
                            break

                    #ind = 0
                    #while (len(canvas[0].dependencies) == len(canvas[ind].inputNodes))
                    #   while (True):
                    #      if (all dependencies are filled):
                    #         if (ind == 0):
                    #            break all the way down
                    #         out = canvas[ind].play()
                    #         for i in canvas[ind].
                    #         pass to everything that it depends on
                    #         break
                    #      else:
                    #         ind = canvas[ind].dependencies[len(canvas[ind].filledInputs)]

                    canvas[0].play()
                    for i in canvas:
                        print(i.filledInputs)
                        i.filledInputs = []

                
    
    w.fill((127, 127, 50))
    
    mx, my = pygame.mouse.get_pos()

    points = [
        [mx, my],
        [mx+20, my],
        [200+20, 200],
        [200, 200]
    ]

    mouseState = pygame.mouse.get_pressed()

    for i in canvas:
        i.render(w)
        i.update(mx, my, mouseState)

    for i in canvas:
        for j in i.dependencies:
            a = canvas[j[0]].outputNodePoints[j[1]]
            b = i.inputNodePoints[j[2]]

            points = [
                [a[0], a[1]],
                [a[0]+20, a[1]],
                [b[0]-20, b[1]],
                [b[0], b[1]]
            ]
                
            lp = [k for k in a]

            for k in range(100):
                p = cubic(points, k/100)
                pygame.draw.line(w, (255, 255, 255), lp, p, 2)
                lp = p
    
    w.blit(playImage, playButtonRect)
    
    pygame.display.flip()
pygame.quit()
