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
    QScrollArea,
    QSpinBox,
    QFormLayout
)

from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt


# ============================================================
# CANVAS VISUAL DO MAPA
# ============================================================
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

        # Controle de arrasto de objeto
        self.dragging_object = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

    # ========================================================
    # SELEÇÃO DE OBJETOS
    # ========================================================
    def mousePressEvent(self, event):

        if not self.level_data:
            return

        # Só inicia seleção/arrasto com botão esquerdo
        if event.button() != Qt.MouseButton.LeftButton:
            return

        mouse_x = event.position().x()
        mouse_y = event.position().y()

        # ----------------------------------------------------
        # PLAYER
        # Player é tratado separadamente porque no JSON
        # ele é um dicionário, e não uma lista.
        # ----------------------------------------------------
        player = self.level_data.get("player", {})

        if player:

            x = player.get("x", 0)
            y = player.get("y", 0)
            width = player.get("width", 50)
            height = player.get("height", 50)

            if x <= mouse_x <= x + width and y <= mouse_y <= y + height:

                self.selected_item = player
                self.selected_category = "player"
                self.selected_index = 0

                # Inicia arrasto
                self.dragging_object = True
                self.drag_offset_x = mouse_x - x
                self.drag_offset_y = mouse_y - y

                if self.on_object_selected:
                    self.on_object_selected(
                        "player",
                        0,
                        player
                    )

                self.update()
                return

        # ----------------------------------------------------
        # OUTROS OBJETOS
        # ----------------------------------------------------
        categories = [
            "blocks",
            "coins",
            "keys",
            "doors",
            "checkpoints",
            "enemies",
            "powerups"
        ]

        # Percorre os objetos de trás para frente
        # para priorizar objetos desenhados por último.
        for category in categories:

            items = self.level_data.get(category, [])

            for index in range(len(items) - 1, -1, -1):

                item = items[index]

                x = item.get("x", 0)
                y = item.get("y", 0)

                width = item.get("width", 35)
                height = item.get("height", 35)

                # Moedas normalmente não possuem
                # width/height no JSON.
                if category == "coins":
                    width = 35
                    height = 35

                if x <= mouse_x <= x + width and y <= mouse_y <= y + height:

                    self.selected_item = item
                    self.selected_category = category
                    self.selected_index = index

                    # Inicia arrasto
                    self.dragging_object = True
                    self.drag_offset_x = mouse_x - x
                    self.drag_offset_y = mouse_y - y

                    if self.on_object_selected:
                        self.on_object_selected(
                            category,
                            index,
                            item
                        )

                    self.update()
                    return

        # ----------------------------------------------------
        # CLICOU EM ÁREA VAZIA
        # ----------------------------------------------------
        self.selected_item = None
        self.selected_category = None
        self.selected_index = None
        self.dragging_object = False

        if self.on_object_selected:
            self.on_object_selected(
                None,
                None,
                None
            )

        self.update()

    # ========================================================
    # ARRASTAR OBJETO
    # ========================================================
    def mouseMoveEvent(self, event):

        if not self.dragging_object:
            return

        if not self.selected_item:
            return

        # Só move enquanto botão esquerdo estiver pressionado
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        mouse_x = event.position().x()
        mouse_y = event.position().y()

        new_x = int(mouse_x - self.drag_offset_x)
        new_y = int(mouse_y - self.drag_offset_y)

        self.selected_item["x"] = new_x
        self.selected_item["y"] = new_y

        # Atualiza lista e Inspector
        if self.on_object_selected:
            self.on_object_selected(
                self.selected_category,
                self.selected_index,
                self.selected_item
            )

        # Redesenha mapa
        self.update()

    # ========================================================
    # FINALIZA ARRASTO
    # ========================================================
    def mouseReleaseEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging_object = False

    # ========================================================
    # RECEBE DADOS DA FASE
    # ========================================================
    def set_level_data(self, level_data):

        self.level_data = level_data

        # Limpa seleção anterior
        self.selected_item = None
        self.selected_category = None
        self.selected_index = None
        self.dragging_object = False

        # Ajusta tamanho do canvas conforme o mundo
        world = self.level_data.get("world", {})

        world_width = world.get("width", 1200)
        world_height = world.get("height", 800)

        self.setMinimumSize(
            world_width,
            world_height
        )

        self.resize(
            world_width,
            world_height
        )

        self.update()

    # ========================================================
    # DESENHA O MAPA
    # ========================================================
    def paintEvent(self, event):

        painter = QPainter(self)

        # Fundo
        painter.fillRect(
            self.rect(),
            QColor(25, 25, 30)
        )

        if not self.level_data:

            painter.setPen(
                QColor(220, 220, 220)
            )

            painter.drawText(
                20,
                30,
                "Abra uma fase JSON para visualizar o mapa."
            )

            return

        # ----------------------------------------------------
        # PLAYER
        # ----------------------------------------------------
        player = self.level_data.get("player", {})

        if player:

            painter.setBrush(
                QColor(80, 180, 255)
            )

            painter.drawRect(
                player.get("x", 0),
                player.get("y", 0),
                player.get("width", 50),
                player.get("height", 50)
            )

        # ----------------------------------------------------
        # BLOCOS
        # ----------------------------------------------------
        painter.setBrush(
            QColor(120, 120, 140)
        )

        for block in self.level_data.get("blocks", []):

            painter.drawRect(
                block.get("x", 0),
                block.get("y", 0),
                block.get("width", 80),
                block.get("height", 80)
            )

        # ----------------------------------------------------
        # MOEDAS
        # ----------------------------------------------------
        painter.setBrush(
            QColor(255, 220, 80)
        )

        for coin in self.level_data.get("coins", []):

            painter.drawEllipse(
                coin.get("x", 0),
                coin.get("y", 0),
                35,
                35
            )

        # ----------------------------------------------------
        # INIMIGOS
        # ----------------------------------------------------
        painter.setBrush(
            QColor(255, 80, 80)
        )

        for enemy in self.level_data.get("enemies", []):

            painter.drawRect(
                enemy.get("x", 0),
                enemy.get("y", 0),
                enemy.get("width", 50),
                enemy.get("height", 50)
            )

        # ----------------------------------------------------
        # CHAVES
        # ----------------------------------------------------
        painter.setBrush(
            QColor(255, 200, 50)
        )

        for key in self.level_data.get("keys", []):

            painter.drawEllipse(
                key.get("x", 0),
                key.get("y", 0),
                key.get("width", 35),
                key.get("height", 35)
            )

        # ----------------------------------------------------
        # PORTAS
        # ----------------------------------------------------
        painter.setBrush(
            QColor(120, 80, 255)
        )

        for door in self.level_data.get("doors", []):

            painter.drawRect(
                door.get("x", 0),
                door.get("y", 0),
                door.get("width", 60),
                door.get("height", 80)
            )

        # ----------------------------------------------------
        # CHECKPOINTS
        # ----------------------------------------------------
        painter.setBrush(
            QColor(80, 255, 180)
        )

        for checkpoint in self.level_data.get("checkpoints", []):

            painter.drawRect(
                checkpoint.get("x", 0),
                checkpoint.get("y", 0),
                checkpoint.get("width", 45),
                checkpoint.get("height", 60)
            )

        # ----------------------------------------------------
        # POWER-UPS
        # ----------------------------------------------------
        painter.setBrush(
            QColor(80, 255, 255)
        )

        for powerup in self.level_data.get("powerups", []):

            painter.drawEllipse(
                powerup.get("x", 0),
                powerup.get("y", 0),
                powerup.get("width", 35),
                powerup.get("height", 35)
            )

        # ----------------------------------------------------
        # DESTAQUE DO OBJETO SELECIONADO
        # ----------------------------------------------------
        if self.selected_item:

            painter.setPen(
                QColor(255, 255, 255)
            )

            painter.setBrush(
                Qt.BrushStyle.NoBrush
            )

            x = self.selected_item.get("x", 0)
            y = self.selected_item.get("y", 0)

            width = self.selected_item.get(
                "width",
                35
            )

            height = self.selected_item.get(
                "height",
                35
            )

            if self.selected_category == "coins":
                width = 35
                height = 35

            painter.drawRect(
                x - 3,
                y - 3,
                width + 6,
                height + 6
            )


