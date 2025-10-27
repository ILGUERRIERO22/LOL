import tkinter as tk
from tkinter import ttk, messagebox
import requests
import base64
import json
import urllib3
import os
import platform
import threading
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ModernProgressBar:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent)
        self.progress = ttk.Progressbar(
            self.frame, 
            mode='indeterminate',
            length=300,
            style="Modern.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=8)
        self.frame.pack_forget()
    
    def show(self):
        self.frame.pack(pady=8)
        self.progress.start(8)
    
    def hide(self):
        self.progress.stop()
        self.frame.pack_forget()

class RiotIDChanger:
    def __init__(self, root):
        self.root = root
        self.root.title("Riot ID Changer - League of Legends")
        self.root.configure(bg="#0A1428")
        
        # Set window size and position
        window_width = 520
        window_height = 550
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(True, True)
        self.root.minsize(520, 550)
        
        # Configure styles
        self.setup_styles()
        
        # Create UI
        self.create_ui()
        
        # Initialize progress bar
        self.progress_bar = ModernProgressBar(self.main_frame)
        
        # Variables for threading and validation state
        self.current_operation = None
        self.is_validated = False
        self.is_available = False  # Nuovo: traccia se il Riot ID è disponibile
        self.last_validated_name = ""
        self.last_validated_tag = ""

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Modern color palette
        colors = {
            'bg_primary': '#0A1428',
            'bg_secondary': '#1E2328',
            'bg_input': '#3C3C41',
            'accent': '#0AC8B9',
            'accent_hover': '#4BDEDB',
            'accent_disabled': '#1E2328',
            'text_primary': '#F0E6D2',
            'text_secondary': '#C8AA6E',
            'text_muted': '#787A8D',
            'success': '#00F5FF',
            'error': '#E74856',
            'warning': '#FFCC00'
        }
        
        # Configure widget styles
        self.style.configure("TFrame", background=colors['bg_primary'])
        
        # Labels
        self.style.configure("Header.TLabel", 
                            background=colors['bg_primary'], 
                            foreground=colors['text_secondary'], 
                            font=("Segoe UI", 20, "bold"))
        self.style.configure("Subtitle.TLabel", 
                            background=colors['bg_primary'], 
                            foreground=colors['text_muted'], 
                            font=("Segoe UI", 10))
        self.style.configure("Field.TLabel", 
                            background=colors['bg_primary'], 
                            foreground=colors['text_primary'], 
                            font=("Segoe UI", 11))
        self.style.configure("Status.TLabel", 
                            background=colors['bg_primary'], 
                            foreground=colors['text_muted'], 
                            font=("Segoe UI", 10))
        self.style.configure("Success.TLabel", 
                            background=colors['bg_primary'], 
                            foreground=colors['success'], 
                            font=("Segoe UI", 10, "bold"))
        self.style.configure("Error.TLabel", 
                            background=colors['bg_primary'], 
                            foreground=colors['error'], 
                            font=("Segoe UI", 10, "bold"))
        
        # Entries
        self.style.configure("Modern.TEntry", 
                            fieldbackground=colors['bg_input'], 
                            foreground=colors['text_primary'], 
                            borderwidth=1,
                            relief="solid",
                            insertcolor=colors['text_primary'])
        self.style.map("Modern.TEntry",
                      focuscolor=[("!focus", colors['bg_input']),
                                ("focus", colors['accent'])])
        
        # Buttons
        self.style.configure("Modern.TButton", 
                            background=colors['accent'], 
                            foreground=colors['bg_primary'], 
                            font=("Segoe UI", 11, "bold"),
                            borderwidth=0,
                            focuscolor='none')
        # Configure colors for disabled state
        self.style.map("Modern.TButton",
                      background=[("active", colors['accent_hover']), 
                                ("disabled", colors['bg_secondary'])],
                      foreground=[("active", colors['bg_primary']), 
                                ("disabled", colors['text_muted'])])
        
        self.style.configure("Secondary.TButton", 
                            background=colors['bg_secondary'], 
                            foreground=colors['text_primary'], 
                            font=("Segoe UI", 11),
                            borderwidth=1,
                            relief="solid")
        self.style.map("Secondary.TButton",
                      background=[("active", colors['bg_input']), 
                                ("disabled", colors['bg_secondary'])],
                      foreground=[("active", colors['text_primary']), 
                                ("disabled", colors['text_muted'])])
        
        # Disabled button style 
        self.style.configure("Disabled.TButton",
                            background=colors['bg_secondary'],
                            foreground=colors['text_muted'],
                            font=("Segoe UI", 11),
                            borderwidth=1,
                            relief="solid")
        self.style.map("Disabled.TButton",
                      background=[("active", colors['bg_secondary']), 
                                ("disabled", colors['bg_secondary'])],
                      foreground=[("active", colors['text_muted']), 
                                ("disabled", colors['text_muted'])])
        
        # Progress bar
        self.style.configure("Modern.Horizontal.TProgressbar",
                            background=colors['accent'],
                            troughcolor=colors['bg_secondary'],
                            borderwidth=0,
                            lightcolor=colors['accent'],
                            darkcolor=colors['accent'])
        
        # Separator
        self.style.configure("Modern.TSeparator",
                            background=colors['bg_secondary'])

    def create_ui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding=25)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        self.create_header()
        
        # Separator
        separator1 = ttk.Separator(self.main_frame, orient='horizontal', style="Modern.TSeparator")
        separator1.pack(fill=tk.X, pady=15)
        
        # Input section
        self.create_input_section()
        
        # Separator
        separator2 = ttk.Separator(self.main_frame, orient='horizontal', style="Modern.TSeparator")
        separator2.pack(fill=tk.X, pady=15)
        
        # Buttons section
        self.create_buttons_section()
        
        # Status section
        self.create_status_section()

    def create_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="RIOT ID CHANGER", style="Header.TLabel")
        title_label.pack()
        
        subtitle_label = ttk.Label(header_frame, text="Cambia il tuo Riot ID per League of Legends", style="Subtitle.TLabel")
        subtitle_label.pack(pady=(5, 0))

    def create_input_section(self):
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        # Game Name
        name_container = ttk.Frame(input_frame)
        name_container.pack(fill=tk.X, pady=(0, 12))
        
        name_label = ttk.Label(name_container, text="Nome Giocatore:", style="Field.TLabel")
        name_label.pack(anchor=tk.W, pady=(0, 4))
        
        self.entry_name = ttk.Entry(name_container, 
                                   font=("Segoe UI", 12), 
                                   style="Modern.TEntry",
                                   width=40)
        self.entry_name.pack(fill=tk.X, ipady=6)
        self.add_placeholder(self.entry_name, "Es: NomeGiocatore")
        # Bind per invalidare quando cambia l'input
        self.entry_name.bind('<KeyRelease>', self.on_input_change)
        self.entry_name.bind('<FocusOut>', lambda e: [self.on_entry_focus_out(e), self.on_input_change(e)])
        
        # Game Tag
        tag_container = ttk.Frame(input_frame)
        tag_container.pack(fill=tk.X)
        
        tag_label = ttk.Label(tag_container, text="Tag:", style="Field.TLabel")
        tag_label.pack(anchor=tk.W, pady=(0, 4))
        
        self.entry_tag = ttk.Entry(tag_container, 
                                  font=("Segoe UI", 12), 
                                  style="Modern.TEntry",
                                  width=40)
        self.entry_tag.pack(fill=tk.X, ipady=6)
        self.add_placeholder(self.entry_tag, "Es: EUW")
        # Bind per invalidare quando cambia l'input
        self.entry_tag.bind('<KeyRelease>', self.on_input_change)
        self.entry_tag.bind('<FocusOut>', lambda e: [self.on_entry_focus_out(e), self.on_input_change(e)])

    def create_buttons_section(self):
        buttons_frame = ttk.Frame(self.main_frame)
        buttons_frame.pack(fill=tk.X, pady=5)
        
        # Validate button
        self.validate_button = ttk.Button(buttons_frame, 
                                         text="VERIFICA DISPONIBILITÀ", 
                                         command=self.validate_threaded,
                                         style="Secondary.TButton")
        self.validate_button.pack(fill=tk.X, pady=(0, 8), ipady=8)
        
        # Change button - inizialmente disabilitato
        self.change_button = ttk.Button(buttons_frame, 
                                       text="CAMBIA RIOT ID", 
                                       command=self.change_threaded,
                                       style="Modern.TButton",
                                       state='disabled')
        self.change_button.pack(fill=tk.X, ipady=8)

    def create_status_section(self):
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Status container
        status_container = ttk.Frame(status_frame)
        status_container.pack()
        
        self.status_var = tk.StringVar(value="Inserisci nome e tag, poi verifica la disponibilità")
        self.status_label = ttk.Label(status_container, 
                                     textvariable=self.status_var, 
                                     style="Status.TLabel")
        self.status_label.pack()

    def add_placeholder(self, entry, placeholder_text):
        entry.placeholder_text = placeholder_text
        entry.insert(0, placeholder_text)
        entry.bind('<FocusIn>', self.on_entry_focus_in)
        entry.bind('<FocusOut>', self.on_entry_focus_out)
        entry.config(foreground='#787A8D')

    def on_entry_focus_in(self, event):
        if event.widget.get() == event.widget.placeholder_text:
            event.widget.delete(0, tk.END)
            event.widget.config(foreground='#F0E6D2')

    def on_entry_focus_out(self, event):
        if event.widget.get() == '':
            event.widget.insert(0, event.widget.placeholder_text)
            event.widget.config(foreground='#787A8D')

    def on_input_change(self, event=None):
        """Chiamato quando l'input cambia - invalida la validazione precedente"""
        current_name = self.get_clean_input(self.entry_name)
        current_tag = self.get_clean_input(self.entry_tag)
        
        # Se l'input è cambiato rispetto all'ultimo validato, invalida
        if (current_name != self.last_validated_name or 
            current_tag != self.last_validated_tag):
            self.invalidate_validation()

    def invalidate_validation(self):
        """Invalida lo stato di validazione e disabilita il pulsante cambio"""
        self.is_validated = False
        self.is_available = False
        self.last_validated_name = ""
        self.last_validated_tag = ""
        self.change_button.configure(
            state='disabled', 
            text="CAMBIA RIOT ID (Verifica richiesta)",
            style="Disabled.TButton"
        )
        if hasattr(self, 'status_var'):
            if any(word in self.status_var.get().lower() for word in ["validato", "disponibile", "verificato"]):
                self.status_var.set("Verifica richiesta dopo le modifiche")
                self.status_label.configure(style="Status.TLabel")

    def validate_availability_state(self, game_name, game_tag, is_available):
        """Abilita il pulsante cambio SOLO se il Riot ID è disponibile"""
        self.is_validated = True
        self.is_available = is_available
        self.last_validated_name = game_name
        self.last_validated_tag = game_tag
        
        if is_available:
            # Riot ID disponibile - PULSANTE ABILITATO
            self.change_button.configure(
                state='normal', 
                text="CAMBIA RIOT ID ✅ DISPONIBILE",
                style="Modern.TButton"
            )
        else:
            # Riot ID NON disponibile - PULSANTE DISABILITATO
            self.change_button.configure(
                state='disabled', 
                text="❌ RIOT ID NON DISPONIBILE",
                style="Disabled.TButton"
            )

    def get_lockfile_path(self):
        """Ottiene il percorso del lockfile in base al sistema operativo"""
        system = platform.system()
        if system == "Windows":
            return "C:/Riot Games/League of Legends/lockfile"
        elif system == "Darwin":  # macOS
            return "/Applications/League of Legends.app/Contents/LoL/lockfile"
        else:  # Linux
            home = os.path.expanduser("~")
            return f"{home}/.wine/drive_c/Riot Games/League of Legends/lockfile"

    def get_lcu_auth(self):
        try:
            lockfile_path = self.get_lockfile_path()
            if not os.path.exists(lockfile_path):
                self.show_error("File lockfile non trovato. Assicurati che il client di League sia in esecuzione.")
                return None, None
                
            with open(lockfile_path, "r") as lockfile:
                data = lockfile.read().split(":")
                if len(data) < 4:
                    self.show_error("Formato lockfile non valido.")
                    return None, None
                port = data[2]
                token = data[3]
                auth = base64.b64encode(f"riot:{token}".encode()).decode()
                return port, auth
        except PermissionError:
            self.show_error("Permesso negato per leggere il lockfile. Esegui come amministratore.")
            return None, None
        except Exception as e:
            self.show_error(f"Errore nella lettura del lockfile: {str(e)}")
            return None, None

    def send_request(self, port, auth, method, endpoint, payload=None, timeout=10):
        url = f"https://127.0.0.1:{port}{endpoint}"
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
        try:
            if method == "post":
                response = requests.post(url, headers=headers, json=payload, verify=False, timeout=timeout)
            elif method == "get":
                response = requests.get(url, headers=headers, verify=False, timeout=timeout)
            else:
                raise ValueError("Metodo HTTP non supportato.")
            return response
        except requests.exceptions.Timeout:
            self.show_error("Timeout della connessione. Riprova.")
            return None
        except requests.exceptions.ConnectionError:
            self.show_error("Errore di connessione. Verifica che il client sia in esecuzione.")
            return None
        except Exception as e:
            self.show_error(f"Errore di connessione: {str(e)}")
            return None

    def get_clean_input(self, entry):
        """Ottiene il valore pulito dall'entry (rimuove placeholder)"""
        value = entry.get()
        if hasattr(entry, 'placeholder_text') and value == entry.placeholder_text:
            return ""
        return value.strip()

    def validate_input(self):
        """Valida l'input dell'utente"""
        game_name = self.get_clean_input(self.entry_name)
        game_tag = self.get_clean_input(self.entry_tag)
        
        if not game_name or not game_tag:
            self.show_error("Inserisci un nome e un tag validi.")
            return None, None
            
        if len(game_name) < 3 or len(game_name) > 16:
            self.show_error("Il nome deve essere tra 3 e 16 caratteri.")
            return None, None
            
        if len(game_tag) < 3 or len(game_tag) > 5:
            self.show_error("Il tag deve essere tra 3 e 5 caratteri.")
            return None, None
            
        return game_name, game_tag

    def validate_riot_id(self, port, auth, game_name, game_tag):
        endpoint = "/lol-summoner/v1/validate-alias"
        payload = {
            "gameName": game_name,
            "tagLine": game_tag
        }
        
        response = self.send_request(port, auth, "post", endpoint, payload)
        if response and response.status_code == 200:
            result = response.json()
            
            # Controlla se la richiesta è riuscita
            if result.get("isSuccess", False):
                # Il Riot ID è valido e disponibile
                return True, True, "Riot ID disponibile e pronto per il cambio!"
            else:
                # Il Riot ID non è disponibile (già in uso o non valido)
                error_msg = result.get('message', 'Riot ID non disponibile o non valido')
                return True, False, f"Verifica completata: {error_msg}"
        elif response:
            return False, False, f"Errore del server: {response.status_code}"
        else:
            return False, False, "Errore di connessione durante la verifica"

    def change_riot_id(self, port, auth, game_name, game_tag):
        endpoint = "/lol-summoner/v1/save-alias"
        payload = {
            "gameName": game_name,
            "tagLine": game_tag
        }
        
        response = self.send_request(port, auth, "post", endpoint, payload)
        if response and response.status_code == 200:
            result = response.json()
            if result.get("isSuccess", False):
                return True, f"Riot ID cambiato con successo in {game_name}#{game_tag}!"
            else:
                error_msg = result.get('message', 'Errore sconosciuto')
                return False, f"Errore nel cambio: {error_msg}"
        elif response:
            return False, f"Errore del server: {response.status_code}"
        else:
            return False, "Errore di connessione"

    def validate_threaded(self):
        if self.current_operation:
            return
        threading.Thread(target=self._validate_process, daemon=True).start()

    def _validate_process(self):
        self.current_operation = "validate"
        self.set_loading_state(True, "Verifica disponibilità in corso...")
        
        try:
            game_name, game_tag = self.validate_input()
            if not game_name or not game_tag:
                return
                
            port, auth = self.get_lcu_auth()
            if not port or not auth:
                return
                
            connection_ok, is_available, message = self.validate_riot_id(port, auth, game_name, game_tag)
            
            self.root.after(0, self._handle_validate_result, connection_ok, is_available, message, game_name, game_tag)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Errore inaspettato: {str(e)}")
        finally:
            self.root.after(0, lambda: self.set_loading_state(False))
            self.current_operation = None

    def _handle_validate_result(self, connection_ok, is_available, message, game_name, game_tag):
        if connection_ok:
            if is_available:
                self.show_success(message)
                self.validate_availability_state(game_name, game_tag, True)
                messagebox.showinfo("✅ Disponibile!", 
                                  f"Ottimo! Il Riot ID {game_name}#{game_tag} è disponibile!\n\n"
                                  "Ora puoi cliccare 'CAMBIA RIOT ID' per procedere.")
            else:
                # Riot ID non disponibile ma connessione ok
                self.show_error(message)
                self.validate_availability_state(game_name, game_tag, False)
                messagebox.showwarning("❌ Non Disponibile", 
                                     f"Il Riot ID {game_name}#{game_tag} non è disponibile.\n\n"
                                     "Prova con un nome diverso.")
        else:
            # Errore di connessione
            self.show_error(message)
            self.invalidate_validation()

    def change_threaded(self):
        if self.current_operation:
            return
            
        # Controlla se è stato validato E se è disponibile
        if not self.is_validated or not self.is_available:
            if not self.is_validated:
                messagebox.showwarning("⚠️ Verifica Richiesta", 
                                     "Devi prima verificare la disponibilità del Riot ID prima di poterlo cambiare.")
            elif not self.is_available:
                messagebox.showwarning("⚠️ Non Disponibile", 
                                     "Il Riot ID non è disponibile. Verifica nuovamente con un nome diverso.")
            return
            
        # Controlla se l'input corrente corrisponde a quello validato
        current_name = self.get_clean_input(self.entry_name)
        current_tag = self.get_clean_input(self.entry_tag)
        
        if (current_name != self.last_validated_name or 
            current_tag != self.last_validated_tag):
            messagebox.showwarning("⚠️ Verifica Richiesta", 
                                 "L'input è cambiato dopo l'ultima verifica. Verifica nuovamente la disponibilità.")
            self.invalidate_validation()
            return
            
        threading.Thread(target=self._change_process, daemon=True).start()

    def _change_process(self):
        self.current_operation = "change"
        
        try:
            # Usa i valori già validati
            game_name = self.last_validated_name
            game_tag = self.last_validated_tag
                
            port, auth = self.get_lcu_auth()
            if not port or not auth:
                return
            
            # Ask for confirmation on main thread
            self.root.after(0, self._ask_confirmation, game_name, game_tag, port, auth)
            
        except Exception as e:
            self.root.after(0, self.show_error, f"Errore inaspettato: {str(e)}")
            self.current_operation = None

    def _ask_confirmation(self, game_name, game_tag, port, auth):
        if messagebox.askyesno("Conferma", 
                              f"Sei sicuro di voler cambiare il tuo Riot ID in {game_name}#{game_tag}?\n\n"
                              "Questa operazione potrebbe non essere reversibile."):
            threading.Thread(target=self._perform_change, args=(game_name, game_tag, port, auth), daemon=True).start()
        else:
            self.current_operation = None

    def _perform_change(self, game_name, game_tag, port, auth):
        self.root.after(0, lambda: self.set_loading_state(True, "Cambio Riot ID in corso..."))
        
        try:
            success, message = self.change_riot_id(port, auth, game_name, game_tag)
            self.root.after(0, self._handle_change_result, success, message)
        except Exception as e:
            self.root.after(0, self.show_error, f"Errore inaspettato: {str(e)}")
        finally:
            self.root.after(0, lambda: self.set_loading_state(False))
            self.current_operation = None

    def _handle_change_result(self, success, message):
        if success:
            self.show_success(message)
            messagebox.showinfo("Successo", "Riot ID cambiato con successo!")
            # Clear inputs e reset validazione
            self.entry_name.delete(0, tk.END)
            self.entry_tag.delete(0, tk.END)
            self.on_entry_focus_out(type('obj', (object,), {'widget': self.entry_name})())
            self.on_entry_focus_out(type('obj', (object,), {'widget': self.entry_tag})())
            self.invalidate_validation()
        else:
            self.show_error(message)

    def set_loading_state(self, loading, message=""):
        if loading:
            self.progress_bar.show()
            self.validate_button.configure(state='disabled')
            self.change_button.configure(state='disabled')
            if message:
                self.status_var.set(message)
        else:
            self.progress_bar.hide()
            self.validate_button.configure(state='normal')
            # Riabilita il pulsante change SOLO se è validato E disponibile
            if self.is_validated and self.is_available:
                self.change_button.configure(state='normal', text="CAMBIA RIOT ID ✓ DISPONIBILE")
            elif self.is_validated and not self.is_available:
                self.change_button.configure(state='disabled', text="CAMBIA RIOT ID (Non disponibile)")
            else:
                self.change_button.configure(state='disabled', text="CAMBIA RIOT ID (Verifica richiesta)")

    def show_error(self, message):
        self.status_var.set(message)
        self.status_label.configure(style="Error.TLabel")
        self.root.after(5000, self._reset_status)

    def show_success(self, message):
        self.status_var.set(message)
        self.status_label.configure(style="Success.TLabel")
        self.root.after(5000, self._reset_status)

    def _reset_status(self):
        if self.is_validated and self.is_available:
            self.status_var.set(f"✅ {self.last_validated_name}#{self.last_validated_tag} è disponibile e pronto!")
        elif self.is_validated and not self.is_available:
            self.status_var.set(f"❌ {self.last_validated_name}#{self.last_validated_tag} non è disponibile")
        else:
            self.status_var.set("Inserisci nome e tag, poi verifica la disponibilità")
        self.status_label.configure(style="Status.TLabel")

if __name__ == "__main__":
    root = tk.Tk()
    app = RiotIDChanger(root)
    root.mainloop()