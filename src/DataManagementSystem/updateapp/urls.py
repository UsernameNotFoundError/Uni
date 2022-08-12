from django.urls import path
from updateapp import views


app_name = 'updateapp'

urlpatterns = [
    path('', views.home_page, name="home_page"),
    path('test/', views.test_page, name="test_page"),
    path('progress/', views.update_view, name="update_view_page"),
    path('fdog/', views.after_update_page, name="update_fdog_page"),
    path('mysql/', views.mysql_script, name="mysql_run"),
    path('clear_cache/', views.del_cache, name="clear_cache"),

] 