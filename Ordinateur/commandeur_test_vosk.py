import paho.mqtt.client as mqtt
import time
import pyaudio
import json
from vosk import Model, KaldiRecognizer

# Connexion a MQTT
broker = "test.mosquitto.org"  # adresse du broker mqtt
port = 1883  # Port MQTT par défaut
qos = 2  # Niveau de QoS

topic_pieton = "mode/pieton"
topic_panne = "mode/panne"
topic_urgence = "mode/urgence"
def publish_pieton_command(client):
    client.publish(topic_pieton, "pieton_on")
    print("Commande 'pieton_on' envoyee.")

def publish_panne_command(client, command):
    client.publish(topic_panne, command)
    print(f"Commande '{command}' envoyee.")

def publish_urgence_command(client, command):
    client.publish(topic_urgence, command)
    print(f"Commande '{command}' envoyee.")

# Creer une instance du client
client = mqtt.Client()

# Se connecter au broker
client.connect(broker, port, 60)

# Publier un message
client.loop_start()

# ----------------------------------------------------------------------------------------------------------------------

# Charger le modèle Vosk
model = Model("vosk-model-small-fr-0.22")

# Initialiser l'objet de reconnaissance avec le modèle et la fréquence d'échantillonnage
recognizer = KaldiRecognizer(model, 16000)

# Initialiser PyAudio pour capturer l'audio du micro
p = pyaudio.PyAudio()

# Ouvrir un flux audio (stream) à partir du micro
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()

mot_cles_activation = ["mode normal", "mode piéton", "mode panne", "mode urgence"]
mot_cles_urgence = ["Direction numéro un", "Direction numéro deux"]

# ----------------------------------------------------------------------------------------------------------------------

print("Parlez dans le micro...")

# Boucle pour capturer et transcrire l'audio en direct
try:
    while True:
        # Lire les données audio du micro
        data = stream.read(4000, exception_on_overflow=False)
        # Si les données sont valides, tenter de les reconnaître
        if len(data) == 0:
            break
        # Transcrire l'audio en direct
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            transcribed_text = result['text'].lower()

            # Mode Normal - PAS ENCORE FAIT
            if transcribed_text == mot_cles_activation[0].lower():
                print(f"{transcribed_text}: Mode Normal Allumer.")

            # Mode Pieton - GOOD
            elif transcribed_text == mot_cles_activation[1].lower():
                publish_pieton_command(client)
                print(f"{transcribed_text}: Mode Pieton Allumer.")

            # Mode Panne - GOOD
            elif transcribed_text == mot_cles_activation[2].lower():
                panne = "panne_on"
                publish_panne_command(client, panne)
                print(f"{transcribed_text}: Mode Panne Allumer.")

                mot_cles_panne = ["Sortir du mode panne", "mode urgence"]
                print(f"Dites '{mot_cles_panne[0]}' pour sortir du mode panne ou '{mot_cles_panne[1]}' pour passer en mode urgence: ")
                while panne == "panne_on":
                    # Lire les données audio du micro
                    dataPanne = stream.read(4000, exception_on_overflow=False)
                    # Si les données sont valides, tenter de les reconnaître
                    if len(dataPanne) == 0:
                        break
                    # Transcrire l'audio en direct
                    if recognizer.AcceptWaveform(dataPanne):
                        result = json.loads(recognizer.Result())
                        transcribed_text_panne = result['text'].lower()
                        # Si panne_off est appeler
                        if transcribed_text_panne == mot_cles_panne[0].lower():
                            panne = "panne_off"
                            publish_panne_command(client, panne)
                        # Si mode urgence est appeler
                        elif transcribed_text_panne == mot_cles_panne[1].lower():
                            print(f"{transcribed_text_panne}: Mode Urgence Allumer.")
                            panneUrgence = ""
                            print(f"Dites '{mot_cles_urgence[0]}' ou '{mot_cles_urgence[1]}' pour activer le mode urgence: ")
                            while panneUrgence == "":
                                # Lire les données audio du micro
                                dataPanneUrgence = stream.read(4000, exception_on_overflow=False)
                                # Si les données sont valides, tenter de les reconnaître
                                if len(dataPanneUrgence) == 0:
                                    break
                                # Transcrire l'audio en direct
                                if recognizer.AcceptWaveform(dataPanneUrgence):
                                    result = json.loads(recognizer.Result())
                                    transcribed_text_panneUrgence = result['text'].lower()
                                    if transcribed_text_panneUrgence == mot_cles_urgence[0].lower():
                                        panneUrgence = "urgence_direction1"
                                        publish_urgence_command(client, panneUrgence)
                                    elif transcribed_text_panneUrgence == mot_cles_urgence[1].lower():
                                        panneUrgence = "urgence_direction2"
                                        publish_urgence_command(client, panneUrgence)
                                    else:
                                        print(f"{transcribed_text_panneUrgence}: reesaayer")
                                        time.sleep(1)
                        else:
                            print("Mauvaise entree, reesaayer")
                            time.sleep(1)

            # Mode Urgence
            elif transcribed_text == mot_cles_activation[3].lower():
                print(f"{transcribed_text}: Mode Urgence Allumer.")
                urgence = ""
                print(f"Dites '{mot_cles_urgence[0]}' ou '{mot_cles_urgence[1]}' pour activer le mode urgence: ")
                while urgence == "":
                    # Lire les données audio du micro
                    dataUrgence = stream.read(4000, exception_on_overflow=False)
                    # Si les données sont valides, tenter de les reconnaître
                    if len(dataUrgence) == 0:
                        break
                    # Transcrire l'audio en direct
                    if recognizer.AcceptWaveform(dataUrgence):
                        result = json.loads(recognizer.Result())
                        transcribed_text_Urgence = result['text'].lower()
                        if transcribed_text_Urgence == mot_cles_urgence[0].lower():
                            urgence = "urgence_direction1"
                            publish_urgence_command(client, urgence)
                        elif transcribed_text_Urgence == mot_cles_urgence[1].lower():
                            urgence = "urgence_direction2"
                            publish_urgence_command(client, urgence)
                        else:
                            print(f"{transcribed_text_Urgence}: reesaayer")
                            time.sleep(1)

except KeyboardInterrupt:
    print("Exiting...")
finally:
    # Deconnecter de MQTT
    client.loop_stop()
    client.disconnect()
    # Fermer le flux et PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()
