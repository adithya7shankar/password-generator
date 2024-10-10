import random
import string
from cryptography.fernet import Fernet
from flet import *
import flet as ft 
# Function to generate password
def generate_password(min_length, special_characters=True):
    keys = ['299', '792', '458', '7829', '224', '999', '0502', '1301', '63', '1224', '2499', '1999']
    phrases = ['dei', 'lol', 'what', 'honeypot', 'Horizon', 'Whisper', 'Catalyst', 'Ember', 'Quantum', 'Serendipity',
               'Nebula', 'Vortex', 'Echo', 'Solitude', 'Velocity', 'Mirage', 'Labyrinth', 'Paradox', 'Zephyr']
    special = string.punctuation

    characters = keys + phrases
    if special_characters:
        characters += special

    pwd = ["A"]  # Start password with an uppercase letter (just an example)
    meet_criteria = False
    has_phrase = False
    has_special = False

    while not meet_criteria or len(pwd) < min_length:
        new_char = random.choice(characters)
        if new_char in pwd:
            continue
        pwd.append(new_char)

        if new_char in phrases:
            has_phrase = True
        if new_char in special:
            has_special = True
        meet_criteria = True

        # Ensure that special characters are included if required
        if special_characters:
            meet_criteria = has_special and has_phrase

    # Optionally, append 's!' as specified
    pwd.append('s!')
    
    # Join the password list into a single string
    password = ''.join(pwd)
    
    print("Generated password:", password)
    return password



# Generate encryption key using cryptography library
key = Fernet.generate_key()

# Create a cipher object using the key
cipher = Fernet(key)

# Generate password and encrypt it
data = generate_password(5)  # Generate a password of minimum length 5
encrypted_data = cipher.encrypt(data.encode())  # Encrypt the generated password

# Save the encrypted password to a file
with open("passwords.txt", "wb") as f:
    f.write(encrypted_data)

# Save the encryption key to a file for decryption later
with open("passwords_encryption_key.key", "wb") as key_file:
    key_file.write(key)

print("Data encrypted and saved to passwords.txt")
print("Encryption key saved to passwords_encryption_key.key")


def main(page: ft.Page):
    page.title = "Generator for me"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    password_size_number: TextField = TextField(value = '0', text_align = ft.TextAlign.RIGHT, width = 100)
    def decrement( e: ControlEvent):
        password_size_number.value = str(int(password_size_number.value) - 1)
        page.update()
    def increment( e: ControlEvent):
        password_size_number.value = str(int(password_size_number.value) + 1)
        page.update()    
    
    def size_change():
        password_size_number.value = str(int(value))
    
    page.add(
        ft.Row(
        control=[
            ft.IconButton(icon=ft.icons.REMOVE, on_click=decrement),
            password_size_number,
            ft.IconButton(icon=ft.icons.ADD, on_click=increment)
        ],
        alignment=ft.MainAxisAlignment.CENTER  # Or any other valid alignment option
                )
        )

    page.h1("Generator for me")
    page.p("This is a simple password generator that generates a password of minimum length 5 and encrypts it using the Fernet symmetric encryption algorithm.")
    page.p("The encrypted password is saved to passwords.txt and the encryption key is saved to passwords_encryption_key.key.")
    page.p("The generated password is also displayed below.")
    page.p("Generated password: " + data)
    page.p("Data encrypted and saved to passwords.txt")
    page.p("Encryption key saved to passwords_encryption_key.key")

if __name__ == "__main__":
    ft.app(target=main)