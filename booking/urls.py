from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from .views import *



# router = DefaultRouter()

urlpatterns = [
    # path('api/', ReadOnlyOrAuthenticatedView.as_view(), name='home'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('apartments/', ApartmentListCreateView.as_view()),
    path('apartments/<int:pk>/', ApartmentsDetailUpdateDeleteView.as_view()),
    path('ratings/', CreateFeedbackView.as_view(), name='feedback-create'),
    path('reservations/', ReservationListCreateView.as_view(), name='reservation-list-create'),
    path('reservations/<int:pk>/', ReservationDetailUpdateDeleteView.as_view(), name='reservation-detail-list-create'),
    path('user/', CurrentUserView.as_view(), name='current-user'),
    path('user/apartments/', UserOwnedApartmentsView.as_view(), name='users-apartments'),
    path('user/reservations/', UserReservationView.as_view(), name='users-reservations'),
    path('user/owner_reservations/<int:pk>/', UserOwnerReservationView.as_view(), name='owners-reservations'),
]
