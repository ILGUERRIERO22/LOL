import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import subprocess
import re
from PIL import Image, ImageTk
from io import BytesIO
import base64
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


# Icone in base64 (esempi di icone semplici)
VIDEO_ICON = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAH5SURBVFiF7Za/S1tRFMc/N79eQoODRaFDC4VODh0cLIGCi4OT4FCog/9BCh0c3AodHDoUugQKHTp0EAeXQLGTgy6FQlMaUaOJMbm5r8P7PYzG9+JLbMHvdO893HM+5577gEKhI5KyExFxgUEROVTVaKOG1pGQAo+AD8A+sNuJgFmgAJSBH8Bv4A3Q266BCaAM/AKqwBHw9q5Nvzctm+q1Vs3R9uYAsXZCROYBRORbkzD3jmv5FHBF9EBENoDPwDZwAjwFvgLrIjLbFxGqGnY6nYiqqrXDNE0jSZL0I8s0QqrqxnGcqapaluXFcaw/s6yra0FVO4PB4JGfq+qpqk5ks+12ezGKIsuPwzA87UdEPQQrKytunucLfn/RaDTiwWAw7Pv+5/F4PFxdXXXvs5Db8OLdW9+vVJbn5udtKeXpwcFBLs/zhUajEW9tbXn3FbG8vLxULBZn8jyP0jRdGx0dvahUKql5v1AoFG8uVVUzmUxWwjAsBUGQ9xrbJiCKIjsIAr9UKo1nWZZlWVZvbm72O9yd4prdWq02ked5tLGx8SmOY+uu81oFiMh3YA5gcXHRds2dVL+o3QMH+u2CcM3eiMgU8LDZpz8BW8Bt3+kmM5vCbQCvgWfAYwBTNPZSxL3hSsCRqp7fMN8HDo3nhULrXALRTfGhM0u9xAAAAABJRU5ErkJggg==
"""

AUDIO_ICON = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAHSSURBVFiF7ZY/aBNxFMc/uWsuXUJDl4AQCEih4NKpdHAQHKQgDg4O/lkEF0Fwd3ER3AQHB0EodBAcpIMOLgUHhxYcWrRQaLGUGppc7i6XczkH6R1tlF7qYL4w8H7v+973fd/3fuAf/xixWuOJiZp99gyYBCbMcKEVDlvCBTAP5MxwD6AKYGYLwBAwWlOPQCBwgQ/AO+Aj8L0VAfYBg9VqdQp4CfxsZLw5OHg4UC7PAJjZy1YIqANJoABUWrAbj9sxq/GJqjTjOOVOLuEYcAF8qwlwgT3gJ7AxdPNm+cHnz5fvbW8P5QqFVoCzYEJE1uv2iogsBQKB9Wq12l+pVJYikYg3tzwvmc1mO9MnJ2PAC+BuXad7ZvYEeBwOh5f6+vpWjo+PF+fm5oKpVKrr7OzsbjwePxD4Q3ZFRLqBCRHZuqzdMcPNZLLjMBic9vv9k5lMZmJ7ezuVyWQaJm1DASJyE5gWkaGLrJlNicggMDk7OxsIh8ML4XB4PJ/Pz66treWbcXpV8A2gICI9AKOjo5M+n++eGc4NDw+PJBKJgeHh4YYje2XwCysWi/X29PRkem/fHj84OHhcLBZfNePwOgWIGU4kEjkNxmKxvvz+/qnP5wvVC/kP/NV8A2iMhWkUdQ4ZAAAAAElFTkSuQmCC
"""

