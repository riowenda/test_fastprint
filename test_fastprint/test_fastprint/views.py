from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Produk, Kategori, Status
from django.http import JsonResponse
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import ProdukForm
from django.views import View

class ProxyAPI(View):
    def post(self, request):
        api_url = "https://recruitment.fastprint.co.id/tes/api_tes_programmer"  # API eksternal

        # Ambil data dari request POST
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Kirim permintaan ke API eksternal
        response = requests.post(api_url, data={"username": username, "password": password})

        # Jika API eksternal berhasil diakses, teruskan respons
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            return JsonResponse({"error": "Failed to fetch data from external API"}, status=500)

def index(request):
    return render(request, 'test_fastprint/index.html')

# CRUD for Kategori
class KategoriListView(ListView):
    model = Kategori
    template_name = 'test_fastprint/kategori_list.html'
    context_object_name = 'kategoris'

class KategoriCreateView(CreateView):
    model = Kategori
    fields = ['nama_kategori']
    template_name = 'test_fastprint/kategori_form.html'
    success_url = reverse_lazy('kategori_list')

class KategoriUpdateView(UpdateView):
    model = Kategori
    fields = ['nama_kategori']
    template_name = 'test_fastprint/kategori_form.html'
    success_url = reverse_lazy('kategori_list')

def deleteKategori(request, pk):
    if request.method == "POST":
        produk = get_object_or_404(Kategori, pk=pk)
        produk.delete()
        return redirect('kategori_list')  # Sesuaikan nama URL Anda
    return HttpResponse("Metode tidak diizinkan", status=405)


# CRUD for Status
class StatusListView(ListView):
    model = Status
    template_name = 'test_fastprint/status_list.html'
    context_object_name = 'statuses'

class StatusCreateView(CreateView):
    model = Status
    fields = ['nama_status']
    template_name = 'test_fastprint/status_form.html'
    success_url = reverse_lazy('status_list')

class StatusUpdateView(UpdateView):
    model = Status
    fields = ['nama_status']
    template_name = 'test_fastprint/status_form.html'
    success_url = reverse_lazy('status_list')

class StatusDeleteView(DeleteView):
    model = Status
    template_name = 'test_fastprint/status_confirm_delete.html'
    success_url = reverse_lazy('status_list')

def deleteStatus(request, pk):
    if request.method == "POST":
        status = get_object_or_404(Status, pk=pk)
        status.delete()
        return redirect('status_list')  # Sesuaikan nama URL Anda
    return HttpResponse("Metode tidak diizinkan", status=405)

# CRUD for Produk
from django.shortcuts import render
from .models import Produk

def produk_list(request):
    # Ambil parameter filter dari URL
    nama_produk = request.GET.get('nama_produk', '')
    kategori = request.GET.get('kategori', '')
    status = request.GET.get('status', '')

    # Query semua produk
    produks = Produk.objects.all()

    # Tambahkan filter jika parameter tidak kosong
    if nama_produk:
        produks = produks.filter(nama_produk__icontains=nama_produk)
    if kategori:
        produks = produks.filter(kategori__nama_kategori__icontains=kategori)
    if status:
        produks = produks.filter(status__nama_status__icontains=status)

    # Render ke template
    return render(request, 'test_fastprint/produk_list.html', {'produks': produks})


class ProdukCreateView(CreateView):
    model = Produk
    fields = ['id_produk', 'nama_produk', 'kategori', 'harga', 'status']
    template_name = 'test_fastprint/produk_form.html'
    success_url = reverse_lazy('produk_list')

class ProdukUpdateView(UpdateView):
    model = Produk
    fields = ['id_produk', 'nama_produk', 'kategori', 'harga', 'status']
    template_name = 'test_fastprint/produk_form.html'
    success_url = reverse_lazy('produk_list')

def deleteProduk(request, pk):
    if request.method == "POST":
        produk = get_object_or_404(Produk, pk=pk)
        produk.delete()
        return redirect('produk_list')  # Sesuaikan nama URL Anda
    return HttpResponse("Metode tidak diizinkan", status=405)

def produk_form(request, id=None):
    if id:
        produk = get_object_or_404(Produk, id=id)  # Untuk edit produk
    else:
        produk = None

    if request.method == 'POST':
        form = ProdukForm(request.POST, instance=produk)
        if form.is_valid():
            form.save()
            return redirect('produk_list')
    else:
        form = ProdukForm(instance=produk)

    return render(request, 'test_fastprint/produk_form.html', {'form': form})

@csrf_exempt
def save_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Loop untuk setiap item dalam data JSON
            for item in data['data']:  # Mengakses data dari key 'data' dalam JSON
                # Validasi format item untuk menghindari error
                if not isinstance(item, dict):
                    return JsonResponse({'error': 'Data item bukan dictionary yang valid'}, status=400)
                
                # Cek atau tambahkan kategori
                kategori, created_kategori = Kategori.objects.get_or_create(nama_kategori=item['kategori'])  # Referencing 'nama_kategori'
                kategori_id = kategori.id  # Ambil id kategori

                # Cek atau tambahkan status
                status, created_status = Status.objects.get_or_create(nama_status=item['status'])  # Referencing 'nama_status'
                status_id = status.id  # Ambil id status

                # Tambahkan atau update produk
                Produk.objects.update_or_create(
                    id=item['id_produk'],  # Menggunakan 'id_produk' dari JSON untuk mencocokkan 'id' produk
                    defaults={
                        'nama_produk': item['nama_produk'],
                        'harga': item['harga'],
                        'kategori_id': kategori_id,  # Menyimpan id kategori
                        'status_id': status_id,  # Menyimpan id status
                    }
                )
                
            return JsonResponse({'message': 'Data berhasil disimpan!'}, status=200)
        
        except IntegrityError as e:
            return JsonResponse({'error': f'Integrity Error: {str(e)}'}, status=400)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Metode tidak diizinkan'}, status=405)

