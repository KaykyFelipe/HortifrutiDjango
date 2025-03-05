from django.shortcuts import render
from .models import VendasModel

def index(request):
    return render(request, 'index.html')

def registrarVendas(request):
    # Salvar os dados no banco
    nova_venda = VendasModel()
    nova_venda.id_venda = request.POST.get('id_venda')
    nova_venda.valor = request.POST.get('valor')
    nova_venda.data = request.POST.get('data')
    nova_venda.save()

    vendas = {
        'vendas': VendasModel.objects.all()
    }
    return render(request, 'index.html', vendas)
