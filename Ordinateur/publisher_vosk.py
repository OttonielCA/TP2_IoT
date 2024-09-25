import time
import pyaudio
import json
from vosk import Model, KaldiRecognizer
import publisher_functions as pf
from publisher_functions import client
import threading

# Fonction pour publier les commandes vocales
def publish_vocal_command(command):
    client.publish("commande/vocale", command)

def run_voice_recognition(callback):
    model = Model("vosk-model-small-fr-0.22")
    recognizer = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    mot_cles_activation = ["mode normal", "mode passage", "mode panne", "mode urgence"]
    mot_cles_urgence = ["Direction numéro un", "Direction numéro deux"]
    mot_cles_panne = ["Sortir du mode panne", "mode urgence"]

    print("Parlez dans le micro...")

    try:
        while True:
            data = stream.read(4000, exception_on_overflow=False)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                transcribed_text = result['text'].lower()

                if transcribed_text == mot_cles_activation[0].lower():
                    print(f"{transcribed_text}: Mode Normal Allumé.")
                    callback("normal")
                    # Publier la commande vocale via MQTT
                    publish_vocal_command(transcribed_text)

                elif transcribed_text == mot_cles_activation[1].lower():
                    print(f"{transcribed_text}: Mode Piéton Allumé.")
                    callback("pieton")
                    pf.publish_pieton_command(client)
                    # Publier la commande vocale via MQTT
                    publish_vocal_command(transcribed_text)

                elif transcribed_text == mot_cles_activation[2].lower():
                    print(f"{transcribed_text}: Mode Panne Allumé.")
                    callback("panne")
                    pf.publish_panne_command(client, "panne_on")
                    # Publier la commande vocale via MQTT
                    publish_vocal_command(transcribed_text)
                    print(f"Dites '{mot_cles_panne[0]}' pour sortir du mode panne ou '{mot_cles_panne[1]}' pour passer en mode urgence")

                    var = True
                    while var:
                        data = stream.read(4000, exception_on_overflow=False)
                        if len(data) == 0:
                            break
                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            transcribed_text = result['text'].lower()

                            if transcribed_text == mot_cles_panne[0].lower():
                                print(f"{transcribed_text}: Sortie du Mode Panne.")
                                callback("panne_off")
                                pf.publish_panne_command(client, "panne_off")
                                # Publier la commande vocale via MQTT
                                publish_vocal_command(transcribed_text)
                                var = False

                            elif transcribed_text == mot_cles_panne[1].lower():
                                print(f"{transcribed_text}: Mode Urgence Allumé.")
                                callback("urgence")
                                # Publier la commande vocale via MQTT
                                publish_vocal_command(transcribed_text)
                                print(f"Dites '{mot_cles_urgence[0]}' ou '{mot_cles_urgence[1]}' pour activer le mode urgence: ")

                                var1 = True
                                while var1:
                                    data = stream.read(4000, exception_on_overflow=False)
                                    if len(data) == 0:
                                        break
                                    if recognizer.AcceptWaveform(data):
                                        result = json.loads(recognizer.Result())
                                        transcribed_text = result['text'].lower()

                                        if transcribed_text in [mot.lower() for mot in mot_cles_urgence]:
                                            if transcribed_text == mot_cles_urgence[0].lower():
                                                urgence = "urgence_direction1"
                                                # Publier la commande vocale via MQTT
                                                publish_vocal_command(transcribed_text)
                                            elif transcribed_text == mot_cles_urgence[1].lower():
                                                urgence = "urgence_direction2"
                                                # Publier la commande vocale via MQTT
                                                publish_vocal_command(transcribed_text)

                                            print(f"{transcribed_text}: Direction activée.")
                                            callback(urgence)
                                            pf.publish_urgence_command(client, urgence)
                                            var1 = False

                elif transcribed_text == mot_cles_activation[3].lower():
                    print(f"{transcribed_text}: Mode Urgence Allumé.")
                    callback("urgence")
                    # Publier la commande vocale via MQTT
                    publish_vocal_command(transcribed_text)
                    print(f"Dites '{mot_cles_urgence[0]}' ou '{mot_cles_urgence[1]}' pour activer le mode urgence: ")

                    var3 = True
                    while var3:
                        data = stream.read(4000, exception_on_overflow=False)
                        if len(data) == 0:
                            break
                        if recognizer.AcceptWaveform(data):
                            result = json.loads(recognizer.Result())
                            transcribed_text = result['text'].lower()

                            if transcribed_text in [mot.lower() for mot in mot_cles_urgence]:
                                if transcribed_text == mot_cles_urgence[0].lower():
                                    urgence = "urgence_direction1"
                                    # Publier la commande vocale via MQTT
                                    publish_vocal_command(transcribed_text)
                                elif transcribed_text == mot_cles_urgence[1].lower():
                                    urgence = "urgence_direction2"
                                    # Publier la commande vocale via MQTT
                                    publish_vocal_command(transcribed_text)

                                print(f"{transcribed_text}: Direction activée.")
                                callback(urgence)
                                pf.publish_urgence_command(client, urgence)
                                var3 = False

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def start_voice_recognition(callback):
    voice_thread = threading.Thread(target=run_voice_recognition, args=(callback,))
    voice_thread.start()
    return voice_thread

def stop_voice_recognition(voice_thread):
    if voice_thread and voice_thread.is_alive():
        voice_thread.join(timeout=1)

if __name__ == "__main__":
    def test_callback(command):
        print(f"Callback received: {command}")

    try:
        voice_thread = start_voice_recognition(test_callback)
        voice_thread.join()
    finally:
        client.loop_stop()
        client.disconnect()