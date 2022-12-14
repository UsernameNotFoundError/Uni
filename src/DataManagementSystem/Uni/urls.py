from django.contrib import admin
from django.views.generic.base import RedirectView
from django.urls import path, include, re_path
from mainapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('', views.user_login, name="login"),
    path('update/', include('updateapp.urls')),
    path('admin/', admin.site.urls),
    path('home_page/', views.home_page, name="home_page"),
    path('logout/', views.user_logout, name="logout"),
    path('my_space', views.my_space, name="my_space"),
    path('results_page/<str:my_query>/', views.results_page, name="results_page"),
    path('search_page/', views.search_page, name="search_page"),
    path('sign_up/', views.sign_up_page, name="sign_up"),
    path('tree_search_page/', views.tree_search_page, name="tree_search_page"),
    path('test/<str:my_query>/', views._test_page, name="test_page"),
    re_path(r'^media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),
    path('<path:notfound404>', views.home_page, name="home_page"),

] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
