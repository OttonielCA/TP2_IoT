import pyttsx3
import paho.mqtt.client as mqtt
import publisher_vosk as pv
from pymongo import MongoClient
from datetime import datetime


def run_subscriber():
    # Initializer le moteur de synthèse vocale
    engine = pyttsx3.init()

    # Configurer la voix : changer la vitesse et le volume
    engine.setProperty('rate', 150)  # Vitesse de la voix
    engine.setProperty('volume', 1)  # Volume (entre 0.0 et 1.0)

    # Connexion à MongoDB
    client_mongo = MongoClient('mongodb://localhost:27017/')
    db = client_mongo['commande_vocale_db']
    collection = db['commandes']

    # Variables pour le broker mosquitto
    broker = "test.mosquitto.org"
    port = 1883
    qos = 2

    topic_pieton = "mode/pieton"
    topic_panne = "mode/panne"
    topic_urgence = "mode/urgence"
    topic_vocale = "commande/vocale"

    # Dictionnaire pour stocker temporairement les messages
    temp_messages = {
        "commande vocale": "",
        "réponse associée": "",
        "timestamp": None
    }

    def on_connect(client, userdata, flags, rc):
        print(f"Connecté avec le code de résultat {rc}")
        client.subscribe(topic_pieton, qos=qos)
        client.subscribe(topic_panne, qos=qos)
        client.subscribe(topic_urgence, qos=qos)
        client.subscribe(topic_vocale, qos=qos)

    def on_message(client, userdata, message):
        nonlocal temp_messages
        received_message = message.payload.decode()

        if message.topic == topic_vocale:
            temp_messages["commande vocale"] = received_message
        elif received_message in ["Mode pieton activer", "Mode panne activer", "Mode panne desactiver",
                                  "Mode urgence direction 1 activer", "Mode urgence direction 2 activer"]:
            temp_messages["réponse associée"] = received_message
            engine.say(received_message)
            engine.runAndWait()

        # Mettre à jour le timestamp à chaque message reçu
        temp_messages["timestamp"] = datetime.now()

        # Si nous avons reçu à la fois une commande vocale et une réponse associée, enregistrer dans MongoDB
        if temp_messages["commande vocale"] and temp_messages["réponse associée"]:
            collection.insert_one(temp_messages)

            # Réinitialiser le dictionnaire temporaire
            temp_messages = {
                "commande vocale": "",
                "réponse associée": "",
                "timestamp": None
            }

            # Garder uniquement les 5 dernières commandes
            if collection.count_documents({}) > 5:
                oldest_command = collection.find().sort("timestamp", 1).limit(1)
                for command in oldest_command:
                    collection.delete_one({"_id": command['_id']})

    # Créer une instance du client
    client = mqtt.Client()

    # Assigner les fonctions de rappel d'événement
    client.on_connect = on_connect
    client.on_message = on_message

    # Garder le script en cours d'exécution
    try:
        # Se connecter au broker
        client.connect(broker, port, 60)
        # Démarrer la boucle dans un thread séparé
        client.loop_forever()
    except KeyboardInterrupt:
        print("Arrêt de subscriber_mqtt_PC.py")
        client.loop_stop()
        client.disconnect()


if __name__ == "__main__":
    run_subscriber()