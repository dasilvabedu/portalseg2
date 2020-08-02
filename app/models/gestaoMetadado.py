# -*- coding: utf-8 -*-

from ..views import acessoBanco
from flask import request

def metadadoAptoExclusao ():
    camposDesejados = 'mtt_identificador,mtt_tabela,mtt_descricao'
    metadado, retorno, mensagemRetorno = acessoBanco.dado('mtt_metadadotabela', None, camposDesejados, None)
    resultado = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno == 200:
        metadadoResumido = []
        for i in range(len(metadado)):
            if metadado[i]['mtt_tabela'] not in ('mtt_metadadotabela,mta_metadadoatributo'):
                metadadoResumido.append(metadado[i])
        resultado['aresposta']['texto'] = ''
        resultado['cabecalho'] = metadadoResumido

    return resultado, retorno

def metadadoTotal ():
    query_parameters = request.args
    camposDesejados = query_parameters.get('campos')
    tipoTabela = query_parameters.get('mtt_tipo')
    formaEdicao = query_parameters.get('mtt_formaedicao')

    condicao = 'WHERE '
    if tipoTabela != None:
        condicao = condicao + "mtt_tipo = '" + tipoTabela + "' "
    if formaEdicao != None:
        if condicao == 'WHERE ':
            condicao = condicao + "mtt_formaedicao = '" + formaEdicao + "' "
        else:
            condicao = condicao + " AND mtt_formaedicao = '" + formaEdicao + "' "
    if condicao == 'WHERE ':
        condicao = None

    metadado, retorno, mensagemRetorno = acessoBanco.dado('mtt_metadadotabela', condicao, camposDesejados, None)
    resultado = acessoBanco.montaRetorno(retorno, mensagemRetorno)

    if retorno == 200:
        resultado['aresposta']['texto'] = ''
        resultado['cabecalho'] = metadado

    return resultado, retorno

