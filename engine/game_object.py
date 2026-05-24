# Importa a biblioteca Pygame
import pygame


# Classe base para qualquer objeto dentro do jogo
class GameObject:

    # Método construtor do objeto
    def __init__(self, x, y, width, height, color=(80, 180, 255), sprite_path=None):

        # Define a posição e o tamanho do objeto
        self.rect = pygame.Rect(x, y, width, height)

        # Define a cor do objeto
        self.color = color

        # Define se o objeto está ativo na cena
        self.active = True

        # Guarda a imagem do objeto
        self.sprite = None

        # Se o caminho da sprite for informado, carrega a imagem
        if sprite_path:
            self.sprite = pygame.image.load(sprite_path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (width, height))


    # Atualiza a lógica do objeto
    def update(self):
        pass


    # Desenha o objeto na tela
    def draw(self, screen, camera_x=0, camera_y=0):

        # Só desenha se o objeto estiver ativo
        if self.active:

            # Calcula posição na tela baseada na câmera
            render_x = self.rect.x - camera_x
            render_y = self.rect.y - camera_y

            # Se tiver sprite, desenha imagem
            if self.sprite:

                screen.blit(
                    self.sprite,
                    (render_x, render_y)
                )

            # Se não tiver sprite, desenha retângulo
            else:

                pygame.draw.rect(
                    screen,
                    self.color,
                    (
                        render_x,
                        render_y,
                        self.rect.width,
                        self.rect.height
                    )
                )