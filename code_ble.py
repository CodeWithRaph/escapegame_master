from flask import Flask, render_template, jsonify, redirect
import asyncio
import subprocess
import random
import state
import time
from bleak import BleakClient, BleakScanner
import os
from fabric import Connection

SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
CHAR_UUID_NOTIFY = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
CHAR_UUID_WRITE = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

def connection_ssh(commande, ip) :
    ssh = Connection(
        host=ip,
        user="robin",
        connect_kwargs={"key_filename":"/home/qamu/.ssh/id_rsa"} #/!\ attention parfois il y a une confution de clée rsa et dsa par paremiko /!\
        )
    ssh.run(commande)
def update_state(**updates):
    state_data = {}

    # Lire l'état existant
    if os.path.exists("state.py"):
        with open("state.py", "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.split("=", 1)
                    state_data[key.strip()] = value.strip()

    # Appliquer les mises à jour
    for key, value in updates.items():
        if isinstance(value, str):
            state_data[key] = f'"{value}"'
        else:
            state_data[key] = str(value)

    # Réécrire le fichier
    with open("state.py", "w") as f:
        for key, value in state_data.items():
            f.write(f"{key} = {value}\n")


PAGE_MAP = {
    "START": "/contexte",
    "GO": "/etape1",
    "9471": "/etape2",
    "6013": "/etape3",
    "4455": "/ending",
}

async def notification_handler(sender, data, client):
    message = data.decode("utf-8").strip()
    print(f" Signal reçu : {message}")

    # Cas erreur avec code 6013
    if "6013" in message:
        parts = message.split("6013", 1)
        erreur = parts[1] if len(parts) > 1 else 0

        update_state(
            current_page="/etape3",
            erreur=erreur
        )

    elif message == "-FFFF":
        connection_ssh('sudo systemctl stop x11vnc-display1.service', "192.168.1.2")
        connection_ssh('sudo systemctl stop firefox-sae.service', "192.168.1.2")
        print("ok")
    elif message == "FFFF":
        connection_ssh('sudo systemctl start x11vnc-display1.service', "192.168.1.2")
        connection_ssh('sudo systemctl start firefox-sae.service', "192.168.1.2")
        subprocess.run("python3 ../script.py connect 1 &", shell=True)
        update_state(
            current_page="/",
            crono_debut=0,
            crono_fin=0,
            erreur=0,
            nom=""
        )
        
    elif message == "START":    
        update_state(
            current_page="/contexte",
            crono_debut=time.time()
        )

    # Fin du chrono
    elif message == "4455":
        update_state(
            current_page="/ending",
            crono_fin=time.time()
        )
    elif "nom =" in message:
        nom = message.split("nom =")
        print(f"{message}===={nom}")
        nom = nom[1]
        print(f"{message}===={nom}")
        update_state(
            nom=nom,
            Value=True
        )
        
        with open(f"log_file_{state.nom}.log", "w", encoding="utf-8") as log:
            log.write(f"=== FICHIER LOG EQUIPE {state.nom}===\n")
            log.write(f"temps : {state.crono_debut} ---> {state.crono_fin}\n")
            log.write(f"malus : {state.erreur} \n")
        subprocess.run(f"scp /home/qamu/escapegame_master/log_file_{state.nom}.log thorin:", shell=True)
        subprocess.run(f"rm /home/qamu/escapegame_master/log_file_{state.nom}.log", shell=True)
    # Navigation classique
    elif message in PAGE_MAP:
        update_state(
            current_page=PAGE_MAP[message]
        )
        
    await asyncio.sleep(0.05)

    # envoyer la confirmation BLE
    try:
        await client.write_gatt_char(CHAR_UUID_WRITE, b"True", response=True)
        print(" Confirmation envoyée")
    except Exception as e:
        print(" Erreur en envoyant la confirmation :", e)

    return True


async def connect_and_listen(address):
    async with BleakClient(address) as client:
        print(f" Connecté à : {address}")

        stop = False
        last_notification = asyncio.get_event_loop().time()  # timestamp dernière notification

        async def handler(sender, data):
            nonlocal stop, last_notification
            last_notification = asyncio.get_event_loop().time()  # mettre à jour la dernière notification
            stop = await notification_handler(sender, data, client)

        await client.start_notify(CHAR_UUID_NOTIFY, handler)

        while client.is_connected and not stop:
            # vérifier le temps écoulé depuis la dernière notification
            elapsed = asyncio.get_event_loop().time() - last_notification
            if elapsed > random.uniform(2, 3):  # si >2-3s sans notification
                print(f" Aucune donnée reçue depuis {elapsed:.1f}s, déconnexion...")
                break
            await asyncio.sleep(0.1)  # boucle rapide pour vérifier régulièrement

        await client.stop_notify(CHAR_UUID_NOTIFY)
        print(" Déconnecté, nouvelle recherche dans 5s...")
        await asyncio.sleep(5)  # attendre avant nouvelle recherche

async def main():
    while True:
        print(" Recherche de 'STM32WB_BLE'...")
        devices = await BleakScanner.discover(timeout=5.0)
        target = next((d for d in devices if d.name == "STM32WB_BLE"), None)

        if not target:
            print(" Périphérique non trouvé, nouvelle tentative dans 3s...")
            await asyncio.sleep(3)
            continue

        try:
            await connect_and_listen(target.address)
        except Exception as e:
            print(f" Erreur BLE : {e}, nouvelle tentative dans 2s...")
            await asyncio.sleep(2)

if __name__ == "__main__": 
    asyncio.run(main()) 