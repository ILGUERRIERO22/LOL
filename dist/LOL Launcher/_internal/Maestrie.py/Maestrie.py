#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
League of Legends Mastery Tool v2.0
Applicazione completa per visualizzare le maestrie dei campioni
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime
import os
import sys
import requests
import json
import threading
import time
import csv
from pathlib import Path
from urllib.parse import quote
import webbrowser

# Controllo dipendenze opzionali
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

# Configurazione percorsi
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

# Crea cartelle necessarie
for directory in [ASSETS_DIR, DATA_DIR, CONFIG_DIR]:
    directory.mkdir(exist_ok=True)

# Percorsi file
SEARCH_HISTORY_FILE = DATA_DIR / "search_history.json"
RIOT_ID_FILE = DATA_DIR / "riot_id.json"
ENV_FILE = CONFIG_DIR / "API.env"
SETTINGS_FILE = CONFIG_DIR / "settings.json"
CHAMPIONS_FILE = DATA_DIR / "champions_cache.json"

# Temi colori
class Theme:
    DARK = {
        "bg": "#0F1419", "bg_secondary": "#1C1C1E", "bg_tertiary": "#2C2C2E",
        "text": "#FFFFFF", "text_secondary": "#EBEBF5", "text_tertiary": "#8E8E93",
        "accent": "#007AFF", "accent_hover": "#0056CC", "success": "#30D158",
        "warning": "#FF9F0A", "error": "#FF3B30", "gold": "#FFD60A"
    }
    
    LIGHT = {
        "bg": "#FFFFFF", "bg_secondary": "#F2F2F7", "bg_tertiary": "#E5E5EA",
        "text": "#000000", "text_secondary": "#1C1C1E", "text_tertiary": "#6D6D70",
        "accent": "#007AFF", "accent_hover": "#0056CC", "success": "#30D158",
        "warning": "#FF9F0A", "error": "#FF3B30", "gold": "#FFD60A"
    }
    
    LOL = {
        "bg": "#010A13", "bg_secondary": "#0F2027", "bg_tertiary": "#1C3041",
        "text": "#F0E6D2", "text_secondary": "#C9AA71", "text_tertiary": "#785A28",
        "accent": "#C8AA6E", "accent_hover": "#F0E6D2", "success": "#0F8B3F",
        "warning": "#C89B3C", "error": "#C8343E", "gold": "#C8AA6E"
    }

class Config:
    """Gestione configurazione"""
    
    def __init__(self):
        self.settings = self.load_settings()
    
    def load_settings(self):
        defaults = {
            "theme": "DARK", "window_geometry": "800x650", "api_key": "",
            "default_region": "EUW1", "auto_save_searches": True,
            "max_history_items": 10, "show_splash": True
        }
        
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    defaults.update(saved)
            except Exception as e:
                print(f"Errore caricamento impostazioni: {e}")
        
        return defaults
    
    def save_settings(self):
        try:
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Errore salvataggio impostazioni: {e}")
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

