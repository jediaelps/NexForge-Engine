# Importa a classe base GameObject
from engine.game_object import GameObject


# Classe para objetos coletáveis
class CollectibleObject(GameObject):

    # Método construtor do coletável
    def __init__(self, x, y, width, height, color=(255, 220, 80), sprite_path=None):

        # Chama o construtor da classe GameObject
        super().__init__(x, y, width, height, color, sprite_path)

        # Define que este objeto é coletável
        self.is_collectible = True