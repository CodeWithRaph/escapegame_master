#!/usr/bin/env python3
import subprocess
import os
import sys

CONFIG_FILE = "vnc_hosts.conf"

# Crée le fichier de config s'il n'existe pas
if not os.path.exists(CONFIG_FILE):
    open(CONFIG_FILE, "w").close()

def load_hosts():
    hosts = []
    with open(CONFIG_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and ":" in line:
                name, ip = line.split(":", 1)
                hosts.append((name.strip(), ip.strip()))
    return hosts

def save_host(name, ip):
    with open(CONFIG_FILE, "a") as f:
        f.write(f"{name}:{ip}\n")

def vnc_connect(ip):
    print(f"Connexion à {ip}...")
    env = os.environ.copy()
    env["DISPLAY"] = ":0"
    env["XAUTHORITY"] = "/home/qamu/.Xauthority"

    subprocess.Popen([
        "vncviewer",
        f"{ip}:5900",
        "-Fullscreen",
        "-PreferredEncoding", "raw",
        "-CompressLevel", "1",
        "-QualityLevel", "4",
        "-AcceptClipboard", "0",
        "-SendClipboard", "0",
	"-RemoteResize", "0"
    ], env=env)

def list_hosts():
    hosts = load_hosts()
    if not hosts:
        print("Aucun serveur enregistré.")
        return
    print("\n=== Serveurs VNC ===")
    for i, (name, ip) in enumerate(hosts, start=1):
        print(f"{i}) {name} ({ip})")

def add_host():
    name = input("Nom du serveur : ").strip()
    ip = input("IP du serveur : ").strip()
    save_host(name, ip)
    print("Serveur ajouté !")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 script.py {list|connect|add|manual} [paramètres]")
        sys.exit(1)

    option = sys.argv[1]

    if option == "list":
        list_hosts()

    elif option == "connect":
        hosts = load_hosts()
        if len(sys.argv) < 3:
            print("Usage: python3 script.py connect <numéro_du_serveur>")
            sys.exit(1)
        try:
            index = int(sys.argv[2]) - 1
            if 0 <= index < len(hosts):
                vnc_connect(hosts[index][1])
            else:
                print("Numéro de serveur invalide.")
        except ValueError:
            print("Numéro de serveur invalide.")

    elif option == "add":
        add_host()

    elif option == "manual":
        if len(sys.argv) < 3:
            print("Usage: python3 script.py manual <ip>")
            sys.exit(1)
        ip = sys.argv[2]
        vnc_connect(ip)

    else:
        print("Option inconnue. Choisissez list, connect, add ou manual.")

if __name__ == "__main__":
    main()
