import requests
import base64
import time
import threading
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import logging
import datetime
from dotenv import load_dotenv
import json
import os

env_path = r"C:\Users\dbait\Desktop\MOD LOL\script\API.emv"  # Modifica con il percorso corretto del file .emv
load_dotenv(env_path)
api_key = os.getenv("RIOT_API_KEY")

# Disabilita gli avvisi di certificato
urllib3.disable_warnings(InsecureRequestWarning)

running = False

# Percorso del lockfile
LOCKFILE_PATH = r"C:\Riot Games\League of Legends\lockfile"

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S"
)

def log_message(message):
    """Esegue il log di un messaggio."""
    logging.info(message)

class RiotAPIError(Exception):
    """Eccezione personalizzata per errori nell'API Riot."""
    pass


def get_lockfile_data():
    """Legge i dati dal lockfile di Riot Client."""
    try:
        with open(LOCKFILE_PATH, 'r') as f:
            data = f.read().split(':')
        return {
            'name': data[0],
            'pid': data[1],
            'port': data[2],
            'password': data[3],
            'protocol': data[4]
        }
    except FileNotFoundError:
        raise RiotAPIError("Il file lockfile non è stato trovato.")
    except Exception as e:
        raise RiotAPIError(f"Errore nella lettura del lockfile: {e}")


def get_authenticated_headers(endpoint):
    """Genera URL e header autenticati per l'API Riot."""
    lockfile_data = get_lockfile_data()
    port = lockfile_data['port']
    password = lockfile_data['password']
    protocol = lockfile_data['protocol']
    url = f"{protocol}://127.0.0.1:{port}{endpoint}"
    auth = f"riot:{password}"
    encoded_auth = base64.b64encode(auth.encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json'
    }
    return url, headers


def send_request(endpoint, method="GET", data=None):
    """Invia una richiesta HTTP autenticata."""
    url, headers = get_authenticated_headers(endpoint)
    try:
        if method == "POST":
            response = requests.post(url, headers=headers, json=data, verify=False)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, verify=False)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, verify=False)
        else:  # Default to GET
            response = requests.get(url, headers=headers, verify=False)

        response.raise_for_status()  # Solleva eccezione per codici di errore HTTP
        return response
    except requests.exceptions.RequestException as e:
        raise RiotAPIError(f"Errore di rete: {e}")


def create_normal_lobby(queue_id):
    """Crea una lobby normale."""
    data = {'queueId': queue_id}
    send_request("/lol-lobby/v2/lobby", method="POST", data=data)


def create_custom_lobby(game_mode, lobby_name, lobby_password):
    """Crea una lobby personalizzata."""
    # Verifica degli input
    if not game_mode:
        raise ValueError("Errore: Il parametro 'game_mode' è obbligatorio.")
    
    data = {
        "customGameLobby": {
            "configuration": {
                "gameMode": game_mode,
                "gameMutator": "",
                "gameServerRegion": "",
                "mapId": 11,  # ID mappa per "Landa degli evocatori"
                "mutators": {"id": 1},  # Mutatore predefinito
                "spectatorPolicy": "AllAllowed",  # Spettatori consentiti
                "teamSize": 5  # Dimensione della squadra
            },
            "lobbyName": lobby_name if lobby_name else f"{game_mode} Lobby",
            "lobbyPassword": lobby_password if lobby_password else None
        },
        "isCustom": True
    }

    try:
        response = send_request("/lol-lobby/v2/lobby", method="POST", data=data)

        # Controllo del risultato della richiesta
        if response.status_code == 200:
            return f"Lobby personalizzata '{lobby_name}' creata con successo."
        else:
            error_message = f"Errore: {response.status_code} - {response.text}"
            raise RiotAPIError(error_message)

    except RiotAPIError as e:
        raise RiotAPIError(f"Errore API durante la creazione della lobby personalizzata: {e}")

    except Exception as e:
        raise Exception(f"Errore sconosciuto durante la creazione della lobby: {e}")


def set_position_preferences(primary_role, secondary_role):
    """Imposta i ruoli preferiti."""
    data = {
        "firstPreference": primary_role,
        "secondPreference": secondary_role
    }
    response = send_request("/lol-lobby/v1/lobby/members/localMember/position-preferences", method="PUT", data=data)
    if response.status_code in [204, 201]:
        return f"Ruoli aggiornati con successo"
    else:
        error_message = f"Errore: {response.status_code } - {response.text}"
        raise RiotAPIError(error_message)
    

def start_queue():
    """Avvia la coda."""
    response = send_request("/lol-lobby/v2/lobby/matchmaking/search", method="POST")
    if response and (response.status_code == 200 or response.status_code == 204):
        start_monitoring()


def stop_queue():
    """Ferma la coda."""
    response = send_request("/lol-lobby/v2/lobby/matchmaking/search", method="DELETE")
    if response and (response.status_code == 200 or response.status_code == 204):
        stop_monitoring()

def is_champion_select():
    """Verifica se il gioco è in fase di champion select."""
    try:
        send_request("/lol-champ-select/v1/session")
        return True
    except RiotAPIError:
        return False


def accept_ready_check():
    """Accetta automaticamente il ready check."""
    try:
        send_request("/lol-matchmaking/v1/ready-check/accept", method="POST")
        log_message("Ready check accettato con successo!")
    except RiotAPIError as e:
        if "404" in str(e):
            log_message("Errore: Il ready check non è attivo al momento.")
        else:
            log_message(f"Errore nell'accettare il ready check: {e}")
    except Exception as e:
        log_message(f"Errore sconosciuto nell'accettare il ready check: {e}")


