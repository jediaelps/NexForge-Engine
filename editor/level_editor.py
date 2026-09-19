# Importa módulos do sistema
import sys
import json
from pathlib import Path

# Importa componentes do PySide6
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QTreeWidget,
    QToolButton,
    QButtonGroup,
    QHBoxLayout,
    QScrollArea,
    QSpinBox,
    QFormLayout,
    QComboBox
)

from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt


# ============================================================
# CANVAS VISUAL DO MAPA
# ============================================================
class LevelCanvas(QWidget):

    HANDLE_SIZE = 10
    MIN_OBJECT_SIZE = 10

    def __init__(self):
        super().__init__()

        self.level_data = None
        self.setMinimumSize(1200, 800)

        # Objeto selecionado
        self.selected_item = None
        self.selected_category = None
        self.selected_index = None

        # Callback para LevelEditor
        self.on_object_selected = None

        # Movimento
        self.dragging_object = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Resize
        self.resizing_object = False
        self.active_handle = None

        # Snapshot do retângulo no INÍCIO do resize.
        # Isso mantém a borda oposta fixa durante todo o arrasto.
        self.resize_start_x = 0
        self.resize_start_y = 0
        self.resize_start_width = 0
        self.resize_start_height = 0
        self.resize_start_right = 0
        self.resize_start_bottom = 0

        # Para detectar movimento do mouse mesmo sem clicar
        self.setMouseTracking(True)

        # Ferramenta ativa
        self.active_tool = "select"
        self.on_object_deleted = None
        self.on_object_created = None
        self.create_category = "blocks"

    # ========================================================
    # TAMANHO REAL DO OBJETO
    # ========================================================
    def get_object_rect(self, item, category=None):

        x = item.get("x", 0)
        y = item.get("y", 0)

        # Defaults temporários para objetos antigos
        if category == "player":
            width = item.get("width", 50)
            height = item.get("height", 50)

        elif category == "blocks":
            width = item.get("width", 80)
            height = item.get("height", 80)

        elif category == "enemies":
            width = item.get("width", 50)
            height = item.get("height", 50)

        elif category == "doors":
            width = item.get("width", 60)
            height = item.get("height", 80)

        elif category == "checkpoints":
            width = item.get("width", 45)
            height = item.get("height", 60)

        else:
            width = item.get("width", 35)
            height = item.get("height", 35)

        return x, y, width, height

    # ========================================================
    # POSIÇÕES DAS 8 ALÇAS
    # ========================================================
    def get_resize_handles(self):

        if self.selected_item is None:
            return {}

        x, y, width, height = self.get_object_rect(
            self.selected_item,
            self.selected_category
        )

        half = self.HANDLE_SIZE / 2

        left = x
        right = x + width
        top = y
        bottom = y + height

        center_x = x + width / 2
        center_y = y + height / 2

        return {
            "top_left": (
                left - half,
                top - half
            ),

            "top": (
                center_x - half,
                top - half
            ),

            "top_right": (
                right - half,
                top - half
            ),

            "right": (
                right - half,
                center_y - half
            ),

            "bottom_right": (
                right - half,
                bottom - half
            ),

            "bottom": (
                center_x - half,
                bottom - half
            ),

            "bottom_left": (
                left - half,
                bottom - half
            ),

            "left": (
                left - half,
                center_y - half
            )
        }

    # ========================================================
    # DESCOBRE SE MOUSE ESTÁ SOBRE UMA ALÇA
    # ========================================================
    def get_handle_at_position(self, mouse_x, mouse_y):

        handles = self.get_resize_handles()

        for handle_name, position in handles.items():

            handle_x, handle_y = position

            if (
                handle_x <= mouse_x <= handle_x + self.HANDLE_SIZE
                and
                handle_y <= mouse_y <= handle_y + self.HANDLE_SIZE
            ):
                return handle_name

        return None

    # ========================================================
    # CURSOR DO MOUSE
    # ========================================================
    def update_mouse_cursor(self, mouse_x, mouse_y):

        if self.selected_item is None:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            return

        handle = self.get_handle_at_position(
            mouse_x,
            mouse_y
        )

        if handle in ("left", "right"):
            self.setCursor(
                Qt.CursorShape.SizeHorCursor
            )

        elif handle in ("top", "bottom"):
            self.setCursor(
                Qt.CursorShape.SizeVerCursor
            )

        elif handle in ("top_left", "bottom_right"):
            self.setCursor(
                Qt.CursorShape.SizeFDiagCursor
            )

        elif handle in ("top_right", "bottom_left"):
            self.setCursor(
                Qt.CursorShape.SizeBDiagCursor
            )

        else:
            self.setCursor(
                Qt.CursorShape.ArrowCursor
            )

    # ========================================================
    # CLIQUE DO MOUSE
    # ========================================================
    def set_create_category(self, category):
        self.create_category = category

    def create_object_at_position(self, mouse_x, mouse_y):
        if not self.level_data:
            return

        category = self.create_category

        # Defaults visuais/compatíveis com o formato atual da demo.
        defaults = {
            "blocks": (80, 80),
            "coins": (35, 35),
            "enemies": (50, 50),
            "keys": (35, 35),
            "doors": (60, 80),
            "checkpoints": (45, 60),
            "powerups": (35, 35),
        }

        width, height = defaults.get(category, (40, 40))

        item = {
            "x": max(0, int(mouse_x - width / 2)),
            "y": max(0, int(mouse_y - height / 2)),
            "width": width,
            "height": height,
            "sprite_path": None,
        }

        # Compatibilidade com o formato que o LevelManager atual carrega.
        if category == "blocks":
            item["color"] = [120, 120, 140]

        elif category == "enemies":
            item["patrol_axis"] = "horizontal"

        items = self.level_data.setdefault(category, [])
        items.append(item)
        index = len(items) - 1

        self.selected_item = item
        self.selected_category = category
        self.selected_index = index
        self.dragging_object = False
        self.resizing_object = False
        self.active_handle = None

        if self.on_object_created:
            self.on_object_created(
                category,
                index,
                item
            )

        self.update()

    def set_active_tool(self, tool_name):
        self.active_tool = tool_name
        self.dragging_object = False
        self.resizing_object = False
        self.active_handle = None

        if tool_name == "select":
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif tool_name == "move":
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        elif tool_name == "create":
            self.setCursor(Qt.CursorShape.CrossCursor)
        elif tool_name == "delete":
            self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.update()

    def find_object_at_position(self, mouse_x, mouse_y):
        if not self.level_data:
            return None, None, None

        player = self.level_data.get("player")
        if player:
            x, y, width, height = self.get_object_rect(player, "player")
            if x <= mouse_x <= x + width and y <= mouse_y <= y + height:
                return player, "player", 0

        categories = [
            "blocks", "coins", "keys", "doors",
            "checkpoints", "enemies", "powerups"
        ]

        for category in categories:
            items = self.level_data.get(category, [])
            for index in range(len(items) - 1, -1, -1):
                item = items[index]
                x, y, width, height = self.get_object_rect(item, category)
                if x <= mouse_x <= x + width and y <= mouse_y <= y + height:
                    return item, category, index

        return None, None, None

    def delete_object_at_position(self, mouse_x, mouse_y):
        item, category, index = self.find_object_at_position(mouse_x, mouse_y)

        if item is None:
            return

        # Por enquanto o Player é estrutural e não é apagado por clique.
        if category == "player":
            return

        items = self.level_data.get(category, [])
        if 0 <= index < len(items):
            del items[index]

        if self.selected_item is item:
            self.selected_item = None
            self.selected_category = None
            self.selected_index = None

        self.dragging_object = False
        self.resizing_object = False
        self.active_handle = None

        if self.on_object_deleted:
            self.on_object_deleted()

        self.update()

    def mousePressEvent(self, event):

        if not self.level_data:
            return

        if event.button() != Qt.MouseButton.LeftButton:
            return

        mouse_x = event.position().x()
        mouse_y = event.position().y()

        # ----------------------------------------------------
        # FERRAMENTAS COM AÇÃO DIRETA
        # ----------------------------------------------------
        if self.active_tool == "delete":
            self.delete_object_at_position(
                mouse_x,
                mouse_y
            )
            return

        if self.active_tool == "create":
            self.create_object_at_position(
                mouse_x,
                mouse_y
            )
            return

        # ----------------------------------------------------
        # PRIMEIRO: VERIFICA RESIZE
        # ----------------------------------------------------
        if (
            self.active_tool == "select"
            and self.selected_item is not None
        ):

            handle = self.get_handle_at_position(
                mouse_x,
                mouse_y
            )

            if handle:

                self.resizing_object = True
                self.active_handle = handle
                self.dragging_object = False

                start_x, start_y, start_width, start_height = (
                    self.get_object_rect(
                        self.selected_item,
                        self.selected_category
                    )
                )

                self.resize_start_x = int(start_x)
                self.resize_start_y = int(start_y)
                self.resize_start_width = int(start_width)
                self.resize_start_height = int(start_height)
                self.resize_start_right = int(start_x + start_width)
                self.resize_start_bottom = int(start_y + start_height)

                return

        # ----------------------------------------------------
        # PLAYER
        # ----------------------------------------------------
        player = self.level_data.get(
            "player",
            {}
        )

        if player:

            x, y, width, height = self.get_object_rect(
                player,
                "player"
            )

            if (
                x <= mouse_x <= x + width
                and
                y <= mouse_y <= y + height
            ):

                self.select_object(
                    "player",
                    0,
                    player,
                    mouse_x,
                    mouse_y
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

        for category in categories:

            items = self.level_data.get(
                category,
                []
            )

            for index in range(
                len(items) - 1,
                -1,
                -1
            ):

                item = items[index]

                x, y, width, height = self.get_object_rect(
                    item,
                    category
                )

                if (
                    x <= mouse_x <= x + width
                    and
                    y <= mouse_y <= y + height
                ):

                    self.select_object(
                        category,
                        index,
                        item,
                        mouse_x,
                        mouse_y
                    )

                    return

        # ----------------------------------------------------
        # CLICOU NO VAZIO
        # ----------------------------------------------------
        self.clear_selection()

    # ========================================================
    # SELECIONA OBJETO
    # ========================================================
    def select_object(
        self,
        category,
        index,
        item,
        mouse_x,
        mouse_y
    ):

        self.selected_item = item
        self.selected_category = category
        self.selected_index = index

        x, y, _, _ = self.get_object_rect(
            item,
            category
        )

        self.dragging_object = True
        self.resizing_object = False
        self.active_handle = None

        self.drag_offset_x = mouse_x - x
        self.drag_offset_y = mouse_y - y

        if self.on_object_selected:

            self.on_object_selected(
                category,
                index,
                item
            )

        self.update()

    # ========================================================
    # LIMPA SELEÇÃO
    # ========================================================
    def clear_selection(self):

        self.selected_item = None
        self.selected_category = None
        self.selected_index = None

        self.dragging_object = False
        self.resizing_object = False
        self.active_handle = None

        if self.on_object_selected:

            self.on_object_selected(
                None,
                None,
                None
            )

        self.update()

    # ========================================================
    # MOVIMENTO DO MOUSE
    # ========================================================
    def mouseMoveEvent(self, event):

        mouse_x = event.position().x()
        mouse_y = event.position().y()

        # ----------------------------------------------------
        # RESIZE
        # ----------------------------------------------------
        if (
            self.resizing_object
            and
            self.selected_item
            and
            event.buttons() & Qt.MouseButton.LeftButton
        ):

            self.resize_selected_object(
                mouse_x,
                mouse_y
            )

            return

        # ----------------------------------------------------
        # MOVIMENTO NORMAL
        # ----------------------------------------------------
        if (
            self.dragging_object
            and
            self.selected_item
            and
            event.buttons() & Qt.MouseButton.LeftButton
        ):

            self.selected_item["x"] = int(
                mouse_x - self.drag_offset_x
            )

            self.selected_item["y"] = int(
                mouse_y - self.drag_offset_y
            )

            self.notify_object_changed()

            self.update()

            return

        # ----------------------------------------------------
        # APENAS HOVER
        # ----------------------------------------------------
        self.update_mouse_cursor(
            mouse_x,
            mouse_y
        )

    # ========================================================
    # REDIMENSIONA OBJETO
    # ========================================================
    def resize_selected_object(
        self,
        mouse_x,
        mouse_y
    ):
        if self.selected_item is None:
            return

        mouse_x = int(mouse_x)
        mouse_y = int(mouse_y)

        start_x = self.resize_start_x
        start_y = self.resize_start_y
        start_right = self.resize_start_right
        start_bottom = self.resize_start_bottom
        min_size = self.MIN_OBJECT_SIZE
        handle = self.active_handle

        new_x = start_x
        new_y = start_y
        new_width = self.resize_start_width
        new_height = self.resize_start_height

        # ----------------------------------------------------
        # HORIZONTAL
        # ----------------------------------------------------
        if handle in ("left", "top_left", "bottom_left"):
            # A borda direita permanece fixa.
            new_x = min(mouse_x, start_right - min_size)
            new_width = start_right - new_x

        elif handle in ("right", "top_right", "bottom_right"):
            # A borda esquerda permanece fixa.
            new_width = max(
                min_size,
                mouse_x - start_x
            )

        # ----------------------------------------------------
        # VERTICAL
        # ----------------------------------------------------
        if handle in ("top", "top_left", "top_right"):
            # A borda inferior permanece fixa.
            new_y = min(mouse_y, start_bottom - min_size)
            new_height = start_bottom - new_y

        elif handle in ("bottom", "bottom_left", "bottom_right"):
            # A borda superior permanece fixa.
            new_height = max(
                min_size,
                mouse_y - start_y
            )

        self.selected_item["x"] = int(new_x)
        self.selected_item["y"] = int(new_y)
        self.selected_item["width"] = int(new_width)
        self.selected_item["height"] = int(new_height)

        self.notify_object_changed()
        self.update()

    # ========================================================
    # AVISA EDITOR QUE OBJETO MUDOU
    # ========================================================
    def notify_object_changed(self):

        if not self.on_object_selected:
            return

        self.on_object_selected(
            self.selected_category,
            self.selected_index,
            self.selected_item
        )

    # ========================================================
    # SOLTA BOTÃO DO MOUSE
    # ========================================================
    def mouseReleaseEvent(self, event):

        if event.button() != Qt.MouseButton.LeftButton:
            return

        self.dragging_object = False
        self.resizing_object = False
        self.active_handle = None

        mouse_x = event.position().x()
        mouse_y = event.position().y()

        self.update_mouse_cursor(
            mouse_x,
            mouse_y
        )

    # ========================================================
    # CARREGA LEVEL
    # ========================================================
    def set_level_data(
        self,
        level_data
    ):

        self.level_data = level_data

        self.selected_item = None
        self.selected_category = None
        self.selected_index = None

        self.dragging_object = False
        self.resizing_object = False
        self.active_handle = None

        world = self.level_data.get(
            "world",
            {}
        )

        world_width = world.get(
            "width",
            1200
        )

        world_height = world.get(
            "height",
            800
        )

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
    # DESENHO
    # ========================================================
    def paintEvent(self, event):

        painter = QPainter(self)

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
                "Nenhuma fase encontrada no projeto."
            )

            return

        # ----------------------------------------------------
        # PLAYER
        # ----------------------------------------------------
        player = self.level_data.get(
            "player",
            {}
        )

        if player:

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(
                QColor(80, 180, 255)
            )

            x, y, width, height = self.get_object_rect(
                player,
                "player"
            )

            painter.drawRect(
                x,
                y,
                width,
                height
            )

        # ----------------------------------------------------
        # BLOCKS
        # ----------------------------------------------------
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(
            QColor(120, 120, 140)
        )

        for item in self.level_data.get(
            "blocks",
            []
        ):

            x, y, width, height = self.get_object_rect(
                item,
                "blocks"
            )

            painter.drawRect(
                x,
                y,
                width,
                height
            )

        # ----------------------------------------------------
        # COINS
        # ----------------------------------------------------
        painter.setBrush(
            QColor(255, 220, 80)
        )

        for item in self.level_data.get(
            "coins",
            []
        ):

            x, y, width, height = self.get_object_rect(
                item,
                "coins"
            )

            painter.drawEllipse(
                x,
                y,
                width,
                height
            )

        # ----------------------------------------------------
        # ENEMIES
        # ----------------------------------------------------
        painter.setBrush(
            QColor(255, 80, 80)
        )

        for item in self.level_data.get(
            "enemies",
            []
        ):

            x, y, width, height = self.get_object_rect(
                item,
                "enemies"
            )

            painter.drawRect(
                x,
                y,
                width,
                height
            )

        # ----------------------------------------------------
        # KEYS
        # ----------------------------------------------------
        painter.setBrush(
            QColor(255, 200, 50)
        )

        for item in self.level_data.get(
            "keys",
            []
        ):

            x, y, width, height = self.get_object_rect(
                item,
                "keys"
            )

            painter.drawEllipse(
                x,
                y,
                width,
                height
            )

        # ----------------------------------------------------
        # DOORS
        # ----------------------------------------------------
        painter.setBrush(
            QColor(120, 80, 255)
        )

        for item in self.level_data.get(
            "doors",
            []
        ):

            x, y, width, height = self.get_object_rect(
                item,
                "doors"
            )

            painter.drawRect(
                x,
                y,
                width,
                height
            )

        # ----------------------------------------------------
        # CHECKPOINTS
        # ----------------------------------------------------
        painter.setBrush(
            QColor(80, 255, 180)
        )

        for item in self.level_data.get(
            "checkpoints",
            []
        ):

            x, y, width, height = self.get_object_rect(
                item,
                "checkpoints"
            )

            painter.drawRect(
                x,
                y,
                width,
                height
            )

        # ----------------------------------------------------
        # POWERUPS
        # ----------------------------------------------------
        painter.setBrush(
            QColor(80, 255, 255)
        )

        for item in self.level_data.get(
            "powerups",
            []
        ):

            x, y, width, height = self.get_object_rect(
                item,
                "powerups"
            )

            painter.drawEllipse(
                x,
                y,
                width,
                height
            )

        # ----------------------------------------------------
        # SELEÇÃO + ALÇAS DE REDIMENSIONAMENTO
        # ----------------------------------------------------
        if self.selected_item is not None:

            x, y, width, height = self.get_object_rect(
                self.selected_item,
                self.selected_category
            )

            # ==============================
            # CONTORNO DO OBJETO
            # ==============================
            painter.setPen(
                QColor(255, 255, 255)
            )

            painter.setBrush(
                Qt.BrushStyle.NoBrush
            )

            painter.drawRect(
                int(x - 2),
                int(y - 2),
                int(width + 4),
                int(height + 4)
            )

            # ==============================
            # ALÇAS DE RESIZE
            # ==============================
            handle_size = self.HANDLE_SIZE

            half = handle_size // 2

            left = int(x)
            right = int(x + width)

            top = int(y)
            bottom = int(y + height)

            center_x = int(x + width / 2)
            center_y = int(y + height / 2)

            handle_positions = [
                # Canto superior esquerdo
                (left - half, top - half),

                # Meio superior
                (center_x - half, top - half),

                # Canto superior direito
                (right - half, top - half),

                # Meio direito
                (right - half, center_y - half),

                # Canto inferior direito
                (right - half, bottom - half),

                # Meio inferior
                (center_x - half, bottom - half),

                # Canto inferior esquerdo
                (left - half, bottom - half),

                # Meio esquerdo
                (left - half, center_y - half)
            ]

            # Borda escura das alças
            painter.setPen(
                QColor(20, 20, 20)
            )

            # Interior branco
            painter.setBrush(
                QColor(255, 255, 255)
            )

            for handle_x, handle_y in handle_positions:

                painter.drawRect(
                    int(handle_x),
                    int(handle_y),
                    int(handle_size),
                    int(handle_size)
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

        # Fases encontradas no projeto atual
        self.project_levels = []

        # ----------------------------------------------------
        # WIDGET PRINCIPAL
        # ----------------------------------------------------
        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        root_layout = QVBoxLayout()
        central_widget.setLayout(root_layout)

        # ====================================================
        # BARRA DE FERRAMENTAS
        # ====================================================
        tools_bar = QHBoxLayout()

        self.tool_buttons = {}
        self.tool_group = QButtonGroup(self)
        self.tool_group.setExclusive(True)

        # Salvar fica como ação global, separado das ferramentas.
        self.save_button = QToolButton()
        self.save_button.setText("💾")
        self.save_button.setToolTip("Salvar fase")
        self.save_button.setMinimumSize(36, 32)
        self.save_button.clicked.connect(
            self.save_level
        )
        tools_bar.addWidget(
            self.save_button
        )
        tools_bar.addSpacing(12)

        tool_specs = [
            ("select", "↖ Select"),
            ("move", "✥ Move"),
            ("create", "＋ Create"),
            ("delete", "⌫ Delete"),
        ]

        for tool_name, label in tool_specs:
            button = QToolButton()
            button.setText(label)
            button.setCheckable(True)
            button.setMinimumHeight(32)
            button.clicked.connect(
                lambda checked=False, name=tool_name:
                    self.set_active_tool(name)
            )
            self.tool_group.addButton(button)
            self.tool_buttons[tool_name] = button
            tools_bar.addWidget(button)

        tools_bar.addSpacing(10)

        self.create_type_label = QLabel(
            "Create type:"
        )
        tools_bar.addWidget(
            self.create_type_label
        )

        self.create_type_combo = QComboBox()

        create_types = [
            ("Block", "blocks"),
            ("Coin", "coins"),
            ("Enemy", "enemies"),
            ("Key", "keys"),
            ("Door", "doors"),
            ("Checkpoint", "checkpoints"),
            ("PowerUp", "powerups"),
        ]

        for label, category in create_types:
            self.create_type_combo.addItem(
                label,
                category
            )

        self.create_type_combo.currentIndexChanged.connect(
            self.on_create_type_changed
        )

        tools_bar.addWidget(
            self.create_type_combo
        )

        # Só aparece quando Create estiver ativo.
        self.create_type_label.setVisible(False)
        self.create_type_combo.setVisible(False)

        tools_bar.addStretch()
        self.tool_buttons["select"].setChecked(True)

        root_layout.addLayout(tools_bar)

        main_layout = QHBoxLayout()
        root_layout.addLayout(main_layout)

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

        # Árvore do projeto / cena
        self.object_list = QTreeWidget()
        self.object_list.setHeaderLabel("Project / Scene")
        self.object_list.setIndentation(18)
        self.object_list.itemClicked.connect(self.on_tree_item_clicked)

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

        self.canvas.on_object_deleted = (
            self.on_canvas_object_deleted
        )

        self.canvas.on_object_created = (
            self.on_canvas_object_created
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

        # Carrega automaticamente as fases existentes do projeto.
        self.load_project_levels()

    # ========================================================
    # FERRAMENTA ATIVA
    # ========================================================
    def set_active_tool(self, tool_name):
        self.canvas.set_active_tool(tool_name)

        creating = tool_name == "create"
        self.create_type_label.setVisible(
            creating
        )
        self.create_type_combo.setVisible(
            creating
        )

        if creating:
            self.on_create_type_changed(
                self.create_type_combo.currentIndex()
            )

    def on_create_type_changed(self, index):
        category = self.create_type_combo.itemData(
            index
        )

        if category:
            self.canvas.set_create_category(
                category
            )

    # ========================================================
    # OBJETO CRIADO PELO CANVAS
    # ========================================================
    def on_canvas_object_created(
        self,
        category,
        index,
        item
    ):
        self.update_inspector(
            item
        )
        self.refresh_object_list()
        self.select_tree_object(
            category,
            index
        )

    # ========================================================
    # OBJETO APAGADO PELO CANVAS
    # ========================================================
    def on_canvas_object_deleted(self):
        self.update_inspector(None)
        self.refresh_object_list()

    # ========================================================
    # LOCALIZA A PASTA LEVELS DO PROJETO
    # ========================================================
    def get_levels_directory(self):
        # Funciona ao executar a partir da raiz do projeto
        # ou diretamente de dentro da pasta editor.
        candidates = [
            Path.cwd() / "levels",
            Path(__file__).resolve().parent.parent / "levels"
        ]

        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                return candidate

        return None

    # ========================================================
    # DESCOBRE E CARREGA AS FASES DO PROJETO
    # ========================================================
    def load_project_levels(self):
        levels_dir = self.get_levels_directory()

        self.project_levels = []

        if levels_dir is None:
            self.refresh_object_list()
            return

        self.project_levels = sorted(
            levels_dir.glob("*.json"),
            key=lambda path: path.name.lower()
        )

        if not self.project_levels:
            self.refresh_object_list()
            return

        # Abre automaticamente a primeira fase.
        self.load_level_file(
            self.project_levels[0]
        )

    # ========================================================
    # CARREGA UM ARQUIVO DE FASE
    # ========================================================
    def load_level_file(self, file_path):
        file_path = Path(file_path)

        if not file_path.exists():
            return

        with file_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            self.level_data = json.load(file)

        self.current_file = str(file_path)

        self.update_inspector(None)

        self.canvas.set_level_data(
            self.level_data
        )

        self.refresh_object_list()

    # ========================================================
    # ABRIR FASE
    # ========================================================
    def open_level(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir fase",
            str(self.get_levels_directory() or Path.cwd()),
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        selected_path = Path(file_path)

        # Se a fase pertence à pasta levels, atualiza a lista do projeto.
        levels_dir = self.get_levels_directory()
        if levels_dir is not None:
            self.project_levels = sorted(
                levels_dir.glob("*.json"),
                key=lambda path: path.name.lower()
            )

        self.load_level_file(
            selected_path
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
        """Reconstrói a árvore lateral sem perder a seleção atual."""
        self.object_list.blockSignals(True)
        self.object_list.clear()

        if not self.level_data:
            self.object_list.blockSignals(False)
            return

        # Import local para manter a alteração concentrada neste arquivo.
        from PySide6.QtWidgets import QTreeWidgetItem

        def make_group(label):
            group = QTreeWidgetItem([label])
            group.setData(0, Qt.ItemDataRole.UserRole, None)
            self.object_list.addTopLevelItem(group)
            return group

        def add_object(parent, label, category, index, item):
            child = QTreeWidgetItem([label])
            child.setData(
                0,
                Qt.ItemDataRole.UserRole,
                {
                    "category": category,
                    "index": index
                }
            )
            parent.addChild(child)
            return child

        # ----------------------------------------------------
        # LEVELS
        # ----------------------------------------------------
        levels_group = make_group("Levels")

        current_resolved = (
            Path(self.current_file).resolve()
            if self.current_file
            else None
        )

        for level_path in self.project_levels:
            level_item = QTreeWidgetItem(
                [level_path.stem]
            )

            level_item.setData(
                0,
                Qt.ItemDataRole.UserRole,
                {
                    "node_type": "level",
                    "path": str(level_path)
                }
            )

            levels_group.addChild(
                level_item
            )

            if (
                current_resolved is not None
                and level_path.resolve() == current_resolved
            ):
                level_item.setSelected(True)

        # Placeholder visual. A criação real entra depois.
        new_level_item = QTreeWidgetItem(
            ["+ New Level"]
        )
        new_level_item.setData(
            0,
            Qt.ItemDataRole.UserRole,
            {
                "node_type": "new_level"
            }
        )
        levels_group.addChild(
            new_level_item
        )

        # ----------------------------------------------------
        # PLAYER
        # ----------------------------------------------------
        player_group = make_group("Player")
        player = self.level_data.get("player")

        if player:
            add_object(
                player_group,
                "Player",
                "player",
                0,
                player
            )

        # ----------------------------------------------------
        # ENEMIES
        # ----------------------------------------------------
        enemies_group = make_group("Enemies")
        for index, item in enumerate(
            self.level_data.get("enemies", [])
        ):
            add_object(
                enemies_group,
                f"Enemy {index + 1}",
                "enemies",
                index,
                item
            )

        # ----------------------------------------------------
        # OBJECTS
        # ----------------------------------------------------
        objects_group = make_group("Objects")

        object_categories = [
            ("coins", "Coin"),
            ("keys", "Key"),
            ("doors", "Door"),
            ("powerups", "PowerUp")
        ]

        for category, display_name in object_categories:
            for index, item in enumerate(
                self.level_data.get(category, [])
            ):
                add_object(
                    objects_group,
                    f"{display_name} {index + 1}",
                    category,
                    index,
                    item
                )

        # ----------------------------------------------------
        # SCENARIO
        # ----------------------------------------------------
        scenario_group = make_group("Scenario")

        scenario_categories = [
            ("blocks", "Block"),
            ("checkpoints", "Checkpoint")
        ]

        for category, display_name in scenario_categories:
            for index, item in enumerate(
                self.level_data.get(category, [])
            ):
                add_object(
                    scenario_group,
                    f"{display_name} {index + 1}",
                    category,
                    index,
                    item
                )

        self.object_list.expandAll()

        # Restaura seleção caso exista.
        if self.canvas.selected_item is not None:
            self.select_tree_object(
                self.canvas.selected_category,
                self.canvas.selected_index
            )

        self.object_list.blockSignals(False)

    # ========================================================
    # PROCURA / SELECIONA OBJETO NA ÁRVORE
    # ========================================================
    def select_tree_object(self, category, index):
        root = self.object_list.invisibleRootItem()

        for group_index in range(root.childCount()):
            group = root.child(group_index)

            for child_index in range(group.childCount()):
                child = group.child(child_index)
                data = child.data(
                    0,
                    Qt.ItemDataRole.UserRole
                )

                if not isinstance(data, dict):
                    continue

                if (
                    data.get("category") == category
                    and data.get("index") == index
                ):
                    self.object_list.setCurrentItem(child)
                    return

    # ========================================================
    # CLIQUE EM UM ITEM DA ÁRVORE
    # ========================================================
    def on_tree_item_clicked(self, tree_item, column):
        data = tree_item.data(
            0,
            Qt.ItemDataRole.UserRole
        )

        if not isinstance(data, dict):
            return

        node_type = data.get("node_type")

        # Troca a fase ativa ao clicar em um Level.
        if node_type == "level":
            level_path = data.get("path")
            if level_path:
                self.load_level_file(
                    level_path
                )
            return

        # + New Level continua reservado para o passo de criação.
        if node_type == "new_level":
            return

        category = data.get("category")
        index = data.get("index")

        # Sempre resolve o objeto a partir do level_data atual.
        # A árvore guarda apenas a identidade (categoria + índice).
        if category == "player":
            item = self.level_data.get("player")
        else:
            items = self.level_data.get(category, [])
            if index is None or not (0 <= index < len(items)):
                return
            item = items[index]

        if item is None:
            return

        # Seleciona no Canvas sem iniciar drag.
        self.canvas.selected_item = item
        self.canvas.selected_category = category
        self.canvas.selected_index = index
        self.canvas.dragging_object = False
        self.canvas.resizing_object = False
        self.canvas.active_handle = None

        self.update_inspector(item)
        self.canvas.update()

    # ========================================================
    # OBJETO SELECIONADO NO CANVAS
    # ========================================================
    def on_canvas_object_selected(
        self,
        category,
        index,
        item
    ):
        if category is None:
            self.object_list.clearSelection()
            self.update_inspector(None)
            return

        self.update_inspector(item)

        # Sincroniza Canvas -> árvore.
        self.select_tree_object(
            category,
            index
        )

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