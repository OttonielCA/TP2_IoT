# sauvegarde 18h30
# Importations des bibliotheques necessaires
import time
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import publisher_mqtt_RPi as pRPi

GPIO.setwarnings(False)

# Initialisation du dictionnaire des broches LED
led_pins = {
    "LED_DIR1_GREEN": 17,
    "LED_DIR1_YELLOW": 27,
    "LED_DIR1_RED": 22,
    "LED_DIR2_GREEN": 23,
    "LED_DIR2_YELLOW": 24,
    "LED_DIR2_RED": 25
}


# Fonction pour allumer ou eteindre les LEDs
def control_led(pin, state):
    GPIO.output(pin, state)


# Eteindre toutes les LEDs au debut du code pour s'assurer de la qualite d'execution
def turn_off_all_leds():
    for pin in led_pins.values():
        control_led(pin, GPIO.LOW)


# Configuration des GPIO
GPIO.setmode(GPIO.BCM)
for pin in led_pins.values():
    GPIO.setup(pin, GPIO.OUT)

# Eteindre toutes les LEDs avant de commencer le cycle
turn_off_all_leds()


# -----------------------------------------------------------------------------------------------------

# Fonction pour le mode urgence
def modeUrgence():
    global mode_urgence, message_urgence, jaune
    # Si le message MQTT recu est urgence_direction1
    if message_urgence == "urgence_direction1":
        print("Mode urgence active: direction 1 au vert")
        # Si direction 2 est actuellement verte, on doit d'abord la passer en rouge
        if GPIO.input(led_pins['LED_DIR2_GREEN']) == GPIO.HIGH and GPIO.input(led_pins['LED_DIR1_RED']) == GPIO.HIGH:
            print("Passage de la direction 2 au rouge")
            control_led(led_pins['LED_DIR2_GREEN'], GPIO.LOW)  # eteindre le vert de la direction 2
            control_led(led_pins['LED_DIR2_YELLOW'], GPIO.HIGH)  # Allumer le jaune
            # Maintenir le feu jaune pendant 3 secondes
            for x in range(3, 0, -1):
                print(x)
                time.sleep(1)
            control_led(led_pins['LED_DIR2_YELLOW'], GPIO.LOW)  # eteindre le jaune
            control_led(led_pins['LED_DIR2_RED'], GPIO.HIGH)  # Allumer le rouge
            print("Direction 1: rouge - Direction 2: rouge")
            print(1)  # Affichage temps de securite
            time.sleep(1)  # Temps de securite
        # Si le mode_pieton est True
        elif mode_pieton:
            control_led(led_pins['LED_DIR2_RED'], GPIO.HIGH)  # Allumer le rouge
        # Activer le vert pour direction 1
        control_led(led_pins['LED_DIR1_YELLOW'], GPIO.LOW)  # eteindre le jaune de la direction 1
        control_led(led_pins['LED_DIR2_YELLOW'], GPIO.LOW)  # eteindre le jaune de la direction 2
        control_led(led_pins['LED_DIR1_RED'], GPIO.LOW)  # eteindre le rouge de la direction 1
        control_led(led_pins['LED_DIR2_RED'], GPIO.HIGH)  # Allumer le rouge de la direction 2
        control_led(led_pins['LED_DIR1_GREEN'], GPIO.HIGH)  # Allumer le vert de la direction 1
        control_led(led_pins['LED_DIR2_GREEN'], GPIO.LOW)  # eteindre le vert de la direction 2
        # Maintenir le feu vert pendant 20 secondes
        print("Debut du compte a rebours pour direction 1 au vert")
        for x in range(20, 0, -1):
            print(x)
            time.sleep(1)
        print("Mode urgence terminer: retour au mode precedent")
        mode_urgence = False
        # Si la variable jaune est vrai
        if jaune:
            transition_jaune()  # Effectuer la fonctione transition_jaune()


    # Cas ou la direction 2 est activee pour l'urgence
    elif message_urgence == "urgence_direction2":
        print("Mode urgence active: direction 2 au vert")
        # Si direction 1 est actuellement verte, on doit d'abord la passer en rouge
        if GPIO.input(led_pins['LED_DIR1_GREEN']) == GPIO.HIGH:
            print("Passage de la direction 1 au rouge")
            control_led(led_pins['LED_DIR1_GREEN'], GPIO.LOW)  # eteindre le vert de la direction 1
            control_led(led_pins['LED_DIR1_YELLOW'], GPIO.HIGH)  # Allumer le jaune
            # Maintenir le feu jaune pendant 3 secondes
            for x in range(3, 0, -1):
                print(x)
                time.sleep(1)
            control_led(led_pins['LED_DIR1_YELLOW'], GPIO.LOW)  # eteindre le jaune
            control_led(led_pins['LED_DIR1_RED'], GPIO.HIGH)  # Allumer le rouge
            print("Direction 1: rouge - Direction 2: rouge")
            print(1)  # Affichage temps de securite
            time.sleep(1)  # Temps de securite
        # Si le mode_pieton est vrai
        elif mode_pieton:
            control_led(led_pins['LED_DIR1_RED'], GPIO.HIGH)  # Allumer le rouge de la direction 1
        # Activer le vert pour direction 2
        control_led(led_pins['LED_DIR1_YELLOW'], GPIO.LOW)  # eteindre le jaune de la direction 1
        control_led(led_pins['LED_DIR2_YELLOW'], GPIO.LOW)  # eteindre le jaune de la direction 2
        control_led(led_pins['LED_DIR2_RED'], GPIO.LOW)  # eteindre le rouge de la direction 2
        control_led(led_pins['LED_DIR1_RED'], GPIO.HIGH)  # Allumer le rouge de la direction 1
        control_led(led_pins['LED_DIR1_GREEN'], GPIO.LOW)  # eteindre le vert de la direction 2
        control_led(led_pins['LED_DIR2_GREEN'], GPIO.HIGH)  # Allumer le vert de la direction 2
        # Maintenir le feu vert pendant 20 secondes
        print("Debut du compte a rebours pour direction 2 au vert")
        for x in range(20, 0, -1):
            print(x)
            time.sleep(1)
        print("Mode urgence terminer: retour au mode precedent")
        mode_urgence = False
        # Si la variable jaune est False ou la led verte 2 est allumee
        if not jaune or GPIO.input(led_pins['LED_DIR2_GREEN']) == GPIO.HIGH:
            transition_jaune()  # Effectuer la fonction transition_jaune()


