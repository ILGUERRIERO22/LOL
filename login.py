import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Toplevel
import json
import os
import subprocess
import time
import pyautogui
import psutil
import pygetwindow as gw
from pywinauto.application import Application
import threading
from PIL import Image, ImageTk
import sys
from datetime import datetime

# Prevent pyautogui from triggering the failsafe
pyautogui.FAILSAFE = False

# File paths and global variables
credentials_file = r"C:\Users\dbait\Desktop\MOD LOL\credentials.json"
verification_image_path = r"C:\Users\dbait\Desktop\MOD LOL\script\Client.png"
riot_client_path = r"C:\Riot Games\Riot Client\RiotClientServices.exe"
icon_path = r"C:\Users\dbait\Desktop\MOD LOL\script\lol_icon.png"

# Modern color palette - più raffinata e coerente
COLORS = {
    "bg_primary": "#0F1419",      # Sfondo principale ultra-scuro
    "bg_secondary": "#1E2328",    # Sfondo secondario
    "bg_tertiary": "#2D3035",     # Sfondo elementi
    "surface": "#3C3C42",         # Superfici elevate
    "accent_primary": "#C89B3C",  # Oro LoL ufficiale
    "accent_secondary": "#0596AA", # Blu-teal per contrasto
    "accent_hover": "#F0E6D2",    # Oro chiaro per hover
    "text_primary": "#F0E6D2",    # Testo principale (crema)
    "text_secondary": "#A09B8C",  # Testo secondario
    "text_muted": "#5B5A56",      # Testo disabilitato
    "success": "#0F9B45",         # Verde successo
    "warning": "#E89611",         # Giallo warning
    "danger": "#C8372C",          # Rosso errore
    "info": "#005A82",            # Blu informazioni
    "border": "#463714",          # Bordi sottili
    "shadow": "#000000",          # Ombra
}

def run_in_thread(target_function, *args):
    """Esegue una funzione in un thread separato"""
    thread = threading.Thread(target=target_function, args=args)
    thread.daemon = True
    thread.start()

