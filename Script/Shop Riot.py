import json
import requests
import base64
import re
import tkinter as tk
from tkinter import ttk, messagebox, font
from urllib3.exceptions import InsecureRequestWarning
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import threading
import os
from io import BytesIO
import webbrowser
from datetime import datetime

# Disabilita gli avvisi di certificato
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Percorso del lockfile
lockfile_path = r"C:\Riot Games\League of Legends\lockfile"

# Schema colori migliorato - palette ispirata a League of Legends
class Colors:
    # Colori primari
    DARK_BG = "#0A1428"           # Blu scuro profondo
    DARK_SECONDARY = "#091428"    # Blu ancora più scuro
    CARD_BG = "#1E2328"          # Grigio scuro per card
    
    # Colori accent
    GOLD = "#C8AA6E"             # Oro principale LoL
    GOLD_DARK = "#785A28"        # Oro scuro
    GOLD_LIGHT = "#E7C767"       # Oro chiaro
    GOLD_BRIGHT = "#F0E6D2"      # Oro molto chiaro
    
    # Colori testo
    TEXT_PRIMARY = "#F0E6D2"     # Beige chiaro
    TEXT_SECONDARY = "#A09B8C"   # Beige scuro
    TEXT_MUTED = "#5BC0DE"       # Azzurro per info
    
    # Colori stato
    SUCCESS = "#0AC8B9"          # Verde acqua
    WARNING = "#F0AD4E"          # Arancione
    DANGER = "#C9302C"           # Rosso
    INFO = "#5BC0DE"             # Azzurro
    
    # Colori interazione
    HOVER = "#463714"            # Hover oro scuro
    ACTIVE = "#2C1810"           # Active ancora più scuro
    BORDER = "#463714"           # Bordi
    SELECTED = "#C8AA6E"         # Selezione

class ModernTooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event):
        if self.tooltip:
            return
        
        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Stile moderno per tooltip
        frame = tk.Frame(self.tooltip, 
                        background=Colors.CARD_BG, 
                        relief="solid", 
                        borderwidth=1,
                        highlightbackground=Colors.GOLD)
        frame.pack()
        
        label = tk.Label(frame, 
                        text=self.text,
                        background=Colors.CARD_BG,
                        foreground=Colors.TEXT_PRIMARY,
                        font=("Segoe UI", 9),
                        padx=8,
                        pady=4)
        label.pack()
    
    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class LolShopApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configurazione finestra principale
        self.title("League of Legends - Monitor Offerte Negozio")
        self.geometry("1400x800")
        self.configure(bg=Colors.DARK_BG)
        self.minsize(1200, 700)
        
        # Centra la finestra
        self.center_window()
        
        # Variabili di stato
        self._temp_data = {}
        self.loading_animation_id = None
        self.data_loaded = False
        
        # Configurazione
        self.setup_fonts()
        self.setup_styles()
        self.create_widgets()
        
        # Event bindings
        self.bind("<<DataLoaded>>", self._on_data_loaded)
        self.bind("<<HideLoading>>", self._on_hide_loading)
        
        # Avvia caricamento dati
        self.show_loading()
        threading.Thread(target=self.load_data, daemon=True).start()
    
    def center_window(self):
        """Centra la finestra sullo schermo"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        pos_x = (self.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")
    
    def setup_fonts(self):
        """Configura i font personalizzati"""
        self.fonts = {
            'title': font.Font(family="Segoe UI", size=24, weight="bold"),
            'subtitle': font.Font(family="Segoe UI", size=12),
            'heading': font.Font(family="Segoe UI", size=14, weight="bold"),
            'body': font.Font(family="Segoe UI", size=10),
            'button': font.Font(family="Segoe UI", size=10, weight="bold"),
            'small': font.Font(family="Segoe UI", size=9)
        }
    
    def setup_styles(self):
        """Configura stili avanzati per ttk"""
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Configurazioni globali
        style.configure(".", background=Colors.DARK_BG, foreground=Colors.TEXT_PRIMARY)
        
        # Treeview moderno
        style.configure(
            "Modern.Treeview",
            background=Colors.CARD_BG,
            foreground=Colors.TEXT_PRIMARY,
            rowheight=40,
            fieldbackground=Colors.CARD_BG,
            borderwidth=0,
            font=self.fonts['body'],
            selectbackground=Colors.GOLD,
            selectforeground=Colors.DARK_BG
        )
        
        style.configure(
            "Modern.Treeview.Heading",
            background=Colors.DARK_SECONDARY,
            foreground=Colors.GOLD,
            font=self.fonts['heading'],
            borderwidth=0,
            relief="flat",
            padding=(10, 8)
        )
        
        style.map(
            "Modern.Treeview",
            background=[("selected", Colors.GOLD)],
            foreground=[("selected", Colors.DARK_BG)]
        )
        
        style.map(
            "Modern.Treeview.Heading",
            background=[("active", Colors.HOVER)],
            foreground=[("active", Colors.GOLD_LIGHT)]
        )
        
        # Bottoni moderni
        style.configure(
            "Modern.TButton",
            font=self.fonts['button'],
            background=Colors.GOLD,
            foreground=Colors.DARK_BG,
            borderwidth=0,
            focusthickness=0,
            padding=(16, 10),
            relief="flat"
        )
        
        style.map(
            "Modern.TButton",
            background=[("active", Colors.GOLD_LIGHT), ("pressed", Colors.GOLD_DARK)],
            foreground=[("pressed", Colors.TEXT_PRIMARY)]
        )
        
        # Bottoni secondari
        style.configure(
            "Secondary.TButton",
            font=self.fonts['body'],
            background=Colors.CARD_BG,
            foreground=Colors.TEXT_PRIMARY,
            borderwidth=1,
            bordercolor=Colors.BORDER,
            focusthickness=0,
            padding=(12, 8),
            relief="flat"
        )
        
        style.map(
            "Secondary.TButton",
            background=[("active", Colors.HOVER), ("pressed", Colors.ACTIVE)],
            foreground=[("pressed", Colors.GOLD)]
        )
        
        # Bottone pericolo
        style.configure(
            "Danger.TButton",
            font=self.fonts['body'],
            background=Colors.CARD_BG,
            foreground=Colors.DANGER,
            borderwidth=1,
            bordercolor=Colors.DANGER,
            focusthickness=0,
            padding=(12, 8),
            relief="flat"
        )
        
        style.map(
            "Danger.TButton",
            background=[("active", Colors.DANGER), ("pressed", Colors.DARK_BG)],
            foreground=[("active", Colors.TEXT_PRIMARY), ("pressed", Colors.TEXT_PRIMARY)]
        )
        
        # Combobox moderna
        style.configure(
            "Modern.TCombobox",
            fieldbackground=Colors.CARD_BG,
            background=Colors.CARD_BG,
            foreground=Colors.TEXT_PRIMARY,
            borderwidth=1,
            bordercolor=Colors.BORDER,
            selectbackground=Colors.GOLD,
            selectforeground=Colors.DARK_BG,
            padding=(8, 6)
        )
        
        # Scrollbar moderna
        style.configure(
            "Modern.Vertical.TScrollbar",
            gripcount=0,
            background=Colors.CARD_BG,
            darkcolor=Colors.DARK_BG,
            lightcolor=Colors.CARD_BG,
            troughcolor=Colors.DARK_BG,
            bordercolor=Colors.DARK_BG,
            arrowcolor=Colors.GOLD,
            arrowsize=16
        )
        
        # Frame
        style.configure("Card.TFrame", 
                       background=Colors.CARD_BG,
                       borderwidth=1,
                       relief="solid",
                       bordercolor=Colors.BORDER)
        
        style.configure("Main.TFrame", background=Colors.DARK_BG)
        
        # Label
        style.configure("Title.TLabel", 
                       background=Colors.DARK_BG, 
                       foreground=Colors.GOLD,
                       font=self.fonts['title'])
        
        style.configure("Subtitle.TLabel", 
                       background=Colors.DARK_BG, 
                       foreground=Colors.TEXT_SECONDARY,
                       font=self.fonts['subtitle'])
        
        style.configure("Info.TLabel", 
                       background=Colors.CARD_BG, 
                       foreground=Colors.INFO,
                       font=self.fonts['small'])
        
        style.configure("Success.TLabel", 
                       background=Colors.CARD_BG, 
                       foreground=Colors.SUCCESS,
                       font=self.fonts['small'])
        
        style.configure("Body.TLabel", 
                       background=Colors.DARK_BG, 
                       foreground=Colors.TEXT_PRIMARY,
                       font=self.fonts['body'])
        
        # Separator
        style.configure("Modern.TSeparator",
                       background=Colors.GOLD)

    def create_widgets(self):
        """Crea l'interfaccia utente migliorata"""
        # Container principale
        self.main_frame = ttk.Frame(self, style="Main.TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header elegante
        self.create_header()
        
        # Toolbar con filtri e controlli
        self.create_toolbar()
        
        # Area principale con treeview
        self.create_main_area()
        
        # Status bar
        self.create_status_bar()
        
        # Footer con pulsanti
        self.create_footer()
    
    def create_header(self):
        """Crea header moderno"""
        self.header_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Contenitore sinistro (logo + testi)
        left_container = ttk.Frame(self.header_frame, style="Main.TFrame")
        left_container.pack(side=tk.LEFT, fill=tk.Y)
        
        # Titolo principale
        title_label = ttk.Label(
            left_container,
            text="LEAGUE OF LEGENDS",
            style="Title.TLabel"
        )
        title_label.pack(anchor=tk.W)
        
        # Sottotitolo
        subtitle_label = ttk.Label(
            left_container,
            text="Monitor Offerte del Negozio • Skin e Campioni in Saldo",
            style="Subtitle.TLabel"
        )
        subtitle_label.pack(anchor=tk.W, pady=(2, 0))
        
        # Container destro (informazioni)
        right_container = ttk.Frame(self.header_frame, style="Card.TFrame")
        right_container.pack(side=tk.RIGHT, padx=(20, 0), pady=10)
        
        # Versione
        self.version_label = ttk.Label(
            right_container,
            text="Caricamento versione...",
            style="Info.TLabel"
        )
        self.version_label.pack(padx=15, pady=(8, 4))
        
        # Ultimo aggiornamento
        self.update_time_label = ttk.Label(
            right_container,
            text="",
            style="Info.TLabel"
        )
        self.update_time_label.pack(padx=15, pady=(0, 8))
        
        # Separatore elegante
        separator = ttk.Separator(self.main_frame, orient="horizontal", style="Modern.TSeparator")
        separator.pack(fill=tk.X, pady=(10, 0))
    
    def create_toolbar(self):
        """Crea toolbar con controlli"""
        self.toolbar_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.toolbar_frame.pack(fill=tk.X, pady=(15, 10))
        
        # Sezione filtri (sinistra)
        filter_frame = ttk.Frame(self.toolbar_frame, style="Main.TFrame")
        filter_frame.pack(side=tk.LEFT)
        
        # Label filtro
        filter_label = ttk.Label(
            filter_frame,
            text="Mostra:",
            style="Body.TLabel"
        )
        filter_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Combobox filtro
        self.filter_var = tk.StringVar(value="Tutti gli articoli")
        self.filter_combo = ttk.Combobox(
            filter_frame,
            values=["Tutti gli articoli", "Solo Skin", "Solo Campioni", "Sconti > 50%", "Sconti > 25%"],
            textvariable=self.filter_var,
            state="readonly",
            width=15,
            style="Modern.TCombobox"
        )
        self.filter_combo.pack(side=tk.LEFT, padx=(0, 15))
        self.filter_combo.bind("<<ComboboxSelected>>", self.apply_filter)
        
        # Tooltip per filtro
        ModernTooltip(self.filter_combo, "Filtra gli articoli in base al tipo o percentuale di sconto")
        
        # Sezione informazioni (destra)
        info_frame = ttk.Frame(self.toolbar_frame, style="Main.TFrame")
        info_frame.pack(side=tk.RIGHT)
        
        # Contatore articoli
        self.items_count_label = ttk.Label(
            info_frame,
            text="Articoli: 0",
            style="Success.TLabel"
        )
        self.items_count_label.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Risparmio totale
        self.savings_label = ttk.Label(
            info_frame,
            text="",
            style="Success.TLabel"
        )
        self.savings_label.pack(side=tk.RIGHT, padx=(15, 0))
    
    def create_main_area(self):
        """Crea area principale con treeview"""
        # Container per il treeview
        self.tree_container = ttk.Frame(self.main_frame, style="Card.TFrame")
        self.tree_container.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Frame interno
        tree_inner = ttk.Frame(self.tree_container, style="Main.TFrame")
        tree_inner.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Treeview migliorato
        self.tree = ttk.Treeview(
            tree_inner,
            columns=("ID", "Nome", "Tipo", "Prezzo", "PrezzoOriginale", "Valuta", "Sconto", "Risparmio"),
            show="headings",
            selectmode="browse",
            style="Modern.Treeview"
        )
        
        # Configurazione colonne
        columns_config = {
            "ID": {"text": "ID", "width": 80, "anchor": "center"},
            "Nome": {"text": "Nome Articolo", "width": 300, "anchor": "w"},
            "Tipo": {"text": "Categoria", "width": 100, "anchor": "center"},
            "Prezzo": {"text": "Prezzo Scontato", "width": 120, "anchor": "center"},
            "PrezzoOriginale": {"text": "Prezzo Originale", "width": 120, "anchor": "center"},
            "Valuta": {"text": "Valuta", "width": 80, "anchor": "center"},
            "Sconto": {"text": "Sconto %", "width": 90, "anchor": "center"},
            "Risparmio": {"text": "Risparmio", "width": 100, "anchor": "center"}
        }
        
        for col, config in columns_config.items():
            self.tree.heading(col, text=config["text"])
            self.tree.column(col, width=config["width"], anchor=config["anchor"])
        
        # Scrollbar verticale
        scrollbar_y = ttk.Scrollbar(
            tree_inner,
            orient="vertical",
            command=self.tree.yview,
            style="Modern.Vertical.TScrollbar"
        )
        
        self.tree.configure(yscrollcommand=scrollbar_y.set)
        
        # Layout con grid
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        
        tree_inner.grid_rowconfigure(0, weight=1)
        tree_inner.grid_columnconfigure(0, weight=1)
        
        # Bind eventi
        self.tree.bind("<Double-1>", self.on_item_double_click)
    
    def create_status_bar(self):
        """Crea status bar informativa"""
        self.status_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Status principale
        self.status_label = ttk.Label(
            self.status_frame,
            text="Pronto",
            style="Body.TLabel"
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Progress bar (nascosta inizialmente)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            length=200,
            mode='determinate',
            variable=self.progress_var
        )
        # Inizialmente non mostrata
    
    def create_footer(self):
        """Crea footer con pulsanti"""
        self.footer_frame = ttk.Frame(self.main_frame, style="Main.TFrame")
        self.footer_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Pulsanti sinistra
        left_buttons = ttk.Frame(self.footer_frame, style="Main.TFrame")
        left_buttons.pack(side=tk.LEFT)
        
        # Pulsante aggiorna
        self.refresh_button = ttk.Button(
            left_buttons,
            text="🔄 Aggiorna Dati",
            command=self.refresh_data,
            style="Modern.TButton"
        )
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        ModernTooltip(self.refresh_button, "Ricarica i dati dal client di League of Legends")
        
        # Pulsante esporta
        self.export_button = ttk.Button(
            left_buttons,
            text="💾 Esporta Dati",
            command=self.export_data,
            style="Secondary.TButton"
        )
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        ModernTooltip(self.export_button, "Esporta i dati in formato CSV")
        
        # Pulsanti centro
        center_buttons = ttk.Frame(self.footer_frame, style="Main.TFrame")
        center_buttons.pack()
        
        # Link sito LoL
        self.lol_site_button = ttk.Button(
            center_buttons,
            text="🌐 Sito Ufficiale LoL",
            command=lambda: webbrowser.open("https://www.leagueoflegends.com/it-it/"),
            style="Secondary.TButton"
        )
        self.lol_site_button.pack(side=tk.LEFT, padx=5)
        
        # Pulsante informazioni
        self.info_button = ttk.Button(
            center_buttons,
            text="ℹ️ Info",
            command=self.show_info,
            style="Secondary.TButton"
        )
        self.info_button.pack(side=tk.LEFT, padx=5)
        
        # Pulsanti destra
        right_buttons = ttk.Frame(self.footer_frame, style="Main.TFrame")
        right_buttons.pack(side=tk.RIGHT)
        
        # Pulsante chiudi
        self.close_button = ttk.Button(
            right_buttons,
            text="❌ Chiudi",
            command=self.on_closing,
            style="Danger.TButton"
        )
        self.close_button.pack(side=tk.RIGHT)
        
        # Gestione chiusura finestra
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def show_loading(self):
        """Mostra overlay di caricamento moderno"""
        # Overlay semitrasparente
        self.loading_overlay = tk.Frame(self, bg=Colors.DARK_BG)
        self.loading_overlay.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Container centrale
        loading_container = ttk.Frame(self.loading_overlay, style="Card.TFrame")
        loading_container.place(relx=0.5, rely=0.5, anchor="center", width=400, height=250)
        
        # Contenuto interno
        content_frame = ttk.Frame(loading_container, style="Main.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icona di caricamento (Unicode)
        loading_icon = ttk.Label(
            content_frame,
            text="⚡",
            font=("Segoe UI", 48),
            foreground=Colors.GOLD,
            background=Colors.CARD_BG
        )
        loading_icon.pack(pady=(10, 15))
        
        # Titolo caricamento
        loading_title = ttk.Label(
            content_frame,
            text="CARICAMENTO DATI",
            font=self.fonts['heading'],
            foreground=Colors.GOLD,
            background=Colors.CARD_BG
        )
        loading_title.pack(pady=(0, 10))
        
        # Messaggio di stato
        self.loading_status = ttk.Label(
            content_frame,
            text="Connessione al client League of Legends...",
            font=self.fonts['body'],
            foreground=Colors.TEXT_SECONDARY,
            background=Colors.CARD_BG,
            wraplength=350
        )
        self.loading_status.pack(pady=(0, 15))
        
        # Barra di progresso animata
        self.loading_progress = ttk.Progressbar(
            content_frame,
            length=300,
            mode='indeterminate'
        )
        self.loading_progress.pack(pady=(0, 10))
        self.loading_progress.start(10)
    
    def hide_loading(self):
        """Nasconde overlay di caricamento"""
        try:
            if hasattr(self, 'loading_progress'):
                self.loading_progress.stop()
            if hasattr(self, 'loading_overlay'):
                self.loading_overlay.destroy()
        except Exception as e:
            print(f"Errore durante la chiusura del loading: {e}")
    
    def update_loading_status(self, message):
        """Aggiorna messaggio di stato nel loading"""
        try:
            if hasattr(self, 'loading_status'):
                self.after(0, lambda: self.loading_status.config(text=message))
        except Exception as e:
            print(f"Errore aggiornamento status loading: {e}")
    
    def load_data(self):
        """Carica dati con messaggi di stato migliorati"""
        try:
            # Fase 1: Lockfile
            self.update_loading_status("Lettura configurazione League of Legends...")
            lockfile_data = get_lockfile_data()
            if not lockfile_data:
                self.show_error("League of Legends non è in esecuzione o non è accessibile.\n\nAssicurati che il client sia aperto e che tu sia connesso.")
                return
            
            # Fase 2: Versione
            self.update_loading_status("Rilevamento versione del gioco...")
            lol_version = get_lol_version(lockfile_data)
            if not lol_version:
                self.show_error("Impossibile ottenere la versione di League of Legends.\n\nRiprova tra qualche secondo.")
                return
            
            self._temp_data['version'] = lol_version
            
            # Fase 3: Data Dragon
            self.update_loading_status("Download dati campioni e skin da Riot Games...")
            skins_data = get_skins_data(lol_version)
            if not skins_data:
                self.show_error("Impossibile scaricare i dati da Data Dragon.\n\nControlla la connessione internet.")
                return
            
            skin_map = map_skin_ids_to_names(skins_data)
            champ_map = map_champion_ids_to_names(skins_data)
            
            # Fase 4: Catalogo negozio
            self.update_loading_status("Accesso al catalogo del negozio...")
            catalog_data = get_catalog(lockfile_data)
            if not catalog_data:
                self.show_error("Impossibile accedere al catalogo del negozio.\n\nAssicurati di essere connesso al client.")
                return
            
            # Fase 5: Elaborazione offerte
            self.update_loading_status("Elaborazione offerte speciali...")
            sales_items = filter_sales_items(catalog_data, skin_map, champ_map)
            
            if not sales_items:
                self._temp_data['no_sales'] = True
            else:
                self._temp_data['sales_items'] = sales_items
            
            # Fase 6: Finalizzazione
            self.update_loading_status("Finalizzazione caricamento...")
            self.event_generate("<<DataLoaded>>")
            
        except Exception as e:
            self.show_error(f"Errore durante il caricamento dei dati:\n\n{str(e)}\n\nRiprova o riavvia l'applicazione.")
        finally:
            self.event_generate("<<HideLoading>>")
    
    def _on_data_loaded(self, event):
        """Gestisce caricamento completato"""
        try:
            # Aggiorna versione
            if 'version' in self._temp_data:
                self.version_label.config(text=f"Versione: {self._temp_data['version']}")
            
            # Aggiorna timestamp
            now = datetime.now().strftime("%H:%M:%S")
            self.update_time_label.config(text=f"Aggiornato: {now}")
            
            # Gestisci risultati
            if self._temp_data.get('no_sales', False):
                self.status_label.config(text="Nessuna offerta speciale disponibile al momento")
                messagebox.showinfo(
                    "Nessuna Offerta",
                    "Al momento non ci sono skin o campioni in saldo nel negozio.\n\nTorna a controllare più tardi!"
                )
            else:
                if 'sales_items' in self._temp_data:
                    self.update_treeview(self._temp_data['sales_items'])
                    self.data_loaded = True
                    count = len(self._temp_data['sales_items'])
                    self.status_label.config(text=f"Caricati {count} articoli in offerta")
        
        except Exception as e:
            print(f"Errore in _on_data_loaded: {e}")
    
    def _on_hide_loading(self, event):
        """Nasconde schermata di caricamento"""
        self.hide_loading()
    
    def update_treeview(self, sales_items):
        """Aggiorna treeview con stile migliorato"""
        try:
            # Pulisci contenuti esistenti
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            total_savings = 0
            
            # Inserisci nuovi dati
            for index, item in enumerate(sales_items):
                # Formattazione
                item_id = item['id']
                name = item['name']
                item_type = "Skin" if item['type'] == "CHAMPION_SKIN" else "Campione"
                
                current_price = item['price']
                original_price = item.get('original_price', current_price)
                currency = item['currency']
                
                discount = item.get('discount', 0)
                discount_text = f"{discount}%" if discount > 0 else "N/A"
                
                # Calcola risparmio
                savings = original_price - current_price if original_price > current_price else 0
                savings_text = f"{savings} {currency}" if savings > 0 else "N/A"
                total_savings += savings
                
                # Stile alternato
                tag = "even" if index % 2 == 0 else "odd"
                if discount >= 50:
                    tag += "_high_discount"
                elif discount >= 25:
                    tag += "_medium_discount"
                
                # Inserisci riga
                self.tree.insert(
                    "", "end",
                    values=(
                        item_id,
                        name,
                        item_type,
                        f"{current_price} {currency}",
                        f"{original_price} {currency}",
                        currency,
                        discount_text,
                        savings_text
                    ),
                    tags=(tag,)
                )
            
            # Aggiorna contatori
            self.items_count_label.config(text=f"Articoli: {len(sales_items)}")
            if total_savings > 0:
                self.savings_label.config(text=f"Risparmio totale: {total_savings} RP")
            
            # Configura tags per stili righe
            self.tree.tag_configure("even", background=Colors.CARD_BG)
            self.tree.tag_configure("odd", background=Colors.DARK_SECONDARY)
            self.tree.tag_configure("even_high_discount", background="#0F4C3A", foreground=Colors.SUCCESS)
            self.tree.tag_configure("odd_high_discount", background="#0F4C3A", foreground=Colors.SUCCESS)
            self.tree.tag_configure("even_medium_discount", background="#4C3A0F", foreground=Colors.WARNING)
            self.tree.tag_configure("odd_medium_discount", background="#4C3A0F", foreground=Colors.WARNING)
            
        except Exception as e:
            print(f"Errore aggiornamento treeview: {e}")
    
    def apply_filter(self, event=None):
        """Applica filtri avanzati"""
        try:
            if not self.data_loaded or 'sales_items' not in self._temp_data:
                return
            
            selected_filter = self.filter_var.get()
            all_items = self._temp_data['sales_items']
            
            # Applica filtro
            if selected_filter == "Tutti gli articoli":
                filtered_items = all_items
            elif selected_filter == "Solo Skin":
                filtered_items = [item for item in all_items if item['type'] == "CHAMPION_SKIN"]
            elif selected_filter == "Solo Campioni":
                filtered_items = [item for item in all_items if item['type'] == "CHAMPION"]
            elif selected_filter == "Sconti > 50%":
                filtered_items = [item for item in all_items if item.get('discount', 0) > 50]
            elif selected_filter == "Sconti > 25%":
                filtered_items = [item for item in all_items if item.get('discount', 0) > 25]
            else:
                filtered_items = all_items
            
            # Aggiorna visualizzazione
            self.update_treeview(filtered_items)
            
        except Exception as e:
            print(f"Errore applicazione filtro: {e}")
    
    def on_item_double_click(self, event):
        """Gestisce doppio click su elemento"""
        try:
            selection = self.tree.selection()
            if not selection:
                return
            
            item = self.tree.item(selection[0])
            values = item['values']
            
            if len(values) >= 2:
                name = values[1]  # Nome articolo
                item_type = values[2]  # Tipo
                
                # Mostra info dettagliate
                messagebox.showinfo(
                    f"Dettagli {item_type}",
                    f"Nome: {name}\n"
                    f"Tipo: {item_type}\n"
                    f"ID: {values[0]}\n"
                    f"Prezzo Attuale: {values[3]}\n"
                    f"Prezzo Originale: {values[4]}\n"
                    f"Sconto: {values[6]}\n"
                    f"Risparmio: {values[7]}"
                )
        except Exception as e:
            print(f"Errore doppio click: {e}")
    
    def refresh_data(self):
        """Ricarica dati"""
        self.data_loaded = False
        self.show_loading()
        threading.Thread(target=self.load_data, daemon=True).start()
    
    def export_data(self):
        """Esporta dati in CSV"""
        try:
            if not self.data_loaded or 'sales_items' not in self._temp_data:
                messagebox.showwarning("Esportazione", "Nessun dato da esportare. Carica prima i dati.")
                return
            
            from tkinter import filedialog
            import csv
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Salva dati offerte"
            )
            
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    # Header
                    writer.writerow(['ID', 'Nome', 'Tipo', 'Prezzo Scontato', 'Prezzo Originale', 'Valuta', 'Sconto %', 'Risparmio'])
                    
                    # Dati
                    for item in self._temp_data['sales_items']:
                        writer.writerow([
                            item['id'],
                            item['name'],
                            "Skin" if item['type'] == "CHAMPION_SKIN" else "Campione",
                            item['price'],
                            item.get('original_price', item['price']),
                            item['currency'],
                            item.get('discount', 0),
                            item.get('original_price', item['price']) - item['price']
                        ])
                
                messagebox.showinfo("Esportazione", f"Dati esportati con successo in:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Errore Esportazione", f"Errore durante l'esportazione:\n{str(e)}")
    
    def show_info(self):
        """Finestra informazioni migliorata"""
        try:
            # Crea finestra modale
            info_window = tk.Toplevel(self)
            info_window.title("Informazioni - LoL Shop Monitor")
            info_window.geometry("500x400")
            info_window.configure(bg=Colors.DARK_BG)
            info_window.resizable(False, False)
            info_window.transient(self)
            info_window.grab_set()
            
            # Centra finestra
            info_window.update_idletasks()
            x = (info_window.winfo_screenwidth() // 2) - (500 // 2)
            y = (info_window.winfo_screenheight() // 2) - (400 // 2)
            info_window.geometry(f"500x400+{x}+{y}")
            
            # Container principale
            main_container = ttk.Frame(info_window, style="Card.TFrame")
            main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            content_frame = ttk.Frame(main_container, style="Main.TFrame")
            content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            # Titolo
            title = ttk.Label(
                content_frame,
                text="LEAGUE OF LEGENDS SHOP MONITOR",
                font=self.fonts['heading'],
                foreground=Colors.GOLD,
                background=Colors.CARD_BG
            )
            title.pack(pady=(0, 15))
            
            # Separatore
            sep = ttk.Separator(content_frame, orient="horizontal", style="Modern.TSeparator")
            sep.pack(fill=tk.X, pady=(0, 15))
            
            # Informazioni
            info_text = """Questa applicazione ti permette di monitorare le offerte speciali del negozio di League of Legends in tempo reale.

🔍 FUNZIONALITÀ:
• Visualizzazione di tutte le skin e campioni in saldo
• Calcolo automatico del risparmio
• Filtri avanzati per tipo e percentuale di sconto
• Esportazione dati in formato CSV
• Aggiornamento in tempo reale

⚙️ REQUISITI:
• League of Legends deve essere in esecuzione
• Connessione internet attiva
• Client LoL con accesso ai dati del negozio

💡 UTILIZZO:
1. Avvia il client di League of Legends
2. Apri questa applicazione
3. I dati verranno caricati automaticamente
4. Usa il pulsante "Aggiorna" per dati più recenti

Sviluppato per migliorare la tua esperienza di shopping in League of Legends!"""
            
            info_label = ttk.Label(
                content_frame,
                text=info_text,
                font=self.fonts['body'],
                foreground=Colors.TEXT_PRIMARY,
                background=Colors.CARD_BG,
                wraplength=450,
                justify="left"
            )
            info_label.pack(pady=(0, 20))
            
            # Pulsante chiudi
            close_btn = ttk.Button(
                content_frame,
                text="✅ Ho Capito",
                command=info_window.destroy,
                style="Modern.TButton"
            )
            close_btn.pack(pady=(10, 0))
        
        except Exception as e:
            print(f"Errore finestra info: {e}")
    
    def show_error(self, message):
        """Mostra errore con stile migliorato"""
        self.after(0, lambda: messagebox.showerror("Errore", message))
        self.after(0, self.hide_loading)
    
    def on_closing(self):
        """Gestisce chiusura applicazione"""
        if messagebox.askokcancel("Chiudi Applicazione", "Sei sicuro di voler chiudere l'applicazione?"):
            self.destroy()

# FUNZIONI DI SUPPORTO MIGLIORATE

def get_lockfile_data():
    """Legge dati dal lockfile con gestione errori migliorata"""
    try:
        if not os.path.exists(lockfile_path):
            return None
        
        with open(lockfile_path, 'r', encoding='utf-8') as f:
            data = f.read().strip().split(':')
        
        if len(data) < 5:
            return None
        
        return {
            'name': data[0],
            'pid': data[1],
            'port': data[2],
            'password': data[3],
            'protocol': data[4]
        }
    
    except Exception as e:
        print(f"Errore lettura lockfile: {e}")
        return None

def get_lol_version(lockfile_data):
    """Ottiene versione LoL con timeout migliorato"""
    try:
        url = f"{lockfile_data['protocol']}://127.0.0.1:{lockfile_data['port']}/lol-patch/v1/game-version"
        auth_header = base64.b64encode(f"riot:{lockfile_data['password']}".encode()).decode()
        headers = {"Authorization": f"Basic {auth_header}"}
        
        response = requests.get(url, headers=headers, verify=False, timeout=15)
        
        if response.status_code == 200:
            version_data = response.json()
            # Estrai versione dal formato completo
            if isinstance(version_data, str):
                version_match = re.search(r"(\d+\.\d+)", version_data)
                return version_match.group(1) if version_match else None
        
        return None
    
    except Exception as e:
        print(f"Errore ottenimento versione: {e}")
        return None

def get_catalog(lockfile_data):
    """Ottiene catalogo negozio con retry"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            url = f"{lockfile_data['protocol']}://127.0.0.1:{lockfile_data['port']}/lol-store/v1/catalog"
            auth_header = base64.b64encode(f"riot:{lockfile_data['password']}".encode()).decode()
            headers = {"Authorization": f"Basic {auth_header}"}
            
            response = requests.get(url, headers=headers, verify=False, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else None
            
            if attempt < max_retries - 1:
                import time
                time.sleep(2)  # Attendi prima del retry
        
        except Exception as e:
            print(f"Tentativo {attempt + 1} fallito: {e}")
            if attempt < max_retries - 1:
                import time
                time.sleep(2)
    
    return None

def get_skins_data(version):
    """Ottiene dati da Data Dragon con cache"""
    try:
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}.1/data/it_IT/championFull.json"
        response = requests.get(url, timeout=20)
        
        if response.status_code == 200:
            return response.json()
        
        return {}
    
    except Exception as e:
        print(f"Errore Data Dragon: {e}")
        return {}

def filter_sales_items(catalog_data, skin_map, champ_map):
    """Filtra articoli in saldo con informazioni dettagliate"""
    try:
        sales_items = []
        
        # Verifica che catalog_data sia valido
        if not catalog_data or not isinstance(catalog_data, list):
            print("Catalogo dati non valido o vuoto")
            return []
        
        for item in catalog_data:
            # Controlla che item non sia None e sia un dizionario
            if not item or not isinstance(item, dict):
                continue
            
            # Verifica presenza di vendita e prezzi
            sale_data = item.get('sale')
            if not sale_data or not isinstance(sale_data, dict):
                continue
                
            prices = sale_data.get('prices')
            if not prices or not isinstance(prices, list) or len(prices) == 0:
                continue
            
            # Estrai informazioni base
            item_id = str(item.get('itemId', '0'))
            inventory_type = item.get('inventoryType', '')
            
            # Salta se tipo non supportato
            if inventory_type not in ["CHAMPION_SKIN", "CHAMPION"]:
                continue
            
            # Determina nome
            if inventory_type == "CHAMPION_SKIN":
                name = skin_map.get(item_id, f"Skin Sconosciuta (ID: {item_id})")
            else:  # CHAMPION
                name = champ_map.get(item_id, f"Campione Sconosciuto (ID: {item_id})")
            
            # Estrai prezzi con controlli di sicurezza
            try:
                first_price = prices[0]
                if not isinstance(first_price, dict):
                    continue
                    
                current_price = first_price.get('cost', 0)
                currency = first_price.get('currency', 'RP')
                
                # Verifica che il prezzo sia valido
                if not isinstance(current_price, (int, float)) or current_price <= 0:
                    continue
                
                # Prezzo originale
                original_price = current_price
                original_prices = sale_data.get('originalPrices')
                
                if (original_prices and isinstance(original_prices, list) and 
                    len(original_prices) > 0 and isinstance(original_prices[0], dict)):
                    
                    orig_cost = original_prices[0].get('cost')
                    if isinstance(orig_cost, (int, float)) and orig_cost > 0:
                        original_price = orig_cost
                
                # Calcola sconto
                discount = 0
                if original_price > current_price and original_price > 0:
                    discount = round(100 - (current_price / original_price * 100))
                    # Assicurati che lo sconto sia ragionevole
                    discount = max(0, min(100, discount))
                
                # Aggiungi articolo solo se tutti i dati sono validi
                if current_price > 0 and original_price > 0:
                    sales_items.append({
                        'id': item_id,
                        'name': name,
                        'type': inventory_type,
                        'price': current_price,
                        'original_price': original_price,
                        'currency': currency,
                        'discount': discount
                    })
            
            except (KeyError, IndexError, TypeError, AttributeError, ValueError) as e:
                print(f"Errore elaborazione articolo {item_id}: {e}")
                continue
        
        print(f"Trovati {len(sales_items)} articoli in saldo validi")
        return sales_items
    
    except Exception as e:
        print(f"Errore critico filtro articoli: {e}")
        import traceback
        traceback.print_exc()
        return []

def map_skin_ids_to_names(skins_data):
    """Mappa skin IDs con nomi migliorati"""
    try:
        skin_map = {}
        for champion_data in skins_data.get('data', {}).values():
            champion_name = champion_data.get('name', 'Sconosciuto')
            for skin in champion_data.get('skins', []):
                skin_id = str(skin.get('id', ''))
                skin_name = skin.get('name', 'Skin Predefinita')
                
                # Migliora nome skin
                if skin_name == 'default':
                    skin_name = f"{champion_name} (Classico)"
                elif champion_name not in skin_name:
                    skin_name = f"{champion_name} {skin_name}"
                
                skin_map[skin_id] = skin_name
        
        return skin_map
    
    except Exception as e:
        print(f"Errore mapping skin: {e}")
        return {}

def map_champion_ids_to_names(skins_data):
    """Mappa champion IDs con nomi"""
    try:
        champion_map = {}
        for champion_data in skins_data.get('data', {}).values():
            champion_id = str(champion_data.get('key', ''))
            champion_name = champion_data.get('name', 'Campione Sconosciuto')
            champion_map[champion_id] = champion_name
        
        return champion_map
    
    except Exception as e:
        print(f"Errore mapping campioni: {e}")
        return {}

# ESECUZIONE APPLICAZIONE
if __name__ == "__main__":
    try:
        # Verifica requisiti
        import sys
        print("Avvio League of Legends Shop Monitor...")
        
        app = LolShopApp()
        app.mainloop()
    
    except ImportError as e:
        missing_module = str(e).split("'")[1] if "'" in str(e) else "sconosciuto"
        messagebox.showerror(
            "Modulo Mancante",
            f"Modulo richiesto mancante: {missing_module}\n\n"
            f"Installa con: pip install {missing_module}"
        )
    
    except Exception as e:
        error_msg = f"Errore critico: {str(e)}"
        print(error_msg)
        
        # Log errore
        try:
            with open("lol_shop_error.log", "a", encoding='utf-8') as f:
                f.write(f"{datetime.now()}: {error_msg}\n")
        except:
            pass
        
        # Mostra errore all'utente
        try:
            messagebox.showerror(
                "Errore Critico",
                f"{error_msg}\n\n"
                "Suggerimenti:\n"
                "• Assicurati che League of Legends sia in esecuzione\n"
                "• Verifica la connessione internet\n"
                "• Riavvia l'applicazione\n"
                "• Controlla il file di log per maggiori dettagli"
            )
        except:
            print("Impossibile mostrare finestra di errore")