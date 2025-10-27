import sys
import os
import json
import base64
import urllib3
import requests
import websocket
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from PIL import Image, ImageTk
import io
import re
from datetime import datetime

class ModernTheme:
    """Tema moderno migliorato per l'applicazione."""
    # Colori principali del tema LoL con palette estesa
    BG_PRIMARY = "#0f1419"        # Sfondo principale più scuro
    BG_SECONDARY = "#1e2328"      # Sfondo secondario
    BG_TERTIARY = "#292e38"       # Sfondo terziario per elementi interattivi
    BG_HOVER = "#3c3c41"          # Sfondo hover
    
    TEXT_PRIMARY = "#f0e6d2"      # Testo principale (oro chiaro)
    TEXT_SECONDARY = "#c8aa6e"    # Testo secondario (oro)
    TEXT_MUTED = "#a09b8c"        # Testo attenuato
    TEXT_DARK = "#5bc0de"         # Testo su sfondo scuro
    
    ACCENT_PRIMARY = "#c8aa6e"    # Accent principale (oro LoL)
    ACCENT_SECONDARY = "#0596aa"  # Accent secondario (ciano)
    ACCENT_HOVER = "#cdbe91"      # Accent hover
    
    SUCCESS = "#0f2027"           # Verde scuro per successo
    SUCCESS_TEXT = "#00f5ff"      # Verde chiaro per testo successo
    ERROR = "#3c1518"             # Rosso scuro per errore
    ERROR_TEXT = "#ff6b6b"        # Rosso chiaro per testo errore
    WARNING = "#463b00"           # Giallo scuro per warning
    WARNING_TEXT = "#ffd700"      # Giallo per testo warning
    
    # Stati presenza amici
    ONLINE = "#00f5ff"            # Ciano brillante per online
    AWAY = "#ffd700"              # Oro per away
    BUSY = "#ff6b6b"              # Rosso per busy/dnd
    OFFLINE = "#5a5a5a"           # Grigio per offline
    
    # Gradients e shadows
    GRADIENT_START = "#1e2328"
    GRADIENT_END = "#0f1419"
    SHADOW_COLOR = "#000000"
    
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_HEADER = 14
    
    @classmethod
    def apply(cls, root):
        """Applica il tema moderno migliorato."""
        style = ttk.Style()
        
        # Tema di base
        style.theme_use('clam')
        
        # Configurazioni globali
        style.configure(".",
            background=cls.BG_PRIMARY,
            foreground=cls.TEXT_PRIMARY,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL),
            borderwidth=0,
            focuscolor='none')
        
        # Frame configurations
        style.configure("TFrame", 
            background=cls.BG_PRIMARY,
            relief='flat')
        
        style.configure("Card.TFrame",
            background=cls.BG_SECONDARY,
            relief='flat',
            borderwidth=1)
        
        # LabelFrame con stile migliorato
        style.configure("TLabelframe", 
            background=cls.BG_PRIMARY,
            foreground=cls.TEXT_SECONDARY,
            borderwidth=1,
            relief='solid')
        
        style.configure("TLabelframe.Label", 
            background=cls.BG_PRIMARY, 
            foreground=cls.ACCENT_PRIMARY,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_LARGE, "bold"))
        
        # Labels
        style.configure("TLabel", 
            background=cls.BG_PRIMARY, 
            foreground=cls.TEXT_PRIMARY)
        
        style.configure("Header.TLabel",
            background=cls.BG_PRIMARY,
            foreground=cls.ACCENT_PRIMARY,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_HEADER, "bold"))
        
        style.configure("Muted.TLabel",
            background=cls.BG_PRIMARY,
            foreground=cls.TEXT_MUTED,
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_SMALL))
        
        style.configure("StatusBar.TLabel", 
            background=cls.BG_SECONDARY, 
            foreground=cls.TEXT_PRIMARY,
            relief='flat',
            padding=(10, 5))
        
        # Buttons con stile migliorato
        style.configure("TButton", 
            background=cls.ACCENT_PRIMARY, 
            foreground=cls.BG_PRIMARY,
            padding=(15, 8),
            font=(cls.FONT_FAMILY, cls.FONT_SIZE_NORMAL, "bold"),
            focuscolor='none')
        
        style.map("TButton",
            background=[
                ('active', cls.ACCENT_HOVER), 
                ('pressed', cls.ACCENT_SECONDARY),
                ('disabled', cls.BG_HOVER)
            ],
            foreground=[
                ('active', cls.BG_PRIMARY),
                ('disabled', cls.TEXT_MUTED)
            ],
            relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        
        # Secondary button style
        style.configure("Secondary.TButton",
            background=cls.BG_TERTIARY,
            foreground=cls.TEXT_PRIMARY,
            padding=(12, 6))
        
        style.map("Secondary.TButton",
            background=[
                ('active', cls.BG_HOVER),
                ('pressed', cls.BG_SECONDARY)
            ])
        
        # Entry fields con stile migliorato
        style.configure("TEntry", 
            fieldbackground=cls.BG_TERTIARY, 
            foreground=cls.TEXT_PRIMARY,
            bordercolor=cls.ACCENT_PRIMARY,
            insertcolor=cls.TEXT_PRIMARY,
            padding=(10, 8),
            relief='flat')
        
        style.map("TEntry",
            focuscolor=[('focus', cls.ACCENT_PRIMARY)],
            bordercolor=[('focus', cls.ACCENT_HOVER)])
        
        # Search entry
        style.configure("Search.TEntry",
            fieldbackground=cls.BG_SECONDARY,
            padding=(10, 6))
        
        # Scrollbar migliorato
        style.configure("TScrollbar", 
            background=cls.BG_TERTIARY,
            troughcolor=cls.BG_SECONDARY,
            borderwidth=0,
            arrowsize=12,
            width=12)
        
        style.map("TScrollbar",
            background=[('active', cls.BG_HOVER)],
            arrowcolor=[('active', cls.ACCENT_PRIMARY)])
        
        # Combobox
        style.configure("TCombobox", 
            fieldbackground=cls.BG_TERTIARY, 
            foreground=cls.TEXT_PRIMARY,
            background=cls.BG_TERTIARY,
            arrowcolor=cls.ACCENT_PRIMARY)
        
        # PanedWindow
        style.configure("TPanedwindow", 
            background=cls.BG_PRIMARY)
        
        # Separator
        style.configure("TSeparator",
            background=cls.BG_HOVER)
        
        # Menu configurations
        root.option_add("*Menu.background", cls.BG_SECONDARY)
        root.option_add("*Menu.foreground", cls.TEXT_PRIMARY)
        root.option_add("*Menu.selectColor", cls.ACCENT_PRIMARY)
        root.option_add("*Menu.activeBackground", cls.BG_HOVER)
        root.option_add("*Menu.activeForeground", cls.ACCENT_PRIMARY)

class StatusIndicator(tk.Canvas):
    """Widget personalizzato per indicatori di stato."""
    def __init__(self, parent, status="offline", size=12, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        highlightthickness=0, **kwargs)
        self.size = size
        self.status = status
        self.configure(bg=ModernTheme.BG_PRIMARY)
        self.draw_status()
    
    def draw_status(self):
        self.delete("all")
        colors = {
            "online": ModernTheme.ONLINE,
            "away": ModernTheme.AWAY,
            "busy": ModernTheme.BUSY,
            "dnd": ModernTheme.BUSY,
            "offline": ModernTheme.OFFLINE
        }
        
        color = colors.get(self.status, ModernTheme.OFFLINE)
        margin = 2
        
        # Disegna il cerchio con un effetto glow
        self.create_oval(margin, margin, 
                        self.size - margin, self.size - margin,
                        fill=color, outline=color, width=1)
    
    def update_status(self, new_status):
        self.status = new_status
        self.draw_status()

class FriendListItem(ttk.Frame):
    """Widget personalizzato per elementi della lista amici."""
    def __init__(self, parent, friend_data, callback, **kwargs):
        super().__init__(parent, **kwargs)
        self.friend_data = friend_data
        self.callback = callback
        self.selected = False
        
        self.configure(style="Card.TFrame")
        self.configure(padding=(10, 8))
        
        # Crea il layout
        self.create_widgets()
        self.bind_events()
    
    def create_widgets(self):
        # Container principale
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Status indicator
        self.status_indicator = StatusIndicator(
            main_frame, 
            status=self.friend_data.get('availability', 'offline'),
            bg=ModernTheme.BG_SECONDARY
        )
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        # Info container
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Nome amico
        name = self.friend_data.get('name', 'Sconosciuto')
        self.name_label = ttk.Label(
            info_frame, 
            text=name,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL, "bold")
        )
        self.name_label.pack(anchor=tk.W)
        
        # Status text
        status_text = self.get_status_text()
        self.status_label = ttk.Label(
            info_frame, 
            text=status_text,
            style="Muted.TLabel"
        )
        self.status_label.pack(anchor=tk.W)
    
    def get_status_text(self):
        status = self.friend_data.get('availability', 'offline')
        status_map = {
            'online': 'Online',
            'away': 'Assente',
            'busy': 'Occupato',
            'dnd': 'Non disturbare',
            'offline': 'Offline'
        }
        return status_map.get(status, 'Sconosciuto')
    
    def bind_events(self):
        """Bind eventi per interazioni."""
        widgets = [self, self.status_indicator, self.name_label, self.status_label]
        for widget in widgets:
            widget.bind("<Button-1>", self.on_click)
            widget.bind("<Enter>", self.on_hover_enter)
            widget.bind("<Leave>", self.on_hover_leave)
    
    def on_click(self, event):
        self.callback(self.friend_data)
        self.set_selected(True)
    
    def on_hover_enter(self, event):
        if not self.selected:
            self.configure(style="Card.TFrame")
            # Effetto hover leggero
    
    def on_hover_leave(self, event):
        if not self.selected:
            self.configure(style="Card.TFrame")
    
    def set_selected(self, selected):
        self.selected = selected
        if selected:
            self.configure(relief='solid', borderwidth=2)
        else:
            self.configure(relief='flat', borderwidth=1)

