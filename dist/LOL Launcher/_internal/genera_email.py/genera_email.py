import requests
import random
import string
import tkinter as tk
from tkinter import ttk, messagebox
from plyer import notification
from datetime import datetime

# Variabili globali
account_data = None
jwt_token = None
auto_refresh_enabled = False
notified_messages = set()  # Contiene gli ID dei messaggi già notificati
refresh_timer = 10  # Timer iniziale in secondi

def auto_refresh_inbox():
    """Funzione per aggiornare automaticamente la posta"""
    global auto_refresh_enabled

    if auto_refresh_enabled:
        check_inbox()  # Esegui la funzione per aggiornare la posta
        # Pianifica il prossimo aggiornamento dopo 10 secondi
        root.after(10000, auto_refresh_inbox)

def toggle_auto_refresh():
    global auto_refresh_enabled, refresh_timer
    
    auto_refresh_enabled = not auto_refresh_enabled  # Alterna tra True e False
    
    if auto_refresh_enabled:
        auto_refresh_button.config(text="Disattiva Auto-refresh", bg="#e74c3c")
        refresh_timer = 10  # Reset del timer
        update_timer()  # Avvia il countdown
    else:
        auto_refresh_button.config(text="Attiva Auto-refresh", bg="#3498db")
        timer_var.set("Auto-refresh disattivato")

def update_timer():
    global refresh_timer, auto_refresh_enabled

    if auto_refresh_enabled:
        if refresh_timer > 0:
            refresh_timer -= 1
            timer_var.set(f"Aggiornamento in: {refresh_timer}s")
            root.after(1000, update_timer)  # Chiama di nuovo la funzione dopo 1 secondo
        else:
            refresh_timer = 10  # Reset del timer
            check_inbox()  # Aggiorna la posta
            update_timer()  # Riavvia il countdown
    else:
        timer_var.set("Auto-refresh disattivato")

# Funzione per ottenere un dominio valido dall'API
def get_valid_domain():
    try:
        response = requests.get("https://api.mail.tm/domains")
        if response.status_code == 200:
            domains = response.json()["hydra:member"]
            return domains[0]["domain"]  # Prendi il primo dominio valido
        else:
            messagebox.showerror("Errore", "Impossibile recuperare i domini validi.")
            return None
    except Exception as e:
        messagebox.showerror("Errore di connessione", f"Errore: {str(e)}")
        return None