CONVERT_ICON = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAJ1SURBVFiF7ZW9a1NRGMZ/7/HmJtWmpRaqKCLiB7SgUKnYoYMfg4v/gFMXJwcRdHMRxKWgk3+Ag5NOTg6CDiJOWhCFiq1WEGxaa9LYJDf35J4OeUtuTXubtEnB4jNduOe8z/M+58ADGTJkyPBfw0l7ot/vI6I452YXYwZVFUTkvdZ6m4isqeqtiDdQ1XJpmMQY8zXOT4KIlIO9NN2zikhRVe+JyGkROdnpdO4EXL9Ae+RygojUsizLqaqVy+XT7Xb7GHDaH4kKMQmMMUZEauVy+Uy9Xv+8srLSqFQqp3zDNQlCgvX19b1LS0snOp3O2UqlcrdarZ6LMnwLZIw5m8vlbohI1RhTUVW01h3gCRDbe865XWYnm81mLZ/PF1X1RLvdPua6bg3YD9wHPs3iXURcVV0GXgNvgY+qeisi8BI4OIu4b+KOLwAeAHeAJVXdPyKQ5Hc3EIhUQK2127Ozs42FhYWXwGvn3I1arXY0n8+/CK4n+SQRFU9cgVarlQcOqepuVd3TbDZzQNEYU5vXp6omrhb4w2cGRgRUdcB/1nXdL8aYxUDcOec8z5ub+Lj80ikW4YlBEAXOAeR5XlFrXVbVfKjJWmvvL8JXVX0EfExqMAacA+p9TQ4Ds8uLyDegEbdOiC1xCkSOCeC6btEYUwCMXzKbAf8x8ERrfReYqoCI/AQeAC+AL3Gx4hQYIyoiZREpqepAVbsR4h3gPdAEXgXnrLUrwONpRKcdwVCwF9ivqvuCuFrrflSMMbHPzIqkCvSMMY1er9eDUYuFENEHWw3HCmR8i4VYAj9E5IGq3lLVpYjC/Ci1CbYi/tspYv8SZMiQIcMW4jf5rrjDZiJKWAAAAABJRU5ErkJggg==
"""

MERGE_ICON = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAOxAAADsQBlSsOGwAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAI3SURBVFiF7ZbPS1RRFMc/577nzDiTEy0aNGgWEUG0qF1Bi1ZtonatIvoPahH9B+5aFO2iRbQSXLWJIKJFtWlRUEGrNiUxE2rNOOO8d08L33vOmxnHmaaBwS8M791zz/2e8+493wcKFChQoMD/DJnFsNvtNp1OZyUQUdWLwIK11jjnNlX1k4i8ttY+abfbm5MmiJQqzWZzMQzDG8aYa8aYFWttFUBVW8aYdVV9Wq/XV4Mg6InIfaPRqJZKpTsi8hA4OjZBu90OO53O3TAMbwVBcKxSqZxy1XLlbBzHx621K1EUXQFu9vv9u61Wq+OLlEqlh8aYNSDsdrsPnHM/gcdAaTxHqVQ6EQTBbWvttTiOT1er1WUXVStnrbXGGFM2xpzpdDrvnXNvRWQDOMgePtvtdl+VSqXPURRdiuP4euCLj4+Xy+Vz5XL5gohc9rGx4CKy7JzbaDQar51za5VK5ZAxZsmvCZ/rfWzGbr9njNlQVSqVyjVV/QzUx+33vxaXgKNAWVVPjpt3rbXOWtt0znkROR4EwdnJBKpaF5EVEQlnQVUDY4zzRfz1jwg45zZFZM0551R1S0ROisjBXQhcCMPwmKoumCnw/xRxHH9T1Rc+tygiB0TkyBQCw1qt9jWO4y3gN9MY4zwkl4AHQNUY84+J7wa+b3WBdWAPu9iJ/EuoSxzPzwHww1r7Q1XXvBABh/1z5OMQeAbsA94Ab/aiaOa/4SRUtV6tVhftbhcXKFCgQIECufEHlk64twuI8fEAAAAASUVORK5CYII=
"""




# Imposta manualmente il percorso di FFmpeg se necessario
FFMPEG_PATH = r"C:\ffmpeg\bin\ffmpeg.exe"

