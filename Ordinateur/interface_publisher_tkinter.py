import tkinter as tk
from commandeur_fonction import publish_pieton_command, publish_panne_command, publish_urgence_command, client, broker, port

val_panne = False

# Fonction pour passer à la fenêtre du mode panne
def open_panne_window():
    # Masquer la fenêtre principale
    root.withdraw()

    # Envoyer la requête pour passer au mode panne
    publish_panne_command(client, "panne_on")

    # Créer une nouvelle fenêtre pour le mode panne
    failure_window = tk.Toplevel(root)
    failure_window.title("Mode Panne")

    # Création d'un label pour afficher du texte
    status_label = tk.Label(failure_window, text="Mode panne activé")
    status_label.grid(row=3, column=0, pady=20)  # Utilisation correcte de row et column avec grid()

    # Bouton pour sortir du mode panne
    exit_failure_button = tk.Button(failure_window, text="Sortir du Mode Panne", command=lambda: exit_failure_mode(failure_window))
    exit_failure_button.grid(row=0, column=0, padx=20, pady=20)

    # Bouton pour passer en mode urgence
    to_emergency_button = tk.Button(failure_window, text="Passer en Mode Urgence", command=lambda: pass_to_emergency(failure_window))
    to_emergency_button.grid(row=0, column=1, padx=20, pady=20)

# Fonction pour sortir du mode panne
def exit_failure_mode(failure_window):
    publish_panne_command(client, "panne_off")  # Sortir du mode panne

    failure_window.destroy()  # Fermer la fenêtre mode panne

    root.deiconify()  # Réafficher la fenêtre principale

    # Création d'un label pour afficher du texte dynamique
    panne_label = tk.Label(root, text="Mode panne: off")
    panne_label.grid(row=3, column=0, pady=20)  # Utilisation correcte de row et column avec grid()

    # Utilisation de after() pour détruire le label après 5 secondes (5000 millisecondes)
    root.after(5000, panne_label.destroy)

# Fonction pour passer en mode urgence depuis la fenêtre mode panne
def pass_to_emergency(failure_window):
    global val_panne
    val_panne = True
    failure_window.withdraw()  # Fermer la fenêtre mode panne
    open_urgence_window(failure_window)

# Fonction pour passer à la fenêtre du mode urgence
def open_urgence_window(failure_window):
    # Masquer la fenêtre principale
    root.withdraw()

    # Créer une nouvelle fenêtre pour le mode urgence
    emergency_window = tk.Toplevel(root)
    emergency_window.title("Mode Urgence")

    # Bouton pour mettre la direction 1 au vert
    direction1 = tk.Button(emergency_window, text="Direction 1 au vert", command=lambda: publish_command1(emergency_window, failure_window))
    direction1.grid(row=0, column=0, padx=20, pady=20)

    # Bouton pour revenir au mode panne
    direction2 = tk.Button(emergency_window, text="Direction 2 au vert", command=lambda: publish_command2(emergency_window, failure_window))
    direction2.grid(row=0, column=1, padx=20, pady=20)

def publish_command1(emergency_window, failure_window):
    global val_panne

    publish_urgence_command(client, "urgence_direction1")

    emergency_window.destroy()  # Fermer la fenêtre mode urgence

    if val_panne:
        val_panne = False
        failure_window.deiconify()  # Réafficher la fenêtre panne
        # Création d'un label pour afficher du texte dynamique
        urgence1_label = tk.Label(failure_window, text="Mode urgence 1 envoyé")
        urgence1_label.grid(row=3, column=0, pady=20)  # Utilisation correcte de row et column avec grid()

        # Utilisation de after() pour détruire le label après 5 secondes (5000 millisecondes)
        failure_window.after(5000, urgence1_label.destroy)
    else:
        root.deiconify()  # Réafficher la fenêtre principale

    # Création d'un label pour afficher du texte dynamique
    urgence1_label = tk.Label(root, text="Mode urgence 1 envoyé")
    urgence1_label.grid(row=3, column=0, pady=20)  # Utilisation correcte de row et column avec grid()

    # Utilisation de after() pour détruire le label après 5 secondes (5000 millisecondes)
    root.after(5000, urgence1_label.destroy)

def publish_command2(emergency_window, failure_window):
    global val_panne
    publish_urgence_command(client, "urgence_direction2")
    emergency_window.destroy()  # Fermer la fenêtre mode urgence
    if val_panne:
        val_panne = False
        failure_window.deiconify()  # Réafficher la fenêtre panne

        # Création d'un label pour afficher du texte dynamique
        urgence2_label = tk.Label(failure_window, text="Mode urgence 2 envoyé")
        urgence2_label.grid(row=3, column=0, pady=20)  # Utilisation correcte de row et column avec grid()

        # Utilisation de after() pour détruire le label après 5 secondes (5000 millisecondes)
        failure_window.after(5000, urgence2_label.destroy)
    else:
        root.deiconify()  # Réafficher la fenêtre principale

    # Création d'un label pour afficher du texte dynamique
    urgence2_label = tk.Label(root, text="Mode urgence 2 envoyé")
    urgence2_label.grid(row=3, column=0, pady=20)  # Utilisation correcte de row et column avec grid()

    # Utilisation de after() pour détruire le label après 5 secondes (5000 millisecondes)
    root.after(5000, urgence2_label.destroy)


def send_pieton_window():
    # Envoie de la requete pour le mode pieton
    publish_pieton_command(client)

    # Création d'un label pour afficher du texte dynamique
    status_label = tk.Label(root, text="Mode piéton envoyé")
    status_label.grid(row=3, column=0, pady=20)  # Utilisation correcte de row et column avec grid()

    # Utilisation de after() pour détruire le label après 5 secondes (5000 millisecondes)
    root.after(5000, status_label.destroy)



# Interface graphique Tkinter
root = tk.Tk()
root.title("Gestion des Feux de Croisement")

# Boutons pour changer de mode
pedestrian_button = tk.Button(root, text="Mode Piéton", command=send_pieton_window)
pedestrian_button.grid(row=2, column=0, padx=20, pady=20)

failure_button = tk.Button(root, text="Mode Panne", command=open_panne_window)
failure_button.grid(row=2, column=1, padx=20, pady=20)

emergency_button = tk.Button(root, text="Mode Urgence", command=lambda: open_urgence_window(None))
emergency_button.grid(row=2, column=2, padx=20, pady=20)

try:
    # Lancement de l'interface graphique Tkinter
    root.mainloop()

finally:
    # Arrêter la boucle MQTT après la fermeture de l'interface
    client.loop_stop()
    client.disconnect()