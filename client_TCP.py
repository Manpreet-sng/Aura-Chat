import socket
import datetime
import xml.etree.ElementTree as ET
import os

def log_message(mittente, ip, contenuto, filename="log_client.xml"):
    """Funzione per loggare messaggi in formato XML"""
    
    # Se il file non esiste o è vuoto → inizializza XML
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        root = ET.Element("logs")
        tree = ET.ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)

    # Ora il file ESISTE ed è valido → parse OK
    tree = ET.parse(filename)
    root = tree.getroot()

    message = ET.SubElement(root, "message")

    ET.SubElement(message, "timestamp").text = \
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ET.SubElement(message, "sender").text = mittente
    ET.SubElement(message, "ip").text = ip
    ET.SubElement(message, "contenuto").text = contenuto

    ET.indent(tree, space="    ", level=0)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

def generate_html_log():
    """Genera un file HTML con i log colorati del CLIENT"""
    log_file = "log_client.xml"
    html_file = "log_client.html"
    
    if not os.path.exists(log_file):
        return
    
    tree = ET.parse(log_file)
    root = tree.getroot()
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Client Log</title>
    <style>
        body { font-family: 'Courier New', monospace; background-color: #1e1e1e; color: #d4d4d4; padding: 20px; }
        .log-entry { margin: 15px 0; padding: 10px; border-left: 4px solid; }
        .log-entry.client { border-color: #4FC3F7; background-color: #2d3d4d; }
        .log-entry.server { border-color: #81C784; background-color: #2d3d2d; }
        .field { margin: 5px 0; }
        .label { font-weight: bold; color: #FFB74D; }
        .timestamp { color: #CE93D8; }
        .sender { color: #4FC3F7; }
        .ip { color: #FFB74D; }
        .contenuto { color: #d4d4d4; }
        h1 { color: #4FC3F7; }
    </style>
</head>
<body>
    <h1>📋 Client Log</h1>
"""
    
    for message in root.findall("message"):  # ← CORRETTO: cerca "message", non "log_entry"
        sender = message.find("sender").text
        status_class = "client" if sender == "CLIENT" else "server"
        
        html_content += f'    <div class="log-entry {status_class}">\n'
        html_content += f'        <div class="field"><span class="label">TIMESTAMP:</span> <span class="timestamp">{message.find("timestamp").text}</span></div>\n'
        html_content += f'        <div class="field"><span class="label">SENDER:</span> <span class="sender">{sender}</span></div>\n'
        html_content += f'        <div class="field"><span class="label">IP:</span> <span class="ip">{message.find("ip").text}</span></div>\n'
        html_content += f'        <div class="field"><span class="label">CONTENUTO:</span> <span class="contenuto">{message.find("contenuto").text}</span></div>\n'
        html_content += '    </div>\n'
    
    html_content += """</body>
</html>"""
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

# Creazione del socket client
CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connessione al server (IP localhost e porta 12345)
CLIENT.connect(("127.0.0.1", 12345))
print("Connesso al server!")

while True:
    # Invio di messaggi al server
    mess = input("[CLIENT] --> Inserisci un messaggio da inviare: ")
    CLIENT.send(mess.encode())
    
    # Log del messaggio inviato dal client
    log_message(mittente="CLIENT", ip="127.0.0.1", contenuto=mess)
    generate_html_log()
    
    # Ricezione risposta del server
    data = CLIENT.recv(1024).decode()

    # Chiusura del client se il server risponde con -1
    if data == "-1":
        print("[SERVER] --> Disconnessione richiesta dal server")
        CLIENT.close()
        break

    # Stampa e log della risposta del server
    print(f"[SERVER] --> {data}")
    log_message(mittente="SERVER", ip="127.0.0.1", contenuto=data)
    generate_html_log()