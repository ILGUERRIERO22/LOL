import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
import math
import subprocess
from pynput import keyboard
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw, ImageTk, ImageFont
from Riot_API import create_normal_lobby, create_custom_lobby, set_position_preferences, start_queue, stop_queue, is_champion_select, start_monitoring, stop_monitoring, accept_ready_check

# Costanti
HOTKEYS_FILE = "hotkeys_config.json"
RIOT_SERVER_IP = "1.118.32.0"
ASSETS_FOLDER = "assets/"

# Variabili globali per i frame
frame_lobby = None
frame_roles = None
frame_matchmaking = None

# Schema colori migliorato per League of Legends
DARK_BG = "#0A1428"
DARKER_BG = "#091428"
CARD_BG = "#1E2328"
ACCENT_COLOR = "#C8AA6E"
ACCENT_COLOR_HOVER = "#E1C387"
BUTTON_BG = "#463714"
BUTTON_ACTIVE = "#5A4519"
TEXT_COLOR = "#F0E6D2"
SECONDARY_TEXT = "#A09B8C"
LOG_SUCCESS = "#5CD99D"
LOG_ERROR = "#F04967"
LOG_WARNING = "#FDB86B"
LOG_INFO = "#1CB7E3"
BORDER_COLOR = "#1E2328"
GOLD_ACCENT = "#C89B3C"

# Ruoli con icone LoL
ROLE_ICONS = {
    "TOP": "assets/icons/Position_Gold-Top.png",
    "JUNGLE": "assets/icons/Position_Gold-Jungle.png",
    "MIDDLE": "assets/icons/Position_Gold-Mid.png",
    "BOTTOM": "assets/icons/Position_Gold-Bot.png",
    "UTILITY": "assets/icons/Position_Gold-Support.png"
}

# Assicurati che la cartella assets esista
def create_assets_folders():
    if not os.path.exists(ASSETS_FOLDER):
        os.makedirs(ASSETS_FOLDER)
    if not os.path.exists(f"{ASSETS_FOLDER}icons/"):
        os.makedirs(f"{ASSETS_FOLDER}icons/")

def create_role_icons():
    """Crea icone ruoli migliorate con design più raffinato"""
    for role, path in ROLE_ICONS.items():
        if not os.path.exists(path):
            img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Background circolare
            draw.ellipse([(8, 8), (56, 56)], outline=ACCENT_COLOR, fill=CARD_BG, width=2)
            
            # Simboli specifici per ogni ruolo
            if role == "TOP":
                # Scudo
                draw.polygon([(32, 20), (44, 28), (40, 44), (24, 44), (20, 28)], 
                           outline=ACCENT_COLOR, fill=BUTTON_BG, width=2)
            elif role == "JUNGLE":
                # Artigli incrociati
                draw.line([(24, 24), (40, 40)], fill=ACCENT_COLOR, width=3)
                draw.line([(40, 24), (24, 40)], fill=ACCENT_COLOR, width=3)
                for i in range(3):
                    draw.line([(20+i*2, 28+i*2), (18+i*2, 30+i*2)], fill=ACCENT_COLOR, width=2)
            elif role == "MIDDLE":
                # Stella a 4 punte
                draw.line([(32, 20), (32, 44)], fill=ACCENT_COLOR, width=3)
                draw.line([(20, 32), (44, 32)], fill=ACCENT_COLOR, width=3)
                draw.ellipse([(28, 28), (36, 36)], fill=ACCENT_COLOR)
            elif role == "BOTTOM":
                # Frecce multiple
                for i in range(3):
                    y = 24 + i * 6
                    draw.polygon([(20, y), (28, y-3), (28, y+3)], fill=ACCENT_COLOR)
                    draw.polygon([(36, y), (44, y-3), (44, y+3)], fill=ACCENT_COLOR)
            elif role == "UTILITY":
                # Croce di supporto
                draw.line([(32, 22), (32, 42)], fill=ACCENT_COLOR, width=4)
                draw.line([(22, 32), (42, 32)], fill=ACCENT_COLOR, width=4)
                draw.ellipse([(28, 28), (36, 36)], outline=ACCENT_COLOR, fill=CARD_BG, width=2)
            
            img.save(path)

def log_message(message, level="INFO"):
    """Registra messaggi con codifica colore migliorata"""
    if 'log_text' not in globals():
        return
        
    log_text.configure(state="normal")
    timestamp = time.strftime('%H:%M:%S')
    
    # Determina il colore e l'icona
    level_config = {
        "ERROR": {"tag": "error", "icon": "⚠"},
        "SUCCESS": {"tag": "success", "icon": "✓"},
        "STOP": {"tag": "stop", "icon": "⏹"},
        "WARNING": {"tag": "warning", "icon": "!"},
        "INFO": {"tag": "info", "icon": "ℹ"}
    }
    
    # Auto-detection del livello basata sul contenuto
    if "Errore" in message or level == "ERROR":
        config = level_config["ERROR"]
    elif any(word in message.lower() for word in ["avviato", "successo", "creata"]) or level == "SUCCESS":
        config = level_config["SUCCESS"]
    elif any(word in message.lower() for word in ["interrotto", "fermata"]) or level == "STOP":
        config = level_config["STOP"]
    elif level == "WARNING":
        config = level_config["WARNING"]
    else:
        config = level_config["INFO"]
    
    log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
    log_text.insert(tk.END, f"{config['icon']} {message}\n", config["tag"])
    log_text.see(tk.END)
    log_text.configure(state="disabled")

def handle_create_normal_lobby():
    try:
        queue_mapping = {
            "Draft Normale": 400, "Classificata Solo/Duo": 420, "Flex": 440, "ARAM": 450, 
            "Swiftplay": 480, "Quickplay": 490, "URF": 900, "Arena": 1700, 
            "TFT Classificata": 1100, "TFT Normale": 1090, "TFT Double Up": 1160, 
            "TFT Hyper Roll": 1130, "TFT 4.5": 6100
        }
        selected_mode = lobby_combobox.get()
        if selected_mode not in queue_mapping:
            log_message("Seleziona una modalità di gioco valida", "ERROR")
            return
            
        queue_id = queue_mapping[selected_mode]
        create_normal_lobby(queue_id)
        log_message(f"Lobby '{selected_mode}' creata con successo", "SUCCESS")
    except Exception as e:
        log_message(f"Errore nella creazione della lobby: {str(e)}", "ERROR")

