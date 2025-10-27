import tkinter as tk
from tkinter import ttk, messagebox

class CalcolatoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("💎 Convertitore RP → EURO")
        self.root.geometry("750x700")  # Finestra più larga per la tabella
        self.root.configure(bg='#1a1a1a')
        
        # Configura lo stile
        self.setup_style()
        
        # Crea il notebook (sistema di tab)
        self.create_notebook()
        
        # Centra la finestra
        self.center_window()
    
    def setup_style(self):
        """Configura lo stile dei widget"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Stile per i frame
        style.configure('Card.TFrame', 
                       background='#2d2d30',
                       relief='flat',
                       borderwidth=1)
        
        style.configure('DarkCard.TFrame', 
                       background='#1e1e1e',
                       relief='flat',
                       borderwidth=1)
        
        # Stile per le label
        style.configure('Title.TLabel',
                       background='#1a1a1a',
                       foreground='#ffffff',
                       font=('Segoe UI', 20, 'bold'))
        
        style.configure('Subtitle.TLabel',
                       background='#2d2d30',
                       foreground='#cccccc',
                       font=('Segoe UI', 10))
        
        style.configure('SubtitleDark.TLabel',
                       background='#1e1e1e',
                       foreground='#cccccc',
                       font=('Segoe UI', 10))
        
        style.configure('Result.TLabel',
                       background='#2d2d30',
                       foreground='#00d4aa',
                       font=('Segoe UI', 13, 'bold'))
        
        style.configure('ResultDiscount.TLabel',
                       background='#2d2d30',
                       foreground='#ff6b6b',
                       font=('Segoe UI', 13, 'bold'))
        
        # Stile per i bottoni
        style.configure('Calculate.TButton',
                       background='#0078d4',
                       foreground='white',
                       font=('Segoe UI', 11, 'bold'),
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 12))
        
        style.map('Calculate.TButton',
                 background=[('active', '#106ebe'),
                           ('pressed', '#005a9e')])
        
        style.configure('Action.TButton',
                       background='#6c5ce7',
                       foreground='white',
                       font=('Segoe UI', 10),
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.map('Action.TButton',
                 background=[('active', '#5f3dc4'),
                           ('pressed', '#4c63d2')])
        
        # Stile per il notebook
        style.configure('TNotebook', 
                       background='#1a1a1a',
                       borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background='#2d2d30',
                       foreground='#cccccc',
                       padding=[20, 12],
                       borderwidth=0)
        style.map('TNotebook.Tab',
                 background=[('selected', '#0078d4')],
                 foreground=[('selected', 'white')])
        
        # Stile per la tabella
        style.configure('Treeview',
                       background='#1e1e1e',
                       foreground='#ffffff',
                       fieldbackground='#1e1e1e',
                       borderwidth=0,
                       font=('Segoe UI', 10))
        
        style.configure('Treeview.Heading',
                       background='#0078d4',
                       foreground='white',
                       font=('Segoe UI', 10, 'bold'),
                       borderwidth=0)
        
        style.map('Treeview.Heading',
                 background=[('active', '#106ebe')])
        
        style.map('Treeview',
                 background=[('selected', '#0078d4')],
                 foreground=[('selected', 'white')])
    
    def create_notebook(self):
        """Crea il notebook con le tab"""
        # Titolo principale
        title_label = ttk.Label(self.root, 
                               text="💎 Convertitore RP → EURO", 
                               style='Title.TLabel')
        title_label.pack(pady=20)
        
        # Crea il notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=25, pady=(0, 25))
        
        # Tab 1: Convertitore RP
        self.create_calculator_tab()
        
        # Tab 2: Convertitore inverso EURO -> RP
        self.create_reverse_calculator_tab()
        
        # Tab 3: Tabella skin e pass
        self.create_table_tab()
    
    def create_calculator_tab(self):
        """Crea la tab del convertitore"""
        calc_frame = ttk.Frame(self.notebook, padding=25)
        calc_frame.configure(style='DarkCard.TFrame')
        self.notebook.add(calc_frame, text='💎 Convertitore RP')
        
        # Frame per input
        input_frame = ttk.Frame(calc_frame, style='Card.TFrame', padding=20)
        input_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(input_frame, 
                 text="💎 Inserisci i RP dell'item (skin, pass, ecc.):", 
                 style='Subtitle.TLabel').pack(anchor='w', pady=(0, 10))
        
        self.importo_var = tk.StringVar()
        self.importo_entry = tk.Entry(input_frame, 
                                     textvariable=self.importo_var,
                                     font=('Segoe UI', 16),
                                     justify='center',
                                     bg='#3c3c3c',
                                     fg='#ffffff',
                                     relief='flat',
                                     bd=0,
                                     insertbackground='#ffffff')
        self.importo_entry.pack(fill='x', pady=10, ipady=12)
        self.importo_entry.bind('<Return>', lambda e: self.calcola())
        self.importo_entry.bind('<KeyRelease>', lambda e: self.calcola_automatico())
        
        # Bottone calcola
        calc_button = ttk.Button(input_frame,
                                text="🚀 CONVERTI IN EURO",
                                command=self.calcola,
                                style='Calculate.TButton')
        calc_button.pack(pady=(15, 0))
        
        # Frame risultati - usa grid per una migliore organizzazione
        results_frame = ttk.Frame(calc_frame)
        results_frame.configure(style='DarkCard.TFrame')
        results_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # Risultati normali (sinistra)
        normal_frame = ttk.Frame(results_frame, style='Card.TFrame', padding=20)
        normal_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        ttk.Label(normal_frame, 
                 text="💶 CONVERSIONI EURO", 
                 style='Title.TLabel',
                 background='#2d2d30',
                 font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 15))
        
        # Risultato 1 (x 0.0040)
        ttk.Label(normal_frame, 
                 text="🏷️ Tariffa Base (×0.0040):", 
                 style='Subtitle.TLabel').pack(anchor='w')
        
        self.result1_var = tk.StringVar(value="€ 0.0000")
        result1_label = ttk.Label(normal_frame, 
                                 textvariable=self.result1_var,
                                 style='Result.TLabel')
        result1_label.pack(anchor='w', pady=(8, 20))
        
        # Risultato 2 (x 0.0060)
        ttk.Label(normal_frame, 
                 text="💰 Prezzo di Vendita (×0.0060):", 
                 style='Subtitle.TLabel').pack(anchor='w')
        
        self.result2_var = tk.StringVar(value="€ 0.0000")
        result2_label = ttk.Label(normal_frame, 
                                 textvariable=self.result2_var,
                                 style='Result.TLabel')
        result2_label.pack(anchor='w', pady=(8, 0))
        
        # Risultati con sconto (destra)
        discount_frame = ttk.Frame(results_frame, style='Card.TFrame', padding=20)
        discount_frame.grid(row=0, column=1, sticky='nsew', padx=(10, 0))
        
        ttk.Label(discount_frame, 
                 text="🔥 PREZZO VENDITA SCONTATO", 
                 style='Title.TLabel',
                 background='#2d2d30',
                 font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 30))
        
        # Solo risultato vendita con sconto
        ttk.Label(discount_frame, 
                 text="💰 Prezzo di Vendita -10%:", 
                 style='Subtitle.TLabel').pack(anchor='w')
        
        self.result2_discount_var = tk.StringVar(value="€ 0.0000")
        result2_discount_label = ttk.Label(discount_frame, 
                                          textvariable=self.result2_discount_var,
                                          style='ResultDiscount.TLabel')
        result2_discount_label.pack(anchor='w', pady=(8, 0))
        
        # Configura il grid per espandere le colonne
        results_frame.columnconfigure(0, weight=1)
        results_frame.columnconfigure(1, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def create_reverse_calculator_tab(self):
        """Crea la tab per il convertitore inverso EURO -> RP"""
        calc_frame = ttk.Frame(self.notebook, padding=20)
        calc_frame.configure(style='DarkCard.TFrame')
        self.notebook.add(calc_frame, text='💶 Convertitore EURO')
        
        # Frame per input
        input_frame = ttk.Frame(calc_frame, style='Card.TFrame', padding=15)
        input_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(input_frame, 
                 text="💶 Inserisci l'importo in EURO:", 
                 style='Subtitle.TLabel').pack(anchor='w', pady=(0, 8))
        
        self.euro_var = tk.StringVar()
        self.euro_entry = tk.Entry(input_frame, 
                                   textvariable=self.euro_var,
                                   font=('Segoe UI', 16),
                                   justify='center',
                                   bg='#3c3c3c',
                                   fg='#ffffff',
                                   relief='flat',
                                   bd=0,
                                   insertbackground='#ffffff')
        self.euro_entry.pack(fill='x', pady=8, ipady=10)
        self.euro_entry.bind('<Return>', lambda e: self.calcola_inverso())
        self.euro_entry.bind('<KeyRelease>', lambda e: self.calcola_inverso_automatico())
        
        # Bottone calcola
        calc_button = ttk.Button(input_frame,
                                text="🚀 CONVERTI IN RP",
                                command=self.calcola_inverso,
                                style='Calculate.TButton')
        calc_button.pack(pady=(10, 0))
        
        # Frame risultati
        results_frame = ttk.Frame(calc_frame)
        results_frame.configure(style='DarkCard.TFrame')
        results_frame.pack(fill='both', expand=True, pady=(15, 0))
        
        # Risultati (centro)
        result_frame = ttk.Frame(results_frame, style='Card.TFrame', padding=15)
        result_frame.pack(fill='both', expand=True)
        
        ttk.Label(result_frame, 
                 text="💎 RP NECESSARI", 
                 style='Title.TLabel',
                 background='#2d2d30',
                 font=('Segoe UI', 13, 'bold')).pack(anchor='w', pady=(0, 10))
        
        # Risultato 1 (÷ 0.0040 - tariffa base)
        ttk.Label(result_frame, 
                 text="🏷️ Da Tariffa Base (÷0.0040):", 
                 style='Subtitle.TLabel').pack(anchor='w')
        
        self.rp_result1_var = tk.StringVar(value="0 RP")
        rp_result1_label = ttk.Label(result_frame, 
                                     textvariable=self.rp_result1_var,
                                     style='Result.TLabel')
        rp_result1_label.pack(anchor='w', pady=(5, 12))
        
        # Risultato 2 (÷ 0.0060 - prezzo vendita)
        ttk.Label(result_frame, 
                 text="💰 Da Prezzo Vendita (÷0.0060):", 
                 style='Subtitle.TLabel').pack(anchor='w')
        
        self.rp_result2_var = tk.StringVar(value="0 RP")
        rp_result2_label = ttk.Label(result_frame, 
                                     textvariable=self.rp_result2_var,
                                     style='Result.TLabel')
        rp_result2_label.pack(anchor='w', pady=(5, 12))
        
        # Risultato 3 (÷ 0.0054 - prezzo vendita con sconto 10%)
        ttk.Label(result_frame, 
                 text="🔥 Da Prezzo Vendita -10% (÷0.0054):", 
                 style='Subtitle.TLabel').pack(anchor='w')
        
        self.rp_result3_var = tk.StringVar(value="0 RP")
        rp_result3_label = ttk.Label(result_frame, 
                                     textvariable=self.rp_result3_var,
                                     style='ResultDiscount.TLabel')
        rp_result3_label.pack(anchor='w', pady=(5, 0))
    
    def calcola_inverso_automatico(self):
        """Calcola automaticamente la conversione inversa mentre si digita"""
        if hasattr(self, 'euro_timer'):
            self.root.after_cancel(self.euro_timer)
        
        self.euro_timer = self.root.after(300, self.calcola_inverso_silenzioso)
    
    def calcola_inverso_silenzioso(self):
        """Calcola la conversione inversa senza mostrare messaggi di errore"""
        try:
            euro_str = self.euro_var.get().replace(',', '.')
            
            if not euro_str.strip():
                self.reset_reverse_results()
                return
            
            euro = float(euro_str)
            
            # Calcola i RP necessari (operazione inversa)
            rp_da_base = euro / 0.0040  # Da tariffa base
            rp_da_vendita = euro / 0.0060  # Da prezzo di vendita
            rp_da_vendita_sconto = euro / 0.0054  # Da prezzo vendita con -10% (0.006 * 0.9 = 0.0054)
            
            # Aggiorna le label
            self.rp_result1_var.set(f"{rp_da_base:.0f} RP")
            self.rp_result2_var.set(f"{rp_da_vendita:.0f} RP")
            self.rp_result3_var.set(f"{rp_da_vendita_sconto:.0f} RP")
            
        except ValueError:
            self.reset_reverse_results()
    
    def calcola_inverso(self):
        """Esegue i calcoli inversi e aggiorna i risultati con validazione"""
        try:
            euro_str = self.euro_var.get().replace(',', '.')
            
            if not euro_str.strip():
                raise ValueError("Inserisci un importo valido")
            
            euro = float(euro_str)
            
            # Calcola i RP necessari (operazione inversa)
            rp_da_base = euro / 0.0040  # Da tariffa base
            rp_da_vendita = euro / 0.0060  # Da prezzo di vendita
            rp_da_vendita_sconto = euro / 0.0054  # Da prezzo vendita con -10%
            
            # Aggiorna le label
            self.rp_result1_var.set(f"{rp_da_base:.0f} RP")
            self.rp_result2_var.set(f"{rp_da_vendita:.0f} RP")
            self.rp_result3_var.set(f"{rp_da_vendita_sconto:.0f} RP")
            
            # Animazione visiva
            self.animate_results()
            
        except ValueError as e:
            messagebox.showerror("❌ Errore", 
                               "Per favore inserisci un numero valido!\n\n"
                               "Esempi: 5.00, 10.50, 15.99")
            self.reset_reverse_results()
    
    def reset_reverse_results(self):
        """Resetta i risultati della conversione inversa"""
        self.rp_result1_var.set("0 RP")
        self.rp_result2_var.set("0 RP")
        self.rp_result3_var.set("0 RP")
    
    def create_table_tab(self):
        """Crea la tab con la tabella dei valori predefiniti"""
        table_frame = ttk.Frame(self.notebook, padding=25)
        table_frame.configure(style='DarkCard.TFrame')
        self.notebook.add(table_frame, text='🎮 Skin & Pass')
        
        # Titolo della tabella
        ttk.Label(table_frame, 
                 text="🎮 Prezzi Skin & Pass", 
                 style='Title.TLabel',
                 background='#1e1e1e').pack(pady=(0, 25))
        
        # Frame per la tabella
        table_container = ttk.Frame(table_frame, style='DarkCard.TFrame', padding=10)
        table_container.pack(fill='both', expand=True)
        
        # Crea il Treeview per la tabella
        columns = ('rp', 'base', 'vendita', 'vendita_sconto')
        self.table = ttk.Treeview(table_container, 
                                 columns=columns, 
                                 show='headings',
                                 height=12)
        
        # Definisci le intestazioni
        self.table.heading('rp', text='💎 RP')
        self.table.heading('base', text='🏷️ Base (×0.004)')
        self.table.heading('vendita', text='💰 Vendita (×0.006)')
        self.table.heading('vendita_sconto', text='💰 Vendita -10%')
        
        # Configura le larghezze delle colonne - ottimizzate per evitare tagli
        self.table.column('rp', width=100, anchor='center', minwidth=80)
        self.table.column('base', width=130, anchor='center', minwidth=110)
        self.table.column('vendita', width=140, anchor='center', minwidth=120)
        self.table.column('vendita_sconto', width=140, anchor='center', minwidth=120)
        
        # Scrollbar per la tabella
        scrollbar = ttk.Scrollbar(table_container, orient='vertical', command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        
        # Posiziona la tabella e scrollbar
        self.table.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Popola la tabella con valori predefiniti
        self.populate_table()
        
        # Aggiungi bottoni per la tabella
        buttons_frame = ttk.Frame(table_frame)
        buttons_frame.configure(style='DarkCard.TFrame')
        buttons_frame.pack(fill='x', pady=(20, 0))
        
        ttk.Button(buttons_frame, 
                  text="🔄 Aggiorna Tabella",
                  command=self.populate_table,
                  style='Action.TButton').pack(side='left', padx=(0, 15))
        
        ttk.Button(buttons_frame, 
                  text="📥 Usa Valore Selezionato",
                  command=self.usa_valore_selezionato,
                  style='Action.TButton').pack(side='left')
    
    def populate_table(self):
        """Popola la tabella con i valori RP di skin e pass"""
        # Pulisci la tabella esistente
        for item in self.table.get_children():
            self.table.delete(item)
        
        # Valori RP tipici per skin e pass
        rp_values = [1350, 1650, 1820, 2650, 3650]
        
        # Inserisci i dati
        for rp in rp_values:
            base = rp * 0.0040
            vendita = rp * 0.0060
            vendita_sconto = vendita * 0.9  # -10%
            
            self.table.insert('', 'end', values=(
                f"{rp} RP",
                f"€ {base:.4f}",
                f"€ {vendita:.4f}",
                f"€ {vendita_sconto:.4f}"
            ))
    
    def usa_valore_selezionato(self):
        """Usa il valore RP selezionato dalla tabella nel convertitore"""
        selection = self.table.selection()
        if not selection:
            messagebox.showwarning("⚠️ Attenzione", "Seleziona prima una riga dalla tabella!")
            return
        
        # Ottieni il valore RP
        item = self.table.item(selection[0])
        rp_str = item['values'][0]  # "1350 RP"
        rp_numero = rp_str.replace(' RP', '')
        
        # Imposta il valore nel convertitore e passa alla tab convertitore
        self.importo_var.set(rp_numero)
        self.notebook.select(0)  # Seleziona la prima tab
        self.calcola()
        
        messagebox.showinfo("✅ Successo", f"Valore {rp_str} impostato nel convertitore!")
    
    def calcola_automatico(self):
        """Calcola automaticamente mentre si digita (con debounce)"""
        # Cancella il timer precedente se esiste
        if hasattr(self, 'timer'):
            self.root.after_cancel(self.timer)
        
        # Imposta un nuovo timer
        self.timer = self.root.after(300, self.calcola_silenzioso)
    
    def calcola_silenzioso(self):
        """Calcola senza mostrare messaggi di errore"""
        try:
            importo_str = self.importo_var.get().replace(',', '.')
            
            if not importo_str.strip():
                self.reset_results()
                return
            
            importo = float(importo_str)
            
            # Calcola i risultati normali
            result1 = importo * 0.0040
            result2 = importo * 0.0060
            
            # Calcola solo il risultato vendita con sconto 10%
            result2_discount = result2 * 0.9
            
            # Aggiorna le label
            self.result1_var.set(f"€ {result1:.4f}")
            self.result2_var.set(f"€ {result2:.4f}")
            self.result2_discount_var.set(f"€ {result2_discount:.4f}")
            
        except ValueError:
            self.reset_results()
    
    def calcola(self):
        """Esegue i calcoli e aggiorna i risultati con validazione"""
        try:
            importo_str = self.importo_var.get().replace(',', '.')
            
            if not importo_str.strip():
                raise ValueError("Inserisci un importo valido")
            
            importo = float(importo_str)
            
            # Calcola i risultati normali
            result1 = importo * 0.0040
            result2 = importo * 0.0060
            
            # Calcola solo il risultato vendita con sconto 10%
            result2_discount = result2 * 0.9
            
            # Aggiorna le label
            self.result1_var.set(f"€ {result1:.4f}")
            self.result2_var.set(f"€ {result2:.4f}")
            self.result2_discount_var.set(f"€ {result2_discount:.4f}")
            
            # Animazione visiva
            self.animate_results()
            
        except ValueError as e:
            messagebox.showerror("❌ Errore", 
                               "Per favore inserisci un numero valido!\n\n"
                               "Esempi: 1350, 1650, 1820")
            self.reset_results()
    
    def animate_results(self):
        """Piccola animazione per i risultati"""
        style = ttk.Style()
        # Cambia colore temporaneamente
        style.configure('Result.TLabel', foreground='#ffd700')
        style.configure('ResultDiscount.TLabel', foreground='#ffd700')
        
        # Ripristina i colori dopo 400ms
        self.root.after(400, lambda: [
            style.configure('Result.TLabel', foreground='#00d4aa'),
            style.configure('ResultDiscount.TLabel', foreground='#ff6b6b')
        ])
    
    def reset_results(self):
        """Resetta i risultati"""
        self.result1_var.set("€ 0.0000")
        self.result2_var.set("€ 0.0000")
        self.result2_discount_var.set("€ 0.0000")
    
    def center_window(self):
        """Centra la finestra sullo schermo"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        pos_x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

def main():
    """Funzione principale"""
    root = tk.Tk()
    app = CalcolatoreGUI(root)
    
    try:
        root.iconbitmap()
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()