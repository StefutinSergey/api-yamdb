import random
import string

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import IntegrityError

from rest_framework import filters, mixins, status, viewsets, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdmin,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleSerializer,
    TokenSerializer,
    UserSerializer,
)
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    email = serializer.validated_data['email']
    try:
        user, created = User.objects.get_or_create(
            username=username, defaults={'email': email}
        )
    except IntegrityError:
        return Response(
            {'email': 'Пользователь с таким email уже существует.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not created and user.email != email:
        return Response(
            {'username': 'Пользователь с таким username уже существует.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    chars = getattr(settings, 'CONFIRMATION_CODE_CHARS', string.digits)
    length = getattr(settings, 'CONFIRMATION_CODE_LENGTH', 6)
    confirmation_code = ''.join(random.choices(chars, k=length))
    user.confirmation_code = confirmation_code
    user.save()
    send_mail(
        subject='Код подтверждения',
        message=f'Ваш код: {confirmation_code}',
        from_email=None,
        recipient_list=[email],
    )
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    serializer = TokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data['username']
    code = serializer.validated_data['confirmation_code']
    user = get_object_or_404(User, username=username)
    if user.confirmation_code != code:
        raise serializers.ValidationError(
            {'detail': 'Неверный код подтверждения'})
    user.confirmation_code = None
    user.save()
    return Response({'access': str(AccessToken.for_user(user))})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin, IsAuthenticated]
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        url_name='me',
        # для /me/ нужна просто авторизация
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(
                user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            if 'role' in serializer.validated_data:
                del serializer.validated_data['role']
            serializer.save()
            return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrModeratorOrAdmin]

    def get_title(self):
        if not hasattr(self, '_title'):
            self._title = get_object_or_404(Title, pk=self.kwargs['title_id'])
        return self._title

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrModeratorOrAdmin]

    def get_review(self):
        if not hasattr(self, '_review'):
            self._review = get_object_or_404(
                Review, pk=self.kwargs['review_id'])
        return self._review

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        get_object_or_404(Review, id=review_id)
        serializer.save(
            author=self.request.user,
            review=self.get_review()
        )


class BaseSlugViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    http_method_names = ['get', 'post', 'patch', 'delete']


class CategoryViewSet(BaseSlugViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseSlugViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений (только администратор может редактировать)."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        queryset = super().get_queryset()
        genre_slug = self.request.query_params.get('genre')
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        category_slug = self.request.query_params.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(year=year)
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name=name)
        return queryset
