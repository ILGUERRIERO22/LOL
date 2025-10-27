import os
import requests
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import json
import threading
from PIL import Image, ImageTk
import io
import sys
from pathlib import Path

# Carica il file API.env (supporta anche .emv come estensione alternativa)
try:
    load_dotenv(r"C:\Users\dbait\Desktop\MOD LOL\script\API.emv")
except:
    try:
        load_dotenv(r"C:\Users\dbait\Desktop\MOD LOL\script\API.env")
    except:
        load_dotenv("API.env")  # Fallback per path relativo

# Recupera la chiave API dal file API.env
API_KEY = os.getenv("RIOT_API_KEY")
ACCOUNT_API_URL = "https://europe.api.riotgames.com"
MATCH_API_URL = "https://europe.api.riotgames.com"

# Verifica che la chiave API sia caricata
if not API_KEY:
    print("ERRORE: La chiave API non è stata caricata!")
    print("File cercati:")
    print("1. C:\\Users\\dbait\\Desktop\\MOD LOL\\script\\API.emv")
    print("2. C:\\Users\\dbait\\Desktop\\MOD LOL\\script\\API.env")
    print("3. API.env (directory corrente)")
    print("\nVerifica che:")
    print("- Il file esista in uno dei percorsi sopra")
    print("- Contenga: RIOT_API_KEY=la_tua_chiave_api")
    print("- Non ci siano spazi extra o caratteri speciali")

# Mappa per le modalità di gioco
QUEUE_ID_MAP = {
    420: "Classificata Solo/Duo",
    400: "Normale Draft",
    440: "Classificata Flex",
    450: "ARAM",
    700: "Clash",
    830: "Co-op vs AI - Intro",
    840: "Co-op vs AI - Beginner",
    850: "Co-op vs AI - Intermediate",
    900: "URF",
    1010: "ARAM Ultra Rapid Fire",
    1020: "One for All",
    1300: "Nexus Blitz",
    1400: "Ultimate Spellbook"
}

# Percorsi file
SETTINGS_FILE = "settings.json"
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "cache.json"
ASSETS_DIR = Path("assets")

# Crea le directory se non esistono
CACHE_DIR.mkdir(exist_ok=True)
ASSETS_DIR.mkdir(exist_ok=True)

# Tema moderno con gradiente
THEME = {
    "bg_primary": "#0F1419",      # Nero profondo
    "bg_secondary": "#1E2328",    # Grigio scuro
    "bg_tertiary": "#3C3C41",     # Grigio medio
    "accent_primary": "#C89B3C",  # Oro LoL
    "accent_secondary": "#F0E6D2", # Oro chiaro
    "accent_blue": "#0596AA",     # Blu accento
    "text_primary": "#F0E6D2",    # Testo principale
    "text_secondary": "#A09B8C",  # Testo secondario
    "text_muted": "#5BC0DE",      # Testo muto
    "success": "#00F5FF",         # Verde vittoria
    "error": "#FF6B6B",           # Rosso sconfitta
    "warning": "#F39C12",         # Arancione avviso
    "border": "#463714",          # Bordo oro scuro
    "hover": "#CDBE91"            # Hover oro
}

# Funzioni di utilità per le impostazioni
def load_settings():
    """Carica le impostazioni dal file JSON, se esiste."""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Errore nel caricamento impostazioni: {e}")
    return {}

def save_settings(settings):
    """Salva le impostazioni nel file JSON."""
    try:
        with open(SETTINGS_FILE, "w", encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Errore nel salvataggio impostazioni: {e}")

# Funzioni di utilità per la cache
def load_cache():
    """Carica la cache dal file JSON, se esiste."""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r", encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Errore nel caricamento cache: {e}")
    return {}

def save_cache(cache):
    """Salva la cache nel file JSON."""
    try:
        with open(CACHE_FILE, "w", encoding='utf-8') as f:
            json.dump(cache, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Errore nel salvataggio cache: {e}")

def get_queue_name(queue_id):
    """Restituisce il nome della modalità in base al queueId."""
    return QUEUE_ID_MAP.get(queue_id, f"Modalità Sconosciuta ({queue_id})")

def format_duration(seconds):
    """Converte i secondi in formato minuti:secondi."""
    if not seconds:
        return "0m 0s"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}m {remaining_seconds}s"

def safe_request(url, headers, timeout=10):
    """Effettua una richiesta HTTP con gestione degli errori."""
    try:
        print(f"Tentativo richiesta a: {url}")
        response = requests.get(url, headers=headers, timeout=timeout)
        print(f"Status code: {response.status_code}")
        return response
    except requests.exceptions.Timeout:
        print("Errore: Timeout della richiesta")
        messagebox.showerror("Errore di Connessione", "Timeout: Il server Riot non risponde entro il tempo limite.")
        return None
    except requests.exceptions.ConnectionError as e:
        print(f"Errore di connessione: {e}")
        messagebox.showerror("Errore di Connessione", 
                           "Impossibile connettersi al server Riot Games.\n"
                           "Verifica:\n"
                           "• Connessione internet\n"
                           "• Firewall/antivirus\n"
                           "• Status server Riot")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta: {e}")
        messagebox.showerror("Errore di Rete", f"Errore nella richiesta HTTP: {e}")
        return None

# Funzioni API Riot
def get_puuid_by_riot_id(game_name, tag_line):
    """Ottieni il PUUID tramite Riot ID (gameName + tagLine)."""
    if not API_KEY:
        messagebox.showerror("Errore", "API Key non configurata!")
        return None
        
    url = f"{ACCOUNT_API_URL}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {"X-Riot-Token": API_KEY}
    response = safe_request(url, headers)
    
    if response and response.status_code == 200:
        return response.json()
    else:
        if response:
            if response.status_code == 404:
                error_message = f"Account non trovato: {game_name}#{tag_line}\n\nVerifica che:\n• Il nome utente sia corretto\n• Il tag sia corretto (es: EUW, NA1, KR)\n• L'account esista su League of Legends"
            elif response.status_code == 403:
                error_message = "API Key non valida o scaduta.\nGenera una nuova chiave da:\nhttps://developer.riotgames.com/"
            elif response.status_code == 429:
                error_message = "Troppe richieste. Attendi qualche minuto prima di riprovare."
            else:
                error_message = f"Errore API: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'status' in error_data and 'message' in error_data['status']:
                        error_message += f"\nDettagli: {error_data['status']['message']}"
                except:
                    pass
        else:
            error_message = "Impossibile connettersi al server Riot"
        
        messagebox.showerror("Errore API", error_message)
        return None

