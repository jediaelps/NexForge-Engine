# Importa a classe base GameObject
from engine.game_object import GameObject


# Classe para projétil
class ProjectileObject(GameObject):

    def __init__(self, x, y, width, height, direction_x, direction_y, color=(255, 255, 80), sprite_path=None):

        super().__init__(x, y, width, height, color, sprite_path)

        # Define que este objeto é projétil
        self.is_projectile = True

        # Direção do projétil
        self.direction_x = direction_x
        self.direction_y = direction_y

        # Velocidade do projétil
        self.speed = 10


    # Atualiza o projétil
    def update(self):

        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed