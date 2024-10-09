import sys

import pygame

from scripts.utils import load_images, load_image
from scripts.tilemap import Tilemap

RENDER_SCALE = 2.0

class Editor:
    def __init__(self):
        # Initialisiere Pygame
        pygame.init()

        # Erstelle Fenster
        pygame.display.set_caption("Map Editor")            # Fenstername festlegen
        self.screen = pygame.display.set_mode((640, 480))   # Legt die Fenstergröße fest
        self.display = pygame.Surface((320, 240))           # Erstellt eine Fläche

        # Lege FPS fest
        self.clock = pygame.time.Clock()

        # Lade Assets (Bilder)
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'spawners': load_images('tiles/spawners'),
            'goal': [load_images('tiles/goal')[0]], # Benutze nur die erste Flagge, ohne Fahne für den Editor / Zweite Flagge mit Fahne wird im Spiel verwendet, wenn Spiel gewonnen werden kann
            'heart': load_images('tiles/heart'),
        }

        self.level = 10

        # Kamera Bewegung
        self.movement = [False, False, False, False]    # [hoch, runter, links, rechts]
        self.scroll = [0, 0]                            # [x, y]

        self.tilemap = Tilemap(self, tile_size=16)
        try:
            self.tilemap.load(f'./data/maps/{self.level}.json')
        except:
            print(FileNotFoundError("WARNUNG: Karte map.json nicht gefunden! - Starte mit leerer Karte"))
        
        self.tile_list = list(self.assets)
        self.tile_group = 0
        self.tile_variant = 0

        self.clicking = False
        self.right_clicking = False
        self.shift = False

        self.num_goals = 0
        self.num_player = 0

    def run(self):
        # Hauptspiel-Schleife
        while True:
            self.display.fill((0, 0, 0))

            # Bewegung der Kamera
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))

            # Aktuelle Kachel im Editor anzeigen (oben links)
            current_tile_img = self.assets[self.tile_list[self.tile_group]][self.tile_variant].copy()
            current_tile_img.set_alpha(150)

            # Maus Position
            mpos = pygame.mouse.get_pos()
            mpos = (mpos[0] / RENDER_SCALE, mpos[1] / RENDER_SCALE)
            
            # Maus Position in Kachel Position umwandeln
            tile_pos = (int(mpos[0] + self.scroll[0]) // self.tilemap.tile_size, int(mpos[1] + self.scroll[1]) // self.tilemap.tile_size)
            self.display.blit(current_tile_img, mpos)

            # ================================================================================================
            # Zeichne Kacheln
            # Setze Kachel an Maus-Position (Links-Klick)
            if self.clicking:
                tile_type = self.tile_list[self.tile_group]
                tile_variant = self.tile_variant

                # Prüfe, ob Ziel-Flagge bereits gesetzt wurde
                if tile_type == 'goal' and tile_variant == 0:
                    if self.num_goals == 0:
                        self.num_goals = 1
                    else:
                        # Wenn Ziel-Flagge bereits gesetzt wurde, dann entferne die Ziel-Flagge, um nur eine Ziel-Flagge zu haben
                        self.num_goals = 0
                        self.tilemap.extract([('goal', 0)], keep=False)

                # Prüfe, ob Spieler-Spawner bereits gesetzt wurde
                if tile_type == 'spawners' and tile_variant == 0:
                    if self.num_player == 0:
                        self.num_player = 1
                    else:
                        # Wenn Spieler-Spawner bereits gesetzt wurde, dann entferne den Spieler-Spawner, um nur einen Spieler-Spawner zu haben
                        self.num_player = 0
                        self.tilemap.extract([('spawners', 0)], keep=False)        

                self.tilemap.tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': self.tile_list[self.tile_group], 'variant': self.tile_variant, 'pos': list(tile_pos)}
                    

            # Lösche Kachel bei Rechtsklick
            if self.right_clicking:
                tile_loc = str(tile_pos[0]) + ';' + str(tile_pos[1])
                if tile_loc in self.tilemap.tilemap:
                    del self.tilemap.tilemap[tile_loc]

            # Zeichne alle aktuellen Kacheln (Karte)
            self.tilemap.render(self.display, offset=render_scroll)

            # Zeichne aktuelle Kachel auf Display (oben links)
            self.display.blit(current_tile_img, (5, 5))


            # ================================================================================================
            # Event-Handling (Eingaben von Tastatur, Maus, etc.)
            # Prüfe alle verfügbaren Events
            for event in pygame.event.get():
                # Beende Editor mit Fenster schließen oder ESC-Taste
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()


                # Maus-Events drücken
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # Linksklick drücken
                        self.clicking = True
                    if event.button == 3:
                        # Rechtsklick drücken
                        self.right_clicking = True
                    if self.shift:
                        # Verändere die Variation der Kachel (Gras 1, Gras 2, ...)
                        if event.button == 4:
                            # Mausrad nach oben
                            self.tile_variant = (self.tile_variant + 1) % len(self.assets[self.tile_list[self.tile_group]])
                        if event.button == 5:
                            # Mausrad nach unten
                            self.tile_variant = (self.tile_variant - 1) % len(self.assets[self.tile_list[self.tile_group]])
                    else:
                        # Verändere die Gruppe der Kacheln (Gras, Stein, ...)
                        if event.button == 4:
                            # Mausrad nach oben
                            self.tile_group = (self.tile_group + 1) % len(self.tile_list)
                            self.tile_variant = 0
                        if event.button == 5:
                            # Mausrad nach unten
                            self.tile_group = (self.tile_group - 1) % len(self.tile_list)
                            self.tile_variant = 0

                # Maus-Events loslassen
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        # Linksklick loslassen
                        self.clicking = False
                    if event.button == 3:
                        # Rechtsklick loslassen
                        self.right_clicking = False


                # Taste drücken
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        # Kamera nach links bewegen
                        self.movement[0] = True
                    if event.key == pygame.K_d:
                        # Kamera nach rechts bewegen
                        self.movement[1] = True
                    if event.key == pygame.K_w:
                        # Kamera nach oben bewegen
                        self.movement[2] = True
                    if event.key == pygame.K_s:
                        # Kamera nach unten bewegen
                        self.movement[3] = True
                    if event.key == pygame.K_LSHIFT:
                        # Verändere die Variation der Kachel (Gras 1, Gras 2, ...)
                        self.shift = True
                    if event.key == pygame.K_o:
                        # Speichere die aktuelle Karte
                        self.tilemap.save(f'./data/maps/{self.level}.json')
                    if event.key == pygame.K_t:
                        # Starte autotiling (automatisches Füllen der Kacheln)
                        self.tilemap.autotile()

                # Taste loslassen
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        # Beende Kamera-Bewegung nach links
                        self.movement[0] = False
                    if event.key == pygame.K_d:
                        # Beende Kamera-Bewegung nach rechts
                        self.movement[1] = False
                    if event.key == pygame.K_w:
                        # Beende Kamera-Bewegung nach oben
                        self.movement[2] = False
                    if event.key == pygame.K_s:
                        # Beende Kamera-Bewegung nach unten
                        self.movement[3] = False
                    if event.key == pygame.K_LSHIFT:#
                        # Beende Veränderung der Variation der Kachel
                        self.shift = False



            # ================================================================================================
            # Zeichne Display auf Fenster
            # Vergrößere die Anzeige und zeichne sie auf das Fenster
            # Dadurch wird der Pixel-Effekt erzeugt, in dem alle Elemente vergrößert werden
            # Vergrößere display auf die Größe von screen und zeichne es auf screen
            # Von 320x240 -> 640x480
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            
            # Update den Bildschirm (Zeige alle gezcihneten Elemente an) 
            pygame.display.update()
            
            # Setze die FPS auf 60
            self.clock.tick(60)

                    
if __name__ == '__main__':
    # Initialisiere Editor
    editor = Editor()
    
    # Starte Editor
    editor.run()