from django.shortcuts import render
from rest_framework import viewsets

from reviews.models import Category, Genre, Title
from api.serializers import CategorySerializer, GenreSerializer, TitleSerializer


class CategoryVieSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(rating=Avg("reviews__score"))
    # queryset = Title.objects.all()
    serializer_class = TitleSerializer
