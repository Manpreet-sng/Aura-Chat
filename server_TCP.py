import socket
import threading
import datetime
import xml.etree.ElementTree as ET
import os
import csv

HOST = "0.0.0.0"
PORT = 12345

clients = {}
lock = threading.Lock()

LOG_FILE = "log_server.xml"

HELP_TEXT = """
================= AURACHAT COMMANDS =================
TIME                     -> Server current time
NAME                     -> Server name
EXIT                     -> Disconnect client
LOG                      -> Receive server logs
INFO                     -> Show INFO types
INFO 1                   -> Number of connected clients
INFO 2                   -> Number of users in DB
INFO 3                   -> Server network info
INFO 4                   -> Client network info
INFO 5                   -> Users available for chat
USERSLIST                -> List all connected users
CHAT [USER_ID]           -> Open chat with user
EX xml [n] [ALL|CLIENT|SERVER]
EX csv [n] [ALL|CLIENT|SERVER]
EX txt [n] [ALL|CLIENT|SERVER]
HELP                     -> Show this menu
=====================================================
"""


# ---------- LOGGING ----------
def log_message(sender, ip, content):
    if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
        root = ET.Element("logs")
        ET.ElementTree(root).write(LOG_FILE, encoding="utf-8", xml_declaration=True)

    tree = ET.parse(LOG_FILE)
    root = tree.getroot()

    msg = ET.SubElement(root, "message")
    ET.SubElement(msg, "timestamp").text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ET.SubElement(msg, "sender").text = sender
    ET.SubElement(msg, "ip").text = ip
    ET.SubElement(msg, "contenuto").text = content

    ET.indent(tree)
    tree.write(LOG_FILE, encoding="utf-8", xml_declaration=True)


# ---------- EXPORT ----------
def export_logs(fmt, number=None, who="ALL"):
    tree = ET.parse(LOG_FILE)
    messages = tree.getroot().findall("message")

    if who != "ALL":
        messages = [m for m in messages if m.find("sender").text == who]

    if number:
        messages = messages[-number:]

    if fmt == "xml":
        ET.ElementTree(tree.getroot()).write("export_server.xml", encoding="utf-8")
        return "export_server.xml created"

    if fmt == "txt":
        with open("export_server.txt", "w") as f:
            for m in messages:
                f.write(m.find("contenuto").text + "\n")
        return "export_server.txt created"

    if fmt == "csv":
        with open("export_server.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "sender", "ip", "contenuto"])
            for m in messages:
                writer.writerow([
                    m.find("timestamp").text,
                    m.find("sender").text,
                    m.find("ip").text,
                    m.find("contenuto").text
                ])
        return "export_server.csv created"


# ---------- CLIENT HANDLER ----------
def handle_client(sock, addr, uid):
    log_message("SERVER", addr[0], f"{uid} connected")

    while True:
        try:
            data = sock.recv(4096).decode()
            if not data:
                break

            log_message("CLIENT", addr[0], data)
            parts = data.split()
            cmd = parts[0].upper()

            if cmd == "EXIT":
                sock.send("-1".encode())
                break

            elif cmd == "TIME":
                reply = datetime.datetime.now().strftime("%H:%M:%S")

            elif cmd == "NAME":
                reply = socket.gethostname()

            elif cmd == "HELP":
                reply = HELP_TEXT

            elif cmd == "LOG":
                reply = open(LOG_FILE).read()

            elif cmd == "INFO":
                if len(parts) == 1:
                    reply = "INFO types: 1-5"
                elif parts[1] == "1":
                    reply = f"Connected clients: {len(clients)}"
                elif parts[1] == "2":
                    reply = "Users in DB: simulated"
                elif parts[1] == "3":
                    reply = socket.gethostbyname(socket.gethostname())
                elif parts[1] == "4":
                    reply = addr[0]
                elif parts[1] == "5":
                    reply = ", ".join(clients.keys())
                else:
                    reply = "Invalid INFO type"

            elif cmd == "USERSLIST":
                reply = "Users: " + ", ".join(clients.keys())

            elif cmd == "CHAT" and len(parts) > 1:
                reply = "Chat system ready (basic)"

            elif cmd == "EX":
                fmt = parts[1]
                num = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
                who = parts[3] if len(parts) > 3 else "ALL"
                reply = export_logs(fmt, num, who)

            else:
                reply = f"Unknown command. Type HELP."

            sock.send(reply.encode())
            log_message("SERVER", addr[0], reply)

        except:
            break

    with lock:
        if uid in clients:
            del clients[uid]

    sock.close()
    log_message("SERVER", addr[0], f"{uid} disconnected")


# ---------- SERVER ----------
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SERVER.bind((HOST, PORT))
SERVER.listen(5)

print("AuraChat Server running...")

user_id = 1
while True:
    client_socket, client_address = SERVER.accept()
    uid = f"USER{user_id}"
    user_id += 1

    with lock:
        clients[uid] = client_socket

    threading.Thread(target=handle_client, args=(client_socket, client_address, uid)).start()
