import pygame

class PhysicsEntity:
    """ 
    Basisklasse für alle physikalischen Entitäten 
    Gibt den Entitäten die Möglichkeit Gravtitation zu spüren
    """
    def __init__(self, game, e_type, pos, size):
        """
        game: Referenz zum Spiel
        e_type: Typ der Entität (Spieler, Gegner, etc.)
        pos: Position der Entität (x, y)
        size: Größe der Entität (width, height)
        """
        self.game = game
        self.e_type = e_type
        self.pos = list(pos)
        self.size = size

        self.velocity = [0, 0]  # Geschwindigkeit der Entität
        self.collision = {'up': False, 'down': False, 'left': False, 'right': False}    # Check, falls in einer Richtung mit anderen Entitäten kollidiert wird

        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False               # Spieler dreht sich nach links oder rechts abh. von der Bewegungsrichtung
        self.set_action('idle')         # Standard-Aktion: idle (Steht still)
    
    def rect(self):
        """ Gibt das Rechteck um dem Objekt zurück """
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        """ Setze die Aktion der Entität """
        # Wenn Aktion der Entität sich ändert, dann setze Aktion neu und lade das zugehörige Bild (steht in assets)
        if self.action != action:
            self.action = action
            self.animation = self.game.assets[self.e_type + '/' + self.action].copy()
        
    def update(self, tilemap, movement):
        """ Update die Position der Entität und prüfe Kollisionen """
        # Setze die Überprüfungsvariable für Kollisionen zurück
        self.collisions = {'up': False, 'down': False, 'left': False, 'right': False}

        # Berechne die Bewegung der Entität (Ändere Position entsprechend der Geschwindigkeit)
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])

        # ================================================================================================
        # Ändere die Position der Entität in x-Richtung (rechts/links)
        self.pos[0] += frame_movement[0]
        # Prüfe Kollisionen in x-Richtung
        entity_rect = self.rect()   # Rechteck um die Entität (Spieler)
        # Prüfe ob, um die Entität herum Kollisionen mit anderen Entitäten oder der Karte vorhanden sind
        # --> Prüfe nicht alle Felder, sondern nur die, die in der Nähe der Entität sind
        for rect in tilemap.physics_rects_around(self.pos):
            # Prüfe, ob das Rechteck der Entität mit einem anderen Rechteck kollidiert
            if entity_rect.colliderect(rect):
                # Wenn Entität nach rechts bewegt und kollidiert, dann ändere Rechteck der Entität - Position rechts wird auf linke Position des kollidierten Rechtecks gesetzt 
                # --> Dadurch kann Entität (Spieler oder Gegner) nicht durch Objekte laufen
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                # Wenn Entität nach links bewegt und kollidiert, dann ändere Rechteck der Entität - Position links wird auf rechte Position des kollidierten Rechtecks gesetzt 
                # --> Dadurch kann Entität (Spieler oder Gegner) nicht durch Objekte laufen
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                
                # Setze die Position der Entität auf die neue Position von seinem Rechteck, dass um ihn liegt
                self.pos[0] = entity_rect.x


        # ================================================================================================
        # Ändere die Position der Entität in y-Richtung (oben/unten)
        self.pos[1] += frame_movement[1]
        # Prüfe Kollisionen in y-Richtung
        entity_rect = self.rect()   # Rechteck um die Entität (Spieler)
        # Prüfe ob, um die Entität herum Kollisionen mit anderen Entitäten oder der Karte vorhanden sind
        # --> Prüfe nicht alle Felder, sondern nur die, die in der Nähe der Entität sind
        for rect in tilemap.physics_rects_around(self.pos):
            # Prüfe, ob das Rechteck der Entität mit einem anderen Rechteck kollidiert
            if entity_rect.colliderect(rect):
                # Wenn Entität nach unten bewegt und kollidiert, dann ändere Rechteck der Entität - Position unten wird auf obere Position des kollidierten Rechtecks gesetzt 
                # --> Dadurch kann Entität (Spieler oder Gegner) nicht durch Objekte fallen
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                # Wenn Entität nach oben bewegt und kollidiert, dann ändere Rechteck der Entität - Position oben wird auf untere Position des kollidierten Rechtecks gesetzt 
                # --> Dadurch kann Entität (Spieler oder Gegner) nicht durch Objekte springen
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                
                # Setze die Position der Entität auf die neue Position von seinem Rechteck, dass um ihn liegt
                self.pos[1] = entity_rect.y

        
        # ================================================================================================
        # Spiegel die Animation, wenn Entität sich nach links bewegt
        if movement[0] > 0:         # nach rechts
            self.flip = False
        if movement[0] < 0:         # nach links
            self.flip = True

        # ================================================================================================
        # Gravitation
        self.velocity[1] = min(5, self.velocity[1] + 0.1)   # Maximale Geschwindigkeit in y-Richtung: 5

        # Setze Gravitation auf 0, wenn Kollision in y-Richtung (Entität steht auf dem Boden oder springt gegen Decke)
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0

        # ================================================================================================
        self.animation.update() 

    def render(self, surf, offset=(0, 0)):
        """ 
        Zeichne die Entität auf Display 
        offset: Verschiebung der Entität (um, Kamera-Position) -> Spieler bewegt sich, Kamera folgt Spieler
        flip die Animation (Bild des Spielers), wenn Spieler sich nach links bewegt (dass er in die Richtung schaut)
        """
        surf.blit(pygame.transform.flip(self.animation.img(), flip_x=self.flip, flip_y=False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))


class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0

    def update(self, tilemap, movement=(0, 0)):
        """ Update die Position und Aktion/Animation des Spielers """
        super().update(tilemap, movement)

        self.air_time += 1
        if self.collisions['down']:
            self.air_time = 0

        if self.air_time > 4:
            # Wenn Spieler springt (air_time > 4), dann setze Aktion auf 'jump'
            self.set_action('jump')
        elif movement[0] != 0:
            # Wenn Spieler sich bewegt (movement[0] != 0), dann setze Aktion auf 'run'
            self.set_action('run')
        else:
            # Wenn Spieler steht, dann setze Aktion auf 'idle'
            self.set_action('idle')