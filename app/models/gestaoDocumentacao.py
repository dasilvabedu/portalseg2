# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request


def documentacaoGeral():
    camposDesejados = 'doc_grupo,doc_nome,doc_descricao,doc_arquivo'
    condicao = "WHERE doc_grupo = 'Geral'"
    dados, retorno, mensagemRetorno = acessoBanco.leDado('doc_documentacaoassociada', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, retorno, {}
    if dados == []:
        return {}, 200, {}

    retorna=[]
    for i in range(len(dados)):
        lista = {}
        lista['grupo'] = dados[i][0]
        lista['nome'] = dados[i][1]
        lista['descricao'] = dados[i][2]
        lista['arquivo'] = dados[i][3]
        retorna.append(lista)

    listaMensagem = {}
    listaMensagem['documentos'] = retorna
    return listaMensagem, retorno, {}

def documentacaoAgrupado(grupo):
    if grupo == "geral":
        header = {}
    else:
        checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
        if not checa:
            return mensagem, 400, header

    camposDesejados = 'doc_grupo,doc_nome,doc_descricao,doc_arquivo'
    condicao = "WHERE doc_grupo = '" + grupo + "'"
    dados, retorno, mensagemRetorno = acessoBanco.leDado('doc_documentacaoassociada', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    retorna=[]
    for i in range(len(dados)):
        lista = {}
        lista['grupo'] = dados[i][0]
        lista['titulo'] = dados[i][1]
        lista['descricao'] = dados[i][2]
        lista['arquivo'] = dados[i][3]
        retorna.append(lista)

    listaMensagem = {}
    listaMensagem['documentos'] = retorna
    return listaMensagem, retorno, header

