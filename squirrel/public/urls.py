from django.urls import path
from . import views

urlpatterns = [
    path('', views.howtouse, name='howtouse'),
    path('<user_id>', views.thatperson, name='thatperson'),
    path('search/', views.search, name='search'),
]
