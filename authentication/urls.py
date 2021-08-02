from django.urls import path
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView
# )

from authentication import views

app_name = 'auth'
urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    # path('hello/', views.HelloView.as_view(), name='hello')
]