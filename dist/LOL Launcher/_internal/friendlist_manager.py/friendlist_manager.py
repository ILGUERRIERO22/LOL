import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import requests
import base64
import json
import urllib3
import subprocess
import re
import os
import sys
import time
import threading
import csv
from datetime import datetime
from PIL import Image, ImageTk
import io

# Disabilita gli avvisi SSL
urllib3.disable_warnings()

class LoLFriendsManager:
    def __init__(self, root):
        self.root = root
        self.root.title("LoL Friends Manager v2.0")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        self.root.minsize(700, 600)
        
        # Colori tematici
        self.colors = {
            'primary_bg': '#0A1428',
            'secondary_bg': '#1E2328',
            'accent': '#C8AA6E',
            'text_primary': '#F0E6D2',
            'text_secondary': '#A09B8C',
            'success': '#00F5FF',
            'warning': '#CDBE91',
            'error': '#CF3030',
            'button_bg': '#3C3C41',
            'frame_bg': '#1E2D3F'
        }
        
        self.root.configure(bg=self.colors['primary_bg'])
        
        # Variabili per la connessione LCU
        self.port = None
        self.token = None
        self.active_threads = []
        self.sent_invites = []
        self.debug_window = None
        
        # Inizializza i widget come None
        self.status_label = None
        self.username_entry = None
        self.add_friend_btn = None
        self.refresh_btn = None
        self.remove_all_btn = None
        self.import_btn = None
        self.friends_text = None
        self.stats_label = None
        self.csv_path_var = None
        self.column_var = None
        self.progress = None
        
        # Setup stili base
        self.setup_styles()
        
        # Crea l'interfaccia
        self.create_widgets()
        
        # Verifica client dopo caricamento UI
        self.root.after(500, self.check_lol_running)
    
    def setup_styles(self):
        """Configura stili base senza layout personalizzati problematici"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configura solo stili sicuri
        style.configure('Title.TLabel', 
                       background=self.colors['primary_bg'],
                       foreground=self.colors['accent'],
                       font=('Segoe UI', 16, 'bold'))
        
        style.configure('Custom.TLabel',
                       background=self.colors['primary_bg'],
                       foreground=self.colors['text_primary'],
                       font=('Segoe UI', 10))
        
        style.configure('Status.TLabel',
                       background=self.colors['primary_bg'],
                       foreground=self.colors['success'],
                       font=('Segoe UI', 9, 'bold'))
    
    def create_widgets(self):
        """Crea l'interfaccia utente"""
        # Container principale
        main_container = tk.Frame(self.root, bg=self.colors['primary_bg'])
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header
        self.create_header(main_container)
        
        # Sezioni
        self.create_single_friend_section(main_container)
        self.create_csv_section(main_container) 
        self.create_friends_list_section(main_container)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_container, mode='indeterminate')
        
        # Footer
        self.create_footer(main_container)
    
    def create_header(self, parent):
        """Crea la sezione header"""
        header_frame = tk.Frame(parent, bg=self.colors['primary_bg'])
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Titolo
        title_label = tk.Label(header_frame, 
                              text="League of Legends Friends Manager v2.0",
                              bg=self.colors['primary_bg'],
                              fg=self.colors['accent'],
                              font=('Segoe UI', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Frame status
        status_frame = tk.Frame(header_frame, 
                               bg=self.colors['frame_bg'],
                               relief='solid',
                               bd=1)
        status_frame.pack(fill='x', ipady=8, ipadx=10)
        
        status_left = tk.Frame(status_frame, bg=self.colors['frame_bg'])
        status_left.pack(side='left', fill='x', expand=True)
        
        tk.Label(status_left, text="Stato Client:", 
                bg=self.colors['frame_bg'],
                fg=self.colors['accent'],
                font=('Segoe UI', 10, 'bold')).pack(side='left', padx=(0, 10))
        
        self.status_label = tk.Label(status_left, text="Verifica in corso...",
                                    bg=self.colors['frame_bg'],
                                    fg=self.colors['text_secondary'],
                                    font=('Segoe UI', 10))
        self.status_label.pack(side='left')
        
        # Bottoni di controllo
        button_frame = tk.Frame(status_frame, bg=self.colors['frame_bg'])
        button_frame.pack(side='right')
        
        self.detect_btn = tk.Button(button_frame, text="Rileva Client",
                                   bg=self.colors['button_bg'],
                                   fg=self.colors['text_primary'],
                                   font=('Segoe UI', 9, 'bold'),
                                   relief='raised',
                                   command=self.check_lol_running)
        self.detect_btn.pack(side='right', padx=(5, 0))
        
        self.debug_btn = tk.Button(button_frame, text="Debug Console",
                                  bg=self.colors['button_bg'],
                                  fg=self.colors['text_primary'],
                                  font=('Segoe UI', 9, 'bold'),
                                  relief='raised',
                                  command=self.toggle_debug_console)
        self.debug_btn.pack(side='right', padx=(5, 0))
    
    def create_single_friend_section(self, parent):
        """Crea la sezione per aggiungere un singolo amico"""
        # Uso LabelFrame standard senza stile personalizzato
        friend_frame = tk.LabelFrame(parent, 
                                    text="Aggiungi Amico",
                                    bg=self.colors['frame_bg'],
                                    fg=self.colors['accent'],
                                    font=('Segoe UI', 11, 'bold'),
                                    relief='solid',
                                    bd=1)
        friend_frame.pack(fill='x', pady=(0, 15), ipady=10, ipadx=15)
        
        # Frame per input
        input_frame = tk.Frame(friend_frame, bg=self.colors['frame_bg'])
        input_frame.pack(fill='x', pady=5)
        
        tk.Label(input_frame, text="RIOT ID:",
                bg=self.colors['frame_bg'],
                fg=self.colors['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(side='left', padx=(0, 10))
        
        self.username_entry = tk.Entry(input_frame, 
                                      font=('Segoe UI', 11),
                                      bg=self.colors['secondary_bg'],
                                      fg=self.colors['text_primary'],
                                      insertbackground=self.colors['text_primary'],
                                      width=25)
        self.username_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        self.username_entry.insert(0, "NomePlayer#TAG")
        self.username_entry.bind('<FocusIn>', self.clear_placeholder)
        self.username_entry.bind('<Return>', lambda e: self.add_friend_thread())
        
        self.add_friend_btn = tk.Button(input_frame, text="Invia Richiesta",
                                       bg=self.colors['accent'],
                                       fg=self.colors['primary_bg'],
                                       font=('Segoe UI', 10, 'bold'),
                                       relief='raised',
                                       command=self.add_friend_thread)
        self.add_friend_btn.pack(side='right')
        
        # Info label
        info_label = tk.Label(friend_frame, 
                             text="Inserisci il RIOT ID completo (es. PlayerName#EUW)",
                             bg=self.colors['frame_bg'],
                             fg=self.colors['warning'],
                             font=('Segoe UI', 9))
        info_label.pack(pady=(10, 0))
    
    def create_csv_section(self, parent):
        """Crea la sezione per importazione CSV"""
        csv_frame = tk.LabelFrame(parent, 
                                 text="Importazione Batch da CSV",
                                 bg=self.colors['frame_bg'],
                                 fg=self.colors['accent'],
                                 font=('Segoe UI', 11, 'bold'),
                                 relief='solid',
                                 bd=1)
        csv_frame.pack(fill='x', pady=(0, 15), ipady=10, ipadx=15)
        
        # Selezione file
        file_frame = tk.Frame(csv_frame, bg=self.colors['frame_bg'])
        file_frame.pack(fill='x', pady=5)
        
        tk.Label(file_frame, text="File CSV:",
                bg=self.colors['frame_bg'],
                fg=self.colors['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(side='left', padx=(0, 10))
        
        self.csv_path_var = tk.StringVar()
        self.csv_entry = tk.Entry(file_frame, 
                                 textvariable=self.csv_path_var,
                                 font=('Segoe UI', 10),
                                 bg=self.colors['secondary_bg'],
                                 fg=self.colors['text_primary'],
                                 insertbackground=self.colors['text_primary'])
        self.csv_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(file_frame, text="Sfoglia",
                              bg=self.colors['button_bg'],
                              fg=self.colors['text_primary'],
                              font=('Segoe UI', 9, 'bold'),
                              command=self.browse_csv_file)
        browse_btn.pack(side='right')
        
        # Configurazione colonna
        col_frame = tk.Frame(csv_frame, bg=self.colors['frame_bg'])
        col_frame.pack(fill='x', pady=5)
        
        tk.Label(col_frame, text="Nome Colonna:",
                bg=self.colors['frame_bg'],
                fg=self.colors['text_primary'],
                font=('Segoe UI', 10, 'bold')).pack(side='left', padx=(0, 10))
        
        self.column_var = tk.StringVar(value="Riot ID")
        col_entry = tk.Entry(col_frame, 
                            textvariable=self.column_var,
                            font=('Segoe UI', 10),
                            bg=self.colors['secondary_bg'],
                            fg=self.colors['text_primary'],
                            width=20)
        col_entry.pack(side='left')
        
        # Bottone importazione
        import_frame = tk.Frame(csv_frame, bg=self.colors['frame_bg'])
        import_frame.pack(pady=(10, 0))
        
        self.import_btn = tk.Button(import_frame, text="Importa e Invia Richieste",
                                   bg=self.colors['accent'],
                                   fg=self.colors['primary_bg'],
                                   font=('Segoe UI', 10, 'bold'),
                                   command=self.import_csv_thread)
        self.import_btn.pack()
    
    def create_friends_list_section(self, parent):
        """Crea la sezione lista amici"""
        friends_frame = tk.LabelFrame(parent, 
                                     text="Lista Amici",
                                     bg=self.colors['frame_bg'],
                                     fg=self.colors['accent'],
                                     font=('Segoe UI', 11, 'bold'),
                                     relief='solid',
                                     bd=1)
        friends_frame.pack(fill='both', expand=True, ipady=10, ipadx=15)
        
        # Toolbar
        toolbar = tk.Frame(friends_frame, bg=self.colors['frame_bg'])
        toolbar.pack(fill='x', pady=(0, 10))
        
        self.refresh_btn = tk.Button(toolbar, text="Aggiorna Lista",
                                    bg=self.colors['button_bg'],
                                    fg=self.colors['text_primary'],
                                    font=('Segoe UI', 9, 'bold'),
                                    command=self.refresh_friends_thread)
        self.refresh_btn.pack(side='left', padx=(0, 10))
        
        self.remove_all_btn = tk.Button(toolbar, text="Rimuovi Tutti",
                                       bg=self.colors['error'],
                                       fg=self.colors['text_primary'],
                                       font=('Segoe UI', 9, 'bold'),
                                       command=self.remove_all_friends_thread)
        self.remove_all_btn.pack(side='left')
        
        # Area lista amici
        self.friends_text = scrolledtext.ScrolledText(
            friends_frame,
            font=('Consolas', 10),
            bg=self.colors['secondary_bg'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            selectbackground=self.colors['accent'],
            selectforeground=self.colors['primary_bg'],
            wrap='word',
            height=12
        )
        self.friends_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Statistiche
        self.stats_label = tk.Label(friends_frame, 
                                   text="Statistiche: 0 amici caricati",
                                   bg=self.colors['frame_bg'],
                                   fg=self.colors['text_secondary'],
                                   font=('Segoe UI', 9))
        self.stats_label.pack()
    
    def create_footer(self, parent):
        """Crea il footer"""
        footer_frame = tk.Frame(parent, bg=self.colors['primary_bg'])
        footer_frame.pack(fill='x', pady=(15, 0))
        
        tk.Label(footer_frame, 
                text="Sviluppato con le API LCU di League of Legends",
                bg=self.colors['primary_bg'],
                fg=self.colors['text_secondary'],
                font=('Segoe UI', 8)).pack()
    
    def toggle_debug_console(self):
        """Mostra/nasconde la console di debug"""
        if self.debug_window is None or not self.debug_window.winfo_exists():
            self.create_debug_console()
        else:
            self.debug_window.destroy()
            self.debug_window = None
    
    def create_debug_console(self):
        """Crea finestra debug"""
        self.debug_window = tk.Toplevel(self.root)
        self.debug_window.title("Debug Console - LoL Friends Manager")
        self.debug_window.geometry("700x500")
        self.debug_window.configure(bg=self.colors['primary_bg'])
        
        debug_frame = tk.Frame(self.debug_window, bg=self.colors['primary_bg'])
        debug_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header console
        header = tk.Frame(debug_frame, bg=self.colors['frame_bg'], relief='solid', bd=1)
        header.pack(fill='x', pady=(0, 10), ipady=5)
        
        tk.Label(header, text="Console di Debug",
                bg=self.colors['frame_bg'],
                fg=self.colors['accent'],
                font=('Segoe UI', 12, 'bold')).pack(side='left', padx=10)
        
        clear_btn = tk.Button(header, text="Pulisci",
                             bg=self.colors['button_bg'],
                             fg=self.colors['text_primary'],
                             font=('Segoe UI', 9),
                             command=self.clear_debug)
        clear_btn.pack(side='right', padx=10)
        
        # Area di testo debug
        self.debug_text = scrolledtext.ScrolledText(
            debug_frame,
            font=('Consolas', 9),
            bg=self.colors['secondary_bg'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['text_primary'],
            wrap='word'
        )
        self.debug_text.pack(fill='both', expand=True)
        
        self.log_debug("Debug console inizializzata")
        self.log_debug("I messaggi di debug appariranno qui")
    
    def clear_debug(self):
        """Pulisce la console di debug"""
        if hasattr(self, 'debug_text') and self.debug_text.winfo_exists():
            self.debug_text.delete(1.0, tk.END)
            self.log_debug("Console pulita")
    
    def log_debug(self, message):
        """Aggiunge messaggio alla console debug"""
        if hasattr(self, 'debug_text') and self.debug_text.winfo_exists():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.debug_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.debug_text.see(tk.END)
    
    def clear_placeholder(self, event):
        """Pulisce il placeholder dall'entry"""
        if self.username_entry.get() == "NomePlayer#TAG":
            self.username_entry.delete(0, tk.END)
    
    def update_status(self, message, color_type="info"):
        """Aggiorna status con colori"""
        color_map = {
            "success": self.colors['success'],
            "error": self.colors['error'],
            "warning": self.colors['warning'],
            "info": self.colors['text_secondary']
        }
        
        color = color_map.get(color_type, self.colors['text_primary'])
        
        def update_ui():
            if self.status_label:
                self.status_label.config(text=message, fg=color)
        
        self.root.after(0, update_ui)
        self.log_debug(f"[{color_type.upper()}] {message}")
    
    def show_progress(self):
        """Mostra barra di progresso"""
        if self.progress and self.stats_label:
            self.progress.pack(fill='x', pady=10, before=self.stats_label)
            self.progress.start(10)
    
    def hide_progress(self):
        """Nasconde barra di progresso"""
        if self.progress:
            self.progress.stop()
            self.progress.pack_forget()
    
    def browse_csv_file(self):
        """Seleziona file CSV"""
        filepath = filedialog.askopenfilename(
            title="Seleziona file CSV",
            filetypes=[("File CSV", "*.csv"), ("Tutti i file", "*.*")]
        )
        
        if filepath:
            self.csv_path_var.set(filepath)
            self.analyze_csv_headers(filepath)
    
    def analyze_csv_headers(self, filepath):
        """Analizza headers CSV"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                headers = next(reader)
                
                self.log_debug(f"Headers CSV trovati: {', '.join(headers)}")
                
                # Auto-detect colonna RIOT ID
                for header in headers:
                    if any(term in header.lower() for term in ['riot id', 'riotid', 'riot_id']):
                        self.column_var.set(header)
                        self.log_debug(f"Colonna RIOT ID auto-rilevata: {header}")
                        break
                        
        except Exception as e:
            self.update_status(f"Errore lettura CSV: {str(e)}", "error")
    
    def check_lol_running(self):
        """Verifica client LoL"""
        self.update_status("Ricerca client in corso...", "info")
        
        try:
            possible_paths = [
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Riot Games', 'League of Legends'),
                os.path.join('C:', os.sep, 'Riot Games', 'League of Legends'),
                os.path.join('D:', os.sep, 'Riot Games', 'League of Legends'),
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'Riot Games', 'League of Legends'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'Riot Games', 'League of Legends'),
            ]
            
            for path in possible_paths:
                lockfile_path = os.path.join(path, 'lockfile')
                if os.path.exists(lockfile_path):
                    try:
                        with open(lockfile_path, 'r') as f:
                            parts = f.read().strip().split(':')
                            if len(parts) >= 4:
                                self.port = parts[2] 
                                self.token = parts[3]
                                
                                self.update_status(f"Client connesso su porta {self.port}", "success")
                                
                                if not hasattr(self, 'initial_load_done'):
                                    self.initial_load_done = True
                                    self.root.after(1000, self.refresh_friends_thread)
                                
                                return True
                                
                    except Exception as e:
                        self.log_debug(f"Errore lettura lockfile {lockfile_path}: {str(e)}")
                        continue
            
            self.update_status("Client non trovato o non in esecuzione", "warning")
            return False
            
        except Exception as e:
            self.update_status(f"Errore ricerca client: {str(e)}", "error")
            return False
    
    def make_lcu_request(self, method, endpoint, data=None):
        """Richiesta LCU"""
        try:
            if not self.port or not self.token:
                return None
                
            auth = base64.b64encode(f"riot:{self.token}".encode('ascii')).decode('ascii')
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json", 
                "Authorization": f"Basic {auth}"
            }
            
            url = f"https://127.0.0.1:{self.port}{endpoint}"
            
            self.log_debug(f"API {method} {endpoint}")
            
            response = None
            if method == "GET":
                response = requests.get(url, headers=headers, verify=False, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, verify=False, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, verify=False, timeout=10)
            
            if response:
                self.log_debug(f"Risposta: {response.status_code}")
            
            return response
            
        except requests.exceptions.ConnectionError:
            self.log_debug("Errore connessione al client")
            return None
        except Exception as e:
            self.log_debug(f"Errore richiesta API: {str(e)}")
            return None
    
    def add_friend_thread(self):
        """Thread per aggiungere amico"""
        if not self.validate_riot_id():
            return
            
        self.add_friend_btn.config(state=tk.DISABLED)
        self.show_progress()
        
        thread = threading.Thread(target=self.add_friend, daemon=True)
        thread.start()
    
    def validate_riot_id(self):
        """Valida formato RIOT ID"""
        riot_id = self.username_entry.get().strip()
        
        if not riot_id or riot_id == "NomePlayer#TAG":
            self.update_status("Inserisci un RIOT ID valido", "warning")
            return False
            
        if "#" not in riot_id:
            self.update_status("Formato non valido. Usa: Nome#TAG", "error")
            return False
            
        parts = riot_id.split('#')
        if len(parts) != 2 or not parts[0] or not parts[1]:
            self.update_status("RIOT ID malformato", "error")
            return False
            
        return True
    
    def add_friend(self):
        """Aggiunge un singolo amico"""
        try:
            if not self.port or not self.token:
                self.update_status("Client non connesso", "error")
                return
                
            riot_id = self.username_entry.get().strip()
            game_name, tag_line = riot_id.split('#', 1)
            
            self.update_status(f"Invio richiesta a {riot_id}...", "info")
            
            endpoint = "/lol-chat/v2/friend-requests"
            data = {
                "summonerId": "",
                "icon": "",
                "id": "",
                "name": "",
                "pid": "",
                "puuid": "",
                "gameName": game_name,
                "tagLine": tag_line,
                "note": "",
                "direction": "out"
            }
            
            response = self.make_lcu_request("POST", endpoint, data)
            
            if response and response.status_code in [200, 201, 204]:
                self.update_status(f"Richiesta inviata a {riot_id}!", "success")
                self.root.after(0, lambda: self.username_entry.delete(0, tk.END))
                self.root.after(2000, self.refresh_friends_thread)
            else:
                error_msg = "Errore sconosciuto"
                if response:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", f"HTTP {response.status_code}")
                    except:
                        error_msg = f"HTTP {response.status_code}"
                        
                self.update_status(f"Errore: {error_msg}", "error")
                
        except Exception as e:
            self.update_status(f"Errore aggiunta amico: {str(e)}", "error")
        finally:
            self.hide_progress()
            self.root.after(0, lambda: self.add_friend_btn.config(state=tk.NORMAL))
    
    def import_csv_thread(self):
        """Thread importazione CSV"""
        csv_path = self.csv_path_var.get()
        if not csv_path or not os.path.exists(csv_path):
            messagebox.showerror("Errore", "Seleziona un file CSV valido")
            return
            
        self.import_btn.config(state=tk.DISABLED)
        self.show_progress()
        
        thread = threading.Thread(target=self.import_csv_friends, daemon=True)
        thread.start()
    
    def import_csv_friends(self):
        """Importa amici da CSV"""
        try:
            if not self.port or not self.token:
                self.update_status("Client non connesso", "error")
                return
                
            csv_path = self.csv_path_var.get()
            column_name = self.column_var.get()
            
            # Leggi RIOT IDs dal CSV
            riot_ids = []
            try:
                with open(csv_path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    
                    if column_name not in reader.fieldnames:
                        self.update_status(f"Colonna '{column_name}' non trovata", "error")
                        return
                    
                    for row in reader:
                        riot_id = row[column_name].strip()
                        if riot_id and "#" in riot_id:
                            riot_ids.append(riot_id)
                            
            except Exception as e:
                self.update_status(f"Errore lettura CSV: {str(e)}", "error")
                return
            
            if not riot_ids:
                self.update_status("Nessun RIOT ID valido nel CSV", "warning")
                return
            
            self.update_status(f"Trovati {len(riot_ids)} RIOT ID nel CSV", "info")
            
            # Invia richieste
            self.sent_invites = []
            for i, riot_id in enumerate(riot_ids):
                self.update_status(f"Invio {i+1}/{len(riot_ids)}: {riot_id}", "info")
                result = self.send_friend_request_bulk(riot_id)
                self.sent_invites.append((riot_id, result))
                time.sleep(1)
            
            self.show_import_report()
            self.root.after(2000, self.refresh_friends_thread)
            
        except Exception as e:
            self.update_status(f"Errore importazione: {str(e)}", "error")
        finally:
            self.hide_progress()
            self.root.after(0, lambda: self.import_btn.config(state=tk.NORMAL))
    
    def send_friend_request_bulk(self, riot_id):
        """Invia richiesta amicizia per importazione bulk"""
        try:
            if "#" not in riot_id:
                return "Formato non valido"
                
            game_name, tag_line = riot_id.split('#', 1)
            
            endpoint = "/lol-chat/v2/friend-requests"
            data = {
                "summonerId": "", "icon": "", "id": "", "name": "", "pid": "", "puuid": "",
                "gameName": game_name, "tagLine": tag_line, "note": "", "direction": "out"
            }
            
            response = self.make_lcu_request("POST", endpoint, data)
            
            if response and response.status_code in [200, 201, 204]:
                return "Inviata con successo"
            else:
                if response:
                    try:
                        error_data = response.json()
                        return f"Errore: {error_data.get('message', f'HTTP {response.status_code}')}"
                    except:
                        return f"HTTP {response.status_code}"
                return "Errore connessione"
                
        except Exception as e:
            return f"Errore: {str(e)}"
    
    def show_import_report(self):
        """Mostra report importazione"""
        report_window = tk.Toplevel(self.root)
        report_window.title("Report Importazione Amici")
        report_window.geometry("600x500")
        report_window.configure(bg=self.colors['primary_bg'])
        
        main_frame = tk.Frame(report_window, bg=self.colors['primary_bg'])
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Header
        tk.Label(main_frame, text="Report Importazione Completata",
                bg=self.colors['primary_bg'],
                fg=self.colors['accent'],
                font=('Segoe UI', 14, 'bold')).pack(pady=(0, 15))
        
        # Statistiche
        success_count = sum(1 for _, result in self.sent_invites if "successo" in result)
        
        stats_text = f"Successi: {success_count} | Falliti: {len(self.sent_invites) - success_count} | Totale: {len(self.sent_invites)}"
        tk.Label(main_frame, text=stats_text,
                bg=self.colors['primary_bg'],
                fg=self.colors['success'],
                font=('Segoe UI', 11, 'bold')).pack(pady=(0, 15))
        
        # Area dettagli
        report_text = scrolledtext.ScrolledText(
            main_frame,
            font=('Consolas', 10),
            bg=self.colors['secondary_bg'],
            fg=self.colors['text_primary'],
            height=15
        )
        report_text.pack(fill='both', expand=True, pady=(0, 15))
        
        for i, (riot_id, result) in enumerate(self.sent_invites):
            report_text.insert(tk.END, f"{i+1:3d}. {riot_id:<20} -> {result}\n")
        
        # Bottoni
        button_frame = tk.Frame(main_frame, bg=self.colors['primary_bg'])
        button_frame.pack(fill='x')
        
        tk.Button(button_frame, text="Salva Report",
                 bg=self.colors['button_bg'],
                 fg=self.colors['text_primary'],
                 font=('Segoe UI', 10),
                 command=lambda: self.save_report(self.sent_invites, "import")).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="Chiudi",
                 bg=self.colors['accent'],
                 fg=self.colors['primary_bg'],
                 font=('Segoe UI', 10, 'bold'),
                 command=report_window.destroy).pack(side='right')
        
        self.update_status(f"Importazione completata: {success_count}/{len(self.sent_invites)}", "success")
    
    def refresh_friends_thread(self):
        """Thread aggiornamento lista amici"""
        if self.refresh_btn:
            self.refresh_btn.config(state=tk.DISABLED)
        self.show_progress()
        
        thread = threading.Thread(target=self.refresh_friends_list, daemon=True)
        thread.start()
    
    def refresh_friends_list(self):
        """Aggiorna lista amici"""
        try:
            if not self.port or not self.token:
                self.update_status("Client non connesso", "error")
                return
                
            endpoint = "/lol-chat/v1/friends"
            response = self.make_lcu_request("GET", endpoint)
            
            def update_friends_ui(friends_data=None):
                if self.friends_text:
                    self.friends_text.delete(1.0, tk.END)
                    
                    if not friends_data:
                        self.friends_text.insert(tk.END, "Lista amici vuota\n")
                        self.friends_text.insert(tk.END, "Aggiungi alcuni amici per iniziare!")
                        if self.stats_label:
                            self.stats_label.config(text="Statistiche: 0 amici")
                        return
                    
                    # Header della lista
                    self.friends_text.insert(tk.END, f"LISTA AMICI ({len(friends_data)} totali)\n")
                    self.friends_text.insert(tk.END, "=" * 50 + "\n\n")
                    
                    for i, friend in enumerate(friends_data, 1):
                        name = friend.get("name", "Unknown")
                        game_name = friend.get("gameName", "")
                        game_tag = friend.get("gameTag", "")
                        status = friend.get("gameStatus", "offline")
                        status_msg = friend.get("statusMessage", "")
                        
                        display_name = f"{game_name}#{game_tag}" if game_name and game_tag else name
                        
                        self.friends_text.insert(tk.END, f"{i:2d}. {display_name}\n")
                        self.friends_text.insert(tk.END, f"     Status: {status.title()}\n")
                        
                        if status_msg:
                            self.friends_text.insert(tk.END, f"     Messaggio: {status_msg}\n")
                        
                        self.friends_text.insert(tk.END, "\n")
                    
                    # Statistiche
                    online_count = sum(1 for f in friends_data if f.get('gameStatus') in ['online', 'inGame'])
                    if self.stats_label:
                        self.stats_label.config(text=f"Statistiche: {len(friends_data)} amici totali, {online_count} online")
            
            if response and response.status_code == 200:
                friends_data = response.json()
                self.root.after(0, lambda: update_friends_ui(friends_data))
                self.update_status(f"Lista amici aggiornata ({len(friends_data)} amici)", "success")
            else:
                self.root.after(0, lambda: update_friends_ui(None))
                self.update_status("Errore aggiornamento lista amici", "error")
                
        except Exception as e:
            self.update_status(f"Errore: {str(e)}", "error")
        finally:
            self.hide_progress()
            if self.refresh_btn:
                self.root.after(0, lambda: self.refresh_btn.config(state=tk.NORMAL))
    
    def remove_all_friends_thread(self):
        """Thread rimozione tutti gli amici"""
        if self.remove_all_btn:
            self.remove_all_btn.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.confirm_remove_all, daemon=True)
        thread.start()
    
    def confirm_remove_all(self):
        """Conferma rimozione tutti gli amici"""
        try:
            if not self.port or not self.token:
                self.update_status("Client non connesso", "error")
                return
                
            response = self.make_lcu_request("GET", "/lol-chat/v1/friends")
            if not response or response.status_code != 200:
                self.update_status("Impossibile ottenere lista amici", "error")
                return
                
            friends_data = response.json()
            if not friends_data:
                messagebox.showinfo("Informazione", "Non hai amici nella lista da rimuovere.")
                return
            
            confirm = messagebox.askyesno(
                "Conferma Rimozione",
                f"Sei sicuro di voler rimuovere tutti i {len(friends_data)} amici?\n\n"
                "Questa azione NON puo essere annullata!",
                icon="warning"
            )
            
            if confirm:
                self.show_progress()
                self.perform_remove_all_friends(friends_data)
            else:
                self.update_status("Rimozione annullata", "info")
                
        except Exception as e:
            self.update_status(f"Errore: {str(e)}", "error")
        finally:
            if self.remove_all_btn:
                self.root.after(0, lambda: self.remove_all_btn.config(state=tk.NORMAL))
    
    def perform_remove_all_friends(self, friends_data):
        """Esegue rimozione di tutti gli amici"""
        try:
            results = []
            total = len(friends_data)
            
            for i, friend in enumerate(friends_data):
                friend_id = friend.get("id")
                game_name = friend.get("gameName", "")
                game_tag = friend.get("gameTag", "")
                
                display_name = f"{game_name}#{game_tag}" if game_name and game_tag else friend.get("name", "Unknown")
                
                self.update_status(f"Rimozione {i+1}/{total}: {display_name}", "info")
                
                if not friend_id:
                    results.append((display_name, "ID non trovato"))
                    continue
                
                endpoint = f"/lol-chat/v1/friends/{friend_id}"
                response = self.make_lcu_request("DELETE", endpoint)
                
                if response and response.status_code in [200, 204]:
                    results.append((display_name, "Rimosso"))
                else:
                    status_code = response.status_code if response else "N/A"
                    results.append((display_name, f"Errore {status_code}"))
                
                time.sleep(0.5)
            
            self.show_removal_report(results)
            self.root.after(2000, self.refresh_friends_thread)
            
        except Exception as e:
            self.update_status(f"Errore rimozione: {str(e)}", "error")
        finally:
            self.hide_progress()
            if self.remove_all_btn:
                self.root.after(0, lambda: self.remove_all_btn.config(state=tk.NORMAL))
    
    def show_removal_report(self, results):
        """Mostra report rimozione"""
        success_count = sum(1 for _, result in results if result == "Rimosso")
        
        report_window = tk.Toplevel(self.root)
        report_window.title("Report Rimozione Amici")
        report_window.geometry("600x500")
        report_window.configure(bg=self.colors['primary_bg'])
        
        main_frame = tk.Frame(report_window, bg=self.colors['primary_bg'])
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        tk.Label(main_frame, text="Report Rimozione Completata",
                bg=self.colors['primary_bg'],
                fg=self.colors['error'],
                font=('Segoe UI', 14, 'bold')).pack(pady=(0, 15))
        
        stats_text = f"Rimossi: {success_count} | Falliti: {len(results) - success_count} | Totale: {len(results)}"
        tk.Label(main_frame, text=stats_text,
                bg=self.colors['primary_bg'],
                fg=self.colors['text_primary'],
                font=('Segoe UI', 11)).pack(pady=(0, 15))
        
        report_text = scrolledtext.ScrolledText(main_frame, height=15, 
                                              bg=self.colors['secondary_bg'], fg=self.colors['text_primary'])
        report_text.pack(fill='both', expand=True, pady=(0, 15))
        
        for i, (name, result) in enumerate(results, 1):
            report_text.insert(tk.END, f"{i:3d}. {name:<25} -> {result}\n")
        
        button_frame = tk.Frame(main_frame, bg=self.colors['primary_bg'])
        button_frame.pack(fill='x')
        
        tk.Button(button_frame, text="Salva Report",
                 bg=self.colors['button_bg'],
                 fg=self.colors['text_primary'],
                 command=lambda: self.save_report(results, "removal")).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="Chiudi",
                 bg=self.colors['accent'],
                 fg=self.colors['primary_bg'],
                 font=('Segoe UI', 10, 'bold'),
                 command=report_window.destroy).pack(side='right')
        
        self.update_status(f"Rimozione completata: {success_count}/{len(results)}", "success")
    
    def save_report(self, results, operation_type):
        """Salva report su file"""
        try:
            operation_name = "importazione" if operation_type == "import" else "rimozione"
            
            filepath = filedialog.asksaveasfilename(
                title=f"Salva report {operation_name}",
                defaultextension=".txt",
                filetypes=[("File di testo", "*.txt"), ("Tutti i file", "*.*")],
                initialfile=f"lol_friends_{operation_type}_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
            )
            
            if not filepath:
                return
            
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(f"### Report {operation_name.title()} Amici League of Legends ###\n")
                file.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                success_count = sum(1 for _, result in results if 
                                  ("successo" in result if operation_type == "import" else result == "Rimosso"))
                file.write(f"Operazioni completate con successo: {success_count}/{len(results)}\n\n")
                
                file.write(f"Dettagli {operation_name}:\n")
                file.write("-" * 50 + "\n")
                
                for i, (name, result) in enumerate(results, 1):
                    file.write(f"{i:3d}. {name:<25} -> {result}\n")
            
            messagebox.showinfo("Salvataggio Completato", 
                               f"Report salvato con successo:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore salvataggio report: {str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = LoLFriendsManager(root)
        root.mainloop()
    except Exception as e:
        error_root = tk.Tk()
        error_root.title("Errore - LoL Friends Manager")
        error_root.geometry("500x300")
        error_root.configure(bg="#0A1428")
        
        error_frame = tk.Frame(error_root, bg="#0A1428")
        error_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(error_frame, text="Si e verificato un errore critico:", 
                font=('Segoe UI', 12, 'bold'), fg="#CF3030", bg="#0A1428").pack(pady=(0, 10))
        
        tk.Label(error_frame, text=str(e), font=('Segoe UI', 10), 
                fg="#F0E6D2", bg="#0A1428", wraplength=450).pack(pady=10)
        
        suggestions = [
            "• Verifica che League of Legends sia installato",
            "• Assicurati che il client di LoL sia in esecuzione", 
            "• Controlla i permessi del programma",
            "• Prova a riavviare come amministratore"
        ]
        
        for suggestion in suggestions:
            tk.Label(error_frame, text=suggestion, font=('Segoe UI', 9),
                    fg="#A09B8C", bg="#0A1428").pack(anchor='w', pady=1)
        
        tk.Button(error_frame, text="Riprova", font=('Segoe UI', 10, 'bold'),
                 bg="#C8AA6E", fg="#0A1428", command=error_root.destroy).pack(pady=15)
        
        error_root.mainloop()