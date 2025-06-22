from django.contrib import admin
from django.urls import path
from Neural_algo import views
urlpatterns = [
    path('',views.index, name='home'),
    path('home/',views.index, name='home'),
    path('contact/',views.contact, name='contact'),
    path('about/',views.about, name='about'),
    path('editor/',views.editor, name='editor'),
    path('login/',views.login_view, name='login'),
    path('register/',views.register_view, name='register'),
    path('dashboard/',views.admin_dashboard, name='admin'),
    path('dashboard/index',views.admin_dashboard, name='admin'),
    path('dashboard/profile', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/add_questions',views.add_questions, name='add_questions'),
    path('dashboard/edit_questions/<int:question_id>/',views.edit_questions, name='edit_questions'),
    path('dashboard/delete_questions/<int:question_id>/', views.delete_questions, name='delete_questions'),
    path('dashboard/view_questions',views.view_questions, name='view_questions'),
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/solve_questions/', views.solve_questions, name='solve_questions'),
    path('user/solve_question/<int:question_id>/', views.solve_question, name='solve_question'),
]