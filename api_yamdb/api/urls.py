from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SignUpView, TokenView, MeView, UserViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/signup/', SignUpView.as_view(), name='signup'),
    path('auth/token/', TokenView.as_view(), name='token'),
    path('users/me/', MeView.as_view(), name='me'),
    path('', include(router_v1.urls)),
]
