from django.urls import path
from updateapp import views


app_name = 'updateapp'

urlpatterns = [
    path('', views.home_page, name="home_page"),
    path('test/', views.test_page, name="test_page"),
    path('progress/', views.update_view, name="update_view_page"),
    path('fdog/', views.update_view, name="update_view_page")

]