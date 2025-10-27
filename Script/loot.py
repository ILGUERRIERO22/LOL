import os
import requests
import json
import base64
import tkinter as tk
from tkinter import ttk, messagebox, font
from PIL import Image, ImageTk
import urllib3
import threading
import webbrowser
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ModernLoLInventoryViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("League of Legends - Inventory Viewer Pro")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        self.root.configure(bg="#0A1428")
        
        # Modern color palette
        self.colors = {
            'primary_bg': '#0A1428',
            'secondary_bg': '#1E2328', 
            'tertiary_bg': '#282D32',
            'accent': '#C8AA6E',  # LoL Gold
            'accent_hover': '#F0E6D2',
            'success': '#00C851',
            'error': '#FF4444',
            'warning': '#FF8800',
            'text_primary': '#F0E6D2',
            'text_secondary': '#A09B8C',
            'border': '#3C3C41',
            'hover': '#5BC0DE'
        }
        
        # Configure the modern theme
        self.configure_styles()
        
        # Main container with gradient effect
        self.main_container = tk.Frame(root, bg=self.colors['primary_bg'])
        self.main_container.pack(fill="both", expand=True)
        
        # Create header with modern design
        self.create_modern_header()
        
        # Main content area
        self.content_area = tk.Frame(self.main_container, bg=self.colors['primary_bg'])
        self.content_area.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create modern status bar
        self.create_modern_status_bar()
        
        # Initialize data
        self.inventory_data = []
        self.filtered_data = []
        self.sort_column = "Nome"
        self.sort_reverse = False
        self.connection_active = False
        
        # Create UI components
        self.create_modern_filters()
        self.create_enhanced_treeview()
        self.create_action_panel()
        
        # Auto-connect with loading animation
        self.root.after(500, self.init_connection)

    def configure_styles(self):
        """Configure modern ttk styles with LoL theme"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure modern button style
        self.style.configure("Modern.TButton",
                          background=self.colors['tertiary_bg'],
                          foreground=self.colors['text_primary'],
                          font=('Segoe UI', 10, 'bold'),
                          borderwidth=0,
                          focuscolor='none',
                          padding=(15, 8))
        
        self.style.map("Modern.TButton",
                    background=[('active', self.colors['accent']), 
                              ('pressed', self.colors['accent_hover'])],
                    foreground=[('active', self.colors['primary_bg']),
                              ('pressed', self.colors['primary_bg'])])
        
        # Accent button style
        self.style.configure("Accent.TButton",
                          background=self.colors['accent'],
                          foreground=self.colors['primary_bg'],
                          font=('Segoe UI', 10, 'bold'),
                          borderwidth=0,
                          focuscolor='none',
                          padding=(15, 8))
        
        # Modern Entry style
        self.style.configure("Modern.TEntry",
                          fieldbackground=self.colors['secondary_bg'],
                          background=self.colors['secondary_bg'],
                          foreground=self.colors['text_primary'],
                          borderwidth=1,
                          insertcolor=self.colors['accent'],
                          font=('Segoe UI', 10))
        
        # Modern Combobox style
        self.style.configure("Modern.TCombobox",
                          fieldbackground=self.colors['secondary_bg'],
                          background=self.colors['secondary_bg'],
                          foreground=self.colors['text_primary'],
                          borderwidth=1,
                          arrowcolor=self.colors['accent'],
                          font=('Segoe UI', 10))
        
        # Enhanced Treeview style
        self.style.configure("Modern.Treeview",
                          background=self.colors['secondary_bg'],
                          foreground=self.colors['text_primary'],
                          fieldbackground=self.colors['secondary_bg'],
                          borderwidth=0,
                          rowheight=30,
                          font=('Segoe UI', 9))
        
        self.style.configure("Modern.Treeview.Heading",
                          background=self.colors['tertiary_bg'],
                          foreground=self.colors['accent'],
                          font=('Segoe UI', 10, 'bold'),
                          borderwidth=1,
                          relief='flat')
        
        # Modern Scrollbar
        self.style.configure("Modern.Vertical.TScrollbar",
                          background=self.colors['tertiary_bg'],
                          troughcolor=self.colors['secondary_bg'],
                          arrowcolor=self.colors['accent'],
                          borderwidth=0)

    def create_modern_header(self):
        """Create a modern header with LoL styling"""
        header_frame = tk.Frame(self.main_container, bg=self.colors['secondary_bg'], height=80)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Left side - Logo and title
        left_frame = tk.Frame(header_frame, bg=self.colors['secondary_bg'])
        left_frame.pack(side=tk.LEFT, fill="y", padx=20)
        
        title_font = font.Font(family="Segoe UI", size=20, weight="bold")
        title = tk.Label(left_frame, text="⚔️ LoL Inventory Pro", font=title_font, 
                        bg=self.colors['secondary_bg'], fg=self.colors['accent'])
        title.pack(side=tk.LEFT, pady=20)
        
        version_label = tk.Label(left_frame, text="v2.0", font=('Segoe UI', 8), 
                               bg=self.colors['secondary_bg'], fg=self.colors['text_secondary'])
        version_label.pack(side=tk.LEFT, padx=(10, 0), pady=25)
        
        # Right side - Connection status with modern indicator
        right_frame = tk.Frame(header_frame, bg=self.colors['secondary_bg'])
        right_frame.pack(side=tk.RIGHT, fill="y", padx=20)
        
        # Connection indicator
        self.connection_frame = tk.Frame(right_frame, bg=self.colors['secondary_bg'])
        self.connection_frame.pack(side=tk.RIGHT, pady=20)
        
        self.status_dot = tk.Label(self.connection_frame, text="●", font=('Segoe UI', 16),
                                 bg=self.colors['secondary_bg'], fg=self.colors['error'])
        self.status_dot.pack(side=tk.LEFT, padx=(0, 5))
        
        self.connection_label = tk.Label(self.connection_frame, text="Disconnesso", 
                                       font=('Segoe UI', 11, 'bold'),
                                       bg=self.colors['secondary_bg'], fg=self.colors['text_primary'])
        self.connection_label.pack(side=tk.LEFT)

    def create_modern_filters(self):
        """Create modern filter controls with better spacing and design"""
        filters_frame = tk.Frame(self.content_area, bg=self.colors['primary_bg'])
        filters_frame.pack(fill="x", pady=(0, 15))
        
        # Search section
        search_section = tk.Frame(filters_frame, bg=self.colors['primary_bg'])
        search_section.pack(side=tk.LEFT, fill="x", expand=True)
        
        search_label = tk.Label(search_section, text="🔍 Cerca:", font=('Segoe UI', 10, 'bold'),
                              bg=self.colors['primary_bg'], fg=self.colors['text_primary'])
        search_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_section, textvariable=self.search_var, 
                                    width=25, style="Modern.TEntry")
        self.search_entry.pack(side=tk.LEFT, padx=(0, 20))
        self.search_var.trace("w", lambda *args: self.filter_data())
        
        # Type filter
        type_label = tk.Label(search_section, text="📦 Tipo:", font=('Segoe UI', 10, 'bold'),
                            bg=self.colors['primary_bg'], fg=self.colors['text_primary'])
        type_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.type_var = tk.StringVar()
        self.type_combobox = ttk.Combobox(search_section, textvariable=self.type_var, 
                                        width=18, state="readonly", style="Modern.TCombobox")
        self.type_combobox.pack(side=tk.LEFT, padx=(0, 20))
        self.type_var.trace("w", lambda *args: self.filter_data())
        
        # Rarity filter
        rarity_label = tk.Label(search_section, text="💎 Rarità:", font=('Segoe UI', 10, 'bold'),
                              bg=self.colors['primary_bg'], fg=self.colors['text_primary'])
        rarity_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.rarity_var = tk.StringVar()
        self.rarity_combobox = ttk.Combobox(search_section, textvariable=self.rarity_var, 
                                          width=15, state="readonly", style="Modern.TCombobox")
        self.rarity_combobox.pack(side=tk.LEFT, padx=(0, 20))
        self.rarity_var.trace("w", lambda *args: self.filter_data())
        
        # Reset button
        reset_btn = ttk.Button(search_section, text="🔄 Reset", command=self.reset_filters, 
                              style="Modern.TButton")
        reset_btn.pack(side=tk.RIGHT)

    def create_enhanced_treeview(self):
        """Create an enhanced treeview with better styling"""
        tree_container = tk.Frame(self.content_area, bg=self.colors['primary_bg'])
        tree_container.pack(fill="both", expand=True, pady=(0, 15))
        
        # Info bar above treeview
        info_bar = tk.Frame(tree_container, bg=self.colors['secondary_bg'], height=35)
        info_bar.pack(fill="x", pady=(0, 2))
        info_bar.pack_propagate(False)
        
        self.total_items_label = tk.Label(info_bar, text="📊 Totale oggetti: 0", 
                                        font=('Segoe UI', 10, 'bold'),
                                        bg=self.colors['secondary_bg'], fg=self.colors['text_primary'])
        self.total_items_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        self.value_label = tk.Label(info_bar, text="💰 Valore totale: 0 BE", 
                                  font=('Segoe UI', 10),
                                  bg=self.colors['secondary_bg'], fg=self.colors['accent'])
        self.value_label.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Treeview frame
        tree_frame = tk.Frame(tree_container, bg=self.colors['primary_bg'])
        tree_frame.pack(fill="both", expand=True)
        
        # Column configuration (fixed encoding issues)
        columns = ("Nome", "Prezzo Upgrade", "Prezzo Disincanto", "Quantità", "Tipo", "Rarità")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", 
                               style="Modern.Treeview")
        
        # Configure columns with better widths
        column_config = {
            "Nome": 200,
            "Prezzo Upgrade": 120, 
            "Prezzo Disincanto": 130,
            "Quantità": 80,
            "Tipo": 120,
            "Rarità": 100
        }
        
        for col in columns:
            self.tree.heading(col, text=col, anchor=tk.W,
                           command=lambda c=col: self.sort_treeview(c))
            self.tree.column(col, width=column_config[col], anchor=tk.W, minwidth=80)
        
        # Enhanced row styling
        self.tree.tag_configure('common', background='#2D3748', foreground='#E2E8F0')
        self.tree.tag_configure('rare', background='#2D5A87', foreground='#87CEEB')
        self.tree.tag_configure('epic', background='#6B46C1', foreground='#DDD6FE')
        self.tree.tag_configure('legendary', background='#B45309', foreground='#FED7AA')
        self.tree.tag_configure('mythic', background='#DC2626', foreground='#FECACA')
        self.tree.tag_configure('selected', background=self.colors['accent'], 
                              foreground=self.colors['primary_bg'])
        
        # Modern scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview,
                                style="Modern.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<ButtonRelease-1>", self.on_item_select)
        self.tree.bind("<Motion>", self.on_tree_hover)

    def create_action_panel(self):
        """Create modern action panel with enhanced buttons"""
        action_frame = tk.Frame(self.content_area, bg=self.colors['secondary_bg'], height=60)
        action_frame.pack(fill="x", pady=(5, 0))
        action_frame.pack_propagate(False)
        
        # Left side - Statistics
        stats_frame = tk.Frame(action_frame, bg=self.colors['secondary_bg'])
        stats_frame.pack(side=tk.LEFT, fill="y", padx=15)
        
        self.last_update_label = tk.Label(stats_frame, text="🕒 Mai aggiornato", 
                                        font=('Segoe UI', 9),
                                        bg=self.colors['secondary_bg'], fg=self.colors['text_secondary'])
        self.last_update_label.pack(pady=20)
        
        # Right side - Action buttons
        button_frame = tk.Frame(action_frame, bg=self.colors['secondary_bg'])
        button_frame.pack(side=tk.RIGHT, fill="y", padx=15, pady=10)
        
        self.refresh_btn = ttk.Button(button_frame, text="🔄 Aggiorna", 
                                    command=self.refresh_data, style="Accent.TButton")
        self.refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        export_btn = ttk.Button(button_frame, text="📤 Esporta", 
                               command=self.export_data, style="Modern.TButton")
        export_btn.pack(side=tk.RIGHT, padx=5)

    def create_modern_status_bar(self):
        """Create modern status bar"""
        self.status_frame = tk.Frame(self.main_container, bg=self.colors['tertiary_bg'], height=25)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_frame, text="Pronto per la connessione", 
                                   font=('Segoe UI', 9), bg=self.colors['tertiary_bg'], 
                                   fg=self.colors['text_secondary'], anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=10, pady=3)

    def get_lcu_info(self):
        """Enhanced LCU connection with better error handling"""
        try:
            potential_paths = [
                r"C:\Riot Games\League of Legends\lockfile",
                os.path.expanduser("~/Riot Games/League of Legends/lockfile"),
                os.path.expanduser("~/Games/League of Legends/lockfile"),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Riot Games/League of Legends/lockfile')
            ]
            
            for path in potential_paths:
                if os.path.exists(path):
                    with open(path, "r", encoding='utf-8') as f:
                        lockfile = f.read().strip().split(":")
                        if len(lockfile) >= 4:
                            return lockfile[0], lockfile[2], lockfile[3]
            
            return None, None, None
            
        except Exception as e:
            self.update_status(f"Errore accesso lockfile: {str(e)}", "error")
            return None, None, None

    def get_inventory(self, lcu_port, lcu_token):
        """Enhanced inventory fetching with timeout and retry"""
        try:
            auth_value = base64.b64encode(f"riot:{lcu_token}".encode()).decode()
            url = f'https://127.0.0.1:{lcu_port}/lol-loot/v1/player-loot'
            headers = {'Authorization': f'Basic {auth_value}'}
            
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.update_status(f"Errore API: {response.status_code}", "error")
                return None
                
        except requests.exceptions.RequestException as e:
            self.update_status(f"Errore connessione: {str(e)}", "error")
            return None

    def init_connection(self):
        """Initialize connection with loading animation"""
        self.animate_loading()
        self.connect_to_client()

    def animate_loading(self):
        """Simple loading animation for connection status"""
        dots = ["", ".", "..", "..."]
        
        def animate(count=0):
            if not self.connection_active and count < 20:
                dot = dots[count % len(dots)]
                self.connection_label.config(text=f"Connessione in corso{dot}")
                self.root.after(200, lambda: animate(count + 1))
            elif not self.connection_active:
                self.connection_label.config(text="Timeout connessione")
                self.status_dot.config(fg=self.colors['error'])
        
        animate()

    def connect_to_client(self):
        """Enhanced connection method with better feedback"""
        def worker():
            try:
                self.update_status("🔄 Ricerca client League of Legends...", "info")
                
                lcu_user, lcu_port, lcu_token = self.get_lcu_info()
                
                if lcu_port and lcu_token:
                    self.update_status("🔗 Connessione al client...", "info")
                    inventory_data = self.get_inventory(lcu_port, lcu_token)
                    
                    if inventory_data:
                        self.process_inventory_data(inventory_data)
                        self.root.after(0, self.update_ui_success)
                    else:
                        self.root.after(0, self.update_ui_failure)
                else:
                    self.root.after(0, lambda: self.update_status(
                        "❌ Client non trovato. Assicurati che League of Legends sia avviato.", "error"))
                    self.root.after(0, self.update_ui_failure)
                    
            except Exception as e:
                self.root.after(0, lambda: self.update_status(f"❌ Errore: {str(e)}", "error"))
                self.root.after(0, self.update_ui_failure)
        
        threading.Thread(target=worker, daemon=True).start()

    def process_inventory_data(self, inventory_data):
        """Enhanced data processing with better item categorization"""
        self.inventory_data = []
        
        # Special items translation
        special_items = {
            "MATERIAL_key_fragment": "Frammento di Chiave",
            "CURRENCY_cosmetic": "Essenza Arancione", 
            "CURRENCY_champion": "Essenza Blu",
            "MATERIAL_key": "Chiave Esadecimale",
            "MATERIAL_clashtickets": "Biglietto Scontro",
            "CURRENCY_rp": "Riot Points",
            "MATERIAL_mastery_token": "Token Maestria"
        }
        
        for item in inventory_data:
            name = item.get("localizedName", "") or item.get("itemDesc", "Oggetto Sconosciuto")
            loot_name = item.get("lootName", "")
            
            if loot_name in special_items:
                name = special_items[loot_name]
            
            # Enhanced rarity mapping
            rarity = item.get("rarity", "COMMON").upper()
            rarity_map = {
                "DEFAULT": "Comune",
                "COMMON": "Comune", 
                "RARE": "Rara",
                "EPIC": "Epica",
                "LEGENDARY": "Leggendaria",
                "MYTHIC": "Mitica",
                "ULTIMATE": "Suprema"
            }
            
            processed_item = {
                "localizedName": name,
                "itemDesc": item.get("itemDesc", "N/A"),
                "upgradeEssenceValue": item.get("upgradeEssenceValue", 0),
                "disenchantValue": item.get("disenchantValue", 0),
                "count": item.get("count", 0),
                "type": item.get("type", "N/A"),
                "rarity": rarity_map.get(rarity, rarity.title()),
                "lootName": loot_name,
                "rawRarity": rarity
            }
            
            self.inventory_data.append(processed_item)

    def update_ui_success(self):
        """Update UI after successful connection"""
        self.connection_active = True
        self.status_dot.config(fg=self.colors['success'])
        self.connection_label.config(text="Connesso")
        
        # Update filters
        types = sorted(list(set(item["type"] for item in self.inventory_data)))
        rarities = sorted(list(set(item["rarity"] for item in self.inventory_data)))
        
        self.type_combobox['values'] = ["Tutti"] + types
        self.rarity_combobox['values'] = ["Tutte"] + rarities
        
        if not self.type_var.get():
            self.type_var.set("Tutti")
        if not self.rarity_var.get():
            self.rarity_var.set("Tutte")
        
        self.filter_data()
        
        # Update timestamp
        now = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.config(text=f"🕒 Ultimo aggiornamento: {now}")
        
        self.update_status(f"✅ Caricati {len(self.inventory_data)} oggetti dall'inventario", "success")

    def update_ui_failure(self):
        """Update UI after failed connection"""
        self.connection_active = False
        self.status_dot.config(fg=self.colors['error'])
        self.connection_label.config(text="Disconnesso")

    def filter_data(self):
        """Enhanced filtering with value calculation"""
        search_term = self.search_var.get().lower()
        selected_type = self.type_var.get()
        selected_rarity = self.rarity_var.get()
        
        self.filtered_data = self.inventory_data.copy()
        
        if search_term:
            self.filtered_data = [item for item in self.filtered_data 
                                if search_term in item["localizedName"].lower()]
        
        if selected_type and selected_type != "Tutti":
            self.filtered_data = [item for item in self.filtered_data 
                                if item["type"] == selected_type]
        
        if selected_rarity and selected_rarity != "Tutte":
            self.filtered_data = [item for item in self.filtered_data 
                                if item["rarity"] == selected_rarity]
        
        self.sort_data()
        self.update_treeview()
        
        # Calculate total value
        total_disenchant = sum(item["disenchantValue"] * item["count"] 
                             for item in self.filtered_data)
        
        self.total_items_label.config(text=f"📊 Oggetti mostrati: {len(self.filtered_data)}")
        self.value_label.config(text=f"💰 Valore disincanto: {total_disenchant:,} BE")

    def sort_data(self):
        """Enhanced sorting with proper type handling"""
        column_map = {
            "Nome": "localizedName",
            "Prezzo Upgrade": "upgradeEssenceValue", 
            "Prezzo Disincanto": "disenchantValue",
            "Quantità": "count",
            "Tipo": "type",
            "Rarità": "rarity"
        }
        
        key = column_map.get(self.sort_column, "localizedName")
        
        if key in ("upgradeEssenceValue", "disenchantValue", "count"):
            self.filtered_data.sort(
                key=lambda x: int(x[key]) if isinstance(x[key], (int, float, str)) and str(x[key]).isdigit() else 0,
                reverse=self.sort_reverse
            )
        else:
            self.filtered_data.sort(
                key=lambda x: str(x[key]).lower(),
                reverse=self.sort_reverse
            )

    def update_treeview(self):
        """Enhanced treeview update with rarity-based styling"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for i, item in enumerate(self.filtered_data):
            values = (
                item["localizedName"],
                f"{item['upgradeEssenceValue']:,}" if item['upgradeEssenceValue'] > 0 else "-",
                f"{item['disenchantValue']:,}" if item['disenchantValue'] > 0 else "-", 
                f"{item['count']:,}",
                item["type"],
                item["rarity"]
            )
            
            # Choose tag based on rarity
            rarity_tags = {
                "COMMON": "common",
                "RARE": "rare", 
                "EPIC": "epic",
                "LEGENDARY": "legendary",
                "MYTHIC": "mythic"
            }
            tag = rarity_tags.get(item["rawRarity"], "common")
            
            self.tree.insert("", "end", values=values, tags=(tag,))

    def sort_treeview(self, column):
        """Enhanced sorting with visual indicators"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Update headers with sort indicators
        for col in self.tree["columns"]:
            if col == column:
                indicator = " ↓" if self.sort_reverse else " ↑"
                self.tree.heading(col, text=col + indicator)
            else:
                self.tree.heading(col, text=col)
        
        self.sort_data()
        self.update_treeview()

    def reset_filters(self):
        """Reset all filters"""
        self.search_var.set("")
        self.type_var.set("Tutti")
        self.rarity_var.set("Tutte")

    def refresh_data(self):
        """Refresh inventory data"""
        self.refresh_btn.config(state="disabled")
        self.connect_to_client()
        self.root.after(2000, lambda: self.refresh_btn.config(state="normal"))

    def export_data(self):
        """Export inventory data to JSON"""
        if not self.filtered_data:
            messagebox.showwarning("Avviso", "Nessun dato da esportare!")
            return
        
        try:
            filename = f"lol_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.filtered_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Successo", f"Dati esportati in {filename}")
            self.update_status(f"📤 Esportati {len(self.filtered_data)} oggetti", "success")
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esportazione: {str(e)}")

    def on_item_select(self, event):
        """Handle item selection"""
        selected_items = self.tree.selection()
        if selected_items:
            item_id = selected_items[0]
            item_index = self.tree.index(item_id)
            if item_index < len(self.filtered_data):
                item = self.filtered_data[item_index]
                self.update_status(f"🔍 {item['localizedName']} - {item['type']} ({item['rarity']})", "info")

    def on_item_double_click(self, event):
        """Handle item double-click"""
        selected_items = self.tree.selection()
        if selected_items:
            item_id = selected_items[0]
            item_index = self.tree.index(item_id)
            if item_index < len(self.filtered_data):
                item = self.filtered_data[item_index]
                self.show_item_details(item)

    def on_tree_hover(self, event):
        """Handle tree hover for visual feedback"""
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            self.tree.configure(cursor="hand2")
        else:
            self.tree.configure(cursor="")

    def show_item_details(self, item):
        """Show enhanced item details dialog"""
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Dettagli: {item['localizedName']}")
        details_window.geometry("500x400")
        details_window.configure(bg=self.colors['primary_bg'])
        details_window.transient(self.root)
        details_window.grab_set()
        
        # Header
        header_frame = tk.Frame(details_window, bg=self.colors['secondary_bg'], height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text=item['localizedName'], 
                             font=('Segoe UI', 16, 'bold'),
                             bg=self.colors['secondary_bg'], fg=self.colors['accent'])
        title_label.pack(pady=15)
        
        # Content
        content_frame = tk.Frame(details_window, bg=self.colors['primary_bg'])
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        details = [
            ("🏷️ Tipo", item['type']),
            ("💎 Rarità", item['rarity']),
            ("📦 Quantità", f"{item['count']:,}"),
            ("⬆️ Prezzo Upgrade", f"{item['upgradeEssenceValue']:,} BE" if item['upgradeEssenceValue'] > 0 else "Non disponibile"),
            ("⬇️ Prezzo Disincanto", f"{item['disenchantValue']:,} BE" if item['disenchantValue'] > 0 else "Non disponibile"),
            ("🔧 ID Oggetto", item['lootName']),
            ("💰 Valore Totale", f"{item['disenchantValue'] * item['count']:,} BE")
        ]
        
        for i, (label, value) in enumerate(details):
            detail_frame = tk.Frame(content_frame, bg=self.colors['primary_bg'])
            detail_frame.pack(fill="x", pady=8)
            
            label_widget = tk.Label(detail_frame, text=label, width=20, anchor="w",
                                  font=('Segoe UI', 11, 'bold'),
                                  bg=self.colors['primary_bg'], fg=self.colors['text_secondary'])
            label_widget.pack(side=tk.LEFT)
            
            value_widget = tk.Label(detail_frame, text=str(value), anchor="w",
                                  font=('Segoe UI', 11),
                                  bg=self.colors['primary_bg'], fg=self.colors['text_primary'])
            value_widget.pack(side=tk.LEFT, fill="x", expand=True)
        
        # Close button
        close_btn = ttk.Button(content_frame, text="Chiudi", command=details_window.destroy, 
                              style="Accent.TButton")
        close_btn.pack(pady=(20, 0))

    def update_status(self, message, status_type="info"):
        """Enhanced status updates with colors and icons"""
        icons = {
            "info": "ℹ️",
            "success": "✅", 
            "error": "❌",
            "warning": "⚠️"
        }
        
        colors = {
            "info": self.colors['text_secondary'],
            "success": self.colors['success'],
            "error": self.colors['error'], 
            "warning": self.colors['warning']
        }
        
        icon = icons.get(status_type, "ℹ️")
        color = colors.get(status_type, self.colors['text_secondary'])
        
        self.status_label.config(text=f"{icon} {message}", fg=color)
        print(f"[{status_type.upper()}] {message}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernLoLInventoryViewer(root)
    root.mainloop()