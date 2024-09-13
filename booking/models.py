from rest_framework.authtoken.admin import User
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.utils.translation import gettext_lazy as _
from django.db import models
from rest_framework.exceptions import ValidationError

from booking.managers import SoftDeleteManager


# class User(AbstractBaseUser, PermissionsMixin):
#     username = models.CharField(_("Name"), max_length=50,
#                                 error_messages={"unique": _("A user with that username already exists.")})
#     email = models.EmailField(_("email address"), max_length=150, unique=True)
#     phone = models.CharField(max_length=15, null=True, blank=True)
#     date_joined = models.DateTimeField(
#         name="registered", auto_now_add=True
#     )
#     # is_staff = models.BooleanField(default=False)
#     # is_active = models.BooleanField(default=True)
#     # last_login = models.DateTimeField(null=True, blank=True)
#     # updated_at = models.DateTimeField(auto_now=True)
#     # deleted_at = models.DateTimeField(null=True, blank=True)
#     # deleted = models.BooleanField(default=False)
#
#     # apartment = models.ForeignKey(
#     #     Apartment,
#     #     on_delete=models.PROTECT,
#     #     related_name="users",
#     #     null=True,
#     #     blank=True,
#     # )
#
#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = [
#         "username",
#     ]
#
#     objects = UserManager()
#
#     def __str__(self):
#         return self.username


class Apartment(models.Model):
    CATEGORY_CHOICES = [
        ('Hotel', 'Hotel'),
        ('Room', 'Room'),
        ('Hostel', 'Hostel'),
        ('Suite', 'Suite'),
        ('House', 'House'),
    ]

    title = models.CharField(max_length=100, unique=True, verbose_name="Title")
    description = models.TextField(max_length=255, verbose_name="Description")
    location = models.CharField(max_length=150, verbose_name="Location")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price pro night")
    category = models.CharField(max_length=50, null=True, choices=CATEGORY_CHOICES)
    rooms_amount = models.PositiveIntegerField(verbose_name="Number of rooms")
    created_at = models.DateField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='apartments', verbose_name='Owner')

    objects = SoftDeleteManager()

    def __str__(self):
        return f': {self.title}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Apartment'

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('free', 'Free'),
        ('reserved', 'Reserved'),
    ]

    apartment_reserv = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='reservations',
                                  verbose_name='Apartment')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations', verbose_name='User')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_reservations', verbose_name='Owner')
    start_date = models.DateTimeField(verbose_name='Start Date')
    end_date = models.DateTimeField(verbose_name='End Date')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='free', verbose_name='Status')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    def __str__(self):
        return f'Reservation for {self.apartment_reserv.title} by {self.user.username}'

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Reservation'
        verbose_name_plural = 'Reservations'

    def clean(self):
        # Check for overlapping reservations
        overlapping_reservations = Reservation.objects.filter(
            apartment_reserv=self.apartment_reserv,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        ).exclude(id=self.id)

        if overlapping_reservations.exists():
            raise ValidationError(_('This apartment is already reserved for the selected dates.'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)



