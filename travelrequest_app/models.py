from django.db import models
from django.contrib.auth.models import User
from datetime import date,datetime


 
# Choices for status field in Employee, Manager, Admin
STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive')
]

# Choices for travel mode
TRAVEL_MODE_CHOICES = [
    ('Plane', 'Plane'),
    ('Train', 'Train'),
    ('Car', 'Car'),
]

ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('manager', 'Manager'),
    ('employee', 'Employee'),
]



ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('manager', 'Manager'),
    ('employee', 'Employee'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return f'{self.user.username} - {self.role}'
    
# Employee model - An employee has a one-to-one relationship with User
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One-to-one with User model
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    status = models.CharField(max_length=15, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    manager = models.ForeignKey('Manager', on_delete=models.SET_NULL, null=True, blank=True)  # ForeignKey to Manager
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return self.name

# Manager model - A manager has a one-to-one relationship with User
class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    status = models.CharField(max_length=15, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='manager')

    def __str__(self):
        return self.name
    
    

# Admin model - An admin has a one-to-one relationship with User
class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=150,default='admin')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='active')
    
    
# TravelRequest model - Represents a travel request made by an employee
class TravelRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='requests')  # Link to Employee
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, blank=True)  # Link to Manager
    date_of_request = models.DateField(default=datetime.now)  # Date of request
    from_location = models.CharField(max_length=100)  # Location where the travel starts
    to_location = models.CharField(max_length=100)  # Location where the travel ends
    travel_mode = models.CharField(max_length=20, choices=TRAVEL_MODE_CHOICES)  # Travel mode (Plane, Train, Car)
    start_date = models.DateField(default=date.today)  # Starting date of the travel
    end_date = models.DateField()  # Ending date of the travel
    additional_requests = models.TextField(blank=True, null=True)  # Additional requests, optional
    lodging_required = models.BooleanField(default=False)  # Whether lodging is required
    lodging_location = models.CharField(max_length=200, blank=True, null=True)  # Preferred lodging location
    purpose_of_travel = models.TextField()  # Purpose of the travel
    status = models.CharField(max_length=20, default='Pending', choices=[('Pending', 'Pending'), ('Approved', 'Approved'), 
        ('Rejected', 'Rejected'), ('closed', 'closed'), ('update request', 'update request')])  # Status of the request
    manager_notes = models.TextField(blank=True, null=True)  # Notes attached by the manager (if any)
    Admin_notes = models.TextField(blank=True, null=True)  # Notes attached by the Admin (if any)
    is_resubmitted = models.BooleanField(default=False)  # Flag to check if the request is resubmitted after rejection or further data requested

    
 





