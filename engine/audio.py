# Importa a biblioteca Pygame
import pygame # type: ignore


# Classe responsável por controlar sons da engine
class AudioManager:

    # Método construtor do gerenciador de áudio
    def __init__(self):

        # Inicializa o mixer de áudio do Pygame
        pygame.mixer.init()


    # Carrega um som a partir do caminho informado
    def load_sound(self, sound_path):

        return pygame.mixer.Sound(sound_path)


    # Toca um som carregado
    def play_sound(self, sound):

        sound.play()

    # Toca uma música de fundo
    def play_music(self, music_path, volume=0.4):

        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)


    # Para a música de fundo
    def stop_music(self):

        pygame.mixer.music.stop()