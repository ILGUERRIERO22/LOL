import tkinter as tk
from tkinter import ttk, messagebox, font, filedialog
from Riot_API import get_current_ranked_stats, RiotAPIError
import os
import threading
import json
from datetime import datetime
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Costanti per il tema colori Nord migliorato
COLORS = {
    "background": "#2E3440",
    "surface": "#3B4252",
    "surface_alt": "#4C566A", 
    "surface_light": "#5E81AC",
    "accent": "#88C0D0",
    "accent_hover": "#81A1C1",
    "text": "#ECEFF4",
    "text_secondary": "#D8DEE9",
    "text_muted": "#616E88",
    "error": "#BF616A",
    "success": "#A3BE8C",
    "warning": "#EBCB8B",
    "info": "#5E81AC",
    "highlight": "#5E81AC",
    "highlight_alt": "#81A1C1",
    "border": "#434C5E",
    "shadow": "#242832"
}

# Mappe per icone e colori leghe migliorati
TIER_COLORS = {
    "IRON": "#795548",
    "BRONZE": "#8D6E63",
    "SILVER": "#90A4AE",
    "GOLD": "#FFB300",
    "PLATINUM": "#00ACC1",
    "EMERALD": "#4CAF50",
    "DIAMOND": "#03DAC6",
    "MASTER": "#9C27B0",
    "GRANDMASTER": "#F44336",
    "CHALLENGER": "#FF6F00",
    "UNRANKED": "#616E88"
}

def calculate_winrate(wins, losses):
    """Calcola il winrate in base a vittorie e sconfitte."""
    total_games = wins + losses
    return (wins / total_games) * 100 if total_games > 0 else 0

def get_winrate_color(winrate):
    """Restituisce un colore appropriato in base al winrate"""
    if winrate >= 65:
        return COLORS["success"]
    elif winrate >= 55:
        return COLORS["warning"] 
    elif winrate >= 45:
        return COLORS["text"]
    else:
        return COLORS["error"]

def format_tier_display(tier, division, lp):
    """Formatta la visualizzazione del tier"""
    if tier in ["MASTER", "GRANDMASTER", "CHALLENGER"]:
        return f"{tier.title()} {lp} LP"
    elif tier == "UNRANKED":
        return "Non Classificato"
    else:
        return f"{tier.title()} {division} {lp} LP"

class LoadingDialog:
    """Dialog di caricamento animato"""
    
    def __init__(self, parent, message="Caricamento..."):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Attendere")
        self.dialog.geometry("300x150")
        self.dialog.configure(bg=COLORS["surface"])
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centra la finestra
        self.dialog.geometry("+{}+{}".format(
            int(parent.winfo_rootx() + parent.winfo_width()/2 - 150),
            int(parent.winfo_rooty() + parent.winfo_height()/2 - 75)
        ))
        
        # Contenuto
        frame = tk.Frame(self.dialog, bg=COLORS["surface"])
        frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.label = tk.Label(
            frame, 
            text=message,
            font=("Helvetica", 12),
            bg=COLORS["surface"],
            fg=COLORS["text"]
        )
        self.label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=10)
        self.progress.start()
        
        # Disabilita la chiusura
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
    
    def close(self):
        """Chiude il dialog"""
        self.progress.stop()
        self.dialog.destroy()

