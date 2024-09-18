from django.utils import timezone
from django.db.models import Q
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import *
from django.contrib.auth.models import User
import re


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'apartment_reserv', 'start_date', 'end_date']

    def validate(self, data):
        apartment_reserv = data.get('apartment_reserv')
        if apartment_reserv.is_deleted:
            raise serializers.ValidationError('The selected apartment has been deleted.')

        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date < timezone.now():
            raise serializers.ValidationError('Start date must be in the future.')
        if end_date <= start_date:
            raise serializers.ValidationError('End date must be after the start date.')

        overlapping_reservations = Reservation.objects.filter(
            apartment_reserv=apartment_reserv
        ).filter(
            Q(start_date__lt=end_date) &
            Q(end_date__gt=start_date) &
            Q(is_deleted=False) &
            ~Q(status='cancelled')
        )

        if overlapping_reservations.exists():
            raise serializers.ValidationError('This apartment is already reserved for the selected dates.')

        return data

class ReservationUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'apartment_reserv', 'start_date', 'end_date', 'status', 'is_deleted']
        read_only_fields = ['id', 'apartment_reserv', 'start_date', 'end_date', 'status']


class ReservationOwnerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'apartment_reserv', 'start_date', 'end_date', 'status', 'user_username', 'apartment_reserv__owner__username']
        read_only_fields = ['id', 'apartment_reserv', 'start_date', 'end_date', 'user_username', 'apartment_reserv__owner__username']



class ApartmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = ['title', 'description', 'category', 'location', 'price', 'rooms_amount']



class ApartmentDetailSerializer(serializers.ModelSerializer):
    # category = CategorySerializer()
    # sub_tasks = SubTaskSerializer(many=True, read_only=True)
    class Meta:
        model = Apartment
        fields = '__all__'
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'apartment', 'rating', 'feedback']


class RegisterUserSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(
    max_length=128,
    write_only=True,
    )
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            're_password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            're_password': {'write_only': True}
        }

    def validate(self, data):
        username = data.get('username')

        if not re.match('^[a-zA-Z0-9_]*$', username):
            raise serializers.ValidationError(
                "The username must be alphanumeric characters or have only_symbol "
            )

        email = data.get('email')

        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise serializers.ValidationError(
                "The email is not valid."
            )

        password = data.get("password")
        re_password = data.get("re_password")

        if password != re_password:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        try:
            validate_password(password)
        except ValidationError as err:
            raise serializers.ValidationError({"password": err.messages})

        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        validated_data.pop('re_password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginUserSerializer(serializers.Serializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {
            'email': {
                'required': True,
                'allow_blank': False
            },
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }

