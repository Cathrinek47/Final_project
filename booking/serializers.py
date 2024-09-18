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


class ReservationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'apartment_reserv', 'start_date', 'end_date', 'status']
        read_only_fields = ['id', 'apartment_reserv', 'start_date', 'end_date']



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

