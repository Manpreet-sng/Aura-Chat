import socket
import datetime
import xml.etree.ElementTree as ET
import os

LOG_FILE = "log_client.xml"

MENU = """
================= AURACHAT MENU =================
Type one of the following commands:

TIME
NAME
INFO
INFO 1
INFO 2
INFO 3
INFO 4
INFO 5
USERSLIST
CHAT [USER_ID]
LOG
EX xml [n] [ALL|CLIENT|SERVER]
EX csv [n] [ALL|CLIENT|SERVER]
EX txt [n] [ALL|CLIENT|SERVER]
HELP
EXIT
===============================================
"""


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


CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CLIENT.connect(("127.0.0.1", 12345))

print("Connected to AuraChat Server")
print(MENU)

while True:
    cmd = input("[CLIENT] > ")

    CLIENT.send(cmd.encode())
    log_message("CLIENT", "127.0.0.1", cmd)

    response = CLIENT.recv(8192).decode()

    if response == "-1":
        print("Disconnected from server")
        break

    print("\n[SERVER RESPONSE]")
    print(response)
    print()

    log_message("SERVER", "127.0.0.1", response)

CLIENT.close()
