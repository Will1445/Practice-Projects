import pywhatkit as kit
import pyautogui
import time

# Phone number (including country code) and message
phone_number = "+447778215119"  # Replace with the recipient's phone number
message = "I think so, I just sent you this message using a python script"

# Send message instantly
kit.sendwhatmsg_instantly(phone_number, message)

# Wait for a few seconds to allow WhatsApp Web to finish typing
time.sleep(1)

# Simulate pressing the "Enter" key to send the message
pyautogui.press('enter')


