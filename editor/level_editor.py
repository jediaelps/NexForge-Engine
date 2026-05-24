# Importa módulos do sistema
import sys
import json

# Importa componentes do PySide6
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QListWidget,
    QHBoxLayout,
    QScrollArea
)

from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt


# Canvas visual do mapa
class LevelCanvas(QWidget):

    def __init__(self):
        super().__init__()

        # Dados da fase
        self.level_data = None

        # Tamanho inicial do canvas
        self.setMinimumSize(1200, 800)

        # Objeto selecionado
        self.selected_item = None
        self.selected_category = None
        self.selected_index = None

        # Função chamada quando selecionar objeto
        self.on_object_selected = None

    # Detecta clique no canvas para selecionar objeto
    def mousePressEvent(self, event):

        if not self.level_data:
            return

        mouse_x = event.position().x()
        mouse_y = event.position().y()

        categories = [
            "blocks",
            "coins",
            "keys",
            "doors",
            "checkpoints",
            "enemies",
            "powerups"
        ]

        # Verifica clique no player
        player = self.level_data.get("player", {})

        x = player.get("x", 0)
        y = player.get("y", 0)
        width = player.get("width", 50)
        height = player.get("height", 50)

        if x <= mouse_x <= x + width and y <= mouse_y <= y + height:

            self.selected_item = player
            self.selected_category = "player"
            self.selected_index = 0

            if self.on_object_selected:
                self.on_object_selected("player", 0, player)

            self.update()
            return

        # Percorre objetos de trás para frente
        for category in categories:

            items = self.level_data.get(category, [])

            for index in range(len(items) - 1, -1, -1):

                item = items[index]

                x = item.get("x", 0)
                y = item.get("y", 0)
                width = item.get("width", 35)
                height = item.get("height", 35)

                # Moedas normalmente não têm width/height no JSON
                if category == "coins":
                    width = 35
                    height = 35

                if x <= mouse_x <= x + width and y <= mouse_y <= y + height:

                    self.selected_item = item
                    self.selected_category = category
                    self.selected_index = index

                    if self.on_object_selected:
                        self.on_object_selected(category, index, item)

                    self.update()
                    return

        # Se clicou fora, limpa seleção
        self.selected_item = None
        self.selected_category = None
        self.selected_index = None

        if self.on_object_selected:
            self.on_object_selected(None, None, None)

        self.update()


    # Recebe os dados da fase
    def set_level_data(self, level_data):

        self.level_data = level_data

        # Ajusta o tamanho do canvas conforme o tamanho do mundo
        world = self.level_data.get("world", {})
        world_width = world.get("width", 1200)
        world_height = world.get("height", 800)

        self.setMinimumSize(world_width, world_height)
        self.resize(world_width, world_height)

        # Redesenha o canvas
        self.update()


    # Desenha os objetos na tela
    def paintEvent(self, event):

        painter = QPainter(self)

        # Fundo do canvas
        painter.fillRect(self.rect(), QColor(25, 25, 30))

        if not self.level_data:
            painter.setPen(QColor(220, 220, 220))
            painter.drawText(20, 30, "Abra uma fase JSON para visualizar o mapa.")
            return

        # Desenha player
        player = self.level_data.get("player", {})
        painter.setBrush(QColor(80, 180, 255))
        painter.drawRect(
            player.get("x", 0),
            player.get("y", 0),
            player.get("width", 50),
            player.get("height", 50)
        )

        # Desenha blocos
        painter.setBrush(QColor(120, 120, 140))
        for block in self.level_data.get("blocks", []):
            painter.drawRect(
                block.get("x", 0),
                block.get("y", 0),
                block.get("width", 80),
                block.get("height", 80)
            )

        # Desenha moedas
        painter.setBrush(QColor(255, 220, 80))
        for coin in self.level_data.get("coins", []):
            painter.drawEllipse(
                coin.get("x", 0),
                coin.get("y", 0),
                35,
                35
            )

        # Desenha inimigos
        painter.setBrush(QColor(255, 80, 80))
        for enemy in self.level_data.get("enemies", []):
            painter.drawRect(
                enemy.get("x", 0),
                enemy.get("y", 0),
                enemy.get("width", 50),
                enemy.get("height", 50)
            )

        # Desenha chaves
        painter.setBrush(QColor(255, 200, 50))
        for key in self.level_data.get("keys", []):
            painter.drawEllipse(
                key.get("x", 0),
                key.get("y", 0),
                key.get("width", 35),
                key.get("height", 35)
            )

        # Desenha portas
        painter.setBrush(QColor(120, 80, 255))
        for door in self.level_data.get("doors", []):
            painter.drawRect(
                door.get("x", 0),
                door.get("y", 0),
                door.get("width", 60),
                door.get("height", 80)
            )

        # Desenha checkpoints
        painter.setBrush(QColor(80, 255, 180))
        for checkpoint in self.level_data.get("checkpoints", []):
            painter.drawRect(
                checkpoint.get("x", 0),
                checkpoint.get("y", 0),
                checkpoint.get("width", 45),
                checkpoint.get("height", 60)
            )

        # Desenha power-ups
        painter.setBrush(QColor(80, 255, 255))
        for powerup in self.level_data.get("powerups", []):
            painter.drawEllipse(
                powerup.get("x", 0),
                powerup.get("y", 0),
                powerup.get("width", 35),
                powerup.get("height", 35)
            )
        
        # Destaca objeto selecionado
        if self.selected_item:

            painter.setPen(QColor(255, 255, 255))
            painter.setBrush(Qt.BrushStyle.NoBrush)

            x = self.selected_item.get("x", 0)
            y = self.selected_item.get("y", 0)
            width = self.selected_item.get("width", 35)
            height = self.selected_item.get("height", 35)

            if self.selected_category == "coins":
                width = 35
                height = 35

            painter.drawRect(x - 3, y - 3, width + 6, height + 6)


