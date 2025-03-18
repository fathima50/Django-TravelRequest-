# views.py
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.exceptions import AuthenticationFailed
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import TravelRequest,Employee,Manager,Admin,UserProfile
from .serializers import TravelRequestSerializer, CreateAdminSerializer,UserCreationSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import authenticate
from django.core.mail import send_mail




@api_view(['POST'])
@permission_classes([AllowAny])  # Make this view accessible to anyone
def create_admin(request):
    """
    Endpoint to create an admin user without generating a token.
    """
    serializer = CreateAdminSerializer(data=request.data)

    if serializer.is_valid():
        # Create the user
        user = serializer.save()
        
        # Create the UserProfile with role 'admin'
        UserProfile.objects.create(user=user, role='admin')

        # Optionally, create the Admin profile as well if required
        Admin.objects.create(user=user, username=request.data['username'], password=request.data['password'])

        return Response({
            'message': 'Admin created successfully. Please login to get your token.'
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Login and generate token for admin
@api_view(['POST'])
@permission_classes([AllowAny])
def login_and_generate_token(request):
    """
    Endpoint to login and generate a token for the user.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    # Ensure both fields are provided
    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate the user
    user = authenticate(username=username, password=password)

    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Generate or get an existing token for the authenticated user
    token, created = Token.objects.get_or_create(user=user)

    return Response({
        'message': 'Login successful',
        'token': token.key
    }, status=status.HTTP_200_OK)


#to generate token for employee and manager 
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    Endpoint to login and generate a token for the user.
    """
    username = request.data.get('username')
    password = request.data.get('password')

    # Ensure both fields are provided
    if not username or not password:
        return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate the user
    user = authenticate(username=username, password=password)

    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    # Generate or get an existing token for the authenticated user
    token, created = Token.objects.get_or_create(user=user)

    # Get user profile and role information
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

    role_data = {}
    if profile.role == 'employee':
        employee = Employee.objects.filter(user=user).first()
        role_data = {
            'name': employee.name,
            'email': employee.email,
            'status': employee.status,
            'manager_id': employee.manager.id if employee.manager else None
        }
    elif profile.role == 'manager':
        manager = Manager.objects.filter(user=user).first()
        role_data = {
            'name': manager.name,
            'email': manager.email,
            'status': manager.status
        }
    elif profile.role == 'admin':
        role_data = {
            'role': 'admin'
        }

    return Response({
        'message': 'Login successful',
        'token': token.key,
        'role': profile.role,
        'profile': role_data
    }, status=status.HTTP_200_OK)


#to add a new employee or a manager
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_manager_employee(request):
    """
    Endpoint to create managers or employees. Only admins are allowed to create.
    """
    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin':
            return Response({'error': 'Only admins can add managers or employees.'}, status=status.HTTP_403_FORBIDDEN)
    except UserProfile.DoesNotExist:
        return Response({'error': 'User profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

    # Deserialize and validate data
    serializer = UserCreationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    username = data['username']
    password = data['password']
    role = data['role']
    name = data['name']
    email = data['email']
    status_choice = data['status']

    # Create the user and profile
    user = get_user_model().objects.create_user(username=username, password=password)
    UserProfile.objects.create(user=user, role=role)

    # Create role-specific profiles
    if role == 'manager':
        Manager.objects.create(user=user, name=name, email=email, status=status_choice)
    elif role == 'employee':
        manager_id = data.get('manager_id')
        manager = None
        if manager_id:
            try:
                manager = Manager.objects.get(id=manager_id)
            except Manager.DoesNotExist:
                return Response({'error': 'Manager not found.'}, status=status.HTTP_400_BAD_REQUEST)
        Employee.objects.create(user=user, name=name, email=email, status=status_choice, manager=manager)

    return Response({'message': f'{role.capitalize()} created successfully.'}, status=status.HTTP_201_CREATED)

# 1. Employee Creates a New Travel Request
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_travel_request(request):
    # Check if the user is authenticated
    # if not request.user.is_authenticated:
    #     raise AuthenticationFailed('Authentication required.')

    # Assuming the user is authenticated as an employee
    try:
        employee = request.user.employee  # Assuming the user is an authenticated employee
    except AttributeError:
        raise AuthenticationFailed('User is not associated with an employee account.')

    manager = employee.manager

    data = request.data
    data['employee'] = employee.id
    data['manager'] = manager.id if manager else None  # Automatically assign manager

    serializer = TravelRequestSerializer(data=data)

    if serializer.is_valid():
        travel_request = serializer.save(status='Pending')  # Set the status to "Pending"
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# 2. Employee Views Past Travel Requests
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def emp_view_travel_requests(request):
    print(f"DEBUG: User - {request.user}")

    try:
        employee = request.user.employee
        print(f"DEBUG: Employee found - {employee}")
    except AttributeError:
        return Response({'error': 'User is not associated with an employee account.'}, status=status.HTTP_403_FORBIDDEN)

    travel_requests = TravelRequest.objects.filter(employee=employee)
    serializer = TravelRequestSerializer(travel_requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

#edit the request by employee
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_travel_request(request, pk):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required.'}, status=status.HTTP_403_FORBIDDEN)

    try:
        # Get the Employee instance linked to the current user
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return Response({'error': 'Employee profile not found.'}, status=status.HTTP_404_NOT_FOUND)

    try:
        # Fetch the travel request linked to the employee
        travel_request = TravelRequest.objects.get(id=pk, employee=employee)
    except TravelRequest.DoesNotExist:
        return Response({'error': 'Travel request not found or not authorized.'}, status=status.HTTP_404_NOT_FOUND)

    # Allow edit only if the status is 'Pending' or 'update request'
    if travel_request.status not in ['Pending', 'update request']:
        return Response({'error': 'Cannot edit processed travel requests.'}, status=status.HTTP_400_BAD_REQUEST)

    # Partial update using serializer
    serializer = TravelRequestSerializer(travel_request, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Travel request updated successfully.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 3. Employee Cancels a Past Request (Only if it’s Pending or Further Data Requested)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_travel_request(request, pk):
    try:
        travel_request = TravelRequest.objects.get(id=pk)
        if travel_request.status not in ['Pending', 'update request']:
            return Response({'error': 'Cannot cancel request, it has been processed.'}, status=status.HTTP_400_BAD_REQUEST)

        travel_request.status = 'Cancelled'
        travel_request.save()
        return Response({'message': 'Travel request cancelled successfully.'})
    except TravelRequest.DoesNotExist:
        return Response({'error': 'Request not found.'}, status=status.HTTP_400_BAD_REQUEST)


# 4. Employee Responds to Further Data Requested by Manager (Resubmission)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def resubmit_travel_request(request, pk):
    travel_request = get_object_or_404(TravelRequest, pk=pk, employee=request.user.employee)

    if travel_request.status != 'update request':
        return Response({'detail': 'This request cannot be resubmitted because it was not flagged for further data.'},
                        status=status.HTTP_400_BAD_REQUEST)

    serializer = TravelRequestSerializer(travel_request, data=request.data)

    if serializer.is_valid():
        travel_request.status = 'Pending'  # Reset the status to Pending for resubmission
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 5. Manager Approves or Rejects Travel Request
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_or_reject_travel_request(request, pk):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return Response({'detail': 'User profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user is a manager
    if user_profile.role != 'manager':
        return Response({'detail': 'Authentication required or not a manager.'}, status=status.HTTP_403_FORBIDDEN)

    # Fetch the travel request
    travel_request = get_object_or_404(TravelRequest, pk=pk)

    # Ensure the correct manager is processing the request
    if travel_request.manager.user != request.user:
        return Response({'detail': 'You are not authorized to approve/reject this request.'}, status=status.HTTP_403_FORBIDDEN)

    action = request.data.get('action')
    manager_notes = request.data.get('manager_notes', '')

    if action == 'approve':
        travel_request.status = 'Approved'
    elif action == 'reject':
        travel_request.status = 'Rejected'
    else:
        return Response({'detail': 'Invalid action. Must be "approve" or "reject".'}, status=status.HTTP_400_BAD_REQUEST)

    travel_request.manager_notes = manager_notes
    travel_request.save()

    return Response({'detail': f'Request has been {action}ed.'}, status=status.HTTP_200_OK)


# 6. Manager Views Travel Requests with Filter and Sorting
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def mngr_view_travel_requests(request):
    # Only managers should be able to view this
    if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
        return Response({'detail': 'Authentication required or not a manager.'}, status=status.HTTP_403_FORBIDDEN)
    
    manager = request.user.manager
    travel_requests = TravelRequest.objects.filter(manager=manager)

    # Apply filters
    employee_name = request.query_params.get('employee', None)
    if employee_name:
        travel_requests = travel_requests.filter(employee__name__icontains=employee_name)

    # Apply date range filter
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    if start_date and end_date:
        travel_requests = travel_requests.filter(start_date__gte=start_date, end_date__lte=end_date)

    # Apply status filter
    status_filter = request.query_params.get('status', None)
    if status_filter:
        travel_requests = travel_requests.filter(status=status_filter)

    # Sorting by request date or other criteria
    sort_by = request.query_params.get('sort_by', 'date_of_request')
    travel_requests = travel_requests.order_by(sort_by)

    # Serialize the data
    serializer = TravelRequestSerializer(travel_requests, many=True)
    return Response(serializer.data)


#update travel request
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def manager_note(request, pk):
    # Only managers should be able to update travel requests
    if not request.user.is_authenticated or not hasattr(request.user, 'manager'):
        return Response({'detail': 'Authentication required or not a manager.'}, status=status.HTTP_403_FORBIDDEN)

    # Get the travel request
    travel_request = get_object_or_404(TravelRequest, pk=pk)

    # Ensure the request is pending or already flagged for further data
    if travel_request.status not in ['Pending', 'update request']:
        return Response({'detail': 'Cannot update this request as it has already been processed.'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the manager's action and note
    action = request.data.get('status')
    manager_notes = request.data.get('manager_notes')

    if action != 'update request':
        return Response({'detail': 'Status must be "update request" to request further data.'}, status=status.HTTP_400_BAD_REQUEST)

    # Set the status to "update request" and save the manager's notes
    travel_request.status = 'update request'
    travel_request.manager_notes = manager_notes
    travel_request.save()

    return Response({'detail': 'Further information requested from the employee.'}, status=status.HTTP_200_OK)



# 1. Admin Views All Travel Requests (with filter, sort, and search)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def view_all_travel_requests(request):
    # Ensure the user is an admin
    if not request.user.is_authenticated or not hasattr(request.user, 'admin'):
        return Response({'detail': 'Authentication required or not an admin.'}, status=status.HTTP_403_FORBIDDEN)

    travel_requests = TravelRequest.objects.all()

    # Filters
    employee_name = request.query_params.get('employee', None)
    if employee_name:
        travel_requests = travel_requests.filter(employee__name__icontains=employee_name)

    # Date range filter
    start_date = request.query_params.get('start_date', None)
    end_date = request.query_params.get('end_date', None)
    if start_date and end_date:
        travel_requests = travel_requests.filter(start_date__gte=start_date, end_date__lte=end_date)

    # Status filter
    status_filter = request.query_params.get('status', None)
    if status_filter:
        travel_requests = travel_requests.filter(status=status_filter)

    # Sorting by request date or other criteria
    sort_by = request.query_params.get('sort_by', 'date_of_request')
    travel_requests = travel_requests.order_by(sort_by)

    # Serialize the data
    serializer = TravelRequestSerializer(travel_requests, many=True)
    return Response(serializer.data)

# 2. Admin Requests Additional Information (Change Status to "update request")
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_note(request, pk):
    # Ensure the user is an admin
    if not request.user.is_authenticated or not hasattr(request.user, 'admin'):
        return Response({'detail': 'Authentication required or not an admin.'}, status=status.HTTP_403_FORBIDDEN)

    travel_request = get_object_or_404(TravelRequest, pk=pk)

    # Only allow admins to update requests that are pending or need further info
    if travel_request.status not in ['Pending', 'update request']:
        return Response({'detail': 'Cannot update this request as it is already processed.'}, status=status.HTTP_400_BAD_REQUEST)

    admin_notes = request.data.get('admin_notes', '')

    # Set the status to "update request" and save the note
    travel_request.status = 'update request'
    travel_request.Admin_notes = admin_notes  # Save note from admin
    travel_request.save()

    return Response({'detail': 'Additional information requested from the employee.'}, status=status.HTTP_200_OK)

# 3. Admin Closes Approved Travel Request (Changes Status to "closed")
@api_view(['PUT'])
def close_approved_travel_request(request, pk):
    # Ensure the user is an admin
    if not request.user.is_authenticated or not hasattr(request.user, 'admin'):
        return Response({'detail': 'Authentication required or not an admin.'}, status=status.HTTP_403_FORBIDDEN)

    travel_request = get_object_or_404(TravelRequest, pk=pk)

    # Only allow closing for approved requests
    if travel_request.status != 'Approved':
        return Response({'detail': 'This request is not approved, cannot be closed.'}, status=status.HTTP_400_BAD_REQUEST)

    # Change status to 'closed' and save
    travel_request.status = 'closed'
    travel_request.save()

    return Response({'detail': 'Travel request has been closed.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def send_email(request, pk):
    # Ensure the user is an authenticated admin
    if not request.user.is_authenticated or not hasattr(request.user, 'admin'):
        return Response({'detail': 'Authentication required or not an admin.'}, status=status.HTTP_403_FORBIDDEN)

    # Get the travel request object
    travel_request = get_object_or_404(TravelRequest, pk=pk)
    employee = travel_request.employee

    # Get the note from the admin
    admin_notes = request.data.get('admin_notes', '')

    if not admin_notes:
        return Response({'detail': 'Admin notes are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Email details
    subject = 'Request for Additional Information on Your Travel Request'
    message = (
        f"Dear {employee.name},\n\n"
        f"The admin team requires additional information regarding your travel request (ID: {travel_request.id}).\n\n"
        f"Admin Notes: {admin_notes}\n\n"
        f"Please update the required information at your earliest convenience.\n\n"
        "Thank you,\nAdmin Team"
    )
    recipient_list = [employee.user.email]

    # Send the email
    send_mail(subject, message, None, recipient_list, fail_silently=False)

    # Update the travel request status
    travel_request.status = 'update request'
    travel_request.admin_notes = admin_notes
    travel_request.save()

    return Response({'detail': 'Email sent successfully to the employee.'}, status=status.HTTP_200_OK)























