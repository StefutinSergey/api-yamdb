import random
import string
from rest_framework.views import APIView
from rest_framework import filters, status, viewsets
from rest_framework import status, viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.pagination import PageNumberPagination

from .serializers import SignUpSerializer, UserSerializer, TokenSerializer, CommentSerializer, ReviewSerializer, CategorySerializer, GenreSerializer, TitleSerializer
from .permissions import IsAdmin, IsOwnerOrReadOnly, IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin
from reviews.models import Comment, Review, Category, Genre, Title

User = get_user_model()


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(username=username)
            if user.email != email:
                return Response(
                    {'username': 'Пользователь с таким username уже существует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            if User.objects.filter(email=email).exists():
                return Response(
                    {'email': 'Пользователь с таким email уже существует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user = User.objects.create_user(username=username, email=email)
        confirmation_code = ''.join(random.choices(string.digits, k=6))
        user.confirmation_code = confirmation_code
        user.save()
        send_mail(
            subject='Код подтверждения',
            message=f'Ваш код: {confirmation_code}',
            from_email=None,
            recipient_list=[email],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        code = serializer.validated_data['confirmation_code']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({'error': 'Пользователь не найден'},
                            status=status.HTTP_404_NOT_FOUND)
        if user.confirmation_code != code:
            return Response({'error': 'Неверный код'},
                            status=status.HTTP_400_BAD_REQUEST)
        access_token = AccessToken.for_user(user)
        return Response({'access': str(access_token)}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch']

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop('role', None)
        serializer.save()
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin, IsAuthenticated]
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email']
    http_method_names = ['get', 'post', 'patch', 'delete']

    def put(self, request):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)



class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        return Review.objects.filter(title_id=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(
            author=self.request.user,
            title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
 
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrModeratorOrAdmin]

    def get_queryset(self):
        return Comment.objects.filter(review_id=self.kwargs.get('review_id'))

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        get_object_or_404(Review, id=review_id)
        serializer.save(
            author=self.request.user,
            review_id=review_id
        )


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'delete']
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def retrieve(self, request, *args, **kwargs):

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'post', 'put', 'delete']
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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

