import os
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from Riot_API import send_request, RiotAPIError
from dotenv import load_dotenv
import urllib3
from datetime import datetime
import requests
import csv
import json
import zipfile
import threading
import time
import pickle
import io
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseUpload
from PIL import Image, ImageTk
import webbrowser
import logging

print("Script avviato!")

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)


# Scopes richiesti per caricare file su Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive.file']

# Costanti per lo stile dell'UI
DARK_BG = "#1e1e1e"
DARK_SECONDARY = "#252526"
ACCENT_COLOR = "#0078D7"  # Blu accento
HOVER_COLOR = "#2A2D2E"
TEXT_COLOR = "#E0E0E0"
BUTTON_BG = "#333333"
BUTTON_HOVER = "#444444"
TREEVIEW_BG = "#2d2d30"
TREEVIEW_SELECTED = "#0e639c"
DISCORD_COLOR = "#5865F2"  # Colore Discord
RIOT_COLOR = "#D13639"     # Colore Riot

def authenticate_google_drive():
    """Autenticazione e creazione del servizio di Google Drive."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'C:\Users\dbait\Desktop\MOD LOL\script\json\credentials.json', SCOPES)  # Usa il tuo file JSON delle credenziali
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Crea il servizio di Google Drive
    service = build('drive', 'v3', credentials=creds)
    return service


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Carica la chiave API dal file .emv
load_dotenv("API.emv")
API_KEY = os.getenv("RIOT_API_KEY")

# Nome del file per salvare i dati
DATA_FILE = r"C:\Users\dbait\Desktop\MOD LOL\script\json\match_data.json"


QUEUE_ID_MAP = {
    400: "Normal Draft",  # Esempio: Selezione normale
    420: "Ranked Solo/Duo",  # Classificata Solo/Duo
    430: "Normal Blind",  # Selezione cieca
    440: "Ranked Flex",  # Classificata Flex
    450: "ARAM",  # ARAM
    480: "Partita rapida", #Swiftplay
    700: "Clash",  # Clash
    900: "URF", #URF
    # Aggiungi altri ID delle code come necessario
}



RIOT_ID_FILE = "riot_id.json"


def save_riot_id(game_name, tag_line):
    """Salva il Riot ID in un file JSON."""
    data = {"game_name": game_name.lower(), "tag_line": tag_line.lower()}
    try:
        with open(RIOT_ID_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel salvataggio del Riot ID: {e}")

def load_riot_id():
    """Carica il Riot ID dal file JSON."""
    if os.path.exists(RIOT_ID_FILE):
        try:
            with open(RIOT_ID_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("game_name", "").lower(), data.get("tag_line", "").lower()
        except json.JSONDecodeError:
            return "", ""  # File vuoto o malformato
    return "", ""


# Funzione per caricare i dati salvati
def load_all_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                # Assicurati che i dati siano un dizionario
                if isinstance(data, dict):
                    return data
                else:
                    # Se i dati non sono un dizionario, sostituisci con un dizionario vuoto
                    return {}
        except json.JSONDecodeError:
            return {}  # File vuoto o malformato
    return {}


def save_all_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Errore", f"Errore nel salvataggio dei dati: {e}")


# Funzione per aggiungere dati evitando duplicati per un Riot ID
def add_data_for_riot_id(riot_id, new_matches):
    """Aggiungi i dati alla cache per un Riot ID."""
    all_data = load_all_data()
    if riot_id.lower() not in all_data:
        all_data[riot_id] = []
    
    existing_ids = {match["id"] for match in all_data[riot_id]}

    # Aggiungi solo i nuovi match
    for match in new_matches:
        if match["id"] not in existing_ids:
            all_data[riot_id].append(match)

    # Salva i dati aggiornati nella cache
    save_all_data(all_data)
    return all_data[riot_id]


def load_data_for_riot_id(riot_id):
    """Carica i dati dalla cache per un Riot ID."""
    all_data = load_all_data()
    return all_data.get(riot_id, [])


def populate_treeview(data):
    # Ordina i dati in base alla data (convertita in datetime per sicurezza)
    sorted_data = sorted(data, key=lambda x: datetime.strptime(x["date"], '%Y-%m-%d %H:%M:%S'), reverse=True)

    # Svuota la Treeview
    tree_matches.delete(*tree_matches.get_children())
    
    # Popola la Treeview con i dati ordinati
    for idx, match in enumerate(sorted_data):
        # Alterna i colori delle righe per una migliore leggibilità
        row_tags = ('oddrow',) if idx % 2 == 1 else ('evenrow',)
        
        # Aggiungi tag per K/D/A positivo o negativo
        kda_parts = match["score"].split('/')
        if len(kda_parts) == 3:
            try:
                kills, deaths, _ = map(int, kda_parts)
                if kills > deaths:
                    row_tags = row_tags + ('positive',)
                elif kills < deaths:
                    row_tags = row_tags + ('negative',)
            except ValueError:
                pass  # Ignora se la conversione fallisce
        
        tree_matches.insert(
            "", "end",
            values=(match["id"], match["mode"], match["duration"], match["date"], match["champion"], match["score"]),
            tags=row_tags
        )


# Funzione per inviare richieste all'API Riot
def send_request(url, method="GET", data=None):
    """
    Invia una richiesta all'API Riot.

    Args:
        url (str): L'URL completo dell'API.
        method (str): Metodo HTTP (default: GET).
        data (dict): Dati per il corpo della richiesta (default: None).

    Returns:
        requests.Response: La risposta dell'API.
    """
    import requests

    headers = {
        "X-Riot-Token": API_KEY,
        "Content-Type": "application/json"
    }
    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=data, verify=False)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, verify=False)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, verify=False)
        else:  # Default: GET
            response = requests.get(url, headers=headers, verify=False)

        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise RiotAPIError(f"Errore di rete: {e}")


# Funzione per recuperare il PUUID dal Riot ID
def get_puuid(game_name, tag_line, region="europe"):
    try:
        endpoint = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        response = send_request(endpoint, method="GET")
        if response.status_code == 200:
            return response.json().get("puuid")
        else:
            raise RiotAPIError(f"Errore nel recupero del PUUID: {response.status_code} - {response.text}")
    except RiotAPIError as e:
        messagebox.showerror("Errore API", str(e))
        return None
    except Exception as e:
        messagebox.showerror("Errore", str(e))
        return None

# Funzione per recuperare i match ID tramite PUUID
def get_match_ids(puuid, region="europe"):
    try:
        endpoint = f"https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=10"
        response = send_request(endpoint, method="GET")
        if response.status_code == 200:
            return response.json()
        else:
            raise RiotAPIError(f"Errore nel recupero dei match ID: {response.status_code} - {response.text}")
    except RiotAPIError as e:
        messagebox.showerror("Errore API", str(e))
        return []
    except Exception as e:
        messagebox.showerror("Errore", str(e))
        return []

import base64

def read_lockfile():
    """
    Legge il lockfile del client Riot per ottenere le informazioni di autenticazione.

    Returns:
        dict: Un dizionario contenente porta, token, e altri dati.
    """
    lockfile_path = "C:\\Riot Games\\League of Legends\\lockfile"    
    try:
        with open(lockfile_path, "r") as file:
            data = file.read().split(":")
            return {
                "name": data[0],
                "pid": data[1],
                "port": data[2],
                "password": data[3],
                "protocol": data[4]
            }
    except FileNotFoundError:
        raise RiotAPIError("Lockfile non trovato. Assicurati che il client Riot sia in esecuzione.")


def send_request_with_lockfile(endpoint, method="GET", data=None):
    """
    Invia una richiesta alle API Riot utilizzando il lockfile per l'autenticazione.

    Args:
        endpoint (str): Endpoint dell'API.
        method (str): Metodo HTTP (default: GET).
        data (dict): Dati per il corpo della richiesta (default: None).

    Returns:
        requests.Response: La risposta dell'API.
    """
    import requests

    lockfile = read_lockfile()
    base_url = f"https://127.0.0.1:{lockfile['port']}{endpoint}"
    auth_header = base64.b64encode(f"riot:{lockfile['password']}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json"
    }
    try:
        if method == "POST":
            response = requests.post(base_url, headers=headers, json=data, verify=False)
        elif method == "PUT":
            response = requests.put(base_url, headers=headers, json=data, verify=False)
        elif method == "DELETE":
            response = requests.delete(base_url, headers=headers, verify=False)
        else:  # Default: GET
            response = requests.get(base_url, headers=headers, verify=False)

        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        raise RiotAPIError(f"Errore di rete: {e}")


# Funzioni per scaricare e guardare il replay
def send_replay_request(endpoint, match_id):
    """
    Invia una richiesta per scaricare o guardare il replay.

    Args:
        endpoint (str): Endpoint API (download o watch).
        match_id (str): ID della partita.

    Returns:
        str: Messaggio di successo o errore.
    """
    match_id_cleaned = match_id.split("_")[1] if "_" in match_id else match_id
    full_endpoint = f"/lol-replays/v1/rofls/{match_id_cleaned}/{endpoint}"
    body = {"componentType": ""}  # Body richiesto
    try:
        response = send_request_with_lockfile(full_endpoint, method="POST", data=body)
        if response.status_code == 204:
            return f"Richiesta {endpoint} per la partita {match_id} completata con successo."
        else:
            return f"Errore durante {endpoint}: {response.status_code} - {response.text}"
    except RiotAPIError as e:
        return f"Errore API Riot: {str(e)}"
    except Exception as e:
        return f"Errore sconosciuto: {str(e)}"


def download_replay_gui(match_id):
    result = send_replay_request("download", match_id)
    if "successo" in result.lower():
        show_custom_messagebox("Download Replay", result, "success")
    else:
        show_custom_messagebox("Errore Download", result, "error")

def watch_replay_gui(match_id):
    result = send_replay_request("watch", match_id)
    if "successo" in result.lower():
        show_custom_messagebox("Avvio Replay", result, "success")
    else:
        show_custom_messagebox("Errore Avvio", result, "error")


# Funzione per ottenere i dettagli di una partita
def get_match_details(match_id, region="europe"):
    try:
        endpoint = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}"
        response = send_request(endpoint, method="GET")
        if response.status_code == 200:
            return response.json()
        else:
            raise RiotAPIError(f"Errore nel recupero dei dettagli del match: {response.status_code} - {response.text}")
    except RiotAPIError as e:
        messagebox.showerror("Errore API", str(e))
        return None
    except Exception as e:
        messagebox.showerror("Errore", str(e))
        return None
    

# Scarica e memorizza i dati dei campioni da DDragon
def load_champion_data():
    """
    Scarica i dati dei campioni da DDragon e crea una mappa championId -> Nome.
    Returns:
        dict: Mappa degli ID dei campioni ai loro nomi.
    """
    try:
        # Ottieni l'ultima versione di DDragon
        version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        response = requests.get(version_url)
        response.raise_for_status()
        latest_version = response.json()[0]

        # Ottieni i dati dei campioni
        champions_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
        response = requests.get(champions_url)
        response.raise_for_status()
        data = response.json()

        # Crea una mappa championId -> Nome
        champion_data = {}
        for champ in data["data"].values():
            champion_data[int(champ["key"])] = champ["name"]
        return champion_data
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Errore DDragon", f"Errore nel caricamento dei dati dei campioni: {e}")
        return {}


def fetch_champion_names():
    """
    Scarica i dati dei campioni da DataDragon e restituisce una lista di nomi.
    Returns:
        list: Lista con i nomi dei campioni.
    """
    try:
        # Ottieni l'ultima versione di DataDragon
        version_url = "https://ddragon.leagueoflegends.com/api/versions.json"
        response = requests.get(version_url)
        response.raise_for_status()
        latest_version = response.json()[0]

        # Ottieni i dati dei campioni
        champions_url = f"https://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
        response = requests.get(champions_url)
        response.raise_for_status()
        data = response.json()

        # Crea una lista con i nomi dei campioni
        champion_names = [champ["name"] for champ in data["data"].values()]
        return sorted(champion_names)
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Errore DataDragon", f"Errore nel caricamento dei dati dei campioni: {e}")
        return []

# Carica i dati dei campioni una volta sola
champion_map = load_champion_data()

def get_champion_name(champion_id):
    """
    Ottieni il nome del campione dato il suo ID.
    Args:
        champion_id (int): ID del campione.
    Returns:
        str: Nome del campione o 'Sconosciuto' se non trovato.
    """
    return champion_map.get(champion_id, "Sconosciuto")


def send_to_discord_webhook(match_id, match_details, webhook_url):
    """
    Invia i dettagli del replay al webhook di Discord.

    Args:
        match_id (str): ID del match.
        match_details (dict): Dettagli del replay (modalità, durata, ecc.).
        webhook_url (str): URL del webhook di Discord.
    """
    try:
        # Messaggio da inviare al webhook
        message = {
            "content": f"📢 **Nuovo Replay Condiviso!**\n"
                       f"**Match ID:** {match_id}\n"
                       f"**Modalità:** {match_details['mode']}\n"
                       f"**Durata:** {match_details['duration']}\n"
                       f"**Campione:** {match_details['champion']}\n"
                       f"**Punteggio:** {match_details['score']}\n"
                       f"**Data:** {match_details['date']}"
        }

        # Invia il messaggio al webhook
        response = requests.post(webhook_url, json=message, headers={"Content-Type": "application/json"})
        response.raise_for_status()
        show_custom_messagebox("Condivisione Completata", "Il replay è stato condiviso su Discord con successo!", "success")
    except requests.exceptions.RequestException as e:
        show_custom_messagebox("Errore Discord", f"Errore durante la condivisione su Discord: {e}", "error")


def get_correct_file_path(replay_folder, match_id):
    """
    Cerca il file del replay nella cartella specificata, gestendo "_" e "-".

    Args:
        replay_folder (str): Cartella in cui cercare il file.
        match_id (str): ID del match.

    Returns:
        str: Percorso corretto del file.

    Raises:
        FileNotFoundError: Se il file non viene trovato.
    """
    # Percorso con underscore (_)
    replay_file = os.path.join(replay_folder, f"{match_id}.rofl")

    # Se non esiste, prova con il trattino (-)
    if not os.path.exists(replay_file):
        replay_file = os.path.join(replay_folder, f"{match_id.replace('_', '-')}.rofl")

    # Lancia un errore se nessuna variante è valida
    if not os.path.exists(replay_file):
        raise FileNotFoundError(f"Impossibile trovare il file specificato: {replay_file}")

    return replay_file


def upload_to_google_drive(file_path):
    """Carica un file su Google Drive e restituisce il link di download."""
    service = authenticate_google_drive()

    # Crea i metadati del file
    file_metadata = {'name': os.path.basename(file_path)}  # Il nome del file su Google Drive
    media = MediaFileUpload(file_path, mimetype='application/octet-stream')

    # Carica il file su Google Drive
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"File caricato con ID: {file['id']}")

    # Imposta il permesso per rendere il file accessibile a chiunque abbia il link
    permission = service.permissions().create(
        fileId=file['id'],
        body={'role': 'reader', 'type': 'anyone'},
    ).execute()
    print(f"Permessi impostati per il file con ID: {file['id']}")

    # Restituisce il link per il download del file
    return f"https://drive.google.com/uc?id={file['id']}"  # Link pubblico per il download

def upload_to_google_drive_with_progress(file_path, progress_bar):
    """Carica un file su Google Drive e aggiorna la barra di avanzamento manualmente."""
    try:
        service = authenticate_google_drive()  # Assicurati che l'autenticazione funzioni correttamente

        file_metadata = {'name': os.path.basename(file_path)}  # Nome del file su Google Drive
        file_size = os.path.getsize(file_path)  # Ottieni la dimensione del file

        progress_bar["maximum"] = file_size  # Imposta il valore massimo della barra
        print(f"Avvio caricamento del file: {file_path}, dimensione: {file_size} bytes")

        media = MediaFileUpload(file_path, mimetype="application/octet-stream", resumable=True)
        request = service.files().create(body=file_metadata, media_body=media)

        # Eseguiamo il caricamento con monitoraggio manuale
        bytes_uploaded = 0
        while True:
            status, response = request.next_chunk()  # Usa next_chunk per monitorare lo stato
            if status:
                bytes_uploaded = status.resumable_progress  # Ottieni i byte caricati
                progress_bar["value"] = bytes_uploaded  # Aggiorna la barra di progresso
                progress_bar.update()  # Forza l'aggiornamento della barra di progresso
                print(f"Caricato: {bytes_uploaded} bytes di {file_size}")

            if status is None:  # Se l'upload è completo
                print(f"Caricamento completato! File ID: {response['id']}")
                break

        file_id = response.get("id")
        print(f"File caricato con successo con ID: {file_id}")

        # Imposta i permessi per rendere il file accessibile a chiunque abbia il link
        service.permissions().create(
            fileId=file_id,
            body={'role': 'reader', 'type': 'anyone'},
        ).execute()

        return f"https://drive.google.com/uc?id={file_id}"

    except Exception as e:
        print(f"Errore durante il caricamento su Google Drive: {e}")  # Debug: Stampa l'errore
        show_custom_messagebox("Errore", f"Errore durante il caricamento su Google Drive: {e}", "error")
        return None

def share_replay_link_on_discord_with_progress(match_id, link, webhook_url):
    """Condividi il link del file caricato su Google Drive su Discord."""
    try:
        print("Inizio caricamento e condivisione su Discord...")  # Debug: Aggiungi log
        selected = tree_matches.selection()
        if selected:
            # Supponiamo che i dettagli del match siano memorizzati in "tree_matches"
            match_data = tree_matches.item(selected[0], "values")  # Ottieni i dati della riga selezionata
            match_id = match_data[0]  # ID del match
            match_date = match_data[3]  # Data del match
            match_type = match_data[1]
            champion = match_data[4]  # Campione usato
            score = match_data[5]  # K/D/A

            # Crea il messaggio per Discord includendo i dettagli
            message = f"📢 **Replay Condiviso!**\n" \
                      f"**Match ID:** {match_id}\n" \
                      f"**Data:** {match_date}\n" \
                      f"**Modalità di gioco:** {match_type}\n" \
                      f"**Campione Usato:** {champion}\n" \
                      f"**K/D/A:** {score}\n" \
                      f"🔗 [Scarica il Replay]({link})"

            # Invia il messaggio a Discord
            response = requests.post(
                webhook_url,
                json={"content": message}
            )
            response.raise_for_status()

            print(f"Risposta webhook Discord: {response.status_code}")  # Debug: Risposta del webhook
            show_custom_messagebox("Condivisione Completata", "Il replay è stato condiviso su Discord con successo!", "success")
        else:
            show_custom_messagebox("Errore", "Impossibile ottenere i dettagli del match.", "error")
    except Exception as e:
        print(f"Errore durante la condivisione su Discord: {e}")  # Debug: Stampa l'errore
        show_custom_messagebox("Errore", f"Errore durante la condivisione su Discord: {e}", "error")


def ensure_replay_downloaded(match_id):
    """
    Verifica se il replay è presente nella cartella locale, altrimenti lo scarica.

    Args:
        match_id (str): ID del match.

    Returns:
        str: Percorso del file del replay.
    """
    replay_folder = os.path.join(os.path.expanduser("~"), "Documents", "League of Legends", "Replays")

    try:
        # Cerca il file con "_" o "-" utilizzando la funzione di supporto
        replay_file = get_correct_file_path(replay_folder, match_id)
        return replay_file
    except FileNotFoundError:
        
        # Scarica il replay se non esiste
        endpoint = "download"
        result = send_replay_request(endpoint, match_id)
        if "successo" not in result.lower():
            raise Exception(f"Errore durante il download del replay: {result}")

        # Dopo il download, verifica nuovamente la presenza del file con attesa attiva
        for attempt in range(10):  # Tenta per un massimo di 10 volte
            try:
                replay_file = get_correct_file_path(replay_folder, match_id)
                return replay_file
            except FileNotFoundError:
                time.sleep(1)  # Attendi un secondo prima di riprovare

        # Se il file non viene trovato dopo il tempo massimo, lancia un errore
        raise FileNotFoundError(f"Impossibile trovare il file del replay anche dopo il download: {match_id}")


# === NUOVE FUNZIONI PER LA UI MODERNA ===

def show_custom_messagebox(title, message, msg_type="info"):
    """Mostra una finestra di messaggio personalizzata e moderna"""
    dialog = tk.Toplevel()
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.configure(bg=DARK_BG)
    dialog.resizable(False, False)
    dialog.transient(root)  # Rende la finestra modale
    dialog.grab_set()  # Blocca l'input nella finestra principale
    
    # Centrata rispetto alla finestra principale
    dialog.geometry(f"+{root.winfo_x() + (root.winfo_width() // 2) - 200}+{root.winfo_y() + (root.winfo_height() // 2) - 100}")
    
    # Icona in base al tipo di messaggio
    icon_label = tk.Label(dialog, bg=DARK_BG)
    if msg_type == "success":
        icon_text = "✅"
        title_color = "#4CAF50"  # Verde
    elif msg_type == "error":
        icon_text = "❌"
        title_color = "#F44336"  # Rosso
    elif msg_type == "warning":
        icon_text = "⚠️"
        title_color = "#FFC107"  # Giallo
    else:  # info
        icon_text = "ℹ️"
        title_color = "#2196F3"  # Blu
    
    icon_label.config(text=icon_text, font=("Segoe UI", 48), fg=title_color)
    icon_label.pack(pady=(20, 10))
    
    # Titolo del messaggio
    title_label = tk.Label(dialog, text=title, bg=DARK_BG, fg=title_color, font=("Segoe UI", 14, "bold"))
    title_label.pack(pady=(0, 10))
    
    # Messaggio
    msg_label = tk.Label(dialog, text=message, bg=DARK_BG, fg=TEXT_COLOR, font=("Segoe UI", 10), wraplength=350)
    msg_label.pack(pady=(0, 20))
    
    # Pulsante OK
    ok_button = tk.Button(dialog, text="OK", bg=BUTTON_BG, fg=TEXT_COLOR, font=("Segoe UI", 10),
                         activebackground=BUTTON_HOVER, activeforeground=TEXT_COLOR, bd=0, width=10,
                         command=dialog.destroy)
    ok_button.pack(pady=(0, 20))
    
    # Effetto hover per il pulsante
    def on_enter(e):
        ok_button['background'] = BUTTON_HOVER
    def on_leave(e):
        ok_button['background'] = BUTTON_BG
        
    ok_button.bind("<Enter>", on_enter)
    ok_button.bind("<Leave>", on_leave)
    
    # Centra la finestra e porta in primo piano
    dialog.update_idletasks()
    dialog.lift()
    dialog.focus_set()
    
    # Gestisce il tasto Escape e il pulsante di chiusura
    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
    dialog.bind("<Escape>", lambda e: dialog.destroy())


def create_tooltip(widget, text):
    """Crea un tooltip personalizzato per i widget dell'interfaccia"""
    tooltip = None
    
    def enter(event):
        nonlocal tooltip
        x, y, _, _ = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 20
        
        # Crea una finestra di tooltip
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{x}+{y}")
        
        # Frame con bordo e colore di sfondo
        frame = tk.Frame(tooltip, bg=DARK_SECONDARY, bd=1, relief="solid")
        frame.pack(ipadx=5, ipady=5)
        
        # Testo del tooltip
        label = tk.Label(frame, text=text, justify="left", bg=DARK_SECONDARY, 
                         fg=TEXT_COLOR, font=("Segoe UI", 9), wraplength=250,
                         padx=5, pady=5)
        label.pack()
    
    def leave(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
            tooltip = None
    
    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)


