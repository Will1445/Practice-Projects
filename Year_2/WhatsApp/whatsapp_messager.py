import pywhatkit as kit
import pyautogui
import time

# Phone number (including country code) and message
phone_number = "+447541717922"  
message = "Wadup"


kit.sendwhatmsg_instantly(phone_number, message)

time.sleep(1)

pyautogui.press('enter')