def handle_create_custom_lobby():
    try:
        custom_game_modes = {
            "Landa degli Evocatori": "CLASSIC",
            "Strumento di Allenamento": "PRACTICETOOL",
        }
        
        selected_mode_name = custom_mode_combobox.get()
        if selected_mode_name not in custom_game_modes:
            log_message("Seleziona una modalità personalizzata valida", "ERROR")
            return
            
        selected_mode = custom_game_modes[selected_mode_name]
        lobby_name = lobby_name_entry.get().strip()
        lobby_password = lobby_password_entry.get().strip()
        
        if not lobby_name:
            log_message("Inserisci un nome per la lobby", "ERROR")
            return
            
        create_custom_lobby(selected_mode, lobby_name, lobby_password)
        log_message(f"Lobby personalizzata '{lobby_name}' creata", "SUCCESS")
    except Exception as e:
        log_message(f"Errore nella creazione della lobby personalizzata: {str(e)}", "ERROR")

def handle_update_roles():
    try:
        primary_role = primary_role_var.get()
        secondary_role = secondary_role_var.get()

        if not primary_role or not secondary_role:
            log_message("Seleziona entrambi i ruoli", "ERROR")
            return

        if primary_role == secondary_role:
            log_message("I ruoli primario e secondario devono essere diversi", "ERROR")
            return

        set_position_preferences(primary_role, secondary_role)
        log_message(f"Ruoli aggiornati: {primary_role} / {secondary_role}", "SUCCESS")
    except Exception as e:
        log_message(f"Errore nell'aggiornamento dei ruoli: {str(e)}", "ERROR")

def handle_start_queue():
    try:
        start_queue()
        log_message("Coda avviata con successo", "SUCCESS")
    except Exception as e:
        log_message(f"Errore nell'avvio della coda: {str(e)}", "ERROR")

def handle_stop_queue():
    try:
        stop_queue()
        log_message("Coda fermata con successo", "STOP")
    except Exception as e:
        log_message(f"Errore nell'arresto della coda: {str(e)}", "ERROR")

def handle_start_monitoring():
    try:
        global running
        running = True
        message = start_monitoring()
        log_message("Monitoraggio auto-accept avviato", "SUCCESS")
        threading.Thread(target=monitor_ready_check, daemon=True).start()
    except Exception as e:
        log_message(f"Errore nell'avvio del monitoraggio: {str(e)}", "ERROR")

def handle_stop_monitoring():
    try:
        global running
        running = False
        stop_monitoring()
        log_message("Monitoraggio interrotto", "STOP")
    except Exception as e:
        log_message(f"Errore nell'arresto del monitoraggio: {str(e)}", "ERROR")

def monitor_ready_check():
    global running
    while running:
        try:
            if is_champion_select():
                log_message("Champion select rilevato - monitoraggio interrotto", "INFO")
                running = False
                break
            time.sleep(1)
        except Exception as e:
            log_message(f"Errore nel monitoraggio: {str(e)}", "ERROR")
            break

def load_hotkeys():
    global hotkeys_config
    if os.path.exists(HOTKEYS_FILE):
        try:
            with open(HOTKEYS_FILE, "r", encoding='utf-8') as file:
                hotkeys_config = json.load(file)
                log_message("Configurazione hotkeys caricata", "SUCCESS")
        except Exception as e:
            log_message(f"Errore nel caricamento hotkeys: {str(e)}", "ERROR")

def save_hotkeys():
    try:
        with open(HOTKEYS_FILE, "w", encoding='utf-8') as file:
            json.dump(hotkeys_config, file, indent=4, ensure_ascii=False)
        log_message("Configurazione hotkeys salvata", "SUCCESS")
    except Exception as e:
        log_message(f"Errore nel salvataggio hotkeys: {str(e)}", "ERROR")

def create_gradient_background(width, height, color1, color2):
    """Crea un background con gradiente migliorato"""
    img = Image.new('RGB', (width, height), color1)
    draw = ImageDraw.Draw(img)
    
    # Gradiente verticale
    for y in range(height):
        ratio = y / height
        r = int(int(color1[1:3], 16) * (1 - ratio) + int(color2[1:3], 16) * ratio)
        g = int(int(color1[3:5], 16) * (1 - ratio) + int(color2[3:5], 16) * ratio)
        b = int(int(color1[5:7], 16) * (1 - ratio) + int(color2[5:7], 16) * ratio)
        
        color = f"#{r:02x}{g:02x}{b:02x}"
        draw.line([(0, y), (width, y)], fill=color)
    
    # Aggiungi pattern sottile
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            if (x + y) % 16 == 0:
                draw.point((x, y), fill="#0C1A32")
    
    return img

def create_main_window():
    global root, style, log_text, lobby_combobox, custom_mode_combobox
    global lobby_name_entry, lobby_password_entry, primary_role_var, secondary_role_var
    
    root = tk.Tk()
    root.title("League Tools - Advanced")
    root.geometry("1200x700")
    root.configure(bg=DARK_BG)
    root.resizable(True, True)
    root.minsize(1000, 600)
    
    # Icona della finestra
    try:
        if os.path.exists("assets/league_tools_icon.png"):
            icon = ImageTk.PhotoImage(file="assets/league_tools_icon.png")
            root.iconphoto(True, icon)
    except Exception:
        pass
    
    # Background con gradiente
    bg_image = create_gradient_background(1200, 700, DARK_BG, DARKER_BG)
    bg_photo = ImageTk.PhotoImage(bg_image)
    
    bg_label = tk.Label(root, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Configura stili ttk migliorati
    setup_styles()
    
    # Layout principale
    main_frame = ttk.Frame(root, style='Main.TFrame')
    main_frame.place(relx=0.5, rely=0.5, relwidth=0.95, relheight=0.92, anchor="center")
    
    main_frame.grid_rowconfigure(1, weight=1)
    main_frame.grid_columnconfigure(0, weight=3)
    main_frame.grid_columnconfigure(1, weight=1)
    
    # Header
    create_enhanced_header(main_frame)
    
    # Contenuto principale
    left_frame = create_enhanced_left_frame(main_frame)
    left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=10)
    
    right_frame = create_enhanced_right_frame(main_frame)
    right_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
    
    # Status bar
    create_enhanced_status_bar(main_frame)
    
    return root

