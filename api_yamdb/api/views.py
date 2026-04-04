import random
import string
from django.db.models import Avg
from rest_framework.views import APIView
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend
from .filters import TitleFilter

from .serializers import (
    SignUpSerializer,
    UserSerializer,
    TokenSerializer,
    CommentSerializer,
    ReviewSerializer,
    CategorySerializer,
    GenreSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
)
from .permissions import IsAdmin, IsOwnerOrReadOnly, IsAdminOrReadOnly
from reviews.models import Comment, Review, Category, Genre, Title

User = get_user_model()


class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        email = serializer.validated_data["email"]
        user, _ = User.objects.get_or_create(username=username, email=email)
        code = "".join(random.choices(string.digits, k=6))
        user.confirmation_code = code
        user.save()
        send_mail(
            subject="Код подтверждения",
            message=f"Ваш код: {code}",
            from_email=None,
            recipient_list=[email],
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data["username"]
        code = serializer.validated_data["confirmation_code"]
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND
            )
        if user.confirmation_code != code:
            return Response(
                {"error": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST
            )
        token = AccessToken.for_user(user)
        return Response({"access": str(token)}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data.pop("role", None)
        serializer.save()
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get("title_id")
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get("title_id")
        serializer.save(author=self.request.user, title_id_id=title_id)


class CommentViewSet(viewsets.ModelViewSet):

    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        return Comment.objects.filter(review_id=review_id)

    def perform_create(self, serializer):
        review_id = self.kwargs.get("review_id")
        serializer.save(author=self.request.user, review_id=review_id)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ["get", "post", "put", "delete"]
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def retrieve(self, request, *args, **kwargs):

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ["get", "post", "put", "delete"]
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведений (только администратор может редактировать)."""

    queryset = Title.objects.annotate(rating=Avg("reviews__score")).order_by("name")
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ["get", "post", "patch", "delete"]

    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TitleReadSerializer
        return TitleWriteSerializer

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     genre_slug = self.request.query_params.get("genre")
    #     if genre_slug:
    #         queryset = queryset.filter(genre__slug=genre_slug)
    #     category_slug = self.request.query_params.get("category")
    #     if category_slug:
    #         queryset = queryset.filter(category__slug=category_slug)
    #     year = self.request.query_params.get("year")
    #     if year:
    #         queryset = queryset.filter(year=year)
    #     name = self.request.query_params.get("name")
    #     if name:
    #         queryset = queryset.filter(name=name)
    #     return queryset