# Fonction pour le mode Panne
def modePanne():
    global mode_panne, mode_urgence
    control_led(led_pins['LED_DIR1_YELLOW'], GPIO.LOW)  # Eteint de la led jaune pour la direction 1
    control_led(led_pins['LED_DIR1_GREEN'], GPIO.LOW)  # Eteint de la led verte pour la direction 1
    control_led(led_pins['LED_DIR2_YELLOW'], GPIO.LOW)  # Eteint de la led jaune pour la direction 2
    control_led(led_pins['LED_DIR2_GREEN'], GPIO.LOW)  # Eteint de la led verte pour la direction 2
    print("Mode panne active: toutes les directions rouges clignotent.")
    while mode_panne:  # Pendant que le mode panne est vrai
        control_led(led_pins["LED_DIR1_RED"], GPIO.HIGH)  # Allumage de la led rouge pour la direction 1
        control_led(led_pins["LED_DIR2_RED"], GPIO.HIGH)  # Allumage de la led rouge pour la direction 2
        if mode_urgence:  # si le mode urgence est vrai effectuer la fonction modeUrgence()
            modeUrgence()
        time.sleep(1)
        control_led(led_pins["LED_DIR1_RED"], GPIO.LOW)  # eteint de la led rouge pour la direction 1
        control_led(led_pins["LED_DIR2_RED"], GPIO.LOW)  # eteint de la led rouge pour la direction 2
        if mode_urgence:  # Si la variable mode_urgence est vraie effectuer la fonctione modeUrgence()
            modeUrgence()
        time.sleep(1)
    print("Fin du mode panne.")
    mode_panne = False


