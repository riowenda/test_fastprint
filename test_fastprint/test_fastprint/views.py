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
from .serializers import ProdukSerializer, KategoriSerializer, StatusSerializer
from django.views import View
from .forms import ProdukForm

# Proxy API class
class ProxyAPI(View):
    def post(self, request):
        api_url = "https://recruitment.fastprint.co.id/tes/api_tes_programmer"  # External API

        # Get data from POST request
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Send request to the external API
        response = requests.post(api_url, data={"username": username, "password": password})

        # Return the response from external API if successful
        if response.status_code == 200:
            return JsonResponse(response.json(), safe=False)
        else:
            return JsonResponse({"error": "Failed to fetch data from external API"}, status=500)

# Home page
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
        kategori = get_object_or_404(Kategori, pk=pk)
        kategori.delete()
        return redirect('kategori_list')
    return HttpResponse("Method Not Allowed", status=405)

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
        return redirect('status_list')
    return HttpResponse("Method Not Allowed", status=405)

# CRUD for Produk


def produk_list(request):
    nama_produk = request.GET.get('nama_produk', '')
    kategori_id = request.GET.get('kategori', '')
    status_id = request.GET.get('status', '')

    # Ambil semua kategori dan status untuk dropdown
    kategori_list = Kategori.objects.all()
    status_list = Status.objects.all()

    # Ambil semua produk
    produks = Produk.objects.all()

    # Filter produk berdasarkan nama produk
    if nama_produk:
        produks = produks.filter(nama_produk__icontains=nama_produk)

    # Filter berdasarkan kategori ID jika ada
    if kategori_id:
        produks = produks.filter(kategori__id=kategori_id)

    # Filter berdasarkan status ID jika ada
    if status_id:
        produks = produks.filter(status__id=status_id)

    return render(request, 'test_fastprint/produk_list.html', {
        'produks': produks,
        'kategori_list': kategori_list,
        'status_list': status_list,
    })

def produk_form(request, id=None):
    if id:
        produk = get_object_or_404(Produk, id=id)
    else:
        produk = None

    if request.method == 'POST':
        if produk:
            form = ProdukForm(request.POST, instance=produk)
        else:
            form = ProdukForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('produk_list')
    else:
        form = ProdukForm(instance=produk)

    return render(request, 'test_fastprint/produk_form.html', {'form': form})

def deleteProduk(request, pk):
    if request.method == "POST":
        produk = get_object_or_404(Produk, pk=pk)
        produk.delete()
        return redirect('produk_list')
    return HttpResponse("Method Not Allowed", status=405)

# Save Data (using serializers)
@csrf_exempt
def save_data(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Loop through each item in the data['data']
            for item in data['data']:
                if not isinstance(item, dict):
                    return JsonResponse({'error': 'Data item must be a valid dictionary'}, status=400)

                # Get or create Kategori
                kategori, created_kategori = Kategori.objects.get_or_create(nama_kategori=item['kategori'])
                kategori_id = kategori.id

                # Get or create Status
                status, created_status = Status.objects.get_or_create(nama_status=item['status'])
                status_id = status.id

                # Update or create Produk using serializer
                produk_data = {
                    'id_produk': item['id_produk'],
                    'nama_produk': item['nama_produk'],
                    'harga': item['harga'],
                    'kategori': kategori_id,
                    'status': status_id,
                }
                produk_serializer = ProdukSerializer(data=produk_data)
                if produk_serializer.is_valid():
                    produk_serializer.save()
                else:
                    return JsonResponse({'error': produk_serializer.errors}, status=400)

            return JsonResponse({'message': 'Data successfully saved!'}, status=200)

        except IntegrityError as e:
            return JsonResponse({'error': f'Integrity Error: {str(e)}'}, status=400)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Method Not Allowed'}, status=405)
