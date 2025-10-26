import json
import requests
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, Listbox, Scrollbar, VERTICAL, RIGHT, Y, END, Frame, FLAT, messagebox
import os
import base64
import urllib3
from datetime import datetime
import threading

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LoLStatusManager:
    def __init__(self):
        # Directory per i file di cronologia
        self.HISTORY_DIR = r"C:\Users\dbait\Desktop\MOD LOL\script\history"
        
        # Colori moderni con tema scuro
        self.COLORS = {
            "bg_primary": "#0a0e13",      # Sfondo principale molto scuro
            "bg_secondary": "#1e2328",    # Sfondo secondario
            "bg_tertiary": "#3c4043",     # Sfondo terziario
            "accent": "#c89b3c",          # Oro LoL
            "accent_hover": "#f0e6d2",    # Oro chiaro hover
            "text_primary": "#f0e6d2",    # Testo principale
            "text_secondary": "#cdbe91",  # Testo secondario
            "success": "#0f2027",         # Verde scuro
            "success_text": "#0ac8b9",    # Verde chiaro
            "error": "#3c1518",           # Rosso scuro
            "error_text": "#e4626f",      # Rosso chiaro
            "border": "#463714",          # Bordo oro scuro
            "hover": "#5bc0de"            # Blu hover
        }
        
        # Font migliorati
        self.FONTS = {
            "title": ("Segoe UI", 18, "bold"),
            "header": ("Segoe UI", 12, "bold"),
            "normal": ("Segoe UI", 10),
            "button": ("Segoe UI", 10, "bold"),
            "small": ("Segoe UI", 8)
        }
        
        # Inizializza variabili
        self.current_account_id = None
        self.message_history = []
        self.root = None
        self.notification_label = None
        self.history_listbox = None
        self.status_var = None
        self.message_entry = None
        
        self.setup_gui()
        self.load_account_data()

    def read_lockfile(self):
        """Legge il lockfile di League of Legends"""
        lockfile_path = os.path.join("C:\\Riot Games\\League of Legends", "lockfile")
        try:
            with open(lockfile_path, "r") as lockfile:
                content = lockfile.read().split(":")
                return {
                    "name": content[0],
                    "PID": content[1],
                    "port": content[2],
                    "password": base64.b64encode(f"riot:{content[3]}".encode()).decode(),
                    "protocol": content[4]
                }
        except FileNotFoundError:
            return None
        except Exception as e:
            print(f"Errore nella lettura del lockfile: {e}")
            return None

    def get_current_account_id(self):
        """Ottiene l'ID dell'account attualmente loggato"""
        lockfile_data = self.read_lockfile()
        if not lockfile_data:
            return None
        
        url = f"https://127.0.0.1:{lockfile_data['port']}/lol-summoner/v1/current-summoner"
        headers = {
            "Authorization": f"Basic {lockfile_data['password']}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=5)
            if response.status_code == 200:
                summoner_data = response.json()
                return summoner_data.get("puuid")
        except requests.RequestException as e:
            print(f"Errore nella richiesta API: {e}")
            return None

    def get_history_file(self, account_id):
        """Ottiene il percorso del file cronologia per l'account specificato"""
        if not os.path.exists(self.HISTORY_DIR):
            os.makedirs(self.HISTORY_DIR)
        return os.path.join(self.HISTORY_DIR, f"history_{account_id}.json")

    def load_history(self, account_id):
        """Carica la cronologia dell'account corrente e converte al nuovo formato"""
        history_file = self.get_history_file(account_id)
        try:
            with open(history_file, "r", encoding='utf-8') as file:
                history = json.load(file)
                
                # Converte il vecchio formato al nuovo se necessario
                converted_history = []
                for entry in history:
                    if isinstance(entry, str):
                        # Converte dal vecchio formato stringa
                        try:
                            if "] " in entry:
                                status_part, message = entry.split("] ", 1)
                                status = status_part.strip("[]").lower()
                            else:
                                status = "chat"
                                message = entry
                            
                            converted_entry = {
                                "timestamp": "Data sconosciuta",
                                "status": status,
                                "message": message
                            }
                            converted_history.append(converted_entry)
                        except:
                            # Se non riesce a convertire, mantiene il formato originale
                            converted_history.append({
                                "timestamp": "Data sconosciuta",
                                "status": "chat",
                                "message": str(entry)
                            })
                    else:
                        # È già nel nuovo formato
                        converted_history.append(entry)
                
                return converted_history
                
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_history(self):
        """Salva la cronologia dell'account corrente"""
        if not self.current_account_id:
            return
        
        history_file = self.get_history_file(self.current_account_id)
        try:
            with open(history_file, "w", encoding='utf-8') as file:
                json.dump(self.message_history, file, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Errore nel salvataggio della cronologia: {e}")

    def add_to_history(self, status, message):
        """Aggiunge un messaggio alla cronologia con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "status": status,
            "message": message
        }
        
        # Evita duplicati basandosi su status e message (compatibile con entrambi i formati)
        duplicate_found = False
        for h in self.message_history:
            if isinstance(h, dict):
                if h.get("status") == status and h.get("message") == message:
                    duplicate_found = True
                    break
            elif isinstance(h, str):
                # Compatibilità con il vecchio formato
                if f"[{status}] {message}" == h:
                    duplicate_found = True
                    break
        
        if not duplicate_found:
            self.message_history.insert(0, entry)  # Inserisce in cima
            
            # Mantieni solo gli ultimi 50 elementi
            if len(self.message_history) > 50:
                self.message_history = self.message_history[:50]
            
            self.save_history()
            self.update_history_listbox()

    def update_history_listbox(self):
        """Aggiorna il Listbox della cronologia"""
        self.history_listbox.delete(0, END)
        for entry in self.message_history:
            if isinstance(entry, dict):
                # Nuovo formato con timestamp
                timestamp = entry.get('timestamp', 'Data sconosciuta')
                status = entry.get('status', 'chat').upper()
                message = entry.get('message', '')
                
                # Formato più compatto per la visualizzazione
                if timestamp != 'Data sconosciuta':
                    # Mostra solo ora se è di oggi
                    try:
                        entry_date = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                        if entry_date.date() == datetime.now().date():
                            time_str = entry_date.strftime("%H:%M")
                        else:
                            time_str = entry_date.strftime("%d/%m %H:%M")
                    except:
                        time_str = timestamp
                    
                    display_text = f"[{status}] {message} ({time_str})"
                else:
                    display_text = f"[{status}] {message}"
                    
                self.history_listbox.insert(END, display_text)
            else:
                # Compatibilità con il vecchio formato (non dovrebbe più succedere dopo il caricamento)
                self.history_listbox.insert(END, str(entry))

    def set_from_history(self):
        """Imposta lo stato selezionato dalla cronologia"""
        selection = self.history_listbox.curselection()
        if not selection:
            self.show_notification("Seleziona un elemento dalla cronologia.", "error")
            return
        
        entry = self.message_history[selection[0]]
        
        if isinstance(entry, dict):
            status = entry['status']
            message = entry['message']
        else:
            # Compatibilità con il vecchio formato
            try:
                if "] " in entry:
                    status, message = entry.split("] ", 1)
                    status = status.strip("[]").lower()
                else:
                    status, message = "chat", entry
            except:
                self.show_notification("Errore nel formato della cronologia.", "error")
                return
        
        # Aggiorna i valori nella GUI
        self.status_var.set(status)
        self.message_entry.delete(0, END)
        self.message_entry.insert(0, message)
        
        self.show_notification(f"Stato caricato: {status.upper()}", "success")

    def show_notification(self, message, msg_type="success"):
        """Mostra notifiche temporanee con colori appropriati"""
        if msg_type == "success":
            color = self.COLORS["success_text"]
            bg_color = self.COLORS["success"]
        else:
            color = self.COLORS["error_text"]
            bg_color = self.COLORS["error"]
        
        self.notification_label.config(
            text=message, 
            fg=color,
            bg=bg_color
        )
        
        # Nasconde la notifica dopo 4 secondi
        self.root.after(4000, lambda: self.notification_label.config(
            text="", 
            bg=self.COLORS["bg_primary"]
        ))

    def update_availability_async(self, status):
        """Aggiorna lo stato in un thread separato"""
        def update():
            lockfile_data = self.read_lockfile()
            if not lockfile_data:
                self.root.after(0, lambda: self.show_notification("Client LoL non trovato o non avviato.", "error"))
                return

            url = f"https://127.0.0.1:{lockfile_data['port']}/lol-chat/v1/me"
            headers = {
                "Authorization": f"Basic {lockfile_data['password']}",
                "Content-Type": "application/json"
            }
            payload = {"availability": status}

            try:
                response = requests.put(url, headers=headers, json=payload, verify=False, timeout=5)
                if response.status_code in (200, 201):
                    self.root.after(0, lambda: self.show_notification(f"Disponibilità aggiornata: {status.upper()}", "success"))
                else:
                    self.root.after(0, lambda: self.show_notification(f"Errore API: {response.status_code}", "error"))
            except requests.RequestException as e:
                self.root.after(0, lambda: self.show_notification(f"Errore di rete: {str(e)}", "error"))

        threading.Thread(target=update, daemon=True).start()

    def update_status_message_async(self, message):
        """Aggiorna il messaggio di stato in un thread separato"""
        def update():
            if not message.strip():
                self.root.after(0, lambda: self.show_notification("Inserisci un messaggio valido.", "error"))
                return

            lockfile_data = self.read_lockfile()
            if not lockfile_data:
                self.root.after(0, lambda: self.show_notification("Client LoL non trovato o non avviato.", "error"))
                return

            url = f"https://127.0.0.1:{lockfile_data['port']}/lol-chat/v1/me"
            headers = {
                "Authorization": f"Basic {lockfile_data['password']}",
                "Content-Type": "application/json"
            }
            payload = {"statusMessage": message}

            try:
                response = requests.put(url, headers=headers, json=payload, verify=False, timeout=5)
                if response.status_code in (200, 201):
                    self.root.after(0, lambda: self.show_notification("Messaggio aggiornato con successo!", "success"))
                    self.root.after(0, lambda: self.add_to_history(self.status_var.get(), message))
                else:
                    self.root.after(0, lambda: self.show_notification(f"Errore API: {response.status_code}", "error"))
            except requests.RequestException as e:
                self.root.after(0, lambda: self.show_notification(f"Errore di rete: {str(e)}", "error"))

        threading.Thread(target=update, daemon=True).start()

    def set_status(self):
        """Aggiorna sia lo stato che il messaggio"""
        status = self.status_var.get()
        message = self.message_entry.get()
        
        if not message.strip():
            self.show_notification("Inserisci un messaggio valido.", "error")
            return
        
        # Aggiorna in parallelo
        self.update_availability_async(status)
        self.update_status_message_async(message)

    def load_account_data(self):
        """Carica i dati dell'account corrente"""
        try:
            self.current_account_id = self.get_current_account_id()
            if self.current_account_id:
                self.message_history = self.load_history(self.current_account_id)
                self.update_history_listbox()
                self.show_notification("Account caricato correttamente.", "success")
            else:
                # Usa un ID temporaneo se non si riesce a ottenere l'account
                self.current_account_id = "temp_account"
                self.message_history = []
                self.show_notification("Client LoL non avviato. Modalità offline attiva.", "error")
        except Exception as e:
            self.current_account_id = "temp_account"
            self.message_history = []
            self.show_notification(f"Errore: {str(e)}", "error")

    def create_styled_button(self, parent, text, command, **kwargs):
        """Crea un pulsante con stile personalizzato"""
        btn = Button(
            parent,
            text=text,
            command=command,
            bg=self.COLORS["accent"],
            fg=self.COLORS["bg_primary"],
            activebackground=self.COLORS["accent_hover"],
            activeforeground=self.COLORS["bg_primary"],
            font=self.FONTS["button"],
            relief=FLAT,
            bd=0,
            cursor="hand2",
            **kwargs
        )
        
        # Effetto hover
        def on_enter(e):
            btn.config(bg=self.COLORS["accent_hover"])
        
        def on_leave(e):
            btn.config(bg=self.COLORS["accent"])
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn

    def setup_gui(self):
        """Configura l'interfaccia grafica"""
        self.root = Tk()
        self.root.title("LoL Status Manager v2.0")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        self.root.configure(bg=self.COLORS["bg_primary"])
        
        # Icona (se esiste)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # Frame principale con padding
        main_frame = Frame(self.root, bg=self.COLORS["bg_primary"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header con titolo e sottotitolo
        header_frame = Frame(main_frame, bg=self.COLORS["bg_primary"])
        header_frame.pack(fill="x", pady=(0, 25))
        
        title_label = Label(
            header_frame,
            text="🎮 LOL STATUS MANAGER",
            font=self.FONTS["title"],
            bg=self.COLORS["bg_primary"],
            fg=self.COLORS["accent"]
        )
        title_label.pack()
        
        subtitle_label = Label(
            header_frame,
            text="Gestisci il tuo stato di League of Legends",
            font=self.FONTS["small"],
            bg=self.COLORS["bg_primary"],
            fg=self.COLORS["text_secondary"]
        )
        subtitle_label.pack(pady=(5, 0))

        # Sezione Controlli
        controls_frame = Frame(main_frame, bg=self.COLORS["bg_secondary"], relief="raised", bd=1)
        controls_frame.pack(fill="x", pady=(0, 20))
        
        controls_title = Label(
            controls_frame,
            text="⚙️ Controlli",
            font=self.FONTS["header"],
            bg=self.COLORS["bg_secondary"],
            fg=self.COLORS["text_primary"]
        )
        controls_title.pack(pady=(15, 10))

        # Frame per stato
        status_frame = Frame(controls_frame, bg=self.COLORS["bg_secondary"])
        status_frame.pack(fill="x", padx=20, pady=(0, 15))

        status_label = Label(
            status_frame,
            text="Stato:",
            bg=self.COLORS["bg_secondary"],
            fg=self.COLORS["text_primary"],
            font=self.FONTS["normal"]
        )
        status_label.pack(side="left", padx=(0, 10))

        self.status_var = StringVar(value="chat")
        status_menu = OptionMenu(
            status_frame, 
            self.status_var, 
            "chat", "away", "offline", "mobile", "dnd"
        )
        status_menu.config(
            font=self.FONTS["normal"],
            bg=self.COLORS["bg_tertiary"],
            fg=self.COLORS["text_primary"],
            activebackground=self.COLORS["accent"],
            activeforeground=self.COLORS["bg_primary"],
            highlightthickness=0,
            bd=1,
            width=12
        )
        status_menu["menu"].config(
            bg=self.COLORS["bg_tertiary"],
            fg=self.COLORS["text_primary"],
            activebackground=self.COLORS["accent"]
        )
        status_menu.pack(side="left")

        # Frame per messaggio
        message_frame = Frame(controls_frame, bg=self.COLORS["bg_secondary"])
        message_frame.pack(fill="x", padx=20, pady=(0, 20))

        message_label = Label(
            message_frame,
            text="Messaggio di stato:",
            bg=self.COLORS["bg_secondary"],
            fg=self.COLORS["text_primary"],
            font=self.FONTS["normal"]
        )
        message_label.pack(anchor="w", pady=(0, 8))

        self.message_entry = Entry(
            message_frame,
            bg=self.COLORS["bg_tertiary"],
            fg=self.COLORS["text_primary"],
            font=self.FONTS["normal"],
            insertbackground=self.COLORS["accent"],
            relief=FLAT,
            bd=2,
            highlightthickness=1,
            highlightcolor=self.COLORS["accent"]
        )
        self.message_entry.pack(fill="x", ipady=8)
        
        # Bind Enter per inviare
        self.message_entry.bind("<Return>", lambda e: self.set_status())

        # Sezione Cronologia
        history_frame = Frame(main_frame, bg=self.COLORS["bg_secondary"], relief="raised", bd=1)
        history_frame.pack(fill="both", expand=True, pady=(0, 20))

        history_title = Label(
            history_frame,
            text="📜 Cronologia Messaggi",
            font=self.FONTS["header"],
            bg=self.COLORS["bg_secondary"],
            fg=self.COLORS["text_primary"]
        )
        history_title.pack(pady=(15, 10))

        history_container = Frame(history_frame, bg=self.COLORS["bg_tertiary"])
        history_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        scrollbar = Scrollbar(history_container, orient=VERTICAL)
        scrollbar.pack(side=RIGHT, fill=Y)

        self.history_listbox = Listbox(
            history_container,
            yscrollcommand=scrollbar.set,
            bg=self.COLORS["bg_tertiary"],
            fg=self.COLORS["text_primary"],
            font=self.FONTS["normal"],
            selectbackground=self.COLORS["accent"],
            selectforeground=self.COLORS["bg_primary"],
            bd=0,
            highlightthickness=0,
            activestyle="none"
        )
        self.history_listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.history_listbox.yview)

        # Bind doppio click per selezionare dalla cronologia
        self.history_listbox.bind("<Double-Button-1>", lambda e: self.set_from_history())

        # Frame pulsanti
        button_frame = Frame(main_frame, bg=self.COLORS["bg_primary"])
        button_frame.pack(fill="x", pady=(0, 10))

        # Pulsanti principali
        btn_history = self.create_styled_button(
            button_frame, 
            "📖 Carica dalla Cronologia", 
            self.set_from_history,
            padx=15, pady=8
        )
        btn_history.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_availability = self.create_styled_button(
            button_frame, 
            "🟢 Aggiorna Disponibilità", 
            lambda: self.update_availability_async(self.status_var.get()),
            padx=15, pady=8
        )
        btn_availability.pack(side="left", fill="x", expand=True, padx=5)

        btn_message = self.create_styled_button(
            button_frame, 
            "💬 Aggiorna Messaggio", 
            lambda: self.update_status_message_async(self.message_entry.get()),
            padx=15, pady=8
        )
        btn_message.pack(side="left", fill="x", expand=True, padx=5)

        btn_both = self.create_styled_button(
            button_frame, 
            "⚡ Aggiorna Tutto", 
            self.set_status,
            padx=15, pady=8
        )
        btn_both.pack(side="left", fill="x", expand=True, padx=(5, 0))

        # Area notifiche
        self.notification_label = Label(
            main_frame,
            text="",
            bg=self.COLORS["bg_primary"],
            fg=self.COLORS["success_text"],
            font=self.FONTS["normal"],
            height=2
        )
        self.notification_label.pack(fill="x", pady=(10, 0))

    def run(self):
        """Avvia l'applicazione"""
        # Messaggio di benvenuto
        self.show_notification("Applicazione avviata. Pronta per l'uso!", "success")
        
        # Centra la finestra
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Avvia il loop principale
        self.root.mainloop()

# Avvio dell'applicazione
if __name__ == "__main__":
    app = LoLStatusManager()
    app.run()