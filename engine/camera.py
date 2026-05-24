# Classe responsável pela câmera do jogo
class Camera:

    # Método construtor da câmera
    def __init__(self):

        # Posição da câmera
        self.x = 0
        self.y = 0


    # Faz a câmera seguir um alvo com limite de mapa
    def follow(self, target, screen_width, screen_height, world_width, world_height):

        # Centraliza a câmera no alvo
        self.x = target.rect.centerx - screen_width // 2
        self.y = target.rect.centery - screen_height // 2

        # Impede a câmera de passar do lado esquerdo
        if self.x < 0:
            self.x = 0

        # Impede a câmera de passar do topo
        if self.y < 0:
            self.y = 0

        # Impede a câmera de passar do lado direito
        if self.x > world_width - screen_width:
            self.x = world_width - screen_width

        # Impede a câmera de passar da parte inferior
        if self.y > world_height - screen_height:
            self.y = world_height - screen_height