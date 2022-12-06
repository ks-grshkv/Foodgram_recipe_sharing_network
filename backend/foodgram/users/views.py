from http import HTTPStatus
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Subscription
from .permissions import IsAdminorOwner, IsAuth
from .serializers import (
    GetTokenSerializer,
    UserSerializer,
    SubscriptionSerializer,
    UpdatePasswordSerializer,
    UserWithRecipesSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт users/
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'id'

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            id=self.kwargs[self.lookup_field]
        )
        return obj

    def create(self, serializer):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        user = User(
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

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=(IsAdminorOwner,))
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

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe',
        permission_classes=(IsAuth, IsAdminorOwner),
        serializer_class=SubscriptionSerializer)
    def subscribe(self, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('id'))
        if self.request.method == 'POST':
            serializer = SubscriptionSerializer(data=self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(
                user=self.request.user,
                author=author
            )
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
        methods=['get'],
        url_path='subscriptions',
        permission_classes=(IsAuth, IsAdminorOwner),
        serializer_class=UserWithRecipesSerializer
    )
    def subscriptions(self, request, pk=None):
        subscriptions = Subscription.objects.filter(user=self.request.user)
        serializer = self.serializer_class(subscriptions, many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['POST'],
        url_path='set_password',
        permission_classes=(IsAdminorOwner, ),
        serializer_class=UpdatePasswordSerializer
    )
    def set_password(self, request, pk=None):
        user = get_object_or_404(User, id=self.request.user.id)
        new_password = self.request.data['new_password']
        current_password = self.request.data['current_password']
        if current_password != user.password:
            return Response(status=HTTPStatus.BAD_REQUEST)
        user.password = new_password
        user.save()
        return Response(status=HTTPStatus.OK)


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

        user = get_object_or_404(
            User,
            email=email,
        )

        if user.password != password:
            return Response(status=HTTPStatus.BAD_REQUEST)
        # serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(str(refresh.access_token))


class UserDeleteTokenView(generics.GenericAPIView):
    """
    Эндпоинт auth/token/logout .
    Удаление токена.
    """
    serializer_class = GetTokenSerializer
    permission_classes = (IsAdminorOwner, )

    def post(self, request):
        user = get_object_or_404(
            User,
            id=self.request.user.id,
        )
        RefreshToken.for_user(user)
        return Response(status=HTTPStatus.NO_CONTENT)
