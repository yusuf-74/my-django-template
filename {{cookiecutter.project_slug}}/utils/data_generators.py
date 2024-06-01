import random


def generate_username(first_name, last_name):
    user_name = first_name + '_' + last_name
    user_name = user_name.lower()
    user_name = user_name + '_' + str(random.randint(1, 99999))
    return user_name


def generate_password():
    all_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890#$%&@!^*"
    password = []
    for _ in range(12):
        password.append(random.choice(all_chars))
    return ''.join(password)


def generate_otp():
    return random.randint(100000, 999999)
