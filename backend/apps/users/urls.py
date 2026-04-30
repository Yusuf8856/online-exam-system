from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('password-reset-done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/admin/manage-students/', views.manage_students, name='manage_students'),
    path('dashboard/admin/manage-students/add/', views.add_student_view, name='add_student'),
    path('dashboard/admin/manage-teachers/', views.manage_teachers, name='manage_teachers'),
    path('dashboard/admin/manage-exams/', views.manage_exams, name='manage_exams'),
    path('dashboard/admin/question-bank/', views.question_bank, name='question_bank'),
    path('dashboard/admin/results/', views.view_results, name='view_results'),
    path('dashboard/admin/settings/', views.admin_settings, name='admin_settings'),
    path('dashboard/admin/user/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('dashboard/admin/exam/delete/<int:exam_id>/', views.delete_exam_admin, name='delete_exam_admin'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('profile/', views.profile_view, name='my_profile'), # Renamed for clarity
    path('profile/<int:user_id>/', views.profile_view, name='user_profile'), # For viewing specific user profiles
    path('profile/edit/<int:user_id>/', views.edit_profile_view, name='edit_profile'),
    path('logout/', views.logout_view, name='logout'),
]