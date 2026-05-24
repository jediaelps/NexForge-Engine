import pygame # type: ignore

# Importa a cena
from engine.scene import Scene

# Importa o gerenciador de áudio
from engine.audio import AudioManager

# Importa o sistema de UI
from engine.ui import UIManager

# Importa o gerenciador de fases
from engine.level_manager import LevelManager

# Importa a câmera
from engine.camera import Camera

# Importa o jogador
from engine.player_object import PlayerObject

# Importa carregador de configurações
from engine.config_loader import ConfigLoader

# Importa o gerador de sprites
from engine.sprite_generator import SpriteGenerator


# Classe principal da engine
class Engine:

    # Método construtor da engine
    def __init__(self):

        # Carrega configurações do jogo
        self.config = ConfigLoader.load_config("config/game_config.json")

        # Inicializa o Pygame
        pygame.init()

        # Gera sprites padrão da NexForge
        SpriteGenerator.generate_default_sprites()

        # Define largura e altura da janela
        self.width = self.config["width"]
        self.height = self.config["height"]

        # Cria janela em fullscreen ou modo janela
        if self.config["fullscreen"]:

            self.screen = pygame.display.set_mode(
                (self.width, self.height),
                pygame.FULLSCREEN
            )

        else:

            self.screen = pygame.display.set_mode(
                (self.width, self.height)
            )

        # Define o título da janela
        pygame.display.set_caption(self.config["title"])

        # Controla o FPS
        self.clock = pygame.time.Clock()

        # Controla o loop principal
        self.running = True


    # Método principal da engine
    def run(self):

        # Cria a cena principal
        main_scene = Scene()

        # Cria o gerenciador de áudio
        audio = AudioManager()

        # Cria o sistema de interface
        ui = UIManager()
        # Carrega ícones do HUD
        key_icon = ui.load_icon("assets/generated/key.png")
        weapon_icon = ui.load_icon("assets/generated/shoot_powerup.png")

        # Cria a câmera
        camera = Camera()

        # Cria o gerenciador de fases
        level_manager = LevelManager()

        # Cria cor/imagem de fundo
        background_surface = None

        # Lista de fases disponíveis
        levels = self.config["levels"]

        # Índice da fase atual
        current_level = self.config["start_level"]

        # Variável de pontuação
        score = 0

        # Quantidade de vidas do jogador
        lives = self.config["player_lives"]

        # Estado de vitória da fase
        game_won = False

        # Estado de Game Over
        game_over = False

        # Estado do jogo: menu, playing, finished
        game_state = "menu"

        # Controla se os sons de estado já tocaram
        victory_sound_played = False
        game_over_sound_played = False

        # Estado de pausa
        paused = False

        # Carrega efeitos sonoros
        sounds = {}

        for sound_name, sound_path in self.config["sounds"].items():

            if sound_path:
                sounds[sound_name] = audio.load_sound(sound_path)
            else:
                sounds[sound_name] = None


        # Função para carregar a fase atual
        def load_current_level():

            # Limpa a cena atual
            main_scene.clear()

            # Carrega a fase atual
            level_manager.load_level_from_json(
                main_scene,
                levels[current_level]
            )

            nonlocal background_surface

            if level_manager.background_image:
                background_surface = pygame.image.load(level_manager.background_image).convert()
                background_surface = pygame.transform.scale(
                    background_surface,
                    (level_manager.world_width, level_manager.world_height)
                )
            else:
                background_surface = None


        # Carrega a primeira fase
        load_current_level()

        # Loop principal da engine
        while self.running:

            # Define a cor de fundo
            if background_surface:
                self.screen.blit(
                    background_surface,
                    (-camera.x, -camera.y)
                )
            else:
                self.screen.fill(level_manager.background_color)

            # Toca música da fase, se existir
            if level_manager.music:
                audio.play_music(level_manager.music)
            else:
                audio.stop_music()

            # Captura eventos da janela
            for event in pygame.event.get():

                # Fecha a janela
                if event.type == pygame.QUIT:
                    self.running = False

                # Captura teclas pressionadas uma vez
                if event.type == pygame.KEYDOWN:

                    # Fecha com ESC
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

                    # Pausa/despausa o jogo
                    if event.key == pygame.K_p and game_state == "playing":
                        paused = not paused

                    # Inicia o jogo no menu
                    if event.key == pygame.K_RETURN and game_state == "menu":
                        game_state = "playing"

                    # Avança para próxima fase após vencer
                    if event.key == pygame.K_RETURN and game_won:
                        current_level += 1

                        # Reseta controle de som de vitória
                        victory_sound_played = False

                        if current_level < len(levels):

                            # Reinicia estados da fase
                            game_won = False
                            game_over = False
                            lives = self.config["player_lives"]

                            # Carrega próxima fase
                            load_current_level()

                            # Volta para gameplay
                            game_state = "playing"

                        else:

                            # Toca som de vitória final
                            if sounds["victory"]:
                                audio.play_sound(sounds["victory"])

                            # Vai para tela final
                            game_state = "finished"

                    # Reinicia com R apenas se estiver em Game Over
                    if event.key == pygame.K_r and game_over:
                        game_won = False
                        game_over = False
                        lives = self.config["player_lives"]
                        score = 0
                        load_current_level()
                        game_state = "playing"

            # Tela de menu
            if game_state == "menu":

                ui.draw_text(
                    self.screen,
                    "NexForge Engine",
                    330,
                    200,
                    (255, 255, 80)
                )

                ui.draw_text(
                    self.screen,
                    "[ENTER] Jogar",
                    360,
                    250,
                    (220, 220, 220)
                )

                ui.draw_text(
                    self.screen,
                    "[ESC] Sair",
                    380,
                    290,
                    (160, 160, 160)
                )


                pygame.display.flip()
                self.clock.tick(self.config["fps"])
                continue

            # Tela final do jogo
            if game_state == "finished":

                ui.draw_text(
                    self.screen,
                    "PARABENS!",
                    380,
                    200,
                    (255, 255, 80)
                )

                ui.draw_text(
                    self.screen,
                    "Voce concluiu todas as fases.",
                    290,
                    250,
                    (220, 220, 220)
                )

                ui.draw_text(
                    self.screen,
                    "[ESC] Sair",
                    380,
                    300,
                    (160, 160, 160)
                )

                pygame.display.flip()
                self.clock.tick(self.config["fps"])
                continue

            # Só atualiza o jogo durante gameplay
            if game_state == "playing" and not paused and not game_over and not game_won:

                main_scene.update(
                level_manager.world_width,
                level_manager.world_height,
                audio,
                sounds["collect"]
)

                # Verifica se o jogador levou dano
                if main_scene.player_hit:

                    # Remove uma vida
                    lives -= 1

                    # Toca som de dano, se existir
                    if sounds["hit"]:
                        audio.play_sound(sounds["hit"])

                    # Se as vidas acabaram, ativa Game Over
                    if lives <= 0:
                        game_over = True

                        if not game_over_sound_played:
                            if sounds["game_over"]:
                                audio.play_sound(sounds["game_over"])

                            game_over_sound_played = True

                    # Reseta o estado de dano
                    main_scene.player_hit = False

            # Faz a câmera seguir o jogador
            for obj in main_scene.objects:

                # Procura o jogador
                if isinstance(obj, PlayerObject):

                    camera.follow(
                        obj,
                        self.width,
                        self.height,
                        level_manager.world_width,
                        level_manager.world_height
                    )

            # Verifica moedas coletadas para somar score
            for obj in main_scene.objects:

                # Verifica se o objeto foi coletado
                if hasattr(obj, "collected"):

                    # Se ainda estiver marcado como coletado
                    if obj.collected:

                        # Soma pontuação
                        score += 1

                        # Remove a marca para não somar infinitamente
                        obj.collected = False

            # A vitória agora depende da porta/chave
            if not game_over:
                game_won = main_scene.level_completed

                if game_won and not victory_sound_played:
                    if sounds["victory"]:
                        audio.play_sound(sounds["victory"])

                    victory_sound_played = True

            # Desenha os objetos da cena
            main_scene.draw(
                self.screen,
                camera.x,
                camera.y
            )

            # Desenha número da fase atual
            ui.draw_text(
                self.screen,
                f"Fase: {current_level + 1}",
                20,
                20
            )

            # Desenha a pontuação
            ui.draw_text(
                self.screen,
                f"Score: {score}",
                20,
                55
            )

            # Desenha vidas do jogador
            ui.draw_text(
                self.screen,
                f"Vidas: {lives}",
                20,
                90
            )

            # Mostra ícone da chave se o jogador estiver com ela
            if main_scene.has_key:
                ui.draw_icon(
                    self.screen,
                    key_icon,
                    20,
                    130
                )

            # Mostra ícone da arma se o jogador tiver poder de atirar
            for obj in main_scene.objects:

                if isinstance(obj, PlayerObject):

                    if obj.can_shoot:
                        ui.draw_icon(
                            self.screen,
                            weapon_icon,
                            60,
                            130
                        )

            # Se venceu, mostra mensagem
            if game_won:

                ui.draw_text(
                    self.screen,
                    "FASE CONCLUIDA!",
                    330,
                    180,
                    (255, 255, 80)
                )

                ui.draw_text(
                    self.screen,
                    "[ENTER] Proxima fase",
                    310,
                    230,
                    (220, 220, 220)
                )

            # Se perdeu, mostra tela de derrota
            if game_over:

                ui.draw_text(
                    self.screen,
                    "GAME OVER",
                    360,
                    220,
                    (255, 80, 80)
                )

                ui.draw_text(
                    self.screen,
                    "[R] Reiniciar",
                    360,
                    270,
                    (220, 220, 220)
                )

            # Texto discreto de saída
            ui.draw_text(
                self.screen,
                "(ESC) Sair | (P) Pausar",
                15,
                500,
                (160, 160, 160)
            )

            # Tela de pausa
            if paused:

                ui.draw_text(
                    self.screen,
                    "JOGO PAUSADO",
                    320,
                    220,
                    (255, 255, 80)
                )

                ui.draw_text(
                    self.screen,
                    "[P] Continuar",
                    340,
                    270,
                    (220, 220, 220)
                )

            # Atualiza a tela
            pygame.display.flip()

            # Define FPS pelo arquivo de configuração
            self.clock.tick(self.config["fps"])

        # Finaliza o Pygame
        pygame.quit()