# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request


def documentacaoGeral():
    camposDesejados = 'doc_grupo,doc_nome,doc_descricao,doc_arquivo'
    condicao = "WHERE doc_grupo = 'geral'"
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

def documentacaoAgrupado(grupo=None):
    if grupo == "geral":
        header = {}
        camposDesejados = 'doc_grupo,doc_nome,doc_descricao,doc_arquivo'
        condicao = "WHERE doc_grupo = '" + grupo + "'"
        dados, retorno, mensagemRetorno = acessoBanco.leDado('doc_documentacaoassociada', condicao, camposDesejados)
    else:
        checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
        if not checa:
            return mensagem, 400, header
        query_parameters = request.args
#        grupo = query_parameters.get('grupo')
        uhe = query_parameters.get('emp')
        if grupo is None or len(grupo) < 1 or uhe is None or len(uhe) < 1:
            return {"message": "Parâmetros 'grupo' e 'emp' obrigatórios"}, 401, {}
        camposDesejados = 'a.doc_grupo,a.doc_nome,a.doc_descricao,a.doc_arquivo'
        condicao = "WHERE a.doc_grupo = '" + grupo + "' and a.doc_identificador = b.doc_identificador and b.emp_identificador = " + str(uhe)
        dados, retorno, mensagemRetorno = acessoBanco.leDado('doc_documentacaoassociada as a, doc_emp_documentacaoassociada_empreendimento as b', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    retorna=[]
    for i in range(len(dados)):
        lista = {}
        lista['grupo'] = dados[i][0]
        if grupo != 'geral':
            lista['empreendimento'] = str(uhe)
        lista['titulo'] = dados[i][1]
        lista['descricao'] = dados[i][2]
        lista['arquivo'] = dados[i][3]
        retorna.append(lista)

    listaMensagem = {}
    listaMensagem['documentos'] = retorna
    return listaMensagem, retorno, header

