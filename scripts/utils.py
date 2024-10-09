import os

import pygame

BASE_IMG_PATH = './data/images/'

def load_image(path):
    """ Lädt ein Bild und setzt die Farbe Schwarz als transparent """
    img = pygame.image.load(BASE_IMG_PATH + path)
    img.set_colorkey((0, 0, 0)) # Lege Farbe Schwarz (0, 0, 0) als transparent fest
    return img

def load_images(path):
    """
    Lädt eine Liste von Bildern 
    Wenn in einem Ordner mehrere Bilder enthalten sind, werden diese in der Reihenfolge des Dateinamens geladen
    """
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        img = load_image(path + '/' + img_name)
        images.append(img)

    return images

class Animation:
    """ Animation für ein Sprite """
    def __init__(self, images, img_duration=5, loop=True):
        """
        Initialisiere die Animation
        images: Liste von Bildern
        img_duration: Dauer eines Bildes
        loop: Soll die Animation in einer Schleife ausgeführt werden
        """
        self.images = images
        self.img_duration = img_duration
        self.loop = loop
        self.done = False
        self.frame = 0

    def copy(self):
        """ Kopiere die Animation """
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        # Wenn Animation mehrere unterschiedliche Bilder enhält, dann wiederhole die Animationen immer wieder
        if self.loop:
            self.frame = (self.frame + 1) % (len(self.images) * self.img_duration)
        else:
            self.frame = min(self.frame + 1, len(self.images) * self.img_duration - 1)
            
            if self.frame >= len(self.images) * self.img_duration - 1:
                self.done = True
    
    def img(self):
        """ Gibt das aktuelle Bild der Animation zurück """
        return self.images[int(self.frame / self.img_duration)]
    
class GoalFlag:
    """ 
    Ziel-Flagge 
    
    Wechsel Flagge im Sieg-Zustand zu einer Flagge mit Fahne
    """
    def __init__(self, game):
        self.game = game
        self.img = load_image('tiles/goal/0.png')
        
        self.pos = self.game.tilemap.extract([('goal', 0)], keep=True)[0]['pos']
        
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.img.get_width(), self.img.get_height())

    def render(self, surf, offset=(0, 0)):
        """ Zeichne die Flagge im Sieg-Zustand"""
        self.img = load_image('tiles/goal/1.png')
        surf.blit(self.img, (self.pos[0] - offset[0], self.pos[1] - offset[1]))

    def check_finished(self):
        """ Prüfe, ob das Ziel erreicht wurde """
        rect = self.rect.copy()
        # Spieler muss durch die Flagge laufen, um das Ziel zu erreichen
        img_width = self.img.get_width()
        img_height = self.img.get_height()
        reduced_width = img_width // 2
        reduced_height = img_height // 2

        # Zentriere das verkleinerte Rechteck um die Flagge
        rect = pygame.Rect(self.pos[0] + (img_width - reduced_width) // 2, self.pos[1] + (img_height - reduced_height) // 2, reduced_width, reduced_height)
        if rect.colliderect(self.game.player.rect()):
            return True