# Classe principal do editor visual
class LevelEditor(QMainWindow):

    def __init__(self):
        super().__init__()

        # Configura janela
        self.setWindowTitle("NexForge Level Editor")
        self.resize(1200, 800)

        # Dados da fase
        self.level_data = None
        self.current_file = None

        # Widget principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Painel lateral
        side_panel = QWidget()
        side_layout = QVBoxLayout()
        side_panel.setLayout(side_layout)

        # Título
        self.title_label = QLabel("NexForge Level Editor")
        side_layout.addWidget(self.title_label)

        # Botão abrir fase
        self.open_button = QPushButton("Abrir fase JSON")
        self.open_button.clicked.connect(self.open_level)
        side_layout.addWidget(self.open_button)

        # Botão salvar fase
        self.save_button = QPushButton("Salvar fase")
        self.save_button.clicked.connect(self.save_level)
        side_layout.addWidget(self.save_button)

        # Lista de objetos da fase
        self.object_list = QListWidget()
        side_layout.addWidget(self.object_list)

        # Canvas visual
        self.canvas = LevelCanvas()

        self.canvas.on_object_selected = self.on_canvas_object_selected

        # Área com barras de rolagem
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)
        self.scroll_area.setWidget(self.canvas)

        # Adiciona painel lateral e área visual
        main_layout.addWidget(side_panel, 1)
        main_layout.addWidget(self.scroll_area, 4)


    # Abre arquivo JSON da fase
    def open_level(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir fase",
            "levels",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        with open(file_path, "r", encoding="utf-8") as file:
            self.level_data = json.load(file)

        self.current_file = file_path

        self.refresh_object_list()
        self.canvas.set_level_data(self.level_data)


    # Salva arquivo JSON da fase
    def save_level(self):

        if not self.level_data or not self.current_file:
            return

        with open(self.current_file, "w", encoding="utf-8") as file:
            json.dump(self.level_data, file, indent=4, ensure_ascii=False)


    # Atualiza lista de objetos
    def refresh_object_list(self):

        self.object_list.clear()

        if not self.level_data:
            return

        # Adiciona player na lista
        player = self.level_data.get("player", None)

        if player:
            self.object_list.addItem(
                f"player - x:{player.get('x')} y:{player.get('y')}"
            )
        
        categories = [
            "blocks",
            "coins",
            "keys",
            "doors",
            "checkpoints",
            "enemies",
            "powerups"
        ]
        
        for category in categories:

            items = self.level_data.get(category, [])

            for index, item in enumerate(items):
                self.object_list.addItem(
                    f"{category}[{index}] - x:{item.get('x')} y:{item.get('y')}"
                )
    
    # Quando seleciona objeto no canvas
    def on_canvas_object_selected(self, category, index, item):

        if category is None:
            self.object_list.clearSelection()
            return


        # PLAYER
        if category == "player":
            self.object_list.setCurrentRow(0)
            return

        categories = [
            "blocks",
            "coins",
            "keys",
            "doors",
            "checkpoints",
            "enemies",
            "powerups"
        ]

        # Começa em 1 porque player ocupa a linha 0
        row = 1

        for cat in categories:

            items = self.level_data.get(cat, [])

            for i, _ in enumerate(items):

                if cat == category and i == index:
                    self.object_list.setCurrentRow(row)
                    return

                row += 1


# Executa o editor
if __name__ == "__main__":

    app = QApplication(sys.argv)

    editor = LevelEditor()
    editor.show()

    sys.exit(app.exec())