def get_match_history_by_puuid(puuid, count=20, start=0):
    """Ottieni la cronologia delle partite usando il PUUID."""
    url = f"{MATCH_API_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?start={start}&count={count}"
    headers = {"X-Riot-Token": API_KEY}
    response = safe_request(url, headers)
    
    if response and response.status_code == 200:
        return response.json()
    else:
        error_code = response.status_code if response else "Connessione fallita"
        messagebox.showerror("Errore", f"Errore nel recupero delle partite: {error_code}")
        return None

def get_match_details(match_id):
    """Ottieni i dettagli di una partita specifica."""
    url = f"{MATCH_API_URL}/lol/match/v5/matches/{match_id}"
    headers = {"X-Riot-Token": API_KEY}
    response = safe_request(url, headers)
    
    if response and response.status_code == 200:
        return response.json()
    else:
        error_code = response.status_code if response else "Connessione fallita"
        print(f"Errore nel recupero dei dettagli della partita {match_id}: {error_code}")
        return None

def get_cached_puuid(game_name, tag_line):
    """Recupera il PUUID dalla cache locale o dall'API se necessario."""
    settings = load_settings()
    key = f"{game_name}#{tag_line}"
    
    if "puuids" in settings and key in settings["puuids"]:
        return settings["puuids"][key]

    account_data = get_puuid_by_riot_id(game_name, tag_line)
    if account_data and "puuid" in account_data:
        puuid = account_data["puuid"]
        if "puuids" not in settings:
            settings["puuids"] = {}
        settings["puuids"][key] = puuid
        save_settings(settings)
        return puuid

    return None

def get_riot_id_by_puuid(puuid):
    """Ottiene il Riot ID usando il PUUID."""
    url = f"{ACCOUNT_API_URL}/riot/account/v1/accounts/by-puuid/{puuid}"
    headers = {"X-Riot-Token": API_KEY}
    response = safe_request(url, headers)
    
    if response and response.status_code == 200:
        account_data = response.json()
        game_name = account_data.get('gameName', 'Sconosciuto')
        tag_line = account_data.get('tagLine', 'Sconosciuto')
        return f"{game_name}#{tag_line}"
    else:
        return "Sconosciuto#NA"

def get_latest_ddragon_version():
    """Ottiene l'ultima versione di DDragon."""
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = safe_request(url, {})

    if response and response.status_code == 200:
        versions = response.json()
        return versions[0] if versions else None
    else:
        print("Impossibile recuperare la versione DDragon")
        return None

def get_champions_from_ddragon():
    """Ottiene la lista dei campioni da DDragon."""
    latest_version = get_latest_ddragon_version()
    if not latest_version:
        return []

    url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/it_IT/champion.json"
    response = safe_request(url, {})

    if response and response.status_code == 200:
        try:
            champion_data = response.json()
            champions = list(champion_data['data'].keys())
            return sorted(champions)
        except Exception as e:
            print(f"Errore nel parsing dei campioni: {e}")
    
    return []

def fetch_champion_icon(champion_name, size=32):
    """Scarica l'icona del campione da DDragon."""
    if not champion_name or champion_name == "Sconosciuto":
        return None
        
    latest_version = get_latest_ddragon_version()
    if not latest_version:
        return None
        
    url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/img/champion/{champion_name}.png"
    response = safe_request(url, {})
    
    if response and response.status_code == 200:
        try:
            img_data = response.content
            img = Image.open(io.BytesIO(img_data))
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Errore nel caricamento dell'icona per {champion_name}: {e}")
    
    return None

