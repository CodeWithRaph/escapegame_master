import paho.mqtt.client as mqtt
import json

# Configuration
MQTT_BROKER = "10.11.33.100"
MQTT_PORT = 1883
MQTT_TOPIC = "escapegame/stats"

def send_game_stats(nom, debut, fin, erreur):
    """
    Envoie les statistiques de fin de partie au broker MQTT au format JSON.
    """
    # Calcul de la durée totale
    duree_totale = fin - debut if fin > 0 else 0

    # Préparation des données
    payload = {
        "equipe": nom,
        "crono_debut": debut,
        "crono_fin": fin,
        "temps_total_sec": round(duree_totale, 2),
        "malus_erreurs": erreur
    }

    try:
        # Création du client et connexion
        client = mqtt.Client()
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        
        # Envoi du message (en JSON pour faciliter la lecture par la page de stats)
        client.publish(MQTT_TOPIC, json.dumps(payload))
        
        print(f"✅ Données envoyées en MQTT pour l'équipe {nom}")
        
        client.disconnect()
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi MQTT : {e}")