def setup_styles():
    global style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Frame styles
    style.configure('Main.TFrame', background='')
    style.configure('Card.TFrame', background=CARD_BG, relief='flat', borderwidth=1)
    style.configure('Header.TFrame', background=DARKER_BG)
    
    # Label styles
    style.configure('Title.TLabel', background='', foreground=ACCENT_COLOR, 
                   font=('Segoe UI', 20, 'bold'))
    style.configure('Subtitle.TLabel', background='', foreground=SECONDARY_TEXT, 
                   font=('Segoe UI', 10))
    style.configure('CardTitle.TLabel', background=CARD_BG, foreground=TEXT_COLOR,
                   font=('Segoe UI', 12, 'bold'))
    style.configure('Normal.TLabel', background='', foreground=TEXT_COLOR,
                   font=('Segoe UI', 10))
    
    # Button styles
    style.configure('Primary.TButton', 
                   background=ACCENT_COLOR, foreground=DARKER_BG,
                   font=('Segoe UI', 10, 'bold'), padding=(15, 8))
    style.map('Primary.TButton', 
             background=[('active', ACCENT_COLOR_HOVER), ('pressed', GOLD_ACCENT)])
    
    style.configure('Secondary.TButton',
                   background=BUTTON_BG, foreground=TEXT_COLOR,
                   font=('Segoe UI', 10), padding=(12, 6))
    style.map('Secondary.TButton',
             background=[('active', BUTTON_ACTIVE), ('pressed', DARKER_BG)])
    
    style.configure('Tab.TButton',
                   background=DARKER_BG, foreground=SECONDARY_TEXT,
                   font=('Segoe UI', 11), padding=(20, 10))
    style.map('Tab.TButton',
             background=[('active', CARD_BG)], foreground=[('active', TEXT_COLOR)])
    
    style.configure('ActiveTab.TButton',
                   background=CARD_BG, foreground=ACCENT_COLOR,
                   font=('Segoe UI', 11, 'bold'), padding=(20, 10))
    
    # Entry and Combobox styles
    style.configure('Modern.TEntry',
                   fieldbackground=CARD_BG, foreground=TEXT_COLOR,
                   bordercolor=BORDER_COLOR, insertcolor=ACCENT_COLOR)
    
    style.configure('Modern.TCombobox',
                   fieldbackground=CARD_BG, foreground=TEXT_COLOR,
                   selectbackground=ACCENT_COLOR, selectforeground=DARKER_BG,
                   arrowcolor=ACCENT_COLOR, bordercolor=BORDER_COLOR)

def create_enhanced_header(parent):
    header_frame = ttk.Frame(parent, style='Header.TFrame', padding=20)
    header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
    
    # Logo container
    logo_frame = ttk.Frame(header_frame, style='Header.TFrame')
    logo_frame.pack(side="left")
    
    # Logo migliorato
    logo_canvas = tk.Canvas(logo_frame, width=80, height=80, bg=DARKER_BG, highlightthickness=0)
    logo_canvas.pack(side="left", padx=(0, 20))
    
    # Hexagon logo con gradiente
    create_hexagon_logo(logo_canvas, 40, 40, 35)
    
    # Text container
    text_frame = ttk.Frame(header_frame, style='Header.TFrame')
    text_frame.pack(side="left", fill="both", expand=True)
    
    title_label = ttk.Label(text_frame, text="LEAGUE TOOLS", style='Title.TLabel')
    title_label.pack(anchor="w")
    
    subtitle_label = ttk.Label(text_frame, 
                              text="Strumento avanzato per la gestione delle partite di League of Legends",
                              style='Subtitle.TLabel')
    subtitle_label.pack(anchor="w", pady=(5, 0))

def create_hexagon_logo(canvas, x, y, size):
    """Crea un logo esagonale migliorato"""
    points = []
    for i in range(6):
        angle = i * 60 * math.pi / 180
        px = x + size * math.cos(angle)
        py = y + size * math.sin(angle)
        points.extend([px, py])
    
    # Hexagon esterno
    canvas.create_polygon(points, outline=ACCENT_COLOR, fill=CARD_BG, width=3)
    
    # Hexagon interno
    inner_points = []
    for i in range(6):
        angle = i * 60 * math.pi / 180
        px = x + (size - 15) * math.cos(angle)
        py = y + (size - 15) * math.sin(angle)
        inner_points.extend([px, py])
    
    canvas.create_polygon(inner_points, outline=GOLD_ACCENT, fill='', width=2)
    
    # Testo centrale
    canvas.create_text(x, y, text="LT", fill=ACCENT_COLOR, font=("Segoe UI", 24, "bold"))

def create_enhanced_left_frame(parent):
    # Frame principale con scrolling
    container = ttk.Frame(parent, style='Card.TFrame', padding=5)
    
    # Canvas per scrolling
    canvas = tk.Canvas(container, bg=CARD_BG, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    
    scrollable_frame = ttk.Frame(canvas, style='Card.TFrame')
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    def configure_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    scrollable_frame.bind("<Configure>", configure_scroll_region)
    
    # Mouse wheel binding specifico per il frame sinistro
    def _on_left_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _bind_left_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_left_mousewheel)
    
    def _unbind_left_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
    
    canvas.bind('<Enter>', _bind_left_mousewheel)
    canvas.bind('<Leave>', _unbind_left_mousewheel)
    
    # Crea contenuti
    create_navigation_section(scrollable_frame)
    create_content_sections(scrollable_frame)
    
    return container

