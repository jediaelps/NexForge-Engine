# Importa a classe base GameObject
from engine.game_object import GameObject

# Importa a biblioteca Pygame
import pygame # type: ignore


# Classe de inimigo básico
class EnemyObject(GameObject):

    # Método construtor
    def __init__(self, x, y, width, height, color=(255, 80, 80), sprite_path=None):

        # Chama construtor da classe pai
        super().__init__(x, y, width, height, color, sprite_path)

        # Vida do inimigo
        self.health = 3

        # Posição original do inimigo
        self.spawn_x = x
        self.spawn_y = y

        # Define que este objeto é um inimigo
        self.is_enemy = True

        # Velocidades
        self.patrol_speed = 2
        self.chase_speed = 3.5
        self.speed = self.patrol_speed

        # Posição anterior
        self.old_x = x
        self.old_y = y

        # Posição inicial
        self.start_x = x
        self.start_y = y

        # Direção da patrulha
        # Opções: "right", "left", "up", "down"
        self.patrol_direction = "right"

        # Direção para onde o inimigo está olhando
        self.facing_direction = "right"

        # Distância da patrulha
        self.patrol_distance = 200

        # Controle interno da patrulha
        self.patrol_origin_x = x
        self.patrol_origin_y = y
        self.patrol_sign = 1

        # Visão
        self.vision_range = 260
        self.vision_height = 90

        # Controle de perda de visão
        self.time_without_seeing_player = 0
        self.lose_sight_time = 2000

        # Estado atual: patrol, chase, search
        self.state = "patrol"

        # Direção da patrulha: "horizontal" ou "vertical"
        self.patrol_axis = "horizontal"

        # Última posição conhecida do jogador
        self.last_known_player_x = None
        self.last_known_player_y = None


    # Atualiza lógica do inimigo
    def update(self, player=None, obstacles=None):

        if obstacles is None:
            obstacles = []

        # Guarda posição anterior
        self.old_x = self.rect.x
        self.old_y = self.rect.y

        # Tempo aproximado por frame
        delta_time = 16

        # Verifica se o jogador está no campo de visão
        if player and self.can_see_player(player, obstacles):

            self.state = "chase"
            self.time_without_seeing_player = 0

        else:

            if self.state == "chase":

                self.time_without_seeing_player += delta_time

                if self.time_without_seeing_player >= self.lose_sight_time:
                    self.state = "search"

        # Executa comportamento
        if self.state == "patrol":
            self.patrol()

        elif self.state == "chase":
            self.chase(player, obstacles)

        elif self.state == "search":
            self.search()


    # Verifica se o jogador está no campo de visão
    def can_see_player(self, player, obstacles):

        if self.facing_direction == "right":
            vision_rect = pygame.Rect(
                self.rect.right,
                self.rect.centery - self.vision_height // 2,
                self.vision_range,
                self.vision_height
            )

        elif self.facing_direction == "left":
            vision_rect = pygame.Rect(
                self.rect.left - self.vision_range,
                self.rect.centery - self.vision_height // 2,
                self.vision_range,
                self.vision_height
            )

        elif self.facing_direction == "down":
            vision_rect = pygame.Rect(
                self.rect.centerx - self.vision_height // 2,
                self.rect.bottom,
                self.vision_height,
                self.vision_range
            )

        elif self.facing_direction == "up":
            vision_rect = pygame.Rect(
                self.rect.centerx - self.vision_height // 2,
                self.rect.top - self.vision_range,
                self.vision_height,
                self.vision_range
            )

        # Se o jogador não está dentro do campo de visão, retorna falso
        if not vision_rect.colliderect(player.rect):
            return False

        # Cria uma linha aproximada entre inimigo e jogador
        line_rect = pygame.Rect(
            min(self.rect.centerx, player.rect.centerx),
            min(self.rect.centery, player.rect.centery),
            abs(self.rect.centerx - player.rect.centerx),
            abs(self.rect.centery - player.rect.centery)
        )

        # Garante tamanho mínimo para evitar retângulo zerado
        if line_rect.width == 0:
            line_rect.width = 1

        if line_rect.height == 0:
            line_rect.height = 1

        # Se algum obstáculo estiver entre os dois, bloqueia visão
        for obstacle in obstacles:

            if line_rect.colliderect(obstacle.rect):
                return False

        return True


    # Patrulha em apenas um eixo: horizontal ou vertical
    def patrol(self):

        self.speed = self.patrol_speed

        # Patrulha horizontal
        if self.patrol_axis == "horizontal":

            self.rect.x += self.speed * self.patrol_sign

            if self.patrol_sign == 1:
                self.facing_direction = "right"
            else:
                self.facing_direction = "left"

            if self.rect.x >= self.patrol_origin_x + self.patrol_distance:
                self.patrol_sign = -1

            if self.rect.x <= self.patrol_origin_x:
                self.patrol_sign = 1

        # Patrulha vertical
        elif self.patrol_axis == "vertical":

            self.rect.y += self.speed * self.patrol_sign

            if self.patrol_sign == 1:
                self.facing_direction = "down"
            else:
                self.facing_direction = "up"

            if self.rect.y >= self.patrol_origin_y + self.patrol_distance:
                self.patrol_sign = -1

            if self.rect.y <= self.patrol_origin_y:
                self.patrol_sign = 1


    # Persegue o jogador podendo andar em diagonal, mas sem atravessar paredes
    def chase(self, player, obstacles=None):

        if obstacles is None:
            obstacles = []

        self.speed = self.chase_speed

        dx = 0
        dy = 0

        if player.rect.centerx > self.rect.centerx:
            dx = int(self.speed)
        elif player.rect.centerx < self.rect.centerx:
            dx = -int(self.speed)

        if player.rect.centery > self.rect.centery:
            dy = int(self.speed)
        elif player.rect.centery < self.rect.centery:
            dy = -int(self.speed)

        # Atualiza direção de visão
        if abs(dx) > abs(dy):
            self.facing_direction = "right" if dx > 0 else "left"
        elif dy != 0:
            self.facing_direction = "down" if dy > 0 else "up"

        self.move_with_collision(dx, dy, obstacles)


    # Procura o jogador por um curto momento e volta à patrulha
    def search(self):

        self.speed = self.patrol_speed

        # Dá uma pequena andada na direção atual
        if self.facing_direction == "right":
            self.rect.x += self.speed

        elif self.facing_direction == "left":
            self.rect.x -= self.speed

        elif self.facing_direction == "down":
            self.rect.y += self.speed

        elif self.facing_direction == "up":
            self.rect.y -= self.speed

        # Volta para patrulha
        self.state = "patrol"
        self.time_without_seeing_player = 0


    # Volta para posição anterior
    def rollback_position(self):

        self.rect.x = self.old_x
        self.rect.y = self.old_y


    # Quando bate em parede/bloco
    def bounce_back(self):

        # Volta para posição anterior
        self.rollback_position()

        # Se estiver perseguindo o jogador
        if self.state == "chase":

            # Tenta mudar eixo de movimentação
            if self.facing_direction in ["right", "left"]:

                # Tenta subir ou descer
                self.rect.y += self.patrol_speed * self.patrol_sign

            else:

                # Tenta esquerda ou direita
                self.rect.x += self.patrol_speed * self.patrol_sign

            return

        # Se estiver patrulhando
        self.patrol_sign *= -1


    # Reseta IA do inimigo
    def reset_ai(self, reset_position=False):

        # Volta para patrulha
        self.state = "patrol"

        # Reseta contador de visão
        self.time_without_seeing_player = 0

        # Volta para velocidade normal
        self.speed = self.patrol_speed

        # Volta direção padrão
        self.facing_direction = self.patrol_direction
        self.patrol_sign = 1

        # Se solicitado, volta inimigo para posição original
        if reset_position:
            self.rect.x = self.spawn_x
            self.rect.y = self.spawn_y
            self.old_x = self.spawn_x
            self.old_y = self.spawn_y

    # Move o inimigo com colisão rígida, pixel por pixel
    def move_with_collision(self, dx, dy, obstacles):

        # Move no eixo X pixel por pixel
        step_x = 1 if dx > 0 else -1 if dx < 0 else 0

        for _ in range(int(abs(dx))):

            self.rect.x += step_x

            for obstacle in obstacles:
                if self.rect.colliderect(obstacle.rect):
                    self.rect.x -= step_x
                    return

        # Move no eixo Y pixel por pixel
        step_y = 1 if dy > 0 else -1 if dy < 0 else 0

        for _ in range(int(abs(dy))):

            self.rect.y += step_y

            for obstacle in obstacles:
                if self.rect.colliderect(obstacle.rect):
                    self.rect.y -= step_y
                    return
                
    # Inimigo recebe dano
    def take_damage(self, damage=1):

        self.health -= damage

        if self.health <= 0:
            self.active = False