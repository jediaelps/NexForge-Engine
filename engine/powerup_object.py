# Importa a classe base GameObject
from engine.game_object import GameObject


# Classe para power-up
class PowerUpObject(GameObject):

    def __init__(self, x, y, width, height, color=(80, 255, 255), sprite_path=None):

        super().__init__(x, y, width, height, color, sprite_path)

        # Define que este objeto é um power-up
        self.is_powerup = True

        # Tipo do poder
        self.power_type = "shoot"

        # Indica se foi coletado
        self.collected = False