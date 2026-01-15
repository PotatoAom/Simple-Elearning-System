"""
URL configuration for finalproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from teacher import views
from django.conf import settings


urlpatterns = [
    path('profile',views.teacher_profile,name='profile'),
    path('success', views.success, name='success'),

    path('course',views.teacher_course,name='course' ),
    path('manage_course/<str:slug>',views.manage_course,name='manage_course' ),

    path('document_upload/<str:slug>',views.document_upload,name='document_upload' ),
    path('download/<int:pk>/', views.download_file, name='download_file'),

    path('manage_course_content/<str:slug>',views.manage_course_content,name='manage_course_content' ),
    path('edit_course_content/<str:slug>/<int:pk>',views.edit_course_content,name='edit_course_content' ),
    path('get_course_classrooms/<str:slug>/', views.get_course_classrooms, name='get_course_classrooms'),
    path('create_textbox/', views.create_textbox, name='create_textbox'),
    path('create_videobox/', views.create_videobox, name='create_videobox'),
    path('create_imagebox/', views.create_imagebox, name='create_imagebox'),
    path('delete_box/<str:box_type>/<int:box_id>/', views.delete_box, name='delete_box'),
    path('get_classroom_boxes/<int:classroom_id>/', views.get_classroom_boxes, name='get_classroom_boxes'),
    
    path('manage_assignment/<str:slug>', views.manage_assignment, name='manage_assignment'),
    path('edit_assignment/<str:slug>/<int:pk>',views.edit_assignment,name='edit_assignment' ),
    

    path('manage_exam/<int:pk>', views.manage_exam, name='manage_exam'),
    path('edit_exam/<int:course_id>/<int:pk>', views.edit_exam, name='edit_exam'),

    path('manage_score/<str:slug>', views.manage_score,name='manage_score'),

    path('delete_content/<int:pk>', views.delete_content,name='delete_content'),
    path('delete_course/<int:pk>', views.delete_course,name='delete_course'),
    path('delete_doc/<int:pk>', views.delete_doc,name='delete_doc'),
    path('delete_assign/<int:pk>', views.delete_assign,name='delete_assign'),
    path('delete_exam/<int:pk>', views.delete_exam,name='delete_exam'),
    path('delete_question/<int:pk>', views.delete_question,name='delete_question'),
] 

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
