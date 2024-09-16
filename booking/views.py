from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status, generics
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from booking.models import *
from booking.serializers import *


class ApartmentListCreateView(ListCreateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentCreateSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # http://127.0.0.1:8000/tasks/?status=new&deadline=2026-01-01
    filterset_fields = {
        'price': ['gte', 'lte'],
        'location': ['exact', 'icontains'],
        'rooms_amount': ['gte', 'lte'],
        'category': ['exact'],
    }
    # filterset_fields = ['title', 'description', 'location', 'price', 'category', 'rooms_amount']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'price']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ApartmentCreateSerializer
        return ApartmentDetailSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ApartmentsDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentDetailSerializer
    permission_classes = [IsOwnerOrReadOnly]



class ApartmentDetailView(generics.RetrieveAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentDetailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        apartment = super().get_object()
        ratings = Rating.objects.filter(apartment=apartment)
        if ratings.exists():
            average_rating = ratings.aggregate(models.Avg('rating'))['rating__avg']
            apartment.rating = average_rating
            apartment.save()
        return apartment


class ReservationListCreateView(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        apartment = serializer.validated_data['apartment_reserv']
        serializer.save(user=self.request.user)


class ReservationDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationDetailSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        new_start_date = request.data.get('start_date')
        new_end_date = request.data.get('end_date')

        if request.user == instance.user:
            if set(request.data.keys()) == {'start_date', 'end_date'}:
                overlapping_reservations = Reservation.objects.filter(
                    apartment_reserv=instance.apartment_reserv,
                    start_date__lt=new_end_date,
                    end_date__gt=new_start_date
                ).exclude(id=instance.id)

                if overlapping_reservations.exists():
                    return Response({"detail": "These dates are already reserved by another user."},
                                    status=status.HTTP_400_BAD_REQUEST)
        # Change instance.status = 'reserved'
                serializer.save(start_date=new_start_date, end_date=new_end_date)
            else:
                return Response({"detail": "You can only update the start_date and end_date fields."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "You do not have permission to update this reservation."},
                            status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.data)


class UserOwnerReservationView(RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationDetailSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        request_user = request.user
        new_status = request.data.get('status')

        apartment_owner = instance.apartment_reserv.owner

        if request_user == apartment_owner:
            if set(request.data.keys()) == {'apartment_reserv', 'start_date', 'end_date', 'status'}:
                serializer.save(status=new_status)
            else:
                return Response({"detail": "You can only update the status field."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail": "You do not have permission to update this reservation."},
                            status=status.HTTP_403_FORBIDDEN)

        return Response(serializer.data)


class ReadOnlyOrAuthenticatedView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        return Response({"message": "This is readable by anyone, but modifiable only by authenticated users."})

    def post(self, request):
        return Response({"message": "Data created by authenticated user!"})


class PublicView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"message": "This is accessible by anyone!"})


def set_jwt_cookies(response, user):
    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token

    # Устанавливает JWT токены в куки.
    access_expiry = datetime.fromtimestamp(access_token['exp'])
    refresh_expiry = datetime.fromtimestamp(refresh_token['exp'])

    response.set_cookie(
        key='access_token',
        value=str(access_token),
        httponly=True,
        secure=False,
        samesite='Lax',
        expires=access_expiry
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        httponly=True,
        secure=False,
        samesite='Lax',
        expires=refresh_expiry
    )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response = Response({
                'user': {
                    'username': user.username,
                    'email': user.email
                }
            }, status=status.HTTP_201_CREATED)
            set_jwt_cookies(response, user)
            return response
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Используем exp для установки времени истечения куки
            access_expiry = datetime.fromtimestamp(access_token['exp'])
            refresh_expiry = datetime.fromtimestamp(refresh['exp'])
            response = Response(status=status.HTTP_200_OK)
            response.set_cookie(
                key='access_token',
                value=str(access_token),
                httponly=True,
                secure=False, # Используйте True для HTTPS
                samesite='Lax',
                expires=access_expiry
                )
            response.set_cookie(
                key='refresh_token',
                value=str(refresh),
                httponly=True,
                secure=False,
                samesite='Lax',
                expires=refresh_expiry
            )
            return response
        else:
            return Response({"detail": "Invalid credentials"},
                            status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):

    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'username': user.username,
            'email': user.email
        })


class UserOwnedApartmentsView(ListAPIView):
    serializer_class = ApartmentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Apartment.objects.filter(owner=self.request.user)


class UserReservationView(ListAPIView):
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)


class CreateFeedbackView(generics.CreateAPIView):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        reservation_id = self.request.data.get('reservation')
        reservation = Reservation.objects.get(id=reservation_id)

        if reservation.user != user:
            raise ValidationError("You can only rate your own reservations.")

        if reservation.end_date > datetime.now():
            raise ValidationError("You can only rate after the end date of your reservation.")

        serializer.save(user=user)


class ApartmentRatingsView(generics.ListAPIView):
    serializer_class = RatingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        apartment_id = self.kwargs['apartment_id']
        return Rating.objects.filter(apartment__id=apartment_id)