# Fonction pour le mode pieton
def modePieton():
    global mode_panne, mode_urgence
    print("Mode pieton active: toutes les directions passent au rouge.")
    # Allumer les LEDs rouges pour les deux directions pendant 15 secondes
    control_led(led_pins["LED_DIR1_RED"], GPIO.HIGH)  # Allumage de la led rouge pour la direction 1
    control_led(led_pins["LED_DIR2_RED"], GPIO.HIGH)  # Allumage de la led rouge pour la direction 2
    # Compte a rebours inverse
    for x in range(15, 0, -1):  # Demarre a 15, descend jusqu'a 1
        if mode_panne or mode_urgence:  # Si le mode panne ou le mode urgence sont vrai
            break
        print(x)
        time.sleep(1)
    if mode_panne:  # si la variable mode_panne est vrai effectuer la fonction modePanne()
        modePanne()
    elif mode_urgence:  # si la variable mode_urgence est vrai effectuer la fonction modeUrgence()
        modeUrgence()
    control_led(led_pins["LED_DIR1_RED"], GPIO.LOW)  # eteint de la led rouge pour la direction 1
    control_led(led_pins["LED_DIR2_RED"], GPIO.LOW)  # eteint de la led rouge pour la direction 2
    print("Fin du mode pieton.")

# Fonction pour effectuer la transition des led du vert au rouge a partir de la led jaune
def transition_jaune():
    if GPIO.input(led_pins['LED_DIR2_GREEN']) == GPIO.HIGH:  # si la led verte de la direction 2 est allumee
        # Direction 1 : rouge, Direction 2 : transition vert au jaune
        print('transition vert au rouge:')
        print('direction 2: jaune - direction 1: rouge')
        control_led(led_pins['LED_DIR2_GREEN'], GPIO.LOW)  # eteint de la led verte pour la direction 2
        control_led(led_pins['LED_DIR2_YELLOW'], GPIO.HIGH)  # Allumage de la led jaune pour la direction 2
        control_led(led_pins['LED_DIR1_RED'], GPIO.HIGH)  # Allumage de la led rouge pour la direction 2
        # Compte a rebours inverse
        for x in range(3, 0, -1):  # Demarre a 3, descend jusqu'a 1
            if mode_urgence:
                break
            print(x)
            time.sleep(1)
        control_led(led_pins['LED_DIR2_YELLOW'], GPIO.LOW)  # eteint de la led jaune pour la direction 2
        print("deux directions au rouge")
        control_led(led_pins['LED_DIR2_RED'], GPIO.HIGH)  # Allumage de la led rouge pour la direction 2
        control_led(led_pins['LED_DIR1_RED'], GPIO.HIGH)  # Allumage de la led rouge pour la direction 1
        print(1)
        time.sleep(1)
        print("Retour au mode precedent")

    elif GPIO.input(led_pins['LED_DIR1_GREEN']) == GPIO.HIGH:  # si la led verte de la direction 1 est allumee
        # Direction 1 : rouge, Direction 2 : jaune
        print('transition vert au rouge:')
        print('direction 1: jaune - direction 2: rouge')
        control_led(led_pins['LED_DIR1_GREEN'], GPIO.LOW)  # eteint de la led verte pour la direction 2
        control_led(led_pins['LED_DIR1_YELLOW'], GPIO.HIGH)  # Allumage de la led jaune pour la direction 1
        control_led(led_pins['LED_DIR2_RED'], GPIO.HIGH)  # Allumage de la led rouge pour la direction 2
        # Compte a rebours inverse
        for x in range(3, 0, -1):  # Demarre a 3, descend jusqu'a 1
            if mode_urgence:
                break
            print(x)
            time.sleep(1)
        control_led(led_pins['LED_DIR1_YELLOW'], GPIO.LOW)  # eteint de la led jaune pour la direction 1
        print("deux directions au rouge")
        control_led(led_pins['LED_DIR2_RED'], GPIO.HIGH)  # Allumage de la led rouge pour la direction 2
        control_led(led_pins['LED_DIR1_RED'], GPIO.HIGH)  # Allumage de la led rouge pour la direction 1
        print(1)
        time.sleep(1)
        print("Retour au mode precedent")


# -----------------------------------------------------------------------------------------------------


# Variables pour le broker mosquitto
broker = "test.mosquitto.org"
port = 1883
qos = 2  # on veut que la connexion soit la plus forte puisqu'il y a des risques associes

