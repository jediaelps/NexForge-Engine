# Importa a classe base GameObject
from engine.game_object import GameObject


# Classe para checkpoint
class CheckpointObject(GameObject):

    # Método construtor
    def __init__(self, x, y, width, height, color=(80, 255, 180), sprite_path=None):

        # Chama construtor da classe pai
        super().__init__(x, y, width, height, color, sprite_path)

        # Define que este objeto é um checkpoint
        self.is_checkpoint = True

        # Define se o checkpoint já foi ativado
        self.activated = False