class LeagueMessenger:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        
        # Applica il tema moderno
        ModernTheme.apply(root)
        
        # Imposta l'icona dell'applicazione
        self.set_app_icon()
        
        # Disabilita gli avvertimenti SSL
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Variabili di connessione
        self.auth_token = None
        self.port = None
        self.protocol = None
        self.connection_status = False
        self.friends_list = []
        self.ws = None
        self.ws_connected = False
        self.current_summoner = None
        
        # UI state
        self.selected_friend_widget = None
        self.friend_widgets = []
        
        # Crea il menu e l'interfaccia
        self.create_menu()
        self.create_ui()
        
        # Auto-connetti
        self.root.after(1000, self.connect_to_client)
    
    def setup_window(self):
        """Configura la finestra principale."""
        self.root.title("League of Legends Messenger")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.configure(bg=ModernTheme.BG_PRIMARY)
        
        # Centra la finestra
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1000 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"1000x700+{x}+{y}")
    
    def set_app_icon(self):
        """Imposta l'icona dell'applicazione migliorata."""
        # Icona migliorata in Base64 (più grande e dettagliata)
        icon_data = """
        iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAACXBIWXMAAA7EAAAOxAGVKw4bAAAF
        GUlEQVR4nO2Xa0xTVxjHf+fec9v3QqG0tLa8pLwfKsimGzAQdcuWbNk+zCzOJcsHz+bMsmWJH8yy
        JX6ZyczMzD6YL2bMkc1k0YgzKpsiCIKitFBaoC20tLT3fe89+0AHKLQUdckS/8lJcu+9//M7z3nO
        eQ6c/2cQQgghB8uyLMdxnMhxnJhlWRb+D4CiKEEQhFQikbiYSqXOZrPZYqFQKNXr9Uo4HJYoijJE
        URRFURRF0zTN8zyPPM+LLMuKDMOIDMOIHMexGIZhLcsyNsMwNsdxIsdxIsuyYjgcDsVisaAsy4Ei
        y/KyoihBVVW/pml+TdMcqqo6VFX1aJrm0TTNF41Gp6PRqJvneRchBOB5HiGELMuyIgiCKAiCyPO8
        yLKsKIpiWFEUP8/zPkVRfLqu+zVd92ma5tE0zaOqqkNVVaeqqg5VVZ2qqjo0TXOoqupQVdWpKIpT
        lmWHLMsORVEcpmlbFEVZoiiKYlmWZRmGwVarhW3bFs/zouU4NmYZBrIsizNM08SGYSBNU4RhGIZp
        mmCapmmaJk4kEhBFEYZhAI7jIMsyVFWFYRhQVRWyLENRFMiyvHA2VVWh6zq0LAt6OwuGYcBxHFiW
        RZZlASMEYYQxwhgjhBHCGGOEMEYYI4QQxgghhBHCCGOMMMYIY4wxxhgjhDHGGCOEEUIIY4wRQghj
        jDDGGCOEEMYYI4wxxhgjhBHCGGOMEMYYI4wxxhhjjDFCGGOMEcYYY4wxxgghhDHGGCOEEEIYY4wx
        xhhhjDFGCCGMMcYYI4QQxhhjjDFCCGOMMcYYY4wRQghjjDHGGGOMEcYYY4wxxgghhDHGGGOMEUII
        Y4wxxhhjjBFCCGOMMcYYI4QQxhhjjDHGGCOEMMYYY4wxxgghhDHGGGOMEUII49Pp9Ct6vf5VPp9/
        uVAovFoslktms/nSQCDwUjQa7edFUQQ4jofT6YTH44Hf74fD4YDH40G5XEaxWESj0UCz2YSmaWBZ
        FqqqQlVVJJNJJJNJpFIppNNpFAoFFItFFItFFIvFzlg8Hi9VKpVrvV6vr1QqvdZqtd5oNBrLZrPZ
        TCYT6HQ6gV6vF+z3+wO9Xm+w2+0Odrvd4na7HWazucztdju73e5Ap9MZ6PV6A51OZ7Db7Q70+/1B
        t9sd7Ha7w263O9jtdoc6nU6n0+kMer3eYLfbHex0OsNOp+Pv9Xq+brc76PV6/l6v5+90Ov5ut+vv
        dDr+Tqfj73Q6/k6n4+90Ov5ut+vvdDr+drtt73a79k6nY2+322632203yzIsyzKyLIuyLMssy7Is
        y4qyLMuyLMuyLCvKsizLsizLsizLsqwsy7Isy7Isy7IsK8qyLMuyLMuyLCvKsizKsizKsiyznOd5
        XhAEQeB5XhAEQeB5XuB5XhAEQeB5XhAEQeB5XhAEQeB5XhAEQeB5XhAEQRB4nhcEQRAEQRAEQRAE
        nud5QRAEQRAEQRAEnud5QRAEQRAEQRAEnud5gVKr1Q7t7e0/19fXf6Ovr/9EX1//jv7+/rv7+vrO
        9vb2nu3p6f3b1dX1t6ur6+/u7u6/u7q6zu7s7Py7ra3tv7u6uv/u7Oz8u6Oj7b/b29vObmtr+7ut
        re1sd3f332az+Y9Go/FUvV5/qlar/V6pVH4rl8u/lcvl36rV6m+1Wu23er3+W6PR+K1Wq/1Wq9V+
        q9frv1Wr1d+q1epvlUrltwQhBK6vrz9jGMYT8Xi8L5FI9CUSiV4mk+lNp9O9mUymN51O96bT6d50
        Ot2bTqd7U6lUbyqV6k0mk72JRKInHo/3JBKJnmQy2ZtMJnuTyWRvMpnsTSQSvfF4vCcWi/XEYrGe
        WCzWG4vFehOJRG88Hu9LpVJ9qVSqL51O96bT6b50Ot2XTqf7MplMXyaT6U2n072ZTKYvnU735fP5
        vlwu15fP5/tyuVxfNpvty2azfdlsti+bzfZls9m+bDbbl8lk+jKZTF8mk+nLZDJ92Wy2L5fL9eXz
        +b5CodBXKBT6isXifxr8C5nXrv8CYWX5AAAAAElFTkSuQmCC
        """
        
        try:
            icon_bytes = base64.b64decode(icon_data)
            icon_image = Image.open(io.BytesIO(icon_bytes))
            icon_photo = ImageTk.PhotoImage(icon_image)
            self.root.iconphoto(True, icon_photo)
        except Exception as e:
            print(f"Errore nel caricamento dell'icona: {e}")
    
    def create_menu(self):
        """Crea il menu dell'applicazione."""
        menu_bar = tk.Menu(self.root, 
                          bg=ModernTheme.BG_SECONDARY, 
                          fg=ModernTheme.TEXT_PRIMARY,
                          activebackground=ModernTheme.BG_HOVER,
                          activeforeground=ModernTheme.ACCENT_PRIMARY)
        
        # Menu File
        file_menu = tk.Menu(menu_bar, tearoff=0, 
                           bg=ModernTheme.BG_SECONDARY, 
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.BG_HOVER,
                           activeforeground=ModernTheme.ACCENT_PRIMARY)
        file_menu.add_command(label="🔗 Connetti al client", command=self.connect_to_client)
        file_menu.add_command(label="🔄 Aggiorna lista amici", command=self.refresh_friends)
        file_menu.add_separator()
        file_menu.add_command(label="⚙️ Impostazioni", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="❌ Esci", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # Menu Visualizza
        view_menu = tk.Menu(menu_bar, tearoff=0,
                           bg=ModernTheme.BG_SECONDARY,
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.BG_HOVER,
                           activeforeground=ModernTheme.ACCENT_PRIMARY)
        view_menu.add_command(label="🌙 Tema scuro", state="disabled")
        view_menu.add_command(label="📊 Statistiche connessione", command=self.show_connection_stats)
        menu_bar.add_cascade(label="Visualizza", menu=view_menu)
        
        # Menu Aiuto
        help_menu = tk.Menu(menu_bar, tearoff=0,
                           bg=ModernTheme.BG_SECONDARY,
                           fg=ModernTheme.TEXT_PRIMARY,
                           activebackground=ModernTheme.BG_HOVER,
                           activeforeground=ModernTheme.ACCENT_PRIMARY)
        help_menu.add_command(label="❓ Guida", command=self.show_help)
        help_menu.add_command(label="ℹ️ Informazioni", command=self.show_about)
        menu_bar.add_cascade(label="Aiuto", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def create_ui(self):
        """Crea l'interfaccia utente migliorata e moderna."""
        # Container principale con padding
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header con informazioni utente
        self.create_header()
        
        # Separator
        separator = ttk.Separator(self.main_container, orient='horizontal')
        separator.pack(fill=tk.X, pady=(0, 10))
        
        # Content area con PanedWindow
        self.paned_window = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Pannello sinistro (lista amici)
        self.create_friends_panel()
        
        # Pannello destro (chat)
        self.create_chat_panel()
        
        # Status bar
        self.create_status_bar()
        
        # Inizializza stato UI
        self.current_friend = None
        self.current_friend_id = None
        
        # Configurazione avanzata chat
        self.setup_chat_formatting()
    
    def create_header(self):
        """Crea l'header dell'applicazione."""
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Titolo
        title_label = ttk.Label(
            header_frame, 
            text="League of Legends Messenger",
            style="Header.TLabel"
        )
        title_label.pack(side=tk.LEFT)
        
        # Info utente (verrà popolato dopo la connessione)
        self.user_info_frame = ttk.Frame(header_frame)
        self.user_info_frame.pack(side=tk.RIGHT)
        
        self.user_name_label = ttk.Label(
            self.user_info_frame, 
            text="Non connesso",
            style="Muted.TLabel"
        )
        self.user_name_label.pack(side=tk.RIGHT)
        
        # Status indicator per la connessione
        self.connection_indicator = StatusIndicator(
            self.user_info_frame, 
            status="offline",
            bg=ModernTheme.BG_PRIMARY
        )
        self.connection_indicator.pack(side=tk.RIGHT, padx=(0, 5))
    
    def create_friends_panel(self):
        """Crea il pannello degli amici migliorato."""
        friends_frame = ttk.LabelFrame(self.paned_window, text="👥 Amici Online")
        self.paned_window.add(friends_frame, weight=1)
        
        # Header con ricerca e contatori
        header_frame = ttk.Frame(friends_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Barra di ricerca migliorata
        search_container = ttk.Frame(header_frame)
        search_container.pack(fill=tk.X, pady=(0, 10))
        
        search_label = ttk.Label(search_container, text="🔍")
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_friends)
        self.search_entry = ttk.Entry(
            search_container, 
            textvariable=self.search_var,
            style="Search.TEntry",
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL)
        )
        self.search_entry.pack(fill=tk.X, expand=True)
        
        # Contatore amici
        self.friends_counter_label = ttk.Label(
            header_frame, 
            text="0 amici online",
            style="Muted.TLabel"
        )
        self.friends_counter_label.pack(anchor=tk.W)
        
        # Container scrollabile per la lista amici
        self.create_friends_list_container(friends_frame)
        
        # Pulsanti di controllo
        controls_frame = ttk.Frame(friends_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        refresh_button = ttk.Button(
            controls_frame, 
            text="🔄 Aggiorna",
            command=self.refresh_friends,
            style="Secondary.TButton"
        )
        refresh_button.pack(fill=tk.X)
    
    def create_friends_list_container(self, parent):
        """Crea il container scrollabile per la lista amici."""
        # Frame con scrollbar
        list_container = ttk.Frame(parent)
        list_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Canvas per scrolling personalizzato
        self.friends_canvas = tk.Canvas(
            list_container,
            bg=ModernTheme.BG_PRIMARY,
            highlightthickness=0,
            relief='flat'
        )
        
        self.friends_scrollbar = ttk.Scrollbar(
            list_container, 
            orient="vertical", 
            command=self.friends_canvas.yview
        )
        
        self.friends_scrollable_frame = ttk.Frame(self.friends_canvas)
        
        # Configura scrolling
        self.friends_scrollable_frame.bind(
            "<Configure>",
            lambda e: self.friends_canvas.configure(scrollregion=self.friends_canvas.bbox("all"))
        )
        
        self.friends_canvas.create_window((0, 0), window=self.friends_scrollable_frame, anchor="nw")
        self.friends_canvas.configure(yscrollcommand=self.friends_scrollbar.set)
        
        # Pack elements
        self.friends_canvas.pack(side="left", fill="both", expand=True)
        self.friends_scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.friends_canvas.bind("<MouseWheel>", self.on_mouse_wheel)
    
    def on_mouse_wheel(self, event):
        """Gestisce lo scroll della lista amici."""
        self.friends_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def create_chat_panel(self):
        """Crea il pannello della chat migliorato."""
        chat_frame = ttk.LabelFrame(self.paned_window, text="💬 Chat")
        self.paned_window.add(chat_frame, weight=2)
        
        # Header chat con info amico selezionato
        self.create_chat_header(chat_frame)
        
        # Area messaggi
        self.create_message_area(chat_frame)
        
        # Area di input
        self.create_input_area(chat_frame)
    
    def create_chat_header(self, parent):
        """Crea l'header della chat."""
        self.chat_header = ttk.Frame(parent)
        self.chat_header.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Info amico corrente
        friend_info_frame = ttk.Frame(self.chat_header)
        friend_info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.current_friend_label = ttk.Label(
            friend_info_frame, 
            text="Seleziona un amico per iniziare a chattare",
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_LARGE, "bold")
        )
        self.current_friend_label.pack(side=tk.LEFT)
        
        # Status indicator per l'amico
        self.friend_status_frame = ttk.Frame(self.chat_header)
        self.friend_status_frame.pack(side=tk.RIGHT)
        
        self.friend_status_indicator = StatusIndicator(
            self.friend_status_frame, 
            status="offline",
            bg=ModernTheme.BG_PRIMARY
        )
        
        self.friend_status_label = ttk.Label(
            self.friend_status_frame, 
            text="",
            style="Muted.TLabel"
        )
        
        # Separator per header
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, padx=10, pady=5)
    
    def create_message_area(self, parent):
        """Crea l'area dei messaggi."""
        message_container = ttk.Frame(parent)
        message_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.message_area = scrolledtext.ScrolledText(
            message_container,
            bg=ModernTheme.BG_SECONDARY,
            fg=ModernTheme.TEXT_PRIMARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL),
            relief='flat',
            padx=15,
            pady=15,
            state=tk.DISABLED,
            wrap=tk.WORD,
            selectbackground=ModernTheme.ACCENT_SECONDARY,
            insertbackground=ModernTheme.TEXT_PRIMARY,
            borderwidth=0
        )
        self.message_area.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar styling
        scrollbar = self.message_area.vbar
        scrollbar.config(
            bg=ModernTheme.BG_TERTIARY,
            troughcolor=ModernTheme.BG_SECONDARY,
            activebackground=ModernTheme.BG_HOVER
        )
    
    def create_input_area(self, parent):
        """Crea l'area di input migliorata."""
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Separator prima dell'input
        separator = ttk.Separator(parent, orient='horizontal')
        separator.pack(fill=tk.X, padx=10)
        
        # Container per input e pulsanti
        controls_frame = ttk.Frame(input_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Entry per il messaggio
        self.message_entry = ttk.Entry(
            controls_frame,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL)
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.message_entry.bind('<Return>', lambda e: self.send_message())
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())
        
        # Pulsante invia
        send_button = ttk.Button(
            controls_frame, 
            text="📤 Invia",
            command=self.send_message
        )
        send_button.pack(side=tk.RIGHT)
        
        # Shortcuts info
        shortcuts_label = ttk.Label(
            input_frame, 
            text="💡 Premi Invio per inviare • Ctrl+Invio per andare a capo",
            style="Muted.TLabel"
        )
        shortcuts_label.pack(anchor=tk.W, pady=(5, 0))
    
    def create_status_bar(self):
        """Crea la status bar migliorata."""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_bar = ttk.Label(
            status_frame, 
            text="🔴 Non connesso - Avvio in corso...", 
            style="StatusBar.TLabel"
        )
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Timestamp
        self.timestamp_label = ttk.Label(
            status_frame,
            text="",
            style="StatusBar.TLabel"
        )
        self.timestamp_label.pack(side=tk.RIGHT)
        
        # Aggiorna timestamp periodicamente
        self.update_timestamp()
    
    def update_timestamp(self):
        """Aggiorna il timestamp nella status bar."""
        now = datetime.now().strftime("%H:%M:%S")
        self.timestamp_label.config(text=now)
        self.root.after(1000, self.update_timestamp)
    
    def setup_chat_formatting(self):
        """Configura la formattazione avanzata per i messaggi."""
        # Tags per diversi tipi di messaggio
        self.message_area.tag_configure(
            "sent", 
            foreground=ModernTheme.ACCENT_PRIMARY,
            justify="right",
            lmargin1=100,
            lmargin2=100,
            rmargin=20,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL, "bold")
        )
        
        self.message_area.tag_configure(
            "received", 
            foreground=ModernTheme.TEXT_PRIMARY,
            justify="left",
            lmargin1=20,
            lmargin2=20,
            rmargin=100,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL)
        )
        
        self.message_area.tag_configure(
            "system", 
            foreground=ModernTheme.TEXT_MUTED,
            justify="center",
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SMALL, "italic")
        )
        
        self.message_area.tag_configure(
            "timestamp",
            foreground=ModernTheme.TEXT_MUTED,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SMALL)
        )
        
        self.message_area.tag_configure(
            "sender_name",
            foreground=ModernTheme.ACCENT_SECONDARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_SMALL, "bold")
        )
    
    # Continua con i metodi di connessione e gestione eventi...
    def connect_to_client(self):
        """Connette all'API LCU con gestione errori migliorata."""
        self.update_status("🔄 Tentativo di connessione al client...")
        
        try:
            lockfile_path = self.get_lockfile_path()
            
            if not lockfile_path or not os.path.isfile(lockfile_path):
                self.update_status("❌ Client League of Legends non trovato")
                self.connection_indicator.update_status("offline")
                return False
            
            with open(lockfile_path, 'r') as lockfile:
                data = lockfile.read()
                process_name, pid, port, password, protocol = data.split(':')
            
            self.port = port
            self.protocol = protocol
            self.auth_token = base64.b64encode(f"riot:{password}".encode()).decode()
            
            # Verifica la connessione
            self.update_status("🔗 Verifica credenziali...")
            response = self.make_request('/lol-summoner/v1/current-summoner')
            
            if response and response.status_code == 200:
                self.current_summoner = response.json()
                display_name = self.current_summoner['displayName']
                
                self.update_status(f"✅ Connesso come {display_name}")
                self.connection_status = True
                self.connection_indicator.update_status("online")
                self.user_name_label.config(text=f"👤 {display_name}")
                
                # Avvia servizi
                self.refresh_friends()
                self.start_websocket()
                return True
            else:
                self.update_status("❌ Autenticazione fallita")
                self.connection_indicator.update_status("offline")
                return False
                
        except Exception as e:
            error_msg = f"❌ Errore di connessione: {str(e)[:50]}"
            self.update_status(error_msg)
            self.connection_indicator.update_status("offline")
            messagebox.showerror("Errore di Connessione", 
                               f"Impossibile connettersi al client:\n{str(e)}")
            return False
    
    def get_lockfile_path(self):
        """Trova il percorso del lockfile con ricerca migliorata."""
        if hasattr(self, 'install_path') and os.path.exists(
            os.path.join(self.install_path, 'lockfile')):
            return os.path.join(self.install_path, 'lockfile')
        
        # Percorsi comuni di installazione
        default_paths = [
            "C:/Riot Games/League of Legends",
            "D:/Riot Games/League of Legends", 
            "E:/Riot Games/League of Legends",
            "C:/Program Files/Riot Games/League of Legends",
            "C:/Program Files (x86)/Riot Games/League of Legends",
            "/Applications/League of Legends.app/Contents/LoL",  # macOS
            os.path.expanduser("~/Applications/League of Legends.app/Contents/LoL")  # macOS user
        ]
        
        # Cerca nelle posizioni standard
        for path in default_paths:
            lockfile_path = os.path.join(path, 'lockfile')
            if os.path.exists(lockfile_path):
                self.install_path = path
                return lockfile_path
        
        # Chiedi all'utente se non trovato
        result = messagebox.askyesno(
            "Percorso non trovato",
            "Non è stato possibile trovare automaticamente League of Legends.\n"
            "Vuoi selezionare manualmente la cartella di installazione?"
        )
        
        if result:
            self.install_path = filedialog.askdirectory(
                title="Seleziona la cartella di installazione di League of Legends"
            )
            if self.install_path:
                return os.path.join(self.install_path, 'lockfile')
        
        return None
    
    def make_request(self, endpoint, method='GET', data=None):
        """Effettua richieste API con gestione errori migliorata."""
        if not self.port or not self.auth_token:
            return None
        
        url = f"{self.protocol}://127.0.0.1:{self.port}{endpoint}"
        headers = {
            'Authorization': f'Basic {self.auth_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, verify=False, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, verify=False, timeout=10)
            else:
                return None
            
            return response
            
        except requests.exceptions.Timeout:
            self.update_status("⏱️ Timeout richiesta - Client occupato")
            return None
        except requests.exceptions.ConnectionError:
            self.update_status("❌ Connessione persa - Client chiuso?")
            self.connection_status = False
            self.connection_indicator.update_status("offline")
            return None
        except Exception as e:
            self.update_status(f"❌ Errore API: {str(e)[:30]}")
            return None
    
    def refresh_friends(self):
        """Aggiorna la lista degli amici con UI migliorata."""
        if not self.connection_status:
            return
        
        self.update_status("🔄 Aggiornamento lista amici...")
        response = self.make_request('/lol-chat/v1/friends')
        
        if response and response.status_code == 200:
            friends_data = response.json()
            
            # Filtra e processa amici
            self.friends_list = []
            for friend in friends_data:
                if friend['availability'] != 'offline':
                    # Assicura nome valido
                    if not friend.get('name'):
                        friend['name'] = (friend.get('gameName') or 
                                        friend.get('summonerName') or 
                                        friend.get('id', 'Sconosciuto'))
                    self.friends_list.append(friend)
            
            # Ordina per stato e nome
            self.friends_list.sort(key=lambda x: (
                {'online': 0, 'away': 1, 'busy': 2, 'dnd': 2}.get(x['availability'], 3),
                x['name'].lower()
            ))
            
            self.update_friends_display()
            
            count = len(self.friends_list)
            self.update_status(f"✅ {count} amici online")
            self.friends_counter_label.config(text=f"{count} amici online")
        else:
            self.update_status("❌ Errore nel recupero amici")
    
    def update_friends_display(self, search_term=""):
        """Aggiorna il display della lista amici con widget personalizzati."""
        # Rimuovi widget esistenti
        for widget in self.friend_widgets:
            widget.destroy()
        self.friend_widgets.clear()
        
        # Crea nuovi widget
        displayed_count = 0
        for friend in self.friends_list:
            name = friend['name'].lower()
            if search_term and search_term not in name:
                continue
            
            friend_widget = FriendListItem(
                self.friends_scrollable_frame,
                friend,
                self.on_friend_selected
            )
            friend_widget.pack(fill=tk.X, pady=2, padx=5)
            self.friend_widgets.append(friend_widget)
            displayed_count += 1
        
        # Aggiorna contatore se c'è una ricerca attiva
        if search_term:
            self.friends_counter_label.config(
                text=f"{displayed_count} di {len(self.friends_list)} amici"
            )
    
    def filter_friends(self, *args):
        """Filtra la lista amici in tempo reale."""
        search_term = self.search_var.get().lower().strip()
        self.update_friends_display(search_term)
    
    def on_friend_selected(self, friend_data):
        """Gestisce la selezione di un amico."""
        # Deseleziona il widget precedente
        if self.selected_friend_widget:
            self.selected_friend_widget.set_selected(False)
        
        # Trova e seleziona il nuovo widget
        for widget in self.friend_widgets:
            if widget.friend_data['id'] == friend_data['id']:
                widget.set_selected(True)
                self.selected_friend_widget = widget
                break
        
        # Aggiorna stato corrente
        self.current_friend = friend_data
        self.current_friend_id = friend_data['id']
        
        # Aggiorna UI
        self.current_friend_label.config(text=f"💬 {friend_data['name']}")
        
        # Aggiorna status indicator
        status = friend_data['availability']
        self.friend_status_indicator.update_status(status)
        self.friend_status_indicator.pack(side=tk.RIGHT, padx=(5, 0))
        
        status_text = {
            'online': 'Online',
            'away': 'Assente', 
            'busy': 'Occupato',
            'dnd': 'Non disturbare'
        }.get(status, 'Sconosciuto')
        
        self.friend_status_label.config(text=status_text)
        self.friend_status_label.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Carica conversazione
        self.load_conversation_history()
        self.update_status(f"💬 Chat con {friend_data['name']}")
    
    def load_conversation_history(self):
        """Carica la cronologia con formattazione avanzata."""
        if not self.current_friend_id:
            return
        
        self.message_area.config(state=tk.NORMAL)
        self.message_area.delete(1.0, tk.END)
        
        try:
            response = self.make_request(f'/lol-chat/v1/conversations/{self.current_friend_id}/messages')
            
            if response and response.status_code == 200:
                messages = response.json()
                
                if not messages:
                    self.add_system_message("Nessun messaggio precedente. Inizia a chattare! 🎮")
                    return
                
                # Mostra gli ultimi 50 messaggi
                for message in messages[-50:]:
                    self.add_message_to_display(message)
                    
            elif response and response.status_code == 404:
                self.add_system_message("Nuova conversazione - Invia il primo messaggio! ✨")
            else:
                self.add_system_message("⚠️ Impossibile caricare i messaggi precedenti")
                
        except Exception as e:
            self.add_system_message(f"❌ Errore: {str(e)}")
        
        self.message_area.config(state=tk.DISABLED)
        self.message_area.see(tk.END)
    
    def add_message_to_display(self, message_data, is_new=False):
        """Aggiunge un messaggio al display con formattazione avanzata."""
        self.message_area.config(state=tk.NORMAL)
        
        is_from_me = message_data['fromId'] != self.current_friend_id
        sender_name = "Tu" if is_from_me else self.current_friend['name']
        body = message_data['body']
        
        # Timestamp se disponibile
        if 'timestamp' in message_data:
            try:
                timestamp = datetime.fromtimestamp(message_data['timestamp'] / 1000)
                time_str = timestamp.strftime("%H:%M")
            except:
                time_str = ""
        else:
            time_str = datetime.now().strftime("%H:%M")
        
        # Formattazione messaggio
        if is_from_me:
            # Messaggio inviato (allineato a destra)
            self.message_area.insert(tk.END, f"\n{time_str}  ", "timestamp")
            self.message_area.insert(tk.END, f"Tu: ", "sender_name")
            self.message_area.insert(tk.END, f"{body}\n", "sent")
        else:
            # Messaggio ricevuto (allineato a sinistra)  
            self.message_area.insert(tk.END, f"{sender_name}: ", "sender_name")
            self.message_area.insert(tk.END, f"  {time_str}\n", "timestamp")
            self.message_area.insert(tk.END, f"{body}\n", "received")
        
        # Se è un nuovo messaggio, evidenzialo brevemente
        if is_new:
            self.message_area.see(tk.END)
            # Effetto di evidenziazione
            self.root.after(100, lambda: self.message_area.see(tk.END))
        
        self.message_area.config(state=tk.DISABLED)
    
    def add_system_message(self, text):
        """Aggiunge un messaggio di sistema."""
        self.message_area.config(state=tk.NORMAL)
        self.message_area.insert(tk.END, f"\n{text}\n\n", "system")
        self.message_area.config(state=tk.DISABLED)
        self.message_area.see(tk.END)
    
    def send_message(self):
        """Invia un messaggio con validazione migliorata."""
        if not self.current_friend_id:
            messagebox.showinfo("Attenzione", "Seleziona prima un amico dalla lista! 👥")
            return
        
        message = self.message_entry.get().strip()
        if not message:
            return
        
        # Validazione lunghezza messaggio
        if len(message) > 1000:
            messagebox.showwarning("Messaggio troppo lungo", 
                                 "Il messaggio deve essere inferiore a 1000 caratteri.")
            return
        
        data = {"type": "chat", "body": message}
        
        self.update_status("📤 Invio messaggio...")
        response = self.make_request(
            f'/lol-chat/v1/conversations/{self.current_friend_id}/messages', 
            'POST', data
        )
        
        if response and response.status_code == 200:
            # Pulisci input
            self.message_entry.delete(0, tk.END)
            
            # Aggiungi messaggio al display
            fake_message = {
                'fromId': 'me',
                'body': message,
                'timestamp': int(datetime.now().timestamp() * 1000)
            }
            self.add_message_to_display(fake_message, is_new=True)
            
            self.update_status("✅ Messaggio inviato")
        else:
            error_msg = "❌ Impossibile inviare il messaggio"
            self.update_status(error_msg)
            messagebox.showerror("Errore Invio", "Impossibile inviare il messaggio. Riprova.")
    
    def start_websocket(self):
        """Avvia WebSocket con gestione migliorata."""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                event_data = data[2]
                
                # Gestisci eventi di chat
                if event_data['uri'] == '/lol-chat/v1/conversations':
                    if (self.current_friend_id and 
                        event_data.get('data', {}).get('id') == self.current_friend_id):
                        # Nuovo messaggio nella conversazione corrente
                        if event_data['eventType'] == 'Create':
                            self.root.after(500, self.load_conversation_history)
                
                # Gestisci cambi di stato amici
                elif event_data['uri'] == '/lol-chat/v1/friends':
                    self.root.after(1000, self.refresh_friends)
                    
            except Exception as e:
                print(f"WebSocket message error: {e}")
        
        def on_error(ws, error):
            print(f"WebSocket error: {error}")
            self.update_status("⚠️ Errore connessione real-time")
        
        def on_close(ws, close_status_code, close_msg):
            self.ws_connected = False
            print("WebSocket disconnesso")
            self.update_status("📡 Connessione real-time interrotta")
        
        def on_open(ws):
            self.ws_connected = True
            print("WebSocket connesso")
            self.update_status("📡 Connessione real-time attiva")
        
        def run_websocket():
            try:
                ws_url = f"wss://127.0.0.1:{self.port}/"
                self.ws = websocket.WebSocketApp(
                    ws_url,
                    header={"Authorization": f"Basic {self.auth_token}"},
                    on_open=on_open,
                    on_message=on_message,
                    on_error=on_error,
                    on_close=on_close
                )
                self.ws.run_forever(sslopt={"cert_reqs": False})
            except Exception as e:
                print(f"WebSocket thread error: {e}")
        
        # Avvia in thread separato
        ws_thread = threading.Thread(target=run_websocket, daemon=True)
        ws_thread.start()
    
    def update_status(self, message):
        """Aggiorna la status bar con timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"{message}")
        print(f"[{timestamp}] {message}")
    
    def show_settings(self):
        """Mostra la finestra delle impostazioni."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Impostazioni")
        settings_window.geometry("400x300")
        settings_window.configure(bg=ModernTheme.BG_PRIMARY)
        settings_window.resizable(False, False)
        settings_window.grab_set()
        settings_window.transient(self.root)
        
        # Centra la finestra
        settings_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 150
        settings_window.geometry(f"400x300+{x}+{y}")
        
        # Contenuto impostazioni
        main_frame = ttk.Frame(settings_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="⚙️ Impostazioni", style="Header.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Sezione connessione
        conn_frame = ttk.LabelFrame(main_frame, text="🔗 Connessione")
        conn_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(conn_frame, text="Percorso installazione:", padding=5).pack(anchor=tk.W)
        path_label = ttk.Label(
            conn_frame, 
            text=getattr(self, 'install_path', 'Non impostato'),
            style="Muted.TLabel",
            padding=(5, 0, 5, 10)
        )
        path_label.pack(anchor=tk.W, fill=tk.X)
        
        ttk.Button(conn_frame, text="📁 Cambia percorso", 
                  command=self.change_install_path).pack(anchor=tk.W, padx=5, pady=5)
        
        # Pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="❌ Chiudi", 
                  command=settings_window.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="🔄 Test connessione", 
                  command=self.test_connection).pack(side=tk.RIGHT, padx=(0, 10))
    
    def change_install_path(self):
        """Cambia il percorso di installazione."""
        new_path = filedialog.askdirectory(
            title="Seleziona cartella di installazione League of Legends"
        )
        if new_path:
            self.install_path = new_path
            messagebox.showinfo("Successo", "Percorso aggiornato! Riconnetti al client.")
    
    def test_connection(self):
        """Testa la connessione al client."""
        if self.connect_to_client():
            messagebox.showinfo("Test Connessione", "✅ Connessione riuscita!")
        else:
            messagebox.showerror("Test Connessione", "❌ Connessione fallita!")
    
    def show_connection_stats(self):
        """Mostra statistiche della connessione."""
        stats_window = tk.Toplevel(self.root)
        stats_window.title("📊 Statistiche Connessione")
        stats_window.geometry("450x350")
        stats_window.configure(bg=ModernTheme.BG_PRIMARY)
        stats_window.resizable(False, False)
        stats_window.grab_set()
        stats_window.transient(self.root)
        
        # Centra finestra
        stats_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 225
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 175
        stats_window.geometry(f"450x350+{x}+{y}")
        
        main_frame = ttk.Frame(stats_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="📊 Statistiche Connessione", style="Header.TLabel")
        title_label.pack(pady=(0, 20))
        
        # Info connessione
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ Informazioni")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        stats_text = f"""
Status: {'🟢 Connesso' if self.connection_status else '🔴 Disconnesso'}
WebSocket: {'🟢 Attivo' if self.ws_connected else '🔴 Inattivo'}
Porta: {self.port or 'N/A'}
Protocollo: {self.protocol or 'N/A'}
Utente: {self.current_summoner['displayName'] if self.current_summoner else 'N/A'}
Amici online: {len(self.friends_list)}
        """
        
        stats_label = ttk.Label(info_frame, text=stats_text.strip(), justify=tk.LEFT, padding=10)
        stats_label.pack(anchor=tk.W)
        
        # Pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="❌ Chiudi", 
                  command=stats_window.destroy).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="🔄 Aggiorna", 
                  command=lambda: self.update_stats_window(stats_label)).pack(side=tk.RIGHT, padx=(0, 10))
    
    def update_stats_window(self, stats_label):
        """Aggiorna le statistiche nella finestra."""
        stats_text = f"""