class RiotAPI:
    """Gestione API Riot Games"""
    
    REGIONS = {
        "BR1": "americas", "EUN1": "europe", "EUW1": "europe", "JP1": "asia",
        "KR": "asia", "LA1": "americas", "LA2": "americas", "NA1": "americas",
        "OC1": "sea", "RU": "europe", "TR1": "europe"
    }
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": api_key})
    
    def get_puuid(self, game_name, tag_line):
        """Ottiene PUUID da nome#tag"""
        url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{quote(game_name)}/{quote(tag_line)}"
        
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 404:
                raise ValueError(f"Evocatore {game_name}#{tag_line} non trovato")
            response.raise_for_status()
            return response.json()["puuid"]
        except requests.RequestException as e:
            raise ValueError(f"Errore API: {e}")
    
    def get_masteries(self, puuid, region="euw1"):
        """Ottiene maestrie"""
        url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ValueError(f"Errore recupero maestrie: {e}")
    
    def get_champions(self):
        """Ottiene dati campioni"""
        # Prova cache prima
        if CHAMPIONS_FILE.exists():
            try:
                with open(CHAMPIONS_FILE, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                    if time.time() - cache.get("timestamp", 0) < 604800:  # 7 giorni
                        return cache["data"]
            except:
                pass
        
        try:
            # Ottieni ultima versione
            versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
            version = requests.get(versions_url, timeout=10).json()[0]
            
            # Scarica dati campioni
            champs_url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/it_IT/champion.json"
            response = requests.get(champs_url, timeout=10)
            response.raise_for_status()
            champions = response.json()["data"]
            
            # Salva cache
            cache_data = {"timestamp": time.time(), "version": version, "data": champions}
            try:
                with open(CHAMPIONS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
            except:
                pass
            
            return champions
            
        except requests.RequestException as e:
            raise ValueError(f"Errore download campioni: {e}")

class MasteryCalculator:
    """Calcolatori maestrie"""
    
    THRESHOLDS = {1: 0, 2: 1800, 3: 6000, 4: 12600, 5: 21600,
                  6: 31600, 7: 42600, 8: 53600, 9: 64600, 10: 75600}
    
    TOKEN_REQUIREMENTS = {5: 1, 6: 1, 7: 1, 8: 1, 9: 3, 10: 2}
    
    @staticmethod
    def get_mastery_color(level):
        # Colori base per livelli 1-10
        base_colors = {10: "#FF00FF", 9: "#00FF9F", 8: "#00B7FF", 7: "#FF6DF0",
                       6: "#FF0000", 5: "#8C00FF", 4: "#00FFFF", 3: "#00FF00",
                       2: "#FFFF00", 1: "#808080"}
        
        if level <= 10:
            return base_colors.get(level, "#FFFFFF")
        
        # Colori speciali per livelli infiniti (10+)
        infinite_colors = [
            "#FF1493",  # Deep Pink - Livello 11
            "#FF69B4",  # Hot Pink - Livello 12  
            "#FF6347",  # Tomato - Livello 13
            "#FF4500",  # Orange Red - Livello 14
            "#FFD700",  # Gold - Livello 15
            "#FFFF00",  # Yellow - Livello 16
            "#ADFF2F",  # Green Yellow - Livello 17
            "#00FF7F",  # Spring Green - Livello 18
            "#00FFFF",  # Cyan - Livello 19
            "#87CEEB",  # Sky Blue - Livello 20
            "#9370DB",  # Medium Purple - Livello 21+
        ]
        
        # Per livelli oltre 21, usa un colore arcobaleno ciclico
        if level > 21:
            rainbow_colors = ["#FF0080", "#FF8000", "#FFFF00", "#80FF00", "#00FF80", "#0080FF", "#8000FF"]
            color_index = (level - 22) % len(rainbow_colors)
            return rainbow_colors[color_index]
        
        # Per livelli 11-21, usa i colori dalla lista
        color_index = min(level - 11, len(infinite_colors) - 1)
        return infinite_colors[color_index]
    
    @staticmethod
    def format_number(num):
        return f"{num:,}".replace(",", ".")
    
    @staticmethod
    def format_last_played(timestamp_ms):
        if not timestamp_ms:
            return "Mai giocato"
        try:
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return "N/A"

class DataManager:
    """Gestione dati persistenti"""
    
    @staticmethod
    def load_json(file_path, default=None):
        if default is None:
            default = []
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return default
    
    @staticmethod
    def save_json(file_path, data):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    @staticmethod
    def add_search_history(game_name, tag_line, region="EUW1"):
        history = DataManager.load_json(SEARCH_HISTORY_FILE, [])
        entry = {"gameName": game_name, "tagLine": tag_line, "region": region, "timestamp": time.time()}
        
        # Rimuovi duplicati
        history = [h for h in history if not (h.get("gameName") == game_name and h.get("tagLine") == tag_line)]
        history.insert(0, entry)
        history = history[:10]  # Mantieni solo 10
        
        DataManager.save_json(SEARCH_HISTORY_FILE, history)
    
    @staticmethod
    def save_riot_id(game_name, tag_line, region="EUW1"):
        data = {"gameName": game_name, "tagLine": tag_line, "region": region}
        DataManager.save_json(RIOT_ID_FILE, data)
    
    @staticmethod
    def load_riot_id():
        data = DataManager.load_json(RIOT_ID_FILE, {})
        return data.get("gameName", ""), data.get("tagLine", ""), data.get("region", "EUW1")

class ModernButton:
    """Pulsante moderno"""
    
    @staticmethod
    def create(parent, text, command=None, style="primary"):
        if hasattr(parent, 'current_theme'):
            theme = getattr(Theme, parent.current_theme)
        else:
            theme = Theme.DARK
        
        colors = {
            "primary": (theme["accent"], theme["bg"]),
            "secondary": (theme["bg_tertiary"], theme["text"]),
            "success": (theme["success"], theme["bg"]),
            "error": (theme["error"], theme["bg"])
        }
        
        bg, fg = colors.get(style, colors["primary"])
        
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                       relief="flat", bd=0, font=("Segoe UI", 10, "bold"),
                       padx=15, pady=6, cursor="hand2")
        
        def on_enter(e):
            btn.config(bg=theme["accent_hover"])
        def on_leave(e):
            btn.config(bg=bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

class ResultsWindow:
    """Finestra risultati maestrie"""
    
    def __init__(self, parent, masteries, champions_data, summoner_name):
        self.parent = parent
        self.masteries = masteries
        self.champions_data = champions_data
        self.summoner_name = summoner_name
        
        # Mapping ID -> Nome
        self.champ_id_to_name = {int(info["key"]): name for name, info in champions_data.items()}
        
        self.create_window()
    
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"Maestrie - {self.summoner_name}")
        self.window.geometry("1200x700")
        
        # Tema
        theme = getattr(Theme, self.parent.current_theme) if hasattr(self.parent, 'current_theme') else Theme.DARK
        self.window.configure(bg=theme["bg"])
        
        self.create_widgets(theme)
        self.populate_data()
        
        # Centra finestra
        self.center_window()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - self.window.winfo_width()) // 2
        y = (self.window.winfo_screenheight() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")
    
    def create_widgets(self, theme):
        # Header
        header = tk.Frame(self.window, bg=theme["bg"])
        header.pack(fill="x", padx=20, pady=10)
        
        tk.Label(header, text=f"Maestrie di {self.summoner_name}",
                font=("Segoe UI", 16, "bold"), bg=theme["bg"], fg=theme["accent"]).pack()
        
        # Stats
        stats_frame = tk.LabelFrame(self.window, text="Statistiche", bg=theme["bg_secondary"],
                                   fg=theme["accent"], font=("Segoe UI", 11, "bold"))
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Calcola stats
        total_points = sum(m["championPoints"] for m in self.masteries)
        max_level = max(m["championLevel"] for m in self.masteries) if self.masteries else 0
        level_7_plus = sum(1 for m in self.masteries if m["championLevel"] >= 7)
        
        stats_text = f"Punti Totali: {MasteryCalculator.format_number(total_points)} | "
        stats_text += f"Livello Max: {max_level} | Maestria 7+: {level_7_plus}"
        
        tk.Label(stats_frame, text=stats_text, bg=theme["bg_secondary"],
                fg=theme["gold"], font=("Segoe UI", 11)).pack(pady=10)
        
        # Filtri
        filter_frame = tk.LabelFrame(self.window, text="Filtri", bg=theme["bg_secondary"],
                                   fg=theme["accent"], font=("Segoe UI", 11, "bold"))
        filter_frame.pack(fill="x", padx=20, pady=5)
        
        filter_container = tk.Frame(filter_frame, bg=theme["bg_secondary"])
        filter_container.pack(fill="x", padx=10, pady=10)
        
        tk.Label(filter_container, text="Cerca:", bg=theme["bg_secondary"], fg=theme["text"]).pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_data)
        search_entry = tk.Entry(filter_container, textvariable=self.search_var,
                               bg=theme["bg_tertiary"], fg=theme["text"], width=20)
        search_entry.pack(side="left", padx=10)
        
        tk.Label(filter_container, text="Livello:", bg=theme["bg_secondary"], fg=theme["text"]).pack(side="left", padx=(20,5))
        
        self.level_var = tk.StringVar(value="Tutti")
        level_combo = ttk.Combobox(filter_container, textvariable=self.level_var,
                                  values=["Tutti", "10+", "10", "9", "8", "7", "6", "5", "4", "3", "2", "1"],
                                  state="readonly", width=8)
        level_combo.pack(side="left")
        level_combo.bind("<<ComboboxSelected>>", self.filter_data)
        
        # Tabella
        table_frame = tk.Frame(self.window, bg=theme["bg"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Configura stile Treeview per tema
        style = ttk.Style()
        style.configure("Mastery.Treeview",
                       background=theme["bg_secondary"],
                       foreground=theme["text"],
                       fieldbackground=theme["bg_secondary"],
                       borderwidth=0,
                       font=("Segoe UI", 10))
        
        style.configure("Mastery.Treeview.Heading",
                       background=theme["bg_tertiary"],
                       foreground=theme["accent"],
                       font=("Segoe UI", 11, "bold"),
                       borderwidth=1,
                       relief="flat")
        
        style.map("Mastery.Treeview",
                 background=[("selected", theme["accent"])],
                 foreground=[("selected", theme["bg"])])
        
        style.map("Mastery.Treeview.Heading",
                 background=[("active", theme["accent"]),
                           ("pressed", theme["accent_hover"])])
        
        columns = ("Campione", "Livello", "Punti", "Punti Mancanti", "Ultima Partita", "Marchi")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15, style="Mastery.Treeview")
        
        # Configura colonne
        widths = [150, 80, 120, 120, 140, 80]
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=widths[i], anchor="center")
        
        # Scrollbar con stile tema
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Configura scrollbar
        style.configure("Vertical.TScrollbar",
                       background=theme["bg_tertiary"],
                       troughcolor=theme["bg_secondary"],
                       arrowcolor=theme["text"],
                       borderwidth=0)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Pulsanti
        btn_frame = tk.Frame(self.window, bg=theme["bg"])
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ModernButton.create(btn_frame, "Esporta CSV", self.export_csv, "secondary").pack(side="left")
        ModernButton.create(btn_frame, "Calcolatore", self.open_calculator, "primary").pack(side="left", padx=10)
        ModernButton.create(btn_frame, "Chiudi", self.window.destroy, "error").pack(side="right")
    
    def populate_data(self):
        self.filtered_masteries = self.masteries[:]
        self.update_table()
    
    def update_table(self):
        # Pulisci tabella
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Inserisci dati filtrati
        for mastery in self.filtered_masteries:
            champ_name = self.champ_id_to_name.get(mastery["championId"], "Sconosciuto")
            level = mastery["championLevel"]
            points = MasteryCalculator.format_number(mastery["championPoints"])
            points_next = MasteryCalculator.format_number(mastery["championPointsUntilNextLevel"])
            last_played = MasteryCalculator.format_last_played(mastery["lastPlayTime"])
            tokens = mastery.get("tokensEarned", 0)
            
            item_id = self.tree.insert("", "end",
                values=(champ_name, level, points, points_next, last_played, tokens),
                tags=(f"level_{level}",))
        
        # Configura colori per tutti i livelli possibili
        # Prima configura i livelli standard
        for level in range(1, 11):
            color = MasteryCalculator.get_mastery_color(level)
            self.tree.tag_configure(f"level_{level}", foreground=color)
        
        # Poi configura i livelli infiniti che potrebbero esistere nei dati
        max_level = max((m["championLevel"] for m in self.masteries), default=10)
        if max_level > 10:
            for level in range(11, max_level + 1):
                color = MasteryCalculator.get_mastery_color(level)
                self.tree.tag_configure(f"level_{level}", foreground=color)
    
    def filter_data(self, *args):
        search_text = self.search_var.get().lower()
        level_filter = self.level_var.get()
        
        self.filtered_masteries = []
        for mastery in self.masteries:
            champ_name = self.champ_id_to_name.get(mastery["championId"], "").lower()
            level = mastery["championLevel"]
            
            # Filtro ricerca
            if search_text and search_text not in champ_name:
                continue
            
            # Filtro livello
            if level_filter != "Tutti":
                if level_filter == "10+" and level <= 10:
                    continue
                elif level_filter != "10+" and level != int(level_filter):
                    continue
            
            self.filtered_masteries.append(mastery)
        
        self.update_table()
    
    def export_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Campione", "Livello", "Punti", "Punti_Mancanti", "Ultima_Partita", "Marchi"])
                    
                    for mastery in self.masteries:
                        champ_name = self.champ_id_to_name.get(mastery["championId"], "Sconosciuto")
                        writer.writerow([
                            champ_name, mastery["championLevel"], mastery["championPoints"],
                            mastery["championPointsUntilNextLevel"],
                            MasteryCalculator.format_last_played(mastery["lastPlayTime"]),
                            mastery.get("tokensEarned", 0)
                        ])
                
                messagebox.showinfo("Successo", f"Dati esportati in:\n{filename}")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore esportazione:\n{e}")
    
    def open_calculator(self):
        CalculatorWindow(self.window, self.masteries, self.champions_data)

