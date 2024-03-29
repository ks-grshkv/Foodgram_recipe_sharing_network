from http import HTTPStatus

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import CustomPagination

from .models import Subscription, User
from .permissions import IsAdminorOwner, IsAuth
from .serializers import (GetTokenSerializer, UpdatePasswordSerializer,
                          UserFollowReadSerializer, UserFollowWriteSerializer,
                          UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт users/
    """
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    queryset = User.objects.all()
    lookup_field = 'id'

    def get_serializer_context(self):
        """
        Дополнительные данные для контекста сериализатора.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'kwargs': self.kwargs
        }

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            id=self.kwargs[self.lookup_field]
        )
        return obj

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=(IsAdminorOwner,))
    def me(self, request, pk=None):
        """
        Просмотр своего профиля.
        """
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

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=(IsAuth, IsAdminorOwner),
        serializer_class=UserFollowWriteSerializer)
    def subscribe(self, *args, **kwargs):
        """
        Подписка на пользователя и отписка.
        """
        context = self.get_serializer_context()
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        if self.request.method == 'POST':
            serializer = self.serializer_class(
                data=self.request.data,
                context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        elif self.request.method == 'DELETE':
            subscription = get_object_or_404(
                Subscription,
                user=self.request.user,
                author=author
            )
            subscription.delete()
            return Response(status=HTTPStatus.NO_CONTENT)

    @action(
        detail=False,
        methods=['POST'],
        url_path='set_password',
        permission_classes=(IsAdminorOwner, ),
        serializer_class=UpdatePasswordSerializer
    )
    def set_password(self, request, pk=None):
        """
        Смена пароля.
        """
        user = get_object_or_404(User, id=self.request.user.id)
        new_password = self.request.data['new_password']
        current_password = self.request.data['current_password']
        if not authenticate(username=user.username, password=current_password):
            return Response(status=HTTPStatus.BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response(status=HTTPStatus.OK)


class SubscriptionView(viewsets.ModelViewSet):
    """
    Эндпоинт user/subscriptions/ .
    """
    serializer_class = UserFollowReadSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuth, )

    def get_serializer_context(self):
        """
        Дополнительные данные для сериализатора.
        """
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'kwargs': self.kwargs
        }

    def get_queryset(self):
        return self.request.user.followers.all()


class UserGetTokenView(generics.GenericAPIView):
    """
    Эндпоинт auth/token/login .
    Получение токена в ответ на email и пароль.
    """
    serializer_class = GetTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        user = User.objects.get(email=email)

        if not authenticate(username=user.username, password=password):
            return Response(status=HTTPStatus.BAD_REQUEST)

        Token.objects.filter(user=user).delete()
        refresh = Token.objects.create(user=user)
        return Response({"auth_token": str(refresh.key)})


class UserDeleteTokenView(generics.GenericAPIView):
    """
    Эндпоинт auth/token/logout .
    Удаление токена.
    """
    serializer_class = GetTokenSerializer
    permission_classes = (IsAuth, )

    def post(self, request):
        user = get_object_or_404(
            User,
            id=self.request.user.id,
        )
        refresh = get_object_or_404(Token, user=user)
        refresh.delete()
        return Response(status=HTTPStatus.NO_CONTENT)
