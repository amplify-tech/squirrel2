from django.urls import path
from . import views

urlpatterns = [
    path('', views.howtouse, name='howtouse'),
    path('faq', views.faq, name='faq'),
    path('ask/', views.ask, name='ask'),
    path('ansfaq/', views.ansfaq, name='ansfaq'),
    path('delq/<qid>', views.delq, name='delq'),
    path('delans/<ansid>', views.delans, name='delans'),
    path('<user_id>', views.thatperson, name='thatperson'),
    path('search/', views.search, name='search'),
    path('filter_search/<thename>', views.filter_search, name='filter_search'),
]
