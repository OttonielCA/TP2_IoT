import tkinter as tk
from publisher_functions import publish_pieton_command, publish_panne_command, publish_urgence_command, client, broker, port
import multiprocessing
from subscriber_mqtt_PC import run_subscriber
from publisher_vosk import start_voice_recognition, stop_voice_recognition
import threading
import queue

# Variables globales pour gérer l'état de l'application
val_panne = False
current_mode = "Mode Normal"
command_queue = queue.Queue()
current_window = None
previous_mode = "Mode Normal"
emergency_timer = None

# Fonctions pour gérer les différents modes et fenêtres
def update_status_panel():
    status_label.config(text=f"Mode actuel : {current_mode}")

# Fonction pour activer le mode piéton
def send_pieton_window():
    global current_mode
    publish_pieton_command(client)
    current_mode = "Mode Piéton"
    # update_status_panel()
    set_mode("Mode Piéton")

    status_label = tk.Label(root, text="Mode piéton envoyé")
    status_label.grid(row=4, column=0, columnspan=3, pady=20)

    root.after(15000, status_label.destroy)
    root.after(15000, lambda: set_mode("Mode Normal"))

# Fonction pour ouvrir la fenêtre du mode panne
def open_panne_window():
    global current_mode, val_panne, current_window
    root.withdraw()

    publish_panne_command(client, "panne_on")
    # current_mode = "Mode Panne"
    # update_status_panel()
    set_mode("Mode Panne")

    failure_window = tk.Toplevel(root)
    failure_window.title("Mode Panne")
    current_window = failure_window

    status_label = tk.Label(failure_window, text="Mode panne activé")
    status_label.grid(row=3, column=0, columnspan=2, pady=20)

    exit_failure_button = tk.Button(failure_window, text="Sortir du Mode Panne",
                                    command=lambda: exit_failure_mode(failure_window))
    exit_failure_button.grid(row=0, column=0, padx=20, pady=20)

    to_emergency_button = tk.Button(failure_window, text="Passer en Mode Urgence",
                                    command=lambda: pass_to_emergency(failure_window))
    to_emergency_button.grid(row=0, column=1, padx=20, pady=20)

# Fonction pour sortir du mode panne
def exit_failure_mode(failure_window):
    global current_mode, current_window
    publish_panne_command(client, "panne_off")
    # current_mode = "Mode Normal"
    # update_status_panel()
    set_mode("Mode Normal")

    if failure_window:
        failure_window.destroy()
    current_window = None
    root.deiconify()

    panne_label = tk.Label(root, text="Mode panne: off")
    panne_label.grid(row=4, column=0, columnspan=3, pady=20)

    root.after(5000, panne_label.destroy)

# Fonction pour passer au mode urgence depuis le mode panne
def pass_to_emergency(failure_window):
    global val_panne, current_mode
    val_panne = True
    current_mode = "Mode Urgence"
    update_status_panel()
    failure_window.withdraw()
    open_urgence_window(failure_window)

# Fonction pour ouvrir la fenêtre du mode urgence
def open_urgence_window(failure_window):
    global current_mode, current_window
    if failure_window:
        failure_window.withdraw()
    else:
        root.withdraw()

    current_mode = "Mode Urgence"
    update_status_panel()

    emergency_window = tk.Toplevel(root)
    emergency_window.title("Mode Urgence")
    current_window = emergency_window

    direction1 = tk.Button(emergency_window, text="Direction 1 au vert",
                           command=lambda: publish_command1(emergency_window, failure_window))
    direction1.grid(row=0, column=0, padx=20, pady=20)

    direction2 = tk.Button(emergency_window, text="Direction 2 au vert",
                           command=lambda: publish_command2(emergency_window, failure_window))
    direction2.grid(row=0, column=1, padx=20, pady=20)

# Fonction pour publier la commande d'urgence direction 1
def publish_command1(emergency_window, failure_window):
    global val_panne, current_mode, current_window
    publish_urgence_command(client, "urgence_direction1")
    emergency_window.destroy()
    set_mode("Mode Urgence - Direction 1", 20)

    if val_panne:
        val_panne = False
        failure_window.deiconify()
        # current_mode = "Mode Panne"
        current_window = failure_window
    else:
        root.deiconify()
        # current_mode = "Mode Normal"
        current_window = None

    # update_status_panel()

    urgence1_label = tk.Label(root, text="Mode urgence 1 envoyé")
    urgence1_label.grid(row=4, column=0, columnspan=3, pady=20)
    root.after(5000, urgence1_label.destroy)

