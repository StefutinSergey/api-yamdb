from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    signup,
    TitleViewSet,
    token,
    UserViewSet,
)

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='title-review'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='title-review-comment'
)

auth_urls = [
    path('signup/', signup, name='signup'),
    path('token/', token, name='token'),
]


api_urls = [
    path('auth/', include(auth_urls)),
    path('', include(router_v1.urls)),
]

urlpatterns = [
    path('v1/', include(api_urls)),
]