class ModernVideoToAudioConverter:
    def __init__(self, root):
        self.root = root
        root.title("Convertitore Video-Audio")
        root.geometry("700x600")
        root.resizable(True, True)
        root.configure(bg="#f0f0f0")
        
        # Aggiungiamo colori moderni
        self.colors = {
            "bg": "#f0f0f0",
            "primary": "#3498db",
            "secondary": "#2ecc71",
            "text": "#2c3e50",
            "accent": "#9b59b6",
            "warning": "#e74c3c",
            "light": "#ecf0f1",
            "dark": "#34495e"
        }
        
        # Verifica che FFmpeg sia disponibile
        if not os.path.exists(FFMPEG_PATH):
            messagebox.showerror("Errore", "FFmpeg non trovato! Assicurati che il percorso sia corretto.")
            exit()
        
        # Controlla se FFmpeg è accessibile nel PATH di sistema
        os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_PATH)
        
        # Variabili
        self.video_path_var = tk.StringVar()
        self.audio_path_var = tk.StringVar()
        self.format_var = tk.StringVar(value="mp3")
        self.quality_var = tk.StringVar(value="192k")
        
        # Creazione delle icone
        self.video_icon = self.create_icon_from_base64(VIDEO_ICON)
        self.audio_icon = self.create_icon_from_base64(AUDIO_ICON)
        self.convert_icon = self.create_icon_from_base64(CONVERT_ICON)
        self.merge_icon = self.create_icon_from_base64(MERGE_ICON)
        
        self.setup_styles()
        self.create_widgets()
        
    def create_icon_from_base64(self, base64_string):
        from PIL import ImageFile
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        try:
            image_data = base64.b64decode(base64_string)
            image = Image.open(BytesIO(image_data)).convert("RGBA")
            return ImageTk.PhotoImage(image)
        except Exception as e:
            print(f"Errore nel caricamento dell'icona: {e}")
            return None

    
    def setup_styles(self):
        # Configurazione stili ttk
        style = ttk.Style()
        style.theme_use("clam")
        
        # Frame
        style.configure("TFrame", background=self.colors["bg"])
        
        # Label
        style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["text"], font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground=self.colors["primary"])
        style.configure("Status.TLabel", font=("Segoe UI", 9, "italic"), foreground=self.colors["accent"])
        
        # Button
        style.configure("TButton", background=self.colors["primary"], foreground="white", 
                        font=("Segoe UI", 10, "bold"), padding=8)
        style.map("TButton", 
                background=[("pressed", self.colors["dark"]), ("active", "#2980b9")],
                foreground=[("pressed", "white"), ("active", "white")])
        
        # Primary button
        style.configure("Primary.TButton", background=self.colors["primary"])
        style.map("Primary.TButton", 
                background=[("pressed", "#2980b9"), ("active", "#2980b9")])
        
        # Secondary button
        style.configure("Secondary.TButton", background=self.colors["secondary"])
        style.map("Secondary.TButton", 
                background=[("pressed", "#27ae60"), ("active", "#27ae60")])
                
        # Entry
        style.configure("TEntry", foreground=self.colors["text"], font=("Segoe UI", 10))
        
        # Combobox
        style.configure("TCombobox", foreground=self.colors["text"], font=("Segoe UI", 10))
        
        # Progressbar
        style.configure("TProgressbar", troughcolor=self.colors["light"], 
                        background=self.colors["secondary"], thickness=15)
                        
        # Notebook e tabs
        style.configure("TNotebook", background=self.colors["bg"], tabmargins=[2, 5, 2, 0])
        style.configure("TNotebook.Tab", background=self.colors["light"], foreground=self.colors["text"],
                        font=("Segoe UI", 10), padding=[15, 4], focuscolor=self.colors["primary"])
        style.map("TNotebook.Tab", 
                background=[("selected", self.colors["primary"]), ("active", "#2980b9")],
                foreground=[("selected", "white"), ("active", self.colors["dark"])])
                
    def create_widgets(self):
        # Notebook per tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab di conversione
        self.conversion_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.conversion_tab, text="Converti Video in Audio")
        self.setup_conversion_tab()
        
        # Tab di unione
        self.merge_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.merge_tab, text="Unisci File Audio")
        self.setup_merge_tab()
        
        # Barra di stato
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.status_label = ttk.Label(self.status_frame, text="Pronto", style="Status.TLabel")
        self.status_label.pack(side="left", padx=5)
        
    def setup_conversion_tab(self):
        main_frame = ttk.Frame(self.conversion_tab, padding=20)
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(header_frame, image=self.video_icon).pack(side="left", padx=5)
        ttk.Label(header_frame, text="Convertitore Video-Audio", style="Header.TLabel").pack(side="left", padx=5)
        
        # Input video
        video_frame = ttk.Frame(main_frame)
        video_frame.pack(fill="x", pady=5)
        
        ttk.Label(video_frame, text="File video:").pack(side="left", padx=5)
        ttk.Entry(video_frame, textvariable=self.video_path_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(video_frame, text="Sfoglia", command=self.select_video_file).pack(side="left", padx=5)
        
        # Formato audio
        format_frame = ttk.Frame(main_frame)
        format_frame.pack(fill="x", pady=5)
        
        ttk.Label(format_frame, text="Formato audio:").pack(side="left", padx=5)
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, 
                                    values=["mp3", "wav", "ogg", "aac", "flac"], 
                                    state="readonly", width=15)
        format_combo.pack(side="left", padx=5)
        
        # Qualità audio
        ttk.Label(format_frame, text="Qualità:").pack(side="left", padx=(15, 5))
        quality_combo = ttk.Combobox(format_frame, textvariable=self.quality_var, 
                                    values=["64k", "128k", "192k", "256k", "320k"], 
                                    state="readonly", width=10)
        quality_combo.pack(side="left", padx=5)
        
        # Output audio
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill="x", pady=5)
        
        ttk.Label(output_frame, text="Salva audio:").pack(side="left", padx=5)
        ttk.Entry(output_frame, textvariable=self.audio_path_var, width=50).pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(output_frame, text="Sfoglia", command=self.save_audio_file).pack(side="left", padx=5)
        
        # Progress frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill="x", pady=20)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", 
                                          length=400, mode="determinate", style="TProgressbar")
        self.progress_bar.pack(fill="x", padx=5, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="0%", anchor="center")
        self.progress_label.pack(pady=5)
        
        # Pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)
        
        convert_button = ttk.Button(button_frame, text="Converti", style="Primary.TButton",
                                  command=lambda: threading.Thread(target=self.convert_video_to_audio, daemon=True).start())
        convert_button.pack(padx=5, pady=5, fill="x")
        
    def setup_merge_tab(self):
        merge_frame = ttk.Frame(self.merge_tab, padding=20)
        merge_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = ttk.Frame(merge_frame)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(header_frame, image=self.merge_icon).pack(side="left", padx=5)
        ttk.Label(header_frame, text="Unisci File Audio", style="Header.TLabel").pack(side="left", padx=5)
        
        # Descrizione
        ttk.Label(merge_frame, text="Seleziona più file audio da unire in un unico file.").pack(pady=10)
        
        # Lista file
        files_frame = ttk.Frame(merge_frame)
        files_frame.pack(fill="both", expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(files_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.files_listbox = tk.Listbox(files_frame, height=10, bg="white", fg=self.colors["text"],
                                      font=("Segoe UI", 10), bd=1, relief="solid")
        self.files_listbox.pack(side="left", fill="both", expand=True)
        
        self.files_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.files_listbox.yview)
        
        # Pulsanti per la gestione dei file
        list_buttons_frame = ttk.Frame(merge_frame)
        list_buttons_frame.pack(fill="x", pady=10)
        
        ttk.Button(list_buttons_frame, text="Aggiungi Files", 
                 command=self.add_audio_files).pack(side="left", padx=5)
                 
        ttk.Button(list_buttons_frame, text="Rimuovi Selezionato", 
                 command=self.remove_selected_file).pack(side="left", padx=5)
                 
        ttk.Button(list_buttons_frame, text="Svuota Lista", 
                 command=self.clear_files_list).pack(side="left", padx=5)
        
        # Pulsante unisci
        merge_button = ttk.Button(merge_frame, text="Unisci File", style="Secondary.TButton",
                                command=self.merge_audio_files)
        merge_button.pack(pady=10, fill="x")
        
        # Lista per memorizzare i percorsi dei file
        self.audio_files = []
        
    def select_video_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleziona un file video",
            filetypes=[
                ("Video", "*.mp4 *.mkv *.avi *.mov *.flv *.webm *.wmv"),
                ("Tutti i file", "*.*")
            ]
        )
        if file_path:
            self.video_path_var.set(file_path)
            # Suggerisce automaticamente un nome per il file di output
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            output_path = os.path.join(os.path.dirname(file_path), f"{base_name}.{self.format_var.get()}")
            self.audio_path_var.set(output_path)
            
    def save_audio_file(self):
        selected_format = self.format_var.get()
        file_path = filedialog.asksaveasfilename(
            title="Salva come",
            filetypes=[(f"{selected_format.upper()} Audio", f"*.{selected_format}")],
            defaultextension=f".{selected_format}"
        )
        if file_path:
            self.audio_path_var.set(file_path)
            
    def add_audio_files(self):
        file_paths = filedialog.askopenfilenames(
            title="Seleziona i file audio",
            filetypes=[("Audio", "*.mp3 *.wav *.ogg *.aac *.flac")]
        )
        if file_paths:
            self.audio_files.extend(file_paths)
            for file_path in file_paths:
                self.files_listbox.insert(tk.END, os.path.basename(file_path))
                
    def remove_selected_file(self):
        selected_index = self.files_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.files_listbox.delete(index)
            self.audio_files.pop(index)
            
    def clear_files_list(self):
        self.files_listbox.delete(0, tk.END)
        self.audio_files.clear()
            
    def convert_video_to_audio(self):
        video_path = self.video_path_var.get()
        audio_path = self.audio_path_var.get()
        bitrate = self.quality_var.get()

        if not video_path or not audio_path:
            messagebox.showwarning("Attenzione", "Devi selezionare un file video e un percorso per l'audio.")
            return

        if not os.path.exists(video_path):
            messagebox.showerror("Errore", f"Il file video selezionato non esiste:\n{video_path}")
            return

        try:
            self.progress_bar["value"] = 0
            self.status_label.config(text="Analizzando il video...")
            self.progress_label.config(text="Analisi in corso...")
            self.root.update_idletasks()

            # Ottieni la durata totale del video con ffmpeg
            probe_command = [FFMPEG_PATH, "-i", video_path]
            result = subprocess.run(probe_command, stderr=subprocess.PIPE, text=True)
            duration_match = re.search(r"Duration: (\d+):(\d+):(\d+)\.(\d+)", result.stderr)

            if not duration_match:
                messagebox.showerror("Errore", "Impossibile determinare la durata del video.")
                return

            hours, minutes, seconds, _ = map(int, duration_match.groups())
            total_duration = hours * 3600 + minutes * 60 + seconds  # Converti in secondi
            self.progress_bar["maximum"] = total_duration

            self.status_label.config(text="Conversione in corso...")
            self.progress_label.config(text="0%")
            self.root.update_idletasks()

            command = [
                FFMPEG_PATH, "-i", video_path, "-vn", "-ab", bitrate, "-y", audio_path
            ]

            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, 
                                     universal_newlines=True, bufsize=1)

            # Funzione per monitorare l'output in un thread separato
            def monitor_progress():
                for line in iter(process.stderr.readline, ''):
                    time_match = re.search(r"time=(\d+):(\d+):(\d+)\.(\d+)", line)
                    if time_match:
                        h, m, s, _ = map(int, time_match.groups())
                        current_time = h * 3600 + m * 60 + s
                        percentage = min(100, int((current_time / total_duration) * 100))
                        
                        self.progress_bar["value"] = current_time
                        self.progress_label.config(text=f"{percentage}%")
                        self.status_label.config(text=f"Conversione in corso... {percentage}%")
                        self.root.update_idletasks()

            # Avvia il monitoraggio in un thread
            progress_thread = threading.Thread(target=monitor_progress, daemon=True)
            progress_thread.start()

            # Attendi il completamento del processo
            process.wait()
            progress_thread.join(timeout=1.0)  # Attendi che il thread termini

            if process.returncode != 0:
                messagebox.showerror("Errore", "Errore nella conversione con FFmpeg.")
                self.status_label.config(text="Conversione fallita!")
                return

            self.progress_bar["value"] = total_duration
            self.progress_label.config(text="100%")
            self.status_label.config(text="Conversione completata!")
            messagebox.showinfo("Successo", f"Audio salvato in:\n{audio_path}")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante la conversione: {e}")
            self.status_label.config(text="Errore durante la conversione")
            self.progress_label.config(text="Errore")

    def merge_audio_files(self):
        if len(self.audio_files) < 2:
            messagebox.showwarning("Attenzione", "Seleziona almeno due file audio da unire.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Salva file unito",
            defaultextension=".mp3",
            filetypes=[("MP3", "*.mp3"), ("WAV", "*.wav"), ("OGG", "*.ogg")]
        )
        
        if not output_path:
            return

        try:
            self.status_label.config(text="Unione file in corso...")
            self.root.update_idletasks()

            # Crea un file di testo temporaneo con l'elenco dei file
            temp_list_file = os.path.join(os.path.dirname(output_path), "temp_file_list.txt")
            with open(temp_list_file, "w") as f:
                for audio_file in self.audio_files:
                    f.write("file '" + {audio_file.replace('\\', '/')}+ "'\n")

            # Comando ffmpeg per unire i file
            command = [
                FFMPEG_PATH,
                "-f", "concat",
                "-safe", "0",
                "-i", temp_list_file,
                "-c", "copy",
                "-y", output_path
            ]

            result = subprocess.run(command, capture_output=True, text=True)

            # Rimuovi il file temporaneo
            if os.path.exists(temp_list_file):
                os.remove(temp_list_file)

            if result.returncode != 0:
                messagebox.showerror("Errore", f"Errore FFmpeg: {result.stderr}")
                self.status_label.config(text="Unione fallita")
                return

            self.status_label.config(text="Unione completata con successo!")
            messagebox.showinfo("Successo", f"File audio unito salvato in:\n{output_path}")

        except Exception as e:
            messagebox.showerror("Errore", f"Errore durante l'unione dei file: {e}")
            self.status_label.config(text="Errore durante l'unione")


# Funzione principale
def main():
    root = tk.Tk()
    app = ModernVideoToAudioConverter(root)
    
    # Centra la finestra sullo schermo
    window_width = 700
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # Icona dell'applicazione (se disponibile)
    try:
        # Crea un'icona dell'app dal base64
        icon_data = base64.b64decode(AUDIO_ICON)
        icon_image = Image.open(BytesIO(icon_data))
        # Salva temporaneamente l'immagine
        with BytesIO() as output:
            icon_image.save(output, format="ICO")
            output.seek(0)
            icon = ImageTk.PhotoImage(Image.open(output))
            root.iconphoto(True, icon)
    except Exception:
        pass  # Ignora errori nell'impostazione dell'icona

    root.mainloop()


if __name__ == "__main__":
    main()