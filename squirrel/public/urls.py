from django.urls import path
from . import views

urlpatterns = [
    path('', views.howtouse, name='howtouse'),
    path('<user_id>', views.thatperson, name='thatperson'),
    path('search/', views.search, name='search'),
    path('filter_search/<thename>', views.filter_search, name='filter_search'),
]
