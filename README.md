# Cryptend

End-to-end encryption messaging tool for desktop.

## Installing

1. Download [Cryptend](https://github.com/cryptend/cryptend-app/archive/refs/heads/main.zip) and unzip it
2. Install [Python](https://www.python.org/downloads/)
3. Run `install.bat` (`pip install -r requirements.txt`)
4. Run `Cryptend.bat` (`flask run`)

## Usage

1. Open the `Create chat` page, adjust the parameters, set a password, create a configuration and send it to your interlocutor.
2. Your interlocutor should open the `Accept chat` page, paste your configuration, set a password, create a configuration and send it to you.
3. Open the `Add chat` page, paste interlocutor's configuration and add chat.

## Algorithm

1. SHAKE256 to convert a password to a private key
2. Diffie-hellman key exchange to get a shared key
3. Argon2id to get the encryption key
4. AES-256 (CBC) for message encryption

## Dependencies

- [cryptography](https://github.com/pyca/cryptography) `45.0.5`
- [Flask](https://github.com/pallets/flask) `3.1.1`

### Development

- [tailwindcss](https://github.com/tailwindlabs/tailwindcss) `4.1.11`
- [daisyui](https://github.com/saadeghi/daisyui) `5.0.48`
