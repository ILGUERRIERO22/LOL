import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import threading
import glob
import sys


try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ... (tutto il resto dei tuoi import rimane uguale)

# Directory base del launcher.
# - Quando stai sviluppando (python main.py): usa la cartella dove sta main.py
# - Quando usi l'eseguibile compilato (LOL Launcher.exe): usa la cartella in cui si trova quell'exe
BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

def run_tool(folder_name, exe_name):
    """
    Avvia un tool esterno (.exe) in modo portabile.
    Funziona se:
    - stai lanciando il launcher compilato (LOL Launcher.exe)
    - hai spostato la cartella 'dist' su un altro percorso
    - lanci tramite Logitech G Hub (working dir random)

    Assunzione struttura:
    dist/
        LOL Launcher/LOL Launcher.exe  <-- questo programma
        {folder_name}/{exe_name}       <-- gli altri tool
    """

    if getattr(sys, "frozen", False):
        # Stai girando come exe (LOL Launcher.exe)
        launcher_dir = os.path.dirname(sys.executable)
    else:
        # Stai girando da python main.py (sviluppo), quindi
        # immaginiamo struttura simile:
        # LOL/
        #   Script/main.py     <-- questo file
        #   dist/Wallet/Wallet.exe
        launcher_dir = os.path.dirname(os.path.abspath(__file__))

    # suite_root = cartella sorella comune (es. ...\dist)
    suite_root = os.path.abspath(os.path.join(launcher_dir, os.pardir))

    # percorso completo dell'exe del tool richiesto
    exe_path = os.path.join(suite_root, folder_name, exe_name)
    workdir = os.path.join(suite_root, folder_name)

    if not os.path.exists(exe_path):
        messagebox.showerror(
            "Exe non trovato",
            (
                "Il launcher è partito (anche da Logitech), ma non riesce a trovare l'eseguibile richiesto.\n\n"
                f"Cartella tool dichiarata: {folder_name}\n"
                f"Nome exe dichiarato:     {exe_name}\n\n"
                "Percorso costruito:\n"
                f"{exe_path}\n\n"
                "Quindi controlla sul disco:\n"
                f"- Esiste la cartella {workdir} ?\n"
                f"- Dentro c'è davvero un file chiamato {exe_name} ?\n\n"
                "Se il nome/cartella non coincidono, aggiorna SCRIPT_TO_EXE."
            )
        )
        return

    try:
        subprocess.Popen(
            [exe_path],
            shell=False,
            cwd=workdir  # importantissimo: così il tool parte dentro la sua stessa cartella
        )
    except Exception as e:
        messagebox.showerror(
            "Errore di avvio",
            f"Ho trovato {exe_path} ma non riesco ad avviarlo.\n\nDettagli:\n{e}"
        )



# Mappa tra il nome dello script .py e l'exe da lanciare
# Chiave = nome che compare in SCRIPTS / create_script_card (es. "Shop Riot.py")
# Valore = (cartella dove sta l'exe, nome dell'exe)
SCRIPT_TO_EXE = {
    "Wallet.py":                      ("Wallet", "Wallet.exe"),
    "Shop Riot.py":                   ("Shop Riot", "Shop Riot.exe"),
    "rank.py":                        ("rank", "rank.exe"),
    "match.py":                       ("match", "match.exe"),
    "replay.py":                      ("Replay", "Replay.exe"),
    "Stato.py":                       ("Stato", "Stato.exe"),
    "GameMode.py":                    ("GameMode", "GameMode.exe"),
    "login.py":                       ("login", "login.exe"),
    "friendlist_manager.py":          ("friendlist_manager", "friendlist_manager.exe"),
    "friendlist.py":                  ("friendlist_manager", "friendlist_manager.exe"),
    "Info Account.py":                ("Info Account", "Info Account.exe"),
    "change_riotid.py":               ("change_riotid", "change_riotid.exe"),
    "Maestrie.py":                    ("Maestrie", "Maestrie.exe"),
    "loot.py":                        ("loot", "loot.exe"),
    "calcolaRP.py":                   ("calcolaRP", "calcolaRP.exe"),
    "convertitore.py":                ("convertitore", "convertitore.exe"),
    "genera_email.py":                ("genera_email", "genera_email.exe"),
    "image_converter.py":             ("image_converter", "image_converter.exe"),
    "album.py":                       ("album", "album.exe"),
    "gift.py":                        ("gift", "gift.exe"),
    "lol_champion_select_app.py":     ("lol_champion_select_app", "lol_champion_select_app.exe"),
    "lol-messenger.py":               ("lol-messenger", "lol-messenger.exe"),
    "lol-accept-queue-script.py":     ("accept_queue", "accept_queue.exe"),
}



TOOLS = [
    # Core utilities
    {"label": "Wallet",                "folder": "Wallet",                "exe": "Wallet.exe"},
    {"label": "Shop Riot",             "folder": "Shop Riot",             "exe": "Shop Riot.exe"},
    {"label": "Rank",                  "folder": "rank",                  "exe": "rank.exe"},
    {"label": "Match Live / Lobby",    "folder": "match",                 "exe": "match.exe"},
    {"label": "Stato Profilo / Status","folder": "Stato",                 "exe": "Stato.exe"},
    {"label": "Replay Uploader",       "folder": "Replay",                "exe": "Replay.exe"},
    {"label": "Game Mode / Lobby",     "folder": "GameMode",              "exe": "GameMode.exe"},
    {"label": "Login Riot",            "folder": "login",                 "exe": "login.exe"},
    {"label": "Friendlist Manager",    "folder": "friendlist_manager",    "exe": "friendlist_manager.exe"},

    # Utility comfort / extra
    {"label": "Info Account",          "folder": "Info Account",          "exe": "Info Account.exe"},
    {"label": "Cambia Riot ID",        "folder": "change_riotid",         "exe": "change_riotid.exe"},
    {"label": "Maestrie",              "folder": "Maestrie",              "exe": "Maestrie.exe"},
    {"label": "Loot / Ricompense",     "folder": "loot",                  "exe": "loot.exe"},
    {"label": "Shop RP / Calcolo RP",  "folder": "calcolaRP",             "exe": "calcolaRP.exe"},
    {"label": "Convertitore Valute",   "folder": "convertitore",          "exe": "convertitore.exe"},
    {"label": "Genera Email",          "folder": "genera_email",          "exe": "genera_email.exe"},
    {"label": "Image Converter",       "folder": "image_converter",       "exe": "image_converter.exe"},
    {"label": "Album Screenshot/Skin", "folder": "album",                 "exe": "album.exe"},
    {"label": "Gift / Regali",         "folder": "gift",                  "exe": "gift.exe"},
    {"label": "Champion Select Tool",  "folder": "lol_champion_select_app","exe": "lol_champion_select_app.exe"},
    {"label": "Auto Accept Queue",     "folder": "accept_queue",          "exe": "accept_queue.exe"},
    {"label": "Messenger LoL",         "folder": "lol-messenger",         "exe": "lol-messenger.exe"},
]





