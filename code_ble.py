from flask import Flask, render_template, jsonify, redirect
import asyncio
import subprocess
import random
from bleak import BleakClient, BleakScanner

SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
CHAR_UUID_NOTIFY = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
CHAR_UUID_WRITE = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
PAGE_MAP = {
    "START": "/contexte",
    "GO": "/etape1",
    "9471": "/etape2",
    "4456": "/etape3",
    "4456": "/ending",
}

async def notification_handler(sender, data, client):
    message = data.decode("utf-8").strip()
    print(f" Signal reçu : {message}")
    if message in PAGE_MAP :
        redirect(PAGE_MAP[message])  # <-- mise à jour de la page
        print(f" Page actuelle mise à jour :{PAGE_MAP[message]}")

    await asyncio.sleep(0.05)  # petit délai

    # envoyer la confirmation
    try:
        await client.write_gatt_char(CHAR_UUID_WRITE, b"True", response=True)
        print(" Confirmation envoyée")
    except Exception as e:
        print(" Erreur en envoyant la confirmation :", e)

    # exécuter le code reçu
    try:
        print(f" Exécution du code : {message}")
        if message == "AAAA" :
            result = subprocess.run("python3 script.py connect 1 &", shell=True)
        elif message == "-AAAA" :
            result = subprocess.run("pkill -f '^vncviewer'", shell=True)
    except Exception as e:
        print(" Erreur lors de l'exécution :", e)

    # Retourner True pour signaler à la boucle principale de déconnecter
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
        print(" Déconnecté, nouvelle recherche dans 5-10s...")
        await asyncio.sleep(10)  # attendre avant nouvelle recherche

async def main():
    while True:
        print(" Recherche de 'STM32WB_BLE'...")
        devices = await BleakScanner.discover(timeout=5.0)
        target = next((d for d in devices if d.name == "STM32WB_BLE"), None)

        if not target:
            print(" Périphérique non trouvé, nouvelle tentative dans 5s...")
            await asyncio.sleep(5)
            continue

        try:
            await connect_and_listen(target.address)
        except Exception as e:
            print(f" Erreur BLE : {e}, nouvelle tentative dans 5s...")
            await asyncio.sleep(5)