def create_navigation_section(parent):
    nav_frame = ttk.Frame(parent, style='Card.TFrame', padding=20)
    nav_frame.pack(fill="x", pady=(0, 20))
    
    # Titolo navigazione
    nav_title = ttk.Label(nav_frame, text="SEZIONI", style='CardTitle.TLabel')
    nav_title.pack(anchor="w", pady=(0, 15))
    
    # Container per i tab
    tabs_container = ttk.Frame(nav_frame, style='Card.TFrame')
    tabs_container.pack(fill="x")
    
    # Crea i pulsanti tab
    create_tab_buttons(tabs_container)

def create_tab_buttons(parent):
    global frame_lobby, frame_roles, frame_matchmaking
    
    def show_section(section_name):
        # Nascondi tutti i frame
        for frame in [frame_lobby, frame_roles, frame_matchmaking]:
            if frame:
                frame.pack_forget()
        
        # Aggiorna stili dei pulsanti
        for btn_name, btn in tab_buttons.items():
            if btn_name == section_name:
                btn.configure(style='ActiveTab.TButton')
            else:
                btn.configure(style='Tab.TButton')
        
        # Mostra il frame selezionato
        if section_name == "lobby" and frame_lobby:
            frame_lobby.pack(fill="x", pady=10)
        elif section_name == "roles" and frame_roles:
            frame_roles.pack(fill="x", pady=10)
        elif section_name == "queue" and frame_matchmaking:
            frame_matchmaking.pack(fill="x", pady=10)
    
    tab_buttons = {}
    
    # Pulsante Lobby
    lobby_btn = ttk.Button(parent, text="LOBBY", style='ActiveTab.TButton',
                          command=lambda: show_section("lobby"))
    lobby_btn.pack(side="left", padx=(0, 10))
    tab_buttons["lobby"] = lobby_btn
    
    # Pulsante Ruoli
    roles_btn = ttk.Button(parent, text="RUOLI", style='Tab.TButton',
                          command=lambda: show_section("roles"))
    roles_btn.pack(side="left", padx=10)
    tab_buttons["roles"] = roles_btn
    
    # Pulsante Code
    queue_btn = ttk.Button(parent, text="CODE", style='Tab.TButton',
                          command=lambda: show_section("queue"))
    queue_btn.pack(side="left", padx=10)
    tab_buttons["queue"] = queue_btn
    
    # Memorizza i pulsanti per riferimento futuro
    parent.tab_buttons = tab_buttons
    parent.show_section = show_section

def create_content_sections(parent):
    global frame_lobby, frame_roles, frame_matchmaking
    
    # Crea le sezioni
    frame_lobby = create_lobby_section(parent)
    frame_roles = create_roles_section(parent)
    frame_matchmaking = create_matchmaking_section(parent)
    
    # Inizialmente mostra solo la lobby
    frame_lobby.pack(fill="x", pady=10)

def create_lobby_section(parent):
    global lobby_combobox, custom_mode_combobox, lobby_name_entry, lobby_password_entry
    
    section = ttk.Frame(parent, style='Card.TFrame', padding=20)
    
    # Titolo sezione
    title_label = ttk.Label(section, text="GESTIONE LOBBY", style='CardTitle.TLabel')
    title_label.pack(anchor="w", pady=(0, 20))
    
    # Sezione lobby normale
    normal_card = create_modern_card(section, "Lobby Normale", "🎮")
    
    # Selezione modalità
    mode_frame = ttk.Frame(normal_card, style='Card.TFrame')
    mode_frame.pack(fill="x", pady=10)
    
    ttk.Label(mode_frame, text="Modalità:", style='Normal.TLabel').pack(anchor="w")
    
    lobby_combobox = ttk.Combobox(mode_frame, style='Modern.TCombobox',
                                 values=["Draft Normale", "Swiftplay", "Classificata Solo/Duo", 
                                        "Flex", "ARAM", "URF", "Arena", "TFT Normale", 
                                        "TFT Classificata", "TFT Double Up", "TFT Hyper Roll"],
                                 state="readonly", width=30)
    lobby_combobox.pack(fill="x", pady=(5, 0))
    lobby_combobox.set("Draft Normale")
    
    # Pulsante crea lobby normale
    ttk.Button(normal_card, text="CREA LOBBY", style='Primary.TButton',
              command=handle_create_normal_lobby).pack(pady=(15, 0))
    
    # Sezione lobby personalizzata
    custom_card = create_modern_card(section, "Lobby Personalizzata", "🛠")
    
    # Grid per campi personalizzati
    grid_frame = ttk.Frame(custom_card, style='Card.TFrame')
    grid_frame.pack(fill="x", pady=10)
    
    # Modalità personalizzata
    ttk.Label(grid_frame, text="Modalità:", style='Normal.TLabel').grid(row=0, column=0, sticky="w", pady=5)
    custom_mode_combobox = ttk.Combobox(grid_frame, style='Modern.TCombobox',
                                       values=["Landa degli Evocatori", "Strumento di Allenamento"],
                                       state="readonly", width=25)
    custom_mode_combobox.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
    custom_mode_combobox.set("Strumento di Allenamento")
    
    # Nome lobby
    ttk.Label(grid_frame, text="Nome Lobby:", style='Normal.TLabel').grid(row=1, column=0, sticky="w", pady=5)
    lobby_name_entry = ttk.Entry(grid_frame, style='Modern.TEntry', width=25)
    lobby_name_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=5)
    
    # Password
    ttk.Label(grid_frame, text="Password:", style='Normal.TLabel').grid(row=2, column=0, sticky="w", pady=5)
    lobby_password_entry = ttk.Entry(grid_frame, style='Modern.TEntry', show="•", width=25)
    lobby_password_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=5)
    
    grid_frame.columnconfigure(1, weight=1)
    
    # Pulsante crea lobby personalizzata
    ttk.Button(custom_card, text="CREA LOBBY PERSONALIZZATA", style='Primary.TButton',
              command=handle_create_custom_lobby).pack(pady=(15, 0))
    
    return section

