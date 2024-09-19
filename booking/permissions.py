from rest_framework.permissions import BasePermission
from booking.models import Reservation
from datetime import datetime


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешает редактирование объектов только их владельцам, остальным -
    только чтение.
    """
    def has_object_permission(self, request, view, obj):
        # Все пользователи могут просматривать
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
    # Только владелец может изменять объект
        return obj.owner == request.user


class IsOwnerOrUser(BasePermission):
    """
    Разрешает редактирование объектов только их владельцам, остальным -
    только чтение.
    """
    def has_object_permission(self, request, view, obj):
        # Все пользователи могут просматривать
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return (obj.owner == request.user) or (obj.user == request.user)


class IsUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Все пользователи могут просматривать
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return obj.user == request.user



class CheckReservation(BasePermission):

    def has_object_permission(self, request, view, obj):

        reservation_id = self.request.data.get('reservation')
        reservation = Reservation.objects.get(id=reservation_id)
        if reservation.end_date < datetime.now() and reservation.status == 'Confirmed' and reservation.is_deleted == False:
            return True
        else:
            return False