class CalculatorWindow:
    """Calcolatore progressione"""
    
    def __init__(self, parent, masteries, champions_data):
        self.parent = parent
        self.masteries = masteries
        self.champions_data = champions_data
        self.champ_id_to_name = {int(info["key"]): name for name, info in champions_data.items()}
        
        self.create_window()
    
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Calcolatore Progressione")
        self.window.geometry("700x500")
        
        theme = getattr(Theme, self.parent.current_theme) if hasattr(self.parent, 'current_theme') else Theme.DARK
        self.window.configure(bg=theme["bg"])
        
        self.create_widgets(theme)
        self.center_window()
    
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - self.window.winfo_width()) // 2
        y = (self.window.winfo_screenheight() - self.window.winfo_height()) // 2
        self.window.geometry(f"+{x}+{y}")
    
    def create_widgets(self, theme):
        # Header
        tk.Label(self.window, text="Calcolatore Progressione Maestrie",
                font=("Segoe UI", 16, "bold"), bg=theme["bg"], fg=theme["accent"]).pack(pady=20)
        
        # Selezione campione
        select_frame = tk.LabelFrame(self.window, text="Seleziona Campione", bg=theme["bg_secondary"],
                                   fg=theme["accent"], font=("Segoe UI", 11, "bold"))
        select_frame.pack(fill="x", padx=20, pady=10)
        
        # Lista campioni
        champ_list = []
        for mastery in self.masteries:
            name = self.champ_id_to_name.get(mastery["championId"], "Sconosciuto")
            champ_list.append(f"{name} (Liv. {mastery['championLevel']})")
        
        self.champ_var = tk.StringVar()
        champ_combo = ttk.Combobox(select_frame, textvariable=self.champ_var,
                                  values=champ_list, state="readonly", width=50)
        champ_combo.pack(padx=15, pady=15)
        if champ_list:
            champ_combo.current(0)
        
        # Parametri
        params_frame = tk.LabelFrame(self.window, text="Parametri", bg=theme["bg_secondary"],
                                   fg=theme["accent"], font=("Segoe UI", 11, "bold"))
        params_frame.pack(fill="x", padx=20, pady=10)
        
        params_grid = tk.Frame(params_frame, bg=theme["bg_secondary"])
        params_grid.pack(padx=15, pady=15)
        
        tk.Label(params_grid, text="Punti medi per partita:", bg=theme["bg_secondary"], fg=theme["text"]).grid(row=0, column=0, sticky="w", padx=5)
        self.points_var = tk.StringVar(value="1200")
        tk.Entry(params_grid, textvariable=self.points_var, width=10).grid(row=0, column=1, padx=5)
        
        tk.Label(params_grid, text="Partite al giorno:", bg=theme["bg_secondary"], fg=theme["text"]).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.games_var = tk.StringVar(value="3")
        tk.Entry(params_grid, textvariable=self.games_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        # Risultati
        self.results_text = scrolledtext.ScrolledText(self.window, height=12, bg=theme["bg_tertiary"],
                                                     fg=theme["text"], font=("Consolas", 10),
                                                     insertbackground=theme["text"],
                                                     selectbackground=theme["accent"],
                                                     selectforeground=theme["bg"])
        self.results_text.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Pulsanti
        btn_frame = tk.Frame(self.window, bg=theme["bg"])
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ModernButton.create(btn_frame, "Calcola", self.calculate, "primary").pack(side="left")
        ModernButton.create(btn_frame, "Chiudi", self.window.destroy, "secondary").pack(side="right")
    
    def calculate(self):
        try:
            selected_index = [i for i, v in enumerate([f"{self.champ_id_to_name.get(m['championId'], 'Sconosciuto')} (Liv. {m['championLevel']})" for m in self.masteries]) if v == self.champ_var.get()]
            if not selected_index:
                return
            
            mastery = self.masteries[selected_index[0]]
            avg_points = float(self.points_var.get())
            games_per_day = float(self.games_var.get())
            
            if avg_points <= 0 or games_per_day <= 0:
                raise ValueError("Valori devono essere positivi")
            
            # Calcoli
            current_level = mastery["championLevel"]
            current_points = mastery["championPoints"]
            points_needed = mastery["championPointsUntilNextLevel"]
            champ_name = self.champ_id_to_name.get(mastery["championId"], "Sconosciuto")
            
            games_needed = points_needed / avg_points
            days_needed = games_needed / games_per_day
            
            # Report
            report = f"""
REPORT PROGRESSIONE - {champ_name}
{'=' * 50}

STATO ATTUALE:
• Livello Maestria: {current_level}
• Punti Attuali: {MasteryCalculator.format_number(current_points)}
• Prossimo Livello: {current_level + 1}

OBIETTIVO:
• Punti Mancanti: {MasteryCalculator.format_number(points_needed)}

STIME TEMPORALI:
• Partite Necessarie: {games_needed:.1f}
• Giorni Stimati: {days_needed:.1f} giorni
• Settimane Stimate: {days_needed/7:.1f} settimane

PARAMETRI:
• Punti per Partita: {avg_points:.0f}
• Partite al Giorno: {games_per_day:.1f}

RACCOMANDAZIONI:
"""
            
            if current_level >= 5:
                tokens_needed = MasteryCalculator.TOKEN_REQUIREMENTS.get(current_level, 0)
                tokens_current = mastery.get("tokensEarned", 0)
                if tokens_needed > tokens_current:
                    report += f"• Ottieni {tokens_needed - tokens_current} marchi con voti S/S+\n"
            
            if days_needed > 30:
                report += "• Considera di aumentare le partite giornaliere\n"
            
            report += "\nNOTA: Calcoli basati sui parametri inseriti."
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, report)
            
        except ValueError as e:
            messagebox.showerror("Errore", f"Errore nei parametri: {e}")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore calcolo: {e}")

