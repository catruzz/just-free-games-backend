from django.contrib import admin
from django.urls import path
from backend import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token-auth/', views.CustomAuthToken.as_view()),
    path('api/platforms/', views.PlatformListView.as_view()),
    path('api/suppliers/', views.SupplierListView.as_view()),
    path('api/suppliers/<str:pk>/', views.SupplierDetailView.as_view()),
    path('api/giveaways/', views.GiveawayListView.as_view()),
    path('api/giveaways/<int:pk>/', views.GiveawayDetailView.as_view()),
]
