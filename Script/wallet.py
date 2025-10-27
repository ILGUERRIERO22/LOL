import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import os
import threading
import logging
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional

# Importazioni condizionali
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL non disponibile - alcune funzionalità grafiche saranno limitate")

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Matplotlib non disponibile - i grafici non saranno disponibili")

# Importazione dell'API Riot (mantenuta invariata)
from Riot_API import get_balance, RiotAPIError


class ModernButton(tk.Frame):
    """Pulsante personalizzato con effetti moderni"""
    
    def __init__(self, parent, text="", command=None, bg_color="#1E2328", 
                 hover_color="#0397AB", text_color="#F0E6D2", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        
        # Crea il pulsante interno
        self.button = tk.Label(
            self,
            text=text,
            bg=bg_color,
            fg=text_color,
            font=("Segoe UI", 11, "bold"),
            cursor="hand2",
            padx=20,
            pady=8,
            relief="flat"
        )
        self.button.pack(fill="both", expand=True)
        
        # Bind degli eventi
        self.button.bind("<Button-1>", self._on_click)
        self.button.bind("<Enter>", self._on_enter)
        self.button.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_click(self, event=None):
        if self.command:
            self.command()
    
    def _on_enter(self, event=None):
        self.button.configure(bg=self.hover_color)
    
    def _on_leave(self, event=None):
        self.button.configure(bg=self.bg_color)
    
    def configure_text(self, text):
        """Configura il testo del pulsante"""
        self.button.configure(text=text)


class AnimatedProgressBar(tk.Frame):
    """Barra di progresso animata"""
    
    def __init__(self, parent, width=200, height=4, bg_color="#1E2328", 
                 fill_color="#C8AA6E", **kwargs):
        super().__init__(parent, **kwargs)
        
        self.canvas = tk.Canvas(
            self,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=0
        )
        self.canvas.pack()
        
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.progress = 0
        self.animation_id = None
    
    def set_progress(self, value):
        """Imposta il progresso (0-100)"""
        if self.animation_id:
            self.after_cancel(self.animation_id)
        
        target = max(0, min(100, value))
        self._animate_to(target)
    
    def _animate_to(self, target):
        """Anima il progresso verso il valore target"""
        if abs(self.progress - target) < 1:
            self.progress = target
            self._draw()
            return
        
        # Incremento graduale
        step = (target - self.progress) * 0.2
        self.progress += step
        self._draw()
        
        self.animation_id = self.after(16, lambda: self._animate_to(target))
    
    def _draw(self):
        """Disegna la barra di progresso"""
        self.canvas.delete("all")
        
        # Sfondo
        self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill=self.bg_color, outline=""
        )
        
        # Progresso
        progress_width = (self.width * self.progress) / 100
        if progress_width > 0:
            self.canvas.create_rectangle(
                0, 0, progress_width, self.height,
                fill=self.fill_color, outline=""
            )


class CurrencyCard(tk.Frame):
    """Card moderna per visualizzare le valute"""
    
    def __init__(self, parent, currency_name, currency_color, **kwargs):
        super().__init__(parent, bg="#1a1a1a", relief="flat", bd=0, **kwargs)
        
        self.currency_name = currency_name
        self.currency_color = currency_color
        self.current_value = 0
        self.previous_value = None
        
        # Padding interno
        self.configure(padx=15, pady=12)
        
        # Crea il contenuto
        self._create_content()
        
        # Effetti hover
        self._setup_hover_effects()
    
    def _create_content(self):
        """Crea il contenuto della card"""
        # Header con indicatore colorato e nome
        header_frame = tk.Frame(self, bg="#1a1a1a")
        header_frame.pack(fill="x", pady=(0, 8))
        
        # Indicatore colorato
        indicator = tk.Frame(
            header_frame,
            bg=self.currency_color,
            width=4,
            height=30
        )
        indicator.pack(side="left", padx=(0, 12))
        
        # Nome della valuta
        self.name_label = tk.Label(
            header_frame,
            text=self.currency_name,
            font=("Segoe UI", 12, "bold"),
            bg="#1a1a1a",
            fg="#E0E0E0",
            anchor="w"
        )
        self.name_label.pack(side="left", fill="x", expand=True)
        
        # Indicatore di tendenza
        self.trend_label = tk.Label(
            header_frame,
            text="",
            font=("Segoe UI", 14),
            bg="#1a1a1a",
            fg=self.currency_color
        )
        self.trend_label.pack(side="right")
        
        # Valore principale
        value_frame = tk.Frame(self, bg="#1a1a1a")
        value_frame.pack(fill="x")
        
        self.value_label = tk.Label(
            value_frame,
            text="Caricamento...",
            font=("Segoe UI", 18, "bold"),
            bg="#1a1a1a",
            fg=self.currency_color,
            anchor="w"
        )
        self.value_label.pack(side="left")
        
        # Differenza dal valore precedente
        self.diff_label = tk.Label(
            value_frame,
            text="",
            font=("Segoe UI", 10),
            bg="#1a1a1a",
            fg="#888888",
            anchor="w"
        )
        self.diff_label.pack(side="left", padx=(10, 0))
        
        # Barra di progresso (opzionale per alcune valute)
        if "essence" in self.currency_name.lower():
            self.progress_bar = AnimatedProgressBar(
                self,
                width=200,
                height=3,
                bg_color="#2a2a2a",
                fill_color=self.currency_color
            )
            self.progress_bar.pack(fill="x", pady=(8, 0))
        else:
            self.progress_bar = None
    
    def _setup_hover_effects(self):
        """Configura gli effetti hover"""
        def on_enter(event):
            self._change_bg_recursive("#2a2a2a")
        
        def on_leave(event):
            self._change_bg_recursive("#1a1a1a")
        
        # Bind eventi per tutti i widget
        self._bind_recursive(self, on_enter, on_leave)
    
    def _change_bg_recursive(self, color):
        """Cambia il colore di sfondo ricorsivamente"""
        try:
            self.configure(bg=color)
            for widget in self.winfo_children():
                self._change_widget_bg(widget, color)
        except:
            pass
    
    def _change_widget_bg(self, widget, color):
        """Cambia il colore di sfondo di un widget"""
        try:
            if hasattr(widget, 'configure'):
                widget.configure(bg=color)
                for child in widget.winfo_children():
                    self._change_widget_bg(child, color)
        except:
            pass
    
    def _bind_recursive(self, widget, on_enter, on_leave):
        """Applica il binding ricorsivamente"""
        try:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            for child in widget.winfo_children():
                self._bind_recursive(child, on_enter, on_leave)
        except:
            pass
    
    def update_value(self, new_value: int, animate: bool = True):
        """Aggiorna il valore della valuta"""
        self.previous_value = self.current_value
        self.current_value = new_value
        
        # Aggiorna l'etichetta del valore
        formatted_value = f"{new_value:,}".replace(",", ".")
        self.value_label.configure(text=formatted_value)
        
        # Aggiorna l'indicatore di tendenza
        if self.previous_value is not None and self.previous_value != 0:
            diff = new_value - self.previous_value
            if diff > 0:
                self.trend_label.configure(text="▲", fg="#4CAF50")
                self.diff_label.configure(text=f"+{diff:,}".replace(",", "."), fg="#4CAF50")
            elif diff < 0:
                self.trend_label.configure(text="▼", fg="#F44336")
                self.diff_label.configure(text=f"{diff:,}".replace(",", "."), fg="#F44336")
            else:
                self.trend_label.configure(text="●", fg="#888888")
                self.diff_label.configure(text="", fg="#888888")
        else:
            self.trend_label.configure(text="")
            self.diff_label.configure(text="")
        
        # Aggiorna la barra di progresso se presente
        if self.progress_bar and new_value > 0:
            if "blue essence" in self.currency_name.lower():
                max_typical = 100000
            elif "orange essence" in self.currency_name.lower():
                max_typical = 10000
            else:
                max_typical = new_value * 1.2
            
            progress_percent = min(100, (new_value / max_typical) * 100)
            self.progress_bar.set_progress(progress_percent)


