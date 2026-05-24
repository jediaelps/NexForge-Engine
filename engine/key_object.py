# Importa a classe base GameObject
from engine.game_object import GameObject


# Classe para chave
class KeyObject(GameObject):

    def __init__(self, x, y, width, height, color=(255, 220, 80), sprite_path=None):

        super().__init__(x, y, width, height, color, sprite_path)

        # Define que este objeto é uma chave
        self.is_key = True

        # Indica se foi coletada
        self.collected = False