# ============================================================
# JANELA PRINCIPAL DO EDITOR
# ============================================================
class LevelEditor(QMainWindow):

    def __init__(self):
        super().__init__()

        # ----------------------------------------------------
        # JANELA
        # ----------------------------------------------------
        self.setWindowTitle(
            "NexForge Level Editor"
        )

        self.resize(
            1200,
            800
        )

        # Dados da fase
        self.level_data = None
        self.current_file = None

        # ----------------------------------------------------
        # WIDGET PRINCIPAL
        # ----------------------------------------------------
        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        main_layout = QHBoxLayout()

        central_widget.setLayout(
            main_layout
        )

        # ====================================================
        # PAINEL ESQUERDO
        # ====================================================
        side_panel = QWidget()

        side_layout = QVBoxLayout()

        side_panel.setLayout(
            side_layout
        )

        # Título
        self.title_label = QLabel(
            "NexForge Level Editor"
        )

        side_layout.addWidget(
            self.title_label
        )

        # Botão abrir
        self.open_button = QPushButton(
            "Abrir fase JSON"
        )

        self.open_button.clicked.connect(
            self.open_level
        )

        side_layout.addWidget(
            self.open_button
        )

        # Botão salvar
        self.save_button = QPushButton(
            "Salvar fase"
        )

        self.save_button.clicked.connect(
            self.save_level
        )

        side_layout.addWidget(
            self.save_button
        )

        # Lista de objetos
        self.object_list = QListWidget()

        side_layout.addWidget(
            self.object_list
        )

        # ====================================================
        # CANVAS
        # ====================================================
        self.canvas = LevelCanvas()

        self.canvas.on_object_selected = (
            self.on_canvas_object_selected
        )

        # Scroll
        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            False
        )

        self.scroll_area.setWidget(
            self.canvas
        )

        # ====================================================
        # INSPECTOR
        # ====================================================
        inspector_panel = QWidget()

        inspector_layout = QVBoxLayout()

        inspector_panel.setLayout(
            inspector_layout
        )

        inspector_title = QLabel(
            "Inspector"
        )

        inspector_layout.addWidget(
            inspector_title
        )

        form_layout = QFormLayout()

        inspector_layout.addLayout(
            form_layout
        )

        # ----------------------------------------------------
        # X
        # ----------------------------------------------------
        self.x_input = QSpinBox()

        self.x_input.setRange(
            -1000000,
            1000000
        )

        form_layout.addRow(
            "X:",
            self.x_input
        )

        # ----------------------------------------------------
        # Y
        # ----------------------------------------------------
        self.y_input = QSpinBox()

        self.y_input.setRange(
            -1000000,
            1000000
        )

        form_layout.addRow(
            "Y:",
            self.y_input
        )

        # ----------------------------------------------------
        # WIDTH
        # ----------------------------------------------------
        self.width_input = QSpinBox()

        self.width_input.setRange(
            1,
            1000000
        )

        form_layout.addRow(
            "Width:",
            self.width_input
        )

        # ----------------------------------------------------
        # HEIGHT
        # ----------------------------------------------------
        self.height_input = QSpinBox()

        self.height_input.setRange(
            1,
            1000000
        )

        form_layout.addRow(
            "Height:",
            self.height_input
        )

        # Objeto sendo editado
        self.inspector_item = None

        # Detecta alterações
        self.x_input.valueChanged.connect(
            self.update_object_from_inspector
        )

        self.y_input.valueChanged.connect(
            self.update_object_from_inspector
        )

        self.width_input.valueChanged.connect(
            self.update_object_from_inspector
        )

        self.height_input.valueChanged.connect(
            self.update_object_from_inspector
        )

        # ====================================================
        # MONTA LAYOUT PRINCIPAL
        # ====================================================
        main_layout.addWidget(
            side_panel,
            1
        )

        main_layout.addWidget(
            self.scroll_area,
            4
        )

        main_layout.addWidget(
            inspector_panel,
            1
        )

    # ========================================================
    # ABRIR FASE
    # ========================================================
    def open_level(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir fase",
            "levels",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.level_data = json.load(
                file
            )

        self.current_file = file_path

        # Limpa Inspector
        self.update_inspector(None)

        # Atualiza lista
        self.refresh_object_list()

        # Envia fase para canvas
        self.canvas.set_level_data(
            self.level_data
        )

    # ========================================================
    # SALVAR FASE
    # ========================================================
    def save_level(self):

        if not self.level_data:
            return

        if not self.current_file:
            return

        with open(
            self.current_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                self.level_data,
                file,
                indent=4,
                ensure_ascii=False
            )

    # ========================================================
    # ATUALIZA LISTA DE OBJETOS
    # ========================================================
    def refresh_object_list(self):

        self.object_list.clear()

        if not self.level_data:
            return

        # ----------------------------------------------------
        # PLAYER
        # ----------------------------------------------------
        player = self.level_data.get(
            "player",
            None
        )

        if player:

            self.object_list.addItem(
                f"player - x:{player.get('x')} y:{player.get('y')}"
            )

        # ----------------------------------------------------
        # OUTROS OBJETOS
        # ----------------------------------------------------
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

            items = self.level_data.get(
                category,
                []
            )

            for index, item in enumerate(items):

                self.object_list.addItem(
                    f"{category}[{index}] - "
                    f"x:{item.get('x')} "
                    f"y:{item.get('y')}"
                )

    # ========================================================
    # OBJETO SELECIONADO NO CANVAS
    # ========================================================
    def on_canvas_object_selected(
        self,
        category,
        index,
        item
    ):

        # ----------------------------------------------------
        # NENHUM OBJETO
        # ----------------------------------------------------
        if category is None:

            self.object_list.clearSelection()

            self.update_inspector(
                None
            )

            return

        # Atualiza Inspector
        self.update_inspector(
            item
        )

        # ----------------------------------------------------
        # PLAYER
        # ----------------------------------------------------
        if category == "player":

            self.object_list.setCurrentRow(
                0
            )

            return

        # ----------------------------------------------------
        # OUTROS OBJETOS
        # ----------------------------------------------------
        categories = [
            "blocks",
            "coins",
            "keys",
            "doors",
            "checkpoints",
            "enemies",
            "powerups"
        ]

        # Se houver player, linha 0 pertence a ele
        row = (
            1
            if self.level_data.get("player")
            else 0
        )

        for cat in categories:

            items = self.level_data.get(
                cat,
                []
            )

            for i, _ in enumerate(items):

                if (
                    cat == category
                    and i == index
                ):

                    self.object_list.setCurrentRow(
                        row
                    )

                    return

                row += 1

    # ========================================================
    # ATUALIZA INSPECTOR
    # ========================================================
    def update_inspector(self, item):

        self.inspector_item = item

        # Impede que valueChanged seja executado
        # enquanto atualizamos os campos.
        self.x_input.blockSignals(True)
        self.y_input.blockSignals(True)
        self.width_input.blockSignals(True)
        self.height_input.blockSignals(True)

        # ----------------------------------------------------
        # NENHUM OBJETO SELECIONADO
        # ----------------------------------------------------
        if not item:

            self.x_input.setValue(0)
            self.y_input.setValue(0)

            self.width_input.setValue(1)
            self.height_input.setValue(1)

        # ----------------------------------------------------
        # OBJETO SELECIONADO
        # ----------------------------------------------------
        else:

            self.x_input.setValue(
                item.get("x", 0)
            )

            self.y_input.setValue(
                item.get("y", 0)
            )

            self.width_input.setValue(
                item.get("width", 35)
            )

            self.height_input.setValue(
                item.get("height", 35)
            )

        # Libera os sinais novamente
        self.x_input.blockSignals(False)
        self.y_input.blockSignals(False)
        self.width_input.blockSignals(False)
        self.height_input.blockSignals(False)

    # ========================================================
    # ALTERAÇÃO MANUAL PELO INSPECTOR
    # ========================================================
    def update_object_from_inspector(self):

        if not self.inspector_item:
            return

        self.inspector_item["x"] = (
            self.x_input.value()
        )

        self.inspector_item["y"] = (
            self.y_input.value()
        )

        self.inspector_item["width"] = (
            self.width_input.value()
        )

        self.inspector_item["height"] = (
            self.height_input.value()
        )

        # Atualiza mapa
        self.canvas.update()

        # Atualiza lista
        self.refresh_object_list()


# ============================================================
# EXECUTA O EDITOR
# ============================================================
if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    editor = LevelEditor()

    editor.show()

    sys.exit(
        app.exec()
    )