class MainApplication:
    """Applicazione principale"""
    
    def __init__(self, root):
        self.root = root
        self.config = Config()
        self.current_theme = self.config.get("theme", "DARK")
        
        self.setup_window()
        self.create_widgets()
        self.apply_theme()
        self.load_data()
        
        # Log
        self.log("Applicazione avviata", "success")
        
        # Controlla API key
        if not self.config.get("api_key"):
            self.root.after(1000, self.show_api_dialog)
    
    def setup_window(self):
        self.root.title("League of Legends Mastery Tool v2.0")
        self.root.geometry(self.config.get("window_geometry", "800x650"))
        self.root.minsize(700, 500)
        
        # Centra finestra
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        # Container principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title_label = ttk.Label(header_frame, text="League of Legends Mastery Tool",
                               font=("Segoe UI", 18, "bold"))
        title_label.pack()
        
        # Form ricerca
        search_frame = ttk.LabelFrame(main_frame, text="Ricerca Evocatore", padding=15)
        search_frame.pack(fill="x", pady=(0, 15))
        
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Nome Evocatore:").grid(row=0, column=0, sticky="w", padx=(0,10), pady=5)
        self.game_name_entry = ttk.Entry(search_frame, font=("Segoe UI", 11))
        self.game_name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        ttk.Label(search_frame, text="Tag:").grid(row=1, column=0, sticky="w", padx=(0,10), pady=5)
        self.tag_entry = ttk.Entry(search_frame, font=("Segoe UI", 11))
        self.tag_entry.grid(row=1, column=1, sticky="ew", pady=5)
        
        ttk.Label(search_frame, text="Regione:").grid(row=2, column=0, sticky="w", padx=(0,10), pady=5)
        self.region_var = tk.StringVar(value=self.config.get("default_region", "EUW1"))
        self.region_combo = ttk.Combobox(search_frame, textvariable=self.region_var,
                                        values=list(RiotAPI.REGIONS.keys()), state="readonly")
        self.region_combo.grid(row=2, column=1, sticky="w", pady=5)
        
        # Cronologia
        history_frame = ttk.LabelFrame(main_frame, text="Ricerche Recenti", padding=15)
        history_frame.pack(fill="x", pady=(0, 15))
        
        self.history_var = tk.StringVar()
        self.history_combo = ttk.Combobox(history_frame, textvariable=self.history_var, state="readonly")
        self.history_combo.pack(fill="x")
        self.history_combo.bind("<<ComboboxSelected>>", self.on_history_select)
        
        # Controlli
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill="x", pady=(0, 15))
        
        # Status
        self.status_var = tk.StringVar(value="Pronto")
        status_label = ttk.Label(controls_frame, textvariable=self.status_var)
        status_label.pack(side="left")
        
        # Progress
        self.progress = ttk.Progressbar(controls_frame, mode="indeterminate")
        
        # Pulsanti
        ModernButton.create(controls_frame, "Impostazioni", self.show_settings, "secondary").pack(side="right", padx=(5,0))
        self.search_btn = ModernButton.create(controls_frame, "Ottieni Maestrie", self.fetch_data, "primary")
        self.search_btn.pack(side="right", padx=(5,0))
        
        # Log
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding=10)
        log_frame.pack(fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True)
        
        # Menu
        self.create_menu()
        
        # Bind eventi
        self.root.bind("<Return>", lambda e: self.fetch_data())
        self.root.bind("<F5>", lambda e: self.fetch_data())
        self.root.bind("<Control-t>", lambda e: self.cycle_theme())
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Impostazioni", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.on_closing)
        
        # Visualizza
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualizza", menu=view_menu)
        view_menu.add_command(label="Cambia Tema", command=self.cycle_theme)
        view_menu.add_command(label="Pulisci Log", command=self.clear_log)
        
        # Aiuto
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="Informazioni", command=self.show_about)
    
    def apply_theme(self):
        theme = getattr(Theme, self.current_theme)
        
        # Finestra principale
        self.root.configure(bg=theme["bg"])
        
        # Stili TTK
        style = ttk.Style()
        
        # Stili base
        style.configure("TLabel", background=theme["bg"], foreground=theme["text"], font=("Segoe UI", 10))
        style.configure("TFrame", background=theme["bg"])
        style.configure("TLabelframe", background=theme["bg"], foreground=theme["accent"], relief="flat", borderwidth=1)
        style.configure("TLabelframe.Label", background=theme["bg"], foreground=theme["accent"], font=("Segoe UI", 11, "bold"))
        
        # Entry e Combobox
        style.configure("TEntry", 
                       fieldbackground=theme["bg_tertiary"], 
                       foreground=theme["text"],
                       borderwidth=1,
                       insertcolor=theme["text"])
        style.configure("TCombobox", 
                       fieldbackground=theme["bg_tertiary"], 
                       foreground=theme["text"],
                       arrowcolor=theme["text"],
                       borderwidth=1)
        style.map("TCombobox",
                 fieldbackground=[("readonly", theme["bg_tertiary"])],
                 foreground=[("readonly", theme["text"])])
        
        # Progressbar
        style.configure("TProgressbar", 
                       background=theme["accent"],
                       troughcolor=theme["bg_secondary"],
                       borderwidth=0)
        
        # Scrollbar
        style.configure("Vertical.TScrollbar",
                       background=theme["bg_tertiary"],
                       troughcolor=theme["bg_secondary"],
                       arrowcolor=theme["text"],
                       borderwidth=0)
        
        # Treeview globale (per tutte le finestre)
        style.configure("Treeview",
                       background=theme["bg_secondary"],
                       foreground=theme["text"],
                       fieldbackground=theme["bg_secondary"],
                       borderwidth=0,
                       font=("Segoe UI", 10))
        
        style.configure("Treeview.Heading",
                       background=theme["bg_tertiary"],
                       foreground=theme["accent"],
                       font=("Segoe UI", 11, "bold"),
                       borderwidth=1,
                       relief="flat")
        
        style.map("Treeview",
                 background=[("selected", theme["accent"])],
                 foreground=[("selected", theme["bg"])])
        
        style.map("Treeview.Heading",
                 background=[("active", theme["accent"]),
                           ("pressed", theme["accent_hover"])])
        
        # Log
        if hasattr(self, 'log_text'):
            self.log_text.configure(bg=theme["bg_secondary"], fg=theme["text"],
                                   insertbackground=theme["text"],
                                   selectbackground=theme["accent"],
                                   selectforeground=theme["bg"])
    
    def cycle_theme(self):
        themes = ["DARK", "LIGHT", "LOL"]
        current_index = themes.index(self.current_theme)
        next_index = (current_index + 1) % len(themes)
        self.current_theme = themes[next_index]
        
        self.config.set("theme", self.current_theme)
        self.apply_theme()
        self.log(f"Tema: {self.current_theme}", "info")
    
    def load_data(self):
        # Carica ultimo Riot ID
        game_name, tag_line, region = DataManager.load_riot_id()
        if game_name:
            self.game_name_entry.delete(0, tk.END)
            self.game_name_entry.insert(0, game_name)
        if tag_line:
            self.tag_entry.delete(0, tk.END)
            self.tag_entry.insert(0, tag_line)
        if region:
            self.region_var.set(region)
        
        # Carica cronologia
        history = DataManager.load_json(SEARCH_HISTORY_FILE, [])
        history_values = [f"{h['gameName']} - {h['tagLine']} ({h.get('region', 'EUW1')})" for h in history]
        self.history_combo['values'] = history_values
    
    def on_history_select(self, event=None):
        selected = self.history_combo.get()
        if " - " in selected:
            parts = selected.split(" - ")
            game_name = parts[0]
            tag_region = parts[1]
            
            if " (" in tag_region:
                tag_line = tag_region.split(" (")[0]
                region = tag_region.split(" (")[1].rstrip(")")
            else:
                tag_line = tag_region
                region = "EUW1"
            
            self.game_name_entry.delete(0, tk.END)
            self.game_name_entry.insert(0, game_name)
            self.tag_entry.delete(0, tk.END)
            self.tag_entry.insert(0, tag_line)
            self.region_var.set(region)
    
    def fetch_data(self):
        game_name = self.game_name_entry.get().strip()
        tag_line = self.tag_entry.get().strip()
        region = self.region_var.get()
        
        if not game_name or not tag_line:
            messagebox.showwarning("Attenzione", "Inserisci nome evocatore e tag")
            return
        
        api_key = self.config.get("api_key", "")
        if not api_key:
            self.show_api_dialog()
            return
        
        # UI loading
        self.status_var.set("Ricerca in corso...")
        self.search_btn.config(state="disabled")
        self.progress.pack(side="left", padx=(20,0))
        self.progress.start()
        
        self.log(f"Ricerca: {game_name}#{tag_line} ({region})")
        
        def search_thread():
            try:
                api = RiotAPI(api_key)
                puuid = api.get_puuid(game_name, tag_line)
                masteries = api.get_masteries(puuid, region.lower())
                champions = api.get_champions()
                
                def success():
                    self.progress.stop()
                    self.progress.pack_forget()
                    self.status_var.set("Pronto")
                    self.search_btn.config(state="normal")
                    
                    self.log(f"Trovate {len(masteries)} maestrie", "success")
                    
                    # Salva ricerca
                    DataManager.save_riot_id(game_name, tag_line, region)
                    DataManager.add_search_history(game_name, tag_line, region)
                    self.load_data()
                    
                    # Mostra risultati
                    ResultsWindow(self.root, masteries, champions, f"{game_name}#{tag_line}")
                
                self.root.after(0, success)
                
            except Exception as e:
                def error():
                    self.progress.stop()
                    self.progress.pack_forget()
                    self.status_var.set("Errore")
                    self.search_btn.config(state="normal")
                    
                    self.log(f"Errore: {e}", "error")
                    messagebox.showerror("Errore", f"Errore ricerca:\n{e}")
                
                self.root.after(0, error)
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def show_api_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Configura API Key")
        dialog.geometry("500x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centra
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 50
        dialog.geometry(f"+{x}+{y}")
        
        frame = tk.Frame(dialog, padx=30, pady=30)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="Configura API Key Riot Games", font=("Segoe UI", 14, "bold")).pack(pady=(0,15))
        
        tk.Label(frame, text="Vai su https://developer.riotgames.com/\ne copia la tua Personal API Key:",
                justify="left").pack(pady=(0,10))
        
        tk.Label(frame, text="API Key:").pack(anchor="w")
        api_var = tk.StringVar(value=self.config.get("api_key", ""))
        entry = tk.Entry(frame, textvariable=api_var, show="*", width=50)
        entry.pack(fill="x", pady=(5,15))
        entry.focus()
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x")
        
        def save():
            key = api_var.get().strip()
            if key:
                self.config.set("api_key", key)
                self.log("API Key salvata", "success")
                dialog.destroy()
            else:
                messagebox.showwarning("Attenzione", "Inserisci una API Key valida")
        
        tk.Button(btn_frame, text="Riot Developer", 
                 command=lambda: webbrowser.open("https://developer.riotgames.com/")).pack(side="left")
        tk.Button(btn_frame, text="Annulla", command=dialog.destroy).pack(side="right")
        tk.Button(btn_frame, text="Salva", command=save).pack(side="right", padx=(5,0))
        
        dialog.bind("<Return>", lambda e: save())
    
    def show_settings(self):
        settings = tk.Toplevel(self.root)
        settings.title("Impostazioni")
        settings.geometry("400x300")
        settings.transient(self.root)
        settings.grab_set()
        
        frame = tk.Frame(settings, padx=30, pady=30)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="Impostazioni", font=("Segoe UI", 16, "bold")).pack(pady=(0,20))
        
        # Tema
        tk.Label(frame, text="Tema:", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        theme_var = tk.StringVar(value=self.current_theme)
        
        for theme_name, theme_val in [("Scuro", "DARK"), ("Chiaro", "LIGHT"), ("League of Legends", "LOL")]:
            tk.Radiobutton(frame, text=theme_name, variable=theme_var, value=theme_val).pack(anchor="w", padx=20)
        
        # Regione
        tk.Label(frame, text="Regione predefinita:", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(20,5))
        region_var = tk.StringVar(value=self.config.get("default_region", "EUW1"))
        region_combo = ttk.Combobox(frame, textvariable=region_var, values=list(RiotAPI.REGIONS.keys()),
                                   state="readonly", width=10)
        region_combo.pack(anchor="w", padx=20)
        
        # Pulsanti
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=(30,0))
        
        def save_settings():
            # Salva tema
            new_theme = theme_var.get()
            if new_theme != self.current_theme:
                self.current_theme = new_theme
                self.config.set("theme", new_theme)
                self.apply_theme()
            
            # Salva regione
            self.config.set("default_region", region_var.get())
            
            self.log("Impostazioni salvate", "success")
            settings.destroy()
        
        tk.Button(btn_frame, text="Salva", command=save_settings).pack(side="right")
        tk.Button(btn_frame, text="Annulla", command=settings.destroy).pack(side="right", padx=(5,0))
    
    def show_about(self):
        about = tk.Toplevel(self.root)
        about.title("Informazioni")
        about.geometry("400x300")
        about.resizable(False, False)
        about.transient(self.root)
        
        frame = tk.Frame(about, padx=30, pady=30)
        frame.pack(fill="both", expand=True)
        
        tk.Label(frame, text="League of Legends Mastery Tool", font=("Segoe UI", 14, "bold")).pack(pady=(0,10))
        tk.Label(frame, text="Versione 2.0.0", font=("Segoe UI", 10)).pack()
        
        info = """
Applicazione per visualizzare le maestrie
dei campioni di League of Legends.

Caratteristiche:
• Ricerca maestrie in tempo reale
• Calcolatore progressione
• Esportazione CSV
• Temi personalizzabili

Non affiliato con Riot Games Inc.
"""
        
        tk.Label(frame, text=info, justify="center", wraplength=350).pack(pady=20)
        tk.Button(frame, text="Chiudi", command=about.destroy).pack()
    
    def log(self, message, level="info"):
        colors = {"info": "black", "success": "green", "error": "red", "warning": "orange"}
        color = colors.get(level, "black")
        
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        
        # Configura colore ultima riga
        line_start = self.log_text.index("end-2c linestart")
        line_end = self.log_text.index("end-2c lineend")
        
        tag_name = f"color_{level}"
        self.log_text.tag_configure(tag_name, foreground=color)
        self.log_text.tag_add(tag_name, line_start, line_end)
        
        self.log_text.see(tk.END)
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        self.log("Log pulito", "info")
    
    def on_closing(self):
        self.config.set("window_geometry", self.root.geometry())
        self.log("Chiusura applicazione")
        self.root.quit()

def main():
    print("League of Legends Mastery Tool v2.0")
    print("=" * 40)
    
    # Controllo dipendenze
    missing = []
    if not HAS_PIL:
        missing.append("pillow")
    if not HAS_DOTENV:
        missing.append("python-dotenv")
    
    if missing:
        print(f"DIPENDENZE OPZIONALI MANCANTI: {', '.join(missing)}")
        print("Per installarle: pip install " + " ".join(missing))
        print()
    
    try:
        root = tk.Tk()
        app = MainApplication(root)
        
        print("Applicazione avviata!")
        print("Usa F5 o Enter per ricercare")
        print("Usa Ctrl+T per cambiare tema")
        print()
        
        root.mainloop()
        
    except KeyboardInterrupt:
        print("Chiusura forzata")
    except Exception as e:
        print(f"ERRORE FATALE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()