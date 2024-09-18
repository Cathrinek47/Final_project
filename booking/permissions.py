from rest_framework.permissions import BasePermission


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

