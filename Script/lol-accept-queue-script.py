import requests
import urllib3
import time
import json
import os
import base64
import psutil
import sys
import logging
from datetime import datetime

# Per le notifiche Windows
try:
    from win10toast import ToastNotifier
    toast = ToastNotifier()
    notifications_available = True
except ImportError:
    notifications_available = False
    print("Pacchetto win10toast non trovato. Le notifiche non saranno disponibili.")
    print("Per abilitare le notifiche, eseguire: pip install win10toast")

# Configurazione logging
logging.basicConfig(
    filename='lol_accept_queue.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Disabilita gli avvisi SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def show_notification(title, message, duration=5):
    """Mostra una notifica di Windows"""
    if notifications_available:
        try:
            toast.show_toast(
                title,
                message,
                duration=duration,
                icon_path=None,
                threaded=True
            )
        except Exception as e:
            logging.error(f"Errore durante la visualizzazione della notifica: {e}")
    else:
        logging.info(f"Notifica non visualizzata (win10toast non installato): {title} - {message}")

def is_lol_client_running():
    """Verifica se il client di LoL è in esecuzione"""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == "LeagueClientUx.exe":
            return True
    return False

def get_lcu_port_and_token():
    """Ottiene porta e token di autenticazione dal processo del client LoL"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        if proc.info['name'] == "LeagueClientUx.exe":
            try:
                cmdline = proc.info['cmdline']
                port = None
                auth_token = None
                
                for param in cmdline:
                    if "--app-port=" in param:
                        port = param.split("=")[1]
                    if "--remoting-auth-token=" in param:
                        auth_token = param.split("=")[1]
                
                if port and auth_token:
                    return port, auth_token
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    return None, None

def main():
    print(f"LoL Auto Accept Queue - Avviato il {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info("Script avviato")
    
    show_notification(
        "LoL Auto Accept",
        "Avvio del monitoraggio del client LoL...",
        duration=4
    )

    client_was_running = False
    
    # Verifica iniziale se il client è già in esecuzione
    if not is_lol_client_running():
        print("Client LoL non rilevato. In attesa che venga avviato...")
        logging.info("Client LoL non rilevato all'avvio")
    
    while True:
        # Verifica se il client è in esecuzione
        if not is_lol_client_running():
            if client_was_running:
                print("Client LoL è stato chiuso. In attesa del riavvio...")
                logging.info("Client LoL chiuso")
                client_was_running = False
            
            print("Client LoL non in esecuzione. Controllo ogni 60 secondi...")
            time.sleep(60)
            continue
        
        # Se il client è stato appena avviato, mostra una notifica
        if not client_was_running:
            show_notification(
                "LoL Auto Accept",
                "Client LoL rilevato! Monitoraggio partite avviato.",
                duration=4
            )
            client_was_running = True
        
        # Il client è in esecuzione, ottieni porta e token
        port, auth_token = get_lcu_port_and_token()
        if not port or not auth_token:
            print("Client LoL rilevato ma impossibile ottenere le credenziali. Riprovo tra 5 secondi...")
            logging.warning("Client rilevato ma impossibile ottenere le credenziali")
            time.sleep(5)
            continue
        
        print("Client LoL rilevato! Connessione alle API LCU...")
        logging.info("Client LoL rilevato e connesso")
        
        # Configurazione delle richieste HTTP
        base_url = f"https://127.0.0.1:{port}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Basic {base64.b64encode(f'riot:{auth_token}'.encode()).decode()}"
        }
        
        # Variabili per tracciare lo stato precedente
        previous_state = None
        
        # Loop principale per il monitoraggio quando il client è attivo
        active_monitoring = True
        while active_monitoring:
            try:
                # Verifica se il client è ancora in esecuzione
                if not is_lol_client_running():
                    print("Client LoL è stato chiuso. In attesa del riavvio...")
                    logging.info("Client LoL chiuso")
                    active_monitoring = False
                    break
                
                # Ottieni lo stato attuale del gameflow
                gameflow_response = requests.get(f"{base_url}/lol-gameflow/v1/gameflow-phase", headers=headers, verify=False)
                
                if gameflow_response.status_code == 200:
                    gameflow_state = gameflow_response.json()
                    
                    # Debug - Mostra lo stato attuale
                    print(f"Stato attuale: {gameflow_state}")
                    
                    # Traccia i cambiamenti di stato nel log
                    if previous_state != gameflow_state:
                        logging.info(f"Cambio di stato: {previous_state} -> {gameflow_state}")
                        previous_state = gameflow_state
                    
                    # Imposta l'intervallo di controllo in base allo stato
                    if gameflow_state == "Matchmaking":
                        check_interval = 0.5  # 0.5 secondi quando in coda
                        print("In coda - Controllo ogni 0.5 secondi...")
                    else:
                        check_interval = 5  # 5 secondi quando non in coda
                        if gameflow_state != "ReadyCheck":  # Evita di mostrare questo durante il ReadyCheck
                            print(f"Non in coda ({gameflow_state}) - Controllo ogni 5 secondi...")
                    
                    # Verifica se siamo in ReadyCheck
                    if gameflow_state == "ReadyCheck":
                        print("Match trovato! Accettando...")
                        logging.info("Match trovato - Accettando")
                        
                        # Accetta la partita
                        accept_response = requests.post(f"{base_url}/lol-matchmaking/v1/ready-check/accept", headers=headers, verify=False)
                        if accept_response.status_code == 204:
                            print("Partita accettata con successo!")
                            logging.info("Partita accettata con successo")
                        else:
                            print(f"Errore nell'accettare la partita: {accept_response.status_code}")
                            logging.error(f"Errore nell'accettare la partita: {accept_response.status_code}")
                
                else:
                    print(f"Errore nella richiesta dello stato: {gameflow_response.status_code}")
                    logging.error(f"Errore nella richiesta dello stato: {gameflow_response.status_code}")
                    check_interval = 5
            
            except requests.exceptions.RequestException as e:
                print(f"Errore di connessione al client: {e}")
                logging.error(f"Errore di connessione al client: {e}")
                check_interval = 5
                
                # Verifica se il client è ancora in esecuzione
                if not is_lol_client_running():
                    print("Client LoL è stato chiuso. In attesa del riavvio...")
                    logging.info("Client LoL chiuso dopo errore di connessione")
                    active_monitoring = False
                    break
            
            # Pausa tra le verifiche con intervallo dinamico
            time.sleep(check_interval)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nScript interrotto manualmente. Chiusura in corso...")
        logging.info("Script interrotto manualmente")
        sys.exit(0)
    except Exception as e:
        print(f"Errore imprevisto: {e}")
        logging.critical(f"Errore imprevisto: {e}", exc_info=True)
        sys.exit(1)