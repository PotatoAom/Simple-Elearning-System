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
from student import views
from django.conf import settings


urlpatterns = [
    path('profile',views.profile,name='profile'),

    path('course',views.course,name='course'),
    path('course_view/<str:slug>', views.course_view, name='course_view'),

    path('enrolled',views.enrolled,name='enrolled'),
    path('enrolled_view/<str:slug>', views.enrolled_view, name='enrolled_view'),
    path('delete_enrolled/<int:pk>', views.delete_enrolled,name='delete_enrolled'),

    path('document_view/<str:slug>', views.document_view, name='document_view'),
    path('std_download/<int:pk>/', views.std_download_file, name='std_download_file'),

    path('<str:slug>/classroom_view/<int:classroom_id>', views.classroom_view, name='classroom_view'),

    path('assign_view/<str:slug>/<int:assignment_id>', views.assign_view, name='assign_view'),
    
    path('exam_view/<int:pk>', views.exam_view, name='exam_view'),
    path('start_exam/<int:pk>',views.start_exam,name='start_exam'),
    path('calculate-score',views.calculate_score),
    path('result/<str:slug>',views.result,name='result'),

    path('join_course/<int:pk>',views.join_course,name='join_course'),
    path('rate/<int:course_id>/', views.rate_course, name='rate_course'),
] 

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
