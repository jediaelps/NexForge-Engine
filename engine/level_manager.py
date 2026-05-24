# Importa biblioteca para ler arquivos JSON
import json

# Importa o jogador
from engine.player_object import PlayerObject

# Importa objetos comuns
from engine.game_object import GameObject

# Importa objetos coletáveis
from engine.collectible_object import CollectibleObject

from engine.enemy_object import EnemyObject

from engine.checkpoint_object import CheckpointObject

from engine.key_object import KeyObject
from engine.door_object import DoorObject

from engine.powerup_object import PowerUpObject


# Classe responsável por criar/carregar fases
class LevelManager:

    # Método construtor
    def __init__(self):

        # Tamanho padrão do mundo
        self.world_width = 960
        self.world_height = 540
        self.background_color = (30, 30, 35)
        self.background_image = None
        self.music = None


    # Carrega uma fase a partir de um arquivo JSON
    def load_level_from_json(self, scene, file_path):

        # Abre e lê o arquivo JSON
        with open(file_path, "r", encoding="utf-8") as file:
            level_data = json.load(file)

        # Carrega configurações do mundo
        world_data = level_data.get("world", {})

        self.music = world_data.get("music", None)

        self.world_width = world_data.get("width", 960)
        self.world_height = world_data.get("height", 540)

        

        self.background_color = tuple(
            world_data.get("background_color", [30, 30, 35])
        )

        self.background_image = world_data.get("background_image", None)


        # Carrega power-ups da fase
        for powerup_data in level_data.get("powerups", []):

            powerup = PowerUpObject(
                powerup_data["x"],
                powerup_data["y"],
                powerup_data.get("width", 35),
                powerup_data.get("height", 35),
                sprite_path=powerup_data.get("sprite_path") or "assets/generated/shoot_powerup.png"
            )

            scene.add_object(powerup)


        # Carrega chaves da fase
        for key_data in level_data.get("keys", []):

            key = KeyObject(
                key_data["x"],
                key_data["y"],
                key_data.get("width", 35),
                key_data.get("height", 35),
                sprite_path=key_data.get("sprite_path") or "assets/generated/key.png"
            )

            scene.add_object(key)


        # Carrega portas da fase
        for door_data in level_data.get("doors", []):

            door = DoorObject(
                door_data["x"],
                door_data["y"],
                door_data.get("width", 60),
                door_data.get("height", 80),
                sprite_path=door_data.get("sprite_path") or "assets/generated/door.png"
            )

            scene.add_object(door)


        # Carrega os checkpoints da fase
        for checkpoint_data in level_data.get("checkpoints", []):

            checkpoint = CheckpointObject(
                checkpoint_data["x"],
                checkpoint_data["y"],
                checkpoint_data.get("width", 40),
                checkpoint_data.get("height", 40),
                sprite_path=checkpoint_data.get("sprite_path") or "assets/generated/checkpoint.png"
            )

            scene.add_object(checkpoint)

        # Carrega o jogador da fase
        player_data = level_data["player"]

        player = PlayerObject(
            player_data["x"],
            player_data["y"],
            player_data["width"],
            player_data["height"],
            sprite_path = player_data.get("sprite_path") or "assets/generated/player.png"
        )

        player.spawn_x = player_data.get("spawn_x", player_data["x"])
        player.spawn_y = player_data.get("spawn_y", player_data["y"])

        scene.add_object(player)

        # Carrega os blocos da fase
        for block_data in level_data["blocks"]:

            block = GameObject(
                block_data["x"],
                block_data["y"],
                block_data["width"],
                block_data["height"],
                tuple(block_data["color"]),
                block_data.get("sprite_path") or "assets/generated/block.png"
            )

            scene.add_object(block)

        # Carrega as moedas da fase
        for coin_data in level_data["coins"]:

            coin = CollectibleObject(
                coin_data["x"],
                coin_data["y"],
                35,
                35,
                (255, 220, 80),
                coin_data.get("sprite_path") or "assets/generated/coin.png"
            )

            scene.add_object(coin)

        # Carrega os inimigos da fase
        for enemy_data in level_data.get("enemies", []):

            enemy = EnemyObject(
                enemy_data["x"],
                enemy_data["y"],
                enemy_data["width"],
                enemy_data["height"],
                sprite_path = enemy_data.get("sprite_path") or "assets/generated/enemy.png"
            )

            enemy.patrol_axis = enemy_data.get("patrol_axis", "horizontal")

            scene.add_object(enemy)