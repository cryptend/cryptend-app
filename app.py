import base64
import json
import math
import os
import random
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.argon2 import Argon2id
from flask import Flask, request, render_template, redirect


def generate_dh_parameters(key_size: int) -> tuple[int, int]:
    g = random.choice([2, 5])
    numbers = dh.generate_parameters(g, key_size).parameter_numbers()
    return numbers.g, numbers.p


def generate_salt_b64() -> str:
    return base64.b64encode(os.urandom(32)).decode()


def get_private_key(salt_b64: str, p: int, password: str) -> int:
    kdf = Argon2id(
        salt=base64.b64decode(salt_b64),
        length=math.floor(p.bit_length() / 8),
        iterations=1,
        lanes=4,
        memory_cost=64 * 1024,
    )
    return int.from_bytes(kdf.derive(password.encode()))


def get_public_key(g: int, private_key: int, p: int) -> int:
    return pow(g, private_key, p)


def get_shared_key(interlocutor_public_key: int, private_key: int, p: int) -> int:
    return pow(interlocutor_public_key, private_key, p)


def get_encryption_key(
        salt_b64: str,
        iterations: int,
        memory: int,
        parallelism: int,
        shared_key: int,
    ) -> bytes:
    salt = base64.b64decode(salt_b64)
    kdf = Argon2id(
        salt=salt,
        length=32,
        iterations=iterations,
        lanes=parallelism,
        memory_cost=memory * 1024,
    )
    length = math.ceil(shared_key.bit_length() / 8)
    return kdf.derive(shared_key.to_bytes(length))


def encrypt_message(plaintext: str, key: bytes) -> str:
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES256(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(algorithms.AES256.block_size).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    iv_b64 = base64.b64encode(iv).decode()
    ciphertext_b64 = base64.b64encode(ciphertext).decode()
    return iv_b64 + ciphertext_b64


def decrypt_message(message: str, key: bytes) -> str:
    iv = base64.b64decode(message[:24])
    ciphertext = base64.b64decode(message[24:])
    cipher = Cipher(algorithms.AES256(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(ciphertext) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES256.block_size).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()
    return plaintext.decode()


def generate_chat_name():
    while True:
        name = os.urandom(10).hex()
        path = os.path.join('backup', f'{name}.json')
        if not os.path.exists(path):
            return name


def configuration_to_str(conf: dict) -> str:
    return '_'.join([str(i) for i in conf.values()])


def configuration_to_dict(conf: str) -> dict:
    keys = (
        'g',
        'p',
        'public_key',
        'salt',
        'iterations',
        'memory',
        'parallelism',
    )
    conf_list = conf.split('_')
    data = {}
    for i in range(len(keys)):
        if keys[i] == 'salt':
            data[keys[i]] = conf_list[i]
        else:
            data[keys[i]] = int(conf_list[i])
    return data


def get_chat(name: str) -> dict:
    if not os.path.exists('backup'):
        os.makedirs('backup')
    path = os.path.join('backup', f'{name}.json')
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)


def save_chat(name: str, data: dict) -> None:
    if not os.path.exists('backup'):
        os.makedirs('backup')
    path = os.path.join('backup', f'{name}.json')
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2)


app = Flask(__name__)


@app.get('/')
def home():
    if not os.path.exists('backup'):
        os.makedirs('backup')
    chats = []
    for file in os.listdir('backup'):
        if file.endswith('.json'):
            name = os.path.splitext(file)[0]
            data = get_chat(name)
            chats.append((name, len(data['messages'])))
    return render_template('home.html', chats=chats)


@app.route('/create-chat', methods=['GET', 'POST'])
def create_chat():
    if request.method == 'POST':
        key_size = int(request.form['key_size'])
        iterations = int(request.form['iterations'])
        memory = int(request.form['memory'])
        parallelism = int(request.form['parallelism'])
        password = request.form['password']
        g, p = generate_dh_parameters(key_size)
        salt_b64 = generate_salt_b64()
        private_key = get_private_key(salt_b64, p, password)
        public_key = get_public_key(g, private_key, p)
        data = {
            'g': g,
            'p': p,
            'public_key': public_key,
            'salt': salt_b64,
            'iterations': iterations,
            'memory': memory,
            'parallelism': parallelism,
        }
        conf = configuration_to_str(data)
        return render_template('create_chat.html', label='Configuration', output=conf)
    return render_template('create_chat.html')


@app.route('/accept-chat', methods=['GET', 'POST'])
def accept_chat():
    if request.method == 'POST':
        conf = request.form['conf']
        password = request.form['password']
        data = configuration_to_dict(conf)
        private_key = get_private_key(data['salt'], data['p'], password)
        public_key = get_public_key(data['g'], private_key, data['p'])
        data['public_key'] = public_key
        output = configuration_to_str(data)
        return render_template('accept_chat.html', label='Configuration', output=output)
    return render_template('accept_chat.html')


@app.route('/add-chat', methods=['GET', 'POST'])
def add_chat():
    if request.method == 'POST':
        conf = request.form['conf']
        data = configuration_to_dict(conf)
        name = generate_chat_name()
        data['messages'] = []
        save_chat(name, data)
        return redirect('/')
    return render_template('add_chat.html')


@app.route('/chat/<name>', methods=['GET', 'POST'])
def chat(name):
    data = get_chat(name)
    if request.method == 'POST':
        password = request.form['password']
        private_key = get_private_key(data['salt'], data['p'], password)
        shared_key = get_shared_key(data['public_key'], private_key, data['p'])
        key = get_encryption_key(
            data['salt'],
            data['iterations'],
            data['memory'],
            data['parallelism'],
            shared_key,
        )
        messages = []
        for i in data['messages']:
            output = decrypt_message(i[1], key)
            messages.append([i[0], output])
        return render_template('chat.html', name=name, messages=messages)
    messages = data['messages']
    return render_template('chat.html', name=name, messages=messages, encrypted=True)


@app.route('/chat/<name>/add-message', methods=['GET', 'POST'])
def add_message(name):
    if request.method == 'POST':
        message = request.form['message']
        password = request.form['password']
        operation = request.form['operation']
        data = get_chat(name)
        private_key = get_private_key(data['salt'], data['p'], password)
        shared_key = get_shared_key(data['public_key'], private_key, data['p'])
        key = get_encryption_key(
            data['salt'],
            data['iterations'],
            data['memory'],
            data['parallelism'],
            shared_key,
        )
        label = ''
        output = ''
        if operation == 'encrypt':
            output = encrypt_message(message, key)
            data['messages'].append([1, output])
            label = 'Encrypted message'
        elif operation == 'decrypt':
            output = decrypt_message(message, key)
            data['messages'].append([2, message])
            label = 'Decrypted message'
        save_chat(name, data)
        return render_template('add_message.html', name=name, label=label, output=output)
    return render_template('add_message.html', name=name)