Status: {'🟢 Connesso' if self.connection_status else '🔴 Disconnesso'}
WebSocket: {'🟢 Attivo' if self.ws_connected else '🔴 Inattivo'}
Porta: {self.port or 'N/A'}
Protocollo: {self.protocol or 'N/A'}
Utente: {self.current_summoner['displayName'] if self.current_summoner else 'N/A'}
Amici online: {len(self.friends_list)}
        """
        stats_label.config(text=stats_text.strip())
    
    def show_help(self):
        """Mostra la finestra di aiuto migliorata."""
        help_window = tk.Toplevel(self.root)
        help_window.title("❓ Guida")
        help_window.geometry("600x500")
        help_window.configure(bg=ModernTheme.BG_PRIMARY)
        help_window.resizable(True, True)
        help_window.grab_set()
        help_window.transient(self.root)
        
        # Centra finestra
        help_window.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 300
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 250
        help_window.geometry(f"600x500+{x}+{y}")
        
        main_frame = ttk.Frame(help_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="❓ Guida League of Legends Messenger", 
                               style="Header.TLabel")
        title_label.pack(pady=(0, 20))
        
        help_text = """🎮 LEAGUE OF LEGENDS MESSENGER - GUIDA COMPLETA

📋 REQUISITI:
• League of Legends deve essere aperto e funzionante
• Il client deve essere completamente caricato (non solo il launcher)
• Connessione internet attiva

