# Importa a biblioteca Pygame
import pygame # type: ignore


# Classe responsável pela interface da engine
class UIManager:

    # Método construtor da UI
    def __init__(self):

        # Cria a fonte padrão
        self.font = pygame.font.SysFont("arial", 28)


    # Desenha um texto na tela
    def draw_text(self, screen, text, x, y, color=(255, 255, 255)):

        # Renderiza o texto
        text_surface = self.font.render(text, True, color)

        # Desenha o texto na tela
        screen.blit(text_surface, (x, y))

    # Carrega um ícone para usar no HUD
    def load_icon(self, path, size=(32, 32)):

        icon = pygame.image.load(path).convert_alpha()
        icon = pygame.transform.scale(icon, size)

        return icon


    # Desenha um ícone na tela
    def draw_icon(self, screen, icon, x, y):

        screen.blit(icon, (x, y))