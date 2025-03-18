from rest_framework import serializers
from .models import TravelRequest, Employee, Manager, User
from django.contrib.auth import get_user_model
from datetime import datetime



class UserCreationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=['manager', 'employee'])
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    status = serializers.ChoiceField(choices=['active', 'inactive'])
    manager_id = serializers.IntegerField(required=False)  # Optional, only for employees

    def validate_username(self, value):
        if get_user_model().objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value


    
class CreateAdminSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    role = serializers.CharField(default='admin', read_only=True)  # Default role is 'admin'

    def validate_username(self, value):
        """
        Ensure that the username is not already taken.
        """
        if get_user_model().objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def create(self, validated_data):
        """
        Create and return the admin user.
        """
        # Remove the 'role' key from validated_data as it is not expected by the create_user method
        role = validated_data.pop('role', 'admin')  # Default to 'admin' if not present

        # Create the user and assign the role manually
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )

        # Manually assign the role after the user is created
        user.role = role
        user.save()

        return user


class TravelRequestSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField()
    end_date = serializers.DateField()

    class Meta:
        model = TravelRequest
        fields = '__all__'



# Serializer for Manager model
class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['id', 'name', 'email']


# Serializer for Employee model
class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'email']


