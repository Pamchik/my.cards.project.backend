from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import re

UserModel = get_user_model()

def custom_validation(data):
    email = data['email'].strip()
    username = data['username'].strip()
    password = data['password'].strip()
    ##
    if not email or UserModel.objects.filter(email=email).exists():
        raise ValidationError('choose another email')
    ##
    if not password or len(password) < 8:
        raise ValidationError('choose another password, min 8 characters')
    ##
    if not username:
        raise ValidationError('choose another username')
    return data


def validate_email(data):
    email = data['email'].strip()
    if not email:
        raise ValidationError('an email is needed')
    return True

def validate_username(data):
    username = data['username'].strip()
    if not username:
        raise ValidationError('choose another username')
    return True

def validate_password(data):
    password = data['password']
    if not password:
        return {'result': False, 'message': 'Не введен пароль'}
    if not password.isascii():
        return {'result': False, 'message': 'Пароль должен быть на латинице'}
    if len(password) < 8 or len(password) > 24:
        return {'result': False, 'message': 'Пароль должен содержать от 8 до 24 символов'}
    if not re.search(r'[A-Z]', password):
        return {'result': False, 'message': 'Пароль должен содержать хотя бы одну заглавную букву'}
    if not re.search(r'[a-z]', password):
        return {'result': False, 'message': 'Пароль должен содержать хотя бы одну строчную букву'}
    if not re.search(r'\d', password):
        return {'result': False, 'message': 'Пароль должен содержать хотя бы одну цифру'}
    if not re.match(r'^[~!?@#$%^&*_\-a-zA-Z0-9]+$', password):
        return {'result': False, 'message': 'Пароль содержит недопустимые символы'}
    

    return {'result': True, 'message': ''}