# Variables pour le mode pieton
topic_pieton = "mode/pieton"
mode_pieton = False

# Variables pour le mode panne
topic_panne = "mode/panne"
mode_panne = False

# Variables pour le mode urgence
topic_urgence = "mode/urgence"
mode_urgence = False
message_urgence = ""


# Callback pour la connexion au broker MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connecte avec le code de resultat {rc}")
    client.subscribe(topic_pieton, qos=qos)
    client.subscribe(topic_panne, qos=qos)
    client.subscribe(topic_urgence, qos=qos)


# La fonction de rappel pour lorsqu'un message PUBLISH est recu du serveur
# Callback appele lorsqu'un message est recu
def on_message(client, userdata, message):
    global mode_pieton, mode_panne, mode_urgence, message_urgence
    if message.topic == topic_pieton and message.payload.decode() == "pieton_on":
        mode_pieton = True
        print("Commande 'pieton_on' recue.")
        pRPi.publish_pieton_command_RPi(client)  # publication mqtt
    elif message.topic == topic_panne:
        if message.payload.decode() == "panne_on" and mode_panne is False:
            mode_panne = True
            print("Commande 'panne_on' recue.")
            pRPi.publish_panneOn_command_RPi(client)  # publication mqtt
        elif message.payload.decode() == "panne_off" and mode_panne is True:
            mode_panne = False
            print("Commande 'panne_off' recue.")
            pRPi.publish_panneOff_command_RPi(client)  # publication mqtt
    elif message.topic == topic_urgence:
        if message.payload.decode() == "urgence_direction1" and mode_urgence is False:
            mode_urgence = True
            print("Commande 'urgence_direction1' recue.")
            message_urgence = message.payload.decode()
            pRPi.publish_urgence1_command_RPi(client)  # publication mqtt
        elif message.payload.decode() == "urgence_direction2" and mode_urgence is False:
            mode_urgence = True
            print("Commande 'urgence_direction2' recue.")
            message_urgence = message.payload.decode()
            pRPi.publish_urgence2_command_RPi(client)  # publication mqtt


# Creation du client mqtt
client = mqtt.Client()

# Assigner les fonctions de rappel d'evenement
client.on_connect = on_connect
client.on_message = on_message

# connection au broker mqtt
client.connect(broker, port, 60)

client.loop_start()

# -----------------------------------------------------------------------------------------------------


