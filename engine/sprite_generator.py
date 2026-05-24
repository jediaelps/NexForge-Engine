# Importa a biblioteca Pygame
import pygame # type: ignore

# Importa biblioteca do sistema
import os


# Classe responsável por gerar sprites simples automaticamente
class SpriteGenerator:

    # Garante que a pasta de saída exista
    @staticmethod
    def ensure_folder(folder_path):

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)


    # Gera sprite do player
    @staticmethod
    def generate_player(path):

        surface = pygame.Surface((50, 50), pygame.SRCALPHA)

        pygame.draw.rect(surface, (80, 180, 255), (10, 10, 30, 35))
        pygame.draw.circle(surface, (255, 220, 180), (25, 10), 10)
        pygame.draw.circle(surface, (0, 0, 0), (21, 8), 2)
        pygame.draw.circle(surface, (0, 0, 0), (29, 8), 2)

        pygame.image.save(surface, path)


    # Gera sprite do inimigo
    @staticmethod
    def generate_enemy(path):

        surface = pygame.Surface((50, 50), pygame.SRCALPHA)

        pygame.draw.rect(surface, (255, 80, 80), (8, 12, 34, 30))
        pygame.draw.circle(surface, (255, 255, 255), (18, 22), 5)
        pygame.draw.circle(surface, (255, 255, 255), (32, 22), 5)
        pygame.draw.circle(surface, (0, 0, 0), (18, 22), 2)
        pygame.draw.circle(surface, (0, 0, 0), (32, 22), 2)

        pygame.image.save(surface, path)


    # Gera sprite da moeda
    @staticmethod
    def generate_coin(path):

        surface = pygame.Surface((35, 35), pygame.SRCALPHA)

        pygame.draw.circle(surface, (255, 220, 80), (17, 17), 15)
        pygame.draw.circle(surface, (255, 180, 40), (17, 17), 10)
        pygame.draw.circle(surface, (255, 240, 130), (12, 10), 4)

        pygame.image.save(surface, path)


    # Gera sprite do bloco
    @staticmethod
    def generate_block(path):

        surface = pygame.Surface((80, 80), pygame.SRCALPHA)

        pygame.draw.rect(surface, (120, 120, 140), (0, 0, 80, 80))
        pygame.draw.rect(surface, (80, 80, 100), (0, 0, 80, 80), 4)

        pygame.image.save(surface, path)


    # Gera todos os sprites padrão
    @staticmethod
    def generate_default_sprites():

        folder = "assets/generated"

        SpriteGenerator.ensure_folder(folder)

        SpriteGenerator.generate_player(f"{folder}/player.png")
        SpriteGenerator.generate_enemy(f"{folder}/enemy.png")
        SpriteGenerator.generate_coin(f"{folder}/coin.png")
        SpriteGenerator.generate_block(f"{folder}/block.png")
        SpriteGenerator.generate_key(f"{folder}/key.png")
        SpriteGenerator.generate_door(f"{folder}/door.png")
        SpriteGenerator.generate_checkpoint(f"{folder}/checkpoint.png")
        SpriteGenerator.generate_shoot_powerup(f"{folder}/shoot_powerup.png")

    # Gera sprite da chave
    @staticmethod
    def generate_key(path):

        surface = pygame.Surface((35, 35), pygame.SRCALPHA)

        pygame.draw.circle(surface, (255, 220, 80), (12, 17), 8)
        pygame.draw.rect(surface, (255, 220, 80), (18, 15, 14, 5))
        pygame.draw.rect(surface, (255, 180, 40), (27, 20, 4, 8))

        pygame.image.save(surface, path)


    # Gera sprite da porta
    @staticmethod
    def generate_door(path):

        surface = pygame.Surface((60, 80), pygame.SRCALPHA)

        pygame.draw.rect(surface, (120, 80, 255), (8, 5, 44, 70))
        pygame.draw.rect(surface, (70, 50, 160), (8, 5, 44, 70), 4)
        pygame.draw.circle(surface, (255, 220, 80), (42, 40), 4)

        pygame.image.save(surface, path)


    # Gera sprite do checkpoint
    @staticmethod
    def generate_checkpoint(path):

        surface = pygame.Surface((45, 60), pygame.SRCALPHA)

        pygame.draw.rect(surface, (220, 220, 220), (20, 8, 5, 45))
        pygame.draw.polygon(surface, (80, 255, 180), [(25, 10), (42, 20), (25, 30)])

        pygame.image.save(surface, path)


    # Gera sprite do power-up de tiro
    @staticmethod
    def generate_shoot_powerup(path):

        surface = pygame.Surface((35, 35), pygame.SRCALPHA)

        # Corpo da arma
        pygame.draw.rect(surface, (80, 80, 90), (6, 12, 22, 8))

        # Cano
        pygame.draw.rect(surface, (50, 50, 60), (24, 14, 8, 4))

        # Cabo
        pygame.draw.rect(surface, (100, 70, 40), (10, 20, 8, 10))

        # Brilho do power-up
        pygame.draw.circle(surface, (80, 255, 255), (28, 8), 4)

        pygame.image.save(surface, path)