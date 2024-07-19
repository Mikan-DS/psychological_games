import hashlib
import string
import time
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime

from authorization.models import Settings, ConfirmationCode
from authorization.utils import generate_random_code


def generate_and_send_login_code(api, user: User):
    settings = Settings.objects.first()

    try:

        expiry_duration = settings.confirmation_code_expiry if settings else timedelta(days=1)
        expires_at = datetime.now() + expiry_duration
        code = generate_random_code(4, string.digits)
        confirmation_code = ConfirmationCode(user=user, code=code, expires_at=expires_at)
        confirmation_code.save()

        write_message(
            api,
            user.username,
            f"Ваш код для входа: {confirmation_code.code}\nТак-же вы можете зайти по ссылке\n"
            f"{settings.host_url}auth/login/{user.id}/{confirmation_code.code}"
        )

        print(confirmation_code.code)

        return True
    except Exception as e:
        return False


def get_custom_hash(input_string):
    # Получение последних 5 цифр хеш-суммы строки
    hash_object = hashlib.sha256(input_string.encode())
    hash_hex = hash_object.hexdigest()
    hash_number = int(hash_hex, 16)
    last_5_digits = str(hash_number)[-5:]

    # Получение текущей даты и времени в наносекундах
    current_time_nanos = time.time_ns()

    # Возвращение числа в формате [последние 5 цифр хеш-суммы строки][текущая дата и время в наносекундах]
    return int(f"{last_5_digits}{current_time_nanos}")


def write_message(api, user_id, message):
    api.messages.send(
        user_id=user_id,
        message=message,
        random_id=get_custom_hash(message))
