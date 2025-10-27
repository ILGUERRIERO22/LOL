import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from tkinter.font import Font
import os
from datetime import datetime
import shutil

class ModernUI:
    """Classe per i colori e stili dell'interfaccia moderna"""
    DARK_BG = "#1a1a2e"
    DARKER_BG = "#16213e"
    ACCENT = "#0f3460"
    SECONDARY_ACCENT = "#e94560"
    TEXT_COLOR = "#f5f5f5"
    SUCCESS = "#00d4aa"
    WARNING = "#ff9f43"
    ERROR = "#ee5a6f"
    INFO = "#54a0ff"
    BUTTON_BG = "#0f3460"
    BUTTON_HOVER = "#1e5f8b"
    INPUT_BG = "#2c3e50"
    HOVER_COLOR = "#34495e"
    TREEVIEW_BG = "#2c3e50"
    TREEVIEW_FG = "#ecf0f1"
    TREEVIEW_SELECT_BG = "#3498db"
    BORDER_COLOR = "#34495e"
    GRADIENT_START = "#0f3460"
    GRADIENT_END = "#16213e"

class AnimatedButton(tk.Button):
    """Pulsante con effetti di animazione"""
    def __init__(self, parent, **kwargs):
        self.default_bg = kwargs.get('bg', ModernUI.BUTTON_BG)
        self.hover_bg = kwargs.get('activebackground', ModernUI.BUTTON_HOVER)
        
        super().__init__(parent, **kwargs)
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)
    
    def on_enter(self, event):
        self.config(bg=self.hover_bg)
        
    def on_leave(self, event):
        self.config(bg=self.default_bg)
        
    def on_click(self, event):
        self.config(relief=tk.SUNKEN)
        
    def on_release(self, event):
        self.config(relief=tk.RAISED)

