import pyautogui
import time

image_path = r"C:\Users\dbait\Desktop\MOD LOL\script\Client.png"

time.sleep(5)  # Tempo per passare alla finestra corretta

location = pyautogui.locateOnScreen(image_path, confidence=0.8)
if location:
    print("Trovata:", location)
else:
    print("Immagine non trovata.")
