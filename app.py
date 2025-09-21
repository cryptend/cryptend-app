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

DEFAULT_ARGON2 = {
    'password': b'Cryptend-Password',
    'salt': b'Cryptend-Salt',
    'iterations': 1,
    'lanes': 4,
    'memory_cost': 64 * 1024,
}


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
        iterations=DEFAULT_ARGON2['iterations'],
        lanes=DEFAULT_ARGON2['lanes'],
        memory_cost=DEFAULT_ARGON2['memory_cost'],
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
    padder = padding.PKCS7(128).padder()
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
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_data) + unpadder.finalize()
    return plaintext.decode()


def generate_chat_name():
    while True:
        name = os.urandom(10).hex()
        path = os.path.join('backup', f'{name}.json')
        if not os.path.exists(path):
            return name


def get_default_key() -> bytes:
    kdf = Argon2id(
        salt=DEFAULT_ARGON2['salt'],
        length=32,
        iterations=DEFAULT_ARGON2['iterations'],
        lanes=DEFAULT_ARGON2['lanes'],
        memory_cost=DEFAULT_ARGON2['memory_cost'],
    )
    return kdf.derive(DEFAULT_ARGON2['password'])


def encrypt_configuration(data: dict) -> str:
    conf = '_'.join([str(i) for i in data.values()])
    key = get_default_key()
    return encrypt_message(conf, key)


def decrypt_configuration(encrypted_conf: str) -> dict:
    key = get_default_key()
    conf = decrypt_message(encrypted_conf, key)
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


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'conf' in request.form:
            conf = request.form['conf'].strip()
            data = decrypt_configuration(conf)
            name = generate_chat_name()
            data['messages'] = []
            save_chat(name, data)
            return redirect('/')
    if not os.path.exists('backup'):
        os.makedirs('backup')
    chats = []
    for file in os.listdir('backup'):
        if file.endswith('.json'):
            name = os.path.splitext(file)[0]
            data = get_chat(name)
            chats.append((name, len(data['messages'])))
    return render_template('home.html', chats=chats)


@app.route('/1', methods=['GET', 'POST'])
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
        conf = encrypt_configuration(data)
        context = {
            'key_size': key_size,
            'iterations': iterations,
            'memory': memory,
            'parallelism': parallelism,
            'conf': conf,
        }
        return render_template('create_chat.html', **context)
    context = {
        'key_size': 1500,
        'iterations': 30,
        'memory': 128,
        'parallelism': 4,
    }
    return render_template('create_chat.html', **context)


@app.route('/2', methods=['GET', 'POST'])
def accept_chat():
    if request.method == 'POST':
        inter_conf = request.form['conf'].strip()
        password = request.form['password']
        data = decrypt_configuration(inter_conf)
        private_key = get_private_key(data['salt'], data['p'], password)
        public_key = get_public_key(data['g'], private_key, data['p'])
        data['public_key'] = public_key
        conf = encrypt_configuration(data)
        return render_template('accept_chat.html', inter_conf=inter_conf, conf=conf)
    return render_template('accept_chat.html')


@app.route('/3/<name>', methods=['GET', 'POST'])
def chat(name):
    data = get_chat(name)
    context = {'name': name}
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
        if 'message' in request.form:
            message = request.form['message'].strip()
            output = encrypt_message(message, key)
            data['messages'].append([1, output])
            context['message'] = message
            context['encrypted_output'] = output
            save_chat(name, data)
        elif 'encrypted_message' in request.form:
            encrypted_message = request.form['encrypted_message'].strip()
            try:
                output = decrypt_message(encrypted_message, key)
                data['messages'].append([2, encrypted_message])
            except ValueError:
                output = ''
            context['encrypted_message'] = encrypted_message
            context['decrypted_output'] = output
            save_chat(name, data)
        messages = []
        for i in data['messages']:
            try:
                output = decrypt_message(i[1], key)
                messages.append((i[0], output, 'd'))
            except ValueError:
                messages.append((i[0], i[1], 'e'))
        context['messages'] = messages
        return render_template('chat.html', **context)
    messages = []
    for i in data['messages']:
        messages.append((i[0], i[1], 'e'))
    context['messages'] = messages
    return render_template('chat.html', **context)
