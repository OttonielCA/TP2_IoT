import paho.mqtt.client as mqtt

# Configuration du broker MQTT
broker = "test.mosquitto.org"  # adresse du rboker mqtt
port = 1883  # Port MQTT par défaut
qos = 2  # Niveau de QoS

# Définition des topics MQTT
topic_pieton = "mode/pieton"
topic_panne = "mode/panne"
topic_urgence = "mode/urgence"

# Fonctions pour publier des commandes sur différents topics
def publish_pieton_command(client):
    client.publish(topic_pieton, "pieton_on")
    print("Commande 'pieton_on' envoyee a partir du PC.")

def publish_panne_command(client, command):
    client.publish(topic_panne, command)
    print(f"Commande '{command}' envoyee a partir du PC.")

def publish_urgence_command(client, command):
    client.publish(topic_urgence, command)
    print(f"Commande '{command}' envoyee a partir du PC.")


# Creer une instance du client
client = mqtt.Client()

# Se connecter au broker
client.connect(broker, port, 60)

# Publier un message
client.loop_start()