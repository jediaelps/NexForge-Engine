import pygame # type: ignore

# Importa projétil
from engine.projectile_object import ProjectileObject


# Classe responsável por armazenar e controlar os objetos da cena
class Scene:
    

    # Método construtor da cena
    def __init__(self):

        # Lista onde ficam todos os objetos da cena
        self.objects = []

        # Indica se o jogador levou dano
        self.player_hit = False

        self.has_key = False
        self.level_completed = False

        # Indica se algum checkpoint já foi ativado
        self.checkpoint_activated = False

        self.saved_has_key = False
        self.saved_can_shoot = False

    # Adiciona um objeto na cena
    def add_object(self, obj):

        self.objects.append(obj)


    # Atualiza todos os objetos da cena
    def update(self, screen_width, screen_height, audio=None, collect_sound=None):

        # Procura o jogador ativo na cena
        player = None

        for obj in self.objects:
            if hasattr(obj, "is_player") and obj.active:
                player = obj
                break

        # Atualiza todos os objetos ativos
        for obj in self.objects:
            if obj.active:

                # Se o objeto for inimigo, envia o jogador para ele
                if hasattr(obj, "is_enemy"):

                    # Lista de obstáculos sólidos
                    obstacles = []

                    for item in self.objects:
                        if item == obj:
                            continue

                        if not item.active:
                            continue

                        if hasattr(item, "is_player"):
                            continue

                        if hasattr(item, "is_collectible"):
                            continue

                        if hasattr(item, "is_enemy"):
                            continue

                        obstacles.append(item)

                    obj.update(player, obstacles)

                # Caso contrário, atualiza normalmente
                else:
                    obj.update()

                if hasattr(obj, "clamp_to_screen"):
                    obj.clamp_to_screen(screen_width, screen_height)

        # Verifica disparo do jogador
        if player and player.can_shoot:

            keys = pygame.key.get_pressed()

            if keys[pygame.K_f] and player.can_fire():

                projectile = ProjectileObject(
                    player.rect.centerx,
                    player.rect.centery,
                    15,
                    15,
                    player.facing_x,
                    player.facing_y
                )

                self.add_object(projectile)

        self.check_collisions(audio, collect_sound)

        # Remove projéteis inativos da cena
        self.objects = [
            obj for obj in self.objects
            if not hasattr(obj, "is_projectile") or obj.active
        ]


    # Verifica colisões entre objetos
    def check_collisions(self, audio=None, collect_sound=None):

        # =========================
        # COLISÃO DO JOGADOR
        # =========================
        for obj in self.objects:

            if not hasattr(obj, "is_player"):
                continue

            for other in self.objects:

                if obj == other:
                    continue

                if not other.active:
                    continue

                if obj.rect.colliderect(other.rect):

                    # Coletável
                    if hasattr(other, "is_collectible"):

                        other.active = False
                        other.collected = True

                        if audio and collect_sound:
                            audio.play_sound(collect_sound)

                        continue

                    # Chave
                    if hasattr(other, "is_key"):

                        other.active = False
                        other.collected = True
                        self.has_key = True

                        continue

                    # Porta
                    if hasattr(other, "is_door"):

                        if self.has_key:

                            other.locked = False
                            self.level_completed = True

                        else:

                            obj.rollback_position()

                        continue

                    # Checkpoint
                    if hasattr(other, "is_checkpoint"):

                        obj.spawn_x = other.rect.x
                        obj.spawn_y = other.rect.y

                        other.activated = True
                        self.checkpoint_activated = True

                        # Salva estado do jogador no checkpoint
                        self.saved_has_key = self.has_key
                        self.saved_can_shoot = obj.can_shoot

                        continue

                    # Power-up
                    if hasattr(other, "is_powerup"):

                        other.active = False
                        other.collected = True

                        if other.power_type == "shoot":
                            obj.can_shoot = True

                        continue

                    # Inimigo
                    if hasattr(other, "is_enemy"):

                        self.player_hit = True

                        self.has_key = False
                        self.level_completed = False

                        # Reativa chaves
                        for item in self.objects:
                            if hasattr(item, "is_key"):
                                item.active = not self.has_key
                                item.collected = self.has_key

                        # Atualiza status dos power-ups na cena
                        for item in self.objects:
                            if hasattr(item, "is_powerup"):

                                # Se o checkpoint salvou a arma, ela continua fora do mapa
                                if self.saved_can_shoot:
                                    item.active = False
                                    item.collected = True

                                # Se não salvou a arma, ela volta para o mapa
                                else:
                                    item.active = True
                                    item.collected = False

                        # Tranca portas
                        for item in self.objects:
                            if hasattr(item, "is_door"):
                                item.locked = True

                        # Respawn
                        if hasattr(obj, "respawn"):
                            obj.respawn()

                            # Restaura estado salvo no checkpoint
                            if self.checkpoint_activated:
                                self.has_key = self.saved_has_key
                                obj.can_shoot = self.saved_can_shoot
                            else:
                                self.has_key = False
                                obj.can_shoot = False

                        # Reseta IA inimigos
                        for item in self.objects:
                            if hasattr(item, "is_enemy") and hasattr(item, "reset_ai"):
                                item.reset_ai(reset_position=True)

                        # Se não passou checkpoint
                        if not self.checkpoint_activated:

                            for item in self.objects:

                                # Reativa moedas
                                if hasattr(item, "is_collectible"):
                                    item.active = True
                                    item.collected = False

                        continue

                    # Colisão comum
                    obj.rollback_position()

        # =========================
        # PROJÉTEIS
        # =========================
        for projectile in self.objects:

            if not hasattr(projectile, "is_projectile"):
                continue

            if not projectile.active:
                continue

            for other in self.objects:

                if projectile == other:
                    continue

                if not other.active:
                    continue

                # Ignora player
                if hasattr(other, "is_player"):
                    continue

                # =========================
                # TIRO ACERTA INIMIGO
                # =========================
                if hasattr(other, "is_enemy"):

                    if projectile.rect.colliderect(other.rect):

                        projectile.active = False

                        if hasattr(other, "take_damage"):
                            other.take_damage(1)

                        break

                # =========================
                # TIRO ACERTA PAREDE
                # =========================
                if not hasattr(other, "is_collectible") \
                and not hasattr(other, "is_key") \
                and not hasattr(other, "is_door") \
                and not hasattr(other, "is_checkpoint") \
                and not hasattr(other, "is_powerup") \
                and not hasattr(other, "is_projectile") \
                and not hasattr(other, "is_enemy"):

                    if projectile.rect.colliderect(other.rect):

                        projectile.active = False
                        break

        # =========================
        # INIMIGOS COM PAREDES
        # =========================
        for obj in self.objects:

            if not hasattr(obj, "is_enemy"):
                continue

            for other in self.objects:

                if obj == other:
                    continue

                if not other.active:
                    continue

                if hasattr(other, "is_player"):
                    continue

                if hasattr(other, "is_collectible"):
                    continue

                if hasattr(other, "is_enemy"):
                    continue

                if obj.rect.colliderect(other.rect):

                    if hasattr(obj, "bounce_back"):
                        obj.bounce_back()


    # Desenha todos os objetos
    def draw(self, screen, camera_x=0, camera_y=0):

        for obj in self.objects:

            if obj.active:

                obj.draw(
                    screen,
                    camera_x,
                    camera_y
                )

    # Limpa todos os objetos da cena
    def clear(self):

        self.objects = []
        self.player_hit = False
        self.has_key = False
        self.level_completed = False
        self.checkpoint_activated = False
        self.saved_has_key = False
        self.saved_can_shoot = False