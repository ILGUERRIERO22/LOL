#!/usr/bin/env python3
"""
Image Converter - Converti immagini in multipli formati
Interfaccia grafica moderna e intuitiva
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import os
from pathlib import Path

class ImageConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖼️ Image Converter Pro")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Colori moderni
        self.bg_color = "#f0f4f8"
        self.primary_color = "#4a90e2"
        self.secondary_color = "#2c3e50"
        self.success_color = "#27ae60"
        self.card_color = "#ffffff"
        
        self.root.configure(bg=self.bg_color)
        
        # Variabili
        self.input_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.selected_format = tk.StringVar(value='PNG')  # Formato selezionato di default
        self.format_list = ['PNG', 'JPEG', 'BMP', 'GIF', 'TIFF', 'WEBP', 'ICO']
        
        self.quality = tk.IntVar(value=95)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg=self.primary_color, height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🖼️ Image Converter Pro",
            font=("Segoe UI", 24, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Container per scrollbar
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas per lo scroll
        canvas = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        
        # Frame scrollabile
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas e scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(30, 0), pady=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 30), pady=20)
        
        # Abilita scroll con mouse wheel
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Main container (ora dentro scrollable_frame)
        main_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Sezione 1: Seleziona immagine
        self.create_section(main_frame, "📁 Seleziona Immagine", 0)
        
        input_frame = tk.Frame(main_frame, bg=self.card_color, relief=tk.FLAT)
        input_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        input_entry = tk.Entry(
            input_frame,
            textvariable=self.input_path,
            font=("Segoe UI", 10),
            width=45,
            relief=tk.FLAT,
            bd=0
        )
        input_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        browse_btn = tk.Button(
            input_frame,
            text="Sfoglia",
            command=self.browse_input,
            bg=self.primary_color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=5
        )
        browse_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Sezione 2: Seleziona formato
        self.create_section(main_frame, "🎯 Seleziona Formato di Destinazione", 2)
        
        formats_frame = tk.Frame(main_frame, bg=self.card_color, relief=tk.FLAT)
        formats_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        
        # Grid per i radio button dei formati
        radiobutton_container = tk.Frame(formats_frame, bg=self.card_color)
        radiobutton_container.pack(padx=20, pady=15)
        
        row, col = 0, 0
        for format_name in self.format_list:
            rb = tk.Radiobutton(
                radiobutton_container,
                text=format_name,
                variable=self.selected_format,
                value=format_name,
                font=("Segoe UI", 11),
                bg=self.card_color,
                activebackground=self.card_color,
                cursor="hand2",
                selectcolor=self.primary_color
            )
            rb.grid(row=row, column=col, sticky="w", padx=15, pady=5)
            col += 1
            if col > 3:
                col = 0
                row += 1
        
        # Sezione 3: Qualità (per JPEG/WEBP)
        self.create_section(main_frame, "⚙️ Qualità (JPEG/WEBP)", 4)
        
        quality_frame = tk.Frame(main_frame, bg=self.card_color, relief=tk.FLAT)
        quality_frame.grid(row=5, column=0, sticky="ew", pady=(0, 15))
        
        quality_container = tk.Frame(quality_frame, bg=self.card_color)
        quality_container.pack(pady=15)
        
        self.quality_label = tk.Label(
            quality_container,
            text=f"Qualità: {self.quality.get()}%",
            font=("Segoe UI", 11, "bold"),
            bg=self.card_color,
            fg=self.secondary_color
        )
        self.quality_label.pack()
        
        quality_slider = ttk.Scale(
            quality_container,
            from_=1,
            to=100,
            variable=self.quality,
            orient=tk.HORIZONTAL,
            length=300,
            command=self.update_quality_label
        )
        quality_slider.pack(pady=10)
        
        # Sezione 4: Cartella output
        self.create_section(main_frame, "📂 Cartella di Destinazione", 6)
        
        output_frame = tk.Frame(main_frame, bg=self.card_color, relief=tk.FLAT)
        output_frame.grid(row=7, column=0, sticky="ew", pady=(0, 15))
        
        output_entry = tk.Entry(
            output_frame,
            textvariable=self.output_folder,
            font=("Segoe UI", 10),
            width=45,
            relief=tk.FLAT,
            bd=0
        )
        output_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        output_btn = tk.Button(
            output_frame,
            text="Sfoglia",
            command=self.browse_output,
            bg=self.primary_color,
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=5
        )
        output_btn.pack(side=tk.RIGHT, padx=10, pady=5)
        
        # Pulsante Converti
        convert_btn = tk.Button(
            main_frame,
            text="🚀 CONVERTI IMMAGINI",
            command=self.convert_images,
            bg=self.success_color,
            fg="white",
            font=("Segoe UI", 14, "bold"),
            relief=tk.FLAT,
            cursor="hand2",
            padx=30,
            pady=15
        )
        convert_btn.grid(row=8, column=0, pady=20)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        
    def create_section(self, parent, title, row):
        label = tk.Label(
            parent,
            text=title,
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_color,
            fg=self.secondary_color,
            anchor="w"
        )
        label.grid(row=row, column=0, sticky="w", pady=(10, 5))
        
    def update_quality_label(self, value):
        self.quality_label.config(text=f"Qualità: {int(float(value))}%")
            
    def browse_input(self):
        filename = filedialog.askopenfilename(
            title="Seleziona un'immagine",
            filetypes=[
                ("Tutti i formati", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp *.ico"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("BMP", "*.bmp"),
                ("GIF", "*.gif"),
                ("TIFF", "*.tiff"),
                ("WEBP", "*.webp"),
                ("ICO", "*.ico")
            ]
        )
        if filename:
            self.input_path.set(filename)
            # Imposta automaticamente la cartella di output
            if not self.output_folder.get():
                self.output_folder.set(os.path.dirname(filename))
                
    def browse_output(self):
        folder = filedialog.askdirectory(title="Seleziona la cartella di destinazione")
        if folder:
            self.output_folder.set(folder)
            
    def convert_images(self):
        # Validazione input
        if not self.input_path.get():
            messagebox.showerror("Errore", "Seleziona un'immagine da convertire!")
            return
            
        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("Errore", "Il file selezionato non esiste!")
            return
            
        format_name = self.selected_format.get()
        if not format_name:
            messagebox.showerror("Errore", "Seleziona un formato di destinazione!")
            return
            
        if not self.output_folder.get():
            messagebox.showerror("Errore", "Seleziona una cartella di destinazione!")
            return
            
        # Crea la cartella di output se non esiste
        os.makedirs(self.output_folder.get(), exist_ok=True)
        
        try:
            # Apri l'immagine
            img = Image.open(self.input_path.get())
            
            # Converti in RGB se necessario (per JPEG)
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img_rgb = background
            else:
                img_rgb = img.convert('RGB')
            
            # Nome base del file
            base_name = Path(self.input_path.get()).stem
            output_dir = self.output_folder.get()
            
            # Determina l'estensione
            ext = format_name.lower()
            if ext == 'jpeg':
                ext = 'jpg'
                
            output_path = os.path.join(output_dir, f"{base_name}.{ext}")
            
            # Converti nel formato selezionato
            if format_name in ['JPEG', 'WEBP']:
                # Usa qualità per JPEG e WEBP
                img_rgb.save(output_path, format=format_name, quality=self.quality.get())
            elif format_name == 'ICO':
                # ICO richiede dimensioni specifiche
                img_ico = img.copy()
                img_ico.thumbnail((256, 256), Image.Resampling.LANCZOS)
                img_ico.save(output_path, format='ICO')
            elif format_name == 'PNG':
                # PNG mantiene la trasparenza
                img.save(output_path, format='PNG')
            else:
                # Altri formati
                if format_name in ['BMP', 'TIFF']:
                    img_rgb.save(output_path, format=format_name)
                else:
                    img.save(output_path, format=format_name)
            
            # Mostra messaggio di successo
            messagebox.showinfo(
                "Successo! ✅",
                f"Immagine convertita con successo in {format_name}!\n\n"
                f"Salvata in:\n{output_path}"
            )
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la conversione:\n{str(e)}")


def main():
    root = tk.Tk()
    app = ImageConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