# Boucle principale de gestion des feux de circulation
try:
    while True:
        # boucle du mode panne
        if mode_panne:
            modePanne()

        # boucle du mode urgence
        elif mode_urgence:
            modeUrgence()

        # Boucle du mode normal
        else:
            jaune = True
            # Direction 1 : LED verte allumee, Direction 2 : LED rouge allumee
            control_led(led_pins['LED_DIR1_RED'], GPIO.LOW)
            control_led(led_pins['LED_DIR1_GREEN'], GPIO.HIGH)
            control_led(led_pins['LED_DIR2_RED'], GPIO.HIGH)
            print('Premier cycle des feux:')
            print('Direction 1: vert - direction 2: rouge')
            # Compte a rebours inverse
            for x in range(10, 0, -1):  # Demarre a 10, descend jusqu'a 1
                if mode_panne:  # Verifiez si le mode panne est active
                    break  # Quittez immediatement la boucle pour passer au mode panne
                elif mode_urgence:
                    break
                print(x)
                time.sleep(1)

            if mode_panne:  # Si le mode panne a ete active, passez directement au mode panne
                continue
            elif mode_urgence:  # Si le mode urgence a ete active, passez directement au mode panne
                continue

            # Direction 1 : LED jaune allumee, Direction 2 : LED rouge allumee
            control_led(led_pins['LED_DIR1_GREEN'], GPIO.LOW)
            control_led(led_pins['LED_DIR1_YELLOW'], GPIO.HIGH)
            control_led(led_pins['LED_DIR2_RED'], GPIO.HIGH)
            print('deuxieme cycle des feux:')
            print('direction 1: jaune - direction 2: rouge')
            # Compte a rebours inverse
            for x in range(3, 0, -1):  # Demarre a 3, descend jusqu'a 1
                if mode_panne:
                    break
                elif mode_urgence:
                    break
                print(x)
                time.sleep(1)

            if mode_panne:
                continue
            elif mode_urgence:  # Si le mode urgence a ete active, passez directement au mode panne
                continue

            # Verification si le mode pieton est active
            if mode_pieton:
                control_led(led_pins["LED_DIR1_YELLOW"], GPIO.LOW)
                control_led(led_pins["LED_DIR2_RED"], GPIO.LOW)
                modePieton()
                mode_pieton = False  # Reinitialiser le mode pieton pour permettre d'autres commandes
                control_led(led_pins["LED_DIR1_GREEN"], GPIO.LOW)

            # Transition : Les deux directions en rouge pendant 1 seconde
            control_led(led_pins['LED_DIR1_YELLOW'], GPIO.LOW)
            control_led(led_pins['LED_DIR1_RED'], GPIO.HIGH)
            if GPIO.input(led_pins['LED_DIR2_GREEN']) == GPIO.LOW:
                control_led(led_pins['LED_DIR2_RED'], GPIO.HIGH)
            print('troisieme cycle des feux:')
            print('direction 1: rouge - direction 2: rouge')
            print(1)
            time.sleep(1)

            if mode_panne:
                continue
            elif mode_urgence:  # Si le mode urgence a ete active, passez directement au mode panne
                continue

            # Direction 1 : LED rouge allumee, Direction 2 : LED verte allumee
            control_led(led_pins['LED_DIR2_RED'], GPIO.LOW)
            control_led(led_pins['LED_DIR2_GREEN'], GPIO.HIGH)
            control_led(led_pins['LED_DIR1_RED'], GPIO.HIGH)
            print('quatrieme cycle des feux:')
            print('direction 2: vert - direction 1: rouge')
            # Compte a rebours inverse
            for x in range(10, 0, -1):  # Demarre a 10, descend jusqu'a 1
                if mode_panne:
                    break
                elif mode_urgence:
                    break
                print(x)
                time.sleep(1)

            if mode_panne:
                continue
            elif mode_urgence:  # Si le mode urgence a ete active, passez directement au mode panne
                continue

            # Direction 1 : LED rouge allumee, Direction 2 : LED jaune allumee
            control_led(led_pins['LED_DIR2_GREEN'], GPIO.LOW)
            control_led(led_pins['LED_DIR2_YELLOW'], GPIO.HIGH)
            control_led(led_pins['LED_DIR1_RED'], GPIO.HIGH)
            print('cinquieme cycle des feux:')
            print('direction 2: jaune - direction 1: rouge')
            # Compte a rebours inverse
            for x in range(3, 0, -1):  # Demarre a 3, descend jusqu'a 1
                if mode_panne:
                    break
                elif mode_urgence:
                    break
                print(x)
                time.sleep(1)

            if mode_panne:
                continue
            elif mode_urgence:  # Si le mode urgence a ete active, passez directement au mode panne
                continue

            # Verification si le mode pieton est active
            jaune = False
            if mode_pieton:
                control_led(led_pins["LED_DIR2_YELLOW"], GPIO.LOW)
                control_led(led_pins["LED_DIR1_RED"], GPIO.LOW)
                modePieton()
                mode_pieton = False  # Reinitialiser le mode pieton pour permettre d'autres commandes
                control_led(led_pins["LED_DIR2_GREEN"], GPIO.LOW)

            # Transition : Les deux directions en rouge pendant 1 seconde
            control_led(led_pins['LED_DIR2_YELLOW'], GPIO.LOW)
            control_led(led_pins['LED_DIR2_RED'], GPIO.HIGH)
            if GPIO.input(led_pins['LED_DIR1_GREEN']) == GPIO.LOW:
                control_led(led_pins['LED_DIR1_RED'], GPIO.HIGH)
            print('sixieme cycle des feux:')
            print('direction 2: rouge - direction 1: rouge')
            print(1)
            time.sleep(1)

            if mode_panne:
                continue
            elif mode_urgence:  # Si le mode urgence a ete active, passez directement au mode panne
                continue

except KeyboardInterrupt:
    print("Interruption par l'utilisateur")

finally:
    GPIO.cleanup() # Nettoyage des GPIO a la fin du programme

