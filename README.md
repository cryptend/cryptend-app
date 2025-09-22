# Cryptend

End-to-end encrypted messaging tool for desktop.

## Installing

1. Install [Python](https://www.python.org/downloads/).
2. Download [Cryptend](https://github.com/cryptend/cryptend-app/archive/refs/heads/main.zip) and unzip it.
3. Run `install.py` (this will execute `python -m pip install -r requirements.txt`).
4. Run `run.py` (this will execute `flask run` and open `http://127.0.0.1:5000/`).

## Usage

1. Click on `Create chat`, create your configuration and send it to your interlocutor.
2. Your interlocutor must click on `Accept Chat`, create their configuration and send it to you.
3. Add the chat and start the conversation.

## Algorithm

1. Argon2id for converting a password into a private key.
2. Diffie-Hellman key exchange to obtain a shared key.
3. Argon2id for deriving the encryption key.
4. AES-256 (CBC) for message encryption.

## Dependencies

- [cryptography](https://github.com/pyca/cryptography)
- [Flask](https://github.com/pallets/flask)

### Development

- [tailwindcss](https://github.com/tailwindlabs/tailwindcss)
- [daisyui](https://github.com/saadeghi/daisyui)