def metadadoSelecionado():
    query_parameters = request.args
    mtt_identificador = query_parameters.get('mtt_identificador')
    mtt_tabela = query_parameters.get('mtt_tabela')
    camposDesejados = query_parameters.get('campos')

    resultadoTabela, resultadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(mtt_identificador, mtt_tabela, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['cabecalho'] = resultadoTabela[0]
    return resultadoFinal, retorno

def metadadoQualificado():
    query_parameters = request.args
    mtt_identificador = query_parameters.get('mtt_identificador')
    mtt_tabela = query_parameters.get('mtt_tabela')

    if mtt_identificador is None and mtt_tabela is None:
        resultadoFinal = acessoBanco.montaRetorno(400, 'Parâmetros inválidos')
        resultadoFinal['aresposta']['texto'] = ''
        return resultadoFinal, 400

    resultadoTabela, resultadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(mtt_identificador, mtt_tabela, None, 'Sim')
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['cabecalho'] = resultadoTabela[0]
    resultadoFinal['campos'] = resultadoAtributo
    return resultadoFinal, retorno

def metadadoInserido():
    query_parameters = request.args
    mtt_tabela = query_parameters.get('mtt_tabela')
    if mtt_tabela == None:
        resultadoFinal = acessoBanco.montaRetorno(400, ' ')
        resultadoFinal['aresposta']['texto'] = 'Parametro invalido'
        return resultadoFinal, 400

    informacao, retorno, mensagemRetorno = acessoBanco.insereMetadado(mtt_tabela)

    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 201:
        return resultadoFinal, retorno

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['inserido'] = informacao

    return resultadoFinal, retorno

def metadadoExcluido():
    query_parameters = request.args
    mtt_tabela = query_parameters.get('mtt_tabela')
    if mtt_tabela == None:
        resultadoFinal = acessoBanco.montaRetorno(400, ' ')
        resultadoFinal['aresposta']['texto'] = 'Parametro invalido'
        return resultadoFinal, 400

    informacao, retorno, mensagemRetorno = acessoBanco.exclueMetadado(mtt_tabela)

    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['excluido'] = informacao
    return resultadoFinal, retorno

def metadadoAtualizado():
    if not request.json:
        resposta = acessoBanco.montaRetorno(400, 'Argumento não é dado JSON')
        return resposta, 400
    entrada = request.json
    resposta = acessoBanco.montaRetorno(200, 'Era JSON')
    return resposta, 200

def metadadoValidado():
    # recupera tabelas do banco que sejam do modelo de dados do sistema
    camposDesejados = ('table_name')
    query = "WHERE table_schema='public' AND table_type='BASE TABLE'"
    tabelas, retorno, mensagemRetorno = acessoBanco.dado('information_schema.tables', query, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

    relacaoTabelas = "('"
    listaTabelas = []
    for k in range(len(tabelas)):
        if tabelas[k]['table_name'][3] == '_':
            relacaoTabelas = relacaoTabelas + tabelas[k]['table_name'] + "','"
            listaTabelas.append(tabelas[k]['table_name'])
    relacaoTabelas = relacaoTabelas[0:-2] + ')'

    # verifica tabelas armazenadas no banco que não existem mais
    camposDesejados = ('mtt_tabela')
    condicao = "WHERE mtt_tabela NOT IN " + relacaoTabelas
    aApagar, retorno, mensagemRetorno = acessoBanco.dado('mtt_metadadotabela', condicao, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

    if aApagar != []:
        for k in range(len(aApagar)):
            apagados, retorno, mensagemRetorno = acessoBanco.exclueMetadado(aApagar[k]['mtt_tabela'])
            if retorno != 200:
                return resultadoFinal, retorno

    # verificar tabelas que devem ser inseridas em metadados
    camposDesejados = ('mtt_tabela')
    metadados, retorno, mensagemRetorno = acessoBanco.dado('mtt_metadadotabela', None, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno
    listaMetadados = []
    for k in range(len(metadados)):
        listaMetadados.append(metadados[k]['mtt_tabela'])

    diferenca = []
    for k in range(len(listaTabelas)):
        if listaTabelas[k] not in listaMetadados:
            inseridos, retorno, mensagemRetorno = acessoBanco.insereMetadado(listaTabelas[k])
            diferenca.append(listaTabelas[k])

#   valida tabelas de atributos
    camposDesejados = 'mtt_tabela,mtt_identificador'
    metadados, retorno, mensagemRetorno = acessoBanco.dado('mtt_metadadotabela', None, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

    camposInformation = 'column_name'
    camposMetadados = 'mta_atributo'
    atributosApagar = []
    atributosIncluir = []

    for k in range(len(metadados)):
        listaInformation = []
        listaAtributos = []
        condicao = "WHERE table_name = '" + metadados[k]['mtt_tabela'] + "'"
        information, retorno, mensagemRetorno = acessoBanco.dado('information_schema.columns', condicao, camposInformation, None)
        resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
        if retorno != 200:
            return resultadoFinal, retorno
        for j in range(len(information)):
            listaInformation.append(metadados[k]['mtt_tabela']+'###'+information[j]['column_name'])

        condicao = "WHERE mtt_identificador = " + str(metadados[k]['mtt_identificador'])
        atributos, retorno, mensagemRetorno = acessoBanco.dado('mta_metadadoatributo', condicao, camposMetadados, None)
        resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
        if retorno != 200:
            return resultadoFinal, retorno
        for j in range(len(atributos)):
            pesquisa = metadados[k]['mtt_tabela']+'###'+atributos[j]['mta_atributo']
            listaAtributos.append(pesquisa)
    # verifica atributos armazenadas no banco que não existem mais
            if pesquisa not in listaInformation:
                atributosApagar.append(pesquisa)

        for k in listaInformation:
    # verifica atributos que devem ser incluidos
            if k not in listaAtributos:
                atributosIncluir.append(k)

    if atributosIncluir != []:
        atributos, retorno, mensagemRetorno = acessoBanco.insereMetadadoAtributo(atributosIncluir)
        if retorno != 201:
            return resultadoFinal, retorno

    if atributosApagar != []:
        atributos, retorno, mensagemRetorno = acessoBanco.exclueMetadadoAtributo(atributosApagar)
        if retorno != 200:
            return resultadoFinal, retorno

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['cabecalho'] = listaTabelas

    return resultadoFinal, 200, ''

def metadadoAtributoValidado():
    camposDesejados = ('mtt_tabela, mtt_identificador')
    metadados, retorno, mensagemRetorno = acessoBanco.dado('mtt_metadadotabela', None, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

    listaMetadados = []
    for i in metadados:
        listaMetadados.append(i['mtt_tabela'])

    inexistente = []
#    for dicionario in tabelas:
#        tabela = dicionario['table_name']
#        if tabela[3] == '_':
#            if tabela not in listaMetadados:
#                escolhido = {}
#                escolhido['tabela'] = tabela
#                inexistente.append(escolhido)

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['cabecalho'] = inexistente

    return resultadoFinal, retorno

