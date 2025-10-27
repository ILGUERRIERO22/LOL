import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import datetime
from datetime import datetime, timedelta
from Riot_API import get_friendlist, apply_recent_tag  # Importa funzioni API

# Palette colori migliorata - Tema League of Legends
COLORS = {
    'bg_dark': '#0F2027',        # Blu scuro profondo
    'bg_medium': '#1A252F',      # Blu medio
    'bg_light': '#2C5364',       # Blu più chiaro per contrasto
    'accent_gold': '#C89B3C',    # Oro League of Legends
    'accent_blue': '#1E2328',    # Blu scuro per accenti
    'text_primary': '#F0E6D2',   # Crema chiaro
    'text_secondary': '#A09B8C', # Grigio chiaro
    'success': '#0AC8B9',        # Turchese
    'warning': '#E84057',        # Rosso
    'pending': '#E7B45A',        # Arancione
    'recent': '#463714',         # Oro scuro per evidenziare
    'hover': '#3C5364'           # Blu per effetti hover
}

class ModernFriendListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LoL Friend Tracker Pro")
        self.root.geometry("900x700")
        self.root.configure(bg=COLORS['bg_dark'])
        self.root.resizable(True, True)
        
        # Variabili di controllo
        self.search_var = tk.StringVar()
        self.showing_recent_friends = False
        self.full_friend_list = []
        self.countdown = 10
        self.timer_job = None
        
        # Configurazione stili avanzata
        self.setup_advanced_styles()
        
        # Creazione interfaccia moderna
        self.create_modern_interface()
        
        # Avvio iniziale
        self.display_friend_list()
        
        # Binding eventi
        self.setup_event_bindings()
    
    def setup_advanced_styles(self):
        """Configurazione stili avanzata per un look moderno"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Stile tabella principale
        style.configure("Modern.Treeview",
                       background=COLORS['bg_medium'],
                       foreground=COLORS['text_primary'],
                       rowheight=35,
                       fieldbackground=COLORS['bg_medium'],
                       borderwidth=0,
                       font=("Segoe UI", 10))
        
        style.map("Modern.Treeview",
                 background=[('selected', COLORS['accent_gold']),
                            ('focus', COLORS['hover'])],
                 foreground=[('selected', COLORS['bg_dark'])])
        
        # Stile intestazioni tabella
        style.configure("Modern.Treeview.Heading",
                       background=COLORS['bg_dark'],
                       foreground=COLORS['accent_gold'],
                       font=("Segoe UI", 11, "bold"),
                       relief="flat",
                       borderwidth=1)
        
        style.map("Modern.Treeview.Heading",
                 background=[('active', COLORS['bg_light'])])
        
        # Pulsanti moderni
        style.configure("Gold.TButton",
                       font=("Segoe UI", 10, "bold"),
                       background=COLORS['accent_gold'],
                       foreground=COLORS['bg_dark'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 8))
        
        style.map("Gold.TButton",
                 background=[('active', '#D4AF47'),
                            ('pressed', '#B8941F')])
        
        style.configure("Teal.TButton",
                       font=("Segoe UI", 10, "bold"),
                       background=COLORS['success'],
                       foreground=COLORS['bg_dark'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 8))
        
        style.map("Teal.TButton",
                 background=[('active', '#0BDDCE'),
                            ('pressed', '#089B93')])
        
        # Scrollbar moderna
        style.configure("Modern.Vertical.TScrollbar",
                       background=COLORS['bg_medium'],
                       troughcolor=COLORS['bg_dark'],
                       borderwidth=0,
                       arrowcolor=COLORS['accent_gold'],
                       darkcolor=COLORS['bg_medium'],
                       lightcolor=COLORS['bg_medium'])
    
    def create_modern_interface(self):
        """Creazione interfaccia moderna e responsiva"""
        # Container principale con gradient simulato
        main_container = tk.Frame(self.root, bg=COLORS['bg_dark'])
        main_container.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header con design migliorato
        self.create_header(main_container)
        
        # Barra di controllo moderna
        self.create_control_bar(main_container)
        
        # Area stato con design migliorato
        self.create_status_area(main_container)
        
        # Tabella principale con stile moderno
        self.create_modern_table(main_container)
        
        # Footer informativo
        self.create_footer(main_container)
    
    def create_header(self, parent):
        """Crea header con design moderno"""
        header_frame = tk.Frame(parent, bg=COLORS['bg_dark'], height=100)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Container per logo e titolo
        content_frame = tk.Frame(header_frame, bg=COLORS['bg_dark'])
        content_frame.pack(expand=True, fill="both")
        
        # Logo placeholder elegante
        logo_frame = tk.Frame(content_frame, bg=COLORS['bg_dark'])
        logo_frame.pack(side="left", padx=(10, 20), pady=10)
        
        placeholder = tk.Frame(logo_frame, bg=COLORS['accent_gold'], width=70, height=70)
        placeholder.pack()
        placeholder.pack_propagate(False)
        logo_text = tk.Label(placeholder, text="LoL", font=("Segoe UI", 18, "bold"),
                           bg=COLORS['accent_gold'], fg=COLORS['bg_dark'])
        logo_text.place(relx=0.5, rely=0.5, anchor="center")
        
        # Area titolo migliorata
        title_frame = tk.Frame(content_frame, bg=COLORS['bg_dark'])
        title_frame.pack(side="left", fill="y", pady=10)
        
        title_label = tk.Label(title_frame,
                             text="FRIEND TRACKER PRO",
                             font=("Segoe UI", 28, "bold"),
                             fg=COLORS['accent_gold'],
                             bg=COLORS['bg_dark'])
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(title_frame,
                                text="League of Legends • Gestione Amici Avanzata",
                                font=("Segoe UI", 12),
                                fg=COLORS['text_secondary'],
                                bg=COLORS['bg_dark'])
        subtitle_label.pack(anchor="w", pady=(5, 0))
        
        # Linea decorativa
        separator = tk.Frame(header_frame, bg=COLORS['accent_gold'], height=2)
        separator.pack(fill="x", side="bottom")
    
    def create_control_bar(self, parent):
        """Crea barra di controllo moderna"""
        control_frame = tk.Frame(parent, bg=COLORS['bg_medium'], relief="flat", bd=1)
        control_frame.pack(fill="x", pady=(0, 15), ipady=15)
        
        # Area ricerca migliorata
        search_container = tk.Frame(control_frame, bg=COLORS['bg_medium'])
        search_container.pack(side="left", padx=20)
        
        search_label = tk.Label(search_container,
                              text="🔍 Cerca Riot ID:",
                              font=("Segoe UI", 11, "bold"),
                              fg=COLORS['text_primary'],
                              bg=COLORS['bg_medium'])
        search_label.pack(side="left", padx=(0, 10))
        
        # Entry moderna per ricerca
        self.search_entry = tk.Entry(search_container,
                                   textvariable=self.search_var,
                                   font=("Segoe UI", 11),
                                   width=30,
                                   bg=COLORS['bg_dark'],
                                   fg=COLORS['text_primary'],
                                   insertbackground=COLORS['accent_gold'],
                                   relief="flat",
                                   bd=5,
                                   highlightbackground=COLORS['accent_gold'],
                                   highlightcolor=COLORS['accent_gold'],
                                   highlightthickness=1)
        self.search_entry.pack(side="left", padx=5)
        
        # Pulsanti di controllo
        button_container = tk.Frame(control_frame, bg=COLORS['bg_medium'])
        button_container.pack(side="right", padx=20)
        
        self.recent_button = ttk.Button(button_container,
                                      text="👥 Amici Recenti",
                                      style="Teal.TButton",
                                      command=self.toggle_friend_list_view)
        self.recent_button.pack(side="left", padx=5)
        
        refresh_button = ttk.Button(button_container,
                                  text="🔄 Aggiorna",
                                  style="Gold.TButton",
                                  command=self.refresh_data)
        refresh_button.pack(side="left", padx=5)
        
        export_button = ttk.Button(button_container,
                                 text="📊 Esporta CSV",
                                 style="Gold.TButton",
                                 command=self.export_to_csv)
        export_button.pack(side="left", padx=5)
    
    def create_status_area(self, parent):
        """Crea area stato moderna"""
        self.status_frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        self.status_frame.pack(fill="x", pady=(0, 10))
        
        self.status_label = tk.Label(self.status_frame,
                                   text="🔄 Inizializzazione in corso...",
                                   font=("Segoe UI", 10),
                                   fg=COLORS['text_primary'],
                                   bg=COLORS['bg_dark'],
                                   anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True)
        
        self.timer_label = tk.Label(self.status_frame,
                                  text="",
                                  font=("Segoe UI", 10, "bold"),
                                  fg=COLORS['accent_gold'],
                                  bg=COLORS['bg_dark'])
        self.timer_label.pack(side="right")
    
    def create_modern_table(self, parent):
        """Crea tabella moderna con scrollbar"""
        table_container = tk.Frame(parent, bg=COLORS['bg_dark'])
        table_container.pack(fill="both", expand=True, pady=10)
        
        # Frame per tabella e scrollbar
        table_frame = tk.Frame(table_container, bg=COLORS['bg_dark'])
        table_frame.pack(fill="both", expand=True)
        
        # Scrollbar moderna
        scrollbar = ttk.Scrollbar(table_frame, style="Modern.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y", padx=(5, 0))
        
        # Tabella principale
        columns = ("riot_id", "friends_since", "seven_days_status")
        self.tree = ttk.Treeview(table_frame,
                               columns=columns,
                               show="headings",
                               style="Modern.Treeview",
                               yscrollcommand=scrollbar.set)
        
        # Configurazione colonne migliorate
        self.tree.heading("riot_id", text="🎮 RIOT ID", anchor="center")
        self.tree.heading("friends_since", text="📅 AMICI DA", anchor="center")
        self.tree.heading("seven_days_status", text="⏳ STATO 7 GIORNI", anchor="center")
        
        self.tree.column("riot_id", width=300, anchor="center", minwidth=200)
        self.tree.column("friends_since", width=250, anchor="center", minwidth=200)
        self.tree.column("seven_days_status", width=200, anchor="center", minwidth=150)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.tree.yview)
        
        # Configurazione tag per colorazione
        self.tree.tag_configure("recent", background=COLORS['recent'], foreground=COLORS['text_primary'])
        self.tree.tag_configure("pending", foreground=COLORS['pending'])
        self.tree.tag_configure("completed", foreground=COLORS['success'])
        self.tree.tag_configure("error", foreground=COLORS['warning'])
    
    def create_footer(self, parent):
        """Crea footer informativo"""
        footer_frame = tk.Frame(parent, bg=COLORS['bg_dark'])
        footer_frame.pack(fill="x", pady=(15, 0))
        
        # Linea decorativa
        separator = tk.Frame(footer_frame, bg=COLORS['accent_gold'], height=1)
        separator.pack(fill="x", pady=(0, 10))
        
        info_label = tk.Label(footer_frame,
                            text="🔄 Aggiornamento automatico ogni 10 secondi • 📊 Esportazione CSV disponibile",
                            font=("Segoe UI", 9),
                            fg=COLORS['text_secondary'],
                            bg=COLORS['bg_dark'])
        info_label.pack(side="left")
        
        version_label = tk.Label(footer_frame,
                               text="v2.0 Pro",
                               font=("Segoe UI", 9, "bold"),
                               fg=COLORS['accent_gold'],
                               bg=COLORS['bg_dark'])
        version_label.pack(side="right")
    
    def setup_event_bindings(self):
        """Configura eventi e binding"""
        # Ricerca in tempo reale
        self.search_var.trace('w', lambda name, index, mode: self.apply_search_filter())
        
        # Binding per chiusura pulita
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def display_friend_list(self):
        """Recupera e visualizza la lista amici con gestione errori migliorata"""
        self.update_status("🔄 Aggiornamento in corso...", COLORS['text_primary'])
        
        try:
            friends = get_friendlist()
            if friends:
                self.full_friend_list = apply_recent_tag(friends, datetime.now())
                self.apply_search_filter()
                
                total_friends = len(self.full_friend_list)
                recent_friends = sum(1 for f in self.full_friend_list if f.get('added_recently', False))
                
                self.update_status(
                    f"✅ Lista aggiornata: {total_friends} amici totali ({recent_friends} recenti)",
                    COLORS['success']
                )
            else:
                self.update_status("⚠️ Nessun dato ricevuto dall'API Riot", COLORS['warning'])
        except Exception as e:
            self.update_status(f"❌ Errore connessione: {str(e)}", COLORS['warning'])
        
        # Avvia countdown timer
        self.start_countdown_timer()
        
        # Pianifica prossimo aggiornamento
        self.root.after(10000, self.display_friend_list)
    
    def start_countdown_timer(self):
        """Avvia timer con countdown visuale"""
        self.countdown = 10
        self.update_countdown()
    
    def update_countdown(self):
        """Aggiorna countdown con cancellazione sicura"""
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        
        if self.countdown > 0:
            self.timer_label.config(text=f"⏱️ Prossimo aggiornamento: {self.countdown}s")
            self.countdown -= 1
            self.timer_job = self.root.after(1000, self.update_countdown)
        else:
            self.timer_label.config(text="🔄 Aggiornamento...")
    
    def apply_search_filter(self):
        """Filtra lista con ricerca migliorata"""
        query = self.search_var.get().lower().strip()
        
        if self.showing_recent_friends:
            filtered_friends = [
                friend for friend in self.full_friend_list
                if query in friend.get('nick', '').lower() and friend.get('added_recently', False)
            ]
        else:
            filtered_friends = [
                friend for friend in self.full_friend_list
                if query in friend.get('nick', '').lower()
            ]
        
        self.update_table(filtered_friends)
        
        # Aggiorna status ricerca
        if query:
            self.update_status(f"🔍 {len(filtered_friends)} risultati per '{query}'", COLORS['text_primary'])
    
    def toggle_friend_list_view(self):
        """Alterna visualizzazione con feedback migliorato"""
        if self.showing_recent_friends:
            self.showing_recent_friends = False
            self.recent_button.config(text="👥 Amici Recenti")
            self.apply_search_filter()
            self.update_status("👥 Visualizzazione completa attiva", COLORS['text_primary'])
        else:
            self.showing_recent_friends = True
            self.recent_button.config(text="📋 Mostra Tutti")
            self.apply_search_filter()
            
            recent_count = sum(1 for friend in self.full_friend_list if friend.get('added_recently', False))
            self.update_status(f"⭐ Filtro attivo: {recent_count} amici recenti", COLORS['success'])
    
    def update_table(self, data):
        """Aggiorna tabella con dati formattati"""
        # Pulisce tabella
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for friend in data:
            name = friend.get('nick', 'Sconosciuto')
            friends_since = friend.get('friendsSince', 'Sconosciuto')
            
            # Parsing data con formati multipli
            parsed_date = self.parse_date(friends_since)
            
            if parsed_date:
                days_passed = (datetime.now() - parsed_date).days
                
                if days_passed < 7:
                    target_date = parsed_date + timedelta(days=7)
                    seven_days_status = f"⏳ {target_date.strftime('%d/%m/%Y alle %H:%M')}"
                    tag = "pending"
                else:
                    seven_days_status = "✅ Completato"
                    tag = "completed"
                    
                # Formatta data di amicizia
                formatted_date = parsed_date.strftime('%d/%m/%Y alle %H:%M')
            else:
                seven_days_status = "❌ Data non valida"
                formatted_date = friends_since
                tag = "error"
            
            # Inserisce nella tabella
            item_id = self.tree.insert("", "end", 
                                     values=(name, formatted_date, seven_days_status))
            
            # Applica tag colore
            if friend.get('added_recently', False):
                self.tree.item(item_id, tags=("recent",))
            else:
                self.tree.item(item_id, tags=(tag,))
    
    def parse_date(self, date_string):
        """Parsing data con formati multipli"""
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y"
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        return None
    
    def export_to_csv(self):
        """Esportazione CSV migliorata"""
        if not self.tree.get_children():
            messagebox.showwarning("Nessun Dato", "Non ci sono dati da esportare!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("File CSV", "*.csv"), ("Tutti i file", "*.*")],
            title="Salva esportazione CSV",
            initialfile=f"friendlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Intestazioni
                writer.writerow(["Riot ID", "Amici da", "Stato 7 Giorni"])
                
                # Dati
                for item_id in self.tree.get_children():
                    values = self.tree.item(item_id, "values")
                    writer.writerow(values)
            
            self.update_status(f"📊 Esportazione completata: {file_path}", COLORS['success'])
            messagebox.showinfo("Successo", f"Esportazione completata!\n\nFile salvato in:\n{file_path}")
            
        except Exception as e:
            self.update_status(f"❌ Errore esportazione: {e}", COLORS['warning'])
            messagebox.showerror("Errore", f"Errore durante l'esportazione:\n{str(e)}")
    
    def refresh_data(self):
        """Aggiornamento manuale immediato"""
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.display_friend_list()
    
    def update_status(self, message, color):
        """Aggiorna status con colore"""
        self.status_label.config(text=message, fg=color)
    
    def on_closing(self):
        """Gestione chiusura pulita"""
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.root.destroy()

# Avvio applicazione
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernFriendListApp(root)
    root.mainloop()