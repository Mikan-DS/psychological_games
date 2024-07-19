import string
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

        api.messages.send(
            user_id=user.username,
            message=f"Ваш код для входа: {confirmation_code.code}\nТак-же вы можете зайти по ссылке\n"
                    f"{settings.host_url}auth/login/{user.id}/{confirmation_code.code}",
            random_id=0)

        print(confirmation_code.code)

        return True
    except Exception as e:
        return False
