# -*- coding: utf-8 -*-

from ..views import acessoBanco
from flask import request

def dadoQualificado():
    query_parameters = request.args
    mtt_identificador = query_parameters.get('mtt_identificador')
    mtt_tabela = query_parameters.get('mtt_tabela')
    limite = query_parameters.get('limite')

    resultadoTabela, resultadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(mtt_identificador, mtt_tabela, None, 'Sim')
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

    tabela = resultadoTabela[0]['mtt_tabela']
    resultadoDado, retorno, mensagemRetorno = acessoBanco.dado(tabela, None, None, limite)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['cabecalho'] = resultadoTabela[0]
    resultadoFinal['campos'] = resultadoAtributo
    resultadoFinal['dados'] = resultadoDado
    return resultadoFinal, retorno

def dadoExtenso():
    query_parameters = request.args
    mtt_identificador = query_parameters.get('mtt_identificador')
    mtt_tabela = query_parameters.get('mtt_tabela')
    limite = query_parameters.get('limite')

#recupera metadados de tabela e de atributos da tabela de metadados de tabela
    resultadoMetadadoTabela, resultadoMetadadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(None, 'mtt_metadadotabela', None, 'Sim')
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

#recupera metadados de tabela e de atributos da tabela de metadados de atributo
    resultadoAtributoTabela, resultadoAtributoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(None, 'mta_metadadoatributo', None, 'Sim')
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

#recupera metadados de tabela e de atributos da tabela desejada
    resultadoTabela, resultadoAtributo, retorno, mensagemRetorno = acessoBanco.leMetadado(mtt_identificador, mtt_tabela, None, 'Sim')
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

#recupera os dados da tabela de interesse
    tabela = resultadoTabela[0]['mtt_tabela']
    resultadoDado, retorno, mensagemRetorno = acessoBanco.dado(tabela, None, None, limite)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

#traduz os nomes internos dos campos
    metadadoTabelaMontado = acessoBanco.ordenaDicionario(resultadoMetadadoAtributo, resultadoTabela)
    metadadoAtributoMontado = acessoBanco.ordenaDicionario(resultadoAtributoAtributo, resultadoAtributo)
    dadoMontado = acessoBanco.ordenaDicionario(resultadoAtributo, resultadoDado)

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['cabecalho'] = metadadoTabelaMontado
    resultadoFinal['campos'] = metadadoAtributoMontado
    resultadoFinal['dados'] = dadoMontado
    return resultadoFinal, retorno

def dadoExcluido():
    query_parameters = request.args
    mtt_tabela = query_parameters.get('mtt_tabela')
    identificador = query_parameters.get('identificador')
    if mtt_tabela == None or identificador == None:
        resultadoFinal = acessoBanco.montaRetorno(400, ' ')
        resultadoFinal['aresposta']['texto'] = 'Parametro(s) inválido(s)'
        return resultadoFinal, 400

    condicao = "WHERE " + mtt_tabela[0:4] + "identificador = " + str(identificador)
    informacao, retorno, mensagemRetorno = acessoBanco.exclueDado(mtt_tabela, condicao)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno

    resultadoFinal['aresposta']['texto'] = ''
    resultadoFinal['excluido'] = identificador
    return resultadoFinal, retorno

def dadoConvencionalAtualizado():
    try:
        if not request.json:
            resposta = acessoBanco.montaRetorno(400, 'Argumento não é dado JSON')
            return resposta, 400
        dados = request.json
 #       dados = json.loads(entrada)
        mtt_tabela = dados['tabela']
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