class LolWalletApp:
    """Applicazione League of Legends Wallet migliorata"""
    
    def __init__(self, root):
        self.root = root
        self.setup_logging()
        self.init_variables()
        self.setup_window()
        self.create_styles()
        self.setup_ui()
        self.setup_auto_refresh()
        
        # Primo caricamento dati
        self.root.after(500, self.update_data)
        
        self.logger.info("Applicazione avviata con successo")
    
    def setup_logging(self):
        """Configura il sistema di logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('lol_wallet.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def init_variables(self):
        """Inizializza le variabili dell'applicazione"""
        self.current_theme = "dark"
        self.auto_refresh_enabled = True
        self.refresh_interval = 60000
        self.currency_cards: Dict[str, CurrencyCard] = {}
        self.chart_data: Dict[str, Dict[str, List]] = {}
        self._previous_data: Dict[str, Any] = {}
        
        # Definizione temi migliorati
        self.themes = {
            "dark": {
                "bg_primary": "#0A0E13",
                "bg_secondary": "#1E2328", 
                "bg_tertiary": "#2D3142",
                "accent": "#C8AA6E",
                "text_primary": "#F0E6D2",
                "text_secondary": "#C9AA71",
                "success": "#4CAF50",
                "error": "#F44336",
                "warning": "#FF9800",
                "info": "#2196F3"
            },
            "light": {
                "bg_primary": "#F5F5F5",
                "bg_secondary": "#FFFFFF",
                "bg_tertiary": "#E0E0E0",
                "accent": "#8A6D3B",
                "text_primary": "#212121",
                "text_secondary": "#757575",
                "success": "#4CAF50",
                "error": "#F44336",
                "warning": "#FF9800",
                "info": "#2196F3"
            }
        }
        
        # Definizione valute con colori migliorati
        self.currency_config = [
            ("RP", "#FF6B35", "Riot Points", "rp"),
            ("lol_blue_essence", "#0AC8B9", "Blue Essence", "be"),
            ("lol_mythic_essence", "#A885D3", "Mythic Essence", "me"),
            ("lol_orange_essence", "#FF8C42", "Orange Essence", "oe"),
            ("lol_clash_tickets", "#FFC93C", "Clash Tickets", "clash"),
            ("tft_ultra_premium_coin", "#E9C46A", "Medaglie TFT", "medallions"),
            ("TFT_TREASURE_TROVE_TOKEN", "#F4A261", "Token TFT Treasure", "tft_tokens")
        ]
        
        # Inizializza dati grafici
        for currency_id, _, _, _ in self.currency_config:
            self.chart_data[currency_id] = {'values': [], 'times': []}
    
    def setup_window(self):
        """Configura la finestra principale"""
        self.root.title("League of Legends Wallet - Versione 2.5")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)
        
        # Centra la finestra
        self.center_window()
        
        # Configura l'icona se disponibile
        self.setup_window_icon()
        
        # Configura il tema della finestra
        colors = self.themes[self.current_theme]
        self.root.configure(bg=colors["bg_primary"])
        
        # Gestione chiusura finestra
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def center_window(self):
        """Centra la finestra sullo schermo"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_window_icon(self):
        """Configura l'icona della finestra"""
        try:
            icon_paths = [
                os.path.join(os.path.dirname(__file__), "assets", "icon.ico"),
                os.path.join(os.path.dirname(__file__), "icon.ico"),
                "icon.ico"
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    break
        except Exception as e:
            self.logger.warning(f"Impossibile caricare l'icona: {e}")
    
    def create_styles(self):
        """Crea gli stili personalizzati"""
        self.style = ttk.Style()
        colors = self.themes[self.current_theme]
        
        # Configura tema base
        self.style.theme_use("clam")
        
        # Stili per Frame
        self.style.configure(
            "Main.TFrame",
            background=colors["bg_primary"],
            relief="flat"
        )
        
        # Stili per Notebook
        self.style.configure(
            "Modern.TNotebook",
            background=colors["bg_primary"],
            borderwidth=0,
            tabmargins=[2, 5, 2, 0]
        )
        
        self.style.configure(
            "Modern.TNotebook.Tab",
            background=colors["bg_tertiary"],
            foreground=colors["text_primary"],
            padding=[20, 10],
            font=("Segoe UI", 11, "bold"),
            borderwidth=0
        )
        
        self.style.map(
            "Modern.TNotebook.Tab",
            background=[("selected", colors["accent"])],
            foreground=[("selected", colors["bg_primary"])]
        )
    
    def setup_ui(self):
        """Configura l'interfaccia utente"""
        colors = self.themes[self.current_theme]
        
        # Container principale
        self.main_container = tk.Frame(self.root, bg=colors["bg_primary"])
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header()
        
        # Notebook per le tab
        self.create_notebook()
        
        # Footer con controlli
        self.create_footer()
        
        # Status bar
        self.create_status_bar()
    
    def create_header(self):
        """Crea l'header dell'applicazione"""
        colors = self.themes[self.current_theme]
        
        header_frame = tk.Frame(self.main_container, bg=colors["bg_primary"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Logo/Titolo
        title_label = tk.Label(
            header_frame,
            text="LEAGUE OF LEGENDS",
            font=("Beaufort for LOL", 24, "bold"),
            bg=colors["bg_primary"],
            fg=colors["accent"]
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="WALLET TRACKER",
            font=("Beaufort for LOL", 14),
            bg=colors["bg_primary"],
            fg=colors["text_secondary"]
        )
        subtitle_label.pack(pady=(0, 5))
        
        # Separatore decorativo
        separator_frame = tk.Frame(header_frame, bg=colors["accent"], height=2)
        separator_frame.pack(fill="x", pady=(10, 0))
    
    def create_notebook(self):
        """Crea il notebook con le tab"""
        self.notebook = ttk.Notebook(self.main_container, style="Modern.TNotebook")
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))
        
        # Tab Portafoglio
        self.wallet_tab = self.create_wallet_tab()
        self.notebook.add(self.wallet_tab, text="Portafoglio")
        
        # Tab Grafici (solo se matplotlib è disponibile)
        if MATPLOTLIB_AVAILABLE:
            self.chart_tab = self.create_chart_tab()
            self.notebook.add(self.chart_tab, text="Grafici")
        
        # Tab Impostazioni
        self.settings_tab = self.create_settings_tab()
        self.notebook.add(self.settings_tab, text="Impostazioni")
    
    def _create_scrollable_frame(self, parent):
        """Crea un frame scrollabile con scrollbar migliorata"""
        colors = self.themes[self.current_theme]
        
        # Container principale
        container = tk.Frame(parent, bg=colors["bg_primary"])
        container.pack(fill="both", expand=True)
        
        # Canvas per il contenuto scrollabile
        canvas = tk.Canvas(
            container, 
            bg=colors["bg_primary"], 
            highlightthickness=0,
            bd=0
        )
        
        # Scrollbar verticale
        v_scrollbar = ttk.Scrollbar(
            container, 
            orient="vertical", 
            command=canvas.yview
        )
        
        # Frame scrollabile interno
        scrollable_frame = tk.Frame(canvas, bg=colors["bg_primary"])
        
        # Configura il canvas
        canvas.configure(yscrollcommand=v_scrollbar.set)
        canvas_frame = canvas.create_window(
            (0, 0), 
            window=scrollable_frame, 
            anchor="nw"
        )
        
        # Funzioni di callback per il ridimensionamento
        def _configure_scroll_region(event=None):
            canvas.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def _configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_frame, width=canvas_width)
        
        # Binding degli eventi
        scrollable_frame.bind("<Configure>", _configure_scroll_region)
        canvas.bind("<Configure>", _configure_canvas_width)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            """Gestisce lo scroll con la rotella del mouse"""
            try:
                # Calcola la direzione dello scroll
                if event.delta:
                    # Windows/MacOS
                    delta = -1 * (event.delta / 120)
                elif event.num == 4:
                    # Linux - scroll up
                    delta = -1
                elif event.num == 5:
                    # Linux - scroll down
                    delta = 1
                else:
                    return
                
                # Verifica se il contenuto è scrollabile
                canvas.update_idletasks()
                bbox = canvas.bbox("all")
                if bbox:
                    content_height = bbox[3] - bbox[1]
                    canvas_height = canvas.winfo_height()
                    
                    # Scorri solo se c'è contenuto che va oltre la vista
                    if content_height > canvas_height:
                        canvas.yview_scroll(int(delta), "units")
            except Exception as e:
                # Fallback silenzioso in caso di errori
                pass
        
        def _on_enter_canvas(event):
            """Quando il mouse entra nel canvas, abilita lo scroll"""
            canvas.focus_set()
        
        def _on_leave_canvas(event):
            """Quando il mouse esce dal canvas, mantieni il focus per la tastiera"""
            # Non rimuovere il focus per permettere controlli tastiera
            pass
        
        # Binding eventi mouse wheel - solo per il canvas principale
        canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows/MacOS
        canvas.bind("<Button-4>", _on_mousewheel)    # Linux scroll up
        canvas.bind("<Button-5>", _on_mousewheel)    # Linux scroll down
        
        # Binding eventi focus
        canvas.bind("<Enter>", _on_enter_canvas)
        canvas.bind("<Leave>", _on_leave_canvas)
        
        # Binding per il frame scrollabile - propaga al canvas
        def _propagate_scroll(event):
            # Propaga l'evento di scroll al canvas parent
            canvas.event_generate("<MouseWheel>", delta=event.delta, x=0, y=0)
        
        scrollable_frame.bind("<MouseWheel>", _propagate_scroll)
        scrollable_frame.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))
        scrollable_frame.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))
        
        # Aggiungi un metodo per applicare il binding ai widget dinamici
        def bind_wheel_to_widget(widget, canvas_ref):
            """Applica il binding della rotella del mouse a un widget"""
            def _wheel_handler(event):
                # Propaga l'evento al canvas
                try:
                    if event.delta:
                        delta = -1 * (event.delta / 120)
                    elif event.num == 4:
                        delta = -1
                    elif event.num == 5:
                        delta = 1
                    else:
                        return
                    
                    canvas_ref.update_idletasks()
                    bbox = canvas_ref.bbox("all")
                    if bbox:
                        content_height = bbox[3] - bbox[1]
                        canvas_height = canvas_ref.winfo_height()
                        if content_height > canvas_height:
                            canvas_ref.yview_scroll(int(delta), "units")
                except:
                    pass
            
            # Applica il binding al widget e ai suoi figli
            widget.bind("<MouseWheel>", _wheel_handler)
            widget.bind("<Button-4>", lambda e: _wheel_handler(e))
            widget.bind("<Button-5>", lambda e: _wheel_handler(e))
            
            # Applica ricorsivamente ai figli
            try:
                for child in widget.winfo_children():
                    bind_wheel_to_widget(child, canvas_ref)
            except:
                pass
        
        # Salva il metodo nel canvas per uso futuro
        canvas.bind_wheel_to_widget = lambda widget: bind_wheel_to_widget(widget, canvas)
        
        # Focus handling migliorato per keyboard scrolling
        def _on_key_scroll(event):
            """Gestisce lo scroll con la tastiera"""
            try:
                canvas.update_idletasks()
                bbox = canvas.bbox("all")
                if bbox:
                    content_height = bbox[3] - bbox[1]
                    canvas_height = canvas.winfo_height()
                    
                    if content_height > canvas_height:
                        if event.keysym in ["Up", "k"]:
                            canvas.yview_scroll(-1, "units")
                        elif event.keysym in ["Down", "j"]:
                            canvas.yview_scroll(1, "units")
                        elif event.keysym == "Page_Up":
                            canvas.yview_scroll(-1, "pages")
                        elif event.keysym == "Page_Down":
                            canvas.yview_scroll(1, "pages")
                        elif event.keysym == "Home":
                            canvas.yview_moveto(0)
                        elif event.keysym == "End":
                            canvas.yview_moveto(1)
                        return "break"  # Previeni la propagazione
            except:
                pass
        
        # Rendi il canvas focusabile e bind keyboard events
        canvas.config(takefocus=True)
        canvas.bind("<Key>", _on_key_scroll)
        canvas.focus_set()
        
        # Pack dei componenti
        canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        
        # Aggiorna la scroll region iniziale
        scrollable_frame.update_idletasks()
        canvas.after_idle(_configure_scroll_region)
        
        return canvas, scrollable_frame
    
    def create_wallet_tab(self):
        """Crea la tab del portafoglio"""
        colors = self.themes[self.current_theme]
        
        # Frame principale per la tab
        main_frame = tk.Frame(self.notebook, bg=colors["bg_primary"])
        
        # Crea il canvas scrollabile
        self.wallet_canvas, self.wallet_scrollable_frame = self._create_scrollable_frame(main_frame)
        
        # Crea il sommario del portafoglio
        self.create_wallet_summary(self.wallet_scrollable_frame)
        
        # Crea le card delle valute
        self.create_currency_cards(self.wallet_scrollable_frame)
        
        return main_frame
    
    def create_wallet_summary(self, parent):
        """Crea il sommario del portafoglio"""
        colors = self.themes[self.current_theme]
        
        # Frame per il sommario
        summary_frame = tk.Frame(parent, bg=colors["bg_secondary"], padx=20, pady=15)
        summary_frame.pack(fill="x", pady=(0, 20), padx=10)
        
        # Titolo
        title_label = tk.Label(
            summary_frame,
            text="Sommario Portafoglio",
            font=("Segoe UI", 16, "bold"),
            bg=colors["bg_secondary"],
            fg=colors["accent"]
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        # Griglia per i riepiloghi principali
        grid_frame = tk.Frame(summary_frame, bg=colors["bg_secondary"])
        grid_frame.pack(fill="x")
        
        # RP Summary
        rp_frame = tk.Frame(grid_frame, bg=colors["bg_tertiary"], padx=15, pady=10)
        rp_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        tk.Label(
            rp_frame,
            text="Riot Points",
            font=("Segoe UI", 10),
            bg=colors["bg_tertiary"],
            fg=colors["text_secondary"]
        ).pack(anchor="w")
        
        self.rp_summary_label = tk.Label(
            rp_frame,
            text="Caricamento...",
            font=("Segoe UI", 18, "bold"),
            bg=colors["bg_tertiary"],
            fg="#FF6B35"
        )
        self.rp_summary_label.pack(anchor="w")
        
        # BE Summary
        be_frame = tk.Frame(grid_frame, bg=colors["bg_tertiary"], padx=15, pady=10)
        be_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        tk.Label(
            be_frame,
            text="Blue Essence",
            font=("Segoe UI", 10),
            bg=colors["bg_tertiary"],
            fg=colors["text_secondary"]
        ).pack(anchor="w")
        
        self.be_summary_label = tk.Label(
            be_frame,
            text="Caricamento...",
            font=("Segoe UI", 18, "bold"),
            bg=colors["bg_tertiary"],
            fg="#0AC8B9"
        )
        self.be_summary_label.pack(anchor="w")
        
        # Ultimo aggiornamento
        update_frame = tk.Frame(grid_frame, bg=colors["bg_tertiary"], padx=15, pady=10)
        update_frame.pack(side="left", fill="both", expand=True, padx=(5, 0))
        
        tk.Label(
            update_frame,
            text="Ultimo Aggiornamento",
            font=("Segoe UI", 10),
            bg=colors["bg_tertiary"],
            fg=colors["text_secondary"]
        ).pack(anchor="w")
        
        self.last_update_label = tk.Label(
            update_frame,
            text="Mai",
            font=("Segoe UI", 12, "bold"),
            bg=colors["bg_tertiary"],
            fg=colors["accent"]
        )
        self.last_update_label.pack(anchor="w")
    
    def create_currency_cards(self, parent):
        """Crea le card per le valute"""
        # Container per le card
        cards_container = tk.Frame(parent, bg=self.themes[self.current_theme]["bg_primary"])
        cards_container.pack(fill="both", expand=True, padx=10)
        
        # Crea le card per ogni valuta
        for i, (currency_id, color, name, short_name) in enumerate(self.currency_config):
            card = CurrencyCard(
                cards_container,
                currency_name=name,
                currency_color=color
            )
            card.pack(fill="x", pady=5, padx=5)
            
            # Applica il binding della rotella del mouse se disponibile
            if hasattr(self, 'wallet_canvas') and hasattr(self.wallet_canvas, 'bind_wheel_to_widget'):
                self.wallet_canvas.bind_wheel_to_widget(card)
            
            # Memorizza riferimento alla card
            self.currency_cards[currency_id] = card
    
    def create_chart_tab(self):
        """Crea la tab dei grafici"""
        if not MATPLOTLIB_AVAILABLE:
            # Frame di fallback se matplotlib non è disponibile
            frame = tk.Frame(self.notebook, bg=self.themes[self.current_theme]["bg_primary"])
            tk.Label(
                frame,
                text="Grafici non disponibili\n\nInstallare matplotlib per abilitare questa funzionalità",
                font=("Segoe UI", 14),
                bg=self.themes[self.current_theme]["bg_primary"],
                fg=self.themes[self.current_theme]["text_secondary"],
                justify="center"
            ).pack(expand=True)
            return frame
        
        colors = self.themes[self.current_theme]
        
        # Frame principale
        main_frame = tk.Frame(self.notebook, bg=colors["bg_primary"])
        
        # Controlli per il grafico
        controls_frame = tk.Frame(main_frame, bg=colors["bg_secondary"], padx=20, pady=15)
        controls_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        tk.Label(
            controls_frame,
            text="Seleziona valuta:",
            font=("Segoe UI", 12),
            bg=colors["bg_secondary"],
            fg=colors["text_primary"]
        ).pack(side="left", padx=(0, 10))
        
        # Variabile per la selezione
        self.selected_currency_var = tk.StringVar()
        
        # Combobox per selezione valuta
        currency_names = [name for _, _, name, _ in self.currency_config]
        self.currency_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.selected_currency_var,
            values=currency_names,
            state="readonly",
            font=("Segoe UI", 11),
            width=20
        )
        self.currency_combo.pack(side="left", padx=5)
        self.currency_combo.current(0)
        self.currency_combo.bind("<<ComboboxSelected>>", self.update_chart)
        
        # Frame per il grafico
        chart_frame = tk.Frame(main_frame, bg=colors["bg_secondary"])
        chart_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Crea il grafico matplotlib
        self.setup_matplotlib_chart(chart_frame)
        
        return main_frame
    
    def setup_matplotlib_chart(self, parent):
        """Configura il grafico matplotlib"""
        colors = self.themes[self.current_theme]
        
        # Crea la figura
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.fig.patch.set_facecolor(colors["bg_secondary"])
        
        # Crea l'asse
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(colors["bg_secondary"])
        
        # Stile dell'asse
        self.ax.tick_params(colors=colors["text_primary"])
        self.ax.spines['bottom'].set_color(colors["text_primary"])
        self.ax.spines['top'].set_color(colors["text_primary"])
        self.ax.spines['right'].set_color(colors["text_primary"])
        self.ax.spines['left'].set_color(colors["text_primary"])
        
        # Canvas per il grafico
        self.chart_canvas = FigureCanvasTkAgg(self.fig, parent)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Inizializza il grafico
        self.update_chart()
    
    def create_settings_tab(self):
        """Crea la tab delle impostazioni"""
        colors = self.themes[self.current_theme]
        
        # Frame principale
        main_frame = tk.Frame(self.notebook, bg=colors["bg_primary"])
        
        # Crea il canvas scrollabile
        settings_canvas, settings_scrollable_frame = self._create_scrollable_frame(main_frame)
        
        # Contenuto delle impostazioni
        self.create_settings_content(settings_scrollable_frame)
        
        return main_frame
    
    def create_settings_content(self, parent):
        """Crea il contenuto delle impostazioni"""
        colors = self.themes[self.current_theme]
        
        # Padding container
        container = tk.Frame(parent, bg=colors["bg_primary"])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sezione Aggiornamento
        refresh_section = tk.Frame(container, bg=colors["bg_secondary"], padx=20, pady=15)
        refresh_section.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            refresh_section,
            text="Aggiornamento Automatico",
            font=("Segoe UI", 14, "bold"),
            bg=colors["bg_secondary"],
            fg=colors["accent"]
        ).pack(anchor="w", pady=(0, 10))
        
        # Controlli per l'intervallo
        interval_frame = tk.Frame(refresh_section, bg=colors["bg_secondary"])
        interval_frame.pack(fill="x", pady=5)
        
        tk.Label(
            interval_frame,
            text="Intervallo (secondi):",
            font=("Segoe UI", 11),
            bg=colors["bg_secondary"],
            fg=colors["text_primary"]
        ).pack(side="left")
        
        self.interval_var = tk.IntVar(value=self.refresh_interval // 1000)
        interval_spinbox = ttk.Spinbox(
            interval_frame,
            from_=10,
            to=3600,
            textvariable=self.interval_var,
            width=8,
            font=("Segoe UI", 11),
            command=self.update_refresh_interval
        )
        interval_spinbox.pack(side="left", padx=(10, 0))
        
        # Sezione Esportazione
        export_section = tk.Frame(container, bg=colors["bg_secondary"], padx=20, pady=15)
        export_section.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            export_section,
            text="Esportazione Dati",
            font=("Segoe UI", 14, "bold"),
            bg=colors["bg_secondary"],
            fg=colors["accent"]
        ).pack(anchor="w", pady=(0, 10))
        
        export_button = ModernButton(
            export_section,
            text="Esporta in CSV",
            command=self.export_data,
            bg_color=colors["bg_tertiary"],
            hover_color=colors["accent"],
            text_color=colors["text_primary"]
        )
        export_button.pack(pady=5, fill="x")
        
        # Sezione Info App
        info_section = tk.Frame(container, bg=colors["bg_secondary"], padx=20, pady=15)
        info_section.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            info_section,
            text="Informazioni Applicazione",
            font=("Segoe UI", 14, "bold"),
            bg=colors["bg_secondary"],
            fg=colors["accent"]
        ).pack(anchor="w", pady=(0, 10))
        
        tk.Label(
            info_section,
            text="League of Legends Wallet Tracker",
            font=("Segoe UI", 12, "bold"),
            bg=colors["bg_secondary"],
            fg=colors["text_primary"]
        ).pack(anchor="w")
        
        tk.Label(
            info_section,
            text="Versione 2.5 - Edizione Migliorata",
            font=("Segoe UI", 10),
            bg=colors["bg_secondary"],
            fg=colors["text_secondary"]
        ).pack(anchor="w", pady=(2, 0))
        
        tk.Label(
            info_section,
            text="© 2025 Ahristogatti",
            font=("Segoe UI", 9),
            bg=colors["bg_secondary"],
            fg=colors["text_secondary"]
        ).pack(anchor="w", pady=(5, 0))
    
    def create_footer(self):
        """Crea il footer con i controlli principali"""
        colors = self.themes[self.current_theme]
        
        footer_frame = tk.Frame(self.main_container, bg=colors["bg_secondary"], padx=15, pady=10)
        footer_frame.pack(fill="x", pady=(5, 0))
        
        # Pulsante aggiorna
        self.refresh_button = ModernButton(
            footer_frame,
            text="Aggiorna Dati",
            command=self.update_data,
            bg_color=colors["success"],
            hover_color="#45A049",
            text_color="#FFFFFF"
        )
        self.refresh_button.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Pulsante auto-refresh
        auto_text = "ON" if self.auto_refresh_enabled else "OFF"
        self.auto_refresh_button = ModernButton(
            footer_frame,
            text=f"Auto-Refresh: {auto_text}",
            command=self.toggle_auto_refresh,
            bg_color=colors["info"],
            hover_color="#1976D2",
            text_color="#FFFFFF"
        )
        self.auto_refresh_button.pack(side="left", padx=10, fill="x", expand=True)
        
        # Pulsante tema
        theme_text = "Tema Scuro" if self.current_theme == "light" else "Tema Chiaro"
        self.theme_button = ModernButton(
            footer_frame,
            text=theme_text,
            command=self.toggle_theme,
            bg_color=colors["warning"],
            hover_color="#F57C00",
            text_color="#FFFFFF"
        )
        self.theme_button.pack(side="right", padx=(10, 0), fill="x", expand=True)
    
    def create_status_bar(self):
        """Crea la barra di stato"""
        colors = self.themes[self.current_theme]
        
        self.status_frame = tk.Frame(self.root, bg=colors["bg_tertiary"], height=30)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        
        # Status principale
        self.status_var = tk.StringVar(value="Pronto")
        self.status_label = tk.Label(
            self.status_frame,
            textvariable=self.status_var,
            bg=colors["bg_tertiary"],
            fg=colors["text_primary"],
            font=("Segoe UI", 9),
            anchor="w",
            padx=10
        )
        self.status_label.pack(side="left", fill="y")
        
        # API Status
        self.api_status_var = tk.StringVar(value="API: Pronto")
        self.api_status_label = tk.Label(
            self.status_frame,
            textvariable=self.api_status_var,
            bg=colors["bg_tertiary"],
            fg=colors["success"],
            font=("Segoe UI", 9),
            anchor="center",
            padx=10
        )
        self.api_status_label.pack(side="right", fill="y")
    
    def setup_auto_refresh(self):
        """Configura l'auto-refresh"""
        def auto_refresh():
            if self.auto_refresh_enabled:
                self.update_data()
            self.root.after(self.refresh_interval, auto_refresh)
        
        self.root.after(self.refresh_interval, auto_refresh)
    
    def update_data(self):
        """Aggiorna i dati delle valute"""
        self.status_var.set("Aggiornamento in corso...")
        self.refresh_button.button.configure(text="Aggiornando...")
        self.refresh_button.button.configure(state="disabled")
        
        threading.Thread(target=self._fetch_data_thread, daemon=True).start()
    
    def _fetch_data_thread(self):
        """Thread per il recupero dati"""
        try:
            data = get_balance()
            self.root.after(0, lambda d=data: self._update_ui_with_data(d))
            
        except RiotAPIError as e:
            error_msg = f"Errore API: {e}"
            self.root.after(0, lambda msg=error_msg: self._handle_api_error(msg))
            
        except Exception as e:
            error_msg = f"Errore: {e}"
            self.root.after(0, lambda msg=error_msg: self._handle_general_error(msg))
            
        finally:
            self.root.after(0, self._restore_refresh_button)
    
    def _update_ui_with_data(self, data):
        """Aggiorna l'interfaccia con i nuovi dati"""
        from datetime import datetime
        
        # Memorizza dati precedenti
        old_data = self._previous_data.copy()
        self._previous_data = data
        
        # Aggiorna le card delle valute
        for currency_id, card in self.currency_cards.items():
            value = data.get(currency_id, 0)
            card.update_value(value, animate=True)
            
            # Aggiorna dati grafico
            current_time = datetime.now()
            self.chart_data[currency_id]['values'].append(value)
            self.chart_data[currency_id]['times'].append(current_time)
            
            # Mantieni solo gli ultimi 50 punti
            if len(self.chart_data[currency_id]['values']) > 50:
                self.chart_data[currency_id]['values'].pop(0)
                self.chart_data[currency_id]['times'].pop(0)
        
        # Aggiorna sommario
        self.rp_summary_label.configure(text=f"{data.get('RP', 0):,}".replace(",", "."))
        self.be_summary_label.configure(text=f"{data.get('lol_blue_essence', 0):,}".replace(",", "."))
        
        # Aggiorna timestamp
        current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.last_update_label.configure(text=current_time)
        
        # Mostra notifiche per cambiamenti significativi
        self._check_for_significant_changes(old_data, data)
        
        # Aggiorna grafico se visibile
        if hasattr(self, 'chart_canvas') and self.notebook.index("current") == 1:
            self.update_chart()
        
        # Aggiorna status
        self.status_var.set(f"Ultimo aggiornamento: {datetime.now().strftime('%H:%M:%S')}")
        self.api_status_var.set("API: Connesso")
        self.api_status_label.configure(fg=self.themes[self.current_theme]["success"])
        
        self.logger.info("Dati aggiornati con successo")
    
    def _check_for_significant_changes(self, old_data, new_data):
        """Verifica cambiamenti significativi e mostra notifiche"""
        if not old_data:
            return
        
        # Controlla RP e BE per cambiamenti significativi
        currencies_to_check = [
            ("RP", "Riot Points", 100),
            ("lol_blue_essence", "Blue Essence", 1000)
        ]
        
        for currency_id, name, threshold in currencies_to_check:
            old_val = old_data.get(currency_id, 0)
            new_val = new_data.get(currency_id, 0)
            diff = new_val - old_val
            
            if abs(diff) >= threshold:
                self._show_notification(
                    f"{name} {'aumentati' if diff > 0 else 'diminuiti'}!",
                    f"Variazione: {diff:+,}".replace(",", "."),
                    "success" if diff > 0 else "warning"
                )
    
    def _handle_api_error(self, error_message):
        """Gestisce errori API"""
        self.status_var.set("Errore nell'aggiornamento")
        self.api_status_var.set("API: Errore")
        self.api_status_label.configure(fg=self.themes[self.current_theme]["error"])
        
        messagebox.showerror("Errore API", error_message)
        self.logger.error(error_message)
    
    def _handle_general_error(self, error_message):
        """Gestisce errori generali"""
        self.status_var.set("Errore imprevisto")
        self.api_status_var.set("API: Errore")
        self.api_status_label.configure(fg=self.themes[self.current_theme]["error"])
        
        messagebox.showerror("Errore", error_message)
        self.logger.error(error_message)
    
    def _restore_refresh_button(self):
        """Ripristina il pulsante refresh"""
        self.refresh_button.button.configure(
            text="Aggiorna Dati",
            state="normal"
        )
    
    def update_chart(self, event=None):
        """Aggiorna il grafico"""
        if not MATPLOTLIB_AVAILABLE or not hasattr(self, 'ax'):
            return
        
        # Ottieni la valuta selezionata
        selected_name = self.selected_currency_var.get()
        if not selected_name:
            return
        
        # Trova l'ID della valuta
        currency_id = None
        currency_color = "#C8AA6E"
        
        for cid, color, name, _ in self.currency_config:
            if name == selected_name:
                currency_id = cid
                currency_color = color
                break
        
        if not currency_id or not self.chart_data[currency_id]['values']:
            # Mostra messaggio se non ci sono dati
            self.ax.clear()
            self.ax.text(
                0.5, 0.5,
                "Nessun dato disponibile\n\nAggiorna il portafoglio per visualizzare il grafico",
                horizontalalignment='center',
                verticalalignment='center',
                transform=self.ax.transAxes,
                color=self.themes[self.current_theme]["text_secondary"],
                fontsize=12
            )
        else:
            # Disegna il grafico
            self.ax.clear()
            
            times = self.chart_data[currency_id]['times']
            values = self.chart_data[currency_id]['values']
            
            # Linea principale
            self.ax.plot(
                times, values,
                color=currency_color,
                linewidth=2.5,
                marker='o',
                markersize=4,
                alpha=0.8
            )
            
            # Area sotto la curva
            self.ax.fill_between(
                times, values,
                alpha=0.3,
                color=currency_color
            )
            
            # Titolo e etichette
            self.ax.set_title(
                f"Andamento {selected_name}",
                color=self.themes[self.current_theme]["accent"],
                fontsize=14,
                fontweight='bold',
                pad=20
            )
            
            self.ax.set_xlabel("Tempo", color=self.themes[self.current_theme]["text_primary"])
            self.ax.set_ylabel("Valore", color=self.themes[self.current_theme]["text_primary"])
            
            # Formattazione degli assi
            if len(times) > 1:
                self.ax.tick_params(axis='x', rotation=45)
                
            # Grid sottile
            self.ax.grid(True, alpha=0.3, color=self.themes[self.current_theme]["text_secondary"])
        
        # Aggiorna colori del grafico
        colors = self.themes[self.current_theme]
        self.ax.set_facecolor(colors["bg_secondary"])
        self.ax.tick_params(colors=colors["text_primary"])
        
        for spine in self.ax.spines.values():
            spine.set_color(colors["text_secondary"])
        
        # Ridisegna
        self.fig.tight_layout()
        self.chart_canvas.draw()
    
    def toggle_auto_refresh(self):
        """Attiva/disattiva auto-refresh"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        
        status = "ON" if self.auto_refresh_enabled else "OFF"
        self.auto_refresh_button.configure_text(f"Auto-Refresh: {status}")
        
        self.logger.info(f"Auto-refresh: {status}")
    
    def toggle_theme(self):
        """Cambia tema"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        
        # Ricrea gli stili
        self.create_styles()
        
        # Aggiorna l'interfaccia
        self._update_theme_colors()
        
        # Aggiorna testo pulsante
        theme_text = "Tema Scuro" if self.current_theme == "light" else "Tema Chiaro"
        self.theme_button.configure_text(theme_text)
        
        self.logger.info(f"Tema cambiato a: {self.current_theme}")
    
    def _update_theme_colors(self):
        """Aggiorna i colori del tema in tutta l'interfaccia"""
        colors = self.themes[self.current_theme]
        
        # Aggiorna finestra principale
        self.root.configure(bg=colors["bg_primary"])
        self.main_container.configure(bg=colors["bg_primary"])
        
        # Aggiorna ricorsivamente tutti i widget
        def update_widget_colors(widget):
            if hasattr(widget, 'configure'):
                try:
                    widget_class = widget.__class__.__name__
                    
                    if 'Frame' in widget_class or 'Canvas' in widget_class:
                        widget.configure(bg=colors["bg_primary"])
                    elif 'Label' in widget_class:
                        widget.configure(bg=colors["bg_primary"])
                            
                except Exception:
                    pass
            
            try:
                for child in widget.winfo_children():
                    update_widget_colors(child)
            except Exception:
                pass
        
        update_widget_colors(self.root)
        
        # Aggiorna specificamente i canvas scrollabili se esistono
        if hasattr(self, 'wallet_canvas'):
            self.wallet_canvas.configure(bg=colors["bg_primary"])
        
        # Aggiorna le currency cards
        card_bg = "#1a1a1a" if self.current_theme == "dark" else "#f0f0f0"
        for card in self.currency_cards.values():
            try:
                card._change_bg_recursive(card_bg)
            except Exception:
                pass
        
        # Aggiorna grafico se esiste
        if hasattr(self, 'fig') and hasattr(self, 'ax'):
            self.fig.patch.set_facecolor(colors["bg_secondary"])
            self.ax.set_facecolor(colors["bg_secondary"])
            self.update_chart()
    
    def update_refresh_interval(self):
        """Aggiorna intervallo refresh"""
        self.refresh_interval = self.interval_var.get() * 1000
        self.logger.info(f"Intervallo aggiornamento: {self.interval_var.get()}s")
    
    def export_data(self):
        """Esporta i dati in CSV"""
        try:
            import csv
            from datetime import datetime
            
            # Selezione file
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Salva dati come...",
                initialname=f"lol_wallet_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header
                writer.writerow(['Timestamp', 'Data', 'Ora', 'Valuta', 'Valore'])
                
                # Dati
                for currency_id, chart_data in self.chart_data.items():
                    currency_name = next(
                        (name for cid, _, name, _ in self.currency_config if cid == currency_id),
                        currency_id
                    )
                    
                    for i, value in enumerate(chart_data['values']):
                        timestamp = chart_data['times'][i]
                        writer.writerow([
                            timestamp.isoformat(),
                            timestamp.strftime('%Y-%m-%d'),
                            timestamp.strftime('%H:%M:%S'),
                            currency_name,
                            value
                        ])
            
            messagebox.showinfo("Esportazione completata", f"Dati esportati in:\n{filename}")
            self.logger.info(f"Dati esportati in {filename}")
            
        except Exception as e:
            error_msg = f"Errore durante l'esportazione: {e}"
            messagebox.showerror("Errore", error_msg)
            self.logger.error(error_msg)
    
    def _show_notification(self, title, message, notification_type="info"):
        """Mostra una notifica toast"""
        colors = self.themes[self.current_theme]
        
        # Colori per tipo di notifica
        type_colors = {
            "info": colors["info"],
            "success": colors["success"],
            "warning": colors["warning"],
            "error": colors["error"]
        }
        
        notification_color = type_colors.get(notification_type, colors["info"])
        
        # Finestra di notifica
        toast = tk.Toplevel(self.root)
        toast.overrideredirect(True)
        toast.attributes('-topmost', True)
        
        # Posizione (angolo superiore destro)
        x = self.root.winfo_rootx() + self.root.winfo_width() - 320
        y = self.root.winfo_rooty() + 50
        toast.geometry(f"300x80+{x}+{y}")
        
        # Stile notifica
        toast.configure(bg=notification_color, bd=1, relief="solid")
        
        # Frame contenuto
        content_frame = tk.Frame(toast, bg=notification_color)
        content_frame.pack(fill="both", expand=True, padx=10, pady=8)
        
        # Titolo
        tk.Label(
            content_frame,
            text=title,
            font=("Segoe UI", 11, "bold"),
            bg=notification_color,
            fg="white"
        ).pack(anchor="w")
        
        # Messaggio
        tk.Label(
            content_frame,
            text=message,
            font=("Segoe UI", 9),
            bg=notification_color,
            fg="white",
            wraplength=280
        ).pack(anchor="w", pady=(2, 0))
        
        # Auto-chiusura dopo 3 secondi
        toast.after(3000, toast.destroy)
        
        # Effetto fade-in/fade-out (se supportato)
        try:
            toast.attributes('-alpha', 0.9)
        except:
            pass
    
    def on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        if messagebox.askokcancel("Uscita", "Vuoi davvero chiudere l'applicazione?"):
            self.logger.info("Chiusura applicazione")
            self.root.destroy()


def main():
    """Funzione principale"""
    try:
        root = tk.Tk()
        app = LolWalletApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Errore critico: {e}")
        logging.error(f"Errore critico nell'avvio: {e}")


if __name__ == "__main__":
    main()