from django.contrib import admin
from django.urls import path
from . import views
from .views import save_data
from .views import (
    KategoriListView, KategoriCreateView, KategoriUpdateView, deleteKategori,
    StatusListView, StatusCreateView, StatusUpdateView, deleteStatus, 
    deleteProduk , ProxyAPI
)

urlpatterns = [
    path('', views.index, name='index'),  # Halaman index
    path('admin/', admin.site.urls),
     # Kategori
    path('kategori/', KategoriListView.as_view(), name='kategori_list'),
    path('kategori/add/', KategoriCreateView.as_view(), name='kategori_add'),
    path('kategori/<pk>/edit/', KategoriUpdateView.as_view(), name='kategori_edit'),
    path('kategori/delete/<int:pk>/', deleteKategori, name='delete_kategori'),

    # Status
    path('status/', StatusListView.as_view(), name='status_list'),
    path('status/add/', StatusCreateView.as_view(), name='status_add'),
    path('status/<pk>/edit/', StatusUpdateView.as_view(), name='status_edit'),
    path('status/delete/<int:pk>/', deleteStatus, name='delete_status'),
    

    # Produk
    path('produk/', views.produk_list, name='produk_list'),
    path('produk/add/', views.produk_form, name='produk_add'),
    path('produk/edit/<int:id>/', views.produk_form, name='produk_edit'),
    path('produk/delete/<int:pk>/', deleteProduk, name='delete_produk'),

    path('proxy-api/', ProxyAPI.as_view(), name='proxy_api'),
    path('save-data/', save_data, name='save_data'),
]
