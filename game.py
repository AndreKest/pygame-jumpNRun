import sys

import pygame

from scripts.utils import load_image, load_images, Animation, GoalFlag
from scripts.tilemap import Tilemap
from scripts.clouds import Clouds
from scripts.entities import Player, Enemy


class Game:
    def __init__(self):
        # Initialisiere Pygame
        pygame.init()

        # Erstelle Fenster
        pygame.display.set_caption("Jump N Run")            # Fenstername festlegen
        self.screen = pygame.display.set_mode((640, 480))   # Legt die Fenstergröße fest
        self.display = pygame.Surface((320, 240))           # Erstellt eine Fläche

        # Lege FPS fest
        self.clock = pygame.time.Clock()

        # Bewegung des Bildschirms
        self.img_pos = [160, 260]
        self.movement = [False, False]

        # Lade Assets (Bilder)
        self.assets = {
            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.png'),
            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_duration=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_duration=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_duration=6),
            'player/run': Animation(load_images('entities/player/run'), img_duration=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'spawners': load_images('tiles/spawners'),
            'goal': load_images('tiles/goal'),
        }

        # Initialisiere Wolken
        self.clouds = Clouds(load_images('clouds'), count=16)

        # Initialisiere Tilemap
        self.tilemap = Tilemap(self, tile_size=16)

        # Level-Number
        self.level = 0

        # Max Levvel
        self.max_level = 3

        # Lade Spiel/Level
        self.load_game(id=self.level)


    def load_game(self, id=0):
        """ Lade das Spiel/Level"""

        self.tilemap.load(f'./data/maps/{id}.json')

        # Spawner (Gengner und Spieler)
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                # Initialisiere Spieler
                self.player = Player(self, (50, 50), (8, 15))
                # Wenn Spawner ein Spieler ist, dann setze die Position des Spielers auf die Position des Spawners
                self.player.pos = spawner['pos']
            else:
                # Wenn Spawner ein Gegner ist, dann erstelle den Gegner an der Position des Spawners
                enemy = Enemy(self, spawner['pos'], (8, 15))
                self.enemies.append(enemy)

        self.dead = 0   # 0 = Spieler lebt, 1 = Spieler ist tot

        self.scroll = [0, 0]

        # Lade Ziel-Flagge
        self.GoalFlag = GoalFlag(self)

 
    def run(self):
        """ Hauptspiel-Schleife """
        while True:
            # Erstelle Hintergrund
            self.display.blit(self.assets['background'], (0, 0))

            # Wenn Spieler tot ist, dann lade das Spiel neu
            if self.dead:
                self.dead += 1
                if self.dead > 40:
                    self.load_game(self.level)

            # ================================================================================================
            # Kamera Fokus auf den Spieler
            # Spieler ist in der Mitte des Bildschirms -> Kamera bewegt sich entsprechend dem Spieler
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            # Für die Anzeige auf dem Bildschirm (render) -> Runde die Float-Werte auf Int-Werte
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))      # x, y

            # ================================================================================================
            # Update die Positionen der Elemente und zeichne sie auf die Oberfläche
            # Wolke
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)

            # Tilemap (Karte)
            self.tilemap.render(self.display, offset=render_scroll)

            # Spieler
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            # Gegner
            for enemy in self.enemies.copy():
                enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
            

            for enemy in self.enemies.copy():
                self.enemies.remove(enemy)
            

            # Ziel-Flagge
            # Wenn enemies leer ist, dann zeige die Flagge an
            if not self.enemies:
                self.GoalFlag.render(self.display, offset=render_scroll)

            # Checke, ob der Spieler das Ziel erreicht hat 
            if self.GoalFlag.check_finished() and not self.enemies:
                print(f"Level {self.level + 1} beendet")
                self.level += 1
                self.load_game(self.level)


            # ================================================================================================
            # Event-Handling (Eingaben von Tastatur, Maus, etc.)
            # Prüfe alle verfügbaren Events
            for event in pygame.event.get():
                # Beende das Spiel, wenn Fenster geschlossen oder ESC gedrückt wird
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                
                # Verarbeite Spieler-Eingaben
                if event.type == pygame.KEYDOWN:    # Taste gedrückt?
                    if event.key == pygame.K_a:
                        self.movement[0] = True     # Bewegung nach links
                    if event.key == pygame.K_d:
                        self.movement[1] = True     # Bewegung nach rechts
                    if event.key == pygame.K_w:
                        self.player.jump()         # Sprung nach oben ist negative Geschwindigkeit in y-Richtung

                if event.type == pygame.KEYUP:      # Taste losgelassen?
                    if event.key == pygame.K_a:
                        self.movement[0] = False    # Beende Bewegung nach links
                    if event.key == pygame.K_d:
                        self.movement[1] = False    # Beende Bewegung nach rechts
                    

            # ================================================================================================
            # Vergrößere die Anzeige und zeichne sie auf das Fenster
            # Dadurch wird der Pixel-Effekt erzeugt, in dem alle Elemente vergrößert werden
            # Vergrößere display auf die Größe von screen und zeichne es auf screen
            # Von 320x240 -> 640x480
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))

            # Update den Bildschirm (Zeige alle gezcihneten Elemente an) 
            pygame.display.update()
            
            # Setze die FPS auf 60
            self.clock.tick(60)

            if self.level > self.max_level:
                print("Spiel beendet - Alle Level geschafft")
                pygame.quit()
                sys.exit()


if __name__ == '__main__':
    # Initialisiere Spiel
    game = Game()
    
    # Starte Spiel
    game.run()