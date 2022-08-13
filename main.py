import numpy as np
import pyaudio

import pygame
pygame.init()

# PyAudio doesn't seem to have context manager
P = pyaudio.PyAudio()

fs = 44100
T = 1

def _map(x, in_min, in_max, out_min, out_max):
    return float((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

class Slider:
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
    
    def setPos(self, mx, my, clicking):
        if pygame.Rect(self.pos[0]-(self.width/2), self.pos[1]-(self.height/2), self.width, self.height).collidepoint(mx, my) and clicking:
            self.sliderPos = self.numOptions-round((round((min(self.width/2, max(-self.width/2, self.pos[0]-mx))/(self.width/2))*self.numOptions)+self.numOptions)/2)

class Label:
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

class window:
    def __init__(self, x, y, width, height, title="", font=None, moveable = True):
        self.width = width
        self.height = height
        self.pos = [x, y]

        self.title = title
        self.font = pygame.font.Font(font, 18)

        self.moveable = moveable

        self.lo = [0, 0]
        self.onItLastFrame = False

        self.col1 = [50, 50, 50]
        self.col2 = [25, 25, 25]
        self.col3 = [100, 100, 100]
    
    def render(self, w):
        r1 = pygame.Rect(self.pos[0], self.pos[1], self.width, self.height)
        r2 = pygame.Rect(self.pos[0], self.pos[1], self.width, 20)

        pygame.draw.rect(w, self.col1, r1)
        if self.moveable:
            pygame.draw.rect(w, self.col3, r2)
        pygame.draw.rect(w, self.col2, r1, 2)
    
    def update(self, mx, my, clicking):
        r2 = pygame.Rect(self.pos[0], self.pos[1], self.width, 20)

        if self.moveable:
            if clicking[0]:
                if self.onItLastFrame:
                    self.pos[0] = mx+self.lo[0]
                    self.pos[1] = my+self.lo[1]
                    self.onItLastFrame = True
                elif r2.collidepoint(mx, my):
                    self.lo[0] = self.pos[0]-mx
                    self.lo[1] = self.pos[1]-my
                    self.onItLastFrame = True
            else:
                self.lo = [0, 0]
                self.onItLastFrame = False
    
    def set_pos(self, x):
        self.pos = x
    
    def get_pos(self):
        return self.pos

class output(window):
    def __init__(self):
        super().__init__(350, 300, 50, 100, False)
        self.stream = P.open(rate=fs, format=pyaudio.paInt16, channels=1, output=True)
    
    def play(self, x):
        x  = (x*32768).astype(np.int16)  # scale to int16 for sound card

        self.stream.write(x.tobytes())


class oscillator(window):
    def __init__(self, x, y):
        super().__init__(x, y, 100, 50, True)
        self.time = 0
        self.canv = [
            Slider(x+50, y+50, 90, 20, 10, 90)
        ]
    
    def render(self, w):
        super().render(w)
        for i in self.canv:
            i.render(w)
    
    def update(self, mx, my, clicking):
        self.canv[0].pos = [super().get_pos()[0]+50, super().get_pos()[1]+50]
        self.canv[0].setPos(mx, my, clicking[0])
    
    def play(self):

        t = np.arange(0, T, 1/fs)
        return 0.5 * np.sin(2*np.pi*((self.canv[0].sliderPos/90)*3000)*t)   # 0.5 is arbitrary to avoid clipping sound card DAC
        

w = pygame.display.set_mode((400, 400))
c = pygame.time.Clock()

playImage = pygame.transform.rotate(pygame.image.load('play.png'), -90)

canvas = [
    output(),
    oscillator(50, 50)
]

dt = 0

timer = 0

x = np.zeros(fs)

running = True
while running:
    s = pygame.time.get_ticks()

    timer += dt
    playButtonRect = pygame.Rect(10, 10, 25, 25)
    
    mx, my = pygame.mouse.get_pos()
    mousePressed = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mousePressed = pygame.mouse.get_pressed()
            if mousePressed[0]:
                if playButtonRect.collidepoint(mx, my):
                    T=1
                    x = canvas[1].play()
                    canvas[0].play(x)

    
    w.fill((127, 127, 127))
    
    for i in canvas:
        if type(i) == output:
            i.update(mx, my, mousePressed)
        if type(i) == oscillator:
            i.update(mx, my, mousePressed)
        i.render(w)
    
    w.blit(playImage, playButtonRect)
    
    pygame.display.flip()
    e = pygame.time.get_ticks()
    dt = e-s
pygame.quit()
