import sys
import os
import json
import base64
import requests
import urllib3
import time
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTextEdit, 
                             QComboBox, QMessageBox, QCheckBox, QTabWidget,
                             QGroupBox, QRadioButton, QButtonGroup, QSplitter,
                             QFrame, QSpacerItem, QSizePolicy, QProgressBar,QGridLayout, QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QSize, QSortFilterProxyModel
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPixmap, QCursor, QStandardItemModel, QStandardItem


class ChampionFilterProxyModel(QSortFilterProxyModel):
    """Modello proxy personalizzato per il filtraggio avanzato dei campioni"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.acronyms = {
            # Acronimi comuni in League of Legends
            "MF": "Miss Fortune",
            "TF": "Twisted Fate",
            "ASol": "Aurelion Sol",
            "J4": "Jarvan IV",
            "AP": "Aurelion Pantheon",
            "WW": "Warwick",
            "LB": "LeBlanc",
            "GP": "Gangplank",
            "Mundo": "Dr. Mundo",
            "TK": "Tahm Kench",
            "K6": "Kha'Zix",
            "KZ": "Kha'Zix",
            # Aggiungere altri acronimi secondo le necessità
        }
        
    def filterAcceptsRow(self, source_row, source_parent):
        """Sovrascrittura del metodo di filtraggio standard per supportare:
           1. Corrispondenza parziale (es: "Kat" trova "Katarina")
           2. Acronimi (es: "MF" trova "Miss Fortune")
        """
        source_model = self.sourceModel()
        index = source_model.index(source_row, self.filterKeyColumn(), source_parent)
        
        if not index.isValid():
            return False
            
        # Recupero del testo dell'elemento attuale
        champion_name = source_model.data(index, Qt.DisplayRole)
        if not champion_name:
            return False
            
        # Testo di ricerca
        filter_text = self.filterRegExp().pattern().lower()
        
        # Se la ricerca è vuota, mostra tutti i campioni
        if not filter_text:
            return True
            
        # 1. Verifica diretta con corrispondenza parziale standard
        if filter_text.lower() in champion_name.lower():
            return True
            
        # 2. Verifica degli acronimi
        for acronym, full_name in self.acronyms.items():
            if filter_text.lower() == acronym.lower() and full_name.lower() in champion_name.lower():
                return True
                
        # 3. Verifica avanzata: iniziali
        if self._matches_initials(filter_text, champion_name):
            return True
            
        return False
        
    def _matches_initials(self, filter_text, champion_name):
        """Verifica se il testo di filtraggio corrisponde alle iniziali del nome del campione
           Per esempio, "MF" dovrebbe corrispondere a "Miss Fortune" anche senza definizione esplicita
        """
        words = champion_name.split()
        
        # Se il campione ha più parole nel suo nome
        if len(words) > 1:
            initials = ''.join([word[0].lower() for word in words if word])
            if filter_text.lower() == initials:
                return True
                
        return False
    

class StyledButton(QPushButton):
    """Custom styled button class"""
    def __init__(self, text, color_scheme="default"):
        super().__init__(text)
        self.setFixedHeight(36)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        if color_scheme == "default":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0A1428;
                    color: #C8AA6E;
                    border: 1px solid #C8AA6E;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1E2328;
                    border: 1px solid #F0E6D2;
                }
                QPushButton:pressed {
                    background-color: #1E2328;
                    border: 1px solid #C8AA6E;
                }
            """)
        elif color_scheme == "blue":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0A323C;
                    color: #FFFFFF;
                    border: 1px solid #0AC8B9;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0A6270;
                    border: 1px solid #0AC8B9;
                }
                QPushButton:pressed {
                    background-color: #0A323C;
                    border: 1px solid #0AC8B9;
                }
            """)
        elif color_scheme == "red":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4B1113;
                    color: #FFFFFF;
                    border: 1px solid #CB2E2E;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #761C1C;
                    border: 1px solid #CB2E2E;
                }
                QPushButton:pressed {
                    background-color: #4B1113;
                    border: 1px solid #CB2E2E;
                }
            """)
        elif color_scheme == "green":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #153626;
                    color: #FFFFFF;
                    border: 1px solid #3CB371;
                    border-radius: 4px;
                    padding: 8px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1D4B35;
                    border: 1px solid #3CB371;
                }
                QPushButton:pressed {
                    background-color: #153626;
                    border: 1px solid #3CB371;
                }
            """)


class LOLChampionSelectApp(QWidget):
    # Variabili iniziali nella classe LOLChampionSelectApp
    def __init__(self):
        super().__init__()
        self.base_url = None
        self.auth_header = None
        self.lockfile_path = self.get_lockfile_path()
        self.last_session_state = None
        self.is_connected = False
        self.champions_data = {}  # Store champions data for reference
        self.summoner_id = None   # Store summoner ID for verification
        self.game_mode = "CLASSIC"  # Default game mode
        
        # Auto ban variables
        self.auto_ban_enabled = False  # Flag per abilitare/disabilitare l'autoban
        self.ban_action_active = False  # Flag per controllare se l'azione di ban è attiva
        self.ban_completed = False
        self.ban_timer = QTimer(self)
        self.ban_timer.timeout.connect(self.execute_auto_ban)
        self.ban_timer.setSingleShot(True)
        
        # Auto pick variables - NUOVE
        self.pick_completed = False
        self.pick_timer = QTimer(self)
        self.pick_timer.timeout.connect(self.execute_auto_pick)
        self.pick_timer.setSingleShot(True)
        
        # Auto message variables
        self.message_completed = False
        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.send_chat_message)
        self.message_timer.setSingleShot(True)

        # Set the application style
        self.setStyleSheet("""
            QWidget {
                background-color: #0A1428;
                color: #F0E6D2;
                font-family: 'Segoe UI', sans-serif;
                font-size: 10pt;
            }
            QGroupBox {
                border: 1px solid #3C3C3C;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 8px;
                background-color: #091428;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
                color: #C8AA6E;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                background-color: #091428;
            }
            QTabBar::tab {
                background-color: #0A1428;
                color: #C8AA6E;
                border: 1px solid #3C3C3C;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 4px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #091428;
                border-bottom: 2px solid #C8AA6E;
            }
            QLabel {
                color: #F0E6D2;
            }
            QLineEdit, QComboBox, QTextEdit {
                background-color: #1E2328;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                padding: 6px;
                color: #F0E6D2;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border: 1px solid #C8AA6E;
            }
            QCheckBox {
                color: #F0E6D2;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3C3C3C;
                border-radius: 3px;
                background-color: #1E2328;
            }
            QCheckBox::indicator:checked {
                background-color: #C8AA6E;
                border: 1px solid #C8AA6E;
                image: url(check.png);
            }
            QProgressBar {
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                background-color: #1E2328;
                text-align: center;
                color: #F0E6D2;
            }
            QProgressBar::chunk {
                background-color: #0A8270;
                border-radius: 3px;
            }
            QScrollBar:vertical {
                border: none;
                background: #1E2328;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3C3C3C;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QComboBox QAbstractItemView {
                background-color: #1E2328;
                border: 1px solid #3C3C3C;
                selection-background-color: #C8AA6E;
                selection-color: #000000;
            }
        """)


        # Initialize UI
        self.initUI()
        
        # Auto connect at startup
        self.auto_connect()
        
        # Timer for checking champion select
        self.champion_select_timer = QTimer(self)
        self.champion_select_timer.timeout.connect(self.check_champion_select)
        self.champion_select_timer.start(2000)  # Check every 2 secondsmessage(f"❌ Error: {str(e)}")
        

    def get_lockfile_path(self):
        """Find the LCU lockfile path"""
        possible_paths = [
            r"C:/Riot Games/League of Legends/lockfile",
            os.path.expanduser('~/.config/Riot Games/League of Legends/lockfile'),  # Linux
            os.path.expanduser('~/Library/Application Support/Riot Games/League of Legends/lockfile'),  # MacOS
            os.path.join(os.getenv('LOCALAPPDATA', ''), 'Riot Games', 'League of Legends', 'lockfile'),  # Windows
            r"C:\Riot Games\League of Legends\lockfile",  # Alternative Windows path
            os.path.join(os.getenv('USERPROFILE', ''), 'AppData', 'Local', 'Riot Games', 'League of Legends', 'lockfile'),
            r"C:\Program Files\Riot Games\League of Legends\lockfile",
            r"D:\Riot Games\League of Legends\lockfile"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None

    def parse_lockfile(self):
        """Parse the LCU lockfile to get connection details"""
        if not self.lockfile_path:
            self.log_message("❌ Lockfile not found! Is League of Legends running?")
            return None, None

        try:
            with open(self.lockfile_path, 'r') as f:
                lockfile_content = f.read().strip()
            
            # Lockfile format: name:pid:port:password:protocol
            parts = lockfile_content.split(':')
            if len(parts) < 5:
                self.log_message("❌ Invalid lockfile format!")
                return None, None

            port = parts[2]
            password = parts[3]
            return port, password
        
        except Exception as e:
            self.log_message(f"❌ Error reading lockfile: {str(e)}")
            return None, None

    def initUI(self):
        self.setWindowTitle('League of Legends Champion Select Manager')
        self.setGeometry(100, 100, 800, 700)
        self.setMinimumSize(800, 600)  # Impostazione di una dimensione minima per l'app
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header section with gold styling (fuori dallo scroll area)
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setStyleSheet("background-color: #091428; border: 1px solid #C8AA6E; border-radius: 8px; padding: 10px;")
        header_layout = QHBoxLayout(header_frame)
        
        # App logo/title
        title_label = QLabel("CHAMPION SELECT MANAGER")
        title_label.setStyleSheet("color: #C8AA6E; font-size: 18px; font-weight: bold; letter-spacing: 1px;")
        
        # Connection status with LoL styling
        self.connection_status = QLabel('DISCONNECTED')
        self.connection_status.setStyleSheet("""
            font-weight: bold;
            color: #CB2E2E;
            padding: 8px;
            border-radius: 4px;
            background: #1E2328;
            border: 1px solid #CB2E2E;
        """)
        self.connection_status.setAlignment(Qt.AlignCenter)
        self.connection_status.setFixedWidth(200)
        
        # Reconnect button with LoL styling
        reconnect_btn = StyledButton('🔄 RECONNECT', "blue")
        reconnect_btn.clicked.connect(self.auto_connect)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.connection_status)
        header_layout.addWidget(reconnect_btn)
        
        main_layout.addWidget(header_frame)

        # NOVITÀ: Creare un widget scorrevole principale
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(5, 5, 5, 5)  # Margini ridotti
        
        # Creare la QScrollArea principale
        main_scroll_area = QScrollArea()
        main_scroll_area.setWidgetResizable(True)
        main_scroll_area.setWidget(scroll_widget)
        main_scroll_area.setFrameShape(QFrame.NoFrame)
        main_scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #0A1428;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3C3C3C;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Create tab widget for better organization
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                min-width: 120px;
                height: 30px;
            }
        """)
        
        # -------------------------------------------------------------------------
        # CHAMPION SELECT TAB
        # -------------------------------------------------------------------------
        champ_select_tab = QWidget()
        champ_select_layout = QVBoxLayout(champ_select_tab)
        champ_select_layout.setSpacing(10)
        
        # Champion Selection with improved layout
        selection_group = QGroupBox("Champion Selection")
        selection_layout = QVBoxLayout()
        selection_layout.setSpacing(10)
        
        # Top section for champion action buttons
        action_buttons_layout = QHBoxLayout()
        action_buttons_layout.setContentsMargins(0, 0, 0, 0)  # Riduce i margini
        action_buttons_layout.setSpacing(8)  # Riduce lo spacing
        
        # Load champions button
        load_champions_btn = StyledButton('📋 Load Champions')
        load_champions_btn.setFixedHeight(40)  # Riduzione altezza da 36 a 32
        load_champions_btn.clicked.connect(self.load_champions)
        action_buttons_layout.addWidget(load_champions_btn)
        
        # Status indicator
        self.champions_loaded_label = QLabel("Champions: Not Loaded")
        self.champions_loaded_label.setStyleSheet("color: #CB2E2E; padding: 8px; border-radius: 4px; background: #1E2328;")
        self.champions_loaded_label.setAlignment(Qt.AlignCenter)
        self.champions_loaded_label.setFixedHeight(36)  # Imposta altezza fissa
        action_buttons_layout.addWidget(self.champions_loaded_label)
        
        # Game phase status
        self.game_phase_label = QLabel("Phase: Not in Champion Select")
        self.game_phase_label.setStyleSheet("color: #F0E6D2; padding: 8px; border-radius: 4px; background: #1E2328;")
        self.game_phase_label.setAlignment(Qt.AlignCenter)
        self.game_phase_label.setFixedHeight(36)  # Imposta altezza fissa
        action_buttons_layout.addWidget(self.game_phase_label)
        
        selection_layout.addLayout(action_buttons_layout)
        selection_layout.setSpacing(8)  # Ridotto spacing generale
        
        # Champion pick section with improved visual
        pick_frame = QFrame()
        pick_frame.setStyleSheet("background-color: #082133; border-radius: 8px; padding: 10px;")
        pick_layout = QVBoxLayout(pick_frame)
        pick_layout.setContentsMargins(8, 8, 8, 8)  # Ridotti i margini
        pick_layout.setSpacing(6)  # Ridotto spacing
        
        pick_title = QLabel("👑 PICK CHAMPION")
        pick_title.setStyleSheet("color: #3CB371; font-weight: bold; font-size: 12pt;")
        pick_layout.addWidget(pick_title)
        
        # Creare i modelli per i campioni e i ban
        self.champion_list_model = QStandardItemModel()
        self.ban_list_model = QStandardItemModel()

        # Creare i modelli proxy per il filtraggio
        self.champion_filter_model = ChampionFilterProxyModel()
        self.champion_filter_model.setSourceModel(self.champion_list_model)
        self.champion_filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        
        self.ban_filter_model = ChampionFilterProxyModel()
        self.ban_filter_model.setSourceModel(self.ban_list_model)
        self.ban_filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

        pick_combo_layout = QHBoxLayout()
        self.champion_combo = QComboBox()
        self.champion_combo.setEditable(True)
        self.champion_combo.setModel(self.champion_filter_model)
        self.champion_combo.setPlaceholderText('Select Champion to Pick')
        self.champion_combo.setFixedHeight(36)
        self.champion_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 11pt;
            }
        """)

        self.champion_combo.lineEdit().textEdited.connect(self._filter_champion_combo)
    
        
        pick_champion_btn = StyledButton('PICK CHAMPION', "green")
        pick_champion_btn.clicked.connect(self.pick_champion)
        
        pick_combo_layout.addWidget(self.champion_combo, 4)
        pick_combo_layout.addWidget(pick_champion_btn, 1)
        
        pick_layout.addLayout(pick_combo_layout)
        
        # NUOVO: Aggiungi opzione Auto Pick
        auto_pick_layout = QHBoxLayout()
        
        self.auto_pick_checkbox = QCheckBox('Enable Auto Pick')
        self.auto_pick_checkbox.setStyleSheet("font-weight: bold;")
        
        auto_pick_layout.addWidget(self.auto_pick_checkbox)
        
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel('Pick Delay (sec):'))
        self.pick_delay_input = QLineEdit('2')
        self.pick_delay_input.setFixedWidth(50)
        delay_layout.addWidget(self.pick_delay_input)
        
        auto_pick_layout.addLayout(delay_layout)
        auto_pick_layout.addStretch()
        
        pick_layout.addLayout(auto_pick_layout)
        selection_layout.addWidget(pick_frame)
        
        # Champion ban section with improved visual
        ban_frame = QFrame()
        ban_frame.setStyleSheet("background-color: #230E18; border-radius: 8px; padding: 10px;")
        ban_layout = QVBoxLayout(ban_frame)
        ban_layout.setContentsMargins(8, 8, 8, 8)  # Ridotti i margini
        ban_layout.setSpacing(6)  # Ridotto spacing
        
        ban_title = QLabel("⛔ BAN CHAMPION")
        ban_title.setStyleSheet("color: #CB2E2E; font-weight: bold; font-size: 12pt;")
        ban_layout.addWidget(ban_title)
        
        ban_combo_layout = QHBoxLayout()
        self.ban_combo = QComboBox()
        self.ban_combo.setEditable(True)
        self.ban_combo.setModel(self.ban_filter_model)
        self.ban_combo.setPlaceholderText('Select Champion to Ban')
        self.ban_combo.setFixedHeight(36)
        self.ban_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 11pt;
            }
        """)

        self.ban_combo.lineEdit().textEdited.connect(self._filter_ban_combo)
        
        ban_champion_btn = StyledButton('BAN CHAMPION', "red")
        ban_champion_btn.clicked.connect(self.ban_champion)
        
        ban_combo_layout.addWidget(self.ban_combo, 4)
        ban_combo_layout.addWidget(ban_champion_btn, 1)
        
        ban_layout.addLayout(ban_combo_layout)
        
        # Auto ban settings section
        auto_ban_layout = QHBoxLayout()
        
        self.auto_ban_checkbox = QCheckBox('Enable Auto Ban')
        self.auto_ban_checkbox.setStyleSheet("font-weight: bold;")
        
        auto_ban_layout.addWidget(self.auto_ban_checkbox)
        
        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel('Ban Delay (sec):'))
        self.ban_delay_input = QLineEdit('3')
        self.ban_delay_input.setFixedWidth(50)
        delay_layout.addWidget(self.ban_delay_input)
        
        auto_ban_layout.addLayout(delay_layout)
        auto_ban_layout.addStretch()
        
        ban_layout.addLayout(auto_ban_layout)
        selection_layout.addWidget(ban_frame)
        
        selection_group.setLayout(selection_layout)
        champ_select_layout.addWidget(selection_group)
        
        # Add to the Champion Select tab
        self.tabs.addTab(champ_select_tab, "Champion Select")
        
        # -------------------------------------------------------------------------
        # AUTO MESSAGE TAB
        # -------------------------------------------------------------------------
        auto_message_tab = QWidget()
        auto_message_layout = QVBoxLayout(auto_message_tab)
        auto_message_layout.setSpacing(15)  # Maggiore spaziatura tra i componenti
        
        # Header informativo (compatto)
        message_header = QFrame()
        message_header.setStyleSheet("background-color: #091C2E; border-radius: 8px; padding: 10px;")
        message_header_layout = QHBoxLayout(message_header)
        
        # Icona e titolo insieme
        title_layout = QHBoxLayout()
        message_icon = QLabel("💬")
        message_icon.setStyleSheet("font-size: 18pt; color: #0AC8B9;")
        
        message_title = QLabel("AUTO MESSAGE")
        message_title.setStyleSheet("color: #0AC8B9; font-weight: bold; font-size: 14pt;")
        
        title_layout.addWidget(message_icon)
        title_layout.addWidget(message_title)
        title_layout.addStretch()
        
        message_desc = QLabel("Configure messages to be sent automatically when entering champion select")
        message_desc.setStyleSheet("color: #F0E6D2; font-size: 10pt;")
        message_desc.setWordWrap(True)
        
        message_header_layout.addLayout(title_layout)
        message_header_layout.addWidget(message_desc, 1)
        
        auto_message_layout.addWidget(message_header)
        
        # Gruppo per le impostazioni del messaggio
        message_group = QGroupBox("Message Settings")
        message_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3C3C3C;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 8px;
                background-color: #091428;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
                color: #0AC8B9;
                font-weight: bold;
            }
        """)
        
        message_layout = QVBoxLayout(message_group)
        message_layout.setSpacing(15)
        
        # Checkbox per abilitare il messaggio automatico
        self.auto_message_checkbox = QCheckBox('Enable Auto Message')
        self.auto_message_checkbox.setStyleSheet("font-weight: bold; font-size: 11pt; color: #0AC8B9;")
        message_layout.addWidget(self.auto_message_checkbox)
        
        # Descrizione opzionale del funzionamento
        message_info = QLabel("This message will be sent automatically when you enter champion select")
        message_info.setStyleSheet("color: #8A8A8A; font-style: italic; font-size: 9pt;")
        message_layout.addWidget(message_info)
        
        # Input messaggio
        self.auto_message_input = QLineEdit()
        self.auto_message_input.setPlaceholderText('Enter your message here')
        self.auto_message_input.setStyleSheet("""
            QLineEdit {
                background-color: #1E2328;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                padding: 10px;
                color: #F0E6D2;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 1px solid #0AC8B9;
            }
        """)
        self.auto_message_input.setFixedHeight(40)
        message_layout.addWidget(self.auto_message_input)
        
        # Bottone di invio
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        send_msg_btn = StyledButton('Send Message Now', "blue")
        send_msg_btn.clicked.connect(lambda: self.send_chat_message(self.auto_message_input.text()))
        buttons_layout.addWidget(send_msg_btn)
        
        message_layout.addLayout(buttons_layout)
        
        # Aggiungi il gruppo al layout
        auto_message_layout.addWidget(message_group)
        
        # Sezione template messaggi con layout migliorato
        templates_group = QGroupBox("Message Templates")
        templates_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #3C3C3C;
                border-radius: 8px;
                margin-top: 14px;
                padding-top: 8px;
                background-color: #091428;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
                color: #0AC8B9;
                font-weight: bold;
            }
        """)
        
        templates_layout = QVBoxLayout(templates_group)
        templates_layout.setSpacing(10)
        
        # Descrizione secondaria
        templates_description = QLabel("Click on a template to use it")
        templates_description.setStyleSheet("color: #8A8A8A; font-style: italic; font-size: 9pt;")
        templates_description.setAlignment(Qt.AlignCenter)
        templates_layout.addWidget(templates_description)
        
        # Grid layout per i bottoni dei template - 4 righe x 2 colonne
        template_buttons_layout = QGridLayout()
        template_buttons_layout.setSpacing(10)
        template_buttons_layout.setContentsMargins(5, 5, 5, 5)
        
        # Funzione per creare bottoni template
        def create_template_button(text, message):
            btn = QPushButton(text)
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #0A1428;
                    color: #F0E6D2;
                    border: 1px solid #0AC8B9;
                    border-radius: 4px;
                    padding: 8px;
                    text-align: left;
                    font-size: 10pt;
                }
                QPushButton:hover {
                    background-color: #0A323C;
                    border: 1px solid #00FFDD;
                }
            """)
            btn.clicked.connect(lambda: self.auto_message_input.setText(message))
            return btn
        
        # Creare tutti i bottoni template
        template1_btn = create_template_button("👋 Greeting", "Hello team! Let's have a good game!")
        template2_btn = create_template_button("🧠 Strategy", "I prefer mid/top, but can fill if needed")
        template3_btn = create_template_button("🔄 Flex", "Can pick for swap if anyone needs")
        template4_btn = create_template_button("🏆 Competitive", "Let's focus and win this game!")
        template5_btn = create_template_button("🤝 Support", "I'll support the team, let me know what you need")
        template6_btn = create_template_button("💪 Confidence", "I'm confident with this pick, it fits our comp")
        template7_btn = create_template_button("🙏 Respect", "Let's have a respectful game, no flame please")
        template8_btn = create_template_button("🌟 Team Player", "I'll adapt to what the team needs")
        
        # Aggiungere i bottoni al layout
        template_buttons_layout.addWidget(template1_btn, 0, 0)
        template_buttons_layout.addWidget(template2_btn, 0, 1)
        template_buttons_layout.addWidget(template3_btn, 1, 0)
        template_buttons_layout.addWidget(template4_btn, 1, 1)
        template_buttons_layout.addWidget(template5_btn, 2, 0)
        template_buttons_layout.addWidget(template6_btn, 2, 1)
        template_buttons_layout.addWidget(template7_btn, 3, 0)
        template_buttons_layout.addWidget(template8_btn, 3, 1)
        
        templates_layout.addLayout(template_buttons_layout)
        
        # Aggiungi il gruppo template al layout
        auto_message_layout.addWidget(templates_group)
        
        # Aggiungi spaziatura alla fine
        auto_message_layout.addStretch()
        
        self.tabs.addTab(auto_message_tab, "Auto Message")
        
        # -------------------------------------------------------------------------
        # LOG TAB
        # -------------------------------------------------------------------------
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        
        # Status log with improved styling
        log_group = QGroupBox("Status Log")
        log_inner_layout = QVBoxLayout()
        
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("""
            background-color: #091428;
            font-family: 'Consolas', monospace;
            border: 1px solid #3C3C3C;
            padding: 5px;
            color: #F0E6D2;
        """)
        
        log_controls_layout = QHBoxLayout()
        
        clear_log_btn = StyledButton('Clear Log')
        clear_log_btn.clicked.connect(self.log_area.clear)
        
        log_controls_layout.addStretch()
        log_controls_layout.addWidget(clear_log_btn)
        
        log_inner_layout.addWidget(self.log_area)
        log_inner_layout.addLayout(log_controls_layout)
        
        log_group.setLayout(log_inner_layout)
        log_layout.addWidget(log_group)
        
        self.tabs.addTab(log_tab, "Log")
        
        # -------------------------------------------------------------------------
        # SETTINGS TAB
        # -------------------------------------------------------------------------
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        
        # Sezione impostazioni generali
        general_settings_group = QGroupBox("General Settings")
        general_settings_layout = QVBoxLayout()
        
        # Opzione di auto-start
        auto_start_checkbox = QCheckBox("Auto-connect on startup")
        auto_start_checkbox.setChecked(True)
        auto_start_checkbox.setStyleSheet("font-weight: bold;")
        general_settings_layout.addWidget(auto_start_checkbox)
        
        # Altre impostazioni possono essere aggiunte qui
        general_settings_group.setLayout(general_settings_layout)
        settings_layout.addWidget(general_settings_group)
        
        # Aggiunta di una sezione About
        about_group = QGroupBox("About")
        about_layout = QVBoxLayout()
        
        about_text = QLabel("""
        <html>
        <body style='color: #F0E6D2;'>
        <p>League of Legends Champion Select Manager v2.0</p>
        <p>This application helps you automate champion selection in LoL.</p>
        <p>© 2025 - All rights reserved</p>
        </body>
        </html>
        """)
        about_text.setAlignment(Qt.AlignCenter)
        about_text.setStyleSheet("padding: 15px;")
        about_layout.addWidget(about_text)
        
        about_group.setLayout(about_layout)
        settings_layout.addWidget(about_group)
        settings_layout.addStretch()
        
        self.tabs.addTab(settings_tab, "Settings")
        
        # Aggiungi il tab widget al layout scorrevole
        scroll_layout.addWidget(self.tabs)
        
        # Aggiungi uno stretch per garantire che l'interfaccia rimanga compatta
        scroll_layout.addStretch()
        
        # Aggiungi info app in fondo
        info_frame = QFrame()
        info_frame.setStyleSheet("background-color: #091428; border-top: 1px solid #3C3C3C; padding: 5px;")
        info_layout = QHBoxLayout(info_frame)
        
        info_label = QLabel("League of Legends Champion Select Manager v2.0")
        info_label.setStyleSheet("color: #C8AA6E; font-style: italic;")
        info_label.setAlignment(Qt.AlignCenter)
        
        info_layout.addWidget(info_label)
        
        # Aggiungi l'info frame al layout scorrevole
        scroll_layout.addWidget(info_frame)
        
        # Aggiungi lo scroll area al layout principale
        main_layout.addWidget(main_scroll_area)
        
        self.setLayout(main_layout)

    def _filter_champion_combo(self, text):
        """Filtra la lista dei campioni per il combo di selezione"""
        self.champion_filter_model.setFilterRegExp(text)
        
    def _filter_ban_combo(self, text):
        """Filtra la lista dei campioni per il combo di ban"""
        self.ban_filter_model.setFilterRegExp(text)

    # Crea un nuovo metodo per il ridimensionamento dinamico dell'interfaccia
    def resizeEvent(self, event):
        """Gestisce il ridimensionamento della finestra adattando l'interfaccia"""
        super().resizeEvent(event)
        
        # Controlla la larghezza della finestra e adatta l'interfaccia
        if self.width() < 900:
            # Per schermi stretti, rendi più compatti alcuni elementi
            self.champion_combo.setPlaceholderText('Select Champion')
            self.ban_combo.setPlaceholderText('Select Champion')
            
            # Riduci le dimensioni minime dei tab
            self.tabs.setStyleSheet("""
                QTabBar::tab {
                    min-width: 100px;
                    height: 30px;
                }
            """)
        else:
            # Per schermi più larghi, usa testi più descrittivi
            self.champion_combo.setPlaceholderText('Select Champion to Pick')
            self.ban_combo.setPlaceholderText('Select Champion to Ban')
            
            # Ripristina le dimensioni dei tab
            self.tabs.setStyleSheet("""
                QTabBar::tab {
                    min-width: 120px;
                    height: 30px;
                }
            """)
    

    def log_message(self, message):
        """Log messages to the text area with improved formatting"""
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        
        # Apply different styling based on message type
        if "✅" in message:
            formatted_message = f"<span style='color:#3CB371;'>[{timestamp}] {message}</span>"
        elif "❌" in message:
            formatted_message = f"<span style='color:#CB2E2E;'>[{timestamp}] {message}</span>"
        elif "⚠️" in message:
            formatted_message = f"<span style='color:#F0A500;'>[{timestamp}] {message}</span>"
        elif "🔄" in message:
            formatted_message = f"<span style='color:#0AC8B9;'>[{timestamp}] {message}</span>"
        elif "📊" in message:
            formatted_message = f"<span style='color:#C8AA6E;'>[{timestamp}] {message}</span>"
        else:
            formatted_message = f"<span style='color:#F0E6D2;'>[{timestamp}] {message}</span>"
            
        self.log_area.append(formatted_message)
        # Auto-scroll to bottom
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def auto_connect(self):
        """Automatically connect to LCU API using lockfile"""
        # Disable SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.log_message("🔄 Connecting to League client...")
        
        # MODIFICA IMPORTANTE: Cerca nuovamente il lockfile ad ogni tentativo di connessione
        # invece di usare quello memorizzato, poiché cambia ad ogni avvio del client
        self.lockfile_path = self.get_lockfile_path()
        
        # Parse lockfile
        port, password = self.parse_lockfile()
        
        if not port or not password:
            self.log_message("❌ Could not retrieve connection details")
            self.connection_status.setText("DISCONNECTED")
            self.connection_status.setStyleSheet("""
                font-weight: bold;
                color: #CB2E2E;
                padding: 8px;
                border-radius: 4px;
                background: #1E2328;
                border: 1px solid #CB2E2E;
            """)
            self.is_connected = False
            return False

        try:
            # Create authentication header
            auth_string = f"riot:{password}"
            auth_bytes = auth_string.encode('ascii')
            base64_bytes = base64.b64encode(auth_bytes)
            base64_string = base64_bytes.decode('ascii')
            
            self.base_url = f"https://127.0.0.1:{port}"
            self.auth_header = {
                'Authorization': f'Basic {base64_string}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            # Visual feedback durante la connessione
            self.connection_status.setText("CONNECTING...")
            self.connection_status.setStyleSheet("""
                font-weight: bold;
                color: #F0A500;
                padding: 8px;
                border-radius: 4px;
                background: #1E2328;
                border: 1px solid #F0A500;
            """)
            QApplication.processEvents()  # Update UI immediately

            # Test connection
            response = requests.get(f"{self.base_url}/lol-summoner/v1/current-summoner", 
                                    headers=self.auth_header, verify=False, timeout=5)
            
            if response.status_code == 200:
                summoner_data = response.json()
                self.summoner_id = summoner_data.get('summonerId')
                summoner_name = summoner_data.get('displayName', 'Unknown')
                
                self.log_message(f"✅ Successfully connected to LCU API! Welcome {summoner_name}!")
                self.connection_status.setText(f"CONNECTED: {summoner_name}")
                self.connection_status.setStyleSheet("""
                    font-weight: bold;
                    color: #3CB371;
                    padding: 8px;
                    border-radius: 4px;
                    background: #1E2328;
                    border: 1px solid #3CB371;
                """)
                self.is_connected = True
                
                # Show a success notification
                self.show_notification("Connection Success", f"Connected to League client as {summoner_name}", "success")
                
                # Automatically load owned champions
                self.load_champions()
                return True
            else:
                self.log_message(f"❌ Connection failed. Status code: {response.status_code}")
                self.connection_status.setText("CONNECTION FAILED")
                self.connection_status.setStyleSheet("""
                    font-weight: bold;
                    color: #CB2E2E;
                    padding: 8px;
                    border-radius: 4px;
                    background: #1E2328;
                    border: 1px solid #CB2E2E;
                """)
                self.is_connected = False
                
                # Show an error notification
                self.show_notification("Connection Failed", 
                                    f"Failed to connect to League client (Status: {response.status_code})", 
                                    "error")
                return False
        
        except requests.exceptions.RequestException as e:
            self.log_message(f"❌ Connection error: {str(e)}")
            self.connection_status.setText("CONNECTION ERROR")
            self.connection_status.setStyleSheet("""
                font-weight: bold;
                color: #CB2E2E;
                padding: 8px;
                border-radius: 4px;
                background: #1E2328;
                border: 1px solid #CB2E2E;
            """)
            self.is_connected = False
            
            # Show an error notification with details
            self.show_notification("Connection Error", 
                                f"Cannot connect to League client: {str(e)}", 
                                "error")
            return False
        
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)}")
            self.connection_status.setText("CONNECTION ERROR")
            self.connection_status.setStyleSheet("""
                font-weight: bold;
                color: #CB2E2E;
                padding: 8px;
                border-radius: 4px;
                background: #1E2328;
                border: 1px solid #CB2E2E;
            """)
            self.is_connected = False
            
            # Show an error notification
            self.show_notification("Unknown Error", 
                                f"An error occurred: {str(e)}", 
                                "error")
            return False

    def load_champions(self):
        """Load available champions with visual progress feedback"""
        if not self.base_url or not self.auth_header:
            self.log_message("❌ Please ensure League client is running!")
            self.show_notification("Connection Error", "League client not detected. Please ensure it's running.", "error")
            return

        try:
            # Update champions loaded indicator
            self.champions_loaded_label.setText("Champions: Loading...")
            self.champions_loaded_label.setStyleSheet("color: #F0A500; padding: 8px; border-radius: 4px; background: #1E2328;")
            QApplication.processEvents()  # Update UI immediately
            
            # Visual progress indicator
            self.log_message("🔄 Loading champions data...")
            
            # Try different endpoints for champions
            endpoints = [
                "/lol-champions/v1/owned-champions-minimal",
                "/lol-champ-select/v1/all-grid-champions"
            ]
            
            # Create a styled list of endpoints we're trying
            endpoint_list = "🔄 Trying these champion endpoints:\n"
            endpoint_list += "┌───────────────────────────────────────────┐\n"
            for i, endpoint in enumerate(endpoints):
                endpoint_list += f"│ {i+1}. {endpoint.ljust(40)} │\n"
            endpoint_list += "└───────────────────────────────────────────┘"
            self.log_message(endpoint_list)
            
            champions = None
            for endpoint in endpoints:
                try:
                    self.log_message(f"🔄 Trying to load from: {endpoint}")
                    response = requests.get(f"{self.base_url}{endpoint}", 
                                        headers=self.auth_header, verify=False, timeout=5)
                    
                    if response.status_code == 200:
                        champions = response.json()
                        self.log_message(f"✅ Champions loaded from {endpoint}")
                        break
                except Exception as e:
                    self.log_message(f"⚠️ Couldn't load champions from {endpoint}: {str(e)}")
            
            if not champions:
                self.log_message("❌ Failed to load champions from all endpoints")
                self.champions_loaded_label.setText("Champions: Failed to Load")
                self.champions_loaded_label.setStyleSheet("color: #CB2E2E; padding: 8px; border-radius: 4px; background: #1E2328;")
                self.show_notification("Loading Error", "Failed to load champions data. Try reconnecting to the client.", "error")
                return
            
            # Store champions data for lookup
            self.champions_data = {}
            
            # Process champions data with visual progress
            self.log_message("🔄 Processing champions data...")
            self.champion_list_model.clear()
            self.ban_list_model.clear()
            
            # Check data structure for compatibility
            if isinstance(champions, list):
                # Direct list of champions
                champion_list = champions
            elif isinstance(champions, dict) and 'champions' in champions:
                # Nested structure
                champion_list = champions.get('champions', [])
            else:
                self.log_message("❌ Unknown champion data format")
                self.champions_loaded_label.setText("Champions: Unknown Format")
                self.champions_loaded_label.setStyleSheet("color: #CB2E2E; padding: 8px; border-radius: 4px; background: #1E2328;")
                self.show_notification("Loading Error", "Unknown champion data format detected.", "error")
                return
            
            # Sort champions by name
            self.log_message("🔄 Sorting champions alphabetically...")
            sorted_champions = sorted(champion_list, key=lambda x: x.get('name', ''))
            
            owned_champions = []
            all_champions = []
            
            # Update progress label
            self.champions_loaded_label.setText("Champions: Processing...")
            self.champions_loaded_label.setStyleSheet("color: #F0A500; padding: 8px; border-radius: 4px; background: #1E2328;")
            QApplication.processEvents()  # Update UI immediately
            
            for champ in sorted_champions:
                # Different APIs might have different ownership fields
                is_owned = False
                
                if 'ownership' in champ:
                    is_owned = champ.get('ownership', {}).get('owned', False)
                elif 'active' in champ:
                    is_owned = champ.get('active', False)
                elif 'freeToPlay' in champ:
                    is_owned = champ.get('owned', False) or champ.get('freeToPlay', False)
                else:
                    # Assume owned if no ownership field exists
                    is_owned = True
                
                # Get champion ID (might be in different fields)
                champ_id = None
                if 'id' in champ:
                    champ_id = champ.get('id')
                elif 'championId' in champ:
                    champ_id = champ.get('championId')
                
                champ_name = champ.get('name', 'Unknown')
                
                # Store champion info for lookup
                self.champions_data[champ_id] = {
                    'name': champ_name,
                    'id': champ_id,
                    'owned': is_owned
                }
                
                ban_item = QStandardItem(champ_name)
                ban_item.setData(champ_id, Qt.UserRole)
                self.ban_list_model.appendRow(ban_item)
                all_champions.append(champ_name)


                # Add ALL champions to the ban combo (regardless of ownership)
                self.ban_combo.addItem(champ_name, champ_id)
                all_champions.append(champ_name)
                
                # Add only owned champions to the pick combo
                if is_owned:
                    champion_item = QStandardItem(champ_name)
                    champion_item.setData(champ_id, Qt.UserRole)
                    self.champion_list_model.appendRow(champion_item)
                    owned_champions.append(champ_name)
            
            # Update success indicator with count
            self.champions_loaded_label.setText(f"Champions: {len(owned_champions)} Loaded")
            self.champions_loaded_label.setStyleSheet("color: #3CB371; padding: 8px; border-radius: 4px; background: #1E2328;")
            
            self.log_message(f"✅ Loaded {self.champion_combo.count()} owned champions for picking!")
            self.show_notification("Champions Loaded", f"Successfully loaded {len(owned_champions)} owned champions.", "success")
            
            # Try to load all champions if needed
            if len(all_champions) < 150:  # If we didn't get all champions (there should be 150+)
                self.log_message("⚠️ Did not get all champions, trying alternative method...")
                self.load_all_champions()
            
        except Exception as e:
            self.log_message(f"❌ Error loading champions: {str(e)}")
            self.champions_loaded_label.setText("Champions: Error")
            self.champions_loaded_label.setStyleSheet("color: #CB2E2E; padding: 8px; border-radius: 4px; background: #1E2328;")
            self.show_notification("Loading Error", f"Error: {str(e)}", "error")


    def execute_auto_ban(self):
        """Execute ban after a delay with visual feedback"""
        # Visual notification with countdown completed
        self.log_message("⏱️ Ban delay expired, executing auto ban...")
        
        # Highlight the ban controls
        self.ban_combo.setStyleSheet("""
            QComboBox {
                background-color: #761C1C;
                border: 2px solid #CB2E2E;
                border-radius: 4px;
                padding: 8px;
                font-size: 11pt;
                color: #FFFFFF;
                font-weight: bold;
            }
        """)
        
        QApplication.processEvents()  # Update UI immediately
        
        # Execute the ban
        self.ban_champion()
        
        # Reset styling after a short delay
        QTimer.singleShot(800, lambda: self.ban_combo.setStyleSheet("""
            QComboBox {
                background-color: #1E2328;
                border: 1px solid #3C3C3C;
                border-radius: 4px;
                padding: 6px;
                color: #F0E6D2;
            }
            QComboBox:focus {
                border: 1px solid #C8AA6E;
            }
        """))


    def execute_auto_pick(self):
        """Esegue il pick dopo un ritardo"""
        self.log_message("⏱️ Il ritardo per auto-pick è terminato, esecuzione del pick...")
        self.pick_champion()

    def load_all_champions(self):
        """Load all champions (for banning) if the first method didn't get them all"""
        try:
            # Alternative endpoint for all champions
            endpoint = "/lol-game-data/assets/v1/champion-summary.json"
            response = requests.get(f"{self.base_url}{endpoint}", 
                                   headers=self.auth_header, verify=False, timeout=5)
            
            if response.status_code == 200:
                champions = response.json()
                
                if not champions or len(champions) < 200:
                    # Another endpoint to try
                    endpoint = "/lol-champions/v1/champion-grid-champions"
                    response = requests.get(f"{self.base_url}{endpoint}", 
                                           headers=self.auth_header, verify=False, timeout=5)
                    
                    if response.status_code == 200:
                        champions = response.json()
                
                # Clear and refill ban combo
                self.ban_combo.clear()
                
                # Sort champions by name
                sorted_champions = sorted(champions, key=lambda x: x.get('name', ''))
                
                for champ in sorted_champions:
                    champ_id = champ.get('id')
                    champ_name = champ.get('name', 'Unknown')
                    
                    # Store champion info for lookup if not already stored
                    if champ_id not in self.champions_data:
                        self.champions_data[champ_id] = {
                            'name': champ_name,
                            'id': champ_id,
                            'owned': False  # Default to not owned since we don't know
                        }
                    
                    # Add to ban combo
                    self.ban_combo.addItem(champ_name, champ_id)
                
                self.log_message(f"✅ Loaded {self.ban_combo.count()} champions for banning (all champions)!")
        
        except Exception as e:
            self.log_message(f"⚠️ Error loading all champions: {str(e)}")


    def pick_champion(self):
        """Pick selected champion with improved visual feedback"""
        if not self.base_url or not self.auth_header:
            self.log_message("❌ Please ensure League client is running!")
            return

        try:
            # Get selected champion
            current_index = self.champion_combo.currentIndex()
            if current_index == -1:
                self.log_message("❌ Please select a champion!")
                
                # Visual error feedback
                original_style = self.champion_combo.styleSheet()
                self.champion_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #4B1113;
                        border: 2px solid #CB2E2E;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """)

            
                
                # Reset styling after a short delay
                QTimer.singleShot(1500, lambda: self.champion_combo.setStyleSheet(original_style))
                return
            
            proxy_index = self.champion_filter_model.index(current_index, 0)
            source_index = self.champion_filter_model.mapToSource(proxy_index)
            
            champion_id = self.champion_list_model.itemFromIndex(source_index).data(Qt.UserRole)
            champion_name = self.champion_list_model.itemFromIndex(source_index).text()

            champion_id = self.champion_combo.currentData()
            champion_name = self.champion_combo.currentText()

            # Visual feedback - attempting pick
            self.log_message(f"🔄 Attempting to pick {champion_name}...")
            
            # Highlight the champion being picked in the combo box
            self.champion_combo.setStyleSheet("""
                QComboBox {
                    background-color: #153626;
                    border: 2px solid #3CB371;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 11pt;
                    color: #FFFFFF;
                    font-weight: bold;
                }
            """)
            QApplication.processEvents()  # Update UI immediately

            # First, get current champion select session
            session_response = requests.get(f"{self.base_url}/lol-champ-select/v1/session", 
                                        headers=self.auth_header, verify=False, timeout=5)
            
            if session_response.status_code != 200:
                self.log_message("❌ Not in champion select!")
                
                # Reset styling
                self.champion_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #1E2328;
                        border: 1px solid #3C3C3C;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """)
                return

            session_data = session_response.json()
            
            # Find the player's cell ID
            local_player_cell_id = None
            try:
                local_player_cell_id = session_data.get('localPlayerCellId')
                if local_player_cell_id is None:
                    # Try alternative method to find cell ID using summoner ID
                    self.log_message("🔄 Using alternative method to find your position...")
                    for i, player in enumerate(session_data.get('myTeam', [])):
                        if player.get('summonerId') == self.summoner_id:
                            local_player_cell_id = player.get('cellId')
                            break
            except Exception:
                pass
            
            if local_player_cell_id is None:
                self.log_message("❌ Could not identify your position in champion select!")
                
                # Reset styling
                self.champion_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #1E2328;
                        border: 1px solid #3C3C3C;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """)
                return
            
            # Find the current action for the player
            current_actions = session_data.get('actions', [])
            my_action = None

            # Flatten the actions and find the first pickable action
            for action_group in current_actions:
                for action in action_group:
                    if (action.get('type') == 'pick' and 
                        action.get('actorCellId') == local_player_cell_id and 
                        not action.get('completed', False)):
                        my_action = action
                        break
                
                if my_action:
                    break

            if not my_action:
                self.log_message("❌ No pickable action found! It may not be your turn yet.")
                
                # Reset styling
                self.champion_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #1E2328;
                        border: 1px solid #3C3C3C;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """)
                return

            # Prepare the pick request
            pick_data = {
                "championId": champion_id,
                "completed": True,
            }

            # Try multiple endpoints
            endpoints = [
                f"/lol-champ-select/v1/session/actions/{my_action['id']}",  # Standard API
                f"/lol-lobby-team-builder/champ-select/v1/session/actions/{my_action['id']}"  # Alternative API
            ]
            
            success = False
            for endpoint in endpoints:
                try:
                    self.log_message(f"🔄 Trying pick endpoint: {endpoint}")
                    pick_response = requests.patch(
                        f"{self.base_url}{endpoint}", 
                        headers=self.auth_header, 
                        json=pick_data, 
                        verify=False,
                        timeout=5
                    )
                    
                    # Check if the request was successful
                    if pick_response.status_code in [200, 204]:
                        self.log_message(f"✅ Successfully picked {champion_name}")
                        success = True
                        self.pick_completed = True  # Imposta il flag di completamento
                        
                        # Visual success feedback
                        self.champion_combo.setStyleSheet("""
                            QComboBox {
                                background-color: #153626;
                                border: 2px solid #3CB371;
                                border-radius: 4px;
                                padding: 8px;
                                font-size: 11pt;
                                color: #FFFFFF;
                                font-weight: bold;
                            }
                        """)
                        
                        # Reset styling after a delay
                        QTimer.singleShot(1500, lambda: self.champion_combo.setStyleSheet("""
                            QComboBox {
                                background-color: #1E2328;
                                border: 1px solid #3C3C3C;
                                border-radius: 4px;
                                padding: 6px;
                                color: #F0E6D2;
                            }
                        """))
                        
                        # Mostra una notifica di successo
                        self.show_notification("Champion Picked", 
                                            f"Successfully picked {champion_name}!", 
                                            "success")
                        break
                    else:
                        self.log_message(f"⚠️ Failed with endpoint {endpoint}: {pick_response.status_code}")
                except Exception as e:
                    self.log_message(f"⚠️ Error with endpoint {endpoint}: {str(e)}")
            
            # If standard methods fail, try alternative method with complete=false first
            if not success:
                try:
                    self.log_message("🔄 Trying alternative pick method (two-step)...")
                    # First, select champion without completing
                    pick_data["completed"] = False
                    
                    interim_response = requests.patch(
                        f"{self.base_url}/lol-champ-select/v1/session/actions/{my_action['id']}", 
                        headers=self.auth_header, 
                        json=pick_data, 
                        verify=False,
                        timeout=5
                    )
                    
                    if interim_response.status_code in [200, 204]:
                        self.log_message("✅ Selected champion (step 1)")
                        # Now complete the action
                        pick_data["completed"] = True
                        
                        complete_response = requests.patch(
                            f"{self.base_url}/lol-champ-select/v1/session/actions/{my_action['id']}", 
                            headers=self.auth_header, 
                            json=pick_data, 
                            verify=False,
                            timeout=5
                        )
                        
                        if complete_response.status_code in [200, 204]:
                            self.log_message(f"✅ Successfully picked {champion_name} (step 2)")
                            success = True
                            self.pick_completed = True  # Imposta il flag di completamento
                            
                            # Visual success feedback
                            self.champion_combo.setStyleSheet("""
                                QComboBox {
                                    background-color: #153626;
                                    border: 2px solid #3CB371;
                                    border-radius: 4px;
                                    padding: 8px;
                                    font-size: 11pt;
                                    color: #FFFFFF;
                                    font-weight: bold;
                                }
                            """)
                            
                            # Reset styling after a delay
                            QTimer.singleShot(1500, lambda: self.champion_combo.setStyleSheet("""
                                QComboBox {
                                    background-color: #1E2328;
                                    border: 1px solid #3C3C3C;
                                    border-radius: 4px;
                                    padding: 6px;
                                    color: #F0E6D2;
                                }
                            """))
                            
                            # Mostra una notifica di successo
                            self.show_notification("Champion Picked", 
                                                f"Successfully picked {champion_name}!", 
                                                "success")
                    else:
                        self.log_message(f"⚠️ Failed step 1: {interim_response.status_code}")
                except Exception as e:
                    self.log_message(f"⚠️ Error with alternative method: {str(e)}")
            
            # Another alternative: using intent
            if not success:
                try:
                    self.log_message("🔄 Trying intent method...")
                    intent_response = requests.patch(
                        f"{self.base_url}/lol-champ-select/v1/session/my-selection", 
                        headers=self.auth_header, 
                        json={"championId": champion_id}, 
                        verify=False,
                        timeout=5
                    )
                    
                    if intent_response.status_code in [200, 204]:
                        self.log_message(f"✅ Set champion intent. Try clicking the champion or the lock button.")
                        
                        # Visual partial success feedback
                        self.champion_combo.setStyleSheet("""
                            QComboBox {
                                background-color: #155051;
                                border: 2px solid #0AC8B9;
                                border-radius: 4px;
                                padding: 8px;
                                font-size: 11pt;
                                color: #FFFFFF;
                            }
                        """)
                        
                        # Mostra un messaggio di hint
                        self.show_notification("Intent Set", 
                                            f"Pick intent set for {champion_name}. You may need to click the lock button.", 
                                            "info")
                        
                        # Reset styling after a delay
                        QTimer.singleShot(3000, lambda: self.champion_combo.setStyleSheet("""
                            QComboBox {
                                background-color: #1E2328;
                                border: 1px solid #3C3C3C;
                                border-radius: 4px;
                                padding: 6px;
                                color: #F0E6D2;
                            }
                        """))
                    else:
                        self.log_message(f"⚠️ Intent method failed: {intent_response.status_code}")
                except Exception as e:
                    self.log_message(f"⚠️ Error with intent method: {str(e)}")
            
            if not success:
                self.log_message(f"❌ Failed to pick champion after trying all methods.")
                
                # Visual error feedback
                self.champion_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #4B1113;
                        border: 1px solid #CB2E2E;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """)
                
                # Reset styling after a delay
                QTimer.singleShot(1500, lambda: self.champion_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #1E2328;
                        border: 1px solid #3C3C3C;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """))

        except Exception as e:
            self.log_message(f"❌ Error picking champion: {str(e)}")
            
            # Reset styling in case of error
            self.champion_combo.setStyleSheet("""
                QComboBox {
                    background-color: #1E2328;
                    border: 1px solid #3C3C3C;
                    border-radius: 4px;
                    padding: 6px;
                    color: #F0E6D2;
                }
            """)


    def check_champion_select(self):
        """Check if in champion select and handle auto features"""
        # Skip if not connected
        if not self.is_connected:
            return

        if not self.base_url or not self.auth_header:
            self.is_connected = False
            return

        try:
            # Fetch current champion select session
            response = requests.get(f"{self.base_url}/lol-champ-select/v1/session", 
                                headers=self.auth_header, verify=False, timeout=5)
            
            # Check if we're in champion select
            if response.status_code == 200:
                current_session = response.json()
                
                # Update game phase label
                phase = current_session.get('timer', {}).get('phase', 'UNKNOWN')
                self.game_phase_label.setText(f"Phase: {phase}")
                
                # Color code the phase label based on phase type
                if phase == 'BAN_PICK':
                    self.game_phase_label.setStyleSheet("color: #CB2E2E; padding: 8px; border-radius: 4px; background: #1E2328; font-weight: bold;")
                elif phase == 'PLANNING':
                    self.game_phase_label.setStyleSheet("color: #0AC8B9; padding: 8px; border-radius: 4px; background: #1E2328; font-weight: bold;")
                elif phase == 'FINALIZATION':
                    self.game_phase_label.setStyleSheet("color: #3CB371; padding: 8px; border-radius: 4px; background: #1E2328; font-weight: bold;")
                else:
                    self.game_phase_label.setStyleSheet("color: #C8AA6E; padding: 8px; border-radius: 4px; background: #1E2328; font-weight: bold;")
                
                # Check if this is a new champion select session
                if self.last_session_state is None:
                    # Visual notification of entering champion select
                    self.log_message("✅ Entered Champion Select!")
                    
                    # Send auto message if checkbox is checked and message is not empty
                    if (self.auto_message_checkbox.isChecked() and 
                        self.auto_message_input.text().strip() and not self.message_completed):
                        self.log_message("🔄 Sending automatic message...")
                        
                        # Show visual indicator that auto message is being sent
                        original_text = self.auto_message_input.text()
                        self.auto_message_input.setStyleSheet("background-color: #153626; color: #FFFFFF;")
                        QApplication.processEvents()  # Ensure UI updates
                        
                        self.retry_send_message(self.auto_message_input.text(), max_retries=15, delay=1000)

                        
                        # Reset styling after a brief moment
                        QTimer.singleShot(800, lambda: self.auto_message_input.setStyleSheet(
                            "background-color: #1E2328; border: 1px solid #3C3C3C; border-radius: 4px; padding: 6px; color: #F0E6D2;"
                        ))

                # Initialize ban_action_active flag outside conditional blocks
                ban_action_active = False
                pick_action_active = False

                local_player_cell_id = current_session.get('localPlayerCellId')

                # Auto ban feature
                if self.auto_ban_checkbox.isChecked() and self.ban_combo.currentIndex() != -1 and not self.ban_completed:
                    # Get player's cell ID
                    local_player_cell_id = current_session.get('localPlayerCellId')
                    
                    # Check current phase
                    timer = current_session.get('timer', {})
                    phase = timer.get('phase', '')
                    
                    # Visual feedback for phase changes in the log
                    if hasattr(self, 'last_logged_phase') and self.last_logged_phase != phase:
                        self.log_message(f"📊 New champion select phase: {phase}")
                        self.last_logged_phase = phase
                    elif not hasattr(self, 'last_logged_phase'):
                        self.last_logged_phase = phase
                        self.log_message(f"📊 Current phase: {phase}")

                    # Visual indication when we're in ban phase
                    if phase == 'BAN_PICK':
                        # Check if it's our turn to ban
                        for action_group in current_session.get('actions', []):
                            for action in action_group:
                                # Find an uncompleted ban action for the local player
                                if (action.get('type') == 'ban' and 
                                    action.get('actorCellId') == local_player_cell_id and 
                                    not action.get('completed', False)):

                                    if action.get("isInProgress", False):
                                        ban_action_active = True

                                        # Highlight the ban controls when it's ban time
                                        self.ban_combo.setStyleSheet("""
                                            QComboBox {
                                                background-color: #4B1113;
                                                border: 2px solid #CB2E2E;
                                                border-radius: 4px;
                                                padding: 8px;
                                                font-size: 11pt;
                                                color: #FFFFFF;
                                            }
                                            QComboBox:hover {
                                                background-color: #761C1C;
                                            }
                                        """)

                                        if not self.ban_timer.isActive() and not hasattr(self, 'ban_executed_this_turn') and not self.ban_completed:
                                            try:
                                                # Get delay from input box
                                                delay_seconds = int(self.ban_delay_input.text())
                                                if delay_seconds < 0:
                                                    delay_seconds = 0
                                            except ValueError:
                                                delay_seconds = 3  # Default if value is invalid
                                                
                                            # Visual countdown feedback
                                            self.log_message(f"⏱️ AUTO BAN: Scheduled in {delay_seconds} seconds...")
                                            
                                            # Add visual highlight to the ban delay input
                                            self.ban_delay_input.setStyleSheet("""
                                                background-color: #4B1113;
                                                color: #FFFFFF;
                                                border: 2px solid #CB2E2E;
                                                border-radius: 4px;
                                                padding: 6px;
                                                font-weight: bold;
                                            """)
                                            
                                            # Start the ban timer
                                            self.ban_timer.start(delay_seconds * 1000)  # Convert to milliseconds
                                            self.ban_executed_this_turn = True  # Mark that we've scheduled a ban
                                            
                                            # Reset styling after delay ends
                                            QTimer.singleShot(delay_seconds * 1000, lambda: self.ban_delay_input.setStyleSheet(
                                                "background-color: #1E2328; border: 1px solid #3C3C3C; border-radius: 4px; padding: 6px; color: #F0E6D2;"
                                            ))
                                        break
                # NUOVO: Handle auto-pick
                if self.auto_pick_checkbox.isChecked() and self.champion_combo.currentIndex() != -1 and not self.pick_completed:
                    # Check if in pick phase
                    timer = current_session.get('timer', {})
                    phase = timer.get('phase', '')
                    
                    # Check if it's our turn to pick
                    for action_group in current_session.get('actions', []):
                        for action in action_group:
                            # Find an uncompleted pick action for the local player
                            if (action.get('type') == 'pick' and 
                                action.get('actorCellId') == local_player_cell_id and 
                                not action.get('completed', False)):
                                
                                if action.get("isInProgress", False):
                                    pick_action_active = True
                                    
                                    # Highlight the pick controls when it's pick time
                                    self.champion_combo.setStyleSheet("""
                                        QComboBox {
                                            background-color: #153626;
                                            border: 2px solid #3CB371;
                                            border-radius: 4px;
                                            padding: 8px;
                                            font-size: 11pt;
                                            color: #FFFFFF;
                                        }
                                        QComboBox:hover {
                                            background-color: #1D4B35;
                                        }
                                    """)
                                    
                                    if not self.pick_timer.isActive() and not hasattr(self, 'pick_executed_this_turn') and not self.pick_completed:
                                        try:
                                            # Get delay from input box
                                            delay_seconds = int(self.pick_delay_input.text())
                                            if delay_seconds < 0:
                                                delay_seconds = 0
                                        except ValueError:
                                            delay_seconds = 2  # Default if value is invalid
                                            
                                        # Visual countdown feedback
                                        self.log_message(f"⏱️ AUTO PICK: Scheduled in {delay_seconds} seconds...")
                                        
                                        # Add visual highlight to the pick delay input
                                        self.pick_delay_input.setStyleSheet("""
                                            background-color: #153626;
                                            color: #FFFFFF;
                                            border: 2px solid #3CB371;
                                            border-radius: 4px;
                                            padding: 6px;
                                            font-weight: bold;
                                        """)
                                        
                                        # Start the pick timer
                                        self.pick_timer.start(delay_seconds * 1000)  # Convert to milliseconds
                                        self.pick_executed_this_turn = True  # Mark that we've scheduled a pick
                                        
                                        # Reset styling after delay ends
                                        QTimer.singleShot(delay_seconds * 1000, lambda: self.pick_delay_input.setStyleSheet(
                                            "background-color: #1E2328; border: 1px solid #3C3C3C; border-radius: 4px; padding: 6px; color: #F0E6D2;"
                                        ))
                                    break
                
                # Reset ban styling when not active
                if not ban_action_active:
                    # Reset ban combo styling to normal
                    self.ban_combo.setStyleSheet("""
                        QComboBox {
                            background-color: #1E2328;
                            border: 1px solid #3C3C3C;
                            border-radius: 4px;
                            padding: 6px;
                            color: #F0E6D2;
                        }
                        QComboBox:focus {
                            border: 1px solid #C8AA6E;
                        }
                    """)
                    
                    # Reset ban flag if it's no longer our turn
                    if hasattr(self, 'ban_executed_this_turn'):
                        delattr(self, 'ban_executed_this_turn')
                

                 # Reset pick styling when not active
                if not pick_action_active:
                    # Reset pick combo styling to normal
                    self.champion_combo.setStyleSheet("""
                        QComboBox {
                            background-color: #1E2328;
                            border: 1px solid #3C3C3C;
                            border-radius: 4px;
                            padding: 6px;
                            color: #F0E6D2;
                        }
                        QComboBox:focus {
                            border: 1px solid #C8AA6E;
                        }
                    """)
                    
                    # Reset pick flag if it's no longer our turn
                    if hasattr(self, 'pick_executed_this_turn'):
                        delattr(self, 'pick_executed_this_turn')
                    # Update last session state
                    self.last_session_state = current_session
                
            elif response.status_code == 404:
                # No longer in champion select
                if self.last_session_state is not None:
                    self.log_message("❌ Left Champion Select")
                    self.last_session_state = None
                    self.ban_completed = False
                    self.message_completed = False
                        
                    # Reset game phase label
                    self.game_phase_label.setText("Phase: Not in Champion Select")
                    self.game_phase_label.setStyleSheet("color: #F0E6D2; padding: 8px; border-radius: 4px; background: #1E2328;")
                        
                    # Reset UI elements to default state
                    self.ban_combo.setStyleSheet("""
                        QComboBox {
                            background-color: #1E2328;
                            border: 1px solid #3C3C3C;
                            border-radius: 4px;
                            padding: 6px;
                            color: #F0E6D2;
                        }
                    """)
                        
                    self.ban_delay_input.setStyleSheet("""
                        background-color: #1E2328;
                        border: 1px solid #3C3C3C;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    """)
            
        except requests.exceptions.RequestException:
            # Connection error, might be temporary, don't change connection status yet
            pass
            
        except Exception as e:
            # Only log serious errors
            if "ChampSelect.SetAction" not in str(e):  # Ignore common errors
                self.log_message(f"⚠️ Error checking champion select: {str(e)}")


    def detect_chat_endpoint(self):
        """Detect the appropriate chat endpoint based on game mode with improved search for champion select"""
        if not self.base_url or not self.auth_header:
            return None
            
        try:
            # Show visual feedback that we're searching for chat
            self.log_message("🔄 Ricerca del canale di chat...")
            
            # Get all conversations
            chat_response = requests.get(
                f"{self.base_url}/lol-chat/v1/conversations", 
                headers=self.auth_header, verify=False, timeout=5
            )
            
            if chat_response.status_code != 200:
                self.log_message("⚠️ Impossibile recuperare le conversazioni chat")
                return None
                
            conversations = chat_response.json()
            
            # MIGLIORAMENTO: Cerca in modo più specifico il canale champion-select
            champion_select_channels = []
            
            for conv in conversations:
                conv_id = str(conv.get('id', ''))
                conv_type = str(conv.get('type', ''))
                
                # Verifica specifica per canali di champion select
                if (conv_type == 'championSelect' or 
                    'champ-select' in conv_id.lower() or 
                    'champion-select' in conv_id.lower() or
                    'champion-select' in conv_type.lower() or
                    'championselect' in conv_id.lower()):
                    
                    champion_select_channels.append(conv)
                    self.log_message(f"✅ Trovato canale champion select: {conv_id}")
                    return conv_id
            
            # Se non abbiamo trovato un canale con criteri specifici, prova a cercare con criteri più ampi
            game_id = None
            try:
                session_response = requests.get(
                    f"{self.base_url}/lol-champ-select/v1/session", 
                    headers=self.auth_header, verify=False, timeout=5
                )
                
                if session_response.status_code == 200:
                    session_data = session_response.json()
                    game_id = session_data.get('gameId')
            except Exception:
                pass
            
            if game_id:
                # Cerca conversazioni che contengono l'ID del gioco
                for conv in conversations:
                    conv_id = str(conv.get('id', ''))
                    if str(game_id) in conv_id:
                        self.log_message(f"✅ Trovato canale con ID gioco: {conv_id}")
                        return conv_id
                
                # Costruisci ID canale usando formati comuni
                possible_id = f"{game_id}@champ-select.riotgames.com"
                self.log_message(f"✅ Generato ID canale: {possible_id}")
                return possible_id
            
            # Fallback per altri tipi di canali che potrebbero funzionare
            default_ids = [
                "champ-select",
                "champion-select-legacy",
                "champion-select"
            ]
            
            for default_id in default_ids:
                self.log_message(f"🔄 Provo il canale predefinito: {default_id}")
                return default_id
                
            self.log_message("⚠️ Impossibile determinare il canale di chat")
            return None
            
        except Exception as e:
            self.log_message(f"⚠️ Errore nella ricerca del canale chat: {str(e)}")
            return None

    def send_chat_message(self, message=None):
        """Send a message in champion select chat with improved visual feedback and retry mechanism"""
        # Get message from input if not provided
        if message is None:
            message = self.auto_message_input.text()
            
        if not message.strip():
            self.log_message("❌ Message is empty!")
            
            # Visual error feedback
            original_style = self.auto_message_input.styleSheet()
            self.auto_message_input.setStyleSheet("""
                background-color: #4B1113;
                border: 1px solid #CB2E2E;
                border-radius: 4px;
                padding: 6px;
                color: #F0E6D2;
            """)
            
            # Reset styling after a short delay
            QTimer.singleShot(1000, lambda: self.auto_message_input.setStyleSheet(original_style))
            return
            
        if not self.base_url or not self.auth_header:
            self.log_message("❌ Please ensure League client is running!")
            return

        # Create a new function for retry attempts
        self.retry_send_message(message, max_retries=10, delay=1000)  # 10 tentativi con 1 secondo di intervallo

    def retry_send_message(self, message, current_retry=0, max_retries=10, delay=1000):
        """Funzione ricorsiva per riprovare a inviare il messaggio fino a max_retries volte"""
        try:
            # Visual feedback for retry attempt
            if current_retry > 0:
                self.log_message(f"🔄 Tentativo {current_retry}/{max_retries} di inviare il messaggio...")
            else:
                self.log_message(f"🔄 Tentativo di inviare il messaggio: '{message}'")
            
            # First check if we're in champion select
            session_response = requests.get(
                f"{self.base_url}/lol-champ-select/v1/session", 
                headers=self.auth_header, verify=False, timeout=5
            )
            
            if session_response.status_code != 200:
                self.log_message("❌ Not in champion select!")
                return
                
            # Visual progress update
            self.log_message("🔄 Ricerca del canale di chat corretto...")
            
            # Method 1: Try to find the right conversation ID
            chat_id = self.detect_chat_endpoint()
            
            if chat_id:
                # Visual progress with chat ID
                self.log_message(f"🔄 Invio messaggio al canale: {chat_id}")
                
                # Visual feedback - message is being sent
                send_response = requests.post(
                    f"{self.base_url}/lol-chat/v1/conversations/{chat_id}/messages", 
                    headers=self.auth_header, 
                    json={"type": "chat", "body": message},
                    verify=False,
                    timeout=5
                )
                
                if send_response.status_code in [200, 204]:
                    # Success animation
                    self.log_message(f"✅ Messaggio inviato con successo: '{message}'")
                    self.message_completed = True
                    
                    # Visual success feedback in the input field
                    original_style = self.auto_message_input.styleSheet()
                    self.auto_message_input.setStyleSheet("""
                        background-color: #153626;
                        border: 1px solid #3CB371;
                        border-radius: 4px;
                        padding: 6px;
                        color: #FFFFFF;
                    """)
                    
                    # Reset styling after a short delay
                    QTimer.singleShot(1500, lambda: self.auto_message_input.setStyleSheet(original_style))
                    return
                else:
                    self.log_message(f"⚠️ Errore nell'invio al canale {chat_id}: {send_response.status_code}")
            
            # Try other methods (existing code)...
            # [existing code for alternative methods]
            
            # If we've reached here, none of the methods worked
            if current_retry < max_retries:
                # Schedule another retry after delay
                self.log_message(f"⏱️ Riproverò tra {delay/1000} secondi...")
                QTimer.singleShot(delay, lambda: self.retry_send_message(message, current_retry + 1, max_retries, delay))
            else:
                self.log_message(f"❌ Impossibile inviare il messaggio dopo {max_retries} tentativi.")
                
                # Visual error feedback
                original_style = self.auto_message_input.styleSheet()
                self.auto_message_input.setStyleSheet("""
                    background-color: #4B1113;
                    border: 1px solid #CB2E2E;
                    border-radius: 4px;
                    padding: 6px;
                    color: #F0E6D2;
                """)
                
                # Reset styling after a short delay
                QTimer.singleShot(1500, lambda: self.auto_message_input.setStyleSheet(original_style))
                
        except Exception as e:
            self.log_message(f"❌ Errore nell'invio del messaggio: {str(e)}")
            
            if current_retry < max_retries:
                # Schedule another retry after delay even after exception
                self.log_message(f"⏱️ Riproverò tra {delay/1000} secondi...")
                QTimer.singleShot(delay, lambda: self.retry_send_message(message, current_retry + 1, max_retries, delay))


    def ban_champion(self):
        """Ban selected champion with improved visual feedback"""
        if not self.base_url or not self.auth_header:
            self.log_message("❌ Please ensure League client is running!")
            return

        try:
            # Get selected champion
            current_index = self.ban_combo.currentIndex()
            if current_index == -1:
                self.log_message("❌ Please select a champion to ban!")
                
                # Visual error feedback
                original_style = self.ban_combo.styleSheet()
                self.ban_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #4B1113;
                        border: 2px solid #CB2E2E;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """)
                
                # Reset styling after a short delay
                QTimer.singleShot(1500, lambda: self.ban_combo.setStyleSheet(original_style))
                return
            
            proxy_index = self.ban_filter_model.index(current_index, 0)
            source_index = self.ban_filter_model.mapToSource(proxy_index)
            
            champion_id = self.ban_list_model.itemFromIndex(source_index).data(Qt.UserRole)
            champion_name = self.ban_list_model.itemFromIndex(source_index).text()

            champion_id = self.ban_combo.currentData()
            champion_name = self.ban_combo.currentText()

            # Visual feedback - attempting ban
            self.log_message(f"🔄 Attempting to ban {champion_name}...")
            
            # Highlight the champion being banned in the combo box
            self.ban_combo.setStyleSheet("""
                QComboBox {
                    background-color: #4B1113;
                    border: 2px solid #CB2E2E;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 11pt;
                    color: #FFFFFF;
                    font-weight: bold;
                }
            """)
            QApplication.processEvents()  # Update UI immediately

            # First, get current champion select session with visual progress
            self.log_message("🔄 Checking champion select session...")
            session_response = requests.get(f"{self.base_url}/lol-champ-select/v1/session", 
                                        headers=self.auth_header, verify=False, timeout=5)
            
            if session_response.status_code != 200:
                self.log_message("❌ Not in champion select!")
                
                # Reset styling
                self.ban_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #1E2328;
                        border: 1px solid #3C3C3C;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """)
                return

            session_data = session_response.json()
            
            # Find the player's cell ID with visual progress
            self.log_message("🔄 Identifying your position in champion select...")
            local_player_cell_id = None
            try:
                local_player_cell_id = session_data.get('localPlayerCellId')
                if local_player_cell_id is None:
                    # Try alternative method to find cell ID using summoner ID
                    self.log_message("🔄 Using alternative method to find your position...")
                    for i, player in enumerate(session_data.get('myTeam', [])):
                        if player.get('summonerId') == self.summoner_id:
                            local_player_cell_id = player.get('cellId')
                            break
            except Exception:
                pass
            
            if local_player_cell_id is None:
                self.log_message("❌ Could not identify your position in champion select!")
                
                # Reset styling
                self.ban_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #1E2328;
                        border: 1px solid #3C3C3C;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """)
                return
            
            # Find the current action for the player with visual progress
            self.log_message("🔄 Checking if it's your turn to ban...")
            current_actions = session_data.get('actions', [])
            my_action = None

            # Flatten the actions and find the first bannable action
            for action_group in current_actions:
                for action in action_group:
                    if (action.get('type') == 'ban' and 
                        action.get('actorCellId') == local_player_cell_id and 
                        not action.get('completed', False)):
                        my_action = action
                        break
                
                if my_action:
                    break

            if not my_action:
                self.log_message("❌ No bannable action found! It may not be ban phase yet.")
                
                # Reset styling
                self.ban_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #1E2328;
                        border: 1px solid #3C3C3C;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """)
                return

            # Prepare the ban request with visual progress
            self.log_message(f"🔄 Preparing to ban {champion_name}...")
            ban_data = {
                "championId": champion_id,
                "completed": True,
            }

            # Try multiple endpoints with visual progress
            endpoints = [
                f"/lol-champ-select/v1/session/actions/{my_action['id']}",  # Standard API
                f"/lol-lobby-team-builder/champ-select/v1/session/actions/{my_action['id']}"  # Alternative API
            ]
            
            # Create a styled list of endpoints we're trying
            endpoint_list = "🔄 Trying these ban endpoints:\n"
            endpoint_list += "┌───────────────────────────────────────────────────────────────────┐\n"
            for i, endpoint in enumerate(endpoints):
                endpoint_list += f"│ {i+1}. {endpoint.ljust(60)} │\n"
            endpoint_list += "└───────────────────────────────────────────────────────────────────┘"
            self.log_message(endpoint_list)
            
            success = False
            for endpoint in endpoints:
                try:
                    self.log_message(f"🔄 Sending ban request to: {endpoint}")
                    ban_response = requests.patch(
                        f"{self.base_url}{endpoint}", 
                        headers=self.auth_header, 
                        json=ban_data, 
                        verify=False,
                        timeout=5
                    )
                    
                    # Check if the request was successful
                    if ban_response.status_code in [200, 204]:
                        # Visual success animation
                        self.log_message(f"✅ Successfully banned: {champion_name}")
                        success = True
                        self.ban_completed = True
                        
                        # Change combo box to green success state briefly
                        self.ban_combo.setStyleSheet("""
                            QComboBox {
                                background-color: #153626;
                                border: 2px solid #3CB371;
                                border-radius: 4px;
                                padding: 8px;
                                font-size: 11pt;
                                color: #FFFFFF;
                                font-weight: bold;
                            }
                        """)
                        QApplication.processEvents()  # Update UI immediately
                        
                        # Reset styling after a short delay
                        QTimer.singleShot(1500, lambda: self.ban_combo.setStyleSheet("""
                            QComboBox {
                                background-color: #1E2328;
                                border: 1px solid #3C3C3C;
                                border-radius: 4px;
                                padding: 6px;
                                color: #F0E6D2;
                            }
                        """))
                        break
                    else:
                        self.log_message(f"⚠️ Failed with endpoint {endpoint}: {ban_response.status_code}")
                except Exception as e:
                    self.log_message(f"⚠️ Error with endpoint {endpoint}: {str(e)}")
            
            # If standard methods fail, try alternative method with complete=false first
            if not success:
                try:
                    self.log_message("🔄 Trying alternative ban method (two-step)...")
                    # First, select champion without completing
                    ban_data["completed"] = False
                    
                    # Visual progress indicator
                    self.log_message("🔄 Step 1: Selecting champion to ban...")
                    
                    interim_response = requests.patch(
                        f"{self.base_url}/lol-champ-select/v1/session/actions/{my_action['id']}", 
                        headers=self.auth_header, 
                        json=ban_data, 
                        verify=False,
                        timeout=5
                    )
                    
                    if interim_response.status_code in [200, 204]:
                        self.log_message("✅ Selected champion to ban (step 1 complete)")
                        # Now complete the action
                        ban_data["completed"] = True
                        
                        # Visual progress for step 2
                        self.log_message("🔄 Step 2: Confirming ban...")
                        
                        complete_response = requests.patch(
                            f"{self.base_url}/lol-champ-select/v1/session/actions/{my_action['id']}", 
                            headers=self.auth_header, 
                            json=ban_data, 
                            verify=False,
                            timeout=5
                        )
                        
                        if complete_response.status_code in [200, 204]:
                            self.log_message(f"✅ Successfully banned: {champion_name} (step 2 complete)")
                            success = True
                            self.ban_completed = True
                            
                            # Change combo box to green success state briefly
                            self.ban_combo.setStyleSheet("""
                                QComboBox {
                                    background-color: #153626;
                                    border: 2px solid #3CB371;
                                    border-radius: 4px;
                                    padding: 8px;
                                    font-size: 11pt;
                                    color: #FFFFFF;
                                    font-weight: bold;
                                }
                            """)
                            QApplication.processEvents()  # Update UI immediately
                            
                            # Reset styling after a short delay
                            QTimer.singleShot(1500, lambda: self.ban_combo.setStyleSheet("""
                                QComboBox {
                                    background-color: #1E2328;
                                    border: 1px solid #3C3C3C;
                                    border-radius: 4px;
                                    padding: 6px;
                                    color: #F0E6D2;
                                }
                            """))
                        else:
                            self.log_message(f"⚠️ Failed step 2: {complete_response.status_code}")
                    else:
                        self.log_message(f"⚠️ Failed step 1: {interim_response.status_code}")
                except Exception as e:
                    self.log_message(f"⚠️ Error with alternative method: {str(e)}")
            
            # Another alternative: using intent
            if not success:
                try:
                    self.log_message("🔄 Trying intent method...")
                    intent_response = requests.patch(
                        f"{self.base_url}/lol-champ-select/v1/session/my-selection", 
                        headers=self.auth_header, 
                        json={"championId": champion_id, "banIntentSquareId": champion_id}, 
                        verify=False,
                        timeout=5
                    )
                    
                    if intent_response.status_code in [200, 204]:
                        self.log_message(f"✅ Set ban intent for {champion_name}. Try clicking the champion or the lock button.")
                        
                        # Visual partial success feedback
                        self.ban_combo.setStyleSheet("""
                            QComboBox {
                                background-color: #155051;
                                border: 2px solid #0AC8B9;
                                border-radius: 4px;
                                padding: 8px;
                                font-size: 11pt;
                                color: #FFFFFF;
                            }
                        """)
                        
                        # Add a hint tooltip to the screen
                        hint_message = QMessageBox(self)
                        hint_message.setWindowTitle("Ban Intent Set")
                        hint_message.setText(f"Ban intent set for {champion_name}.\nYou may need to manually click the champion or lock button in the client.")
                        hint_message.setIcon(QMessageBox.Information)
                        hint_message.setStyleSheet("""
                            QMessageBox {
                                background-color: #0A1428;
                                color: #F0E6D2;
                            }
                            QMessageBox QLabel {
                                color: #F0E6D2;
                                font-size: 12px;
                            }
                            QPushButton {
                                background-color: #0A323C;
                                color: #FFFFFF;
                                border: 1px solid #0AC8B9;
                                border-radius: 4px;
                                padding: 8px 12px;
                                font-weight: bold;
                            }
                            QPushButton:hover {
                                background-color: #0A6270;
                                border: 1px solid #0AC8B9;
                            }
                        """)
                        
                        # Show the hint non-blocking
                        QTimer.singleShot(100, lambda: hint_message.show())
                        
                        # Reset styling after a short delay
                        QTimer.singleShot(3000, lambda: self.ban_combo.setStyleSheet("""
                            QComboBox {
                                background-color: #1E2328;
                                border: 1px solid #3C3C3C;
                                border-radius: 4px;
                                padding: 6px;
                                color: #F0E6D2;
                            }
                        """))
                    else:
                        self.log_message(f"⚠️ Intent method failed: {intent_response.status_code}")
                except Exception as e:
                    self.log_message(f"⚠️ Error with intent method: {str(e)}")
            
            if not success:
                self.log_message(f"❌ Failed to ban champion after trying all methods.")
                
                # Visual error feedback
                self.ban_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #4B1113;
                        border: 1px solid #CB2E2E;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """)
                
                # Reset styling after a short delay
                QTimer.singleShot(1500, lambda: self.ban_combo.setStyleSheet("""
                    QComboBox {
                        background-color: #1E2328;
                        border: 1px solid #3C3C3C;
                        border-radius: 4px;
                        padding: 6px;
                        color: #F0E6D2;
                    }
                """))

        except Exception as e:
            self.log_message(f"❌ Error banning champion: {str(e)}")
            
            # Reset styling in case of error
            self.ban_combo.setStyleSheet("""
                QComboBox {
                    background-color: #1E2328;
                    border: 1px solid #3C3C3C;
                    border-radius: 4px;
                    padding: 6px;
                    color: #F0E6D2;
                }
            """)

    def show_notification(self, title, message, type="info", duration=3000):
        """Show a stylized pop-up notification"""
        # Create notification widget
        notification = QFrame(self)
        notification.setFrameShape(QFrame.StyledPanel)
        notification.setFixedWidth(350)
        notification.setMinimumHeight(100)
        
        # Set style based on notification type
        if type == "success":
            notification.setStyleSheet("""
                QFrame {
                    background-color: #153626;
                    border: 2px solid #3CB371;
                    border-radius: 8px;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #FFFFFF;
                }
            """)
            icon_text = "✅"
        elif type == "error":
            notification.setStyleSheet("""
                QFrame {
                    background-color: #4B1113;
                    border: 2px solid #CB2E2E;
                    border-radius: 8px;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #FFFFFF;
                }
            """)
            icon_text = "❌"
        elif type == "warning":
            notification.setStyleSheet("""
                QFrame {
                    background-color: #3A2200;
                    border: 2px solid #F0A500;
                    border-radius: 8px;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #FFFFFF;
                }
            """)
            icon_text = "⚠️"
        else:  # info
            notification.setStyleSheet("""
                QFrame {
                    background-color: #0A323C;
                    border: 2px solid #0AC8B9;
                    border-radius: 8px;
                    color: #FFFFFF;
                }
                QLabel {
                    color: #FFFFFF;
                }
            """)
            icon_text = "ℹ️"
        
        # Layout for notification
        layout = QHBoxLayout(notification)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icon
        icon_label = QLabel(icon_text)
        icon_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(icon_label)
        
        # Text content
        text_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(message_label)
        layout.addLayout(text_layout, 1)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #FFFFFF;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
            }
        """)
        close_btn.clicked.connect(notification.deleteLater)
        layout.addWidget(close_btn)
        
        # Position notification in the bottom right
        notification.setParent(self)
        notification.show()
        x = self.width() - notification.width() - 20
        y = self.height() - notification.height() - 20
        notification.move(x, y)
        
        # Fade in animation
        notification.setWindowOpacity(0)
        for i in range(1, 11):
            notification.setWindowOpacity(i/10)
            QApplication.processEvents()
            time.sleep(0.02)
        
        # Auto close after duration
        QTimer.singleShot(duration, lambda: self.fade_out_notification(notification))
        
        return notification

    def fade_out_notification(self, notification):
        """Fade out and delete notification"""
        try:
            # Fade out animation
            for i in range(10, -1, -1):
                notification.setWindowOpacity(i/10)
                QApplication.processEvents()
                time.sleep(0.02)
            notification.deleteLater()
        except:
            # If notification was already closed
            pass

def main():
    app = QApplication(sys.argv)
    ex = LOLChampionSelectApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()