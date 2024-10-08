import json

import pygame

# Regeln für die automatische Kachelsetzung
# Wenn Nachbarn mit Index Key vorhanden sind, dann setze die Kachel mit Value
# Wemm Es gibt 9 unterschiedliche Gras- und Stein-Kacheln, abhängig von den Nachbarn, die vorhanden sind, soll die entsprechende Kachel automatisch gesetzt werden
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2,
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,

}

NEIGHBOR_OFFSET = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, -1), (0, 1), (1, 1)] # Positionen aller Nachbarn (8 Richtungen)
PHYSICS_TILES = {'grass', 'stone'}      # Welche Objekte sollen Physik haben
AUTOTILE_TYPES = {'grass', 'stone'}    # Welche Objekte können automatisch gesetzt werden

class Tilemap:
    """
    Karte in Kacheln
    --> Teilt die Karte in Kacheln der Größe tile_size ein

    Speichert nur die Kacheln, mit Position und Typ (Grass, Stone, etc.) in einem Dictionary die auch ein Element enthalten
    Leere Kacheln werden nicht als Leer gespeichert (spart Speicherplatz), da diese keine Information enthalten
    """
    def __init__(self, game, tile_size=16):
        """
        Initialisiere die Karte
        game: Referenz zum Spiel
        tile_size: Anzahl von Kacheln in x- und y-Richtung
        """
        self.game = game                # Referenz zum Spiel
        self.tile_size = tile_size      # Größe der Kacheln
        self.tilemap = {}               # Speichert alle Kacheln, die Objekte enthalten mit Position und Typ  

    def extract(self, id_pairs, keep=False):
        matches = []
        del_keys = []

        # Gehe durch alle Kacheln
        for loc in self.tilemap:
            # Nehme Kachel an Position loc
            tile = self.tilemap[loc]
            # Wenn Kachel-Typ und Variante in id_pairs vorhanden sind, dann füge Kachel der Liste hinzu
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                # Wenn keep=False, dann lösche Kachel aus tilemap
                if not keep:
                    del_keys.append(loc)

        # Lösche Kacheln aus tilemap, wenn keep=False
        if not keep:
            for loc in del_keys:
                del self.tilemap[loc]
        


        return matches


    def tiles_around(self, pos):
        """ Gibt alle Nachbar-Kacheln zurück, die um die Position pos liegen """
        tiles = []
        
        # Wandle Pixel-Position in Kachel-Position um
        tiles_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size)) # Kachel, in der sich das Objekt an pos befindet

        # Prüfe alle Nachbarn (8 Richtungen), ob diese ein Objekt enthalten
        for offset in NEIGHBOR_OFFSET:
            check_loc = str(tiles_loc[0] + offset[0]) + ';' + str(tiles_loc[1] + offset[1]) # Position des Nachbarn
            # Wenn Kachel ein Objekt enthält und somit in tilemap vorhanden ist, dann füge es der Liste hinzu
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])

        return tiles
    
    def save(self, path):
        """ Speichert die Karte in einer Datei """
        with open(path, 'w') as f:
            json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size}, f)

        print("Karte gespeichert")

        # Alternative: (Öffnen und Schließen der Datei manuell kümmern)
        # f = open(path, 'w')
        # json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size}, f)
        # f.close()

    def load(self, path):
        """ Lädt die Karte aus einer Datei """
        with open(path, 'r') as f:
            data = json.load(f)
            self.tilemap = data['tilemap']
            self.tile_size = data['tile_size']

        # Alternative: (Öffnen und Schließen der Datei manuell kümmern)
        # f = open(path, 'r')
        # data = json.load(f)
        # self.tilemap = data['tilemap']
        # self.tile_size = data['tile_size']
        # f.close()

    def solid_check(self, pos):
        """ Prüfe ob Kachel an Position pos fest ist (Boden ist) """
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]
        

    def physics_rects_around(self, pos):
        """
        Prüfe, ob Kachel um Position pos Physik besitzt und gebe (falls Physik vorhanden) das Rechteck der Kachel zurück
        Nicht alle Objekte haben Physik (z.B. Dekorationen, etc.)
        Mit diesen Dekorationen kann der Spieler nicht kollidieren (Spieler kann Durchlaufen)
        """
        rects = []
        # Prüfe alle Nachbarn (8 Richtungen), ob diese ein Objekt enthalten
        for tile in self.tiles_around(pos):
            # Wenn type der Kachel in PHYSICS_TILES enthalten ist, dann füge das Rechteck der Kachel der Liste hinzu
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0]*self.tile_size, tile['pos'][1]*self.tile_size, self.tile_size, self.tile_size))
                
        return rects
    
    def autotile(self):
        """ Fülle Kacheln, automatisch mit passenden Kacheln (z.B. Gras, Steine, etc.) """
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()

            # Prüfe alle Nachbarn (4 Richtungen), ob diese ein Objekt enthalten
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    # Autotiling nur wenn Nachbar selben Typ hat wie an der aktuellen Position loc
                    # Zwischen Stein und Gras macht es kein Sinn zu autotilen
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
                
            # Erzeuge Key für AUTOTILE_MAP Regeln
            neighbors = tuple(sorted(neighbors)) 

            # Wenn tile ein AUTOTILE_TYPE ist und die Nachbarn in AUTOTILE_MAP vorhanden sind, dann setze die Kachel
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]
                        


    def render(self, surf, offset=(0, 0)):
        """ Zeichne die Karte (Objekte wie Boden, Steine, Dekorationen, ...) auf das Display """
        # Gehe durch alle Kacheln in tilemap und zeichne die Kacheln auf die Oberfläche
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0]*self.tile_size - offset[0], tile['pos'][1]*self.tile_size - offset[1]))
    
        # Optimierte Version, die nur die Kacheln zeichnet, die auf dem Bildschirm auch sichtbar sind
        # Bei Bewegung des Bildschirms wird nur der sichtbare Bereich neu gezeichnet
        # for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
        #     for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
        #         loc = str(x) + ';' + str(y)
        #         if loc in self.tilemap:
        #             tile = self.tilemap[loc]
        #             surf.blit(self.game.assets[tile['type']][tile['variant']], (x*self.tile_size - offset[0], y*self.tile_size - offset[1]))

    def check_finished(self):
        """ Prüfe, ob der Spieler das Ziel erreicht hat """
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if tile['type'] == 'flag':
                return True
        return False


    

