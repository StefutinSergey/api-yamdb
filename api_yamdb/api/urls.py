from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignUpView, TokenView, MeView, UserViewSet, ReviewViewSet, CommentViewSet, GenreViewSet, CategoryViewSet, TitleViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')


urlpatterns = [
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('titles/<int:title_id>/reviews/',
         ReviewViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='review-list'),
    path('titles/<int:title_id>/reviews/<int:pk>/',
         ReviewViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='review-detail'),

    path('titles/<int:title_id>/reviews/<int:review_id>/comments/',
         CommentViewSet.as_view({'get': 'list', 'post': 'create'}),
         name='comment-list'),
    path('titles/<int:title_id>/reviews/<int:review_id>/comments/<int:pk>/',
         CommentViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='comment-detail'),
    path('auth/token/', TokenView.as_view(), name='token'),
    path('users/me/', MeView.as_view(), name='me'),
    path('', include(router_v1.urls)),
]
