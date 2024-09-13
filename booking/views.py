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
from booking.models import *
from booking.serializers import *


class ApartmentListCreateView(ListCreateAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentCreateSerializer

    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # # http://127.0.0.1:8000/tasks/?status=new&deadline=2026-01-01
    #
    # filterset_fields = ['status', 'deadline']
    # search_fields = ['title', 'description']
    # ordering_fields = ['created_at']
    # permission_classes = [IsOwnerOrReadOnly]
    #
    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return ApartmentCreateSerializer
    #     return ApartmentListSerializer


class ApartmentsDetailUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Apartment.objects.all()
    serializer_class = ApartmentDetailSerializer
    # permission_classes = [IsOwnerOrReadOnly]


class ReservationListCreateView(generics.ListCreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, owner=self.request.user)

class ReservationDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsOwnerOrReadOnly]



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
    access_expiry = datetime.utcfromtimestamp(access_token['exp'])
    refresh_expiry = datetime.utcfromtimestamp(refresh_token['exp'])

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


