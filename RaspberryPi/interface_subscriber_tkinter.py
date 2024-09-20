import tkinter as tk
from RaspberryPi import controleur_led_main as cl
from RaspberryPi.controleur_led_main import led_pins
import RPi.GPIO as GPIO

# Fonction pour detexter l'etat des led
def etat_led():
    # Etat led direction 1
    if cl.GPIO.input(led_pins['LED_DIR1_GREEN']) == GPIO.HIGH:  # si la led verte de la direction 1 est allumEe
        return "Led verte 1 allume"
    elif cl.GPIO.input(led_pins['LED_DIR1_YELLOW']) == GPIO.HIGH:  # si la led verte de la direction 1 est allumEe
        return "Led jaune 1 allume"
    elif cl.GPIO.input(led_pins['LED_DIR1_RED']) == GPIO.HIGH:  # si la led verte de la direction 1 est allumEe
        return "Led rouge 1 allume"
    elif cl.GPIO.input(led_pins['LED_DIR1_GREEN']) == GPIO.LOW:  # si la led verte de la direction 1 est ETEINTE
        return "Led verte 1 eteinte"
    elif cl.GPIO.input(led_pins['LED_DIR1_YELLOW']) == GPIO.LOW:  # si la led verte de la direction 1 est ETEINTE
        return "Led jaune 1 eteinte"
    elif cl.GPIO.input(led_pins['LED_DIR1_RED']) == GPIO.LOW:  # si la led verte de la direction 1 est ETEINTE
        return "Led rouge 1 eteinte"

    # Etat led direction 2
    if cl.GPIO.input(led_pins['LED_DIR2_GREEN']) == GPIO.HIGH:  # si la led verte de la direction 2 est allumEe
        return "Led verte 2 allume"
    elif cl.GPIO.input(led_pins['LED_DIR2_YELLOW']) == GPIO.HIGH:  # si la led verte de la direction 2 est allumEe
        return "Led jaune 2 allume"
    elif cl.GPIO.input(led_pins['LED_DIR2_RED']) == GPIO.HIGH:  # si la led verte de la direction 2 est allumEe
        return "Led rouge 2 allume"
    elif cl.GPIO.input(led_pins['LED_DIR2_GREEN']) == GPIO.LOW:  # si la led verte de la direction 2 est ETEINTE
        return "Led verte 2 eteinte"
    elif cl.GPIO.input(led_pins['LED_DIR2_YELLOW']) == GPIO.LOW:  # si la led verte de la direction 2 est ETEINTE
        return "Led jaune 2 eteinte"
    elif cl.GPIO.input(led_pins['LED_DIR2_RED']) == GPIO.LOW:  # si la led verte de la direction 2 est ETEINTE
        return "Led rouge 2 eteinte"

# Interface graphique Tkinter
root = tk.Tk()
root.title("Etat des feux de circulation")

# Creation d'un label pour afficher du texte dynamique pour la direction 1
led_verte_1 = tk.Label(root, text=etat_led())
led_verte_1.grid(row=0, column=0, pady=20)  # Utilisation correcte de row et column avec grid()

led_jaune_1 = tk.Label(root, text=etat_led())
led_jaune_1.grid(row=0, column=1, pady=20)  # Utilisation correcte de row et column avec grid()

led_rouge_1 = tk.Label(root, text=etat_led())
led_rouge_1.grid(row=0, column=2, pady=20)  # Utilisation correcte de row et column avec grid()

# Creation d'un label pour afficher du texte dynamique pour la direction 2
led_verte_2 = tk.Label(root, text=etat_led())
led_verte_2.grid(row=0, column=3, pady=20)  # Utilisation correcte de row et column avec grid()

led_jaune_2 = tk.Label(root, text=etat_led())
led_jaune_2.grid(row=0, column=4, pady=20)  # Utilisation correcte de row et column avec grid()

led_rouge_2 = tk.Label(root, text=etat_led())
led_rouge_2.grid(row=0, column=5, pady=20)  # Utilisation correcte de row et column avec grid()

try:
    # Lancement de l'interface graphique Tkinter
    root.mainloop()
except:
    print("Something went wrong")
