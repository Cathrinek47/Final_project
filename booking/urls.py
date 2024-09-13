from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from .views import *


# router = DefaultRouter()

urlpatterns = [
    path('api/', ReadOnlyOrAuthenticatedView.as_view(), name='home'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('apartments/', ApartmentListCreateView.as_view()),
    path('apartments/<int:pk>/', ApartmentsDetailUpdateDeleteView.as_view()),
    path('reservations/', ReservationListCreateView.as_view(), name='reservation-list-create'),
    path('reservations/<int:pk>/', ReservationDetailUpdateDeleteView.as_view(), name='reservation-detail-update-delete'),
]