def create_roles_section(parent):
    global primary_role_var, secondary_role_var
    
    section = ttk.Frame(parent, style='Card.TFrame', padding=20)
    
    # Titolo
    ttk.Label(section, text="GESTIONE RUOLI", style='CardTitle.TLabel').pack(anchor="w", pady=(0, 20))
    
    # Card ruoli
    roles_card = create_modern_card(section, "Preferenze Ruolo", "⚔")
    
    # Visualizzazione ruoli con icone
    roles_display = create_roles_display(roles_card)
    
    # Selezione ruoli
    selection_frame = ttk.Frame(roles_card, style='Card.TFrame')
    selection_frame.pack(fill="x", pady=20)
    
    # Ruolo primario
    primary_frame = ttk.Frame(selection_frame, style='Card.TFrame')
    primary_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))
    
    ttk.Label(primary_frame, text="RUOLO PRIMARIO", style='CardTitle.TLabel').pack(anchor="w")
    primary_role_var = tk.StringVar(value="TOP")
    primary_combo = ttk.Combobox(primary_frame, textvariable=primary_role_var, style='Modern.TCombobox',
                                values=["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"], state="readonly")
    primary_combo.pack(fill="x", pady=(10, 0))
    
    # Ruolo secondario
    secondary_frame = ttk.Frame(selection_frame, style='Card.TFrame')
    secondary_frame.pack(side="left", fill="x", expand=True, padx=(10, 0))
    
    ttk.Label(secondary_frame, text="RUOLO SECONDARIO", style='CardTitle.TLabel').pack(anchor="w")
    secondary_role_var = tk.StringVar(value="JUNGLE")
    secondary_combo = ttk.Combobox(secondary_frame, textvariable=secondary_role_var, style='Modern.TCombobox',
                                  values=["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"], state="readonly")
    secondary_combo.pack(fill="x", pady=(10, 0))
    
    # Pulsante aggiorna
    ttk.Button(roles_card, text="AGGIORNA RUOLI", style='Primary.TButton',
              command=handle_update_roles).pack(pady=(20, 0))
    
    return section

def create_roles_display(parent):
    """Crea una visualizzazione migliorata dei ruoli"""
    display_frame = ttk.Frame(parent, style='Card.TFrame')
    display_frame.pack(fill="x", pady=10)
    
    # Background decorativo
    canvas = tk.Canvas(display_frame, height=100, bg=DARKER_BG, highlightthickness=0)
    canvas.pack(fill="x")
    
    # Disegna background per le icone ruoli
    canvas.create_rectangle(0, 0, 800, 100, fill=DARKER_BG, outline=BORDER_COLOR, width=1)
    
    # Aggiungi icone ruoli
    roles = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
    role_names = ["Top", "Jungle", "Mid", "Bot", "Support"]
    
    for i, (role, name) in enumerate(zip(roles, role_names)):
        x = 80 + i * 120
        
        # Cerchio per l'icona
        canvas.create_oval(x-25, 25, x+25, 75, outline=ACCENT_COLOR, fill=CARD_BG, width=2)
        
        # Testo ruolo
        canvas.create_text(x, 50, text=name, fill=ACCENT_COLOR, font=("Segoe UI", 12, "bold"))
        canvas.create_text(x, 90, text=role, fill=SECONDARY_TEXT, font=("Segoe UI", 8))
    
    return display_frame

def create_matchmaking_section(parent):
    section = ttk.Frame(parent, style='Card.TFrame', padding=20)
    
    # Titolo
    ttk.Label(section, text="GESTIONE CODE", style='CardTitle.TLabel').pack(anchor="w", pady=(0, 20))
    
    # Card gestione coda
    queue_card = create_modern_card(section, "Controllo Coda", "🎯")
    
    buttons_frame = ttk.Frame(queue_card, style='Card.TFrame')
    buttons_frame.pack(fill="x", pady=15)
    
    ttk.Button(buttons_frame, text="AVVIA CODA", style='Primary.TButton',
              command=handle_start_queue).pack(side="left", padx=(0, 10))
    ttk.Button(buttons_frame, text="FERMA CODA", style='Secondary.TButton',
              command=handle_stop_queue).pack(side="left")
    
    # Card auto-accept
    accept_card = create_modern_card(section, "Auto Accept", "✓")
    
    accept_buttons_frame = ttk.Frame(accept_card, style='Card.TFrame')
    accept_buttons_frame.pack(fill="x", pady=15)
    
    ttk.Button(accept_buttons_frame, text="AVVIA AUTO ACCEPT", style='Primary.TButton',
              command=handle_start_monitoring).pack(side="left", padx=(0, 10))
    ttk.Button(accept_buttons_frame, text="FERMA AUTO ACCEPT", style='Secondary.TButton',
              command=handle_stop_monitoring).pack(side="left")
    
    return section

def create_modern_card(parent, title, icon):
    """Crea una card moderna con stile migliorato"""
    card_container = ttk.Frame(parent, style='Card.TFrame', padding=2)
    card_container.pack(fill="x", pady=10)
    
    # Card principale
    card = tk.Frame(card_container, bg=CARD_BG, bd=0, relief="flat")
    card.pack(fill="both", expand=True, padx=2, pady=2)
    
    # Header della card
    header = tk.Frame(card, bg=DARKER_BG, height=50)
    header.pack(fill="x")
    header.pack_propagate(False)
    
    # Icona e titolo
    header_content = tk.Frame(header, bg=DARKER_BG)
    header_content.pack(expand=True, fill="both")
    
    icon_label = tk.Label(header_content, text=icon, bg=DARKER_BG, fg=ACCENT_COLOR,
                         font=("Segoe UI Emoji", 16))
    icon_label.pack(side="left", padx=15, pady=10)
    
    title_label = tk.Label(header_content, text=title, bg=DARKER_BG, fg=TEXT_COLOR,
                          font=("Segoe UI", 14, "bold"))
    title_label.pack(side="left", pady=10)
    
    # Contenuto della card
    content = ttk.Frame(card, style='Card.TFrame', padding=20)
    content.pack(fill="both", expand=True)
    
    return content

