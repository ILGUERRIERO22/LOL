import requests
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import os
import base64
import threading
import time
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
from functools import lru_cache

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure Base URL and Headers
BASE_URL = "https://euw-red.lol.sgp.pvp.net"

# App theme and styling constants
THEME = "darkly"
PRIMARY_COLOR = "#3b82f6"
SECONDARY_COLOR = "#1e293b"
ACCENT_COLOR = "#06b6d4"
SUCCESS_COLOR = "#10b981"
ERROR_COLOR = "#ef4444"
WARNING_COLOR = "#f59e0b"
TEXT_COLOR = "#f8fafc"
MUTED_COLOR = "#94a3b8"
PADDING = 20

class RiotAPIOptimizer:
    """Ottimizzatore per API Riot lente con cache aggressiva."""
    
    def __init__(self):
        # Session riutilizzabile per connection pooling
        self.session = requests.Session()
        self.session.verify = False
        
        # Configurazione connessioni ottimizzata
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3,
            pool_block=False
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        # Cache su disco
        self.cache_dir = os.path.expanduser("~/lol_gift_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Timeout ottimizzati
        self.timeout = (5, 30)  # (connect, read)
    
    def get_cache_path(self, key):
        """Percorso file cache per una chiave."""
        safe_key = "".join(c for c in key if c.isalnum() or c in ('-', '_'))
        return os.path.join(self.cache_dir, f"{safe_key}.json")
    
    def load_from_cache(self, key, max_age_minutes=10):
        """Carica dati dalla cache se non scaduti."""
        cache_path = self.get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            # Controlla età del file
            file_age = time.time() - os.path.getmtime(cache_path)
            if file_age > (max_age_minutes * 60):
                return None
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def save_to_cache(self, key, data):
        """Salva dati nella cache."""
        cache_path = self.get_cache_path(key)
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    def make_request_with_retry(self, url, headers, max_retries=3):
        """Richiesta con retry automatico e timeout progressivo."""
        for attempt in range(max_retries):
            try:
                # Timeout progressivo
                timeout = (5, 20 + (attempt * 10))
                
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limit
                    wait_time = 2 ** attempt
                    print(f"Rate limit - attesa {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.Timeout:
                print(f"Timeout tentativo {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)
            except requests.exceptions.ConnectionError:
                print(f"Errore connessione tentativo {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(2)
        
        raise Exception("Troppi tentativi falliti")
    
    def clear_cache(self):
        """Pulisce tutta la cache."""
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, filename))
        except Exception:
            pass

# Istanza globale
api_optimizer = RiotAPIOptimizer()

@lru_cache(maxsize=1)
def fetch_lockfile_data():
    """Fetch data from the League of Legends lockfile."""
    lockfile_path = os.path.expanduser("C:\\Riot Games\\League of Legends\\lockfile")
    if not os.path.exists(lockfile_path):
        raise FileNotFoundError("Lockfile non trovato. Assicurati che il client League of Legends sia in esecuzione.")

    with open(lockfile_path, "r") as lockfile:
        data = lockfile.read().split(":")
        return {
            "protocol": data[4],
            "port": data[2],
            "password": data[3],
        }

def fetch_bearer_token():
    """Get the authentication bearer token from League client with aggressive caching."""
    cache_key = "bearer_token"
    
    # Cache per 5 minuti
    cached = api_optimizer.load_from_cache(cache_key, max_age_minutes=5)
    if cached:
        return cached
    
    lockfile_data = fetch_lockfile_data()
    protocol = lockfile_data["protocol"]
    port = lockfile_data["port"]
    password = lockfile_data["password"]

    basic_auth = base64.b64encode(f"riot:{password}".encode()).decode()
    url = f"{protocol}://127.0.0.1:{port}/lol-rso-auth/v1/authorization/access-token"
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    response = api_optimizer.make_request_with_retry(url, headers)
    token = response.json().get("token", None)
    
    # Salva in cache
    api_optimizer.save_to_cache(cache_key, token)
    return token

def fetch_current_summoner():
    """Get current summoner information with caching."""
    cache_key = "current_summoner"
    
    # Cache per 30 minuti
    cached = api_optimizer.load_from_cache(cache_key, max_age_minutes=30)
    if cached:
        return cached
    
    lockfile_data = fetch_lockfile_data()
    protocol = lockfile_data["protocol"]
    port = lockfile_data["port"]
    password = lockfile_data["password"]

    basic_auth = base64.b64encode(f"riot:{password}".encode()).decode()
    url = f"{protocol}://127.0.0.1:{port}/lol-summoner/v1/current-summoner"
    headers = {
        "Authorization": f"Basic {basic_auth}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    response = api_optimizer.make_request_with_retry(url, headers)
    account_id = response.json().get("accountId", None)
    
    api_optimizer.save_to_cache(cache_key, account_id)
    return account_id

def fetch_friends():
    """Fetch friends list from League client with aggressive caching."""
    cache_key = "friends_list"
    
    # Cache per 30 minuti (gli amici non cambiano spesso)
    cached = api_optimizer.load_from_cache(cache_key, max_age_minutes=30)
    if cached:
        return cached
    
    token = fetch_bearer_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    url = f"{BASE_URL}/storefront/v3/gift/friends?language=it_IT"
    
    response = api_optimizer.make_request_with_retry(url, headers)
    friends = response.json().get("friends", [])
    
    # Cache molto aggressiva
    api_optimizer.save_to_cache(cache_key, friends)
    return friends

def fetch_gift_items(summoner_id, gift_item_id):
    """Fetch available gift items for a specific friend with aggressive caching."""
    cache_key = f"items_{summoner_id}_{gift_item_id}"
    
    # Cache per 60 minuti (oggetti regalo cambiano raramente)
    cached = api_optimizer.load_from_cache(cache_key, max_age_minutes=60)
    if cached:
        return cached
    
    token = fetch_bearer_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    url = f"{BASE_URL}/storefront/v3/gift/giftItems?language=it_IT&summonerId={summoner_id}&giftItemId={gift_item_id}"
    
    response = api_optimizer.make_request_with_retry(url, headers)
    items = response.json().get("catalog", [])
    
    # Cache molto aggressiva
    api_optimizer.save_to_cache(cache_key, items)
    return items

def send_gift(payload):
    """Send a gift to a friend."""
    token = fetch_bearer_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    
    url = f"{BASE_URL}/storefront/v3/gift?language=it_IT"
    response = api_optimizer.session.post(url, headers=headers, json=payload, timeout=api_optimizer.timeout)
    return response

def preload_popular_items(summoner_id, progress_callback=None):
    """Precarica in background i tipi di regalo più popolari."""
    popular_gift_types = [3, 7, 1010, 9, 2, 1]  # Misterioso, RP, Hextech, Misterioso+, Skin, Champion
    
    def load_single_type(gift_type):
        try:
            items = fetch_gift_items(summoner_id, gift_type)
            if progress_callback:
                progress_callback(f"Precaricato tipo {gift_type}: {len(items)} oggetti")
            return gift_type, len(items)
        except Exception as e:
            if progress_callback:
                progress_callback(f"Errore precaricamento tipo {gift_type}: {str(e)}")
            return gift_type, 0
    
    # Esegui in parallelo per velocizzare
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(load_single_type, gt) for gt in popular_gift_types]
        
        results = {}
        for future in as_completed(futures):
            gift_type, count = future.result()
            results[gift_type] = count
    
    return results

class ModernStatusBar(ttk.Frame):
    """Barra di stato ottimizzata."""
    def __init__(self, master):
        super().__init__(master)
        self.configure(padding=(PADDING, 10))
        
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=X, expand=True)
        
        self.status_icon = ttk.Label(main_frame, text="●", font=("Segoe UI", 12))
        self.status_icon.pack(side=LEFT, padx=(0, 10))
        
        self.label = ttk.Label(
            main_frame, 
            text="Pronto per inviare regali",
            font=("Segoe UI", 10),
            foreground=TEXT_COLOR
        )
        self.label.pack(side=LEFT, fill=X, expand=True)
        
        self.progress = ttk.Progressbar(
            self,
            mode='indeterminate',
            bootstyle="primary-striped"
        )
        
        self.current_message_type = "info"
        
    def set_message(self, message, message_type="info", show_progress=False):
        """Imposta il messaggio di stato."""
        self.label.config(text=message)
        
        colors = {
            "info": ACCENT_COLOR,
            "success": SUCCESS_COLOR, 
            "error": ERROR_COLOR,
            "warning": WARNING_COLOR,
            "loading": PRIMARY_COLOR
        }
        
        color = colors.get(message_type, ACCENT_COLOR)
        self.status_icon.config(foreground=color)
        self.label.config(foreground=color)
        self.current_message_type = message_type
        
        if show_progress and message_type == "loading":
            self.progress.pack(fill=X, pady=(5, 0))
            self.progress.start()
        else:
            self.progress.stop()
            self.progress.pack_forget()
        
        if message_type in ["info", "success"]:
            self.after(3000, self.clear_message)
            
    def clear_message(self):
        """Pulisce il messaggio di stato."""
        if self.current_message_type in ["info", "success"]:
            self.label.config(text="Pronto per inviare regali", foreground=TEXT_COLOR)
            self.status_icon.config(foreground=ACCENT_COLOR)
            self.progress.stop()
            self.progress.pack_forget()

def show_available_items_optimized(items, friend_id, gift_item_id, message, account_id, root_window):
    """Finestra oggetti ottimizzata con lazy loading."""
    window = ttk.Toplevel(title="Oggetti Disponibili")
    window.geometry("900x700")
    window.minsize(800, 600)
    
    # Header
    header_frame = ttk.Frame(window, bootstyle="primary", padding=PADDING)
    header_frame.pack(fill=X)
    
    title_frame = ttk.Frame(header_frame)
    title_frame.pack(fill=X)
    
    ttk.Label(
        title_frame,
        text="Seleziona un Oggetto da Regalare",
        font=("Segoe UI", 18, "bold"),
        foreground="white"
    ).pack(side=LEFT)
    
    main_container = ttk.Frame(window)
    main_container.pack(fill=BOTH, expand=True, padx=PADDING, pady=PADDING)
    
    # Controlli
    controls_frame = ttk.Frame(main_container)
    controls_frame.pack(fill=X, pady=(0, 15))
    
    # Ricerca con debouncing
    search_frame = ttk.LabelFrame(controls_frame, text="Ricerca", padding=10)
    search_frame.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
    
    search_var = ttk.StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("Segoe UI", 11))
    search_entry.pack(fill=X)
    
    # Statistiche
    stats_label = ttk.Label(
        controls_frame,
        text=f"Totale: {len(items)} oggetti",
        font=("Segoe UI", 10),
        foreground=MUTED_COLOR
    )
    stats_label.pack(side=RIGHT)
    
    # Treeview ottimizzato
    tree_container = ttk.Frame(main_container)
    tree_container.pack(fill=BOTH, expand=True)
    
    cols = ("Nome", "Costo RP", "Tipo", "ID Oggetto")
    tree = ttk.Treeview(
        tree_container,
        columns=cols,
        show="headings",
        height=15
    )
    
    # Configurazione colonne
    tree.column("Nome", width=350, anchor="w")
    tree.column("Costo RP", width=120, anchor="center")
    tree.column("Tipo", width=150, anchor="center")
    tree.column("ID Oggetto", width=120, anchor="center")
    
    for col in cols:
        tree.heading(col, text=col, anchor="center")
    
    scrollbar = ttk.Scrollbar(tree_container, orient=VERTICAL, command=tree.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(side=LEFT, fill=BOTH, expand=True)
    
    # Tags per alternare colori
    tree.tag_configure('evenrow', background='#2d3748')
    tree.tag_configure('oddrow', background='#1a202c')
    
    status_bar = ModernStatusBar(window)
    status_bar.pack(fill=X, side=BOTTOM)
    
    # Variabili per lazy loading
    search_timeout = None
    
    def populate_tree_optimized(filtered_items, start_index=0, batch_size=50):
        """Popola la tree view con lazy loading."""
        if start_index == 0:
            for row in tree.get_children():
                tree.delete(row)
        
        end_index = min(start_index + batch_size, len(filtered_items))
        batch = filtered_items[start_index:end_index]
        
        for i, item in enumerate(batch):
            actual_index = start_index + i
            tag = 'evenrow' if actual_index % 2 == 0 else 'oddrow'
            rp_cost = f"{item['rp']:,}" if item['rp'] else "Gratuito"
            tree.insert(
                "", "end",
                values=(item["name"], rp_cost, item["inventoryType"], item["itemId"]),
                tags=(tag,)
            )
        
        stats_label.config(text=f"Mostrati: {end_index} di {len(filtered_items)} oggetti")
        
        if end_index < len(filtered_items):
            window.after(10, lambda: populate_tree_optimized(filtered_items, end_index, batch_size))
        else:
            status_bar.set_message(f"Caricati tutti i {len(filtered_items)} oggetti", "success")
    
    def debounced_search():
        """Ricerca con debouncing."""
        nonlocal search_timeout
        
        if search_timeout:
            window.after_cancel(search_timeout)
        
        def do_search():
            search_text = search_var.get().lower()
            if not search_text:
                filtered_items = items
            else:
                filtered_items = [
                    item for item in items 
                    if search_text in item["name"].lower() or 
                       search_text in item["inventoryType"].lower()
                ]
            
            status_bar.set_message("Filtraggio oggetti...", "loading", show_progress=True)
            populate_tree_optimized(filtered_items)
        
        search_timeout = window.after(300, do_search)
    
    search_var.trace_add("write", lambda *args: debounced_search())
    
    # Caricamento iniziale
    status_bar.set_message("Caricamento oggetti...", "loading", show_progress=True)
    window.after(10, lambda: populate_tree_optimized(items))
    
    # Bottoni di azione
    action_frame = ttk.Frame(main_container)
    action_frame.pack(fill=X, pady=(20, 0))
    
    def confirm_send():
        """Conferma e invia il regalo."""
        selected_item = tree.focus()
        if not selected_item:
            status_bar.set_message("Seleziona un oggetto dalla lista", "error")
            return
        
        item_data = tree.item(selected_item)["values"]
        selected_item_name = item_data[0]
        selected_item_cost_str = item_data[1]
        selected_item_id = item_data[3]
        selected_inventory_type = item_data[2]
        
        # Gestione del costo (FIX per l'errore AttributeError)
        if selected_item_cost_str == "Gratuito":
            selected_item_cost = 0
        else:
            if isinstance(selected_item_cost_str, int):
                selected_item_cost = selected_item_cost_str
            else:
                selected_item_cost = int(str(selected_item_cost_str).replace(",", ""))
        
        # Dialogo di conferma
        confirm = messagebox.askyesno(
            "Conferma Regalo",
            f"Inviare '{selected_item_name}' al tuo amico?\n\n"
            f"Costo: {selected_item_cost_str} RP\n"
            f"Messaggio: {message if message else '(Nessun messaggio)'}\n\n"
            f"Assicurati di avere abbastanza RP nel tuo account!",
            parent=window
        )
        
        if not confirm:
            return
            
        status_bar.set_message("Invio regalo in corso...", "loading", show_progress=True)
        
        def send_gift_async():
            try:
                payload = {
                    "customMessage": message,
                    "receiverSummonerId": friend_id,
                    "giftItemId": gift_item_id,
                    "accountId": account_id,
                    "items": [{
                        "inventoryType": selected_inventory_type,
                        "itemId": selected_item_id,
                        "ipCost": None,
                        "rpCost": selected_item_cost,
                        "quantity": 1
                    }]
                }
                
                response = send_gift(payload)
                
                def update_ui():
                    if response.status_code == 200:
                        status_bar.set_message("Regalo inviato con successo!", "success")
                        messagebox.showinfo(
                            "Successo", 
                            "Regalo inviato con successo!\n\nIl tuo amico ricevera una notifica.",
                            parent=window
                        )
                        window.after(2000, window.destroy)
                    else:
                        error_msg = f"Errore nell'invio del regalo: {response.text}"
                        status_bar.set_message(error_msg, "error")
                        messagebox.showerror("Errore", error_msg, parent=window)
                
                window.after(0, update_ui)
                
            except Exception as e:
                def show_error():
                    error_msg = f"Errore nell'invio: {str(e)}"
                    status_bar.set_message(error_msg, "error")
                    messagebox.showerror("Errore", error_msg, parent=window)
                
                window.after(0, show_error)
        
        threading.Thread(target=send_gift_async, daemon=True).start()
    
    # Bottoni
    button_container = ttk.Frame(action_frame)
    button_container.pack(side=RIGHT)
    
    ttk.Button(
        button_container,
        text="Annulla",
        command=window.destroy,
        bootstyle="secondary-outline",
        width=15
    ).pack(side=LEFT, padx=(0, 10))
    
    ttk.Button(
        button_container,
        text="Invia Regalo",
        command=confirm_send,
        bootstyle="success",
        width=15
    ).pack(side=LEFT)
    
    search_entry.focus()
    
    # Binding per Enter
    def on_enter(event):
        confirm_send()
    
    window.bind('<Return>', on_enter)

class OptimizedGiftApp:
    """Applicazione principale ottimizzata per API lente."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("League of Legends Gift Sender Pro - Optimized")
        self.root.geometry("700x800")
        self.root.minsize(650, 750)
        
        # Cache per i dati dell'app
        self.friends = []
        self.friend_options = {}
        self.preload_results = {}
        
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        """Configura l'interfaccia utente ottimizzata."""
        # Header
        header_frame = ttk.Frame(self.root, bootstyle="primary", padding=PADDING)
        header_frame.pack(fill=X)
        
        # Contenitore header
        header_content = ttk.Frame(header_frame)
        header_content.pack(fill=X)
        
        # Lato sinistro - Titolo
        left_frame = ttk.Frame(header_content)
        left_frame.pack(side=LEFT, fill=X, expand=True)
        
        title_label = ttk.Label(
            left_frame,
            text="LoL Gift Sender Pro - Optimized",
            font=("Segoe UI", 20, "bold"),
            foreground="white"
        )
        title_label.pack(anchor="w")
        
        subtitle_label = ttk.Label(
            left_frame,
            text="Versione ottimizzata per API lente",
            font=("Segoe UI", 10),
            foreground="#e2e8f0"
        )
        subtitle_label.pack(anchor="w")
        
        # Lato destro - Indicatore connessione
        right_frame = ttk.Frame(header_content)
        right_frame.pack(side=RIGHT)
        
        self.connection_indicator = ttk.Label(
            right_frame,
            text="● Verifica connessione...",
            font=("Segoe UI", 10),
            foreground=WARNING_COLOR
        )
        self.connection_indicator.pack(anchor="e")
        
        # Main container scrollabile
        from ttkbootstrap.scrolled import ScrolledFrame
        
        self.main_container = ScrolledFrame(
            self.root,
            autohide=True,
            padding=PADDING
        )
        self.main_container.pack(fill=BOTH, expand=True)
        
        self.create_friend_selection()
        self.create_message_input()
        self.create_gift_type_selection()
        self.create_action_buttons()
        self.create_cache_info()
        
        # Status bar
        self.status_bar = ModernStatusBar(self.root)
        self.status_bar.pack(fill=X, side=BOTTOM)
    
    def create_friend_selection(self):
        """Crea la sezione di selezione degli amici."""
        friend_frame = ttk.LabelFrame(
            self.main_container,
            text="Seleziona un Amico",
            padding=PADDING
        )
        friend_frame.pack(fill=X, pady=(0, 20))
        
        # Descrizione
        desc_label = ttk.Label(
            friend_frame,
            text="Scegli l'amico a cui vuoi inviare un regalo:",
            font=("Segoe UI", 10),
            foreground=MUTED_COLOR
        )
        desc_label.pack(anchor="w", pady=(0, 10))
        
        # Frame per la selezione
        friend_select_frame = ttk.Frame(friend_frame)
        friend_select_frame.pack(fill=X)
        
        ttk.Label(
            friend_select_frame,
            text="Amico:",
            font=("Segoe UI", 10, "bold")
        ).pack(side=LEFT, padx=(0, 10))
        
        # Combobox per gli amici
        self.friend_var = ttk.StringVar()
        self.friend_menu = ttk.Combobox(
            friend_select_frame,
            textvariable=self.friend_var,
            state="readonly",
            font=("Segoe UI", 11),
            width=40
        )
        self.friend_menu.pack(side=LEFT, fill=X, expand=True)
        
        # Bottone refresh
        refresh_btn = ttk.Button(
            friend_select_frame,
            text="Aggiorna",
            command=self.refresh_friends,
            bootstyle="primary-outline",
            width=10
        )
        refresh_btn.pack(side=LEFT, padx=(10, 0))
        
        # Info amici
        self.friend_info_label = ttk.Label(
            friend_frame,
            text="",
            font=("Segoe UI", 9),
            foreground=MUTED_COLOR
        )
        self.friend_info_label.pack(anchor="w", pady=(10, 0))
    
    def create_message_input(self):
        """Crea la sezione per il messaggio personalizzato."""
        message_frame = ttk.LabelFrame(
            self.main_container,
            text="Messaggio Personalizzato",
            padding=PADDING
        )
        message_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            message_frame,
            text="Aggiungi un messaggio personale al tuo regalo (opzionale):",
            font=("Segoe UI", 10),
            foreground=MUTED_COLOR
        ).pack(anchor="w", pady=(0, 10))
        
        # Entry per il messaggio
        self.message_entry = ttk.Entry(
            message_frame,
            font=("Segoe UI", 11)
        )
        self.message_entry.pack(fill=X, expand=True)
        
        # Contatore caratteri
        self.char_count_label = ttk.Label(
            message_frame,
            text="0/100 caratteri",
            font=("Segoe UI", 9),
            foreground=MUTED_COLOR
        )
        self.char_count_label.pack(anchor="e", pady=(5, 0))
        
        def update_char_count(*args):
            count = len(self.message_entry.get())
            self.char_count_label.config(text=f"{count}/100 caratteri")
            if count > 100:
                self.char_count_label.config(foreground=ERROR_COLOR)
            else:
                self.char_count_label.config(foreground=MUTED_COLOR)
        
        self.message_entry.bind('<KeyRelease>', update_char_count)
    
    def create_gift_type_selection(self):
        """Crea la sezione per la selezione del tipo di regalo."""
        gift_frame = ttk.LabelFrame(
            self.main_container,
            text="Tipo di Regalo",
            padding=PADDING
        )
        gift_frame.pack(fill=X, pady=(0, 20))
        
        ttk.Label(
            gift_frame,
            text="Seleziona il tipo di regalo che vuoi inviare:",
            font=("Segoe UI", 10),
            foreground=MUTED_COLOR
        ).pack(anchor="w", pady=(0, 15))
        
        # Mappa dei tipi di regalo
        self.gift_type_var = ttk.StringVar()
        self.gift_type_map = {
            "RP": 7,
            "Hextech": 1010,
            "Regalo Misterioso": 3,
            "Regalo Misterioso+": 9,
            "Champion Misterioso": 4,
            "Skin": 2,
            "Champion": 1,
            "Icona": 5,
        }
        
        # Grid per i bottoni
        gift_grid = ttk.Frame(gift_frame)
        gift_grid.pack(fill=X, pady=10)
        
        row, col = 0, 0
        for gift_type, gift_id in self.gift_type_map.items():
            btn = ttk.Radiobutton(
                gift_grid,
                text=gift_type,
                variable=self.gift_type_var,
                value=gift_type,
                bootstyle="primary-outline-toolbutton",
                width=18
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            col += 1
            if col > 2:  # 3 bottoni per riga
                col = 0
                row += 1
        
        for i in range(3):
            gift_grid.columnconfigure(i, weight=1)
    
    def create_action_buttons(self):
        """Crea i bottoni di azione principali."""
        action_frame = ttk.LabelFrame(
            self.main_container,
            text="Azioni",
            padding=PADDING
        )
        action_frame.pack(fill=X, pady=(20, 0))
        
        # Descrizione
        ttk.Label(
            action_frame,
            text="Dopo aver selezionato amico e tipo regalo, clicca qui per vedere gli oggetti disponibili:",
            font=("Segoe UI", 10),
            foreground=MUTED_COLOR,
            wraplength=600
        ).pack(anchor="w", pady=(0, 15))
        
        # Container per i bottoni
        button_container = ttk.Frame(action_frame)
        button_container.pack(fill=X)
        
        # Bottone principale - più grande e visibile
        self.browse_btn = ttk.Button(
            button_container,
            text="🛍️ Cerca Oggetti da Regalare",
            command=self.show_items_window,
            bootstyle="success",
            width=35,
            padding=(20, 15)
        )
        self.browse_btn.pack(fill=X, pady=(0, 10))
        
        # Frame per bottoni secondari
        secondary_buttons = ttk.Frame(button_container)
        secondary_buttons.pack(fill=X)
        
        # Bottone per pulire cache
        clear_cache_btn = ttk.Button(
            secondary_buttons,
            text="🧹 Pulisci Cache",
            command=self.clear_cache,
            bootstyle="warning-outline",
            width=15,
            padding=(10, 8)
        )
        clear_cache_btn.pack(side=LEFT, padx=(0, 10))
        
        # Bottone per aggiornare tutto
        refresh_all_btn = ttk.Button(
            secondary_buttons,
            text="🔄 Aggiorna Tutto",
            command=self.refresh_all,
            bootstyle="info-outline",
            width=15,
            padding=(10, 8)
        )
        refresh_all_btn.pack(side=LEFT)
    
    def create_cache_info(self):
        """Crea la sezione info cache."""
        cache_frame = ttk.Frame(self.main_container)
        cache_frame.pack(fill=X, pady=(15, 0))
        
        separator = ttk.Separator(cache_frame, orient='horizontal')
        separator.pack(fill=X, pady=(0, 10))
        
        self.cache_info_label = ttk.Label(
            cache_frame,
            text="Cache: Nessun dato",
            font=("Segoe UI", 9),
            foreground=MUTED_COLOR
        )
        self.cache_info_label.pack(anchor="w")
    
    def update_connection_status(self, message, status_type):
        """Aggiorna lo stato della connessione."""
        colors = {
            "loading": WARNING_COLOR,
            "success": SUCCESS_COLOR,
            "error": ERROR_COLOR,
            "warning": WARNING_COLOR
        }
        
        color = colors.get(status_type, MUTED_COLOR)
        
        self.connection_indicator.config(
            text=f"● {message}",
            foreground=color
        )
    
    def load_initial_data(self):
        """Carica i dati iniziali in modo asincrono."""
        def load_async():
            try:
                self.root.after(0, lambda: self.update_connection_status("Connessione...", "loading"))
                self.root.after(0, lambda: self.status_bar.set_message("Caricamento amici...", "loading", show_progress=True))
                
                # Carica la lista degli amici
                friends = fetch_friends()
                
                def update_friends_ui():
                    self.friends = friends
                    self.friend_options = {f"{friend['nick']}": friend['summonerId'] for friend in friends}
                    
                    if friends:
                        self.friend_menu["values"] = list(self.friend_options.keys())
                        self.friend_info_label.config(
                            text=f"Trovati {len(friends)} amici",
                            foreground=SUCCESS_COLOR
                        )
                        self.update_connection_status("Connesso", "success")
                        self.status_bar.set_message(f"{len(friends)} amici caricati", "success")
                        
                        # Avvia preloading
                        self.start_preloading()
                    else:
                        self.friend_info_label.config(
                            text="Nessun amico trovato",
                            foreground=WARNING_COLOR
                        )
                        self.update_connection_status("Connesso - nessun amico", "warning")
                        self.status_bar.set_message("Nessun amico trovato", "warning")
                
                self.root.after(0, update_friends_ui)
                
            except Exception as e:
                def show_error():
                    error_msg = f"Errore di connessione: {str(e)}"
                    self.friend_info_label.config(text=error_msg, foreground=ERROR_COLOR)
                    self.update_connection_status("Errore connessione", "error")
                    self.status_bar.set_message(error_msg, "error")
                    self.friends = []
                    self.friend_options = {}
                
                self.root.after(0, show_error)
        
        threading.Thread(target=load_async, daemon=True).start()
    
    def start_preloading(self):
        """Avvia preloading in background."""
        if not self.friends:
            return
        
        # Usa il primo amico per il preloading
        first_friend_id = self.friends[0]['summonerId']
        
        def preload_async():
            try:
                self.root.after(0, lambda: self.status_bar.set_message("Precaricamento oggetti popolari...", "loading", show_progress=True))
                
                def progress_callback(message):
                    self.root.after(0, lambda: self.cache_info_label.config(text=f"Preloading: {message}"))
                
                results = preload_popular_items(first_friend_id, progress_callback)
                
                def finish_preload():
                    self.preload_results = results
                    total_items = sum(results.values())
                    self.cache_info_label.config(text=f"Cache: {total_items} oggetti precaricati")
                    self.status_bar.set_message("Preloading completato", "success")
                
                self.root.after(0, finish_preload)
                
            except Exception as e:
                self.root.after(0, lambda: self.status_bar.set_message("Preloading fallito", "warning"))
        
        threading.Thread(target=preload_async, daemon=True).start()
    
    def refresh_friends(self):
        """Aggiorna la lista degli amici."""
        api_optimizer.clear_cache()
        self.status_bar.set_message("Aggiornamento lista amici...", "loading", show_progress=True)
        self.load_initial_data()
    
    def clear_cache(self):
        """Pulisce tutta la cache."""
        api_optimizer.clear_cache()
        self.cache_info_label.config(text="Cache: Pulita")
        self.status_bar.set_message("Cache pulita", "success")
    
    def refresh_all(self):
        """Aggiorna tutto: cache + amici + preloading."""
        def refresh_async():
            try:
                self.root.after(0, lambda: self.status_bar.set_message("Aggiornamento completo...", "loading", show_progress=True))
                
                # Pulisci cache
                api_optimizer.clear_cache()
                
                # Ricarica amici
                friends = fetch_friends()
                
                def update_ui():
                    self.friends = friends
                    self.friend_options = {f"{friend['nick']}": friend['summonerId'] for friend in friends}
                    
                    if friends:
                        self.friend_menu["values"] = list(self.friend_options.keys())
                        self.friend_info_label.config(
                            text=f"Aggiornati {len(friends)} amici",
                            foreground=SUCCESS_COLOR
                        )
                        self.cache_info_label.config(text="Cache: Aggiornata")
                        self.status_bar.set_message("Aggiornamento completato", "success")
                        
                        # Riavvia preloading
                        self.start_preloading()
                    else:
                        self.status_bar.set_message("Nessun amico trovato", "warning")
                
                self.root.after(0, update_ui)
                
            except Exception as e:
                self.root.after(0, lambda: self.status_bar.set_message(f"Errore aggiornamento: {str(e)}", "error"))
        
        threading.Thread(target=refresh_async, daemon=True).start()
    
    def show_items_window(self):
        """Mostra la finestra degli oggetti disponibili."""
        selected_gift_type = self.gift_type_var.get()
        friend_nick = self.friend_var.get()
        
        # Validazione
        if not friend_nick:
            self.status_bar.set_message("Seleziona prima un amico", "error")
            return
            
        if not selected_gift_type:
            self.status_bar.set_message("Seleziona un tipo di regalo", "error")
            return
        
        message = self.message_entry.get()
        if len(message) > 100:
            self.status_bar.set_message("Il messaggio non può superare i 100 caratteri", "error")
            return
        
        summoner_id = self.friend_options.get(friend_nick)
        gift_item_id = self.gift_type_map.get(selected_gift_type)
        
        self.status_bar.set_message(f"Caricamento oggetti {selected_gift_type}...", "loading", show_progress=True)
        
        def fetch_items_async():
            try:
                available_items = fetch_gift_items(summoner_id, gift_item_id)
                account_id = fetch_current_summoner()
                
                def show_items_ui():
                    if not available_items:
                        self.status_bar.set_message(f"Nessun oggetto disponibile per {selected_gift_type}", "warning")
                        messagebox.showinfo(
                            "Nessun Oggetto",
                            f"Non ci sono oggetti disponibili per il tipo di regalo '{selected_gift_type}'.\n\n"
                            "Prova con un tipo di regalo diverso.",
                            parent=self.root
                        )
                        return
                    
                    self.status_bar.set_message(f"Trovati {len(available_items)} oggetti", "success")
                    show_available_items_optimized(
                        available_items,
                        summoner_id,
                        gift_item_id,
                        message,
                        account_id,
                        self.root
                    )
                
                self.root.after(0, show_items_ui)
                
            except Exception as e:
                def show_error():
                    error_msg = f"Errore nel caricamento: {str(e)}"
                    self.status_bar.set_message(error_msg, "error")
                    messagebox.showerror("Errore", error_msg, parent=self.root)
                
                self.root.after(0, show_error)
        
        threading.Thread(target=fetch_items_async, daemon=True).start()

def create_optimized_gui():
    """Crea e avvia l'applicazione ottimizzata."""
    try:
        root = ttk.Window(themename=THEME)
        
        # Configura l'icona se disponibile
        try:
            root.iconbitmap(default="icon.ico")
        except:
            pass
        
        app = OptimizedGiftApp(root)
        root.mainloop()
        
    except Exception as e:
        messagebox.showerror(
            "Errore Critico",
            f"Si è verificato un errore nell'avvio dell'applicazione:\n\n{str(e)}\n\n"
            "Assicurati che ttkbootstrap sia installato correttamente."
        )

if __name__ == "__main__":
    create_optimized_gui()