class PhotoAlbumManager:
    def __init__(self, root):
        self.root = root
        self.setup_fonts()  # Deve essere chiamato prima di setup_window
        self.setup_window()
        self.setup_data()
        self.create_gui()
        self.update_album_list()
        
        # Bind eventi per chiusura pulita
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_window(self):
        """Configura la finestra principale"""
        self.root.title("📸 Gestione Album Fotografici - Versione Pro")
        self.root.geometry("1100x800")
        self.root.configure(bg=ModernUI.DARK_BG)
        self.root.minsize(900, 600)
        
        # Centra la finestra
        self.center_window()
        
        # Configura stile ttk
        self.setup_ttk_style()
        
    def center_window(self):
        """Centra la finestra sullo schermo"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def setup_fonts(self):
        """Configura i font personalizzati"""
        self.title_font = Font(family="Segoe UI", size=18, weight="bold")
        self.header_font = Font(family="Segoe UI", size=13, weight="bold")
        self.normal_font = Font(family="Segoe UI", size=11)
        self.button_font = Font(family="Segoe UI", size=10, weight="bold")
        self.small_font = Font(family="Segoe UI", size=9)
        
    def setup_ttk_style(self):
        """Configura gli stili ttk"""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Stile per Treeview
        style.configure(
            "Custom.Treeview",
            background=ModernUI.TREEVIEW_BG,
            foreground=ModernUI.TREEVIEW_FG,
            fieldbackground=ModernUI.TREEVIEW_BG,
            font=self.normal_font,
            rowheight=35,
            borderwidth=0
        )
        
        style.configure(
            "Custom.Treeview.Heading",
            background=ModernUI.DARKER_BG,
            foreground=ModernUI.TEXT_COLOR,
            font=self.header_font,
            relief="flat",
            borderwidth=1
        )
        
        style.map(
            "Custom.Treeview",
            background=[("selected", ModernUI.TREEVIEW_SELECT_BG)],
            foreground=[("selected", ModernUI.TEXT_COLOR)]
        )
        
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", ModernUI.HOVER_COLOR)]
        )
        
        # Stile per Scrollbar
        style.configure(
            "Custom.Vertical.TScrollbar",
            background=ModernUI.DARKER_BG,
            troughcolor=ModernUI.DARK_BG,
            borderwidth=0,
            arrowcolor=ModernUI.TEXT_COLOR,
            darkcolor=ModernUI.DARKER_BG,
            lightcolor=ModernUI.DARKER_BG
        )
        
    def setup_data(self):
        """Configura i dati e il file di storage"""
        # Usa il percorso specificato dall'utente
        self.data_file = r"C:\Users\dbait\Desktop\MOD LOL\script\json\albums_data.json"
        
        # Assicurati che la directory esista
        data_dir = os.path.dirname(self.data_file)
        try:
            os.makedirs(data_dir, exist_ok=True)
            self.backup_dir = os.path.join(data_dir, "backups")
            os.makedirs(self.backup_dir, exist_ok=True)
        except Exception as e:
            # Se il percorso non è accessibile, usa la directory corrente come fallback
            print(f"Attenzione: impossibile accedere a {data_dir}. Usando directory corrente.")
            self.data_file = "albums_data.json"
            self.backup_dir = "backups"
            os.makedirs(self.backup_dir, exist_ok=True)
        
        # Carica i dati dal file
        self.albums = self.load_data()
        self.ensure_album_fields()
        
        # Inizializza le posizioni correnti con un primo ordinamento
        self.sort_albums()
        
        # Se è il primo caricamento, inizializza last_position uguale a current_position
        for album in self.albums:
            if album.get("last_position", -1) == -1:
                album["last_position"] = album["current_position"]
        
    def ensure_album_fields(self):
        """Assicura che tutti gli album abbiano i campi necessari"""
        for album in self.albums:
            album.setdefault("last_month_photos", album.get("photos", 0))
            album.setdefault("last_position", -1)
            album.setdefault("current_position", -1)
            album.setdefault("rank_change", 0)
            album.setdefault("difference", 0)
            album.setdefault("month_diff", 0)
            album.setdefault("created_date", datetime.now().isoformat())
            album.setdefault("last_updated", datetime.now().isoformat())

    def load_data(self):
        """Carica i dati dal file JSON"""
        try:
            print(f"Tentativo di caricamento da: {self.data_file}")
            
            if os.path.exists(self.data_file):
                print(f"File trovato! Dimensione: {os.path.getsize(self.data_file)} bytes")
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"Dati caricati con successo! Numero album: {len(data)}")
                    return data
            else:
                print(f"File non trovato: {self.data_file}")
                return []
                
        except json.JSONDecodeError as e:
            print(f"Errore JSON: {e}")
            messagebox.showerror(
                "Errore",
                f"Il file JSON ha un formato non valido:\n{str(e)}\n\nVerrà creato un nuovo file."
            )
            return []
        except Exception as e:
            print(f"Errore generico: {e}")
            messagebox.showerror(
                "Errore",
                f"Errore durante il caricamento dei dati:\n{str(e)}\n\nVerrà creato un nuovo file."
            )
            return []

    def save_data(self):
        """Salva i dati nel file JSON con backup automatico"""
        try:
            # Crea backup prima di salvare
            self.create_backup()
            
            # Aggiorna timestamp di ultima modifica
            for album in self.albums:
                album["last_updated"] = datetime.now().isoformat()
            
            # Salva i dati
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.albums, f, indent=4, ensure_ascii=False)
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante il salvataggio: {str(e)}")
            
    def create_backup(self):
        """Crea un backup automatico"""
        try:
            if os.path.exists(self.data_file):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = os.path.join(self.backup_dir, f"albums_backup_{timestamp}.json")
                shutil.copy2(self.data_file, backup_file)
                
                # Mantieni solo gli ultimi 10 backup
                backups = sorted([f for f in os.listdir(self.backup_dir) if f.startswith("albums_backup_")])
                while len(backups) > 10:
                    os.remove(os.path.join(self.backup_dir, backups.pop(0)))
                    
        except Exception as e:
            print(f"Errore durante il backup: {e}")

    def create_gui(self):
        """Crea l'interfaccia grafica principale"""
        # Container principale con gradiente simulato
        main_container = tk.Frame(self.root, bg=ModernUI.DARK_BG)
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header migliorato
        self.create_header(main_container)
        
        # Pannello di controllo
        self.create_control_panel(main_container)
        
        # Area principale con treeview
        self.create_main_area(main_container)
        
        # Status bar migliorata
        self.create_status_bar(main_container)
        
    def create_header(self, parent):
        """Crea l'header con design migliorato"""
        header_frame = tk.Frame(
            parent, 
            bg=ModernUI.DARKER_BG, 
            relief=tk.FLAT,
            bd=2
        )
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Container interno per padding
        header_inner = tk.Frame(header_frame, bg=ModernUI.DARKER_BG)
        header_inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Titolo con icona
        title_frame = tk.Frame(header_inner, bg=ModernUI.DARKER_BG)
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        title_label = tk.Label(
            title_frame,
            text="📸 Gestione Album Fotografici",
            bg=ModernUI.DARKER_BG,
            fg=ModernUI.TEXT_COLOR,
            font=self.title_font
        )
        title_label.pack(anchor=tk.W)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Versione Pro - Gestisci i tuoi album con stile",
            bg=ModernUI.DARKER_BG,
            fg=ModernUI.INFO,
            font=self.small_font
        )
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Info statistiche
        stats_frame = tk.Frame(header_inner, bg=ModernUI.DARKER_BG)
        stats_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stats_label = tk.Label(
            stats_frame,
            text=f"📊 Album: {len(self.albums)}",
            bg=ModernUI.DARKER_BG,
            fg=ModernUI.SUCCESS,
            font=self.normal_font
        )
        self.stats_label.pack(anchor=tk.E)
        
        total_photos = sum(album.get("photos", 0) for album in self.albums)
        self.photos_label = tk.Label(
            stats_frame,
            text=f"📷 Foto totali: {self.format_number(total_photos)}",
            bg=ModernUI.DARKER_BG,
            fg=ModernUI.WARNING,
            font=self.normal_font
        )
        self.photos_label.pack(anchor=tk.E, pady=(5, 0))
        
    def create_control_panel(self, parent):
        """Crea il pannello di controllo migliorato"""
        control_panel = tk.Frame(parent, bg=ModernUI.DARK_BG)
        control_panel.pack(fill=tk.X, pady=(0, 20))
        
        # Frame per ricerca (sinistra)
        search_container = tk.Frame(control_panel, bg=ModernUI.DARK_BG)
        search_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        search_label = tk.Label(
            search_container,
            text="🔍 Cerca Album:",
            bg=ModernUI.DARK_BG,
            fg=ModernUI.TEXT_COLOR,
            font=self.normal_font
        )
        search_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Entry con stile migliorato
        search_frame = tk.Frame(search_container, bg=ModernUI.INPUT_BG, relief=tk.FLAT, bd=2)
        search_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.search_entry = tk.Entry(
            search_frame,
            font=self.normal_font,
            bg=ModernUI.INPUT_BG,
            fg=ModernUI.TEXT_COLOR,
            insertbackground=ModernUI.TEXT_COLOR,
            relief=tk.FLAT,
            bd=0
        )
        self.search_entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        self.search_entry.bind("<KeyRelease>", self.search_album)
        
        # Pulsante per pulire ricerca
        clear_btn = tk.Button(
            search_frame,
            text="✖",
            command=self.clear_search,
            bg=ModernUI.INPUT_BG,
            fg=ModernUI.ERROR,
            font=self.small_font,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Frame per pulsanti azione (destra)
        action_frame = tk.Frame(control_panel, bg=ModernUI.DARK_BG)
        action_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        # Pulsanti con icone
        self.add_btn = self.create_modern_button(
            action_frame, "➕ Aggiungi", self.show_add_form, ModernUI.SUCCESS
        )
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.calc_btn = self.create_modern_button(
            action_frame, "📊 Calcola", self.calculate_and_update, ModernUI.WARNING
        )
        self.calc_btn.pack(side=tk.LEFT, padx=5)
        
        self.export_btn = self.create_modern_button(
            action_frame, "💾 Esporta", self.export_data, ModernUI.INFO
        )
        self.export_btn.pack(side=tk.LEFT, padx=5)
        
    def create_main_area(self, parent):
        """Crea l'area principale con la tabella"""
        main_area = tk.Frame(parent, bg=ModernUI.DARK_BG)
        main_area.pack(fill=tk.BOTH, expand=True)
        
        # Container per treeview
        tree_container = tk.Frame(main_area, bg=ModernUI.DARKER_BG, relief=tk.FLAT, bd=2)
        tree_container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Frame interno per treeview e scrollbar
        tree_frame = tk.Frame(tree_container, bg=ModernUI.TREEVIEW_BG)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Scrollbar personalizzata
        scrollbar = ttk.Scrollbar(tree_frame, style="Custom.Vertical.TScrollbar")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview migliorata
        self.album_list = ttk.Treeview(
            tree_frame,
            columns=("position", "name", "photos", "difference", "month_diff", "rank_change", "updated"),
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=scrollbar.set
        )
        self.album_list.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.album_list.yview)
        
        # Configurazione colonne migliorata
        columns_config = {
            "position": ("🏆 Pos.", 70, tk.CENTER),
            "name": ("📱 Nome Album", 300, tk.W),
            "photos": ("📷 Foto", 120, tk.CENTER),
            "difference": ("📈 Diff.", 100, tk.CENTER),
            "month_diff": ("📅 Mese", 100, tk.CENTER),
            "rank_change": ("↕️ Cambio", 100, tk.CENTER),
            "updated": ("🕐 Aggiornato", 150, tk.CENTER)
        }
        
        for col_id, (heading, width, anchor) in columns_config.items():
            self.album_list.heading(col_id, text=heading)
            self.album_list.column(col_id, width=width, anchor=anchor, minwidth=50)
        
        # Tag per colori migliorati
        self.album_list.tag_configure("increase", foreground=ModernUI.SUCCESS)
        self.album_list.tag_configure("decrease", foreground=ModernUI.ERROR)
        self.album_list.tag_configure("neutral", foreground=ModernUI.TEXT_COLOR)
        self.album_list.tag_configure("new", foreground=ModernUI.INFO)
        
        # Eventi
        self.album_list.bind("<Button-3>", self.show_context_menu)
        self.album_list.bind("<Double-1>", lambda e: self.edit_album())
        self.album_list.bind("<Return>", lambda e: self.edit_album())
        
    def create_status_bar(self, parent):
        """Crea la status bar migliorata"""
        status_container = tk.Frame(parent, bg=ModernUI.DARKER_BG, relief=tk.FLAT, bd=1)
        status_container.pack(fill=tk.X, pady=(20, 0))
        
        status_inner = tk.Frame(status_container, bg=ModernUI.DARKER_BG)
        status_inner.pack(fill=tk.X, padx=15, pady=8)
        
        # Status text (sinistra)
        self.status_label = tk.Label(
            status_inner,
            text="✅ Pronto - Gestisci i tuoi album fotografici",
            bg=ModernUI.DARKER_BG,
            fg=ModernUI.TEXT_COLOR,
            font=self.normal_font,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Info file (destra)
        self.file_info = tk.Label(
            status_inner,
            text=f"📁 {os.path.basename(self.data_file)}",
            bg=ModernUI.DARKER_BG,
            fg=ModernUI.INFO,
            font=self.small_font,
            anchor=tk.E
        )
        self.file_info.pack(side=tk.RIGHT)
        
    def create_modern_button(self, parent, text, command, color=ModernUI.ACCENT):
        """Crea un pulsante moderno con effetti"""
        btn = AnimatedButton(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=ModernUI.TEXT_COLOR,
            font=self.button_font,
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            activebackground=self.darken_color(color),
            activeforeground=ModernUI.TEXT_COLOR,
            bd=0
        )
        return btn
    
    def darken_color(self, color):
        """Scurisce un colore hex per effetti hover"""
        try:
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            darkened = tuple(max(0, int(c * 0.8)) for c in rgb)
            return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        except:
            return ModernUI.BUTTON_HOVER
    
    def clear_search(self):
        """Pulisce il campo di ricerca"""
        self.search_entry.delete(0, tk.END)
        self.update_album_list()
        
    def show_add_form(self):
        """Mostra il form per aggiungere un nuovo album"""
        self.show_album_dialog("Aggiungi Nuovo Album", None)
        
    def show_album_dialog(self, title, album_data=None):
        """Mostra dialog per aggiungere/modificare album"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("500x350")
        dialog.configure(bg=ModernUI.DARK_BG)
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centra il dialog
        self.center_dialog(dialog, 500, 350)
        
        # Container principale
        main_frame = tk.Frame(dialog, bg=ModernUI.DARK_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_frame = tk.Frame(main_frame, bg=ModernUI.DARKER_BG, relief=tk.FLAT, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            header_frame,
            text=f"📝 {title}",
            bg=ModernUI.DARKER_BG,
            fg=ModernUI.TEXT_COLOR,
            font=self.header_font
        )
        title_label.pack(pady=15)
        
        # Form fields
        fields_frame = tk.Frame(main_frame, bg=ModernUI.DARK_BG)
        fields_frame.pack(fill=tk.X, pady=10)
        
        # Nome album
        name_label = tk.Label(
            fields_frame,
            text="📱 Nome Album:",
            bg=ModernUI.DARK_BG,
            fg=ModernUI.TEXT_COLOR,
            font=self.normal_font
        )
        name_label.pack(anchor=tk.W, pady=(0, 5))
        
        name_frame = tk.Frame(fields_frame, bg=ModernUI.INPUT_BG, relief=tk.FLAT, bd=2)
        name_frame.pack(fill=tk.X, pady=(0, 15))
        
        name_entry = tk.Entry(
            name_frame,
            font=self.normal_font,
            bg=ModernUI.INPUT_BG,
            fg=ModernUI.TEXT_COLOR,
            insertbackground=ModernUI.TEXT_COLOR,
            relief=tk.FLAT,
            bd=0
        )
        name_entry.pack(fill=tk.X, padx=10, pady=8)
        
        if album_data:
            name_entry.insert(0, album_data["name"])
            
        # Numero foto
        photos_label = tk.Label(
            fields_frame,
            text="📷 Numero di Foto:",
            bg=ModernUI.DARK_BG,
            fg=ModernUI.TEXT_COLOR,
            font=self.normal_font
        )
        photos_label.pack(anchor=tk.W, pady=(0, 5))
        
        photos_frame = tk.Frame(fields_frame, bg=ModernUI.INPUT_BG, relief=tk.FLAT, bd=2)
        photos_frame.pack(fill=tk.X, pady=(0, 20))
        
        photos_entry = tk.Entry(
            photos_frame,
            font=self.normal_font,
            bg=ModernUI.INPUT_BG,
            fg=ModernUI.TEXT_COLOR,
            insertbackground=ModernUI.TEXT_COLOR,
            relief=tk.FLAT,
            bd=0
        )
        photos_entry.pack(fill=tk.X, padx=10, pady=8)
        
        if album_data:
            photos_entry.insert(0, str(album_data["photos"]))
        else:
            photos_entry.insert(0, "0")
            
        # Pulsanti
        button_frame = tk.Frame(main_frame, bg=ModernUI.DARK_BG)
        button_frame.pack(fill=tk.X, pady=20, side=tk.BOTTOM)
        
        cancel_btn = self.create_modern_button(
            button_frame, "❌ Annulla", dialog.destroy, ModernUI.ERROR
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        save_btn = self.create_modern_button(
            button_frame, 
            "💾 Salva" if not album_data else "✅ Aggiorna",
            lambda: self.save_album_from_dialog(dialog, name_entry, photos_entry, album_data),
            ModernUI.SUCCESS
        )
        save_btn.pack(side=tk.RIGHT)
        
        # Focus e shortcuts
        name_entry.focus_set()
        dialog.bind("<Return>", lambda e: save_btn.invoke())
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        
    def center_dialog(self, dialog, width, height):
        """Centra un dialog rispetto alla finestra principale"""
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_width = self.root.winfo_width()
        root_height = self.root.winfo_height()
        
        x = root_x + (root_width - width) // 2
        y = root_y + (root_height - height) // 2
        
        dialog.geometry(f"{width}x{height}+{x}+{y}")
        
    def save_album_from_dialog(self, dialog, name_entry, photos_entry, album_data):
        """Salva l'album dal dialog"""
        try:
            name = name_entry.get().strip()
            photos_text = photos_entry.get().strip()
            
            if not name:
                messagebox.showerror("Errore", "Il nome dell'album non può essere vuoto!", parent=dialog)
                return
                
            try:
                photos = int(photos_text)
                if photos < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Errore", "Il numero di foto deve essere un numero intero positivo!", parent=dialog)
                return
                
            if album_data:  # Modifica esistente
                original_name = album_data["name"]
                album_data["name"] = name
                album_data["photos"] = photos
                album_data["last_updated"] = datetime.now().isoformat()
                action = "modificato"
            else:  # Nuovo album
                new_album = {
                    "name": name,
                    "photos": photos,
                    "last_month_photos": photos,
                    "last_position": len(self.albums) + 1,
                    "current_position": -1,
                    "rank_change": 0,
                    "difference": 0,
                    "month_diff": 0,
                    "created_date": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat()
                }
                self.albums.append(new_album)
                action = "aggiunto"
                
            self.sort_albums()
            self.save_data()
            self.update_album_list()
            self.update_statistics()
            
            self.update_status(f"✅ Album '{name}' {action} con successo!")
            dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Errore", f"Si è verificato un errore: {str(e)}", parent=dialog)
            
    def edit_album(self):
        """Modifica l'album selezionato"""
        selected_item = self.album_list.selection()
        if not selected_item:
            self.update_status("⚠️ Seleziona un album da modificare", True)
            return
            
        item_index = int(selected_item[0])
        album = self.albums[item_index]
        self.show_album_dialog(f"Modifica Album: {album['name']}", album)
        
    def delete_album(self):
        """Elimina l'album selezionato"""
        selected_item = self.album_list.selection()
        if not selected_item:
            self.update_status("⚠️ Seleziona un album da eliminare", True)
            return
            
        item_index = int(selected_item[0])
        album_name = self.albums[item_index]["name"]
        
        result = messagebox.askyesno(
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare l'album '{album_name}'?\n\nQuesta azione non può essere annullata.",
            icon='warning',
            parent=self.root
        )
        
        if result:
            del self.albums[item_index]
            self.save_data()
            self.sort_albums()
            self.update_album_list()
            self.update_statistics()
            self.update_status(f"🗑️ Album '{album_name}' eliminato con successo")
            
    def show_context_menu(self, event):
        """Mostra menu contestuale migliorato"""
        item = self.album_list.identify_row(event.y)
        if item:
            self.album_list.selection_set(item)
            
            context_menu = tk.Menu(
                self.root,
                tearoff=0,
                bg=ModernUI.DARKER_BG,
                fg=ModernUI.TEXT_COLOR,
                activebackground=ModernUI.HOVER_COLOR,
                activeforeground=ModernUI.TEXT_COLOR,
                font=self.normal_font
            )
            
            context_menu.add_command(
                label="✏️  Modifica", 
                command=self.edit_album
            )
            context_menu.add_command(
                label="📋  Duplica", 
                command=self.duplicate_album
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="🗑️  Elimina", 
                command=self.delete_album
            )
            
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()
                
    def duplicate_album(self):
        """Duplica l'album selezionato"""
        selected_item = self.album_list.selection()
        if not selected_item:
            return
            
        item_index = int(selected_item[0])
        original_album = self.albums[item_index]
        
        # Crea copia
        new_album = original_album.copy()
        new_album["name"] = f"{original_album['name']} - Copia"
        new_album["created_date"] = datetime.now().isoformat()
        new_album["last_updated"] = datetime.now().isoformat()
        
        self.albums.append(new_album)
        self.sort_albums()
        self.save_data()
        self.update_album_list()
        self.update_statistics()
        
        self.update_status(f"📋 Album duplicato: '{new_album['name']}'")
        
    def search_album(self, event):
        """Cerca album con evidenziazione"""
        query = self.search_entry.get().strip().lower()
        
        # Pulisce la lista
        for row in self.album_list.get_children():
            self.album_list.delete(row)
            
        matches = 0
        for original_index, album in enumerate(self.albums):
            if not query or query in album["name"].lower():
                self.insert_album_row(original_index, album)
                matches += 1
                
        # Aggiorna status con risultati ricerca
        if query:
            self.update_status(f"🔍 Trovati {matches} album per '{query}'")
        else:
            self.update_status("✅ Visualizzazione completa ripristinata")
            
    def insert_album_row(self, original_index, album):
        """Inserisce una riga album nella treeview"""
        # Determina tag per colore
        rank_tag = "neutral"
        if album.get("rank_change", 0) > 0:
            rank_tag = "increase"
        elif album.get("rank_change", 0) < 0:
            rank_tag = "decrease"
            
        # Formatta cambio posizione
        rank_change = album.get("rank_change", 0)
        if rank_change > 0:
            rank_display = f"+{rank_change} ↗️"
        elif rank_change < 0:
            rank_display = f"{rank_change} ↘️"
        else:
            rank_display = "0 ➖"
            
        # Formatta data ultimo aggiornamento
        try:
            updated_date = datetime.fromisoformat(album.get("last_updated", datetime.now().isoformat()))
            updated_display = updated_date.strftime("%d/%m %H:%M")
        except:
            updated_display = "N/A"
            
        self.album_list.insert(
            "",
            "end",
            values=(
                original_index + 1,
                album["name"],
                self.format_number(album["photos"]),
                self.format_number(album.get("difference", 0)),
                self.format_number(album.get("month_diff", 0)),
                rank_display,
                updated_display
            ),
            tags=(rank_tag,),
            iid=original_index
        )
        
    def sort_albums(self):
        """Ordina gli album per numero di foto"""
        # Ordina per foto (decrescente)
        self.albums.sort(key=lambda x: x["photos"], reverse=True)
        
        # Aggiorna posizioni correnti
        for index, album in enumerate(self.albums):
            album["current_position"] = index + 1
            
    def calculate_differences(self):
        """Calcola le differenze tra album"""
        for i, album in enumerate(self.albums):
            # Differenza con album precedente
            if i == 0:
                album["difference"] = 0
            else:
                album["difference"] = album["photos"] - self.albums[i - 1]["photos"]
                
            # Differenza dal mese scorso
            album["month_diff"] = album["photos"] - album.get("last_month_photos", album["photos"])
            
            # Cambio di posizione (viene calcolato dopo sort_albums)
            last_pos = album.get("last_position", album.get("current_position", i + 1))
            current_pos = album.get("current_position", i + 1)
            album["rank_change"] = last_pos - current_pos
            
    def format_number(self, number):
        """Formatta i numeri per la visualizzazione con punto come separatore"""
        if isinstance(number, (int, float)):
            # Converti a intero e formatta con punto come separatore delle migliaia
            return f"{int(number):,}".replace(",", ".")
        return str(number)
        
    def calculate_and_update(self):
        """Calcola le differenze e aggiorna la vista"""
        # Riordina gli album in base al numero di foto corrente
        self.sort_albums()
        
        # Calcola le differenze (usa last_position del mese scorso vs current_position nuova)
        self.calculate_differences()
        
        # DOPO aver calcolato le differenze, salva le posizioni attuali per il prossimo mese
        for album in self.albums:
            album["last_month_photos"] = album["photos"]
            album["last_position"] = album["current_position"]
        
        self.save_data()
        self.update_album_list()
        self.update_statistics()
        self.update_status("📊 Calcoli completati e dati aggiornati!")
        
    def update_album_list(self):
        """Aggiorna la lista degli album"""
        # Pulisce la lista
        for row in self.album_list.get_children():
            self.album_list.delete(row)
            
        # Inserisce tutti gli album
        for original_index, album in enumerate(self.albums):
            self.insert_album_row(original_index, album)
            
    def update_statistics(self):
        """Aggiorna le statistiche nell'header"""
        total_albums = len(self.albums)
        total_photos = sum(album.get("photos", 0) for album in self.albums)
        
        self.stats_label.config(text=f"📊 Album: {total_albums}")
        self.photos_label.config(text=f"📷 Foto totali: {self.format_number(total_photos)}")
        
    def update_status(self, message, is_error=False):
        """Aggiorna la status bar"""
        icon = "❌" if is_error else "✅"
        color = ModernUI.ERROR if is_error else ModernUI.TEXT_COLOR
        
        self.status_label.config(
            text=f"{icon} {message}",
            fg=color
        )
        
        # Auto-reset dopo 5 secondi per messaggi di errore
        if is_error:
            self.root.after(5000, lambda: self.update_status("Pronto"))
            
    def export_data(self):
        """Esporta i dati in formato JSON"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Salva dati album",
                initialname=f"album_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.albums, f, indent=4, ensure_ascii=False)
                    
                self.update_status(f"💾 Dati esportati in: {os.path.basename(file_path)}")
                
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'esportazione: {str(e)}")
            self.update_status("❌ Errore durante l'esportazione", True)
            
    def on_closing(self):
        """Gestisce la chiusura dell'applicazione"""
        if messagebox.askokcancel("Uscita", "Vuoi davvero chiudere l'applicazione?"):
            try:
                self.save_data()
            except:
                pass
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoAlbumManager(root)
    root.mainloop()