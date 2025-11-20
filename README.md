# Cryptend

End-to-end encrypted messaging tool for desktop.

## Installation

### Windows

Install [Git](https://git-scm.com/install/windows)

Install [Python](https://www.python.org/downloads/) (Add python.exe to PATH)

Open a terminal and clone the repository:

```bash
git clone https://github.com/cryptend/cryptend-app.git
```

Run `install.bat` and `Cryptend.bat` or enter the commands:

```bash
cd cryptend-app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask run
```

Open `http://127.0.0.1:5000/`

Update:

```bash
git pull
venv\Scripts\activate
pip install -r requirements.txt
```

### macOS

Install [Homebrew](https://brew.sh/) if you don't already have it, then:

```bash
brew update
brew install git python
git clone https://github.com/cryptend/cryptend-app.git
cd cryptend-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
flask run
```

Update:

```bash
git pull
source venv/bin/activate
pip install -r requirements.txt
```

### Ubuntu

```bash
sudo apt update
sudo apt install git python3-pip python3-venv
git clone https://github.com/cryptend/cryptend-app.git
cd cryptend-app
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
flask run
```

Update:

```bash
git pull
. venv/bin/activate
pip install -r requirements.txt
```

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

- [Flask](https://github.com/pallets/flask)
- [cryptography](https://github.com/pyca/cryptography)

### Development dependencies

- [tailwindcss](https://github.com/tailwindlabs/tailwindcss)
- [daisyUI](https://github.com/saadeghi/daisyui)