def resource_path(relative_path):
    """Ottiene il percorso assoluto delle risorse"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AnimatedButton(tk.Button):
    """Bottone con animazioni fluide e effetti moderni"""
    def __init__(self, master, **kw):
        # Colori base
        self.bg_normal = kw.pop('bg', COLORS["surface"])
        self.bg_hover = kw.pop('bg_hover', COLORS["accent_primary"])
        self.fg_normal = kw.pop('fg', COLORS["text_primary"])
        self.fg_hover = kw.pop('fg_hover', COLORS["bg_primary"])
        
        # Configurazione del bottone
        super().__init__(
            master,
            bg=self.bg_normal,
            fg=self.fg_normal,
            relief="flat",
            bd=0,
            highlightthickness=0,
            activebackground=self.bg_hover,
            activeforeground=self.fg_hover,
            font=('Segoe UI', 10, 'bold'),
            cursor="hand2",
            padx=20,
            pady=12,
            **kw
        )
        
        # Bind degli eventi
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)
        self.bind("<ButtonRelease-1>", self._on_release)
        
    def _on_enter(self, e):
        self.config(bg=self.bg_hover, fg=self.fg_hover)
        
    def _on_leave(self, e):
        self.config(bg=self.bg_normal, fg=self.fg_normal)
        
    def _on_click(self, e):
        self.config(relief="sunken")
        
    def _on_release(self, e):
        self.config(relief="flat")

class ModernEntry(tk.Entry):
    """Campo di input moderno con placeholder e validazione"""
    def __init__(self, master, placeholder="", **kw):
        self.placeholder = placeholder
        self.placeholder_color = COLORS["text_muted"]
        self.normal_color = COLORS["text_primary"]
        self.is_placeholder_active = True
        
        super().__init__(
            master,
            bg=COLORS["bg_tertiary"],
            fg=self.placeholder_color,
            insertbackground=COLORS["accent_primary"],
            relief="flat",
            bd=2,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent_primary"],
            font=('Segoe UI', 11),
            **kw
        )
        
        if self.placeholder:
            self.insert(0, self.placeholder)
            
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        
    def _on_focus_in(self, e):
        if self.is_placeholder_active:
            self.delete(0, tk.END)
            self.config(fg=self.normal_color)
            self.is_placeholder_active = False
            
    def _on_focus_out(self, e):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(fg=self.placeholder_color)
            self.is_placeholder_active = True
            
    def get_value(self):
        """Ritorna il valore reale (senza placeholder)"""
        return "" if self.is_placeholder_active else self.get()

class ModernFrame(tk.Frame):
    """Frame moderno con bordi arrotondati simulati"""
    def __init__(self, master, **kw):
        bg_color = kw.pop('bg_color', COLORS["bg_secondary"])
        border_color = kw.pop('border_color', COLORS["border"])
        
        super().__init__(master, bg=bg_color, relief="flat", bd=1, **kw)
        
        # Simulazione bordi arrotondati con padding interno
        self.config(highlightbackground=border_color, highlightthickness=1)

class StatusIndicator(tk.Canvas):
    """Indicatore di stato animato"""
    def __init__(self, master, size=12):
        super().__init__(master, width=size, height=size, 
                        bg=COLORS["bg_secondary"], highlightthickness=0)
        self.size = size
        self.set_status("ready")
        
    def set_status(self, status):
        """Imposta lo stato: ready, working, error, success"""
        self.delete("all")
        
        colors = {
            "ready": COLORS["info"],
            "working": COLORS["warning"],
            "error": COLORS["danger"],
            "success": COLORS["success"]
        }
        
        color = colors.get(status, COLORS["info"])
        self.create_oval(2, 2, self.size-2, self.size-2, 
                        fill=color, outline="", width=0)

class TooltipManager:
    """Gestore tooltip migliorato con styling moderno"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip, "+")
        self.widget.bind("<Leave>", self.hide_tooltip, "+")
        
    def show_tooltip(self, event=None):
        if self.tooltip:
            return
            
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        self.tooltip.configure(bg=COLORS["shadow"])
        
        # Frame interno per l'ombra
        inner_frame = tk.Frame(
            self.tooltip,
            bg=COLORS["bg_primary"],
            relief="solid",
            bd=1
        )
        inner_frame.pack(padx=1, pady=1)
        
        label = tk.Label(
            inner_frame,
            text=self.text,
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            font=("Segoe UI", 9),
            padx=8,
            pady=4
        )
        label.pack()
        
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class RiotAccountManager:
    def __init__(self, root):
        self.root = root
        self.root.title("League of Legends Account Manager")
        self.root.configure(bg=COLORS["bg_primary"])
        
        # Impostazioni finestra
        self.setup_window()
        self.setup_styles()
        
        # Interfaccia principale
        self.create_main_interface()
        
        # Inizializzazione
        self.update_account_list()
        
        # Variabili di stato
        self.current_operation = None
        
    def setup_window(self):
        """Configurazione della finestra principale"""
        window_width = 900
        window_height = 700
        
        # Centratura
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(800, 600)
        
        # Icona
        try:
            icon = Image.open(icon_path)
            icon = icon.resize((32, 32), Image.LANCZOS)
            icon_photo = ImageTk.PhotoImage(icon)
            self.root.iconphoto(True, icon_photo)
        except Exception:
            pass
            
    def setup_styles(self):
        """Configurazione degli stili ttk"""
        style = ttk.Style()
        
        # Tema base
        style.theme_use('clam')
        
        # Frame principale
        style.configure("Main.TFrame", 
                       background=COLORS["bg_primary"],
                       relief="flat")
        
        # Notebook (tabs)
        style.configure("Modern.TNotebook",
                       background=COLORS["bg_primary"],
                       tabmargins=[2, 5, 2, 0])
        
        style.configure("Modern.TNotebook.Tab",
                       background=COLORS["bg_secondary"],
                       foreground=COLORS["text_secondary"],
                       padding=[20, 10],
                       font=('Segoe UI', 11, 'bold'),
                       focuscolor=COLORS["accent_primary"])
        
        style.map("Modern.TNotebook.Tab",
                 background=[("selected", COLORS["accent_primary"]),
                           ("active", COLORS["surface"])],
                 foreground=[("selected", COLORS["bg_primary"]),
                           ("active", COLORS["text_primary"])])
        
        # Entry fields
        style.configure("Modern.TEntry",
                       fieldbackground=COLORS["bg_tertiary"],
                       foreground=COLORS["text_primary"],
                       bordercolor=COLORS["border"],
                       focuscolor=COLORS["accent_primary"],
                       insertcolor=COLORS["accent_primary"],
                       font=('Segoe UI', 11))
        
        # Labels
        style.configure("Title.TLabel",
                       background=COLORS["bg_primary"],
                       foreground=COLORS["accent_primary"],
                       font=('Segoe UI', 18, 'bold'))
        
        style.configure("Header.TLabel",
                       background=COLORS["bg_primary"],
                       foreground=COLORS["text_primary"],
                       font=('Segoe UI', 12, 'bold'))
        
        style.configure("Body.TLabel",
                       background=COLORS["bg_primary"],
                       foreground=COLORS["text_primary"],
                       font=('Segoe UI', 10))
        
        style.configure("Muted.TLabel",
                       background=COLORS["bg_primary"],
                       foreground=COLORS["text_muted"],
                       font=('Segoe UI', 9))
        
        # Separator
        style.configure("Modern.TSeparator",
                       background=COLORS["border"])
        
        # Progressbar
        style.configure("Modern.Horizontal.TProgressbar",
                       background=COLORS["accent_primary"],
                       troughcolor=COLORS["bg_tertiary"],
                       borderwidth=0,
                       lightcolor=COLORS["accent_primary"],
                       darkcolor=COLORS["accent_primary"])
        
    def create_main_interface(self):
        """Crea l'interfaccia principale"""
        # Container principale con padding
        main_container = tk.Frame(self.root, bg=COLORS["bg_primary"])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self.create_header(main_container)
        
        # Separator
        sep = ttk.Separator(main_container, style="Modern.TSeparator")
        sep.pack(fill="x", pady=(0, 20))
        
        # Notebook per le tabs
        self.create_notebook(main_container)
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self, parent):
        """Crea l'header dell'applicazione"""
        header_frame = tk.Frame(parent, bg=COLORS["bg_primary"])
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Logo e titolo
        title_container = tk.Frame(header_frame, bg=COLORS["bg_primary"])
        title_container.pack(side="left", fill="x", expand=True)
        
        # Titolo principale
        title = ttk.Label(title_container, 
                         text="League of Legends",
                         style="Title.TLabel")
        title.pack(anchor="w")
        
        # Sottotitolo
        subtitle = ttk.Label(title_container,
                           text="Account Manager Pro",
                           style="Header.TLabel")
        subtitle.pack(anchor="w")
        
        # Info versione
        version_info = tk.Frame(header_frame, bg=COLORS["bg_primary"])
        version_info.pack(side="right")
        
        version_label = ttk.Label(version_info,
                                text="v2.5 Enhanced",
                                style="Muted.TLabel")
        version_label.pack()
        
        # Data/ora
        now = datetime.now().strftime("%d/%m/%Y")
        date_label = ttk.Label(version_info,
                              text=now,
                              style="Muted.TLabel")
        date_label.pack()
        
    def create_notebook(self, parent):
        """Crea il notebook con le tabs"""
        # Container per il notebook
        notebook_container = ModernFrame(parent, bg_color=COLORS["bg_secondary"])
        notebook_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Notebook
        self.notebook = ttk.Notebook(notebook_container, style="Modern.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabs
        self.create_accounts_tab()
        self.create_add_account_tab()
        self.create_settings_tab()
        
    def create_accounts_tab(self):
        """Tab per la gestione degli account con menu contestuale"""
        # Frame principale
        accounts_frame = tk.Frame(self.notebook, bg=COLORS["bg_secondary"])
        self.notebook.add(accounts_frame, text="👤 Account")
        
        # Container con padding
        container = tk.Frame(accounts_frame, bg=COLORS["bg_secondary"])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sezione ricerca
        search_frame = self.create_search_section(container)
        search_frame.pack(fill="x", pady=(0, 15))
        
        # Lista account CON MENU CONTESTUALE
        list_frame = self.create_account_list_with_context_menu(container)
        list_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Informazioni di uso (sostituisce i pulsanti)
        info_frame = self.create_usage_info_section(container)
        info_frame.pack(fill="x")

    def create_usage_info_section(self, parent):
        """Sezione informazioni d'uso (sostituisce i pulsanti)"""
        info_frame = ModernFrame(parent, bg_color=COLORS["bg_tertiary"])
        info_frame.configure(padx=15, pady=15)
        
        # Header
        header = ttk.Label(info_frame, text="ℹ️ Come Usare", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 10))
        
        # Istruzioni dettagliate
        instructions_text = """🖱️ Doppio clic: Login rapido (client principale)
    🖱️ Tasto destro: Menu con tutte le opzioni
    ⌨️ Cerca: Digita per filtrare gli account"""
        
        instructions_label = ttk.Label(info_frame,
                                    text=instructions_text,
                                    style="Body.TLabel",
                                    justify="left")
        instructions_label.pack(anchor="w")
        
        return info_frame
        
    def create_search_section(self, parent):
        """Sezione ricerca account"""
        search_frame = ModernFrame(parent, bg_color=COLORS["bg_tertiary"])
        search_frame.configure(padx=15, pady=15)
        
        # Header
        header = ttk.Label(search_frame, text="Ricerca Account", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 10))
        
        # Input container
        input_container = tk.Frame(search_frame, bg=COLORS["bg_tertiary"])
        input_container.pack(fill="x")
        
        # Campo ricerca
        self.search_var = tk.StringVar()
        self.search_entry = ModernEntry(input_container, 
                                       placeholder="Cerca per nome utente...",
                                       textvariable=self.search_var,
                                       width=40)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Bottone ricerca
        search_btn = AnimatedButton(input_container, 
                                  text="Cerca",
                                  bg=COLORS["accent_secondary"],
                                  bg_hover=COLORS["accent_primary"],
                                  command=self.search_accounts)
        search_btn.pack(side="right")
        
        # Bind per ricerca in tempo reale
        self.search_var.trace('w', lambda *args: self.search_accounts())
        
        return search_frame
        
    def create_account_list_with_context_menu(self, parent):
        """Sezione lista account con menu contestuale"""
        list_frame = ModernFrame(parent, bg_color=COLORS["bg_tertiary"])
        list_frame.configure(padx=15, pady=15)
        
        # Header
        header = ttk.Label(list_frame, text="I Tuoi Account", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 10))
        
        # Istruzioni per l'uso
        instructions = ttk.Label(list_frame, 
                            text="💡 Tasto destro per azioni • Doppio clic per login rapido",
                            style="Muted.TLabel")
        instructions.pack(anchor="w", pady=(0, 10))
        
        # Lista con scrollbar
        list_container = tk.Frame(list_frame, bg=COLORS["bg_tertiary"])
        list_container.pack(fill="both", expand=True)
        
        # Listbox personalizzata
        self.account_listbox = tk.Listbox(
            list_container,
            bg=COLORS["surface"],
            fg=COLORS["text_primary"],
            selectbackground=COLORS["accent_primary"],
            selectforeground=COLORS["bg_primary"],
            font=('Segoe UI', 11),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=COLORS["accent_primary"],
            highlightbackground=COLORS["border"],
            activestyle="none"
        )
        self.account_listbox.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        
        # Collegamenti
        self.account_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.account_listbox.yview)
        
        # EVENTI
        # Double-click per login rapido (client principale)
        self.account_listbox.bind("<Double-1>", self.on_double_click_login)
        
        # Tasto destro per menu contestuale
        self.account_listbox.bind("<Button-3>", self.show_context_menu)
        
        # Click sinistro per selezione (necessario per il menu contestuale)
        self.account_listbox.bind("<Button-1>", self.on_left_click_select)
        
        # Inizializza variabile per tracciare l'elemento selezionato dal menu
        self.context_menu_selected_account = None
        
        return list_frame
    
    def on_left_click_select(self, event):
        """Gestisce il click sinistro per selezione"""
        # Ottieni l'indice dell'elemento cliccato
        index = self.account_listbox.nearest(event.y)
        if index >= 0:
            self.account_listbox.selection_clear(0, tk.END)
            self.account_listbox.selection_set(index)
            self.account_listbox.activate(index)

    def on_double_click_login(self, event):
        """Gestisce il doppio click per login rapido"""
        selected_account = self.get_selected_account()
        if selected_account:
            self.update_status(f"Login rapido per {selected_account}...", "working")
            run_in_thread(self.login_to_client)
        else:
            self.update_status("Nessun account selezionato", "warning")

    def show_context_menu(self, event):
        """Mostra il menu contestuale al click destro"""
        # Seleziona l'elemento sotto il mouse
        index = self.account_listbox.nearest(event.y)
        if index < 0:
            return  # Nessun elemento sotto il mouse
            
        # Seleziona l'elemento
        self.account_listbox.selection_clear(0, tk.END)
        self.account_listbox.selection_set(index)
        self.account_listbox.activate(index)
        
        # Ottieni il nome dell'account
        selected_account = self.get_selected_account()
        if not selected_account:
            return
            
        # Salva l'account selezionato per le azioni del menu
        self.context_menu_selected_account = selected_account
        
        # Crea il menu contestuale
        context_menu = tk.Menu(self.root, tearoff=0)
        
        # Configura stile del menu
        context_menu.configure(
            bg=COLORS["bg_primary"],
            fg=COLORS["text_primary"],
            activebackground=COLORS["accent_primary"],
            activeforeground=COLORS["bg_primary"],
            relief="flat",
            bd=1,
            font=('Segoe UI', 10)
        )
        
        # Aggiungi header con nome account
        context_menu.add_command(
            label=f"📋 {selected_account}",
            state="disabled",
            font=('Segoe UI', 10, 'bold')
        )
        context_menu.add_separator()
        
        # Opzioni login
        context_menu.add_command(
            label="🎮 Login Principale",
            command=self.context_login_primary,
            accelerator="Doppio-click"
        )
        context_menu.add_command(
            label="🎯 Login Secondario",
            command=self.context_login_secondary
        )
        
        context_menu.add_separator()
        
        # Opzioni gestione
        context_menu.add_command(
            label="✏️ Modifica Account",
            command=self.context_edit_account
        )
        context_menu.add_command(
            label="🗑️ Elimina Account",
            command=self.context_delete_account
        )
        
        context_menu.add_separator()
        
        # Opzioni aggiuntive
        context_menu.add_command(
            label="📋 Copia Username",
            command=self.context_copy_username
        )
        
        # Mostra il menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def context_login_primary(self):
        """Login con client principale dal menu contestuale"""
        if self.context_menu_selected_account:
            self.update_status(f"Login principale per {self.context_menu_selected_account}...", "working")
            run_in_thread(self.login_to_client_with_account, self.context_menu_selected_account)

    def context_login_secondary(self):
        """Login con client secondario dal menu contestuale"""
        if self.context_menu_selected_account:
            self.update_status(f"Login secondario per {self.context_menu_selected_account}...", "working")
            run_in_thread(self.login_to_client_secondary_with_account, self.context_menu_selected_account)

    def context_edit_account(self):
        """Modifica account dal menu contestuale"""
        if self.context_menu_selected_account:
            self.edit_credentials_with_account(self.context_menu_selected_account)

    def context_delete_account(self):
        """Elimina account dal menu contestuale"""
        if self.context_menu_selected_account:
            self.delete_credentials_with_account(self.context_menu_selected_account)

    def context_copy_username(self):
        """Copia username negli appunti"""
        if self.context_menu_selected_account:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.context_menu_selected_account)
            self.root.update()  # Mantiene negli appunti anche dopo la chiusura
            self.update_status(f"Username '{self.context_menu_selected_account}' copiato negli appunti", "success")

    def login_to_client_with_account(self, username):
        """Login al client principale con account specifico"""
        self._perform_login(username, is_secondary=False)

    def login_to_client_secondary_with_account(self, username):
        """Login al client secondario con account specifico"""
        self._perform_login(username, is_secondary=True)

    def edit_credentials_with_account(self, username):
        """Modifica account specifico"""
        # Carica credenziali
        if not os.path.exists(credentials_file):
            self.update_status("File credenziali non trovato", "error")
            return
            
        with open(credentials_file, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
            
        if username not in credentials:
            self.update_status("Account non trovato", "error")
            return
            
        # Mostra dialog di modifica
        self.show_edit_dialog(username, credentials[username])

    def delete_credentials_with_account(self, username):
        """Elimina account specifico"""
        # Conferma eliminazione
        confirm = messagebox.askyesno(
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare l'account '{username}'?\n\n"
            "Questa azione non può essere annullata.",
            icon="warning"
        )
        
        if not confirm:
            self.update_status("Eliminazione annullata")
            return
            
        try:
            # Carica e aggiorna credenziali
            with open(credentials_file, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
                
            if username in credentials:
                del credentials[username]
                
                with open(credentials_file, 'w', encoding='utf-8') as f:
                    json.dump(credentials, f, indent=2)
                    
                self.update_status(f"Account '{username}' eliminato", "success")
                self.update_account_list()
            else:
                self.update_status("Account non trovato", "error")
                
        except Exception as e:
            self.update_status(f"Errore nell'eliminazione: {e}", "error")
            messagebox.showerror("Errore", f"Impossibile eliminare l'account:\n{e}")


    def create_account_actions_section(self, parent):
        """Sezione azioni account"""
        actions_frame = ModernFrame(parent, bg_color=COLORS["bg_tertiary"])
        actions_frame.configure(padx=15, pady=15)
        
        # Header
        header = ttk.Label(actions_frame, text="Azioni Account", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 15))
        
        # Container pulsanti principali
        main_actions = tk.Frame(actions_frame, bg=COLORS["bg_tertiary"])
        main_actions.pack(fill="x", pady=(0, 10))
        
        # Login principale
        login_btn = AnimatedButton(main_actions,
                                 text="🎮 Login Principale",
                                 bg=COLORS["accent_primary"],
                                 bg_hover=COLORS["accent_hover"],
                                 fg=COLORS["bg_primary"],
                                 fg_hover=COLORS["bg_primary"],
                                 command=lambda: run_in_thread(self.login_to_client))
        login_btn.pack(side="left", padx=(0, 10))
        
        # Login secondario
        secondary_btn = AnimatedButton(main_actions,
                                     text="🎯 Login Secondario (LOR)",
                                     bg=COLORS["accent_secondary"],
                                     bg_hover=COLORS["accent_primary"],
                                     command=lambda: run_in_thread(self.login_to_client_secondary))
        secondary_btn.pack(side="left")
        
        # Container pulsanti gestione
        manage_actions = tk.Frame(actions_frame, bg=COLORS["bg_tertiary"])
        manage_actions.pack(fill="x")
        
        # Modifica
        edit_btn = AnimatedButton(manage_actions,
                                text="✏️ Modifica",
                                bg=COLORS["surface"],
                                bg_hover=COLORS["accent_primary"],
                                command=self.edit_credentials)
        edit_btn.pack(side="left", padx=(0, 10))
        
        # Elimina
        delete_btn = AnimatedButton(manage_actions,
                                  text="🗑️ Elimina",
                                  bg=COLORS["danger"],
                                  bg_hover="#FF4444",
                                  command=self.delete_credentials)
        delete_btn.pack(side="left")
        
        return actions_frame
        
    def create_add_account_tab(self):
        """Tab per aggiungere account"""
        add_frame = tk.Frame(self.notebook, bg=COLORS["bg_secondary"])
        self.notebook.add(add_frame, text="➕ Nuovo Account")
        
        # Container con padding
        container = tk.Frame(add_frame, bg=COLORS["bg_secondary"])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Form container
        form_frame = ModernFrame(container, bg_color=COLORS["bg_tertiary"])
        form_frame.pack(fill="x", expand=False, anchor="center", pady=50)
        form_frame.configure(padx=30, pady=30)
        
        # Header
        header = ttk.Label(form_frame, text="Aggiungi Nuovo Account", style="Header.TLabel")
        header.pack(pady=(0, 20))
        
        # Campo username
        username_section = tk.Frame(form_frame, bg=COLORS["bg_tertiary"])
        username_section.pack(fill="x", pady=(0, 15))
        
        username_label = ttk.Label(username_section, text="Nome Utente", style="Body.TLabel")
        username_label.pack(anchor="w", pady=(0, 5))
        
        self.username_entry = ModernEntry(username_section, 
                                         placeholder="Inserisci nome utente Riot...",
                                         width=40)
        self.username_entry.pack(fill="x")
        
        # Campo password
        password_section = tk.Frame(form_frame, bg=COLORS["bg_tertiary"])
        password_section.pack(fill="x", pady=(0, 15))
        
        password_label = ttk.Label(password_section, text="Password", style="Body.TLabel")
        password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ModernEntry(password_section, 
                                         placeholder="Inserisci password...",
                                         show="•",
                                         width=40)
        self.password_entry.pack(fill="x")
        
        # Checkbox mostra password
        show_password_frame = tk.Frame(form_frame, bg=COLORS["bg_tertiary"])
        show_password_frame.pack(fill="x", pady=(0, 20))
        
        self.show_password_var = tk.BooleanVar()
        show_password_check = tk.Checkbutton(
            show_password_frame,
            text="Mostra password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            bg=COLORS["bg_tertiary"],
            fg=COLORS["text_secondary"],
            selectcolor=COLORS["surface"],
            activebackground=COLORS["bg_tertiary"],
            activeforeground=COLORS["text_primary"],
            font=('Segoe UI', 9)
        )
        show_password_check.pack(anchor="w")
        
        # Pulsanti
        buttons_frame = tk.Frame(form_frame, bg=COLORS["bg_tertiary"])
        buttons_frame.pack(fill="x", pady=(10, 0))
        
        # Salva
        save_btn = AnimatedButton(buttons_frame,
                                text="💾 Salva Account",
                                bg=COLORS["success"],
                                bg_hover=COLORS["accent_primary"],
                                command=self.save_credentials)
        save_btn.pack(side="left", padx=(0, 10))
        
        # Cancella
        clear_btn = AnimatedButton(buttons_frame,
                                 text="🗑️ Cancella",
                                 bg=COLORS["surface"],
                                 bg_hover=COLORS["danger"],
                                 command=self.clear_form)
        clear_btn.pack(side="left")
        
    def create_settings_tab(self):
        """Tab impostazioni"""
        settings_frame = tk.Frame(self.notebook, bg=COLORS["bg_secondary"])
        self.notebook.add(settings_frame, text="⚙️ Impostazioni")
        
        # Container con padding
        container = tk.Frame(settings_frame, bg=COLORS["bg_secondary"])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sezione Backup & Restore
        backup_section = self.create_backup_section(container)
        backup_section.pack(fill="x", pady=(0, 15))
        
        # Sezione Client Control
        client_section = self.create_client_control_section(container)
        client_section.pack(fill="x", pady=(0, 15))
        
        # Sezione About
        about_section = self.create_about_section(container)
        about_section.pack(fill="x")
        
    def create_backup_section(self, parent):
        """Sezione backup e restore"""
        section = ModernFrame(parent, bg_color=COLORS["bg_tertiary"])
        section.configure(padx=15, pady=15)
        
        # Header
        header = ttk.Label(section, text="💾 Backup & Restore", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 15))
        
        # Pulsanti
        buttons_frame = tk.Frame(section, bg=COLORS["bg_tertiary"])
        buttons_frame.pack(fill="x")
        
        export_btn = AnimatedButton(buttons_frame,
                                  text="📤 Esporta Account",
                                  bg=COLORS["info"],
                                  bg_hover=COLORS["accent_primary"],
                                  command=self.export_credentials)
        export_btn.pack(side="left", padx=(0, 10))
        
        import_btn = AnimatedButton(buttons_frame,
                                  text="📥 Importa Account",
                                  bg=COLORS["info"],
                                  bg_hover=COLORS["accent_primary"],
                                  command=self.import_credentials)
        import_btn.pack(side="left")
        
        return section
        
    def create_client_control_section(self, parent):
        """Sezione controllo client"""
        section = ModernFrame(parent, bg_color=COLORS["bg_tertiary"])
        section.configure(padx=15, pady=15)
        
        # Header
        header = ttk.Label(section, text="🎮 Controllo Client", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 15))
        
        # Pulsanti
        buttons_frame = tk.Frame(section, bg=COLORS["bg_tertiary"])
        buttons_frame.pack(fill="x")
        
        open_client_btn = AnimatedButton(buttons_frame,
                                       text="🚀 Apri Client",
                                       bg=COLORS["success"],
                                       bg_hover=COLORS["accent_primary"],
                                       command=lambda: run_in_thread(self.open_client))
        open_client_btn.pack(side="left", padx=(0, 10))
        
        close_riot_btn = AnimatedButton(buttons_frame,
                                      text="🔴 Chiudi Riot Client",
                                      bg=COLORS["warning"],
                                      bg_hover=COLORS["danger"],
                                      command=lambda: run_in_thread(self.close_riot_client))
        close_riot_btn.pack(side="left", padx=(0, 10))
        
        close_league_btn = AnimatedButton(buttons_frame,
                                        text="❌ Chiudi League Client",
                                        bg=COLORS["danger"],
                                        bg_hover="#FF4444",
                                        command=lambda: run_in_thread(self.close_league_client))
        close_league_btn.pack(side="left")
        
        return section
        
    def create_about_section(self, parent):
        """Sezione about"""
        section = ModernFrame(parent, bg_color=COLORS["bg_tertiary"])
        section.configure(padx=15, pady=15)
        
        # Header
        header = ttk.Label(section, text="ℹ️ Informazioni", style="Header.TLabel")
        header.pack(anchor="w", pady=(0, 15))
        
        # Testo info
        info_text = (
            "League of Legends Account Manager Pro v2.5\n\n"
            "✨ Funzionalità principali:\n"
            "• Gestione multipla account LoL\n"
            "• Login automatizzato\n"
            "• Backup e ripristino credenziali\n"
            "• Interfaccia moderna e intuitiva\n\n"
            "Sviluppato per semplificare la gestione dei tuoi account Riot Games."
        )
        
        info_label = ttk.Label(section,
                              text=info_text,
                              style="Body.TLabel",
                              justify="left",
                              wraplength=500)
        info_label.pack(anchor="w")
        
        return section
        
    def create_status_bar(self):
        """Barra di stato moderna"""
        status_frame = tk.Frame(self.root, bg=COLORS["bg_secondary"], height=30)
        status_frame.pack(side="bottom", fill="x")
        status_frame.pack_propagate(False)
        
        # Container interno
        container = tk.Frame(status_frame, bg=COLORS["bg_secondary"])
        container.pack(fill="both", expand=True, padx=15, pady=5)
        
        # Indicatore di stato
        self.status_indicator = StatusIndicator(container, size=16)
        self.status_indicator.pack(side="left", padx=(0, 10))
        
        # Testo status
        self.status_label = ttk.Label(container,
                                    text="Pronto",
                                    style="Body.TLabel")
        self.status_label.pack(side="left", fill="x", expand=True)
        
        # Account count
        self.account_count_label = ttk.Label(container,
                                           text="Account: 0",
                                           style="Muted.TLabel")
        self.account_count_label.pack(side="right")
        
    def toggle_password_visibility(self):
        """Alterna visibilità password"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="•")
            
    def update_status(self, message, status="ready"):
        """Aggiorna lo status con indicatore"""
        self.status_label.config(text=message)
        self.status_indicator.set_status(status)
        self.root.update_idletasks()
        
    def update_status_threadsafe(self, message, status="ready"):
        """Versione thread-safe dell'aggiornamento status"""
        self.root.after(0, lambda: self.update_status(message, status))
        
    def update_account_list(self):
        """Aggiorna la lista degli account"""
        self.account_listbox.delete(0, tk.END)
        
        if os.path.exists(credentials_file):
            with open(credentials_file, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
                
            # Ordina alfabeticamente
            usernames = sorted(credentials.keys())
            
            for username in usernames:
                self.account_listbox.insert(tk.END, f"🎮 {username}")
                
            # Aggiorna conteggio
            self.account_count_label.config(text=f"Account: {len(usernames)}")
            self.update_status(f"Lista aggiornata - {len(usernames)} account trovati")
        else:
            self.account_count_label.config(text="Account: 0")
            self.update_status("Nessun account trovato")
            
    def search_accounts(self):
        """Ricerca account in tempo reale"""
        query = self.search_entry.get_value().lower()
        self.account_listbox.delete(0, tk.END)
        
        if os.path.exists(credentials_file):
            with open(credentials_file, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
                
            # Filtra e ordina
            filtered_usernames = sorted([
                username for username in credentials.keys()
                if query in username.lower()
            ])
            
            for username in filtered_usernames:
                self.account_listbox.insert(tk.END, f"🎮 {username}")
                
            # Aggiorna status
            if query:
                self.update_status(f"Trovati {len(filtered_usernames)} account per '{query}'")
            else:
                self.update_status(f"Mostrati {len(filtered_usernames)} account")
                
    def save_credentials(self):
        """Salva le credenziali"""
        username = self.username_entry.get_value().strip()
        password = self.password_entry.get_value()
        
        if not username or not password:
            self.update_status("Errore: Username e password sono richiesti", "error")
            messagebox.showerror("Input Invalido", "Inserisci sia username che password")
            return
            
        # Carica credenziali esistenti
        if os.path.exists(credentials_file):
            with open(credentials_file, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
        else:
            credentials = {}
            
        # Controlla duplicati
        if username in credentials:
            confirm = messagebox.askyesno(
                "Account Esistente",
                f"L'account '{username}' esiste già.\n"
                "Vuoi aggiornare la password?"
            )
            if not confirm:
                self.update_status("Operazione annullata")
                return
                
        # Salva
        credentials[username] = password
        
        try:
            with open(credentials_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2)
                
            self.update_status(f"Account '{username}' salvato con successo", "success")
            self.clear_form()
            self.update_account_list()
            
            # Passa alla tab account
            self.notebook.select(0)
            
        except Exception as e:
            self.update_status(f"Errore nel salvare: {e}", "error")
            messagebox.showerror("Errore", f"Impossibile salvare l'account:\n{e}")
            
    def clear_form(self):
        """Pulisce il form"""
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, self.username_entry.placeholder)
        self.username_entry.config(fg=self.username_entry.placeholder_color)
        self.username_entry.is_placeholder_active = True
        
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, self.password_entry.placeholder)
        self.password_entry.config(fg=self.password_entry.placeholder_color)
        self.password_entry.is_placeholder_active = True
        
        self.show_password_var.set(False)
        self.password_entry.config(show="•")
        
    def get_selected_account(self):
        """Ottiene l'account selezionato dalla lista"""
        try:
            # Ottieni l'indice selezionato
            selection = self.account_listbox.curselection()
            if not selection:
                return None
                
            # Ottieni il testo dell'elemento selezionato
            selected_text = self.account_listbox.get(selection[0])
            if selected_text and selected_text.startswith("🎮 "):
                return selected_text[2:]  # Rimuove l'emoji e lo spazio
            return None
        except Exception as e:
            print(f"Errore nel get_selected_account: {e}")
            return None
            
    def edit_credentials(self):
        """Modifica l'account selezionato"""
        selected_account = self.get_selected_account()
        if not selected_account:
            self.update_status("Errore: Nessun account selezionato", "error")
            messagebox.showwarning("Selezione Mancante", "Seleziona un account dalla lista")
            return
            
        # Carica credenziali
        if not os.path.exists(credentials_file):
            self.update_status("File credenziali non trovato", "error")
            return
            
        with open(credentials_file, 'r', encoding='utf-8') as f:
            credentials = json.load(f)
            
        if selected_account not in credentials:
            self.update_status("Account non trovato", "error")
            return
            
        # Finestra di modifica
        self.show_edit_dialog(selected_account, credentials[selected_account])
        
    def show_edit_dialog(self, username, password):
        """Mostra dialog di modifica"""
        # Finestra modale
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Modifica Account")
        edit_window.configure(bg=COLORS["bg_primary"])
        edit_window.grab_set()
        edit_window.focus_set()
        
        # Dimensioni e centratura
        window_width = 450
        window_height = 300
        screen_width = edit_window.winfo_screenwidth()
        screen_height = edit_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        edit_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        edit_window.resizable(False, False)
        
        # Container principale
        main_container = ModernFrame(edit_window, bg_color=COLORS["bg_secondary"])
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        main_container.configure(padx=20, pady=20)
        
        # Header
        header = ttk.Label(main_container,
                          text=f"Modifica Account: {username}",
                          style="Header.TLabel")
        header.pack(pady=(0, 20))
        
        # Form
        # Username
        username_frame = tk.Frame(main_container, bg=COLORS["bg_secondary"])
        username_frame.pack(fill="x", pady=(0, 15))
        
        username_label = ttk.Label(username_frame, text="Nome Utente", style="Body.TLabel")
        username_label.pack(anchor="w", pady=(0, 5))
        
        username_var = tk.StringVar(value=username)
        username_entry = ModernEntry(username_frame, textvariable=username_var)
        username_entry.pack(fill="x")
        
        # Password
        password_frame = tk.Frame(main_container, bg=COLORS["bg_secondary"])
        password_frame.pack(fill="x", pady=(0, 15))
        
        password_label = ttk.Label(password_frame, text="Password", style="Body.TLabel")
        password_label.pack(anchor="w", pady=(0, 5))
        
        password_var = tk.StringVar(value=password)
        password_entry = ModernEntry(password_frame, textvariable=password_var, show="•")
        password_entry.pack(fill="x")
        
        # Show password
        show_pass_var = tk.BooleanVar()
        
        def toggle_edit_password():
            if show_pass_var.get():
                password_entry.config(show="")
            else:
                password_entry.config(show="•")
                
        show_check = tk.Checkbutton(
            main_container,
            text="Mostra password",
            variable=show_pass_var,
            command=toggle_edit_password,
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_secondary"],
            selectcolor=COLORS["surface"],
            activebackground=COLORS["bg_secondary"],
            font=('Segoe UI', 9)
        )
        show_check.pack(anchor="w", pady=(0, 20))
        
        # Pulsanti
        buttons_frame = tk.Frame(main_container, bg=COLORS["bg_secondary"])
        buttons_frame.pack(fill="x")
        
        def save_edit():
            new_username = username_var.get().strip()
            new_password = password_var.get().strip()
            
            if not new_username or not new_password:
                messagebox.showwarning("Input Invalido", "Username e password sono richiesti")
                return
                
            # Carica credenziali correnti
            with open(credentials_file, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
                
            # Controlla se nuovo username esiste
            if new_username != username and new_username in credentials:
                messagebox.showwarning("Username Esistente", 
                                     f"L'username '{new_username}' esiste già")
                return
                
            # Aggiorna
            if new_username != username:
                del credentials[username]
            credentials[new_username] = new_password
            
            # Salva
            with open(credentials_file, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2)
                
            self.update_status_threadsafe(f"Account aggiornato: {new_username}", "success")
            self.update_account_list()
            edit_window.destroy()
            
        # Salva
        save_btn = AnimatedButton(buttons_frame,
                                text="💾 Salva Modifiche",
                                bg=COLORS["success"],
                                bg_hover=COLORS["accent_primary"],
                                command=save_edit)
        save_btn.pack(side="left", padx=(0, 10))
        
        # Annulla
        cancel_btn = AnimatedButton(buttons_frame,
                                  text="❌ Annulla",
                                  bg=COLORS["surface"],
                                  bg_hover=COLORS["danger"],
                                  command=edit_window.destroy)
        cancel_btn.pack(side="left")
        
    def delete_credentials(self):
        """Elimina l'account selezionato"""
        selected_account = self.get_selected_account()
        if not selected_account:
            self.update_status("Errore: Nessun account selezionato", "error")
            messagebox.showwarning("Selezione Mancante", "Seleziona un account dalla lista")
            return
            
        # Conferma eliminazione
        confirm = messagebox.askyesno(
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare l'account '{selected_account}'?\n\n"
            "Questa azione non può essere annullata.",
            icon="warning"
        )
        
        if not confirm:
            self.update_status("Eliminazione annullata")
            return
            
        try:
            # Carica e aggiorna credenziali
            with open(credentials_file, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
                
            if selected_account in credentials:
                del credentials[selected_account]
                
                with open(credentials_file, 'w', encoding='utf-8') as f:
                    json.dump(credentials, f, indent=2)
                    
                self.update_status(f"Account '{selected_account}' eliminato", "success")
                self.update_account_list()
            else:
                self.update_status("Account non trovato", "error")
                
        except Exception as e:
            self.update_status(f"Errore nell'eliminazione: {e}", "error")
            messagebox.showerror("Errore", f"Impossibile eliminare l'account:\n{e}")
            
    def export_credentials(self):
        """Esporta le credenziali"""
        if not os.path.exists(credentials_file):
            self.update_status("Nessun account da esportare", "warning")
            messagebox.showwarning("Export Warning", "Non ci sono account da esportare")
            return
            
        export_path = filedialog.asksaveasfilename(
            title="Esporta Account",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialname=f"lol_accounts_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        if not export_path:
            self.update_status("Export annullato")
            return
            
        try:
            with open(credentials_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            self.update_status(f"Esportati {len(data)} account in {os.path.basename(export_path)}", "success")
            messagebox.showinfo("Export Completato", 
                              f"Account esportati con successo!\n\nFile: {os.path.basename(export_path)}\nAccount: {len(data)}")
            
        except Exception as e:
            self.update_status(f"Errore nell'export: {e}", "error")
            messagebox.showerror("Export Error", f"Impossibile esportare:\n{e}")
            
    def import_credentials(self):
        """Importa le credenziali"""
        import_path = filedialog.askopenfilename(
            title="Importa Account",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not import_path:
            self.update_status("Import annullato")
            return
            
        try:
            # Leggi file import
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_data = json.load(f)
                
            if not isinstance(imported_data, dict):
                raise ValueError("Formato file non valido")
                
            # Carica credenziali correnti
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r', encoding='utf-8') as f:
                    current_data = json.load(f)
            else:
                current_data = {}
                
            # Controlla duplicati
            duplicates = set(imported_data.keys()) & set(current_data.keys())
            if duplicates:
                choice = messagebox.askyesnocancel(
                    "Account Duplicati",
                    f"Trovati {len(duplicates)} account duplicati.\n\n"
                    "Sì: Sovrascrivi account esistenti\n"
                    "No: Salta account esistenti\n"
                    "Annulla: Ferma importazione"
                )
                
                if choice is None:
                    self.update_status("Import annullato")
                    return
                elif not choice:  # No - salta duplicati
                    for dupe in duplicates:
                        imported_data.pop(dupe, None)
                        
            # Aggiorna e salva
            current_data.update(imported_data)
            
            with open(credentials_file, 'w', encoding='utf-8') as f:
                json.dump(current_data, f, indent=2)
                
            self.update_status(f"Importati {len(imported_data)} account", "success")
            self.update_account_list()
            
            messagebox.showinfo("Import Completato",
                              f"Account importati con successo!\n\nNuovi account: {len(imported_data)}")
            
        except Exception as e:
            self.update_status(f"Errore nell'import: {e}", "error")
            messagebox.showerror("Import Error", f"Impossibile importare:\n{e}")
            
    # === CLIENT CONTROL METHODS ===
    
    def open_client(self):
        """Apre il client League of Legends"""
        self.update_status_threadsafe("Aprendo Riot Client...", "working")
        
        try:
            # Chiudi client esistenti
            self.close_league_client()
            self.close_riot_client()
            time.sleep(2)
            
            # Apri nuovo client
            command = [
                riot_client_path,
                "--launch-product=league_of_legends",
                "--launch-patchline=live"
            ]
            subprocess.Popen(command)
            self.update_status_threadsafe("Riot Client avviato", "success")
            
        except Exception as e:
            self.update_status_threadsafe(f"Errore apertura client: {e}", "error")
            
    def open_client_secondary(self):
        """Apre un client secondario"""
        self.update_status_threadsafe("Aprendo Client Secondario...", "working")
        
        try:
            subprocess.Popen([riot_client_path, "--allow-multiple-clients"])
            self.update_status_threadsafe("Client Secondario avviato", "success")
        except Exception as e:
            self.update_status_threadsafe(f"Errore apertura secondario: {e}", "error")
            
    def close_riot_client(self):
        """Chiude il Riot Client"""
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'] == "RiotClientServices.exe":
                    subprocess.run(["taskkill", "/F", "/PID", str(proc.info['pid'])])
                    self.update_status_threadsafe("Riot Client chiuso", "success")
                    return
                    
            self.update_status_threadsafe("Riot Client non in esecuzione")
        except Exception as e:
            self.update_status_threadsafe(f"Errore chiusura Riot Client: {e}", "error")
            
    def close_league_client(self):
        """Chiude il League Client"""
        try:
            for proc in psutil.process_iter(['name', 'pid']):
                if proc.info['name'] == "LeagueClient.exe":
                    subprocess.run(["taskkill", "/F", "/PID", str(proc.info['pid'])])
                    self.update_status_threadsafe("League Client chiuso", "success")
                    return
                    
            self.update_status_threadsafe("League Client non in esecuzione")
        except Exception as e:
            self.update_status_threadsafe(f"Errore chiusura League Client: {e}", "error")
            
    def login_to_client(self):
        """Login al client principale"""
        selected_account = self.get_selected_account()
        if not selected_account:
            self.update_status_threadsafe("Errore: Nessun account selezionato", "error")
            messagebox.showwarning("Selezione Mancante", "Seleziona un account dalla lista")
            return
            
        self._perform_login(selected_account, is_secondary=False)
        
    def login_to_client_secondary(self):
        """Login al client secondario"""
        selected_account = self.get_selected_account()
        if not selected_account:
            self.update_status_threadsafe("Errore: Nessun account selezionato", "error")
            messagebox.showwarning("Selezione Mancante", "Seleziona un account dalla lista")
            return
            
        self._perform_login(selected_account, is_secondary=True)
        
    def _perform_login(self, username, is_secondary=False):
        """Esegue il processo di login"""
        try:
            # Carica credenziali
            with open(credentials_file, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
                
            if username not in credentials:
                self.update_status_threadsafe("Account non trovato", "error")
                return
                
            password = credentials[username]
            login_type = "Secondario" if is_secondary else "Principale"
            
            # Mostra progress window
            progress_window = self._create_login_progress_window(username, login_type)
            
            def update_progress(message):
                try:
                    progress_window.status_label.config(text=message)
                    progress_window.update_idletasks()
                except:
                    pass
                    
            # Avvia client
            if is_secondary:
                self.open_client_secondary()
            else:
                self.open_client()
                
            update_progress("Attendo schermata login...")
            
            # Attendi client pronto
            timeout = 120
            while timeout > 0:
                if is_process_running("RiotClientServices.exe") and is_image_on_screen(verification_image_path):
                    update_progress("Inserendo credenziali...")
                    break
                time.sleep(1)
                timeout -= 1
            else:
                progress_window.destroy()
                self.update_status_threadsafe("Timeout: Client non pronto", "error")
                return
                
            # Inserisci credenziali
            pyautogui.write(username)
            pyautogui.press('tab')
            pyautogui.write(password)
            pyautogui.press('enter')
            
            update_progress("Login inviato, attendo League Client...")
            
            # Attendi League Client
            wait_time = 0
            while wait_time < 120:
                time.sleep(1)
                if is_process_running("LeagueClient.exe"):
                    update_progress("Login completato!")
                    time.sleep(2)
                    progress_window.destroy()
                    
                    self.update_status_threadsafe(
                        f"Login {login_type} completato per {username}", "success"
                    )
                    
                    # Chiudi Riot Client dopo login
                    if not is_secondary:
                        time.sleep(5)
                        self.click_close_riot_client()
                    break
                wait_time += 1
            else:
                progress_window.destroy()
                self.update_status_threadsafe("League Client non rilevato", "error")
                
        except Exception as e:
            self.update_status_threadsafe(f"Errore nel login: {e}", "error")
            messagebox.showerror("Errore Login", f"Impossibile completare il login:\n{e}")
            
    def _create_login_progress_window(self, username, login_type):
        """Crea finestra di progresso per il login"""
        progress_window = tk.Toplevel(self.root)
        progress_window.title(f"Login {login_type}")
        progress_window.configure(bg=COLORS["bg_primary"])
        progress_window.grab_set()
        
        # Centratura
        window_width = 400
        window_height = 250
        screen_width = progress_window.winfo_screenwidth()
        screen_height = progress_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        progress_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        progress_window.resizable(False, False)
        
        # Container
        container = ModernFrame(progress_window, bg_color=COLORS["bg_secondary"])
        container.pack(fill="both", expand=True, padx=20, pady=20)
        container.configure(padx=20, pady=20)
        
        # Header
        header = ttk.Label(container,
                          text=f"Login {login_type}",
                          style="Header.TLabel")
        header.pack(pady=(0, 15))
        
        # Account info
        account_frame = tk.Frame(container, bg=COLORS["bg_secondary"])
        account_frame.pack(fill="x", pady=(0, 15))
        
        account_label = ttk.Label(account_frame, text="Account:", style="Muted.TLabel")
        account_label.pack(anchor="w")
        
        username_label = ttk.Label(account_frame, text=username, style="Body.TLabel")
        username_label.pack(anchor="w", pady=(2, 0))
        
        # Progress bar
        progress_bar = ttk.Progressbar(
            container,
            mode="indeterminate",
            length=350,
            style="Modern.Horizontal.TProgressbar"
        )
        progress_bar.pack(pady=(0, 15))
        progress_bar.start()
        
        # Status
        status_label = ttk.Label(container,
                               text="Inizializzazione...",
                               style="Muted.TLabel")
        status_label.pack()
        
        # Salva riferimento al label per aggiornamenti
        progress_window.status_label = status_label
        
        return progress_window
        
    def click_close_riot_client(self):
        """Chiude solo la finestra del Riot Client senza terminare il processo"""
        try:
            # Trova finestra Riot Client usando pygetwindow
            riot_window = None
            for window in gw.getAllWindows():
                if "Riot Client" in window.title and window.visible:
                    riot_window = window
                    break
                    
            if riot_window:
                # Metodo 1: Prova a minimizzare/nascondere la finestra
                try:
                    riot_window.minimize()
                    self.update_status_threadsafe("Finestra Riot Client minimizzata", "success")
                    return
                except Exception:
                    pass
                
                # Metodo 2: Usa pywinauto per chiudere solo la finestra
                try:
                    app = Application().connect(title_re=".*Riot Client.*")
                    main_window = app.window(title_re=".*Riot Client.*")
                    
                    # Invia comando di chiusura finestra (ALT+F4) invece di terminare processo
                    main_window.send_keystrokes("%{F4}")
                    self.update_status_threadsafe("Finestra Riot Client chiusa", "success")
                    return
                except Exception:
                    pass
                    
                # Metodo 3: Usa SendMessage per chiudere la finestra
                try:
                    import win32gui
                    import win32con
                    
                    hwnd = win32gui.FindWindow(None, riot_window.title)
                    if hwnd:
                        # Invia WM_CLOSE per chiudere la finestra senza terminare il processo
                        win32gui.SendMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                        self.update_status_threadsafe("Finestra Riot Client chiusa (Win32)", "success")
                        return
                except ImportError:
                    # win32gui non disponibile, continua con metodi alternativi
                    pass
                except Exception:
                    pass
                    
                # Metodo 4: Usa pyautogui per simulare ALT+F4 sulla finestra attiva
                try:
                    riot_window.activate()
                    time.sleep(0.5)
                    pyautogui.hotkey('alt', 'f4')
                    self.update_status_threadsafe("Finestra Riot Client chiusa (ALT+F4)", "success")
                    return
                except Exception:
                    pass
                    
            else:
                self.update_status_threadsafe("Finestra Riot Client non trovata")
                
        except Exception as e:
            self.update_status_threadsafe(f"Errore chiusura finestra: {e}", "error")
            
        # Se tutti i metodi falliscono, avvisa l'utente
        self.update_status_threadsafe("Impossibile chiudere la finestra automaticamente", "warning")

# === HELPER FUNCTIONS ===

def is_process_running(process_name):
    """Controlla se un processo è in esecuzione"""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] == process_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False

def is_image_on_screen(image_path):
    """Controlla se un'immagine è visibile sullo schermo"""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=0.8)
        return location is not None
    except Exception:
        return False

# === MAIN APPLICATION ===

def main():
    """Funzione principale"""
    root = tk.Tk()
    app = RiotAccountManager(root)
    
    # Bind per chiusura pulita
    def on_closing():
        try:
            # Salva eventuali dati in sospeso
            if hasattr(app, 'current_operation') and app.current_operation:
                app.update_status("Operazione in corso, attendi...")
                return
                
            root.quit()
            root.destroy()
        except Exception as e:
            print(f"Errore durante la chiusura: {e}")
            root.destroy()
            
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Applicazione interrotta dall'utente")
    except Exception as e:
        print(f"Errore critico: {e}")
        messagebox.showerror("Errore Critico", f"Si è verificato un errore critico:\n{e}")
    finally:
        try:
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    # Verifica dipendenze critiche
    try:
        import tkinter
        import json
        import os
        import psutil
        import pyautogui
        import pygetwindow
        from PIL import Image
    except ImportError as e:
        print(f"Errore: Dipendenza mancante - {e}")
        print("Installa le dipendenze richieste:")
        print("pip install pillow psutil pyautogui pygetwindow pywinauto")
        sys.exit(1)
    
    # Verifica path critici
    if not os.path.exists(os.path.dirname(credentials_file)):
        try:
            os.makedirs(os.path.dirname(credentials_file))
        except Exception as e:
            print(f"Impossibile creare directory credenziali: {e}")
    
    if not os.path.exists(riot_client_path):
        print(f"Warning: Riot Client non trovato in {riot_client_path}")
        print("Verifica che League of Legends sia installato correttamente")
    
    # Avvia applicazione
    main()