def create_enhanced_right_frame(parent):
    container = ttk.Frame(parent, style='Card.TFrame', padding=5)
    
    # Canvas per scrolling del frame destro
    canvas = tk.Canvas(container, bg=CARD_BG, highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    
    # Scrollbar per il frame destro
    right_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    right_scrollbar.pack(side="right", fill="y")
    
    # Frame scrollabile
    scrollable_right_frame = ttk.Frame(canvas, style='Card.TFrame')
    canvas.create_window((0, 0), window=scrollable_right_frame, anchor="nw")
    canvas.configure(yscrollcommand=right_scrollbar.set)
    
    def configure_right_scroll_region(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    scrollable_right_frame.bind("<Configure>", configure_right_scroll_region)
    
    # Mouse wheel binding per il frame destro
    def _on_right_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    # Bind solo quando il mouse è sopra il canvas destro
    def _bind_to_mousewheel(event):
        canvas.bind_all("<MouseWheel>", _on_right_mousewheel)
    
    def _unbind_from_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
    
    canvas.bind('<Enter>', _bind_to_mousewheel)
    canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    # Log section
    log_section = create_log_section(scrollable_right_frame)
    log_section.pack(fill="x", pady=(0, 10))
    
    # Network monitoring section
    network_section = create_network_section(scrollable_right_frame)
    network_section.pack(fill="x")
    
    return container

def create_log_section(parent):
    global log_text
    
    log_card = ttk.Frame(parent, style='Card.TFrame', padding=10)
    
    # Header
    header_frame = ttk.Frame(log_card, style='Card.TFrame')
    header_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(header_frame, text="📋 LOG SISTEMA", style='CardTitle.TLabel').pack(side="left")
    
    # Log text area
    log_frame = ttk.Frame(log_card, style='Card.TFrame')
    log_frame.pack(fill="both", expand=True)
    
    log_text = tk.Text(log_frame, height=15, width=40, wrap="word",
                      bg=DARKER_BG, fg=TEXT_COLOR, font=("Consolas", 9),
                      relief="flat", bd=5, padx=10, pady=10,
                      insertbackground=ACCENT_COLOR)
    log_text.pack(side="left", fill="both", expand=True)
    
    # Scrollbar
    log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=log_text.yview)
    log_scrollbar.pack(side="right", fill="y")
    log_text.configure(yscrollcommand=log_scrollbar.set)
    
    # Configurazione tag per colori
    log_text.tag_configure("timestamp", foreground="#888888", font=("Consolas", 8))
    log_text.tag_configure("error", foreground=LOG_ERROR, font=("Consolas", 9, "bold"))
    log_text.tag_configure("success", foreground=LOG_SUCCESS, font=("Consolas", 9, "bold"))
    log_text.tag_configure("warning", foreground=LOG_WARNING, font=("Consolas", 9, "bold"))
    log_text.tag_configure("info", foreground=LOG_INFO)
    log_text.tag_configure("stop", foreground="#FF9800", font=("Consolas", 9, "bold"))
    
    return log_card

def create_network_section(parent):
    network_card = create_modern_card(parent, "Monitor Rete", "🌐")
    
    # Test ping singolo
    test_frame = ttk.Frame(network_card, style='Card.TFrame')
    test_frame.pack(fill="x", pady=(0, 15))
    
    ttk.Button(test_frame, text="TEST PING", style='Primary.TButton',
              command=test_ping_once).pack(fill="x")
    
    # Separatore visivo
    separator_frame = ttk.Frame(network_card, style='Card.TFrame')
    separator_frame.pack(fill="x", pady=5)
    separator_canvas = tk.Canvas(separator_frame, height=2, bg=CARD_BG, highlightthickness=0)
    separator_canvas.pack(fill="x")
    separator_canvas.create_line(0, 1, 400, 1, fill=BORDER_COLOR)
    
    # Monitoraggio continuo
    continuous_frame = ttk.Frame(network_card, style='Card.TFrame')
    continuous_frame.pack(fill="x", pady=(10, 15))
    
    ttk.Label(continuous_frame, text="Monitoraggio Continuo:", style='Normal.TLabel').pack(anchor="w", pady=(0, 8))
    
    # Ping controls
    ping_frame = ttk.Frame(continuous_frame, style='Card.TFrame')
    ping_frame.pack(fill="x")
    
    ttk.Button(ping_frame, text="AVVIA MONITOR", style='Primary.TButton',
              command=start_ping_monitoring).pack(side="left", padx=(0, 10))
    ttk.Button(ping_frame, text="FERMA MONITOR", style='Secondary.TButton',
              command=stop_ping_monitoring).pack(side="left")
    
    # Status indicator
    status_frame = ttk.Frame(network_card, style='Card.TFrame')
    status_frame.pack(fill="x", pady=(15, 0))
    
    ttk.Label(status_frame, text="Stato Connessione:", style='Normal.TLabel').pack(side="left")
    
    global ping_indicator_canvas
    ping_indicator_canvas = tk.Canvas(status_frame, width=20, height=20, 
                                     bg=CARD_BG, highlightthickness=0)
    ping_indicator_canvas.pack(side="left", padx=(10, 0))
    ping_indicator_canvas.create_oval(2, 2, 18, 18, fill="#888888", outline=BORDER_COLOR)
    
    # Legenda colori
    legend_frame = ttk.Frame(network_card, style='Card.TFrame')
    legend_frame.pack(fill="x", pady=(10, 0))
    
    legend_text = ttk.Label(legend_frame, 
                           text="🟢 <100ms  🟡 100-200ms  🔴 >200ms  ⚪ Disconnesso",
                           style='Normal.TLabel',
                           font=('Segoe UI', 8))
    legend_text.pack(anchor="center")
    
    return network_card.master

def create_enhanced_status_bar(parent):
    status_frame = ttk.Frame(parent, style='Header.TFrame', padding=(20, 10))
    status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")
    
    # Left side
    left_frame = ttk.Frame(status_frame, style='Header.TFrame')
    left_frame.pack(side="left")
    
    ttk.Button(left_frame, text="⚙ HOTKEYS", style='Secondary.TButton',
              command=configure_hotkeys).pack(side="left")
    
    # Right side  
    right_frame = ttk.Frame(status_frame, style='Header.TFrame')
    right_frame.pack(side="right")
    
    ttk.Label(right_frame, text="League Tools v2.0", 
             foreground=SECONDARY_TEXT, background=DARKER_BG,
             font=("Segoe UI", 9)).pack(side="right", padx=(20, 0))
    
    ttk.Button(right_frame, text="📤 TRAY", style='Secondary.TButton',
              command=minimize_to_tray).pack(side="right", padx=(0, 20))

def configure_hotkeys():
    """Finestra di configurazione hotkeys migliorata"""
    hotkey_window = tk.Toplevel(root)
    hotkey_window.title("Configurazione Hotkeys")
    hotkey_window.geometry("600x550")
    hotkey_window.configure(bg=DARK_BG)
    hotkey_window.resizable(False, False)
    hotkey_window.transient(root)
    hotkey_window.grab_set()
    
    # Background
    bg_image = create_gradient_background(600, 550, DARK_BG, DARKER_BG)
    bg_photo = ImageTk.PhotoImage(bg_image)
    
    bg_label = tk.Label(hotkey_window, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Main frame
    main_frame = ttk.Frame(hotkey_window, style='Card.TFrame', padding=30)
    main_frame.place(relx=0.5, rely=0.5, relwidth=0.9, relheight=0.9, anchor="center")
    
    # Header
    header_frame = ttk.Frame(main_frame, style='Card.TFrame')
    header_frame.pack(fill="x", pady=(0, 30))
    
    ttk.Label(header_frame, text="⌨ CONFIGURAZIONE HOTKEYS", style='CardTitle.TLabel').pack(anchor="w")
    ttk.Label(header_frame, text="Imposta le combinazioni di tasti (es: ctrl+alt+q)", 
             style='Normal.TLabel').pack(anchor="w", pady=(5, 0))
    
    # Hotkeys container
    hotkeys_frame = ttk.Frame(main_frame, style='Card.TFrame')
    hotkeys_frame.pack(fill="both", expand=True, pady=(0, 20))
    
    hotkey_entries = {}
    
    for i, (action, config) in enumerate(hotkeys_config.items()):
        # Card per ogni hotkey
        hotkey_card = tk.Frame(hotkeys_frame, bg=CARD_BG, bd=1, relief="solid")
        hotkey_card.pack(fill="x", pady=8, padx=5)
        
        # Contenuto card
        card_content = tk.Frame(hotkey_card, bg=CARD_BG, padx=20, pady=15)
        card_content.pack(fill="x")
        
        # Descrizione
        desc_label = tk.Label(card_content, text=config["description"], 
                             bg=CARD_BG, fg=TEXT_COLOR, font=("Segoe UI", 11, "bold"))
        desc_label.pack(anchor="w")
        
        # Entry per hotkey
        entry_frame = tk.Frame(card_content, bg=CARD_BG)
        entry_frame.pack(fill="x", pady=(10, 0))
        
        entry = ttk.Entry(entry_frame, style='Modern.TEntry', font=("Segoe UI", 10))
        entry.pack(fill="x")
        entry.insert(0, "+".join(config["keys"]))
        
        hotkey_entries[action] = entry
    
    # Buttons frame
    buttons_frame = ttk.Frame(main_frame, style='Card.TFrame')
    buttons_frame.pack(fill="x")
    
    def save_and_close():
        for action, entry in hotkey_entries.items():
            keys = [k.strip() for k in entry.get().split("+")]
            hotkeys_config[action]["keys"] = keys
        save_hotkeys()
        hotkey_window.destroy()
    
    ttk.Button(buttons_frame, text="ANNULLA", style='Secondary.TButton',
              command=hotkey_window.destroy).pack(side="left")
    ttk.Button(buttons_frame, text="SALVA", style='Primary.TButton',
              command=save_and_close).pack(side="right")

# Funzioni di sistema
def create_icon_image():
    """Crea icona per system tray migliorata"""
    width, height = 64, 64
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Hexagon moderno
    create_hexagon_on_image(draw, 32, 32, 28)
    
    return image

def create_hexagon_on_image(draw, x, y, size):
    points = []
    for i in range(6):
        angle = i * 60 * math.pi / 180
        px = x + size * math.cos(angle)
        py = y + size * math.sin(angle)
        points.extend([px, py])
    
    draw.polygon(points, outline=ACCENT_COLOR, fill=DARKER_BG, width=3)
    
    # Testo centrale
    try:
        font = ImageFont.truetype("segoeui.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    draw.text((x-10, y-8), "LT", fill=ACCENT_COLOR, font=font)

tray_icon = None
def minimize_to_tray():
    global tray_icon
    
    def show_window(icon, item=None):
        root.deiconify()
        icon.stop()
    
    def exit_app(icon, item=None):
        icon.stop()
        root.destroy()
    
    tray_icon = Icon(
        "LeagueTools",
        create_icon_image(),
        "League Tools",
        menu=Menu(
            MenuItem("Mostra", show_window),
            MenuItem("Esci", exit_app),
        ),
    )
    
    root.withdraw()
    threading.Thread(target=tray_icon.run, daemon=True).start()

# Funzioni ping monitor
monitoring_ping_check = False

def display_ping_status(ping_time):
    """Aggiorna l'indicatore di ping"""
    if 'ping_indicator_canvas' not in globals():
        return
        
    canvas = ping_indicator_canvas
    canvas.delete("all")
    
    if ping_time is None:
        color = "#888888"
    elif ping_time > 200:
        color = LOG_ERROR
    elif ping_time > 100:
        color = LOG_WARNING
    else:
        color = LOG_SUCCESS
    
    canvas.create_oval(2, 2, 18, 18, fill=color, outline=BORDER_COLOR, width=1)

def get_ping():
    """Ottiene il ping verso il server Riot"""
    try:
        cmd = ["ping", "-n", "1", RIOT_SERVER_IP] if os.name == "nt" else ["ping", "-c", "1", RIOT_SERVER_IP]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                              text=True, timeout=5)
        
        if result.returncode != 0:
            return None
        
        import re
        # Ricerca pattern di tempo in millisecondi nell'output
        matches = re.findall(r'(\d+[.,]?\d*)\s*ms', result.stdout)
        
        if matches:
            try:
                time_ms = float(matches[0].replace(',', '.'))
                return int(time_ms)
            except ValueError:
                return None
        
        # Fallback per pattern alternativi come "time=X" 
        time_pattern = re.search(r'(?:time|tempo|zeit|temps|tiempo)\s*=\s*(\d+[.,]?\d*)', result.stdout, re.IGNORECASE)
        if time_pattern:
            try:
                time_ms = float(time_pattern.group(1).replace(',', '.'))
                return int(time_ms)
            except ValueError:
                return None
        
        return None
        
    except subprocess.TimeoutExpired:
        return None
    except Exception:
        return None

def test_ping_once():
    """Esegue un singolo test di ping"""
    try:
        ping_time = get_ping()
        if ping_time is not None:
            display_ping_status(ping_time)
            if ping_time > 200:
                log_message(f"Test ping: {ping_time}ms - Connessione instabile", "ERROR")
            elif ping_time > 100:
                log_message(f"Test ping: {ping_time}ms - Connessione lenta", "WARNING")
            else:
                log_message(f"Test ping: {ping_time}ms - Connessione ottima", "SUCCESS")
        else:
            display_ping_status(None)
            log_message("Test ping fallito - Server non raggiungibile", "ERROR")
    except Exception as e:
        log_message(f"Errore durante il test di ping: {str(e)}", "ERROR")
        display_ping_status(None)

def monitor_ping_loop():
    """Loop di monitoraggio ping continuo"""
    failure_count = 0
    max_failures = 3
    
    while monitoring_ping_check:
        try:
            ping_time = get_ping()
            display_ping_status(ping_time)
            
            if ping_time is not None:
                failure_count = 0
                if ping_time > 200:
                    log_message(f"Ping: {ping_time}ms - Connessione instabile", "ERROR")
                elif ping_time > 100:
                    log_message(f"Ping: {ping_time}ms - Connessione lenta", "WARNING")
                else:
                    log_message(f"Ping: {ping_time}ms", "INFO")
            else:
                failure_count += 1
                if failure_count >= max_failures:
                    log_message(f"Ping non disponibile dopo {max_failures} tentativi", "ERROR")
                    failure_count = 0
                else:
                    log_message(f"Tentativo ping {failure_count}/{max_failures} fallito", "WARNING")
                    
        except Exception as e:
            log_message(f"Errore monitoraggio ping: {str(e)}", "ERROR")
        
        time.sleep(5)

def start_ping_monitoring():
    """Avvia il monitoraggio continuo del ping"""
    global monitoring_ping_check
    if not monitoring_ping_check:
        monitoring_ping_check = True
        log_message("Monitoraggio ping continuo avviato", "SUCCESS")
        threading.Thread(target=monitor_ping_loop, daemon=True).start()
    else:
        log_message("Monitoraggio ping già attivo", "WARNING")

def stop_ping_monitoring():
    """Ferma il monitoraggio continuo del ping"""
    global monitoring_ping_check
    if monitoring_ping_check:
        monitoring_ping_check = False
        log_message("Monitoraggio ping fermato", "STOP")
        display_ping_status(None)
    else:
        log_message("Monitoraggio ping non attivo", "WARNING")

# Funzioni hotkeys
def setup_hotkey_listeners():
    """Configura i listener per le hotkeys"""
    pressed_keys = set()
    
    def on_press(key):
        try:
            if hasattr(key, 'char') and key.char:
                pressed_keys.add(key.char.lower())
            elif hasattr(key, 'name'):
                pressed_keys.add(key.name)
            
            # Controlla combinazioni hotkeys
            for action, config in hotkeys_config.items():
                if set(config["keys"]) <= pressed_keys:
                    execute_hotkey_action(action)
                    pressed_keys.clear()
                    break
                    
        except Exception as e:
            log_message(f"Errore hotkey: {str(e)}", "ERROR")
    
    def on_release(key):
        try:
            if hasattr(key, 'char') and key.char:
                pressed_keys.discard(key.char.lower())
            elif hasattr(key, 'name'):
                pressed_keys.discard(key.name)
        except Exception:
            pass
    
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def execute_hotkey_action(action):
    """Esegue l'azione associata alla hotkey"""
    actions = {
        "create_lobby": handle_create_normal_lobby,
        "start_queue": handle_start_queue,
        "stop_queue": handle_stop_queue,
        "start_monitoring": handle_start_monitoring,
        "stop_monitoring": handle_stop_monitoring,
        "custom": handle_create_custom_lobby
    }
    
    if action in actions:
        try:
            actions[action]()
            log_message(f"Hotkey {action} eseguita", "INFO")
        except Exception as e:
            log_message(f"Errore esecuzione hotkey {action}: {str(e)}", "ERROR")

# Configurazione hotkeys di default
hotkeys_config = {
    "create_lobby": {"keys": ["ctrl", "alt", "l"], "description": "Crea Lobby Normale"},
    "start_queue": {"keys": ["ctrl", "alt", "q"], "description": "Avvia Coda"},
    "stop_queue": {"keys": ["ctrl", "alt", "s"], "description": "Ferma Coda"},
    "start_monitoring": {"keys": ["ctrl", "alt", "m"], "description": "Avvia Auto Accept"},
    "stop_monitoring": {"keys": ["ctrl", "alt", "n"], "description": "Ferma Auto Accept"},
    "custom": {"keys": ["ctrl", "alt", "c"], "description": "Crea Lobby Personalizzata"}
}

# Variabili globali
running = False

def main():
    """Funzione principale"""
    global root
    
    # Crea cartelle necessarie
    create_assets_folders()
    create_role_icons()
    
    # Crea finestra principale
    root = create_main_window()
    
    # Carica configurazione
    load_hotkeys()
    
    # Avvia hotkey listener
    threading.Thread(target=setup_hotkey_listeners, daemon=True).start()
    
    # Messaggio di avvio
    log_message("League Tools v2.0 avviato con successo", "SUCCESS")
    log_message("Interfaccia grafica migliorata e ottimizzazioni applicate", "INFO")
    
    # Gestione chiusura
    def on_closing():
        global monitoring_ping_check, running
        monitoring_ping_check = False
        running = False
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Avvia loop principale
    root.mainloop()

if __name__ == "__main__":
    main()