# Configurazione centralizzata: dizionario con nomi degli script e descrizioni
SCRIPTS = {
    "Shop Riot.py": "Visualizza Offerte Shop Riot",
    "Info Account.py": "Visualizza Info Account",
    "login.py": "Effettua il login",
    "calcolaRP.py": "Calcola il costo in RP",
    "GameMode.py": "GameMode e Auto Accept",
    "lol_champion_select_app.py": "Champion Select",
    "Wallet.py": "Valute",
    "Maestrie.py": "Maestrie",
    "Stato.py": "Modifica stato",
    "lol-messenger.py": "LOL Messenger",
    "friendlist.py": "Amici",
    "friendlist_manager.py": "Gestione amici",
    "rank.py": "Ranked stats",
    "change_riotid.py": "Cambia Riot ID",
    "replay.py": "Replay",
    "gift.py": "Invia un regalo",
    "genera_email.py": "Genera Email temporanea",
    "album.py": "Aggiorna foto",
    "convertitore.py": "Convertitore video",
    "match.py": "Cronologia",
    "loot.py": "Inventario",
    "image_converter.py": "Convertitore immagini"
}

# Configurazione delle cartelle dove cercare gli script
SCRIPT_FOLDERS = [
    ".",  # Cartella corrente
    "scripts",
    "tools",
    "src",
    "Scripts",
    "Tools",
    "league_tools",
    "lol_scripts"
]
            
CATEGORIES = {
    "info": ["Shop Riot.py", "loot.py", "Info Account.py", "Wallet.py", "rank.py"],
    "partita": ["GameMode.py","lol_champion_select_app.py", "replay.py", "match.py"],
    "amici": ["friendlist.py", "gift.py", "friendlist_manager.py", "lol-messenger.py"],
    "account": ["Maestrie.py", "change_riotid.py", "Stato.py"],
    "utility": ["login.py", "genera_email.py", "album.py", "convertitore.py", "calcolaRP.py"]
}

# Icone per le categorie (caratteri Unicode corretti)
CATEGORY_ICONS = {
    "info": "📊",
    "partita": "🎮", 
    "amici": "👥",
    "account": "👤", 
    "utility": "🔧",
    "Tutti": "📋"
}

