from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from hortifruti.models import VendasModel
from hortifruti.repository import Repository


repository = Repository()

def index(request):

    context = repository.listarUltimasVendas(request)

    return render(request, 'index.html', context)


def registrarVendas(request):

    # Salvar os dados no banco
    repository.registrarVendas(request)

    return redirect('index')


def gerenciadorPage(request):

    context = repository.listarUltimasVendas(request)

    return render(request, 'gerenciadorPAGE.html', context)


def relatorioPage(request):
    """
    View que renderiza a página de relatório de vendas
    """
    context = repository.relatorioVendas(request)
    return render(request, 'relatorioPage.html', context)


def editar_venda(request, id_venda):


    if request.method == 'POST':
        # Processa o formulário de edição
        venda = repository.editarVenda(request, id_venda)
        messages.success(request, f'Venda #{id_venda} atualizada com sucesso!')
        return redirect('listar_vendas')  # Redireciona para a página de listagem
    else:
        # Exibe o formulário de edição
        venda = repository.obterVenda(id_venda)
        return render(request, 'editarVendaPage.html', {'venda': venda})

def remover_venda(request, id_venda):

    repository.removerVenda(id_venda)
    messages.success(request, f'Venda #{id_venda} removida com sucesso!')
    return redirect('listar_vendas')  # Redireciona para a página de listagem

def listar_vendas(request):
    context = repository.listarUltimasVendas(request)
    return render(request, 'gerenciadorPAGE.html', context)