🚀 PRIMO AVVIO:
1. Avvia League of Legends normalmente
2. Apri questa applicazione
3. L'app si connetterà automaticamente al client
4. Se non si connette, usa "File → Connetti al client"

💬 UTILIZZO CHAT:
• Seleziona un amico dalla lista per iniziare a chattare
• Scrivi il messaggio nella casella in basso
• Premi Invio per inviare (o clicca il pulsante "Invia")
• I messaggi sono sincronizzati in tempo reale

🔍 FUNZIONI AGGIUNTIVE:
• Barra di ricerca per filtrare gli amici
• Indicatori di stato colorati (Online/Assente/Occupato)
• Aggiornamento automatico della lista amici
• Cronologia conversazioni

⚙️ RISOLUZIONE PROBLEMI:

❌ "Client non trovato":
→ Assicurati che League of Legends sia completamente avviato
→ Prova a riavviare entrambe le applicazioni
→ Verifica il percorso di installazione nelle impostazioni

❌ "Errore di connessione":
→ Riavvia il client League of Legends
→ Controlla che non ci siano firewall che bloccano la connessione
→ Prova a cambiare il percorso di installazione

❌ "Lista amici vuota":
→ Controlla di avere amici online nel client
→ Prova ad aggiornare manualmente la lista
→ Riconnetti al client