def monitor_ready_check():
    """Monitora il ready check e accetta automaticamente."""
    global running
    running = True  # Imposta lo stato di monitoraggio attivo

    while running:
        try:
            # Verifica se sei in champion select
            if is_champion_select():
                log_message("Sei in champion select. Monitoraggio interrotto.")
                stop_monitoring()  # Interrompi il monitoraggio
                break
            # Verifica se il ready check è attivo
            if is_ready_check_active():
                log_message("Ready check trovato, accettazione in corso...")
                accept_ready_check()
            else:
                log_message("Ready check non attivo, continuazione del monitoraggio...")
            
            time.sleep(1)  # Attendi 1 secondo prima di ricontrollare
        except Exception as e:
            log_message(f"Errore durante il monitoraggio: {e}")
            stop_monitoring()
            break


def is_ready_check_active():
    """Verifica se il ready check è attivo."""
    try:
        response = send_request("/lol-matchmaking/v1/ready-check", method="GET")
        return response.status_code == 200  # Ready check attivo se l'endpoint risponde
    except RiotAPIError as e:
        if "404" in str(e):  # Endpoint non trovato = ready check non attivo
            return False
        raise  # Propaga altri errori


def start_monitoring():
    """Avvia il monitoraggio per accettare automaticamente i ready check."""
    global running
    if not running:
        running = True
        threading.Thread(target=monitor_ready_check, daemon=True).start()
        return "Monitoraggio avviato per accettare automaticamente i ready check."
    return "Il monitoraggio è già attivo."


def stop_monitoring():
    """Ferma il monitoraggio del ready check."""
    global running
    running = False
    return "Monitoraggio interrotto."

def get_friendlist():
    lockfile_data = get_lockfile_data()
    if not lockfile_data:
        print("Impossibile ottenere i dati dal lockfile.")
        return None

    port = lockfile_data['port']
    password = lockfile_data['password']
    protocol = lockfile_data['protocol']
    
    url = f"{protocol}://127.0.0.1:{port}/lol-store/v1/giftablefriends"
    auth = f"riot:{password}"
    encoded_auth = base64.b64encode(auth.encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': f'Basic {encoded_auth}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Errore nel recupero della friendlist: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"Errore durante la richiesta: {str(e)}")
        return None

# Funzione per aggiungere il tag "recent" (amici aggiunti recentemente)
def apply_recent_tag(data, now):
    for friend in data:
        friends_since = friend.get('friendsSince', 'Sconosciuto')

        if friends_since != 'Sconosciuto':
            try:
                date_added = datetime.datetime.strptime(friends_since, "%Y-%m-%d %H:%M:%S")
                added_recently = (now - date_added).days < 7  # Amici aggiunti negli ultimi 7 giorni
            except ValueError:
                date_added = "Sconosciuto"
                added_recently = False
        else:
            date_added = "Sconosciuto"
            added_recently = False

        friend['added_recently'] = added_recently  # Aggiungi una chiave per memorizzare lo stato 'recent'

    return data

def get_account_info(lockfile_data):
    """Ottiene le informazioni sull'account tramite l'API di Riot."""
    try:
        port = lockfile_data['port']
        password = lockfile_data['password']
        protocol = lockfile_data['protocol']
        url = f"{protocol}://127.0.0.1:{port}/lol-summoner/v1/current-summoner"
        auth_header = base64.b64encode(f"riot:{password}".encode('utf-8')).decode('utf-8')
        headers = {
            "Authorization": f"Basic {auth_header}"
        }
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()  # Solleva un'eccezione per errori HTTP
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Errore nella richiesta HTTP: {e}")
        raise requests.exceptions.RequestException(f"Errore nella richiesta: {e}")
    except ValueError:
        logging.error("Risposta non valida dal server.")
        raise ValueError("Risposta non valida dal server.")
    

def get_puuid_by_riot_id(game_name, tag_line, api_key, region="europe"):
    """Ottiene il PUUID dato gameName e tagLine."""
    url = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
    headers = {'X-Riot-Token': api_key}

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Solleva eccezioni per errori HTTP
    return response.json().get("puuid")


def get_champion_mastery(puuid, api_key, region="euw1"):
    """Ottiene le maestrie dei campioni dato il PUUID."""
    url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
    headers = {'X-Riot-Token': api_key}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_versions():
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def get_champion_data(version=None, locale="it_IT"):
    if version is None:
        version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json").json()[0]
    url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/{locale}/champion.json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()['data']


def get_balance():
    """Recupera il bilancio delle valute del client Riot."""
    endpoint = "/lol-inventory/v1/wallet/signed"  # Endpoint corretto
    response = send_request(endpoint)
    return response.json()

def get_current_ranked_stats():
    """
    Recupera le statistiche attuali del rango del giocatore.
    """
    endpoint = "/lol-ranked/v1/current-ranked-stats"
    try:
        response = send_request(endpoint, method="GET")
        return response.json()  # Restituisce i dati come JSON
    except RiotAPIError as e:
        raise RiotAPIError(f"Errore durante il recupero delle statistiche del rango: {e}")
    except Exception as e:
        raise Exception(f"Errore sconosciuto durante il recupero delle statistiche del rango: {e}")
