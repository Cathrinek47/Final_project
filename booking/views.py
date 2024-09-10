from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView

from booking.models import *
from booking.serializers import *


# from django.http import HttpResponse
#
#
# def first_view(request):
#     return HttpResponse("<h1>Hello! It's my first view!</h1>")
# class LoginView(APIView):
#     permission_classes = [AllowAny]
#
#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user:
#             refresh = RefreshToken.for_user(user)
#             access_token = refresh.access_token
#
#             # Используем exp для установки времени истечения куки
#             access_expiry = datetime.fromtimestamp(access_token['exp'])
#             refresh_expiry = datetime.fromtimestamp(refresh['exp'])
#             response = Response(status=status.HTTP_200_OK)
#             response.set_cookie(
#                 key='access_token',
#                 value=str(access_token),
#                 httponly=True,
#                 secure=False, # Используйте True для HTTPS
#                 samesite='Lax',
#                 expires=access_expiry
#                 )
#             response.set_cookie(
#                 key='refresh_token',
#                 value=str(refresh),
#                 httponly=True,
#                 secure=False,
#                 samesite='Lax',
#                 expires=refresh_expiry
#             )
#             return response
#         else:
#             return Response({"detail": "Invalid credentials"},
#                             status=status.HTTP_401_UNAUTHORIZED)
#
#
# class LogoutView(APIView):
#
#     def post(self, request, *args, **kwargs):
#         response = Response(status=status.HTTP_204_NO_CONTENT)
#         response.delete_cookie('access_token')
#         response.delete_cookie('refresh_token')
#         return response

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