class ModernTooltip:
    """Tooltip moderno e animato"""
    
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip = None
        self.timer = None
        
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
        self.widget.bind("<Motion>", self.on_motion)
    
    def on_enter(self, event=None):
        self.cancel_timer()
        self.timer = self.widget.after(self.delay, self.show_tooltip)
    
    def on_leave(self, event=None):
        self.cancel_timer()
        self.hide_tooltip()
    
    def on_motion(self, event=None):
        if self.tooltip:
            self.hide_tooltip()
        self.cancel_timer()
        self.timer = self.widget.after(self.delay, self.show_tooltip)
    
    def cancel_timer(self):
        if self.timer:
            self.widget.after_cancel(self.timer)
            self.timer = None
    
    def show_tooltip(self):
        if self.tooltip:
            return
            
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        
        self.tooltip = tk.Toplevel()
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.configure(bg=COLORS["shadow"])
        
        # Frame interno con bordi arrotondati (simulati)
        inner_frame = tk.Frame(
            self.tooltip,
            bg=COLORS["surface_alt"],
            relief="solid",
            borderwidth=1
        )
        inner_frame.pack(padx=2, pady=2)
        
        label = tk.Label(
            inner_frame,
            text=self.text,
            bg=COLORS["surface_alt"],
            fg=COLORS["text"],
            font=("Helvetica", 9),
            justify="left",
            wraplength=200
        )
        label.pack(padx=8, pady=6)
        
        self.tooltip.geometry(f"+{x}+{y}")
        
        # Animazione di fade in (semplificata)
        self.tooltip.attributes("-alpha", 0.0)
        self.fade_in()
    
    def fade_in(self, alpha=0.0):
        alpha += 0.1
        if alpha >= 0.9:
            alpha = 0.9
        self.tooltip.attributes("-alpha", alpha)
        if alpha < 0.9:
            self.tooltip.after(30, lambda: self.fade_in(alpha))
    
    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class StatCard(tk.Frame):
    """Widget card per statistiche personalizzato"""
    
    def __init__(self, parent, title, value, subtitle="", color=None, **kwargs):
        super().__init__(parent, bg=COLORS["surface"], relief="raised", 
                        borderwidth=1, **kwargs)
        
        self.configure(highlightbackground=COLORS["border"], highlightthickness=1)
        
        # Padding interno
        inner_frame = tk.Frame(self, bg=COLORS["surface"])
        inner_frame.pack(fill="both", expand=True, padx=15, pady=12)
        
        # Titolo
        title_label = tk.Label(
            inner_frame,
            text=title,
            font=("Helvetica", 10),
            bg=COLORS["surface"],
            fg=COLORS["text_secondary"]
        )
        title_label.pack(anchor="w")
        
        # Valore principale
        value_color = color if color else COLORS["accent"]
        value_label = tk.Label(
            inner_frame,
            text=str(value),
            font=("Helvetica", 18, "bold"),
            bg=COLORS["surface"],
            fg=value_color
        )
        value_label.pack(anchor="w", pady=(2, 0))
        
        # Sottotitolo se presente
        if subtitle:
            subtitle_label = tk.Label(
                inner_frame,
                text=subtitle,
                font=("Helvetica", 8),
                bg=COLORS["surface"],
                fg=COLORS["text_muted"]
            )
            subtitle_label.pack(anchor="w")

