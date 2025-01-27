# serializers.py

from rest_framework import serializers
from .models import Produk, Kategori, Status

class KategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kategori
        fields = ['id', 'nama_kategori']

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'nama_status']

class ProdukSerializer(serializers.ModelSerializer):
    kategori = KategoriSerializer()
    status = StatusSerializer()

    class Meta:
        model = Produk
        fields = ['id', 'id_produk', 'nama_produk', 'harga', 'kategori', 'status']
