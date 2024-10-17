from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter


from api.views import UserViewSet, ProductViewSet, ReviewViewSet, GroupBuyViewSet, NotificationViewSet, AuthViewSet, \
    OrderViewSet

# Initialize the router and register the viewsets
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'group-buys', GroupBuyViewSet)
router.register(r'reviews', ReviewViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'auth', AuthViewSet, basename='auth')
# Define the URL patterns
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),  # Only need to include this once

    # Custom user actions
    path('api/users/register/', UserViewSet.as_view({'post': 'register'}), name='user-register'),
    path('api/users/login/', UserViewSet.as_view({'post': 'login'}), name='user-login'),
    path('api/users/me/', UserViewSet.as_view({'get': 'me'}), name='user-me'),
]