# Fonction pour publier la commande d'urgence direction 2
def publish_command2(emergency_window, failure_window):
    global val_panne, current_mode, current_window
    publish_urgence_command(client, "urgence_direction2")
    emergency_window.destroy()
    set_mode("Mode Urgence - Direction 2", 20)

    if val_panne:
        val_panne = False
        failure_window.deiconify()
        # current_mode = "Mode Panne"
        current_window = failure_window
    else:
        root.deiconify()
        # current_mode = "Mode Normal"
        current_window = None

    # update_status_panel()

    urgence2_label = tk.Label(root, text="Mode urgence 2 envoyé")
    urgence2_label.grid(row=4, column=0, columnspan=3, pady=20)
    root.after(5000, urgence2_label.destroy)

# Fonction pour définir le mode actuel et gérer le timer en mode urgence
def set_mode(mode, duration=None):
    global current_mode, previous_mode
    if current_mode != "Mode Urgence":
        previous_mode = current_mode
    current_mode = mode
    update_status_panel()

    if duration:
        global emergency_timer
        if emergency_timer:
            emergency_timer.cancel()
        emergency_timer = threading.Timer(duration, lambda: set_mode(previous_mode))
        emergency_timer.start()

# Fonction appelée lors de la fermeture de l'application
def on_closing():
    global emergency_timer
    if emergency_timer:
        emergency_timer.cancel()
    root.quit()

# Fonction pour traiter les commandes vocales reçues
def process_voice_commands():
    global root
    while True:
        try:
            command = command_queue.get(block=False)
            if command == "pieton":
                root.after(0, send_pieton_window)
                show_voice_command_label("Mode Piéton")
            elif command == "panne":
                root.after(0, open_panne_window)
                show_voice_command_label("Mode Panne")
            elif command == "panne_off":
                root.after(0, lambda: exit_failure_mode(current_window))
                show_voice_command_label("Mode Panne off")
            elif command == "urgence":
                root.after(0, lambda: open_urgence_window(None))
                show_voice_command_label("Mode Urgence")
            elif command == "urgence_direction1":
                if current_window:
                    root.after(0, lambda: publish_command1(current_window, current_window))
                    show_voice_command_label("Urgence Direction 1")
            elif command == "urgence_direction2":
                if current_window:
                    root.after(0, lambda: publish_command2(current_window, current_window))
                    show_voice_command_label("Urgence Direction 2")
            elif command == "normal":
                if current_window:
                    current_window.destroy()
                root.after(0, lambda: set_mode("Mode Normal"))
                root.after(0, root.deiconify)
                show_voice_command_label("Mode Normal")
        except queue.Empty:
            break
    root.after(100, process_voice_commands)

# Fonction pour afficher les commandes vocales reçues
def show_voice_command_label(command_text):
    global root
    voice_command_label = tk.Label(root, text=f"Voice Command: {command_text}", font=("Arial", 12))
    voice_command_label.grid(row=5, column=0, columnspan=3, pady=10)
    root.after(5000, voice_command_label.destroy)

# Callback pour les commandes vocales
def voice_command_callback(command):
    command_queue.put(command)

if __name__ == "__main__":
    # Démarrage du processus d'abonnement MQTT
    subscriber_process = multiprocessing.Process(target=run_subscriber)
    subscriber_process.start()

    # Démarrage de la reconnaissance vocale
    voice_thread = start_voice_recognition(voice_command_callback)

    # Configuration de l'interface graphique Tkinter
    root = tk.Tk()
    root.title("Gestion des Feux de Croisement")

    # Création des boutons et labels
    status_label = tk.Label(root, text=f"Mode actuel : {current_mode}", font=("Arial", 14, "bold"))
    status_label.grid(row=0, column=0, columnspan=3, pady=20)

    pedestrian_button = tk.Button(root, text="Mode Piéton", command=send_pieton_window)
    pedestrian_button.grid(row=2, column=0, padx=20, pady=20)

    failure_button = tk.Button(root, text="Mode Panne", command=open_panne_window)
    failure_button.grid(row=2, column=1, padx=20, pady=20)

    emergency_button = tk.Button(root, text="Mode Urgence", command=lambda: open_urgence_window(None))
    emergency_button.grid(row=2, column=2, padx=20, pady=20)

    root.after(100, process_voice_commands)

    # Boucle principale de l'application
    try:
        root.protocol("WM_DELETE_WINDOW", on_closing)
        root.mainloop()
    finally:
        # Nettoyage et fermeture des ressources
        client.loop_stop()
        client.disconnect()
        subscriber_process.terminate()
        subscriber_process.join()
        stop_voice_recognition(voice_thread)