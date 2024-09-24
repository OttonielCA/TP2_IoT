import time
import pyaudio
import json
from vosk import Model, KaldiRecognizer
import publisher_functions as pf
from publisher_functions import client

def run_voice_recognition():
    # Charger le modèle Vosk
    model = Model("vosk-model-small-fr-0.22")

    # Initialiser l'objet de reconnaissance avec le modèle et la fréquence d'échantillonnage
    recognizer = KaldiRecognizer(model, 16000)

    # Initialiser PyAudio pour capturer l'audio du micro
    p = pyaudio.PyAudio()

    # Ouvrir un flux audio (stream) à partir du micro
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
    stream.start_stream()

    mot_cles_activation = ["mode normal", "mode passage", "mode panne", "mode urgence"]
    mot_cles_urgence = ["Direction numéro un", "Direction numéro deux"]

    print("Parlez dans le micro...")

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
                    pf.publish_pieton_command(client)
                    print(f"{transcribed_text}: Mode Pieton Allumer.")

                # Mode Panne - GOOD
                elif transcribed_text == mot_cles_activation[2].lower():
                    panne = "panne_on"
                    pf.publish_panne_command(client, panne)
                    print(f"{transcribed_text}: Mode Panne Allumer.")

                    mot_cles_panne = ["Sortir du mode panne", "mode urgence"]
                    print(
                        f"Dites '{mot_cles_panne[0]}' pour sortir du mode panne ou '{mot_cles_panne[1]}' pour passer en mode urgence: ")
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
                                pf.publish_panne_command(client, panne)
                            # Si mode urgence est appeler
                            elif transcribed_text_panne == mot_cles_panne[1].lower():
                                print(f"{transcribed_text_panne}: Mode Urgence Allumer.")
                                panneUrgence = ""
                                print(
                                    f"Dites '{mot_cles_urgence[0]}' ou '{mot_cles_urgence[1]}' pour activer le mode urgence: ")
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
                                            pf.publish_urgence_command(client, panneUrgence)
                                        elif transcribed_text_panneUrgence == mot_cles_urgence[1].lower():
                                            panneUrgence = "urgence_direction2"
                                            pf.publish_urgence_command(client, panneUrgence)
                                        else:
                                            print(f"{transcribed_text_panneUrgence}: reesaayer")
                                            time.sleep(1)
                            else:
                                print("Mauvaise entree, reesaayer")
                                time.sleep(1)

                # Mode Urgence - GOOD
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
                                pf.publish_urgence_command(client, urgence)
                            elif transcribed_text_Urgence == mot_cles_urgence[1].lower():
                                urgence = "urgence_direction2"
                                pf.publish_urgence_command(client, urgence)
                            else:
                                print(f"{transcribed_text_Urgence}: reesaayer")
                                time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        # Fermer le flux et PyAudio
        stream.stop_stream()
        stream.close()
        p.terminate()

def start_voice_recognition():
    # Start the voice recognition in a separate process or thread
    import threading
    voice_thread = threading.Thread(target=run_voice_recognition)
    voice_thread.start()
    return voice_thread

def stop_voice_recognition(voice_thread):
    # Stop the voice recognition thread
    if voice_thread and voice_thread.is_alive():
        voice_thread.join(timeout=1)  # Wait for the thread to finish

if __name__ == "__main__":
    try:
        voice_thread = start_voice_recognition()
        voice_thread.join()  # Wait for the thread to finish if running as main
    finally:
        # Deconnecter de MQTT
        client.loop_stop()
        client.disconnect()