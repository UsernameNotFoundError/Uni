from django.urls import path
from updateapp import views

urlpatterns = [
    path('db/', views.first_page, name="update_page"),
    path('', views.home_page,name="home_page"),
    path('test/', views.test_page,name="test_page"),
    path('a/', views.a_dance_the_devil, name="a_dance_the_devil"),

]