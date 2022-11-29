from http import HTTPStatus

from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .permissions import IsAdminOrSuper, IsAuth
from .serializers import GetTokenSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт users/
    Используется админами и суперпользователями.
    Исключение: users/me могут использовать авторизованные
    пользователи для просмотра и изменения своего профиля.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAdminOrSuper, )
    lookup_field = 'username'

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            username=self.kwargs[self.lookup_field]
        )
        return obj

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=(IsAuth, ))
    def me(self, request, pk=None):
        data = request.data.copy()
        user = get_object_or_404(User, username=request.user.username)

        if request.method == 'GET':
            serializer = self.serializer_class(user)
            return Response(serializer.data)

        if not request.user.is_admin and not request.user.is_superuser:
            role = request.user.role
            data['role'] = role

        serializer = self.serializer_class(
            user,
            data=data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserRegisterView(generics.GenericAPIView):
    """
    Регистрация нового пользователя.
    Принимаем username и email, высылаем на почту код.
    """
    serializer_class = UserSerializer

    def post(self, serializer):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user = User.objects.get(
            username=self.request.data['username'],
            email=self.request.data['email'],
            password=self.request.data['password'],
            last_name=self.request.data['last_name'],
            first_name=self.request.data['first_name'],
        )
        user.save()

        return Response({
            "username": self.request.data['username'],
            "email": self.request.data['email'],
        })


class UserGetTokenView(generics.GenericAPIView):
    """
    Получение токена в ответ на email и пароль
    """
    serializer_class = GetTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        user = get_object_or_404(
            User,
            email=email,
        )

        if user.password != password:
            return Response(status=HTTPStatus.BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        return Response(str(refresh.access_token))
