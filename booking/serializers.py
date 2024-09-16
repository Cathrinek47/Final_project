from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'apartment_reserv', 'start_date', 'end_date']


class ReservationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'apartment_reserv', 'start_date', 'end_date', 'status']



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

#
# class UserListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = (
#             'username',
#             'email',
#             'phone',
#         )
#
#
# class UserDetailSerializer(serializers.ModelSerializer):
#     project = serializers.StringRelatedField()
#     class Meta:
#         model = User
#         fields = (
#             'username',
#             'email',
#             'phone',
#         )


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
            'phone',
        )
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate(self, data):
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if not re.match('^[a-zA-Z0-9_]*$', username):
            raise serializers.ValidationError(
                "The username must be alphanumeric characters or have only_symbol "
            )
        if not re.match('^[a-zA-Z]*$', first_name):
            raise serializers.ValidationError(
                "The first name must contain only alphabet symbols "
            )
        if not re.match('^[a-zA-Z]*$', last_name):
            raise serializers.ValidationError(
                "The last name must contain only alphabet symbols"
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