# Funzione per generare un nome utente casuale
def generate_random_username(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

# Funzione per creare un'email temporanea
def create_temp_email():
    global account_data, jwt_token
    
    status_var.set("Stato: Generazione email in corso...")
    status_label.config(fg="#f39c12")
    root.update()
    
    domain = get_valid_domain()
    if domain:
        username = generate_random_username()
        email_address = f"{username}@{domain}"

        try:
            response = requests.post("https://api.mail.tm/accounts", json={
                "address": email_address,
                "password": "securepassword123"
            })

            if response.status_code == 201:
                account_data = response.json()
                login_response = requests.post("https://api.mail.tm/token", json={
                    "address": email_address,
                    "password": "securepassword123"
                })
                if login_response.status_code == 200:
                    jwt_token = login_response.json()["token"]
                    email_var.set(account_data['address'])
                    email_entry.config(state="normal", bg="#1e272e", fg="#ffffff", 
                                     readonlybackground="#1e272e", insertbackground="#ffffff")
                    email_entry.config(state="readonly")
                    
                    # Cambia lo stato dell'interfaccia per mostrare che l'email è attiva
                    status_var.set("Stato: Email attiva e pronta")
                    status_label.config(fg="#2ecc71")
                    
                    # Abilita tutti i pulsanti necessari
                    copy_button.config(state="normal")
                    refresh_button.config(state="normal")
                    auto_refresh_button.config(state="normal")
                    read_button.config(state="normal")
                    
                    # Esegui subito un controllo della posta
                    check_inbox()
                    
                    # Opzionale: mostra un tooltip visivo
                    show_tooltip("Email generata con successo!", "#2ecc71")
                else:
                    messagebox.showerror("Errore", "Autenticazione fallita.")
                    status_var.set("Stato: Errore di autenticazione")
                    status_label.config(fg="#e74c3c")
            else:
                messagebox.showerror("Errore", f"Errore nella creazione dell'email: {response.text}")
                status_var.set("Stato: Errore nella creazione")
                status_label.config(fg="#e74c3c")
        except Exception as e:
            messagebox.showerror("Errore di connessione", f"Errore: {str(e)}")
            status_var.set("Stato: Errore di connessione")
            status_label.config(fg="#e74c3c")

# Funzione per mostrare un tooltip visivo temporaneo
def show_tooltip(message, color="#2ecc71"):
    tooltip = tk.Toplevel(root)
    tooltip.overrideredirect(True)  # Rimuove la barra del titolo
    
    # Posiziona al centro della finestra principale
    x = root.winfo_x() + (root.winfo_width() // 2) - 150
    y = root.winfo_y() + (root.winfo_height() // 2) - 40
    tooltip.geometry(f"300x80+{x}+{y}")
    
    # Frame con bordo arrotondato (simulato)
    frame = tk.Frame(tooltip, bg=color, bd=0)
    frame.pack(fill="both", expand=True, padx=0, pady=0)
    
    label = tk.Label(frame, text=message, font=("Segoe UI", 12, "bold"), 
                    bg=color, fg="white", pady=10)
    label.pack(fill="both", expand=True)
    
    # Chiudi dopo 2 secondi
    tooltip.after(2000, tooltip.destroy)

# Funzione per copiare l'indirizzo email negli appunti
def copy_to_clipboard():
    email = email_var.get()
    if email:
        root.clipboard_clear()
        root.clipboard_append(email)
        root.update()  # Aggiorna gli appunti
        show_tooltip("Indirizzo email copiato!", "#3498db")
    else:
        messagebox.showerror("Errore", "Nessun indirizzo email da copiare.")

# Funzione per formattare la data in italiano
def format_date(iso_date):
    try:
        dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
        now = datetime.now()
        
        # Se oggi, mostra solo l'ora
        if dt.date() == now.date():
            return f"Oggi, {dt.strftime('%H:%M')}"
        return dt.strftime("%d/%m/%Y, %H:%M")
    except:
        return "Data sconosciuta"

# Funzione per controllare la posta in arrivo
def check_inbox():
    global notified_messages  # Per accedere alla lista dei messaggi notificati

    if not jwt_token:
        messagebox.showerror("Errore", "Crea prima un'email temporanea.")
        return

    status_var.set("Stato: Controllo della posta...")
    status_label.config(fg="#f39c12")
    root.update()

    try:
        headers = {"Authorization": f"Bearer {jwt_token}"}
        response = requests.get("https://api.mail.tm/messages", headers=headers)

        if response.status_code == 200:
            messages = response.json()["hydra:member"]
            inbox_list.delete(*inbox_list.get_children())  # Svuota la lista

            if messages:
                status_var.set(f"Stato: {len(messages)} messaggio/i trovato/i.")
                status_label.config(fg="#2ecc71")
                
                # Ordina i messaggi per data (i più recenti prima)
                messages.sort(key=lambda m: m.get("createdAt", ""), reverse=True)
                
                for msg in messages:
                    # Aggiungi informazioni sulla data
                    formatted_date = format_date(msg.get("createdAt", ""))
                    from_name = msg.get("from", {}).get("name", "Sconosciuto")
                    from_address = msg.get("from", {}).get("address", "")
                    
                    # Determina se è un messaggio non letto
                    is_unread = not msg.get("seen", True)
                    
                    # Inserisci nella lista, usa tag per messaggi non letti
                    item_id = inbox_list.insert("", "end", 
                                               values=(msg["id"], from_name, msg["subject"], formatted_date),
                                               tags=("unread",) if is_unread else ())
                    
                    # Invia una notifica solo per i nuovi messaggi
                    if msg["id"] not in notified_messages:
                        notification.notify(
                            title="Nuovo Messaggio!",
                            message=f"Da: {from_name}\nOggetto: {msg['subject']}",
                            app_name="Email Temporanea",
                            timeout=5
                        )
                        notified_messages.add(msg["id"])  # Aggiungi l'ID del messaggio notificato
            else:
                status_var.set("Stato: Nessun messaggio trovato.")
                status_label.config(fg="#3498db")
        else:
            messagebox.showerror("Errore", f"Errore durante il recupero della posta: {response.text}")
            status_var.set("Stato: Errore nel recupero della posta")
            status_label.config(fg="#e74c3c")
    except Exception as e:
        messagebox.showerror("Errore di connessione", f"Errore: {str(e)}")
        status_var.set("Stato: Errore di connessione")
        status_label.config(fg="#e74c3c")

# Funzione per leggere il contenuto di un messaggio in una nuova finestra
def read_message(event=None):
    if not jwt_token:
        messagebox.showerror("Errore", "Crea prima un'email temporanea.")
        return

    selected_item = inbox_list.selection()
    if not selected_item:
        messagebox.showerror("Errore", "Seleziona un messaggio da leggere.")
        return

    message_id = inbox_list.item(selected_item[0], "values")[0]
    
    try:
        headers = {"Authorization": f"Bearer {jwt_token}"}
        response = requests.get(f"https://api.mail.tm/messages/{message_id}", headers=headers)

        if response.status_code == 200:
            message = response.json()

            # Segna il messaggio come letto nell'interfaccia
            inbox_list.item(selected_item[0], tags=())

            # Crea una nuova finestra per visualizzare il messaggio
            message_window = tk.Toplevel(root)
            message_window.title("Dettagli del Messaggio")
            message_window.geometry("600x500")
            message_window.configure(bg="#1e272e")
            message_window.minsize(500, 400)
            
            # Aggiungi un'icona di chiusura e altri controlli
            top_frame = tk.Frame(message_window, bg="#1e272e")
            top_frame.pack(fill="x", pady=(10, 0))
            
            subject_frame = tk.Frame(top_frame, bg="#1e272e", padx=15)
            subject_frame.pack(fill="x")
            
            subject_label = tk.Label(subject_frame, text=message.get('subject', 'Nessun oggetto'), 
                                 font=("Segoe UI", 16, "bold"), bg="#1e272e", fg="#ffffff",
                                 anchor="w", justify="left", wraplength=550)
            subject_label.pack(fill="x", pady=(5, 10), anchor="w")
            
            divider = ttk.Separator(message_window, orient="horizontal")
            divider.pack(fill="x", padx=15)
            
            info_frame = tk.Frame(message_window, bg="#1e272e", padx=15, pady=5)
            info_frame.pack(fill="x")
            
            # Info sul mittente
            from_name = message.get("from", {}).get("name", "")
            from_address = message.get("from", {}).get("address", "")
            from_text = f"{from_name} <{from_address}>" if from_name else from_address
            
            from_label = tk.Label(info_frame, text="Da:", font=("Segoe UI", 10, "bold"), 
                               bg="#1e272e", fg="#95a5a6", width=10, anchor="w")
            from_label.grid(row=0, column=0, sticky="w", pady=2)
            
            from_value = tk.Label(info_frame, text=from_text, font=("Segoe UI", 10), 
                               bg="#1e272e", fg="#ffffff", anchor="w")
            from_value.grid(row=0, column=1, sticky="w", pady=2)
            
            # Data di ricezione
            date_str = format_date(message.get("createdAt", ""))
            date_label = tk.Label(info_frame, text="Ricevuto:", font=("Segoe UI", 10, "bold"), 
                               bg="#1e272e", fg="#95a5a6", width=10, anchor="w")
            date_label.grid(row=1, column=0, sticky="w", pady=2)
            
            date_value = tk.Label(info_frame, text=date_str, font=("Segoe UI", 10), 
                               bg="#1e272e", fg="#ffffff", anchor="w")
            date_value.grid(row=1, column=1, sticky="w", pady=2)
            
            # Destinatario
            to_label = tk.Label(info_frame, text="A:", font=("Segoe UI", 10, "bold"), 
                             bg="#1e272e", fg="#95a5a6", width=10, anchor="w")
            to_label.grid(row=2, column=0, sticky="w", pady=2)
            
            to_value = tk.Label(info_frame, text=account_data['address'], font=("Segoe UI", 10), 
                             bg="#1e272e", fg="#ffffff", anchor="w")
            to_value.grid(row=2, column=1, sticky="w", pady=2)
            
            divider2 = ttk.Separator(message_window, orient="horizontal")
            divider2.pack(fill="x", padx=15, pady=(5, 0))
            
            # Contenuto del messaggio
            content_frame = tk.Frame(message_window, bg="#1e272e", padx=15, pady=10)
            content_frame.pack(fill="both", expand=True)
            
            # Text widget con scrollbar
            content_text = tk.Text(content_frame, wrap="word", font=("Segoe UI", 11), 
                                bg="#2c3e50", fg="#ecf0f1", relief="flat", bd=1,
                                padx=10, pady=10)
            content_text.pack(side="left", fill="both", expand=True)
            
            scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=content_text.yview)
            content_text.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            
            # Inserisci il testo del messaggio
            msg_text = message.get('text', message.get('html', 'Nessun contenuto'))
            content_text.insert("1.0", msg_text)
            content_text.config(state="disabled")  # Rendi il testo non modificabile
            
            # Barra dei pulsanti in basso
            button_frame = tk.Frame(message_window, bg="#1e272e", padx=15, pady=10)
            button_frame.pack(fill="x")
            
            reply_button = tk.Button(button_frame, text="Chiudi", font=("Segoe UI", 10), 
                                   command=message_window.destroy, bg="#3498db", fg="white",
                                   padx=15, pady=5, relief="flat", bd=0)
            reply_button.pack(side="right", padx=5)

        else:
            messagebox.showerror("Errore", f"Errore nella lettura del messaggio: {response.text}")
    except Exception as e:
        messagebox.showerror("Errore di connessione", f"Errore: {str(e)}")

# Creazione della GUI
root = tk.Tk()
root.title("Email Temporanea")
root.geometry("750x600")
root.minsize(750, 600)
root.configure(bg="#1e272e")

# Configurazione dei colori e stili
PRIMARY_COLOR = "#3498db"     # Azzurro
ACCENT_COLOR = "#2ecc71"      # Verde
WARNING_COLOR = "#e74c3c"     # Rosso
NEUTRAL_COLOR = "#95a5a6"     # Grigio chiaro
BG_COLOR = "#1e272e"          # Sfondo scuro
BG_DARK = "#0c141c"           # Sfondo più scuro
TEXT_COLOR = "#ecf0f1"        # Testo chiaro

# Variabile per lo stato della GUI
status_var = tk.StringVar()
status_var.set("Stato: In attesa di generare un'email")

# Variabile per mostrare l'email generata
email_var = tk.StringVar()

# Variabile per il timer
timer_var = tk.StringVar()
timer_var.set("Auto-refresh disattivato")

# Frame principale con padding
main_frame = tk.Frame(root, bg=BG_COLOR, padx=20, pady=15)
main_frame.pack(fill="both", expand=True)

# Etichetta per il titolo con icona
header_frame = tk.Frame(main_frame, bg=BG_COLOR)
header_frame.pack(fill="x", pady=(0, 15))

# Icona (qui rappresentata da un emoji, sostituire con un'icona vera)
icon_label = tk.Label(header_frame, text="📧", font=("Segoe UI", 24), bg=BG_COLOR, fg=PRIMARY_COLOR)
icon_label.pack(side="left", padx=(0, 10))

# Titolo principale
label_title = tk.Label(header_frame, text="Email Temporanea", font=("Segoe UI", 24, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
label_title.pack(side="left")

# Frame per i controlli dell'email
email_controls_frame = tk.Frame(main_frame, bg=BG_COLOR)
email_controls_frame.pack(fill="x", pady=10)

# Bottone per generare l'email
generate_button = tk.Button(email_controls_frame, text="Genera Email", 
                         font=("Segoe UI", 11), command=create_temp_email, 
                         bg=PRIMARY_COLOR, fg="white", 
                         padx=15, pady=8, relief="flat", bd=0)
generate_button.pack(side="left", padx=(0, 10))

# Campo per mostrare l'email generata con etichetta
email_frame = tk.Frame(email_controls_frame, bg=BG_COLOR)
email_frame.pack(side="left", fill="x", expand=True)

email_label = tk.Label(email_frame, text="Il tuo indirizzo:", font=("Segoe UI", 9), bg=BG_COLOR, fg=NEUTRAL_COLOR)
email_label.pack(anchor="w", padx=5)

email_entry = tk.Entry(email_frame, textvariable=email_var, font=("Segoe UI", 11), 
                     width=40, bg=BG_DARK, fg=TEXT_COLOR, 
                     relief="flat", bd=0, insertbackground=TEXT_COLOR)
email_entry.pack(fill="x", padx=5, ipady=5)

# Bottone per copiare l'email
copy_button = tk.Button(email_controls_frame, text="Copia", 
                      font=("Segoe UI", 11), command=copy_to_clipboard, 
                      bg="#34495e", fg="white", 
                      padx=12, pady=8, relief="flat", bd=0, state="disabled")
copy_button.pack(side="right", padx=(10, 0))

# Separatore
separator = ttk.Separator(main_frame, orient="horizontal")
separator.pack(fill="x", pady=15)

# Frame per i messaggi
messages_frame = tk.Frame(main_frame, bg=BG_COLOR)
messages_frame.pack(fill="both", expand=True, pady=5)

# Etichetta per la sezione messaggi
inbox_label = tk.Label(messages_frame, text="Messaggi Ricevuti", font=("Segoe UI", 14, "bold"), bg=BG_COLOR, fg=TEXT_COLOR)
inbox_label.pack(anchor="w", pady=(0, 10))

# Lista per mostrare la posta in arrivo
inbox_frame = tk.Frame(messages_frame, bg=BG_COLOR)
inbox_frame.pack(fill="both", expand=True)

# Configurazione dello stile Treeview
style = ttk.Style()
style.theme_use("clam")  # Usa il tema "clam" che funziona bene con la personalizzazione
style.configure("Treeview", 
              background=BG_DARK, 
              foreground=TEXT_COLOR, 
              fieldbackground=BG_DARK, 
              rowheight=30,
              borderwidth=0)
style.configure("Treeview.Heading", 
              background="#34495e", 
              foreground=TEXT_COLOR, 
              relief="flat",
              font=("Segoe UI", 10, "bold"))
style.map("Treeview", 
        background=[("selected", "#2980b9")], 
        foreground=[("selected", "white")])

# Creazione del Treeview con colonne adeguate
inbox_list = ttk.Treeview(inbox_frame, columns=("id", "from", "subject", "date"), show="headings", height=10)

# Nascondi la colonna ID
inbox_list.heading("id", text="ID")
inbox_list.heading("from", text="Mittente")
inbox_list.heading("subject", text="Oggetto")
inbox_list.heading("date", text="Data")

inbox_list.column("id", width=0, stretch=False)  # Nasconde la colonna ID
inbox_list.column("from", width=150, minwidth=120)
inbox_list.column("subject", width=350, minwidth=200)
inbox_list.column("date", width=120, minwidth=100)

# Configura il tag per i messaggi non letti in modo corretto
inbox_list.tag_configure("unread", font=("Segoe UI", 10, "bold"))

# Binding per doppio click
inbox_list.bind("<Double-1>", read_message)
inbox_list.pack(side="left", fill="both", expand=True)

# Scrollbar per la lista
scrollbar = ttk.Scrollbar(inbox_frame, orient="vertical", command=inbox_list.yview)
inbox_list.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

# Frame per i pulsanti di controllo in basso
controls_frame = tk.Frame(main_frame, bg=BG_COLOR, pady=15)
controls_frame.pack(fill="x")

# Etichetta per il timer
timer_label = tk.Label(controls_frame, textvariable=timer_var, font=("Segoe UI", 9), bg=BG_COLOR, fg=NEUTRAL_COLOR)
timer_label.pack(side="left", padx=5)

# Etichetta per lo stato
status_label = tk.Label(controls_frame, textvariable=status_var, font=("Segoe UI", 9), bg=BG_COLOR, fg=NEUTRAL_COLOR)
status_label.pack(side="left", padx=20)

# Frame per i pulsanti a destra
button_container = tk.Frame(controls_frame, bg=BG_COLOR)
button_container.pack(side="right")

# Bottone per leggere il messaggio
read_button = tk.Button(button_container, text="Leggi Messaggio", font=("Segoe UI", 10), 
                      command=read_message, bg="#34495e", fg="white", 
                      padx=10, pady=5, relief="flat", bd=0, state="disabled")
read_button.pack(side="right", padx=5)

# Bottone per attivare l'auto-refresh
auto_refresh_button = tk.Button(button_container, text="Attiva Auto-refresh", font=("Segoe UI", 10), 
                             command=toggle_auto_refresh, bg="#3498db", fg="white", 
                             padx=10, pady=5, relief="flat", bd=0, state="disabled")
auto_refresh_button.pack(side="right", padx=5)

# Bottone per aggiornare manualmente la posta
refresh_button = tk.Button(button_container, text="Aggiorna Posta", font=("Segoe UI", 10), 
                        command=check_inbox, bg="#2ecc71", fg="white", 
                        padx=10, pady=5, relief="flat", bd=0, state="disabled")
refresh_button.pack(side="right", padx=5)

# Esegui la GUI
root.mainloop()