def open_link(url):
    """Apre un URL nel browser predefinito"""
    webbrowser.open(url)


def apply_hover_effect(button, hover_color=BUTTON_HOVER, normal_color=BUTTON_BG):
    """Applica un effetto hover ai pulsanti"""
    def on_enter(e):
        button['background'] = hover_color
    def on_leave(e):
        button['background'] = normal_color
        
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)


def update_status(status_text, status_type="info"):
    """Aggiorna la barra di stato con un messaggio e un colore appropriato"""
    if status_type == "success":
        status_color = "#4CAF50"  # Verde
        prefix = "✅ "
    elif status_type == "error":
        status_color = "#F44336"  # Rosso
        prefix = "❌ "
    elif status_type == "warning":
        status_color = "#FFC107"  # Giallo
        prefix = "⚠️ "
    elif status_type == "loading":
        status_color = "#2196F3"  # Blu
        prefix = "⏳ "
    else:  # info
        status_color = TEXT_COLOR  # Bianco
        prefix = "ℹ️ "
    
    status_bar.config(text=f"{prefix}{status_text}", fg=status_color)
    status_bar.update()


def create_custom_button(parent, text, command, tooltip_text=None, icon=None, bg=BUTTON_BG, hover_bg=BUTTON_HOVER, width=None, height=None):
    """Crea un pulsante personalizzato con stile moderno"""
    # Frame contenitore per dare effetto "rounded" al pulsante
    frame = tk.Frame(parent, background=DARK_BG)
    
    # Il pulsante vero e proprio
    button = tk.Button(frame, text=text, command=command, bg=bg, fg=TEXT_COLOR, 
                       activebackground=hover_bg, activeforeground=TEXT_COLOR,
                       bd=0, font=("Segoe UI", 10), relief="flat", 
                       width=width, height=height, compound="left")
    button.pack(padx=1, pady=1, fill="both", expand=True)
    
    # Aggiunta dell'icona se specificata
    if icon:
        button.config(image=icon, compound="left", padx=5)
    
    # Effetto hover
    apply_hover_effect(button, hover_bg, bg)
    
    # Tooltip se specificato
    if tooltip_text:
        create_tooltip(button, tooltip_text)
        
    return frame


