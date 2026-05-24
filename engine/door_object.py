# Importa a classe base GameObject
from engine.game_object import GameObject


# Classe para porta
class DoorObject(GameObject):

    def __init__(self, x, y, width, height, color=(120, 80, 255), sprite_path=None):

        super().__init__(x, y, width, height, color, sprite_path)

        # Define que este objeto é uma porta
        self.is_door = True

        # Porta começa trancada
        self.locked = True