📡 CONNESSIONE REAL-TIME:
L'app utilizza WebSocket per ricevere messaggi in tempo reale.
Se non funziona, i messaggi saranno comunque inviati correttamente.

🔐 SICUREZZA:
Questa applicazione si connette solo localmente al tuo client.
Non vengono inviate informazioni a server esterni.

💡 SUGGERIMENTI:
• Mantieni sempre aperto il client League of Legends
• Usa Ctrl+Invio per andare a capo nei messaggi
• La ricerca amici funziona in tempo reale mentre scrivi
• I colori degli stati indicano: Verde=Online, Giallo=Assente, Rosso=Occupato"""
        
        # Area di testo scrollabile
        text_frame = ttk.Frame(main_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        help_text_widget = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            bg=ModernTheme.BG_SECONDARY,
            fg=ModernTheme.TEXT_PRIMARY,
            font=(ModernTheme.FONT_FAMILY, ModernTheme.FONT_SIZE_NORMAL),
            relief='flat',
            padx=15,
            pady=15,
            state=tk.NORMAL
        )
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
        
        # Pulsante chiudi
        ttk.Button(main_frame, text="❌ Chiudi", 
                  command=help_window.destroy).pack(pady=(20, 0))
    
    def show_about(self):
        """Mostra informazioni sull'applicazione."""
        about_text = """🎮 League of Legends Messenger

📋 Versione: 3.0 (Migliorata)

✨ Caratteristiche:
• Interfaccia moderna con tema League of Legends
• Chat in tempo reale con gli amici
• Indicatori di stato avanzati
• Ricerca amici intelligente
• Sincronizzazione automatica
• Gestione errori migliorata
• Design responsive e accessibile

🛠️ Tecnologie utilizzate:
• Python 3.8+
• Tkinter per l'interfaccia grafica
• League Client API (LCU)
• WebSocket per connessioni real-time
• PIL per gestione immagini

⚡ Miglioramenti versione 3.0:
• Grafica completamente rinnovata
• Migliore gestione degli errori
• Prestazioni ottimizzate
• Nuovi widget personalizzati
• Esperienza utente migliorata

📧 Supporto:
Per problemi o suggerimenti, controlla la guida
integrata nell'applicazione.

© 2025 League of Legends Messenger
Sviluppato con ❤️ per la community di League of Legends"""
        
        messagebox.showinfo("ℹ️ Informazioni", about_text)
    
    def on_closing(self):
        """Gestisce la chiusura dell'applicazione."""
        if self.ws and self.ws_connected:
            try:
                self.ws.close()
            except:
                pass
        
        self.root.quit()
        self.root.destroy()

def main():
    """Funzione principale dell'applicazione."""
    # Verifica versione Python
    if sys.version_info < (3, 7):
        print("❌ Errore: Python 3.7+ richiesto")
        messagebox.showerror("Versione Python", 
                           "Questa applicazione richiede Python 3.7 o superiore.")
        return
    
    # Verifica dipendenze
    try:
        import requests
        import websocket
        from PIL import Image, ImageTk
    except ImportError as e:
        missing_lib = str(e).split("'")[1]
        print(f"❌ Libreria mancante: {missing_lib}")
        messagebox.showerror("Dipendenza Mancante", 
                           f"Libreria richiesta non trovata: {missing_lib}\n\n"
                           f"Installa con: pip install {missing_lib}")
        return
    
    try:
        # Crea e avvia l'applicazione
        root = tk.Tk()
        app = LeagueMessenger(root)
        
        # Gestisce la chiusura
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Avvia il loop principale
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Errore critico: {e}")
        messagebox.showerror("Errore Critico", 
                           f"Si è verificato un errore critico:\n{str(e)}\n\n"
                           "L'applicazione verrà chiusa.")

if __name__ == "__main__":
    main()