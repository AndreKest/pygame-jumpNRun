import random

class Cloud:
    """ Eine Wolke, die sich von links nach rechts bewegt """

    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth

    def update(self):
        """
        Update die Position der Wolke 
        Verschiebe die Wolke um die Geschwindigkeit nach rechts
        """
        self.pos[0] += self.speed

    def render(self, surf, offset=(0, 0)):
        """ Zeichne die Wolke auf die Oberfläche """
        # Lege die Position fest, wo Wolke gezeichnet werden soll
        # Offset wird verwendet, um die Position der Wolke zu verschieben, wenn sich Spieler (Kamera bewegt)
        # Die Variable depth wird verwendet, um die Wolke weiter hinten in der Szene zu zeichnen (Wirkt kleiner)
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        
        # Zeichne die Wolke auf die Oberfläche und Setze die Wolke wieder auf Startposition, wenn sie vollständig aus dem Bildschirm verschwindet
        len_x = surf.get_width() + self.img.get_width()
        len_y = surf.get_height() + self.img.get_height()
        surf.blit(self.img, (render_pos[0] % len_x - self.img.get_width(), render_pos[1] % len_y - self.img.get_height()))


class Clouds:
    """ Eine Sammlung von Wolken die sich von links nach rechts bewegen """
    def __init__(self, cloud_images, count=1):
        self.clouds = []

        # Erstelle count viele Wolken
        for i in range(count):
            cloud = Cloud(
                pos = (random.random() * 99999, random.random() * 99999),   # Zufällige Position
                img = random.choice(cloud_images),                          # Wähle zufälliges Bild der Wolke (2 verfügbar)
                speed = random.random() * 0.05 + 0.05,                      # Zufällige Geschwindigkeit mit min-Wert 0.05
                depth = random.random() * 0.6 + 0.2                          # Zufällige Tiefe mit min-Wert 0.2 
            )
            self.clouds.append(cloud)
        
        # Sortiere alle Wolken nach ihrer Tiefe (Damit die Wolken weiter hinten gezeichnet werden)
        # Ziel: Wolke die vorne liegen sollen über die hinten liegenden Wolken gezeichnet werden
        self.clouds.sort(key=lambda cloud: cloud.depth)

    def update(self):
        """ Update die Position aller Wolken """
        for cloud in self.clouds:
            cloud.update()
        
    def render(self, surf, offset=(0, 0)):
        """ Zeichne alle Wolken auf die Oberfläche """
        for cloud in self.clouds:
            cloud.render(surf, offset)