class RankStatsApp:
    """Classe principale dell'applicazione migliorata"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("League of Legends - Statistiche Rank")
        self.root.configure(bg=COLORS["background"])
        self.root.minsize(850, 650)
        self.root.geometry("950x700")
        
        # Icona dell'applicazione (se disponibile)
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # Variabili di stato
        self.data = {}
        self.loading_dialog = None
        
        # Font personalizzati
        self.setup_fonts()
        
        # Configurazione degli stili
        self.configure_styles()
        
        # Carica i dati iniziali
        self.load_data_async()
    
    def setup_fonts(self):
        """Configura i font personalizzati"""
        try:
            self.title_font = font.Font(family="Segoe UI", size=22, weight="bold")
            self.header_font = font.Font(family="Segoe UI", size=13, weight="bold")
            self.normal_font = font.Font(family="Segoe UI", size=10)
            self.small_font = font.Font(family="Segoe UI", size=9)
        except:
            # Fallback per sistemi senza Segoe UI
            self.title_font = font.Font(family="Helvetica", size=20, weight="bold")
            self.header_font = font.Font(family="Helvetica", size=12, weight="bold")
            self.normal_font = font.Font(family="Helvetica", size=10)
            self.small_font = font.Font(family="Helvetica", size=9)
    
    def configure_styles(self):
        """Configura gli stili migliorati per l'interfaccia"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Stile Treeview migliorato
        style.configure(
            "Modern.Treeview",
            background=COLORS["surface"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["surface"],
            font=self.normal_font,
            rowheight=35,
            borderwidth=0
        )
        
        style.configure(
            "Modern.Treeview.Heading",
            background=COLORS["surface_alt"],
            foreground=COLORS["text"],
            font=self.header_font,
            relief="flat",
            borderwidth=1
        )
        
        style.map(
            "Modern.Treeview",
            background=[("selected", COLORS["highlight"])],
            foreground=[("selected", COLORS["text"])]
        )
        
        style.map(
            "Modern.Treeview.Heading",
            background=[("active", COLORS["surface_light"])]
        )
        
        # Stile pulsanti moderni
        style.configure(
            "Modern.TButton",
            background=COLORS["highlight"],
            foreground=COLORS["text"],
            font=self.normal_font,
            relief="flat",
            borderwidth=0,
            focuscolor="none",
            padding=(12, 8)
        )
        
        style.map(
            "Modern.TButton",
            background=[
                ("active", COLORS["highlight_alt"]),
                ("pressed", COLORS["surface_light"])
            ],
            foreground=[("active", COLORS["text"])]
        )
        
        # Stile progress bar
        style.configure(
            "Modern.Horizontal.TProgressbar",
            background=COLORS["accent"],
            troughcolor=COLORS["surface_alt"],
            borderwidth=0,
            lightcolor=COLORS["accent"],
            darkcolor=COLORS["accent"]
        )
    
    def load_data_async(self):
        """Carica i dati in modo asincrono"""
        self.loading_dialog = LoadingDialog(self.root, "Caricamento statistiche...")
        
        def load_thread():
            try:
                self.data = get_current_ranked_stats()
                self.root.after(0, self.on_data_loaded)
            except RiotAPIError as e:
                self.root.after(0, lambda: self.on_data_error(f"Errore API Riot: {e}"))
            except Exception as e:
                self.root.after(0, lambda: self.on_data_error(f"Errore sconosciuto: {e}"))
        
        thread = threading.Thread(target=load_thread, daemon=True)
        thread.start()
    
    def on_data_loaded(self):
        """Callback quando i dati sono stati caricati"""
        if self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None
        
        self.build_ui()
    
    def on_data_error(self, error_message):
        """Callback quando si verifica un errore nel caricamento"""
        if self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None
        
        messagebox.showerror("Errore", error_message)
        self.build_error_ui()
    
    def build_ui(self):
        """Costruisce l'interfaccia utente principale migliorata"""
        # Pulizia precedente interfaccia
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Scrollable main frame
        main_canvas = tk.Canvas(self.root, bg=COLORS["background"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg=COLORS["background"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        main_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Contenuto principale con padding
        content_frame = tk.Frame(scrollable_frame, bg=COLORS["background"])
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header migliorato
        self.create_modern_header(content_frame)
        
        # Statistiche card
        self.create_stats_cards(content_frame)
        
        # Tabella dati migliorata
        self.create_modern_table(content_frame)
        
        # Footer migliorato
        self.create_modern_footer(content_frame)
        
        # Bind mouse wheel per scroll
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.root.bind_all("<MouseWheel>", _on_mousewheel)
    
    def build_error_ui(self):
        """Costruisce un'interfaccia di errore"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        error_frame = tk.Frame(self.root, bg=COLORS["background"])
        error_frame.pack(fill="both", expand=True, padx=50, pady=50)
        
        # Icona di errore (emoji)
        error_icon = tk.Label(
            error_frame,
            text="⚠️",
            font=("Arial", 48),
            bg=COLORS["background"],
            fg=COLORS["error"]
        )
        error_icon.pack(pady=20)
        
        # Messaggio
        error_label = tk.Label(
            error_frame,
            text="Impossibile caricare le statistiche",
            font=self.header_font,
            bg=COLORS["background"],
            fg=COLORS["text"]
        )
        error_label.pack(pady=10)
        
        # Pulsante retry
        retry_button = ttk.Button(
            error_frame,
            text="Riprova",
            style="Modern.TButton",
            command=self.load_data_async
        )
        retry_button.pack(pady=20)
    
    def create_modern_header(self, parent):
        """Crea un header moderno"""
        header_frame = tk.Frame(parent, bg=COLORS["background"])
        header_frame.pack(fill="x", pady=(0, 30))
        
        # Titolo principale
        title_label = tk.Label(
            header_frame,
            text="League of Legends",
            font=self.title_font,
            bg=COLORS["background"],
            fg=COLORS["accent"]
        )
        title_label.pack()
        
        # Sottotitolo
        subtitle_label = tk.Label(
            header_frame,
            text="Dashboard Statistiche Classificate",
            font=self.normal_font,
            bg=COLORS["background"],
            fg=COLORS["text_secondary"]
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Data ultimo aggiornamento
        last_updated = self.data.get("lastUpdated")
        if not last_updated:
            last_updated = datetime.now().strftime("%d/%m/%Y alle %H:%M")
        
        update_label = tk.Label(
            header_frame,
            text=f"Ultimo aggiornamento: {last_updated}",
            font=self.small_font,
            bg=COLORS["background"],
            fg=COLORS["text_muted"]
        )
        update_label.pack(pady=(10, 0))
        
        # Linea decorativa
        separator_frame = tk.Frame(header_frame, height=2, bg=COLORS["accent"])
        separator_frame.pack(fill="x", pady=15)
    
    def create_stats_cards(self, parent):
        """Crea le card delle statistiche riassuntive"""
        cards_frame = tk.Frame(parent, bg=COLORS["background"])
        cards_frame.pack(fill="x", pady=(0, 25))
        
        # Calcola statistiche aggregate
        stats = self.calculate_aggregate_stats()
        
        # Grid layout per le cards
        cards_frame.grid_columnconfigure(0, weight=1, uniform="card")
        cards_frame.grid_columnconfigure(1, weight=1, uniform="card")
        cards_frame.grid_columnconfigure(2, weight=1, uniform="card")
        cards_frame.grid_columnconfigure(3, weight=1, uniform="card")
        
        # Card Partite Totali
        total_card = StatCard(
            cards_frame,
            "Partite Totali",
            stats["total_games"],
            f"{stats['total_wins']}W - {stats['total_losses']}L"
        )
        total_card.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        # Card Winrate
        winrate_color = get_winrate_color(stats["winrate"])
        winrate_card = StatCard(
            cards_frame,
            "Winrate Complessivo",
            f"{stats['winrate']:.1f}%",
            f"su {stats['total_games']} partite",
            color=winrate_color
        )
        winrate_card.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Card Rank Principale
        main_rank_color = TIER_COLORS.get(stats["main_tier"], COLORS["text"])
        rank_card = StatCard(
            cards_frame,
            "Rank Principale",
            stats["main_rank"],
            stats["main_queue"],
            color=main_rank_color
        )
        rank_card.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        
        # Card LP
        lp_card = StatCard(
            cards_frame,
            "League Points",
            f"{stats['main_lp']} LP",
            stats["main_tier"]
        )
        lp_card.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        
        # Aggiungi tooltips
        ModernTooltip(total_card, "Somma di tutte le partite classificate giocate")
        ModernTooltip(winrate_card, "Percentuale di vittorie su tutte le code classificate")
        ModernTooltip(rank_card, "Il rank più alto tra tutte le code attive")
        ModernTooltip(lp_card, "League Points del rank principale")
    
    def calculate_aggregate_stats(self):
        """Calcola le statistiche aggregate"""
        queue_data = self.data.get("queueMap", {})
        
        total_wins = 0
        total_losses = 0
        main_tier = "UNRANKED"
        main_division = ""
        main_lp = 0
        main_queue = "Nessuno"
        main_rank = "Non Classificato"
        
        # Ordine di priorità delle tier
        tier_order = {
            "IRON": 1, "BRONZE": 2, "SILVER": 3, "GOLD": 4,
            "PLATINUM": 5, "EMERALD": 6, "DIAMOND": 7,
            "MASTER": 8, "GRANDMASTER": 9, "CHALLENGER": 10
        }
        
        division_order = {"IV": 1, "III": 2, "II": 3, "I": 4}
        
        queue_names = {
            "RANKED_SOLO_5x5": "Solo/Duo",
            "RANKED_FLEX_SR": "Flex 5v5",
            "RANKED_TFT": "TFT",
            "RANKED_TFT_DOUBLE_UP": "TFT Duo"
        }
        
        highest_score = 0
        
        for queue_code, stats in queue_data.items():
            if not stats or queue_code not in queue_names:
                continue
            
            wins = stats.get("wins", 0)
            losses = stats.get("losses", 0)
            tier = stats.get("tier", "UNRANKED")
            division = stats.get("division", "IV")
            lp = stats.get("leaguePoints", 0)
            
            total_wins += wins
            total_losses += losses
            
            # Calcola score per determinare rank principale
            tier_score = tier_order.get(tier, 0) * 1000
            div_score = division_order.get(division, 1) * 10
            total_score = tier_score + div_score + (lp / 100)
            
            if total_score > highest_score:
                highest_score = total_score
                main_tier = tier
                main_division = division
                main_lp = lp
                main_queue = queue_names[queue_code]
                main_rank = format_tier_display(tier, division, lp)
        
        total_games = total_wins + total_losses
        winrate = calculate_winrate(total_wins, total_losses)
        
        return {
            "total_games": total_games,
            "total_wins": total_wins,
            "total_losses": total_losses,
            "winrate": winrate,
            "main_tier": main_tier,
            "main_division": main_division,
            "main_lp": main_lp,
            "main_queue": main_queue,
            "main_rank": main_rank
        }
    
    def create_modern_table(self, parent):
        """Crea una tabella moderna e migliorata"""
        table_frame = tk.Frame(parent, bg=COLORS["surface"], relief="raised", borderwidth=1)
        table_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Header della tabella
        header_frame = tk.Frame(table_frame, bg=COLORS["surface"])
        header_frame.pack(fill="x", padx=15, pady=(15, 10))
        
        header_label = tk.Label(
            header_frame,
            text="📊 Dettaglio Code Classificate",
            font=self.header_font,
            bg=COLORS["surface"],
            fg=COLORS["accent"]
        )
        header_label.pack(side="left")
        
        # Contenuto tabella
        table_content = tk.Frame(table_frame, bg=COLORS["surface"])
        table_content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Configurazione colonne
        columns = ("queue", "rank", "games", "winrate", "trend")
        column_names = {
            "queue": "Coda",
            "rank": "Classificazione", 
            "games": "Partite (W/L)",
            "winrate": "Winrate",
            "trend": "Tendenza"
        }
        
        # Treeview migliorato
        tree = ttk.Treeview(
            table_content,
            columns=columns,
            show="headings",
            style="Modern.Treeview"
        )
        
        # Configurazione colonne
        tree.column("queue", width=120, anchor="center")
        tree.column("rank", width=200, anchor="center")
        tree.column("games", width=120, anchor="center")
        tree.column("winrate", width=100, anchor="center")
        tree.column("trend", width=120, anchor="center")
        
        # Headers
        for col in columns:
            tree.heading(col, text=column_names[col], anchor="center")
        
        # Inserimento dati
        queue_data = self.data.get("queueMap", {})
        queue_names = {
            "RANKED_SOLO_5x5": "🎯 Solo/Duo",
            "RANKED_FLEX_SR": "👥 Flex 5v5",
            "RANKED_TFT": "♟️ TFT",
            "RANKED_TFT_DOUBLE_UP": "👫 TFT Duo"
        }
        
        for queue_code, queue_name in queue_names.items():
            stats = queue_data.get(queue_code)
            if not stats:
                continue
            
            wins = stats.get("wins", 0)
            losses = stats.get("losses", 0)
            tier = stats.get("tier", "UNRANKED")
            division = stats.get("division", "")
            lp = stats.get("leaguePoints", 0)
            
            # Calcoli
            total_games = wins + losses
            winrate = calculate_winrate(wins, losses)
            
            # Trend simulato (in un'app reale verrebbe dall'API)
            if winrate >= 60:
                trend = "📈 Ottimo"
            elif winrate >= 50:
                trend = "➡️ Stabile"
            else:
                trend = "📉 Difficile"
            
            # Formattazione
            rank_display = format_tier_display(tier, division, lp)
            games_display = f"{total_games} ({wins}W/{losses}L)"
            winrate_display = f"{winrate:.1f}%"
            
            # Inserimento riga
            item = tree.insert("", "end", values=(
                queue_name,
                rank_display,
                games_display,
                winrate_display,
                trend
            ))
            
            # Tags per colorazione
            tree.set(item, "queue", queue_name)
        
        # Scrollbar
        scrollbar_tree = ttk.Scrollbar(table_content, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar_tree.set)
        
        # Layout
        tree.pack(side="left", fill="both", expand=True)
        scrollbar_tree.pack(side="right", fill="y")
    
    def create_modern_footer(self, parent):
        """Crea un footer moderno con pulsanti migliorati"""
        footer_frame = tk.Frame(parent, bg=COLORS["background"])
        footer_frame.pack(fill="x", pady=20)
        
        # Separatore
        separator = tk.Frame(footer_frame, height=1, bg=COLORS["border"])
        separator.pack(fill="x", pady=(0, 15))
        
        # Layout footer
        left_frame = tk.Frame(footer_frame, bg=COLORS["background"])
        left_frame.pack(side="left")
        
        right_frame = tk.Frame(footer_frame, bg=COLORS["background"])
        right_frame.pack(side="right")
        
        # Info versione a sinistra
        version_label = tk.Label(
            left_frame,
            text="LoL Stats v2.0.0 | Powered by Riot Games API",
            font=self.small_font,
            bg=COLORS["background"],
            fg=COLORS["text_muted"]
        )
        version_label.pack(side="left")
        
        # Pulsanti a destra
        buttons = [
            ("💾 Esporta JSON", self.export_json),
            ("📄 Esporta CSV", self.export_csv),
            ("🔄 Aggiorna", self.refresh_data)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(
                right_frame,
                text=text,
                style="Modern.TButton",
                command=command
            )
            btn.pack(side="right", padx=(10, 0))
            
            # Tooltip per i pulsanti
            if "Esporta JSON" in text:
                ModernTooltip(btn, "Esporta tutti i dati in formato JSON")
            elif "Esporta CSV" in text:
                ModernTooltip(btn, "Esporta statistiche in formato CSV")
            elif "Aggiorna" in text:
                ModernTooltip(btn, "Aggiorna le statistiche dall'API Riot")
    
    def refresh_data(self):
        """Aggiorna i dati con feedback migliorato"""
        self.load_data_async()
    
    def export_csv(self):
        """Esporta i dati in formato CSV migliorato"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("File CSV", "*.csv"), ("Tutti i file", "*.*")],
                initialname=f"lol_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return
            
            import csv
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Header
                writer.writerow([
                    'Coda', 'Tier', 'Divisione', 'LP', 'Vittorie', 
                    'Sconfitte', 'Partite Totali', 'Winrate'
                ])
                
                # Dati
                queue_data = self.data.get("queueMap", {})
                queue_names = {
                    "RANKED_SOLO_5x5": "Solo/Duo",
                    "RANKED_FLEX_SR": "Flex 5v5",
                    "RANKED_TFT": "TFT",
                    "RANKED_TFT_DOUBLE_UP": "TFT Duo"
                }
                
                for queue_code, queue_name in queue_names.items():
                    stats = queue_data.get(queue_code)
                    if not stats:
                        continue
                    
                    wins = stats.get("wins", 0)
                    losses = stats.get("losses", 0)
                    tier = stats.get("tier", "UNRANKED")
                    division = stats.get("division", "")
                    lp = stats.get("leaguePoints", 0)
                    
                    total_games = wins + losses
                    winrate = calculate_winrate(wins, losses)
                    
                    writer.writerow([
                        queue_name, tier, division, lp, wins,
                        losses, total_games, f"{winrate:.1f}%"
                    ])
            
            messagebox.showinfo("Esportazione", f"Dati esportati con successo in:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esportazione CSV: {e}")
    
    def export_json(self):
        """Esporta tutti i dati in formato JSON"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("File JSON", "*.json"), ("Tutti i file", "*.*")],
                initialname=f"lol_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if not filename:
                return
            
            # Aggiungi timestamp di esportazione
            export_data = self.data.copy()
            export_data["exportTimestamp"] = datetime.now().isoformat()
            
            with open(filename, 'w', encoding='utf-8') as file:
                json.dump(export_data, file, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Esportazione", f"Dati completi esportati in:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esportazione JSON: {e}")

def create_gui():
    """Crea la finestra principale della GUI migliorata"""
    root = tk.Tk()
    
    # Configurazione finestra
    root.state('zoomed') if os.name == 'nt' else root.attributes('-zoomed', True)
    
    # Stile moderno per la finestra
    try:
        root.tk.call('tk', 'scaling', 1.2)  # DPI scaling
    except:
        pass
    
    app = RankStatsApp(root)
    root.mainloop()

if __name__ == "__main__":
    create_gui()