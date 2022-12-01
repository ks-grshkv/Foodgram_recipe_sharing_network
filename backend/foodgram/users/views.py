from http import HTTPStatus

from django.shortcuts import get_object_or_404
from http import HTTPStatus
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Subscription
from .permissions import IsAdminOrSuper, IsAuth
from .serializers import GetTokenSerializer, UserSerializer, SubscriptionSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт users/
    Используется админами и суперпользователями.
    Исключение: users/me могут использовать авторизованные
    пользователи для просмотра и изменения своего профиля.
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    # permission_classes = (IsAdminOrSuper, )
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

    @action(
        detail=False,
        methods=['get'],
        url_path='subscriptions',
        permission_classes=(IsAuth, )
    )
    def subscriptions(self, request, pk=None):
        user = get_object_or_404(User, id=self.request.user.id)
        serializer = self.serializer_class(user.followers.all(), many=True)
        return Response(serializer.data)


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


class SubscriptionViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = SubscriptionSerializer

    def perform_create(self, serializer):
        author = get_object_or_404(User, id=self.kwargs.get('author_id'))
        serializer.save(user=self.request.user, author=author)
        # subscription = Subscription(user=user, author=author)
        # serializer = self.serializer_class(data=self.request.data)
        # serializer.author = self.kwargs.get('author_id')
        # serializer.is_valid(raise_exception=True)
        # subscription.save()
        # serializer.save()

        return Response({
            "email": author.email,
            "id": author.pk,
            "username": author.username,
            "first_name": author.first_name,
            "last_name": author.last_name,
        })

    @action(
        detail=False,
        methods=['delete'],
        url_path='',
        permission_classes=(IsAuth, )
    )
    def dele(self):
        author = get_object_or_404(User, id=self.kwargs.get('author_id'))
        subscription = get_object_or_404(
            Subscription,
            user=self.request.user,
            author=author
        )
        subscription.delete()
        return Response(203)



    

    # def get_queryset(self):
    #     author = get_object_or_404(User, pk=self.kwargs.get('user_id'))
    #     return author

    # def create(self,  serializer):
    #     user = self.request.user.id
    #     print('AAAAAA', *args)
    #     # author = get_object_or_404(User, id=pk)
    #     author = self.get_queryset()
    #     serializer = self.serializer_class(user=user, author=author)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()

    #     subscription = Subscription.objects.get(
    #         user=user, author=author
    #     )
    #     subscription.save()
    #     return Response({author})

    # def destroy(self, request, pk):
    #     user = self.get_object(pk)
    #     user.delete()
    #     return Response({"a": "aa"})


    # permission_classes = (IsAdminOrReadOnlyPermission,)
    # lookup_field = 'slug'
    # pagination_class = PageNumberPagination
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)

    # def get_object(self):
    #     queryset = self.get_queryset()
    #     obj = get_object_or_404(
    #         queryset,
    #         id=self.kwargs[self.lookup_field]
    #     )
    #     return obj