# Classe principale dell'applicazione
class LoLMatchHistoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("League of Legends - Cronologia Partite")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.state('zoomed')  # Massimizza la finestra
        
        # Variabili di istanza
        self.champion_icons = {}
        self.match_data = {}
        self.champions_list = []
        self.current_puuid = None
        self.loading = False
        
        # Configura lo stile
        self.setup_styles()
        
        # Carica i campioni in background
        self.load_champions()
        
        # Crea l'interfaccia
        self.create_widgets()
        
        # Carica le impostazioni salvate
        self.load_saved_settings()
        
        # Setup threading
        self.running_threads = []
        
        # Bind eventi
        self.setup_bindings()
    
    def setup_styles(self):
        """Configura gli stili personalizzati moderni."""
        self.style = ttk.Style()
        
        # Configura il tema di base
        self.root.configure(bg=THEME["bg_primary"])
        
        # Style per Frame
        self.style.configure("TFrame", 
                            background=THEME["bg_primary"],
                            borderwidth=0)
        
        self.style.configure("Card.TFrame",
                            background=THEME["bg_secondary"],
                            relief="solid",
                            borderwidth=1,
                            bordercolor=THEME["border"])
        
        # Style per Label
        self.style.configure("TLabel", 
                            background=THEME["bg_primary"], 
                            foreground=THEME["text_primary"], 
                            font=("Segoe UI", 10))
        
        self.style.configure("Title.TLabel",
                            background=THEME["bg_secondary"],
                            foreground=THEME["accent_primary"],
                            font=("Segoe UI", 20, "bold"))
        
        self.style.configure("Subtitle.TLabel",
                            background=THEME["bg_secondary"],
                            foreground=THEME["text_secondary"],
                            font=("Segoe UI", 11))
        
        # Style per Button
        self.style.configure("TButton",
                            background=THEME["bg_tertiary"],
                            foreground=THEME["text_primary"],
                            font=("Segoe UI", 10),
                            borderwidth=0,
                            focuscolor='none',
                            relief="flat")
        
        self.style.map("TButton",
                      background=[("active", THEME["accent_blue"]), 
                                 ("pressed", THEME["accent_primary"]),
                                 ("!disabled", THEME["bg_tertiary"])],
                      foreground=[("active", THEME["text_primary"]),
                                 ("pressed", THEME["bg_primary"]),
                                 ("!disabled", THEME["text_primary"])])
        
        self.style.configure("Accent.TButton",
                            background=THEME["accent_primary"],
                            foreground=THEME["bg_primary"],
                            font=("Segoe UI", 11, "bold"),
                            borderwidth=0)
        
        self.style.map("Accent.TButton",
                      background=[("active", THEME["accent_secondary"]),
                                 ("pressed", THEME["hover"])],
                      foreground=[("active", THEME["bg_primary"]),
                                 ("pressed", THEME["bg_primary"])])
        
        # Style per Entry
        self.style.configure("TEntry",
                            fieldbackground=THEME["bg_tertiary"],
                            foreground=THEME["text_primary"],
                            insertcolor=THEME["text_primary"],
                            selectbackground=THEME["accent_primary"],
                            selectforeground=THEME["bg_primary"],
                            borderwidth=2,
                            bordercolor=THEME["border"],
                            lightcolor=THEME["accent_blue"],
                            darkcolor=THEME["accent_blue"],
                            font=("Segoe UI", 11))
        
        # Forza i colori per gli Entry
        self.root.option_add('*Entry*Background', THEME["bg_tertiary"])
        self.root.option_add('*Entry*Foreground', THEME["text_primary"])
        self.root.option_add('*Entry*InsertBackground', THEME["text_primary"])
        self.root.option_add('*Entry*HighlightBackground', THEME["accent_blue"])
        self.root.option_add('*Entry*HighlightColor', THEME["accent_blue"])
        
        # Style per Treeview
        self.style.configure("Treeview",
                            background=THEME["bg_secondary"],
                            foreground=THEME["text_primary"],
                            rowheight=35,
                            fieldbackground=THEME["bg_secondary"],
                            font=("Segoe UI", 10),
                            borderwidth=0,
                            relief="flat")
        
        self.style.configure("Treeview.Heading",
                            background=THEME["bg_tertiary"],
                            foreground=THEME["accent_primary"],
                            font=("Segoe UI", 11, "bold"),
                            relief="flat",
                            borderwidth=1,
                            bordercolor=THEME["border"])
        
        self.style.map("Treeview.Heading",
                      background=[("active", THEME["accent_blue"])],
                      foreground=[("active", THEME["text_primary"])])
        
        self.style.map("Treeview",
                      background=[("selected", THEME["accent_blue"])],
                      foreground=[("selected", THEME["text_primary"])])
        
        # Forza il tema scuro per tutti gli elementi del Treeview
        self.style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        
        # Configura i colori delle righe alternate
        self.style.configure("Treeview", 
                            background=THEME["bg_secondary"],
                            fieldbackground=THEME["bg_secondary"])
        
        # Rimuovi i bordi e forza il colore di sfondo
        self.root.option_add('*Treeview*Background', THEME["bg_secondary"])
        self.root.option_add('*Treeview*Foreground', THEME["text_primary"])
        self.root.option_add('*Treeview*FieldBackground', THEME["bg_secondary"])
        self.root.option_add('*Treeview*BorderWidth', '0')
        self.root.option_add('*Treeview*HighlightThickness', '0')
        
        # Style per Combobox
        self.style.configure("TCombobox",
                            fieldbackground=THEME["bg_tertiary"],
                            background=THEME["bg_tertiary"],
                            foreground=THEME["text_primary"],
                            arrowcolor=THEME["accent_primary"],
                            bordercolor=THEME["border"],
                            lightcolor=THEME["accent_blue"],
                            darkcolor=THEME["accent_blue"],
                            insertcolor=THEME["text_primary"],
                            selectbackground=THEME["accent_primary"],
                            selectforeground=THEME["bg_primary"],
                            font=("Segoe UI", 10))
        
        self.style.map("TCombobox",
                      fieldbackground=[("readonly", THEME["bg_tertiary"]),
                                     ("focus", THEME["bg_tertiary"])],
                      foreground=[("readonly", THEME["text_primary"]),
                                ("focus", THEME["text_primary"]),
                                ("!disabled", THEME["text_primary"])])
        
        # Configura le opzioni del dropdown
        self.root.option_add('*TCombobox*Listbox.background', THEME["bg_tertiary"])
        self.root.option_add('*TCombobox*Listbox.foreground', THEME["text_primary"])
        self.root.option_add('*TCombobox*Listbox.selectBackground', THEME["accent_primary"])
        self.root.option_add('*TCombobox*Listbox.selectForeground', THEME["bg_primary"])
        
        # Forza i colori anche per i Combobox
        self.root.option_add('*Combobox*Field.Background', THEME["bg_tertiary"])
        self.root.option_add('*Combobox*Field.Foreground', THEME["text_primary"])
        
        # Forza i colori anche per i Button
        self.root.option_add('*Button*Background', THEME["bg_tertiary"])
        self.root.option_add('*Button*Foreground', THEME["text_primary"])
        self.root.option_add('*Button*ActiveBackground', THEME["accent_blue"])
        self.root.option_add('*Button*ActiveForeground', THEME["text_primary"])
        
        # Tags per il Treeview
        self.setup_treeview_tags()
    
    def setup_treeview_tags(self):
        """Configura i tag per colorare le righe del Treeview."""
        # Tag che verranno applicati dopo la creazione del Treeview
        pass
    
    def load_champions(self):
        """Carica la lista dei campioni in background."""
        def load_thread():
            try:
                self.champions_list = get_champions_from_ddragon()
            except Exception as e:
                print(f"Errore nel caricamento campioni: {e}")
                self.champions_list = []
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()
    
    def create_widgets(self):
        """Crea l'interfaccia utente moderna."""
        # Container principale con padding
        main_container = ttk.Frame(self.root, style="TFrame", padding=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Configura il grid
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Header
        self.create_modern_header(main_container)
        
        # Content area
        content_frame = ttk.Frame(main_container, style="TFrame")
        content_frame.grid(row=1, column=0, sticky="nsew", pady=(20, 0))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(1, weight=1)
        
        # Controls panel
        self.create_controls_panel(content_frame)
        
        # Results area
        self.create_results_area(content_frame)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_modern_header(self, parent):
        """Crea un header moderno con gradiente."""
        header_frame = ttk.Frame(parent, style="Card.TFrame", padding=30)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.columnconfigure(1, weight=1)
        
        # Logo placeholder (può essere sostituito con un'immagine)
        logo_frame = tk.Frame(header_frame, bg=THEME["bg_secondary"], width=60, height=60)
        logo_frame.grid(row=0, column=0, rowspan=2, padx=(0, 20), sticky="w")
        logo_frame.grid_propagate(False)
        
        # Crea un logo semplice con testo
        logo_label = tk.Label(logo_frame, text="LoL", 
                             bg=THEME["accent_primary"], 
                             fg=THEME["bg_primary"],
                             font=("Segoe UI", 16, "bold"))
        logo_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Titolo e sottotitolo
        title_label = ttk.Label(header_frame, 
                               text="LEAGUE OF LEGENDS", 
                               style="Title.TLabel")
        title_label.grid(row=0, column=1, sticky="w")
        
        subtitle_label = ttk.Label(header_frame, 
                                  text="Cronologia Partite | Analisi Prestazioni", 
                                  style="Subtitle.TLabel")
        subtitle_label.grid(row=1, column=1, sticky="w")
    
    def create_controls_panel(self, parent):
        """Crea il pannello di controllo migliorato."""
        controls_frame = ttk.Frame(parent, style="Card.TFrame", padding=20)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        # Configura il layout
        controls_frame.columnconfigure(1, weight=1)
        
        # Sezione Riot ID
        riot_section = ttk.Frame(controls_frame, style="TFrame")
        riot_section.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        riot_section.columnconfigure(1, weight=1)
        
        riot_label = ttk.Label(riot_section, text="Riot ID:", 
                              font=("Segoe UI", 12, "bold"))
        riot_label.grid(row=0, column=0, sticky="w", padx=(0, 15))
        
        # Container per i campi Riot ID
        riot_input_frame = ttk.Frame(riot_section, style="TFrame")
        riot_input_frame.grid(row=0, column=1, sticky="ew")
        riot_input_frame.columnconfigure(0, weight=2)
        riot_input_frame.columnconfigure(2, weight=1)
        
        self.entry_game_name = tk.Entry(riot_input_frame, 
                                       font=("Segoe UI", 11),
                                       bg=THEME["bg_tertiary"],
                                       fg=THEME["text_primary"],
                                       insertbackground=THEME["text_primary"],
                                       selectbackground=THEME["accent_primary"],
                                       selectforeground=THEME["bg_primary"],
                                       relief="solid",
                                       bd=1,
                                       highlightthickness=1,
                                       highlightcolor=THEME["accent_blue"],
                                       highlightbackground=THEME["border"])
        self.entry_game_name.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        hash_label = ttk.Label(riot_input_frame, text="#", 
                              font=("Segoe UI", 14, "bold"),
                              foreground=THEME["accent_primary"])
        hash_label.grid(row=0, column=1, padx=8)
        
        self.entry_tag_line = tk.Entry(riot_input_frame, 
                                      font=("Segoe UI", 11),
                                      bg=THEME["bg_tertiary"],
                                      fg=THEME["text_primary"],
                                      insertbackground=THEME["text_primary"],
                                      selectbackground=THEME["accent_primary"],
                                      selectforeground=THEME["bg_primary"],
                                      relief="solid",
                                      bd=1,
                                      highlightthickness=1,
                                      highlightcolor=THEME["accent_blue"],
                                      highlightbackground=THEME["border"])
        self.entry_tag_line.grid(row=0, column=2, sticky="ew", padx=(5, 0))
        
        # Aggiungi una label di aiuto sotto i campi Riot ID
        help_label = ttk.Label(riot_section, 
                              text="Formato: NomeUtente#TAG (es: Player123#EUW1)",
                              font=("Segoe UI", 9),
                              foreground=THEME["text_muted"])
        help_label.grid(row=1, column=1, sticky="w", pady=(2, 0))
        
        # Sezione opzioni
        options_frame = ttk.Frame(controls_frame, style="TFrame")
        options_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 20))
        options_frame.columnconfigure(2, weight=1)
        options_frame.columnconfigure(4, weight=1)
        
        # Numero partite
        matches_label = ttk.Label(options_frame, text="Partite:", 
                                 font=("Segoe UI", 11))
        matches_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        
        self.entry_max_matches = tk.Entry(options_frame, 
                                         font=("Segoe UI", 11),
                                         bg=THEME["bg_tertiary"],
                                         fg=THEME["text_primary"],
                                         insertbackground=THEME["text_primary"],
                                         selectbackground=THEME["accent_primary"],
                                         selectforeground=THEME["bg_primary"],
                                         relief="solid",
                                         bd=1,
                                         highlightthickness=1,
                                         highlightcolor=THEME["accent_blue"],
                                         highlightbackground=THEME["border"],
                                         width=8)
        self.entry_max_matches.insert(0, "20")
        self.entry_max_matches.grid(row=0, column=1, padx=(0, 30))
        
        # Filtro campione
        champ_label = ttk.Label(options_frame, text="Campione:", 
                               font=("Segoe UI", 11))
        champ_label.grid(row=0, column=2, sticky="w", padx=(0, 10))
        
        # Creo un frame per simulare un combobox con colori personalizzati
        self.combo_champion = tk.StringVar()
        self.combo_champion.set("Tutti")
        self.champ_menu = tk.OptionMenu(options_frame, self.combo_champion, "Tutti")
        self.champ_menu.configure(
            bg=THEME["bg_tertiary"],
            fg=THEME["text_primary"],
            activebackground=THEME["accent_blue"],
            activeforeground=THEME["text_primary"],
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            highlightthickness=0,
            width=15
        )
        # Configura anche il menu dropdown
        self.champ_menu['menu'].configure(
            bg=THEME["bg_tertiary"],
            fg=THEME["text_primary"],
            activebackground=THEME["accent_primary"],
            activeforeground=THEME["bg_primary"]
        )
        self.champ_menu.grid(row=0, column=3, padx=(0, 30))
        
        # Filtro modalità
        mode_label = ttk.Label(options_frame, text="Modalità:", 
                              font=("Segoe UI", 11))
        mode_label.grid(row=0, column=4, sticky="w", padx=(0, 10))
        
        self.combo_mode = tk.StringVar()
        self.combo_mode.set("Tutte")
        mode_values = ["Tutte"] + list(QUEUE_ID_MAP.values())
        mode_menu = tk.OptionMenu(options_frame, self.combo_mode, *mode_values)
        mode_menu.configure(
            bg=THEME["bg_tertiary"],
            fg=THEME["text_primary"],
            activebackground=THEME["accent_blue"],
            activeforeground=THEME["text_primary"],
            font=("Segoe UI", 10),
            relief="solid",
            bd=1,
            highlightthickness=0,
            width=18
        )
        # Configura anche il menu dropdown
        mode_menu['menu'].configure(
            bg=THEME["bg_tertiary"],
            fg=THEME["text_primary"],
            activebackground=THEME["accent_primary"],
            activeforeground=THEME["bg_primary"]
        )
        mode_menu.grid(row=0, column=5)
        
        # Bottoni azione con controllo diretto sui colori
        buttons_frame = ttk.Frame(controls_frame, style="TFrame")
        buttons_frame.grid(row=2, column=0, columnspan=3)
        
        self.btn_load_cache = tk.Button(buttons_frame, 
                                        text="Carica Salvate", 
                                        bg=THEME["bg_tertiary"],
                                        fg=THEME["text_primary"],
                                        activebackground=THEME["accent_blue"],
                                        activeforeground=THEME["text_primary"],
                                        font=("Segoe UI", 10),
                                        relief="solid",
                                        bd=1,
                                        highlightthickness=0,
                                        command=self.load_cached_matches,
                                        width=18)
        self.btn_load_cache.grid(row=0, column=0, padx=(0, 10))
        
        self.btn_update_matches = tk.Button(buttons_frame, 
                                            text="Aggiorna", 
                                            bg=THEME["accent_primary"],
                                            fg=THEME["bg_primary"],
                                            activebackground=THEME["accent_secondary"],
                                            activeforeground=THEME["bg_primary"],
                                            font=("Segoe UI", 11, "bold"),
                                            relief="solid",
                                            bd=1,
                                            highlightthickness=0,
                                            command=self.on_fetch_matches,
                                            width=18)
        self.btn_update_matches.grid(row=0, column=1, padx=(0, 10))
        
        self.btn_apply_filter = tk.Button(buttons_frame, 
                                          text="Filtra", 
                                          bg=THEME["bg_tertiary"],
                                          fg=THEME["text_primary"],
                                          activebackground=THEME["accent_blue"],
                                          activeforeground=THEME["text_primary"],
                                          font=("Segoe UI", 10),
                                          relief="solid",
                                          bd=1,
                                          highlightthickness=0,
                                          command=self.apply_filter,
                                          width=18)
        self.btn_apply_filter.grid(row=0, column=2)
    
    def create_results_area(self, parent):
        """Crea l'area dei risultati migliorata."""
        results_frame = ttk.Frame(parent, style="Card.TFrame", padding=15)
        results_frame.grid(row=1, column=0, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Header risultati
        results_header = ttk.Label(results_frame, 
                                  text="Cronologia Partite", 
                                  font=("Segoe UI", 14, "bold"),
                                  foreground=THEME["accent_primary"])
        results_header.grid(row=0, column=0, sticky="w", pady=(0, 15))
        
        # Frame per la tabella
        table_frame = ttk.Frame(results_frame, style="TFrame")
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        
        # Tabella risultati
        columns = ("data", "modalita", "campione", "score", "durata", "risultato")
        self.results_table = ttk.Treeview(table_frame, 
                                         columns=columns, 
                                         show="headings", 
                                         height=12,
                                         selectmode="browse")
        
        # Configura le colonne
        self.results_table.heading("data", text="Data e Ora")
        self.results_table.heading("modalita", text="Modalità")
        self.results_table.heading("campione", text="Campione")
        self.results_table.heading("score", text="K/D/A")
        self.results_table.heading("durata", text="Durata")
        self.results_table.heading("risultato", text="Risultato")
        
        self.results_table.column("data", anchor="center", width=150, minwidth=120)
        self.results_table.column("modalita", anchor="center", width=180, minwidth=150)
        self.results_table.column("campione", anchor="center", width=150, minwidth=120)
        self.results_table.column("score", anchor="center", width=100, minwidth=80)
        self.results_table.column("durata", anchor="center", width=100, minwidth=80)
        self.results_table.column("risultato", anchor="center", width=120, minwidth=100)
        
        # Scrollbar
        scrollbar_v = ttk.Scrollbar(table_frame, orient="vertical", 
                                   command=self.results_table.yview)
        scrollbar_h = ttk.Scrollbar(table_frame, orient="horizontal", 
                                   command=self.results_table.xview)
        
        self.results_table.configure(yscrollcommand=scrollbar_v.set,
                                    xscrollcommand=scrollbar_h.set)
        
        # Posiziona gli elementi
        self.results_table.grid(row=0, column=0, sticky="nsew")
        scrollbar_v.grid(row=0, column=1, sticky="ns")
        scrollbar_h.grid(row=1, column=0, sticky="ew")
        
        # Configura i tag per le righe
        self.results_table.tag_configure("vittoria", 
                                        background=self.blend_colors(THEME["bg_secondary"], THEME["success"], 0.15))
        self.results_table.tag_configure("sconfitta", 
                                        background=self.blend_colors(THEME["bg_secondary"], THEME["error"], 0.15))
        
        # Bind eventi
        self.results_table.bind("<Double-1>", self.on_match_double_click)
        self.results_table.bind("<Button-3>", self.show_context_menu)  # Click destro
    
    def create_status_bar(self, parent):
        """Crea una status bar moderna."""
        status_frame = ttk.Frame(parent, style="TFrame")
        status_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        status_frame.columnconfigure(0, weight=1)
        
        # Linea separatore
        separator = tk.Frame(status_frame, height=1, bg=THEME["border"])
        separator.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.status_bar = ttk.Label(status_frame, 
                                   text="Pronto", 
                                   foreground=THEME["text_secondary"],
                                   font=("Segoe UI", 10),
                                   anchor="w")
        self.status_bar.grid(row=1, column=0, sticky="ew")
    
    def setup_bindings(self):
        """Configura gli eventi della tastiera."""
        self.root.bind('<Return>', lambda e: self.on_fetch_matches())
        self.root.bind('<F5>', lambda e: self.on_fetch_matches())
        self.root.bind('<Control-r>', lambda e: self.load_cached_matches())
    
    def load_saved_settings(self):
        """Carica le impostazioni salvate."""
        settings = load_settings()
        
        # Carica Riot ID salvato
        game_name = settings.get("last_riot_id", "")
        tag_line = settings.get("last_tag_line", "")
        
        if game_name:
            self.entry_game_name.insert(0, game_name)
        if tag_line:
            self.entry_tag_line.insert(0, tag_line)
        
        # Carica i campioni nel menu quando disponibili
        def update_champions():
            if self.champions_list and hasattr(self, 'champ_menu'):
                # Cancella il menu esistente e ricostruiscilo
                self.champ_menu['menu'].delete(0, 'end')
                for champion in ["Tutti"] + self.champions_list:
                    self.champ_menu['menu'].add_command(label=champion, 
                                                  command=lambda value=champion: self.combo_champion.set(value))
            else:
                self.root.after(1000, update_champions)
        
        self.root.after(500, update_champions)
        
        # Auto-carica se ci sono dati salvati
        if game_name and tag_line:
            self.root.after(1000, self.load_cached_matches)
    
    def set_status(self, message, status_type="info"):
        """Aggiorna la status bar con icone colorate."""
        icons = {
            "info": "",
            "success": "",
            "warning": "",
            "error": "",
            "loading": ""
        }
        
        icon = icons.get(status_type, "")
        self.status_bar.configure(text=f"{icon} {message}")
        
        # Auto-reset dopo 10 secondi per messaggi di successo/info
        if status_type in ["success", "info"]:
            self.root.after(10000, lambda: self.set_status("Pronto", "success"))
    
    def load_cached_matches(self):
        """Carica le partite dalla cache con feedback migliorato."""
        self.set_status("Caricamento dalla cache...", "loading")
        
        game_name = self.entry_game_name.get().strip()
        tag_line = self.entry_tag_line.get().strip()
        
        if not game_name:
            messagebox.showwarning("Attenzione", 
                                 "Inserisci il nome utente per caricare le partite!")
            self.set_status("Nome utente richiesto", "warning")
            return
        
        # Pulisci la tabella
        for item in self.results_table.get_children():
            self.results_table.delete(item)
        
        cache = load_cache()
        cache_key = f"{game_name}#{tag_line}" if tag_line else game_name
        
        if cache_key in cache:
            cached_matches = cache[cache_key]
            
            # Ordina per data
            try:
                cached_matches.sort(key=lambda m: m['info']['gameStartTimestamp'], reverse=True)
            except Exception as e:
                print(f"Errore nell'ordinamento: {e}")
            
            # Ottieni PUUID
            puuid = get_cached_puuid(game_name, tag_line) if tag_line else None
            if not puuid and cached_matches:
                # Fallback: prova a estrarre il PUUID dalla prima partita
                try:
                    puuid = cached_matches[0]['metadata']['participants'][0]
                except:
                    pass
            
            self.current_puuid = puuid
            self.match_data = {}
            
            loaded_count = 0
            for idx, match_details in enumerate(cached_matches):
                if self.add_match_to_table(match_details, idx):
                    loaded_count += 1
            
            self.set_status(f"Caricate {loaded_count} partite dalla cache", "success")
        else:
            self.set_status("Nessuna partita trovata nella cache", "warning")
            messagebox.showinfo("Informazione", 
                              "Non ci sono partite salvate per questo account.")
    
    def add_match_to_table(self, match_details, idx):
        """Aggiunge una partita alla tabella con gestione errori migliorata."""
        try:
            if not match_details or 'info' not in match_details:
                return False
            
            # Info partita
            match_id = match_details['metadata']['matchId']
            queue_id = match_details['info']['queueId']
            queue_name = get_queue_name(queue_id)
            game_duration = format_duration(match_details['info'].get('gameDuration', 0))
            game_start = match_details['info'].get('gameStartTimestamp', 0)
            
            if game_start:
                game_date = datetime.fromtimestamp(game_start / 1000).strftime("%d/%m %H:%M")
            else:
                game_date = "Data sconosciuta"
            
            # Trova il giocatore
            participants = match_details['info'].get('participants', [])
            player_data = None
            
            if self.current_puuid:
                player_data = next((p for p in participants if p.get('puuid') == self.current_puuid), None)
            
            if not player_data and participants:
                # Fallback: prendi il primo giocatore
                player_data = participants[0]
            
            if not player_data:
                return False
            
            # Dati giocatore
            champion_name = player_data.get('championName', 'Sconosciuto')
            kills = player_data.get('kills', 0)
            deaths = player_data.get('deaths', 0)
            assists = player_data.get('assists', 0)
            win = player_data.get('win', False)
            result = "Vittoria" if win else "Sconfitta"
            
            # Memorizza i dati
            self.match_data[str(idx)] = {
                'match_id': match_id,
                'match_details': match_details,
                'player_data': player_data
            }
            
            # Inserisci nella tabella
            item_id = self.results_table.insert("", "end",
                                               values=(game_date, queue_name, champion_name,
                                                      f"{kills}/{deaths}/{assists}", game_duration, result),
                                               tags=("vittoria" if win else "sconfitta",))
            
            self.match_data[str(idx)]['item_id'] = item_id
            return True
            
        except Exception as e:
            print(f"Errore nell'aggiunta della partita {idx}: {e}")
            return False
    
    def on_fetch_matches(self):
        """Avvia il fetch delle partite con validazione migliorata."""
        if self.loading:
            messagebox.showinfo("Info", "Caricamento già in corso...")
            return
        
        game_name = self.entry_game_name.get().strip()
        tag_line = self.entry_tag_line.get().strip()
        
        if not game_name:
            messagebox.showwarning("Attenzione", 
                                 "Inserisci il nome utente!")
            self.entry_game_name.focus()
            return
        
        if not tag_line:
            messagebox.showwarning("Attenzione", 
                                 "Inserisci il tag (es: EUW1)!")
            self.entry_tag_line.focus()
            return
        
        try:
            max_matches = int(self.entry_max_matches.get().strip())
            if max_matches < 1 or max_matches > 100:
                raise ValueError()
        except ValueError:
            messagebox.showwarning("Attenzione", 
                                 "Inserisci un numero valido di partite (1-100)!")
            self.entry_max_matches.focus()
            return
        
        # Disabilita i controlli
        self.toggle_controls(False)
        self.loading = True
        
        # Avvia il thread
        fetch_thread = threading.Thread(
            target=self.fetch_matches_thread,
            args=(game_name, tag_line, max_matches),
            daemon=True
        )
        fetch_thread.start()
    
    def fetch_matches_thread(self, game_name, tag_line, max_matches):
        """Thread per il fetch delle partite con gestione errori completa."""
        try:
            # Salva le impostazioni
            settings = load_settings()
            settings["last_riot_id"] = game_name
            settings["last_tag_line"] = tag_line
            save_settings(settings)
            
            # Step 1: Recupera PUUID
            self.root.after(0, lambda: self.set_status("Connessione all'account...", "loading"))
            account_data = get_puuid_by_riot_id(game_name, tag_line)
            
            if not account_data:
                self.root.after(0, lambda: self.set_status("Errore nel recupero account", "error"))
                return
            
            puuid = account_data["puuid"]
            self.current_puuid = puuid
            
            # Step 2: Recupera lista partite
            self.root.after(0, lambda: self.set_status("Recupero lista partite...", "loading"))
            matches = get_match_history_by_puuid(puuid, count=max_matches)
            
            if not matches:
                self.root.after(0, lambda: self.set_status("Nessuna partita trovata", "warning"))
                return
            
            # Step 3: Carica cache esistente
            cache = load_cache()
            cache_key = f"{game_name}#{tag_line}"
            
            if cache_key not in cache:
                cache[cache_key] = []
            
            # Trova partite nuove
            cached_ids = {m['metadata']['matchId'] for m in cache[cache_key] if 'metadata' in m}
            new_matches = [mid for mid in matches if mid not in cached_ids]
            
            if not new_matches:
                self.root.after(0, lambda: [
                    self.set_status("Nessuna nuova partita", "info"),
                    self.load_cached_matches()
                ])
                return
            
            # Step 4: Scarica dettagli nuove partite
            total_new = len(new_matches)
            new_details = []
            
            for i, match_id in enumerate(new_matches):
                progress = f"Scaricando partita {i+1}/{total_new}..."
                self.root.after(0, lambda p=progress: self.set_status(p, "loading"))
                
                details = get_match_details(match_id)
                if details:
                    new_details.append(details)
                    cache[cache_key].append(details)
            
            # Step 5: Ordina e salva
            try:
                cache[cache_key].sort(key=lambda m: m['info']['gameStartTimestamp'], reverse=True)
            except:
                pass
            
            save_cache(cache)
            
            # Step 6: Aggiorna interfaccia
            self.root.after(0, lambda: [
                self.load_cached_matches(),
                self.set_status(f"Aggiunte {len(new_details)} nuove partite", "success")
            ])
            
        except Exception as e:
            error_msg = f"Errore durante il caricamento: {str(e)}"
            self.root.after(0, lambda: [
                self.set_status("Errore nel caricamento", "error"),
                print(error_msg)
            ])
        finally:
            self.root.after(0, lambda: [
                setattr(self, 'loading', False),
                self.toggle_controls(True)
            ])
    
    def toggle_controls(self, enabled):
        """Abilita/disabilita i controlli durante il caricamento."""
        state = "normal" if enabled else "disabled"
        
        self.btn_update_matches.configure(state=state)
        self.btn_load_cache.configure(state=state)
        self.btn_apply_filter.configure(state=state)
        
        self.entry_game_name.configure(state=state)
        self.entry_tag_line.configure(state=state)
        self.entry_max_matches.configure(state=state)
    
    def apply_filter(self):
        """Applica i filtri con logica migliorata."""
        champion_filter = self.combo_champion.get()
        mode_filter = self.combo_mode.get()
        
        # Nascondi tutte le righe
        all_items = self.results_table.get_children()
        for item in all_items:
            self.results_table.detach(item)
        
        # Riapplica le righe filtrate
        shown_count = 0
        for match_data in self.match_data.values():
            if self.match_passes_filter(match_data, champion_filter, mode_filter):
                item_id = match_data.get('item_id')
                if item_id:
                    self.results_table.reattach(item_id, "", "end")
                    shown_count += 1
        
        self.set_status(f"Filtro applicato: {shown_count} partite mostrate", "info")
    
    def match_passes_filter(self, match_data, champion_filter, mode_filter):
        """Verifica se una partita passa i filtri."""
        try:
            match_details = match_data.get('match_details')
            if not match_details:
                return False
            
            # Filtro modalità
            if mode_filter != "Tutte":
                queue_name = get_queue_name(match_details['info']['queueId'])
                if queue_name != mode_filter:
                    return False
            
            # Filtro campione
            if champion_filter != "Tutti":
                player_data = match_data.get('player_data')
                if not player_data:
                    return False
                
                champion_name = player_data.get('championName', '')
                if champion_name != champion_filter:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Errore nel filtro: {e}")
            return False
    
    def show_context_menu(self, event):
        """Mostra menu contestuale su click destro."""
        item = self.results_table.selection()
        if not item:
            return
        
        context_menu = tk.Menu(self.root, tearoff=0, 
                              bg=THEME["bg_tertiary"], 
                              fg=THEME["text_primary"],
                              activebackground=THEME["accent_primary"],
                              activeforeground=THEME["bg_primary"])
        
        context_menu.add_command(label="Mostra Dettagli", 
                                command=lambda: self.on_match_double_click(event))
        context_menu.add_separator()
        context_menu.add_command(label="Copia Match ID", 
                                command=lambda: self.copy_match_id(item[0]))
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def copy_match_id(self, item_id):
        """Copia il Match ID negli appunti."""
        for match_data in self.match_data.values():
            if match_data.get('item_id') == item_id:
                match_id = match_data.get('match_id', '')
                self.root.clipboard_clear()
                self.root.clipboard_append(match_id)
                self.set_status(f"Match ID copiato: {match_id}", "success")
                break
    
    def on_match_double_click(self, event):
        """Gestisce il doppio click con feedback migliorato."""
        selected_item = self.results_table.selection()
        if not selected_item:
            return
        
        # Trova i dati della partita
        match_data = None
        for data in self.match_data.values():
            if data.get('item_id') == selected_item[0]:
                match_data = data
                break
        
        if not match_data or 'match_details' not in match_data:
            messagebox.showerror("Errore", 
                               "Impossibile recuperare i dettagli della partita.")
            return
        
        self.show_match_details(match_data['match_details'])
    
    def show_match_details(self, match_details):
        """Mostra una finestra dettagli moderna e completa."""
        if 'info' not in match_details or 'participants' not in match_details['info']:
            messagebox.showerror("Errore", "Dati della partita non validi.")
            return
        
        # Calcola le informazioni generali
        info = match_details['info']
        game_duration = format_duration(info.get('gameDuration', 0))
        game_start = info.get('gameStartTimestamp', 0)
        game_date = datetime.fromtimestamp(game_start / 1000).strftime("%d/%m/%Y %H:%M") if game_start else "Data sconosciuta"
        queue_name = get_queue_name(info.get('queueId', 0))
        
        # Crea finestra dettagli
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Dettagli Partita - {queue_name}")
        detail_window.geometry("1000x700")
        detail_window.minsize(900, 600)
        detail_window.configure(bg=THEME["bg_primary"])
        detail_window.transient(self.root)
        detail_window.grab_set()
        
        # Container principale
        main_frame = tk.Frame(detail_window, bg=THEME["bg_primary"])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header informazioni partita
        self.create_match_header(main_frame, queue_name, game_date, game_duration)
        
        # Area squadre
        self.create_teams_area(main_frame, match_details)
        
        # Bottone chiudi
        close_btn = tk.Button(main_frame, 
                             text="Chiudi", 
                             bg=THEME["accent_primary"],
                             fg=THEME["bg_primary"],
                             font=("Segoe UI", 11, "bold"),
                             relief="flat",
                             padx=20,
                             pady=8,
                             command=detail_window.destroy)
        close_btn.pack(pady=(20, 0))
    
    def create_match_header(self, parent, queue_name, game_date, game_duration):
        """Crea l'header della finestra dettagli."""
        header_frame = tk.Frame(parent, bg=THEME["bg_secondary"], relief="solid", bd=1)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Padding interno
        header_content = tk.Frame(header_frame, bg=THEME["bg_secondary"])
        header_content.pack(fill=tk.X, padx=20, pady=15)
        
        # Titolo principale
        title_label = tk.Label(header_content, 
                              text=f"{queue_name}", 
                              bg=THEME["bg_secondary"],
                              fg=THEME["accent_primary"],
                              font=("Segoe UI", 16, "bold"))
        title_label.pack(pady=(0, 5))
        
        # Informazioni secondarie
        info_label = tk.Label(header_content, 
                             text=f"{game_date}  •  {game_duration}", 
                             bg=THEME["bg_secondary"],
                             fg=THEME["text_secondary"],
                             font=("Segoe UI", 11))
        info_label.pack()
    
    def create_teams_area(self, parent, match_details):
        """Crea l'area delle squadre con layout migliorato."""
        participants = match_details['info']['participants']
        team100 = [p for p in participants if p['teamId'] == 100]
        team200 = [p for p in participants if p['teamId'] == 200]
        
        # Container squadre
        teams_container = tk.Frame(parent, bg=THEME["bg_primary"])
        teams_container.pack(fill=tk.BOTH, expand=True)
        teams_container.columnconfigure(0, weight=1)
        teams_container.columnconfigure(1, weight=1)
        
        # Squadra blu
        self.create_team_panel(teams_container, team100, "SQUADRA BLU", THEME["accent_blue"], 0)
        
        # Squadra rossa  
        self.create_team_panel(teams_container, team200, "SQUADRA ROSSA", THEME["error"], 1)
    
    def create_team_panel(self, parent, team_data, team_name, team_color, column):
        """Crea il pannello di una squadra."""
        # Frame principale squadra
        team_frame = tk.Frame(parent, bg=THEME["bg_secondary"], relief="solid", bd=1)
        team_frame.grid(row=0, column=column, sticky="nsew", padx=(0, 10) if column == 0 else (10, 0))
        
        # Header squadra
        team_header = tk.Frame(team_frame, bg=team_color, height=40)
        team_header.pack(fill=tk.X)
        team_header.pack_propagate(False)
        
        # Nome squadra
        name_label = tk.Label(team_header, 
                             text=team_name,
                             bg=team_color,
                             fg="white",
                             font=("Segoe UI", 12, "bold"))
        name_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Risultato squadra
        if team_data:
            result = "VITTORIA" if team_data[0].get('win', False) else "SCONFITTA"
            result_color = THEME["success"] if team_data[0].get('win', False) else THEME["error"]
            
            result_label = tk.Label(team_header, 
                                   text=result,
                                   bg=team_color,
                                   fg="white",
                                   font=("Segoe UI", 12, "bold"))
            result_label.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Tabella giocatori
        self.create_players_table(team_frame, team_data)
    
    def create_players_table(self, parent, players):
        """Crea la tabella dei giocatori."""
        # Frame per la tabella
        table_frame = tk.Frame(parent, bg=THEME["bg_secondary"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Headers
        headers = ["Campione", "Giocatore", "K/D/A", "Danno"]
        for i, header in enumerate(headers):
            header_label = tk.Label(table_frame, 
                                   text=header,
                                   bg=THEME["bg_tertiary"],
                                   fg=THEME["accent_primary"],
                                   font=("Segoe UI", 10, "bold"),
                                   relief="solid",
                                   bd=1)
            header_label.grid(row=0, column=i, sticky="ew", padx=1, pady=1)
        
        # Configura colonne
        for i in range(4):
            table_frame.columnconfigure(i, weight=1)
        
        # Dati giocatori
        for i, player in enumerate(players):
            row = i + 1
            
            # Dati giocatore
            champion = player.get('championName', 'N/A')
            summoner = get_riot_id_by_puuid(player.get('puuid', ''))
            kills = player.get('kills', 0)
            deaths = player.get('deaths', 0)
            assists = player.get('assists', 0)
            damage = player.get('totalDamageDealtToChampions', 0)
            
            # Evidenzia il giocatore corrente
            bg_color = THEME["bg_tertiary"] if player.get('puuid') == self.current_puuid else THEME["bg_secondary"]
            
            # Celle
            cells_data = [champion, summoner, f"{kills}/{deaths}/{assists}", f"{damage:,}"]
            
            for j, cell_data in enumerate(cells_data):
                cell_label = tk.Label(table_frame,
                                     text=str(cell_data),
                                     bg=bg_color,
                                     fg=THEME["text_primary"],
                                     font=("Segoe UI", 9),
                                     relief="solid",
                                     bd=1)
                cell_label.grid(row=row, column=j, sticky="ew", padx=1, pady=1)
    
    def blend_colors(self, color1, color2, factor):
        """Miscela due colori esadecimali."""
        try:
            # Rimuovi #
            color1 = color1.lstrip('#')
            color2 = color2.lstrip('#')
            
            # Converti in RGB
            r1, g1, b1 = int(color1[0:2], 16), int(color1[2:4], 16), int(color1[4:6], 16)
            r2, g2, b2 = int(color2[0:2], 16), int(color2[2:4], 16), int(color2[4:6], 16)
            
            # Miscela
            r = int(r1 + (r2 - r1) * factor)
            g = int(g1 + (g2 - g1) * factor)
            b = int(b1 + (b2 - b1) * factor)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return color1

# Avvio dell'applicazione
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = LoLMatchHistoryApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Errore critico nell'avvio: {e}")
        messagebox.showerror("Errore Critico", f"Impossibile avviare l'applicazione:\n{e}")