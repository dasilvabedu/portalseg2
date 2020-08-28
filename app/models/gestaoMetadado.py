# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request
import datetime

def metadadoAptoExclusao ():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem['message'])
        return resultadoFinal, 400, header

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

    return resultado, retorno, header

def metadadoTotal ():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem['message'])
        return resultadoFinal, 400, header


    codificado, volta = gestaoAutenticacao.expandeToken()
    atual_usuario = volta['sub']
    atual_data = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

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

    return resultado, retorno, header

def metadadoSelecionado():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem['message'])
        return resultadoFinal, 400, header

    query_parameters = request.args
    mtt_identificador = query_parameters.get('mtt_identificador')
    mtt_tabela = query_parameters.get('mtt_tabela')
    camposDesejados = query_parameters.get('campos')

    resultadoTabela, resultadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(mtt_identificador, mtt_tabela, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['cabecalho'] = resultadoTabela[0]
    return resultadoFinal, retorno, header

def metadadoQualificado():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem['message'])
        return resultadoFinal, 400, header

    query_parameters = request.args
    mtt_identificador = query_parameters.get('mtt_identificador')
    mtt_tabela = query_parameters.get('mtt_tabela')

    if mtt_identificador is None and mtt_tabela is None:
        resultadoFinal = acessoBanco.montaRetorno(400, 'Parâmetros inválidos')
        resultadoFinal['aresposta']['texto'] = ''
        return resultadoFinal, 400, header

    resultadoTabela, resultadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(mtt_identificador, mtt_tabela, None, 'Sim')
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['cabecalho'] = resultadoTabela[0]
    resultadoFinal['campos'] = resultadoAtributo
    return resultadoFinal, retorno, header

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
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem['message'])
        return resultadoFinal, 400, header

    codificado, volta = gestaoAutenticacao.expandeToken()
    atual_usuario = volta['sub']
    atual_data = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')


    try:
        if not request.json:
            resposta = acessoBanco.montaRetorno(400, 'Argumento não é dado JSON')
            return resposta, 400
        dados = request.json

        mtt_tabela = dados['tabela']
        prefixo = mtt_tabela[0:4]

        resultadoTabela, resultadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(None, mtt_tabela, None,
                                                                                              'Sim')
        tipo = {}
        for i in range(len(resultadoAtributo)):
            mta_atributo = resultadoAtributo[i]['mta_atributo']
            mta_tipo = resultadoAtributo[i]['mta_tipo']
            tipo[mta_atributo] = mta_tipo

        comando = ''
        for j in dados.keys():
            identificador = prefixo + "identificador"
            if not (j == 'tabela' or j == identificador):
                if tipo[j] == 'text':
                    comando = comando + "," + j + " = '" + dados[j] + "'"
                else:
                    comando = comando + "," + j + " = " + str(dados[j])

        comando = comando[1:]
        condicao = "WHERE " + identificador + " = " + str(dados[identificador])

        dadosAlterado, retorno, mensagemRetorno = acessoBanco.alteraDado(mtt_tabela, comando, condicao)
        if retorno != 200:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno

        resposta = acessoBanco.montaRetorno(200, 'Requisicao plenamente atendida')
        return resposta, 200
    except:
        resposta = acessoBanco.montaRetorno(400, 'Erro interno. Possivelmente tabela ou campo inválido(s)')
        return resposta, 200

def metadadoValidado():
    # recupera tabelas do banco que sejam do modelo de dados do sistema
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem['message'])
        return resultadoFinal, 400, header

    codificado, volta = gestaoAutenticacao.expandeToken()
    atual_usuario = volta['sub']
    atual_data = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    camposDesejados = ('table_name')
    query = "WHERE table_schema='public' AND table_type='BASE TABLE'"
    tabelas, retorno, mensagemRetorno = acessoBanco.dado('information_schema.tables', query, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

    relacaoTabelas = "('"
    listaTabelas = []
    for k in range(len(tabelas)):
        if len(tabelas[k]['table_name']) > 4 and tabelas[k]['table_name'][3] == '_':
            relacaoTabelas = relacaoTabelas + tabelas[k]['table_name'] + "','"
            listaTabelas.append(tabelas[k]['table_name'])
    relacaoTabelas = relacaoTabelas[0:-2] + ')'

    # verifica tabelas armazenadas no banco que não existem mais
    camposDesejados = ('mtt_tabela')
    condicao = "WHERE mtt_tabela NOT IN " + relacaoTabelas
    aApagar, retorno, mensagemRetorno = acessoBanco.dado('mtt_metadadotabela', condicao, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

    if aApagar != []:
        for k in range(len(aApagar)):
            apagados, retorno, mensagemRetorno = acessoBanco.exclueMetadado(aApagar[k]['mtt_tabela'])
            if retorno != 200:
                return resultadoFinal, retorno, header

    # verificar tabelas que devem ser inseridas em metadados
    camposDesejados = ('mtt_tabela')
    metadados, retorno, mensagemRetorno = acessoBanco.dado('mtt_metadadotabela', None, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header
    listaMetadados = []
    for k in range(len(metadados)):
        listaMetadados.append(metadados[k]['mtt_tabela'])

    diferenca = []
    for k in range(len(listaTabelas)):
        if listaTabelas[k] not in listaMetadados:
            inseridos, retorno, mensagemRetorno = acessoBanco.insereMetadado(listaTabelas[k], atual_data, atual_usuario)
            diferenca.append(listaTabelas[k])

#   valida tabelas de atributos
    camposDesejados = 'mtt_tabela,mtt_identificador'
    metadados, retorno, mensagemRetorno = acessoBanco.dado('mtt_metadadotabela', None, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

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
            return resultadoFinal, retorno, header
        for j in range(len(information)):
            listaInformation.append(metadados[k]['mtt_tabela']+'###'+information[j]['column_name'])

        condicao = "WHERE mtt_identificador = " + str(metadados[k]['mtt_identificador'])
        atributos, retorno, mensagemRetorno = acessoBanco.dado('mta_metadadoatributo', condicao, camposMetadados, None)
        resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
        if retorno != 200:
            return resultadoFinal, retorno, header

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
        atributos, retorno, mensagemRetorno = acessoBanco.insereMetadadoAtributo(atributosIncluir, atual_data, atual_usuario)
        if retorno != 201:
            return resultadoFinal, retorno, header

    if atributosApagar != []:
        atributos, retorno, mensagemRetorno = acessoBanco.exclueMetadadoAtributo(atributosApagar)
        if retorno != 200:
            return resultadoFinal, retorno, header

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['cabecalho'] = listaTabelas

    return resultadoFinal, 200, '', header



