import pyttsx3
import paho.mqtt.client as mqtt

def run_subscriber():
    # Initializer le moteur de synthèse vocale
    engine = pyttsx3.init()

    # Configurer la voix : changer la vitesse et le volume
    engine.setProperty('rate', 150)  # Vitesse de la voix
    engine.setProperty('volume', 1)  # Volume (entre 0.0 et 1.0)

    # Variables pour le broker mosquitto
    broker = "test.mosquitto.org"
    port = 1883
    qos = 2

    topic_pieton = "mode/pieton"
    topic_panne = "mode/panne"
    topic_urgence = "mode/urgence"

    def on_connect(client, userdata, flags, rc):
        print(f"Connecté avec le code de résultat {rc}")
        client.subscribe(topic_pieton, qos=qos)
        client.subscribe(topic_panne, qos=qos)
        client.subscribe(topic_urgence, qos=qos)

    def on_message(client, userdata, message):
        text = message.payload.decode()
        if text in ["Mode pieton activer", "Mode panne activer", "Mode panne desactiver",
                    "Mode urgence direction 1 activer", "Mode urgence direction 2 activer"]:
            engine.say(text)
            engine.runAndWait()

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