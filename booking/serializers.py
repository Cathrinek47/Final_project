from rest_framework import serializers
from .models import *


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