class LeagueApp:
    """Classe principale dell'applicazione."""
    
    def __init__(self, root):
        self.root = root
        self.setup_theme()
        self.script_cards = []
        self.active_category_buttons = {}
        self.sidebar_visible = False
        self.current_hover_widget = None
        
        # Cache per i percorsi degli script trovati
        self.script_paths = {}
        
        # Aggiungi un gestore per chiudere correttamente l'applicazione
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Scansiona i percorsi degli script all'avvio
        self.setup_main_window()

        self.scan_script_paths()

        self.show_all_scripts()
        
        

    def scan_script_paths(self):
        """
        Segna tutti gli script come disponibili e prepara i campi che il resto
        dell'app si aspetta:
        - self.available_scripts[script_name] -> True/False (per le card)
        - self.script_paths[script_name]      -> stringa da mostrare sotto il titolo
        - self.status_label (in alto a destra)

        Nota importante:
        Non controlliamo più davvero il filesystem.
        Per noi "trovato" = "lo script è uno dei tool noti".
        L'esecuzione reale poi la fa run_tool() usando SCRIPT_TO_EXE.
        """

        self.available_scripts = {}
        self.script_paths = {}

        # Siamo dentro l'exe buildato (launcher congelato da PyInstaller)?
        is_frozen = getattr(sys, "frozen", False)

        for script_name in SCRIPTS.keys():
            # 1. Questo script è considerato disponibile sempre.
            self.available_scripts[script_name] = True

            # 2. Percorso da mostrare in UI (estetico, non usato per eseguire)
            #    Prima nel tuo launcher mostravano robe tipo ".\_internal\login.py".
            #    Quindi lo riproduciamo uguale così l'interfaccia resta identica.
            if is_frozen:
                nice_path = f".\\_internal\\{script_name}"
            else:
                nice_path = f".\\_internal\\{script_name}"

            self.script_paths[script_name] = nice_path

        # 3. Aggiorna lo stato in alto a destra
        total_count = len(SCRIPTS)
        found_count = total_count  # per la nostra logica attuale, tutti disponibili

        if hasattr(self, "status_label") and self.status_label:
            # verde se tutto trovato
            self.status_label.config(
                text=f"✅ {found_count}/{total_count} script trovati",
                fg=self.current_theme["success"]
            )


    def find_script_path(self, script_name):
        """Trova il percorso completo di uno script."""
        # Prima controlla la cache
        if script_name in self.script_paths:
            return self.script_paths[script_name]
        
        # Se non è nella cache, cerca nelle cartelle configurate
        for folder in SCRIPT_FOLDERS:
            script_path = os.path.join(folder, script_name)
            if os.path.exists(script_path):
                self.script_paths[script_name] = script_path
                return script_path
        
        # Cerca ricorsivamente
        for folder in SCRIPT_FOLDERS:
            if os.path.exists(folder):
                search_pattern = os.path.join(folder, "**", script_name)
                matches = glob.glob(search_pattern, recursive=True)
                if matches:
                    script_path = matches[0]
                    self.script_paths[script_name] = script_path
                    return script_path
        
        return None

    def get_available_scripts(self):
        """Restituisce solo gli script che sono stati trovati sul sistema."""
        available_scripts = {}
        for script_name, description in SCRIPTS.items():
            if script_name in self.script_paths:
                available_scripts[script_name] = description
        return available_scripts

    def on_close(self):
        """Gestisce la chiusura corretta dell'applicazione."""
        # Termina eventuali thread in esecuzione
        for thread in threading.enumerate():
            if thread is not threading.main_thread():
                if hasattr(thread, 'daemon') and not thread.daemon:
                    try:
                        thread.join(0.1)
                    except:
                        pass
        
        self.root.destroy()
    
    def setup_theme(self):
        """Configura i temi dell'applicazione."""
        # Tema scuro migliorato
        self.dark_theme = {
            "bg_dark": "#0F1419",         # Sfondo principale più scuro
            "bg_medium": "#1E2328",       # Sfondo secondario
            "bg_light": "#2A2E35",        # Sfondo elementi
            "accent_primary": "#C89B3C",  # Oro di LoL
            "accent_secondary": "#0F2027", # Blu scuro più sobrio
            "text_light": "#F0E6D2",      # Testo chiaro
            "text_medium": "#CDBE91",     # Testo secondario
            "text_dark": "#0F1419",       # Testo scuro per contrasto
            "button_hover": "#F0E6D2",    # Hover pulsante
            "card_bg": "#1E2328",         # Sfondo card
            "card_hover": "#3C3C41",      # Hover card
            "border": "#463714",          # Bordo elementi
            "success": "#3E8E41",         # Verde più scuro e leggibile
            "error": "#E74C3C",           # Colore errore
            "warning": "#F39C12"          # Colore avvertimento
        }
        
        # Tema chiaro migliorato
        self.light_theme = {
            "bg_dark": "#F5F5F5",
            "bg_medium": "#FFFFFF",
            "bg_light": "#FAFAFA",
            "accent_primary": "#C89B3C",
            "accent_secondary": "#2C3E50",
            "text_light": "#2C3E50",
            "text_medium": "#7F8C8D",
            "text_dark": "#FFFFFF",
            "button_hover": "#34495E",
            "card_bg": "#FFFFFF",
            "card_hover": "#ECF0F1",
            "border": "#BDC3C7",
            "success": "#27AE60",
            "error": "#E74C3C",
            "warning": "#F39C12"
        }
        
        self.current_theme = self.dark_theme
    
    def setup_main_window(self):
        """Configura la finestra principale."""
        self.root.configure(bg=self.current_theme["bg_dark"])
        
        # Configura lo stile TTK
        self.setup_ttk_styles()
        
        # Crea la sidebar
        self.create_sidebar()
        
        # Crea il frame principale del contenuto
        self.main_content_frame = tk.Frame(self.root, bg=self.current_theme["bg_dark"])
        self.main_content_frame.pack(side="left", fill="both", expand=True)

        # Header con titolo e pulsante della sidebar
        self.create_header()
        
        # Barra di ricerca
        self.create_search_bar()
        
        # Area principale con scrolling
        self.create_main_area()
        
        # Footer
        self.create_footer()
        
        # Mostra tutti gli script inizialmente
        self.show_all_scripts()

    def setup_ttk_styles(self):
        """Configura gli stili TTK."""
        style = ttk.Style()
        style.theme_use("default")
        
        # Configurazione scrollbar personalizzata
        style.configure("Custom.Vertical.TScrollbar", 
                      background=self.current_theme["bg_medium"],
                      troughcolor=self.current_theme["bg_dark"],
                      arrowcolor=self.current_theme["text_light"],
                      borderwidth=0,
                      lightcolor=self.current_theme["bg_light"],
                      darkcolor=self.current_theme["bg_medium"])
        
        style.map("Custom.Vertical.TScrollbar",
                 background=[('active', self.current_theme["accent_primary"])])

    def create_header(self):
        """Crea l'header dell'applicazione."""
        header_frame = tk.Frame(self.main_content_frame, bg=self.current_theme["bg_dark"], 
                               padx=20, pady=15)
        header_frame.pack(side="top", fill="x")

        # Pulsante toggle sidebar con stile migliorato
        self.sidebar_toggle_btn = tk.Button(
            header_frame, 
            text="☰" if not self.sidebar_visible else "✕", 
            font=("Segoe UI", 18, "bold"),
            bg=self.current_theme["accent_primary"],
            fg=self.current_theme["text_dark"],
            activebackground=self.current_theme["button_hover"],
            activeforeground=self.current_theme["accent_primary"],
            relief="flat",
            padx=12, 
            pady=8,
            cursor="hand2",
            command=self.toggle_sidebar
        )
        self.sidebar_toggle_btn.pack(side="left", padx=(0, 20))
        
        # Effetti hover per il pulsante toggle
        def on_toggle_enter(e):
            self.sidebar_toggle_btn.configure(bg=self.current_theme["button_hover"], 
                                            fg=self.current_theme["accent_primary"])
        
        def on_toggle_leave(e):
            self.sidebar_toggle_btn.configure(bg=self.current_theme["accent_primary"], 
                                            fg=self.current_theme["text_dark"])
        
        self.sidebar_toggle_btn.bind("<Enter>", on_toggle_enter)
        self.sidebar_toggle_btn.bind("<Leave>", on_toggle_leave)
        
        # Titolo principale con gradiente simulato
        title_label = tk.Label(header_frame, 
                             text="⚔️ League of Legends Tool", 
                             font=("Segoe UI", 24, "bold"),
                             fg=self.current_theme["accent_primary"],
                             bg=self.current_theme["bg_dark"])
        title_label.pack(side="left")
        
        # Indicatore script trovati
        #available_count = len(self.script_paths)
        #total_count = len(SCRIPTS)
        
        #status_color = self.current_theme["success"] if available_count > total_count * 0.7 else (
         #   self.current_theme["warning"] if available_count > 0 else self.current_theme["error"]
        #)
        
        #status_label = tk.Label(header_frame,
         #                      text=f"📦 {available_count}/{total_count} script trovati",
          #                     font=("Segoe UI", 10, "bold"),
           #                    fg=status_color,
            #                   bg=self.current_theme["bg_dark"])
        #status_label.pack(side="right")

    def create_search_bar(self):
        """Crea la barra di ricerca."""
        search_container = tk.Frame(self.main_content_frame, bg=self.current_theme["bg_dark"], 
                                   padx=20, pady=10)
        search_container.pack(fill="x")
        
        # Frame per la barra di ricerca
        search_frame = tk.Frame(search_container, bg=self.current_theme["card_bg"], 
                               relief="solid", bd=1)
        search_frame.pack(fill="x", ipady=8)
        
        # Icona di ricerca (usando carattere Unicode)
        search_icon_label = tk.Label(search_frame, text="🔍", 
                                   font=("Segoe UI", 14),
                                   bg=self.current_theme["card_bg"],
                                   fg=self.current_theme["text_medium"])
        search_icon_label.pack(side="left", padx=(15, 5))
        
        # Campo di input
        self.search_entry = tk.Entry(search_frame, 
                                   font=("Segoe UI", 12), 
                                   bg=self.current_theme["card_bg"], 
                                   fg=self.current_theme["text_light"], 
                                   borderwidth=0, 
                                   highlightthickness=0,
                                   insertbackground=self.current_theme["accent_primary"])
        self.search_entry.pack(fill="x", expand=True, padx=(0, 15))
        
        # Placeholder text
        self.search_placeholder = "Cerca uno script..."
        self.search_entry.insert(0, self.search_placeholder)
        self.search_entry.configure(fg=self.current_theme["text_medium"])
        
        # Eventi per il placeholder
        def on_search_focus_in(event):
            if self.search_entry.get() == self.search_placeholder:
                self.search_entry.delete(0, tk.END)
                self.search_entry.configure(fg=self.current_theme["text_light"])
        
        def on_search_focus_out(event):
            if not self.search_entry.get():
                self.search_entry.insert(0, self.search_placeholder)
                self.search_entry.configure(fg=self.current_theme["text_medium"])
        
        def on_search_key(event):
            # Ricerca in tempo reale
            self.root.after(300, self.perform_search)
        
        self.search_entry.bind("<FocusIn>", on_search_focus_in)
        self.search_entry.bind("<FocusOut>", on_search_focus_out)
        self.search_entry.bind("<KeyRelease>", on_search_key)

    def create_main_area(self):
        """Crea l'area principale dell'applicazione."""
        main_frame = tk.Frame(self.main_content_frame, bg=self.current_theme["bg_dark"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Canvas per lo scrolling
        self.canvas = tk.Canvas(main_frame, bg=self.current_theme["bg_dark"], 
                               highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", 
                                command=self.canvas.yview, 
                                style="Custom.Vertical.TScrollbar")
        
        # Frame scrollabile
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.current_theme["bg_dark"])
        
        # Configura il layout a griglia
        for i in range(3):  # 3 colonne
            self.scrollable_frame.columnconfigure(i, weight=1, uniform="column", minsize=280)
        
        self.scrollable_frame.bind("<Configure>", 
                                 lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Scrolling con la ruota del mouse
        def on_mouse_scroll(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.canvas.bind("<MouseWheel>", on_mouse_scroll)

    def create_footer(self):
        """Crea il footer dell'applicazione."""
        footer_frame = tk.Frame(self.main_content_frame, bg=self.current_theme["bg_medium"], 
                               padx=20, pady=15)
        footer_frame.pack(side="bottom", fill="x")
        
        # Frame per i pulsanti
        button_frame = tk.Frame(footer_frame, bg=self.current_theme["bg_medium"])
        button_frame.pack(side="left")
        
        # Pulsanti footer con stile migliorato
        buttons_config = [
            ("❓ Aiuto", self.show_help),
            ("🎨 Cambia Tema", self.toggle_theme),
            ("🔄 Aggiorna", self.refresh_scripts),
            ("🗂 Percorsi Script", self.show_script_paths)
        ]
        
        for text, command in buttons_config:
            btn = tk.Button(
                button_frame, 
                text=text, 
                font=("Segoe UI", 10, "bold"),
                bg=self.current_theme["accent_secondary"],
                fg="#FFFFFF",  # Testo bianco per migliore contrasto
                activebackground=self.current_theme["button_hover"],
                activeforeground=self.current_theme["accent_secondary"],
                relief="flat",
                padx=15, 
                pady=8,
                cursor="hand2",
                command=command
            )
            btn.pack(side="left", padx=(0, 10))
            
            # Effetti hover
            def make_hover_effects(button):
                def on_enter(e):
                    button.configure(bg=self.current_theme["button_hover"], 
                                   fg=self.current_theme["accent_secondary"])
                def on_leave(e):
                    button.configure(bg=self.current_theme["accent_secondary"], 
                                   fg=self.current_theme["text_dark"])
                return on_enter, on_leave
            
            enter_func, leave_func = make_hover_effects(btn)
            btn.bind("<Enter>", enter_func)
            btn.bind("<Leave>", leave_func)
        
        # Label footer
        footer_label = tk.Label(
            footer_frame,
            text="© 2024-2025 League Tools v5.5 - Sviluppato da Ahristogatti",
            font=("Segoe UI", 9, "italic"),
            fg=self.current_theme["text_medium"],
            bg=self.current_theme["bg_medium"]
        )
        footer_label.pack(side="right")

    def create_sidebar(self):
        """Crea la sidebar con le categorie."""
        self.sidebar_frame = tk.Frame(self.root, bg=self.current_theme["bg_medium"], width=280)
        self.sidebar_frame.pack_propagate(False)
        
        # Canvas per scrolling della sidebar
        sidebar_canvas = tk.Canvas(self.sidebar_frame, bg=self.current_theme["bg_medium"], 
                                 highlightthickness=0, width=260)
        sidebar_scrollbar = ttk.Scrollbar(self.sidebar_frame, orient="vertical", 
                                        command=sidebar_canvas.yview, 
                                        style="Custom.Vertical.TScrollbar")
        
        sidebar_content = tk.Frame(sidebar_canvas, bg=self.current_theme["bg_medium"])
        
        sidebar_content.bind("<Configure>", 
                           lambda e: sidebar_canvas.configure(scrollregion=sidebar_canvas.bbox("all")))
        sidebar_canvas.create_window((0, 0), window=sidebar_content, anchor="nw", width=260)
        sidebar_canvas.configure(yscrollcommand=sidebar_scrollbar.set)
        
        sidebar_canvas.pack(side="left", fill="both", expand=True)
        sidebar_scrollbar.pack(side="right", fill="y")
        
        # Titolo sidebar
        title_label = tk.Label(sidebar_content, 
                             text="🗂 Categorie", 
                             font=("Segoe UI", 18, "bold"), 
                             fg=self.current_theme["accent_primary"], 
                             bg=self.current_theme["bg_medium"])
        title_label.pack(pady=(20, 15), padx=15)
        
        # Pulsante "Tutti"
        all_btn = self.create_sidebar_button(sidebar_content, "📋 Tutti", 
                                           lambda: self.show_category_scripts("Tutti"))
        all_btn.pack(fill="x", pady=2, padx=15)
        
        # Pulsanti categorie
        for category, scripts in CATEGORIES.items():
            icon = CATEGORY_ICONS.get(category, "📄")
            category_display = category.title()
            btn = self.create_sidebar_button(sidebar_content, 
                                           f"{icon} {category_display}", 
                                           lambda c=category: self.show_category_scripts(c))
            btn.pack(fill="x", pady=2, padx=15)

    def create_sidebar_button(self, parent, text, command):
        """Crea un pulsante per la sidebar con effetto hover migliorato."""
        btn_frame = tk.Frame(parent, bg=self.current_theme["bg_medium"])
        
        btn = tk.Button(btn_frame, 
                       text=text, 
                       font=("Segoe UI", 11, "bold"), 
                       bg=self.current_theme["bg_medium"], 
                       fg=self.current_theme["text_light"], 
                       relief="flat", 
                       anchor="w", 
                       padx=15, 
                       pady=12,
                       cursor="hand2",
                       command=command)
        btn.pack(fill="x")
        
        def on_enter(e):
            btn_frame.config(bg=self.current_theme["accent_primary"])
            btn.config(bg=self.current_theme["accent_primary"], 
                      fg=self.current_theme["text_dark"])
        
        def on_leave(e):
            btn_frame.config(bg=self.current_theme["bg_medium"])
            btn.config(bg=self.current_theme["bg_medium"], 
                      fg=self.current_theme["text_light"])
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        btn_frame.bind("<Enter>", on_enter)
        btn_frame.bind("<Leave>", on_leave)

        return btn_frame

    def create_script_card(self, parent, script_name, description):
        """Crea una card per uno script con design migliorato."""
        # Verifica se lo script è disponibile
        is_available = script_name in self.script_paths
        
        card_frame = tk.Frame(parent, 
                            bg=self.current_theme["card_bg"], 
                            relief="solid", 
                            bd=1,
                            padx=20, 
                            pady=20)
        
        # Indicatore di disponibilità
        status_frame = tk.Frame(card_frame, bg=self.current_theme["card_bg"])
        status_frame.pack(fill="x", pady=(0, 5))
        
        status_text = "✅ Disponibile" if is_available else "❌ Non trovato"
        status_color = self.current_theme["success"] if is_available else self.current_theme["error"]
        
        status_label = tk.Label(status_frame, 
                               text=status_text, 
                               font=("Segoe UI", 9, "bold"), 
                               fg=status_color, 
                               bg=self.current_theme["card_bg"])
        status_label.pack(side="right")
        
        # Titolo dello script (rimuove l'estensione .py per una visualizzazione più pulita)
        display_name = script_name.replace(".py", "")
        title_label = tk.Label(card_frame, 
                             text=display_name, 
                             font=("Segoe UI", 14, "bold"), 
                             fg=self.current_theme["accent_primary"], 
                             bg=self.current_theme["card_bg"],
                             wraplength=200)
        title_label.pack(anchor="w")
        
        # Separatore
        separator = tk.Frame(card_frame, height=2, bg=self.current_theme["border"])
        separator.pack(fill="x", pady=(8, 10))
        
        # Descrizione dello script
        desc_label = tk.Label(card_frame, 
                            text=description, 
                            font=("Segoe UI", 10), 
                            fg=self.current_theme["text_medium"], 
                            bg=self.current_theme["card_bg"], 
                            wraplength=220,
                            justify="left")
        desc_label.pack(anchor="w", pady=(0, 15))
        
        # Percorso dello script (se disponibile)
        if is_available:
            path_label = tk.Label(card_frame,
                                text=f"📁 {self.script_paths[script_name]}",
                                font=("Segoe UI", 8),
                                fg=self.current_theme["text_medium"],
                                bg=self.current_theme["card_bg"],
                                wraplength=220,
                                justify="left")
            path_label.pack(anchor="w", pady=(0, 15))
        
        # Pulsante di esecuzione con design migliorato
        btn_text = "▶️ Esegui Script" if is_available else "❌ Non Disponibile"
        btn_color = self.current_theme["success"] if is_available else self.current_theme["error"]
        btn_state = "normal" if is_available else "disabled"
        
        # scegli cosa fare quando clicco
        if is_available and script_name in SCRIPT_TO_EXE:
            folder_name, exe_name = SCRIPT_TO_EXE[script_name]
            click_command = lambda fn=folder_name, ex=exe_name: run_tool(fn, ex)
        elif is_available:
            # fallback vecchio: prova a lanciare il .py col Python locale
            click_command = lambda sn=script_name: self.run_script(sn)
        else:
            click_command = None

        run_button = tk.Button(
            card_frame, 
            text=btn_text, 
            font=("Segoe UI", 11, "bold"), 
            bg=btn_color, 
            fg="#FFFFFF",
            activebackground=self.current_theme["button_hover"],
            activeforeground=btn_color,
            relief="flat",
            padx=20,
            pady=10,
            cursor="hand2" if is_available else "no",
            state=btn_state,
            command=click_command
        )
        run_button.pack(side="bottom", fill="x")

        
        # Effetti hover per il pulsante (solo se disponibile)
        if is_available:
            def on_btn_enter(e):
                run_button.configure(bg=self.current_theme["button_hover"], 
                                   fg=self.current_theme["success"])
            
            def on_btn_leave(e):
                run_button.configure(bg=self.current_theme["success"], 
                                   fg="#FFFFFF")
            
            run_button.bind("<Enter>", on_btn_enter)
            run_button.bind("<Leave>", on_btn_leave)
        
        # Effetti hover per la card
        def on_card_enter(e):
            card_frame.configure(bg=self.current_theme["card_hover"])
            title_label.configure(bg=self.current_theme["card_hover"])
            desc_label.configure(bg=self.current_theme["card_hover"])
            status_frame.configure(bg=self.current_theme["card_hover"])
            status_label.configure(bg=self.current_theme["card_hover"])
            if is_available and 'path_label' in locals():
                path_label.configure(bg=self.current_theme["card_hover"])
        
        def on_card_leave(e):
            card_frame.configure(bg=self.current_theme["card_bg"])
            title_label.configure(bg=self.current_theme["card_bg"])
            desc_label.configure(bg=self.current_theme["card_bg"])
            status_frame.configure(bg=self.current_theme["card_bg"])
            status_label.configure(bg=self.current_theme["card_bg"])
            if is_available and 'path_label' in locals():
                path_label.configure(bg=self.current_theme["card_bg"])
        
        card_frame.bind("<Enter>", on_card_enter)
        card_frame.bind("<Leave>", on_card_leave)
        title_label.bind("<Enter>", on_card_enter)
        title_label.bind("<Leave>", on_card_leave)
        desc_label.bind("<Enter>", on_card_enter)
        desc_label.bind("<Leave>", on_card_leave)
        
        return card_frame

    def clear_script_area(self):
        """Pulisce l'area degli script."""
        for card in self.script_cards:
            card.destroy()
        self.script_cards.clear()

    def show_all_scripts(self):
        """Mostra tutti gli script disponibili."""
        self.clear_script_area()
        
        row, col = 0, 0
        for script_name, description in SCRIPTS.items():
            card = self.create_script_card(self.scrollable_frame, script_name, description)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            self.script_cards.append(card)
            
            col += 1
            if col >= 3:  # 3 card per riga
                col = 0
                row += 1

    def show_category_scripts(self, category):
        """Mostra gli script di una categoria specifica."""
        self.clear_script_area()
        
        row, col = 0, 0
        
        if category == "Tutti":
            scripts_to_show = SCRIPTS.items()
        else:
            scripts_to_show = [(script, SCRIPTS.get(script, "")) 
                             for script in CATEGORIES.get(category, [])]
        
        for script_name, description in scripts_to_show:
            card = self.create_script_card(self.scrollable_frame, script_name, description)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            self.script_cards.append(card)
            
            col += 1
            if col >= 3:
                col = 0
                row += 1
        
        if not scripts_to_show:
            # Mostra messaggio se non ci sono script
            no_scripts_label = tk.Label(self.scrollable_frame,
                                      text=f"Nessuno script trovato per la categoria '{category}'",
                                      font=("Segoe UI", 12),
                                      fg=self.current_theme["text_medium"],
                                      bg=self.current_theme["bg_dark"])
            no_scripts_label.grid(row=0, column=0, columnspan=3, pady=50)
            self.script_cards.append(no_scripts_label)

    def perform_search(self):
        """Esegue la ricerca degli script."""
        search_term = self.search_entry.get().lower()
        
        if search_term == self.search_placeholder.lower() or not search_term:
            self.show_all_scripts()
            return
        
        self.clear_script_area()
        
        matching_scripts = []
        for script_name, description in SCRIPTS.items():
            if (search_term in script_name.lower() or 
                search_term in description.lower()):
                matching_scripts.append((script_name, description))
        
        if matching_scripts:
            row, col = 0, 0
            for script_name, description in matching_scripts:
                card = self.create_script_card(self.scrollable_frame, script_name, description)
                card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
                self.script_cards.append(card)
                
                col += 1
                if col >= 3:
                    col = 0
                    row += 1
        else:
            # Mostra messaggio di nessun risultato
            no_results_label = tk.Label(self.scrollable_frame,
                                      text=f"Nessun risultato per '{search_term}'",
                                      font=("Segoe UI", 12),
                                      fg=self.current_theme["text_medium"],
                                      bg=self.current_theme["bg_dark"])
            no_results_label.grid(row=0, column=0, columnspan=3, pady=50)
            self.script_cards.append(no_results_label)

    def run_script(self, script_name):
        """Esegue lo script selezionato in un thread separato."""
        def target():
            try:
                script_path = self.find_script_path(script_name)
                if not script_path:
                    self.show_notification(f"File '{script_name}' non trovato!", 
                                         color=self.current_theme["error"])
                    return
                
                # Converti in percorso assoluto per evitare problemi
                script_path = os.path.abspath(script_path)
                script_dir = os.path.dirname(script_path)
                
                print(f"Esecuzione script: {script_path}")
                print(f"Directory di lavoro: {script_dir}")
                
                # Su Windows, usa percorsi completi e nascondi la console
                if os.name == 'nt':  # Windows
                    # Configura per nascondere la finestra della console
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = subprocess.SW_HIDE
                    
                    # Prova diversi interpreti Python
                    python_commands = ['python', 'py', 'python.exe']
                    
                    for python_cmd in python_commands:
                        try:
                            result = subprocess.run([python_cmd, script_path], 
                                                  cwd=script_dir,
                                                  capture_output=True, 
                                                  text=True,
                                                  shell=False,
                                                  startupinfo=startupinfo,
                                                  creationflags=subprocess.CREATE_NO_WINDOW)
                            break
                        except FileNotFoundError:
                            continue
                    else:
                        # Se nessun comando Python funziona, prova con shell=True (nascosto)
                        result = subprocess.run(f'python "{script_path}"', 
                                              cwd=script_dir,
                                              capture_output=True, 
                                              text=True,
                                              shell=True,
                                              startupinfo=startupinfo,
                                              creationflags=subprocess.CREATE_NO_WINDOW)
                else:  # Unix/Linux/Mac
                    result = subprocess.run(['python3', script_path], 
                                          cwd=script_dir,
                                          capture_output=True, 
                                          text=True)
                
                if result.returncode == 0:
                    success_msg = f"{script_name} eseguito con successo"
                    if result.stdout.strip():
                        success_msg += f" - Output: {result.stdout.strip()[:300]}..."
                    self.show_notification(success_msg, color=self.current_theme["success"])
                else:
                    error_msg = result.stderr.strip()
                    if not error_msg and result.stdout.strip():
                        error_msg = result.stdout.strip()
                    
                    if not error_msg:
                        error_msg = f"Script terminato con codice {result.returncode}"
                    
                    self.show_notification(f"Errore in {script_name}: {error_msg[:100]}...", 
                                         color=self.current_theme["error"])
                    print(f"Errore completo: {result.stderr}")
                    
            except Exception as e:
                error_detail = str(e)
                self.show_notification(f"Errore imprevisto: {error_detail[:80]}...", 
                                     color=self.current_theme["error"])
                print(f"Errore completo nell'esecuzione di {script_name}: {error_detail}")
        
        # Avvia lo script in un thread separato
        threading.Thread(target=target, daemon=True).start()
        self.show_notification(f"Avvio {script_name}...", 
                             color=self.current_theme["accent_secondary"])

    def show_script_paths(self):
        """Mostra una finestra con i percorsi degli script trovati."""
        paths_window = tk.Toplevel(self.root)
        paths_window.title("🗂 Percorsi Script - League of Legends Tool")
        paths_window.geometry("800x600")
        paths_window.configure(bg=self.current_theme["bg_dark"])
        paths_window.resizable(True, True)

        # Centra la finestra
        paths_window.update_idletasks()
        x = (paths_window.winfo_screenwidth() // 2) - 400
        y = (paths_window.winfo_screenheight() // 2) - 300
        paths_window.geometry(f'800x600+{x}+{y}')
        
        # Frame principale
        main_frame = tk.Frame(paths_window, bg=self.current_theme["bg_dark"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titolo
        title_label = tk.Label(main_frame, 
                            text="🗂 Percorsi Script Scansionati", 
                            font=("Segoe UI", 18, "bold"),
                            fg=self.current_theme["accent_primary"],
                            bg=self.current_theme["bg_dark"])
        title_label.pack(pady=(0, 15))
        
        # Informazioni di scansione
        info_frame = tk.Frame(main_frame, bg=self.current_theme["card_bg"], padx=15, pady=10)
        info_frame.pack(fill="x", pady=(0, 15))
        
        found_count = len(self.script_paths)
        total_count = len(SCRIPTS)
        
        info_text = f"📊 Trovati: {found_count}/{total_count} script\n"
        info_text += f"📂 Cartelle scansionate: {', '.join(SCRIPT_FOLDERS)}"
        
        info_label = tk.Label(info_frame, text=info_text,
                            font=("Segoe UI", 10),
                            fg=self.current_theme["text_light"],
                            bg=self.current_theme["card_bg"],
                            justify="left")
        info_label.pack(anchor="w")
        
        # Canvas per scrolling
        canvas = tk.Canvas(main_frame, bg=self.current_theme["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview,
                                style="Custom.Vertical.TScrollbar")
        scrollable_frame = tk.Frame(canvas, bg=self.current_theme["bg_dark"])
        
        scrollable_frame.bind("<Configure>", 
                            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Lista degli script
        for script_name in sorted(SCRIPTS.keys()):
            script_frame = tk.Frame(scrollable_frame, bg=self.current_theme["card_bg"], 
                                  padx=15, pady=10, relief="solid", bd=1)
            script_frame.pack(fill="x", pady=(0, 5))
            
            if script_name in self.script_paths:
                status_text = "✅"
                path_text = self.script_paths[script_name]
                color = self.current_theme["success"]
            else:
                status_text = "❌"
                path_text = "Non trovato"
                color = self.current_theme["error"]
            
            # Nome script
            name_label = tk.Label(script_frame, text=f"{status_text} {script_name}",
                                font=("Segoe UI", 11, "bold"),
                                fg=color,
                                bg=self.current_theme["card_bg"],
                                anchor="w")
            name_label.pack(fill="x")
            
            # Percorso
            path_label = tk.Label(script_frame, text=f"📁 {path_text}",
                                font=("Segoe UI", 9),
                                fg=self.current_theme["text_medium"],
                                bg=self.current_theme["card_bg"],
                                anchor="w")
            path_label.pack(fill="x", padx=(20, 0))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind scroll del mouse
        def on_mouse_scroll(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<MouseWheel>", on_mouse_scroll)
        
        # Frame pulsanti
        button_frame = tk.Frame(paths_window, bg=self.current_theme["bg_dark"])
        button_frame.pack(side="bottom", fill="x", padx=20, pady=10)
        
        # Pulsante riscan
        rescan_button = tk.Button(button_frame, text="🔄 Riscansiona", 
                                font=("Segoe UI", 11, "bold"),
                                bg=self.current_theme["accent_primary"],
                                fg=self.current_theme["text_dark"],
                                command=lambda: [self.scan_script_paths(), paths_window.destroy(), self.show_script_paths()],
                                relief="flat", padx=20, pady=8)
        rescan_button.pack(side="left")
        
        # Pulsante chiudi
        close_button = tk.Button(button_frame, text="✖️ Chiudi", 
                               font=("Segoe UI", 11, "bold"),
                               bg=self.current_theme["error"],
                               fg=self.current_theme["text_dark"],
                               command=paths_window.destroy,
                               relief="flat", padx=20, pady=8)
        close_button.pack(side="right")

    def toggle_sidebar(self):
        """Mostra/nasconde la sidebar."""
        if self.sidebar_visible:
            self.sidebar_frame.pack_forget()
            self.sidebar_toggle_btn.configure(text="☰")
        else:
            self.sidebar_toggle_btn.configure(text="✕")
            self.sidebar_frame.pack(side="left", fill="y", before=self.main_content_frame)
        
        self.sidebar_visible = not self.sidebar_visible

    def toggle_theme(self):
        """Cambia tra tema chiaro e scuro."""
        if self.current_theme == self.dark_theme:
            self.current_theme = self.light_theme
            message = "🌞 Tema chiaro attivato"
        else:
            self.current_theme = self.dark_theme
            message = "🌙 Tema scuro attivato"
        
        self.refresh_ui()
        self.show_notification(message)

    def refresh_scripts(self):
        """Aggiorna la lista degli script."""
        self.scan_script_paths()
        self.show_all_scripts()
        found_count = len(self.script_paths)
        total_count = len(SCRIPTS)
        self.show_notification(f"🔄 Script aggiornati: {found_count}/{total_count} trovati", 
                             color=self.current_theme["success"])

    def refresh_ui(self):
        """Aggiorna l'interfaccia utente con il nuovo tema."""
        # Ricrea l'interfaccia con il nuovo tema
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.script_cards = []
        self.active_category_buttons = {}
        self.sidebar_visible = False
        
        self.setup_main_window()

    def show_notification(self, message, color=None):
        """Mostra una notifica animata migliorata."""
        if color is None:
            color = self.current_theme["accent_primary"]
                
        notification_frame = tk.Frame(self.root, bg=color, padx=3, pady=3)
        inner_frame = tk.Frame(notification_frame, bg=self.current_theme["bg_medium"], 
                             padx=20, pady=12)
        inner_frame.pack(fill="both", expand=True)
        
        msg_label = tk.Label(inner_frame, text=message, font=("Segoe UI", 11, "bold"), 
                           fg=self.current_theme["text_light"], 
                           bg=self.current_theme["bg_medium"])
        msg_label.pack()
        
        notification_frame.place(relx=0.95, rely=0.05, anchor="ne")
        
        def safe_destroy():
            try:
                if notification_frame.winfo_exists():
                    notification_frame.destroy()
            except:
                pass
        
        self.root.after(3000, safe_destroy)

    def show_help(self):
        """Mostra la finestra di aiuto migliorata."""
        help_window = tk.Toplevel(self.root)
        help_window.title("❓ Aiuto - League of Legends Tool")
        help_window.geometry("700x600")
        help_window.configure(bg=self.current_theme["bg_dark"])
        help_window.resizable(False, False)

        # Centra la finestra
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (350)
        y = (help_window.winfo_screenheight() // 2) - (300)
        help_window.geometry(f'700x600+{x}+{y}')
        
        # Frame principale con scrollbar
        main_frame = tk.Frame(help_window, bg=self.current_theme["bg_dark"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titolo
        title_label = tk.Label(main_frame, 
                            text="📖 Guida Completa", 
                            font=("Segoe UI", 20, "bold"),
                            fg=self.current_theme["accent_primary"],
                            bg=self.current_theme["bg_dark"])
        title_label.pack(pady=(0, 20))
        
        # Canvas per scrolling
        canvas = tk.Canvas(main_frame, bg=self.current_theme["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview,
                                style="Custom.Vertical.TScrollbar")
        scrollable_frame = tk.Frame(canvas, bg=self.current_theme["bg_dark"])
        
        scrollable_frame.bind("<Configure>", 
                            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Sezioni di aiuto
        help_sections = [
            ("🚀 Come Iniziare", 
             "1. Seleziona uno script dalla dashboard principale\n"
             "2. Verifica che sia disponibile (✅)\n"
             "3. Clicca sul pulsante 'Esegui Script'\n"
             "4. Attendi il completamento dell'operazione\n"
             "5. Controlla le notifiche per lo stato di esecuzione"),
            
            ("🗂 Gestione File Script",
             "L'applicazione cerca automaticamente gli script in queste cartelle:\n"
             "• Cartella corrente (.)\n"
             "• scripts/\n"
             "• tools/\n"
             "• src/\n"
             "• Scripts/\n"
             "• Tools/\n"
             "• league_tools/\n"
             "• lol_scripts/\n\n"
             "Usa '🗂 Percorsi Script' per vedere dove sono stati trovati."),
            
            ("📂 Navigazione per Categorie",
             "• Info: Visualizza informazioni su account, shop e statistiche\n"
             "• Partita: Strumenti per le partite (gamemode, champion select, replay)\n"
             "• Amici: Gestione della lista amici e messaggistica\n"
             "• Account: Modifiche al profilo (stato, maestrie, Riot ID)\n"
             "• Utility: Strumenti ausiliari (login, email, convertitore)"),
            
            ("🔍 Ricerca Rapida",
             "Utilizza la barra di ricerca per trovare rapidamente gli script:\n"
             "• Digita il nome dello script\n"
             "• Cerca per funzione (es. 'amici', 'shop', 'rank')\n"
             "• La ricerca è in tempo reale"),
            
            ("⚙️ Funzionalità Principali",
             "🪙 Shop Riot: Visualizza offerte e sconti\n"
             "👤 Info Account: Dati completi del tuo account\n"
             "🎮 GameMode: Selezione modalità e auto-accept\n"
             "🏆 Maestrie: Statistiche di maestria dei campioni\n"
             "💰 Wallet: Gestione valute (RP, BE, ecc.)\n"
             "👥 Amici: Lista e gestione amicizie\n"
             "📊 Ranked Stats: Statistiche competitive\n"
             "🎬 Replay: Gestione replay delle partite"),
            
            ("⚠️ Risoluzione Problemi",
             "Se uno script non funziona:\n"
             "1. Verifica che sia 'Disponibile' (✅) nella card\n"
             "2. Controlla i percorsi con '🗂 Percorsi Script'\n"
             "3. Usa '🔄 Riscansiona' per cercare nuovi script\n"
             "4. Verifica che Python sia installato correttamente\n"
             "5. Assicurati che League of Legends sia in esecuzione\n"
             "6. Controlla le notifiche per messaggi di errore specifici"),
            
            ("📞 Supporto",
             "Per assistenza contatta:\n"
             "🎮 Discord: Ahristogatti\n"
             "🏆 League: TSG Ahristogatti#kiko\n"
             "📧 GitHub: github.com/ahristogatti")
        ]
        
        for title, content in help_sections:
            # Frame per ogni sezione
            section_frame = tk.Frame(scrollable_frame, bg=self.current_theme["card_bg"],
                                   padx=20, pady=15, relief="solid", bd=1)
            section_frame.pack(fill="x", pady=(0, 15))
            
            # Titolo sezione
            section_title = tk.Label(section_frame, text=title, 
                                   font=("Segoe UI", 14, "bold"),
                                   fg=self.current_theme["accent_primary"],
                                   bg=self.current_theme["card_bg"], 
                                   anchor="w")
            section_title.pack(fill="x", pady=(0, 10))
            
            # Contenuto sezione
            section_content = tk.Label(section_frame, text=content,
                                     font=("Segoe UI", 10), 
                                     fg=self.current_theme["text_light"],
                                     bg=self.current_theme["card_bg"], 
                                     wraplength=600, 
                                     justify="left")
            section_content.pack(fill="x")
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind scroll del mouse
        def on_mouse_scroll(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind("<MouseWheel>", on_mouse_scroll)
        
        # Pulsante chiudi
        close_button = tk.Button(help_window, text="✖️ Chiudi", 
                               font=("Segoe UI", 12, "bold"),
                               bg=self.current_theme["error"],
                               fg=self.current_theme["text_dark"],
                               command=help_window.destroy,
                               relief="flat", padx=20, pady=10)
        close_button.pack(side="bottom", pady=10)

def main():
    """Punto di ingresso principale dell'applicazione."""
    root = tk.Tk()
    root.title("⚔️ League of Legends Tool")
    root.geometry("1000x700")
    root.minsize(800, 600)
    
    # Imposta l'icona dell'applicazione se disponibile
    try:
        root.iconbitmap("league_icon.ico")
    except:
        pass  # Ignora se l'icona non esiste
    
    # Crea e avvia l'applicazione
    app = LeagueApp(root)
    
    # Avvia il loop principale
    root.mainloop()

if __name__ == "__main__":
    main()