import socket
import datetime
import xml.etree.ElementTree as ET
import os

def log_message(mittente, ip, contenuto, filename="log_server.xml"):
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
    """Genera un file HTML con i log colorati del SERVER"""
    log_file = "log_server.xml"
    html_file = "log_server.html"
    
    if not os.path.exists(log_file):
        return
    
    tree = ET.parse(log_file)
    root = tree.getroot()
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Server Log</title>
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
        h1 { color: #81C784; }
    </style>
</head>
<body>
    <h1>🖥️ Server Log</h1>
"""
    
    for message in root.findall("message"):  # ← QUESTO ERA IL PROBLEMA: cercava "log_entry" invece di "message"
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

# Creazione del socket TCP (IPv4 + TCP)
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind su IP e porta (0.0.0.0 = accetta da tutte le interfacce)
SERVER.bind(("0.0.0.0", 12345))

# Mettere il server in ascolto
SERVER.listen(5) # Numero di connessioni ammesse
print("Server in ascolto sulla porta 12345...")

# Attesa di una connessione da parte del client
client_socket, client_address = SERVER.accept()
print(f"Connessione da {client_address}")

# Permette l'invio di più messaggi
while True:
    # Ricezione messaggio dal client
    data = client_socket.recv(1024).decode()
    print(f"Messaggio ricevuto: {data}")

    # Log del messaggio RICEVUTO dal client (mittente=CLIENT)
    log_message(mittente="CLIENT", ip=client_address[0], contenuto=data)
    generate_html_log()
    
    # Comandi (TIME, NAME, CIAO, EXIT)
    if data.upper() == "EXIT":
        risposta = "-1"
        client_socket.send(risposta.encode())
        log_message(mittente="SERVER", ip=client_address[0], contenuto=risposta)
        generate_html_log()

        break
    elif data.upper() == "TIME":
        time = datetime.datetime.now()
        risposta = f"{time.hour}.{time.minute}"
        client_socket.send(risposta.encode())
        log_message(mittente="SERVER", ip=client_address[0], contenuto=risposta)
        generate_html_log()

    elif data.upper() == "NAME":
        risposta = f"Sono il server: {socket.gethostname()}"
        client_socket.send(risposta.encode())
        log_message(mittente="SERVER", ip=client_address[0], contenuto=risposta)
        generate_html_log()

    else: 
        risposta = f"Ciao {client_address[0]}, ho ricevuto il tuo messaggio!"
        client_socket.send(risposta.encode())
        log_message(mittente="SERVER", ip=client_address[0], contenuto=risposta)
        generate_html_log()
   
# Chiusura connessione con il client
client_socket.close()
print(f"Chiusura del server effettuata correttamente!")