# === Creazione della GUI ===
def create_gui():
    # Funzioni per la gestione degli eventi
    def on_search():
        """Effettua la ricerca dei match per un Riot ID."""
        game_name = entry_game_name.get().strip().lower()
        tag_line = entry_tag_line.get().strip().lower()
        if not game_name or not tag_line:
            show_custom_messagebox("Attenzione", "Inserisci un Riot ID valido!", "warning")
            return

        # Aggiorna la barra di stato
        update_status("Ricerca in corso...", "loading")
        
        # Salva il Riot ID
        save_riot_id(game_name, tag_line)

        riot_id = f"{game_name}#{tag_line}"  # Crea l'identificatore unico

        # Chiedi all'utente se vuole aggiornare o usare la cache
        use_cache = messagebox.askyesno(
            "Usa Cache?",
            "Vuoi usare i dati salvati in locale? (No per aggiornare dall'API)"
        )

        if use_cache:
            cached_matches = load_data_for_riot_id(riot_id)
            if cached_matches:
                populate_treeview(cached_matches)
                update_status(f"Caricati {len(cached_matches)} match dalla cache", "success")
            else:
                show_custom_messagebox("Info", "Nessun dato trovato nella cache.", "info")
                update_status("Nessun dato in cache", "warning")
        else:
            # Disabilita il pulsante durante la ricerca
            btn_search.config(state="disabled")
            
            def search_thread():
                nonlocal game_name, tag_line
                try:
                    puuid = get_puuid(game_name, tag_line)
                    if puuid:
                        match_ids = get_match_ids(puuid)
                        if match_ids:
                            new_matches = []
                            total_matches = len(match_ids)
                            
                            for idx, match_id in enumerate(match_ids):
                                # Aggiorna lo stato per mostrare il progresso
                                root.after(0, lambda i=idx, t=total_matches: 
                                          update_status(f"Analisi match {i+1}/{t}...", "loading"))
                                
                                match_details = get_match_details(match_id)
                                if match_details:
                                    participants = match_details.get("info", {}).get("participants", [])
                                    player_data = next((p for p in participants if p.get("puuid") == puuid), {})
                                    champion_id = player_data.get("championId", 0)
                                    champion_name = get_champion_name(champion_id)

                                    kills = player_data.get("kills", 0)
                                    deaths = player_data.get("deaths", 0)
                                    assists = player_data.get("assists", 0)

                                    queue_id = match_details.get("info", {}).get("queueId", 0)
                                    game_mode = QUEUE_ID_MAP.get(queue_id, "Sconosciuto")
                                    game_duration = match_details.get("info", {}).get("gameDuration", 0) // 60
                                    game_time = match_details.get("info", {}).get("gameStartTimestamp", 0)

                                    game_date = datetime.fromtimestamp(game_time / 1000).strftime('%Y-%m-%d %H:%M:%S')

                                    new_matches.append({
                                        "id": match_id,
                                        "mode": game_mode,
                                        "duration": f"{game_duration} min",
                                        "date": game_date,
                                        "champion": champion_name,
                                        "score": f"{kills}/{deaths}/{assists}"
                                    })

                            all_matches = add_data_for_riot_id(riot_id, new_matches)
                            
                            # Aggiorna l'interfaccia utente nel thread principale
                            root.after(0, lambda: populate_treeview(all_matches))
                            root.after(0, lambda: update_status(f"Trovati {len(all_matches)} match", "success"))
                        else:
                            root.after(0, lambda: show_custom_messagebox("Info", "Nessun match trovato per questo Riot ID.", "info"))
                            root.after(0, lambda: update_status("Nessun match trovato", "warning"))
                    else:
                        root.after(0, lambda: update_status("PUUID non trovato", "error"))
                except Exception as e:
                    root.after(0, lambda: show_custom_messagebox("Errore", f"Si è verificato un errore: {str(e)}", "error"))
                    root.after(0, lambda: update_status("Errore nella ricerca", "error"))
                finally:
                    # Riabilita il pulsante di ricerca
                    root.after(0, lambda: btn_search.config(state="normal"))
            
            # Esegui la ricerca in un thread separato per evitare il blocco dell'interfaccia
            threading.Thread(target=search_thread, daemon=True).start()

    def on_download():
        """Scarica il replay selezionato."""
        selected = tree_matches.selection()
        if selected:
            match_id = tree_matches.item(selected[0], "values")[0]
            try:
                update_status("Download in corso...", "loading")
                download_replay_gui(match_id)
                update_status("Download completato", "success")
            except Exception as e:
                show_custom_messagebox("Errore", f"Errore durante il download del replay: {e}", "error")
                update_status("Errore nel download", "error")
        else:
            show_custom_messagebox("Attenzione", "Seleziona un match da scaricare!", "warning")

    def on_watch():
        """Guarda il replay selezionato."""
        selected = tree_matches.selection()
        if selected:
            match_id = tree_matches.item(selected[0], "values")[0]
            try:
                update_status("Avvio in corso...", "loading")
                watch_replay_gui(match_id)
                update_status("Replay avviato", "success")
            except Exception as e:
                show_custom_messagebox("Errore", f"Errore durante l'avvio del replay: {e}", "error")
                update_status("Errore nell'avvio", "error")
        else:
            show_custom_messagebox("Attenzione", "Seleziona un match da guardare!", "warning")

    def apply_filter():
        """Applica i filtri e aggiorna la Treeview."""
        game_name = entry_game_name.get().strip().lower()
        tag_line = entry_tag_line.get().strip().lower()
        
        if not game_name or not tag_line:
            show_custom_messagebox("Attenzione", "Inserisci un Riot ID valido prima di filtrare!", "warning")
            return
            
        all_data = load_data_for_riot_id(f"{game_name}#{tag_line}")
        filtered_data = []

        selected_mode = filter_mode.get()
        selected_champion = filter_champion.get()
        selected_date = filter_date.get().strip()

        for match in all_data:
            if selected_mode and match["mode"] != selected_mode:
                continue
            if selected_champion and match["champion"] != selected_champion:
                continue
            if selected_date and not match["date"].startswith(selected_date):
                continue
            filtered_data.append(match)

        populate_treeview(filtered_data)
        update_status(f"Filtro applicato: {len(filtered_data)} match trovati", "info")

    def reset_filter():
        """Reimposta tutti i filtri e mostra tutti i match."""
        filter_mode.set("")
        filter_champion.set("")
        filter_date.delete(0, tk.END)
        
        game_name = entry_game_name.get().strip().lower()
        tag_line = entry_tag_line.get().strip().lower()
        
        if game_name and tag_line:
            all_data = load_data_for_riot_id(f"{game_name}#{tag_line}")
            populate_treeview(all_data)
            update_status(f"Filtri reimpostati: visualizzazione di {len(all_data)} match", "info")


    def on_select_replay():
        """Seleziona un file replay locale e avvialo."""
        # Apri il file explorer per selezionare un replay locale
        file_path = filedialog.askopenfilename(
            title="Seleziona Replay",
            filetypes=[("Replay Files", "*.rofl")],  # Filtra solo i file .rofl
            initialdir=os.path.join(os.path.expanduser("~"), "Documents", "League of Legends", "Replays")
        )
        if file_path:
            try:
                update_status("Avvio replay locale...", "loading")
                # Avvia il replay usando il percorso del file
                start_local_replay(file_path)
                update_status("Replay locale avviato", "success")
            except Exception as e:
                show_custom_messagebox("Errore", f"Errore durante l'avvio del replay locale: {e}", "error")
                update_status("Errore nell'avvio", "error")
        else:
            update_status("Nessun file selezionato", "info")

    # Funzione per avviare un replay locale
    def start_local_replay(file_path):
        """
        Avvia un replay locale specificando il percorso del file.

        Args:
            file_path (str): Percorso del file .rofl
        """
        try:
            # Usare il lockfile per inviare la richiesta al client Riot
            replay_name = os.path.basename(file_path)
            clean_replay_name = replay_name.split("-")[-1].replace(".rofl", "")
            endpoint = f"/lol-replays/v1/rofls/{clean_replay_name}/watch"
            body = {"path": file_path}

            # Invia la richiesta di avvio
            response = send_request_with_lockfile(endpoint, method="POST", data=body)
            if response.status_code == 204:
                show_custom_messagebox("Successo", "Replay locale avviato con successo!", "success")
            else:
                raise Exception(f"Errore API: {response.status_code} - {response.text}")
        except Exception as e:
            show_custom_messagebox("Errore", f"Impossibile avviare il replay locale: {e}", "error")

    def on_share_replay_to_discord():
        """Avvia un thread per condividere il replay su Discord."""
        selected = tree_matches.selection()
        if selected:
            match_id = tree_matches.item(selected[0], "values")[0]
            webhook_url = "https://discord.com/api/webhooks/1326936447130927175/PdWf5kc3CphzEloDc2jFjjFh_tA36rI4x4hfVRfgBiDEkrU6vqAvzCzzVncEwlrSN6Eb"
            
            # Mostra la finestra di progresso
            progress_window = tk.Toplevel(root)
            progress_window.title("Condivisione in corso")
            progress_window.geometry("400x150")
            progress_window.configure(bg=DARK_BG)
            progress_window.transient(root)
            progress_window.grab_set()
            progress_window.resizable(False, False)
            
            # Posiziona la finestra al centro della finestra principale
            progress_window.geometry(f"+{root.winfo_x() + (root.winfo_width() // 2) - 200}+{root.winfo_y() + (root.winfo_height() // 2) - 75}")
            
            # Etichette e barra di avanzamento
            tk.Label(progress_window, text="Caricamento del replay su Google Drive...", bg=DARK_BG, fg=TEXT_COLOR, font=("Segoe UI", 10)).pack(pady=(20, 10))
            progress_bar = ttk.Progressbar(progress_window, style="Custom.Horizontal.TProgressbar", length=350)
            progress_bar.pack(pady=10, padx=25)
            status_label = tk.Label(progress_window, text="Inizializzazione...", bg=DARK_BG, fg=TEXT_COLOR, font=("Segoe UI", 9))
            status_label.pack(pady=10)
            
            def share_replay_thread():
                try:
                    # Aggiorna lo stato
                    progress_window.after(0, lambda: status_label.config(text="Download del replay..."))
                    update_status("Condivisione in corso...", "loading")
                    
                    # Scarica il replay se necessario
                    replay_file = ensure_replay_downloaded(match_id)
                    
                    # Aggiorna lo stato
                    progress_window.after(0, lambda: status_label.config(text="Caricamento su Google Drive..."))
                    
                    # Caricamento su Google Drive
                    link = upload_to_google_drive_with_progress(replay_file, progress_bar)
                    
                    if link:
                        # Aggiorna lo stato
                        progress_window.after(0, lambda: status_label.config(text="Invio a Discord..."))
                        
                        # Condivisione su Discord
                        share_replay_link_on_discord_with_progress(match_id, link, webhook_url)
                        update_status("Replay condiviso su Discord", "success")
                    else:
                        update_status("Errore durante il caricamento", "error")
                except Exception as e:
                    progress_window.after(0, lambda: show_custom_messagebox("Errore", str(e), "error"))
                    update_status("Errore nella condivisione", "error")
                finally:
                    # Chiudi la finestra di progresso
                    progress_window.after(0, progress_window.destroy)
            
            # Avvia il caricamento in un thread separato
            threading.Thread(target=share_replay_thread, daemon=True).start()
        else:
            show_custom_messagebox("Attenzione", "Seleziona un replay da condividere!", "warning")

    def on_treeview_select(event):
        """Gestisce la selezione di un elemento nella Treeview"""
        selected = tree_matches.selection()
        if selected:
            # Abilita i pulsanti per download, visualizzazione e condivisione
            btn_download.config(state="normal")
            btn_watch.config(state="normal")
            btn_share.config(state="normal")
            
            # Ottieni e visualizza dettagli aggiuntivi nella barra di stato
            match_data = tree_matches.item(selected[0], "values")
            update_status(f"Selezionato: {match_data[4]} - {match_data[1]} - {match_data[5]}", "info")
        else:
            # Disabilita i pulsanti se nessun elemento è selezionato
            btn_download.config(state="disabled")
            btn_watch.config(state="disabled")
            btn_share.config(state="disabled")
    
    def about_dialog():
        """Mostra la finestra 'about' con informazioni sull'applicazione"""
        about = tk.Toplevel(root)
        about.title("About Replay Viewer")
        about.geometry("400x300")
        about.configure(bg=DARK_BG)
        about.transient(root)
        about.grab_set()
        about.resizable(False, False)
        
        # Logo (puoi sostituirlo con un'immagine reale)
        logo_label = tk.Label(about, text="🎮", font=("Segoe UI", 48), bg=DARK_BG, fg=RIOT_COLOR)
        logo_label.pack(pady=(20, 10))
        
        # Titolo
        title_label = tk.Label(about, text="Modern Replay Viewer", font=("Segoe UI", 16, "bold"), 
                              bg=DARK_BG, fg=TEXT_COLOR)
        title_label.pack(pady=(0, 5))
        
        # Versione
        version_label = tk.Label(about, text="Version 2.0", font=("Segoe UI", 10), 
                                bg=DARK_BG, fg=TEXT_COLOR)
        version_label.pack(pady=(0, 10))
        
        # Descrizione
        desc_label = tk.Label(about, text="Un'applicazione moderna per gestire e condividere\ni replay di League of Legends.",
                             font=("Segoe UI", 10), bg=DARK_BG, fg=TEXT_COLOR, justify="center")
        desc_label.pack(pady=(0, 20))
        
        # Pulsante OK
        ok_button = tk.Button(about, text="OK", bg=BUTTON_BG, fg=TEXT_COLOR, font=("Segoe UI", 10),
                             activebackground=BUTTON_HOVER, activeforeground=TEXT_COLOR, bd=0, width=10,
                             command=about.destroy)
        ok_button.pack(pady=(0, 20))
        
        # Effetto hover per il pulsante
        apply_hover_effect(ok_button)
        
        # Centra la finestra
        about.update_idletasks()
        x = root.winfo_x() + (root.winfo_width() // 2) - (about.winfo_width() // 2)
        y = root.winfo_y() + (root.winfo_height() // 2) - (about.winfo_height() // 2)
        about.geometry(f"+{x}+{y}")
        about.focus_set()

    global root, tree_matches, status_bar
    root = tk.Tk()
    root.title("Modern Replay Viewer")
    root.geometry("1200x700")
    root.configure(bg=DARK_BG)
    
    # Tenta di impostare un'icona (sostituisci con la tua immagine)
    try:
        icon_path = "replay_icon.ico"
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except:
        pass  # Ignora errori se l'icona non è disponibile
    
    # Configura lo stile
    style = ttk.Style()
    style.theme_use("clam")
    
    # Stile per la Treeview
    style.configure("Treeview", 
                   background=TREEVIEW_BG, 
                   foreground=TEXT_COLOR, 
                   fieldbackground=TREEVIEW_BG, 
                   rowheight=28,
                   font=("Segoe UI", 10))
    
    style.configure("Treeview.Heading", 
                   font=("Segoe UI", 10, "bold"),
                   background=DARK_SECONDARY, 
                   foreground=TEXT_COLOR)
    
    # Stile per tag personalizzati nella Treeview
    style.map("Treeview", 
             background=[("selected", TREEVIEW_SELECTED)],
             foreground=[("selected", TEXT_COLOR)])
    
    # Configurazioni tag di Treeview
    style.map("Treeview", 
             background=[("selected", TREEVIEW_SELECTED)])
    
    # Stile per i pulsanti
    style.configure("TButton", 
                   background=BUTTON_BG, 
                   foreground=TEXT_COLOR, 
                   font=("Segoe UI", 10),
                   padding=6)
    
    style.map("TButton", 
             background=[("active", BUTTON_HOVER)],
             foreground=[("active", TEXT_COLOR)])
    
    # Stile per la barra di progresso
    style.configure("Custom.Horizontal.TProgressbar",
                   troughcolor=DARK_SECONDARY,
                   background=ACCENT_COLOR,
                   thickness=15)
    
    # Stile per le combobox
    style.configure("TCombobox", 
                   fieldbackground=DARK_SECONDARY,
                   background=DARK_SECONDARY,
                   foreground=TEXT_COLOR,
                   selectbackground=TREEVIEW_SELECTED,
                   selectforeground=TEXT_COLOR,
                   insertcolor=TEXT_COLOR,
                   padding=5)
    
    style.map("TCombobox",
            fieldbackground=[("readonly", DARK_SECONDARY)],
            selectbackground=[("readonly", TREEVIEW_SELECTED)])
    
    # Frame principale diviso in sezioni
    main_frame = tk.Frame(root, bg=DARK_BG)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))
    
    # Frame superiore per il Riot ID e la barra degli strumenti
    top_frame = tk.Frame(main_frame, bg=DARK_SECONDARY, pady=10, padx=10)
    top_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Logo o icona dell'app (sostituisci con un'immagine reale)
    logo_label = tk.Label(top_frame, text="🎮", font=("Arial", 18), bg=DARK_SECONDARY, fg=RIOT_COLOR)
    logo_label.pack(side=tk.LEFT, padx=(5, 15))
    
    # Sezione per il Riot ID
    id_frame = tk.Frame(top_frame, bg=DARK_SECONDARY)
    id_frame.pack(side=tk.LEFT, padx=5)
    
    tk.Label(id_frame, text="Game Name:", bg=DARK_SECONDARY, fg=TEXT_COLOR, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5))
    entry_game_name = tk.Entry(id_frame, width=20, font=("Segoe UI", 10), bg=DARK_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
    entry_game_name.pack(side=tk.LEFT, padx=(0, 10))
    
    tk.Label(id_frame, text="Tag Line:", bg=DARK_SECONDARY, fg=TEXT_COLOR, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5))
    entry_tag_line = tk.Entry(id_frame, width=10, font=("Segoe UI", 10), bg=DARK_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
    entry_tag_line.pack(side=tk.LEFT, padx=(0, 10))
    
    # Pulsante di ricerca
    btn_search = tk.Button(top_frame, text="Cerca", command=on_search, bg=ACCENT_COLOR, fg="white", 
                         font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=5)
    btn_search.pack(side=tk.LEFT, padx=10)
    apply_hover_effect(btn_search, "#1e88e5", ACCENT_COLOR)  # Colore hover leggermente più chiaro
    
    # Pulsante About
    btn_about = tk.Button(top_frame, text="?", command=about_dialog, bg=BUTTON_BG, fg=TEXT_COLOR, 
                         font=("Segoe UI", 10, "bold"), bd=0, width=3, height=1)
    btn_about.pack(side=tk.RIGHT, padx=5)
    apply_hover_effect(btn_about)
    create_tooltip(btn_about, "Informazioni sull'applicazione")
    
    # Frame per i filtri
    filter_frame = tk.Frame(main_frame, bg=DARK_SECONDARY, pady=10, padx=10)
    filter_frame.pack(fill=tk.X, padx=5, pady=5)
    
    tk.Label(filter_frame, text="Filtra per:", bg=DARK_SECONDARY, fg=TEXT_COLOR, font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(5, 15))
    
    tk.Label(filter_frame, text="Modalità:", bg=DARK_SECONDARY, fg=TEXT_COLOR, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5))
    # Ottieni le modalità uniche dai dati
    modes = [""] + list(QUEUE_ID_MAP.values())
    filter_mode = ttk.Combobox(filter_frame, values=modes, font=("Segoe UI", 10), width=15, state="readonly")
    filter_mode.pack(side=tk.LEFT, padx=(0, 15))
    
    tk.Label(filter_frame, text="Campione:", bg=DARK_SECONDARY, fg=TEXT_COLOR, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5))
    champion_names = fetch_champion_names()
    filter_champion = ttk.Combobox(filter_frame, values=[""] + champion_names, font=("Segoe UI", 10), width=15, state="readonly")
    filter_champion.pack(side=tk.LEFT, padx=(0, 15))
    
    tk.Label(filter_frame, text="Data:", bg=DARK_SECONDARY, fg=TEXT_COLOR, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 5))
    filter_date = tk.Entry(filter_frame, width=15, font=("Segoe UI", 10), bg=DARK_BG, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
    filter_date.pack(side=tk.LEFT, padx=(0, 15))
    create_tooltip(filter_date, "Formato: YYYY-MM-DD")
    
    # Pulsanti Applica e Reimposta filtri
    btn_apply_filter = tk.Button(filter_frame, text="Applica", command=apply_filter, bg=BUTTON_BG, fg=TEXT_COLOR,
                              font=("Segoe UI", 10), bd=0, padx=10, pady=3)
    btn_apply_filter.pack(side=tk.LEFT, padx=(0, 5))
    apply_hover_effect(btn_apply_filter)
    
    btn_reset_filter = tk.Button(filter_frame, text="Reimposta", command=reset_filter, bg=BUTTON_BG, fg=TEXT_COLOR,
                               font=("Segoe UI", 10), bd=0, padx=10, pady=3)
    btn_reset_filter.pack(side=tk.LEFT)
    apply_hover_effect(btn_reset_filter)
    
    # Frame centrale con la Treeview
    center_frame = tk.Frame(main_frame, bg=DARK_BG)
    center_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Crea lo scrollbar per la Treeview
    scrollbar = ttk.Scrollbar(center_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Crea la Treeview
    global tree_matches
    tree_matches = ttk.Treeview(center_frame, 
                              columns=("id", "mode", "duration", "date", "champion", "score"),
                              show="headings",
                              yscrollcommand=scrollbar.set)
    
    # Configurazione delle colonne
    tree_matches.heading("id", text="Match ID")
    tree_matches.heading("mode", text="Modalità")
    tree_matches.heading("duration", text="Durata")
    tree_matches.heading("date", text="Data")
    tree_matches.heading("champion", text="Campione")
    tree_matches.heading("score", text="K/D/A")
    
    tree_matches.column("id", width=180, anchor=tk.W)
    tree_matches.column("mode", width=120, anchor=tk.CENTER)
    tree_matches.column("duration", width=80, anchor=tk.CENTER)
    tree_matches.column("date", width=180, anchor=tk.CENTER)
    tree_matches.column("champion", width=150, anchor=tk.CENTER)
    tree_matches.column("score", width=100, anchor=tk.CENTER)
    
    # Configura i tag personalizzati per la Treeview
    tree_matches.tag_configure("oddrow", background="#252530")
    tree_matches.tag_configure("evenrow", background=TREEVIEW_BG)
    tree_matches.tag_configure("positive", foreground="#4CAF50")  # Verde per K/D/A positivo
    tree_matches.tag_configure("negative", foreground="#F44336")  # Rosso per K/D/A negativo
    
    # Collega la barra di scorrimento
    scrollbar.config(command=tree_matches.yview)
    
    # Evento di selezione
    tree_matches.bind("<<TreeviewSelect>>", on_treeview_select)
    
    # Packing
    tree_matches.pack(fill=tk.BOTH, expand=True)
    
    # Frame inferiore con pulsanti di azione
    bottom_frame = tk.Frame(main_frame, bg=DARK_SECONDARY, pady=10, padx=10)
    bottom_frame.pack(fill=tk.X, padx=5, pady=5)
    
    # Pulsante per scaricare replay
    btn_download = tk.Button(bottom_frame, text="📥 Scarica Replay", command=on_download, 
                           bg=BUTTON_BG, fg=TEXT_COLOR, font=("Segoe UI", 10), bd=0, padx=15, pady=5,
                           state="disabled")
    btn_download.pack(side=tk.LEFT, padx=5)
    apply_hover_effect(btn_download)
    create_tooltip(btn_download, "Scarica il replay selezionato sul tuo computer")
    
    # Pulsante per guardare replay
    btn_watch = tk.Button(bottom_frame, text="▶️ Guarda Replay", command=on_watch,
                        bg=RIOT_COLOR, fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=5,
                        state="disabled")
    btn_watch.pack(side=tk.LEFT, padx=5)
    apply_hover_effect(btn_watch, "#C62828", RIOT_COLOR)  # Colore hover leggermente più scuro
    create_tooltip(btn_watch, "Avvia il replay selezionato in League of Legends")
    
    # Pulsante per aprire replay locale
    btn_local = tk.Button(bottom_frame, text="📂 Replay Locale", command=on_select_replay,
                        bg=BUTTON_BG, fg=TEXT_COLOR, font=("Segoe UI", 10), bd=0, padx=15, pady=5)
    btn_local.pack(side=tk.LEFT, padx=5)
    apply_hover_effect(btn_local)
    create_tooltip(btn_local, "Seleziona e avvia un file di replay locale")
    
    # Pulsante per condividere su Discord
    btn_share = tk.Button(bottom_frame, text="🔗 Condividi su Discord", command=on_share_replay_to_discord,
                        bg=DISCORD_COLOR, fg="white", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=5,
                        state="disabled")
    btn_share.pack(side=tk.LEFT, padx=5)
    apply_hover_effect(btn_share, "#4752C4", DISCORD_COLOR)  # Colore hover leggermente più scuro
    create_tooltip(btn_share, "Carica e condividi il replay selezionato su Discord")
    
    # Barra di stato
    status_frame = tk.Frame(root, bg=DARK_SECONDARY, height=25)
    status_frame.pack(fill=tk.X, side=tk.BOTTOM)
    
    status_bar = tk.Label(status_frame, text="Pronto", bg=DARK_SECONDARY, fg=TEXT_COLOR, 
                         font=("Segoe UI", 9), anchor=tk.W, padx=10, pady=5)
    status_bar.pack(fill=tk.X)
    
    # Carica il Riot ID salvato
    saved_game_name, saved_tag_line = load_riot_id()
    if saved_game_name and saved_tag_line:
        entry_game_name.insert(0, saved_game_name)
        entry_tag_line.insert(0, saved_tag_line)
        update_status(f"ID caricato: {saved_game_name}#{saved_tag_line}", "info")
    
    
    
    # Focalizza il primo campo se vuoto, altrimenti il pulsante di ricerca
    if not saved_game_name:
        entry_game_name.focus_set()
    else:
        btn_search.focus_set()

    root.mainloop()
    

if __name__ == "__main__":
        
    create_gui()
        