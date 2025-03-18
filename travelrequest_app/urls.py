# urls.py

from django.urls import path
from . import views

urlpatterns = [

    # Other URLs
    path('admin/create/', views.create_admin, name='admin-create'),
    path('login/', views.login_and_generate_token, name='login'),
    path('add-manager-employee/', views.add_manager_employee, name='add-manager-employee'),
    path('login_user/', views.login_user, name='login_user'),

    path('<int:pk>/send-email/', views.send_email, name='send_email'),

    #employee routes
    path('travel-requests/', views.create_travel_request, name='create_travel_request'),
    path('travel-requests/view/', views.emp_view_travel_requests, name='view_travel_requests'),
    path('travel-requests/cancel/<int:pk>/', views.cancel_travel_request, name='cancel_travel_request'),
    path('travel-requests/edit/<int:pk>/', views.edit_travel_request, name='edit_travel_request'),
    path('travel-requests/resubmit/<int:pk>/', views.resubmit_travel_request, name='resubmit_travel_request'),

    # Manager Routes
    path('travel-requests/approve-reject/<int:pk>/', views.approve_or_reject_travel_request, name='approve_or_reject_travel_request'),
    path('manager/requests/', views.mngr_view_travel_requests, name='view_travel_requests'),  # View requests with filter and sort
    path('manager/requests/update/<int:pk>/', views.manager_note, name='update_travel_request'),  # Request further information

    # Admin Routes
    path('admin/requests/', views.view_all_travel_requests, name='view_all_travel_requests'),  # View all travel requests with filters, sorting, and search
    path('admin/requests/<int:pk>/request-info/', views.admin_note, name='request_additional_info'),  # Request additional information from employee
    path('admin/requests/<int:pk>/close/', views.close_approved_travel_request, name='close_approved_travel_request'),  # Close approved request
]
