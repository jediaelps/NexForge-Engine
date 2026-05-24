# Importa a classe base GameObject
from engine.game_object import GameObject

# Importa a biblioteca Pygame
import pygame # type: ignore


# Classe específica para o jogador
class PlayerObject(GameObject):

    # Método construtor do jogador
    def __init__(self, x, y, width, height, color=(80, 180, 255), sprite_path=None):

        # Chama o construtor da classe GameObject
        super().__init__(x, y, width, height, color, sprite_path)

        # Poder de atirar
        self.can_shoot = False
        self.shoot_cooldown = 500
        self.last_shot_time = 0
        self.facing_x = 1
        self.facing_y = 0

        # Tempo entre tiros em milissegundos
        self.shoot_cooldown = 500

        # Momento do último tiro
        self.last_shot_time = 0

        # Direção que o jogador está olhando
        self.facing_x = 1
        self.facing_y = 0

        # Posição de respawn
        self.spawn_x = x
        self.spawn_y = y

        # Define que este objeto é o jogador
        self.is_player = True

        # Define a velocidade do jogador
        self.speed = 5

        # Guarda posição anterior
        self.old_x = x
        self.old_y = y

        # Guarda posição inicial do jogador
        self.spawn_x = x
        self.spawn_y = y


    # Atualiza a lógica do jogador
    def update(self):

        # Guarda posição anterior
        self.old_x = self.rect.x
        self.old_y = self.rect.y

        # Captura teclas pressionadas
        keys = pygame.key.get_pressed()

        # Movimento para cima
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            self.facing_x = 0
            self.facing_y = -1

        if keys[pygame.K_s]:
            self.rect.y += self.speed
            self.facing_x = 0
            self.facing_y = 1

        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_x = -1
            self.facing_y = 0

        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_x = 1
            self.facing_y = 0
        
        


    # Volta para posição anterior em caso de colisão comum
    def rollback_position(self):

        self.rect.x = self.old_x
        self.rect.y = self.old_y


    # Reinicia o jogador para a posição inicial
    def respawn(self):

        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y


    # Impede o jogador de sair da tela
    def clamp_to_screen(self, screen_width, screen_height):

        if self.rect.left < 0:
            self.rect.left = 0

        if self.rect.right > screen_width:
            self.rect.right = screen_width

        if self.rect.top < 0:
            self.rect.top = 0

        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

    # Volta jogador para posição inicial
    def respawn(self):

        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y

    # Verifica se pode atirar
    def can_fire(self):

        current_time = pygame.time.get_ticks()

        if current_time - self.last_shot_time >= self.shoot_cooldown:
            self.last_shot_time = current_time
            return True

        return False