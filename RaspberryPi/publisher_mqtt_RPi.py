topic_pieton = "mode/pieton"
topic_panne = "mode/panne"
topic_urgence = "mode/urgence"

def publish_pieton_command_RPi(client):
    client.publish(topic_pieton, "Mode pieton activer")
    print("Commande 'Mode pieton activer' envoyee a partir du RPi.")

def publish_panneOn_command_RPi(client):
    client.publish(topic_panne, "Mode panne activer")
    print("Commande 'Mode panne activer' envoyee a partir du RPi.")

def publish_panneOff_command_RPi(client):
    client.publish(topic_panne, "Mode panne desactiver")
    print("Commande 'Mode panne desactiver' envoyee a partir du RPi.")

def publish_urgence1_command_RPi(client):
    client.publish(topic_urgence, "Mode urgence direction 1 activer")
    print("Commande 'Mode urgence direction 1 activer' envoyee a partir du RPi.")

def publish_urgence2_command_RPi(client):
    client.publish(topic_urgence, "Mode urgence direction 2 activer")
    print("Commande 'Mode urgence direction 2 activer' envoyee a partir du RPi.")