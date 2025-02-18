from django.db.models import Sum
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, GenericAPIView
from datetime import datetime
from rest_framework.response import Response
from rest_framework import status, generics, mixins
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from .permissions import IsOwnerOrReadOnly, IsOwnerOrUser, IsUser, CheckReservation
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from booking.models import *
from booking.serializers import *


class ApartmentListCreateView(ListCreateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

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
    # queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        apartment = serializer.validated_data['apartment_reserv']
        serializer.save(user=self.request.user)


class ReservationDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView, mixins.CreateModelMixin):
    queryset = Reservation.objects.all()
    # serializer_class = ReservationUserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RatingSerializer
        else:
            return ReservationUserDetailSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user == instance.user:
            instance.is_deleted = True
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "You do not have permission to delete this reservation."},
                            status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation_id = request.parser_context['kwargs']['pk']
            # get_object_or_404(Reservation, pk=self.kwargs['pk']))
        reservation = Reservation.objects.get(id=reservation_id)
        serializer.save(user=self.request.user, reservation=reservation)


        # reservation_id = self.request.data.get('reservation')
        apartment = Apartment.objects.get(reservations=reservation_id)

        all_apartment_ratings = Rating.objects.filter(
            reservation__apartment_reserv=apartment).count()  # Amount of rewiews
        sum_ratings = Rating.objects.filter(reservation__apartment_reserv__id=apartment.id).aggregate(Sum('rating'))[
            'rating__sum']  # Sum of all ratings
        apartment.objects_rating = sum_ratings / all_apartment_ratings if all_apartment_ratings != 0 else 0
        apartment.save()


        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserOwnerReservationView(RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationOwnerDetailSerializer
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
            if set(request.data.keys()) == {'status'}:
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


class RegisterView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterUserSerializer

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
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


class LoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        # email = serializer.validated_data['email']
        # password = serializer.validated_data['password']
        # username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=user.username, password=password)

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
                secure=False, #  True для HTTPS
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


class CreateFeedbackView(generics.ListCreateAPIView):
    # queryset = Rating.objects.all(user=request.user)
    serializer_class = RatingDetailSerializer
    permission_classes = [IsUser, CheckReservation]

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        reservation_id = self.request.data.get('reservation')
        apartment = Apartment.objects.get(reservations=reservation_id)

        all_apartment_ratings = Rating.objects.filter(reservation__apartment_reserv=apartment).count() #Amount of rewiews
        sum_ratings = Rating.objects.filter(reservation__apartment_reserv__id=apartment.id).aggregate(Sum('rating'))['rating__sum'] #Sum of all ratings
        apartment.objects_rating = sum_ratings / all_apartment_ratings if all_apartment_ratings!= 0 else 0
        apartment.save()


class FeedbackDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    queryset = Rating.objects.all()

    def perfom_create(self, instance, validated_data):
        apartment = instance.reservation.apartment_reserv
        total_reviews = apartment.reservations.count()
        new_avg_rating = (apartment.objects_rating * (total_reviews - 1) + validated_data.get('rating',
                                                                                              instance.rating)) / total_reviews
        apartment.objects_rating = new_avg_rating
        apartment.save()

        return instance

class ApartmentRatingsView(ListAPIView):
    serializer_class = RatingSerializer
    reservation = ReservationSerializer(read_only=True)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rating.objects.filter(reservation__apartment_reserv__id=self.kwargs['pk'])
        # apartment_id = self.kwargs['apartment_id']
        # return Rating.objects.filter(apartment__id=apartment_id)
# Reservation.objects.filter(apartment_reserv__id=self.kwargs['pk'])


