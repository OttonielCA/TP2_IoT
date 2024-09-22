import pyttsx3
import paho.mqtt.client as mqtt

# Initialiser le moteur de synthèse vocale
engine = pyttsx3.init()

# Configurer la voix : changer la vitesse et le volume
engine.setProperty('rate', 150) # Vitesse de la voix
engine.setProperty('volume', 1) # Volume (entre 0.0 et 1.0)

# ----------------------------------------------------------------------------------------------------------------------

# Variables pour le broker mosquitto
broker = "test.mosquitto.org"
port = 1883
qos = 2  # on veut que la connexion soit la plus forte puisqu'il y a des risques associes

topic = "led/control"
qos = 2  # Niveau de QoS

# La fonction de rappel pour lorsque le client reçoit une réponse du serveur
def on_connect(client, userdata, flags, rc):
    print(f"Connecté avec le code de résultat {rc}")
    client.subscribe(topic, qos=qos)

# La fonction de rappel pour lorsqu'un message PUBLISH est reçu du serveur
def on_message(client, userdata, message):
    if message.payload.decode() == "Mode pieton activer":
        # Convertir le texte en parole
        engine.say("Mode pieton activer")
        # Attendre que la lecture soit terminée
        engine.runAndWait()
    elif message.payload.decode() == "Mode panne activer":
        # Convertir le texte en parole
        engine.say("Mode panne activer")
        # Attendre que la lecture soit terminée
        engine.runAndWait()
    elif message.payload.decode() == "Mode panne desactiver":
        # Convertir le texte en parole
        engine.say("Mode panne desactiver")
        # Attendre que la lecture soit terminée
        engine.runAndWait()
    elif message.payload.decode() == "Mode urgence direction 1 activer":
        # Convertir le texte en parole
        engine.say("Mode urgence direction 1 activer")
        # Attendre que la lecture soit terminée
        engine.runAndWait()
    elif message.payload.decode() == "Mode urgence direction 2 activer":
        # Convertir le texte en parole
        engine.say("Mode urgence direction 2 activer")
        # Attendre que la lecture soit terminée
        engine.runAndWait()

# ----------------------------------------------------------------------------------------------------------------------

# Créer une instance du client
client = mqtt.Client()

# Assigner les fonctions de rappel d'événement
client.on_connect = on_connect
client.on_message = on_message

# Se connecter au broker
client.connect(broker, port, 60)

# Appel bloquant qui traite le trafic réseau, distribue les rappels et gère la reconnexion
client.loop_forever()