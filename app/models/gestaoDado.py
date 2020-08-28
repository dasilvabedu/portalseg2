# -*- coding: utf-8 -*-

from ..views import acessoBanco
from flask import request
from ..models import gestaoAutenticacao
import datetime

def dadoQualificado():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem['message'])
        return resultadoFinal, 400, header

    query_parameters = request.args
    mtt_identificador = query_parameters.get('mtt_identificador')
    mtt_tabela = query_parameters.get('mtt_tabela')
    limite = query_parameters.get('limite')

    resultadoTabela, resultadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(mtt_identificador, mtt_tabela, None, 'Sim')
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

    tabela = resultadoTabela[0]['mtt_tabela']
    resultadoDado, retorno, mensagemRetorno = acessoBanco.dado(tabela, None, None, limite)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['cabecalho'] = resultadoTabela[0]
    resultadoFinal['campos'] = resultadoAtributo
    resultadoFinal['dados'] = resultadoDado
    return resultadoFinal, retorno, header

def dadoExtenso():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem['message'])
        return resultadoFinal, 400, header

    query_parameters = request.args
    mtt_identificador = query_parameters.get('mtt_identificador')
    mtt_tabela = query_parameters.get('mtt_tabela')
    limite = query_parameters.get('limite')

#recupera metadados de tabela e de atributos da tabela de metadados de tabela
    resultadoMetadadoTabela, resultadoMetadadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(None, 'mtt_metadadotabela', None, 'Sim')
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

#recupera metadados de tabela e de atributos da tabela de metadados de atributo
    resultadoAtributoTabela, resultadoAtributoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(None, 'mta_metadadoatributo', None, 'Sim')
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

#recupera metadados de tabela e de atributos da tabela desejada
    resultadoTabela, resultadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(mtt_identificador, mtt_tabela, None, 'Sim')
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

#recupera os dados da tabela de interesse
    tabela = resultadoTabela[0]['mtt_tabela']
    resultadoDado, retorno, mensagemRetorno = acessoBanco.dado(tabela, None, None, limite)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

#traduz os nomes internos dos campos
    metadadoTabelaMontado = acessoBanco.ordenaDicionario(resultadoMetadadoAtributo, resultadoTabela)
    metadadoAtributoMontado = acessoBanco.ordenaDicionario(resultadoAtributoAtributo, resultadoAtributo)
    dadoMontado = acessoBanco.ordenaDicionario(resultadoAtributo, resultadoDado)

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['cabecalho'] = metadadoTabelaMontado
    resultadoFinal['campos'] = metadadoAtributoMontado
    resultadoFinal['dados'] = dadoMontado
    return resultadoFinal, retorno, header

def dadoExcluido():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem['message'])
        return resultadoFinal, 400, header

    query_parameters = request.args
    mtt_tabela = query_parameters.get('mtt_tabela')
    identificador = query_parameters.get('identificador')
    if mtt_tabela == None or identificador == None or len(mtt_tabela) == 0 or len(identificador) == 0:
        resultadoFinal = acessoBanco.montaRetorno(400, ' ')
        resultadoFinal['aresposta']['texto'] = 'Parametro(s) inválido(s)'
        return resultadoFinal, 400, header

    condicao = "WHERE " + mtt_tabela[0:4] + "identificador = " + str(identificador)
    informacao, retorno, mensagemRetorno = acessoBanco.exclueDado(mtt_tabela, condicao)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['excluido'] = identificador
    return resultadoFinal, retorno, header

def dadoConvencionalAtualizado():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem['message'])
        return resultadoFinal, 400, header

    codificado, volta = gestaoAutenticacao.expandeToken()
    atual_usuario = volta['sub']
    atual_data = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    try:

        if not request.json:
            resposta = acessoBanco.montaRetorno(400, 'Arquivo JSON não fornecido')
            return resposta, 400, header
        dados = request.json

        mtt_tabela = dados['tabela']
        if mtt_tabela not in ('mtt_metadadotabela','mtt_metadadoatributo'):
            resposta = acessoBanco.montaRetorno(400, 'Funcionalidade não permitida para esta tabela.')
            return resposta, 400, header

        prefixo = mtt_tabela[0:4]

        resultadoTabela, resultadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(None, mtt_tabela, None, 'Sim')
        tipo = {}
        for i in range (len(resultadoAtributo)):
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
        comando = comando + "," + prefixo +"identificadoratualizacao = " + str(atual_usuario) + "," + prefixo + "dataatualizacao = '" + atual_data + "'"
        condicao = "WHERE " + identificador + " = " + str(dados[identificador])

        dadosAlterado, retorno, mensagemRetorno = acessoBanco.alteraDado(mtt_tabela, comando, condicao)
        if retorno != 200:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        resposta = acessoBanco.montaRetorno(200, 'Requisicao plenamente atendida')
        return resposta, 200, header
    except:
        resposta = acessoBanco.montaRetorno(400, 'Erro interno. Possivelmente tabela ou campo inválido(s)')
        return resposta, 200, header