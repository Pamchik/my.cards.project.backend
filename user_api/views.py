from django.contrib.auth import get_user_model, login, logout, authenticate
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserRegisterSerializer, UserLoginSerializer
from rest_framework import permissions, status
from .validations import custom_validation, validate_email, validate_password
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone
from datetime import timedelta
from .models import AppUser
from rest_framework import viewsets
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError


class UserRegister(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request):
		clean_data = custom_validation(request.data)
		serializer = UserRegisterSerializer(data=clean_data)
		if serializer.is_valid(raise_exception=True):
			user = serializer.create(clean_data)
			if user:
				return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        data = request.data
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            # Проверка наличия пользователя с данным email
            try:
                user = AppUser.objects.get(email=email)
            except AppUser.DoesNotExist:
                return Response({'message': 'Пользователь не найден'}, status=status.HTTP_400_BAD_REQUEST)

            # Проверка пароля
            if not user.check_password(password):
                return Response({'message': 'Неверный пароль'}, status=status.HTTP_400_BAD_REQUEST)

            # Пользователь найден и пароль верный
            login(request, user)
            session = request.session or SessionStore()
            expiry_age = request.session.get_expiry_age()
            expiry_delta = timedelta(seconds=expiry_age)
            expire_date = timezone.now() + expiry_delta
            user_id = user.user_id

            return Response({
                'sessionid': session.session_key,
                'expire_date': expire_date,
                'user_id': user_id
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLogout(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def post(self, request):
		logout(request)
		return Response(status=status.HTTP_200_OK)

def user_check(request):

	session_id = request.GET.get('sessionid')
	if not session_id:
		return JsonResponse({'message': 'Не передан sessionid'}, status=400)

	try:
		session = Session.objects.get(session_key=session_id)
		session_data = session.get_decoded()
		user_id = session_data.get('_auth_user_id')

		user = AppUser.objects.get(pk=user_id)

		user_role_name = user.user_role.name if user.user_role else None	

		return JsonResponse({
			'username': user.username,
			'email': user.email,
			'active': user.is_active,
			'role': user_role_name,
		}, status=200)

	except Session.DoesNotExist:	
		return JsonResponse({'message': 'Недействительный sessionid'}, status=400)

class UserChangePassword(APIView):

	def post(self, request):

		# Проверка наличия sessionid
		session_id = request.data.get('sessionid')
		if not session_id:
			return Response(status=status.HTTP_400_BAD_REQUEST)
		
		# Получение данных пользователя из сессии
		try:
			session = Session.objects.get(session_key=session_id)
			session_data = session.get_decoded()
			user_id = session_data.get('_auth_user_id')

			user = AppUser.objects.get(pk=user_id)
		except (Session.DoesNotExist, AppUser.DoesNotExist):
			return Response({'message': 'Пользователь не найден'}, status=status.HTTP_400_BAD_REQUEST)

        # Получение данных из запроса
		current_password = request.data.get('password')
		new_password = request.data.get('new_password')
		repeat_password = request.data.get('repeat_password')

		# Проверка текущего пароля
		if not user.check_password(current_password):
			return Response({'message': 'Текущий пароль введен неверно'}, status=status.HTTP_400_BAD_REQUEST)

		# Проверка, что новый пароль не равен текущему
		if current_password == new_password:
			return Response({'message': 'Новый пароль не должен быть равен текущему'}, status=status.HTTP_400_BAD_REQUEST)

        # Проверка нового пароля
		is_password_currect = validate_password({'password': new_password})
		if not is_password_currect['result']:
			return Response({'message': is_password_currect['message']}, status=status.HTTP_400_BAD_REQUEST)
		
		# Проверка совпадения нового пароля и его подтверждения
		if new_password != repeat_password:
			return Response({'message': 'Пароли не совпадают'}, status=status.HTTP_400_BAD_REQUEST)

		# Обновление пароля пользователя
		try:
			user.set_password(new_password)
			user.save()
		except Exception as e:
			return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

		return Response('Изменение пароля прошло успешно', status=status.HTTP_200_OK)