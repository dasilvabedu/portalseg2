# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request
import datetime


def moduloNovoLista():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header

    if request.method == 'POST':
        if not request.json:
            return {"message": "Dados de entrada não fornecidos"}, 404, {}

        token, dadosToken = gestaoAutenticacao.expandeToken()
        entrada = request.json
        sigla = entrada.get('sigla')
        nome = entrada.get('nome')
        resultadoFinal, retorno = trataModuloIncluido(dadosToken["sub"], dadosToken['name'],sigla, nome)
        return resultadoFinal, retorno, header
    elif request.method == 'GET':
        resultadoFinal, retorno = listaModulo()
        return resultadoFinal, retorno, header

    return {"message":"Método invalido"}, 400, {}

def moduloAtual(id):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    if request.method == 'PATCH':
        token, dadosToken = gestaoAutenticacao.expandeToken()

        #atualização de perfil
        if not request.json:
            return {'"message": "Dados de entrada não fornecidos"'}, 404, header

        entrada = request.json
        sigla = entrada.get('sigla')
        nome = entrada.get('nome')
        resultadoFinal, retorno = trataModuloAlterado(id, dadosToken["sub"], dadosToken['name'], sigla, nome)
        return resultadoFinal, retorno, header

    elif request.method == 'DELETE':
        resultadoFinal, retorno = trataModuloDeletado(id)
        return resultadoFinal, retorno, header

    elif request.method == 'GET':

        checa, mensagem, dados = moduloEspecifico(id)
        if not checa:
            return {'message': 'Não foi possível recuperar dados deste modulo'}, 404, header
        return dados, 200, header

    return {"message":"Método invalido"}, 400, header

def listaModulo():
    camposDesejados = 'moc_identificador, moc_sigla, moc_nome, moc_identificadoratualizacao, moc_dataatualizacao,usu_nome'
    condicao = "INNER JOIN usu_usuario ON usu_identificador = moc_modulocapacitacao.moc_identificadoratualizacao"
    dados, retorno, mensagemRetorno = acessoBanco.leDado('moc_modulocapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    dadosRetorno = []
    dicRetorno = {}

    for i in range(len(dados)):

        mensagem = {}
        mensagem['id'] = dados[i][0]
        mensagem['sigla'] = dados[i][1]
        mensagem['nome'] = dados[i][2]
        mensagem['atualizador'] = dados[i][5]
        mensagem['data'] = dados[i][4].strftime('%Y-%m-%d %H:%M:%S')
        dadosRetorno.append(mensagem)
    dicRetorno['modulos'] = dadosRetorno
    return dicRetorno, 200

def moduloEspecifico(id):
    camposDesejados = 'moc_identificador, moc_sigla, moc_nome, moc_identificadoratualizacao, moc_dataatualizacao,usu_nome'
    condicao = "INNER JOIN usu_usuario ON usu_identificador = moc_modulocapacitacao.moc_identificadoratualizacao "
    condicao = condicao + "WHERE moc_identificador = " + str(id)
    dadosModulo, retorno, mensagemRetorno = acessoBanco.leDado('moc_modulocapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return False, {"message": "Erro no acesso ao banco de dados"}, {}
    if retorno != 200:
        return False, {"message": "Não foi possivel recuperar os dados para este módulo"}, {}

    for i in range(len(dadosModulo)):

        mensagem = {}
        mensagem['id'] = dadosModulo[i][0]
        mensagem['sigla'] = dadosModulo[i][1]
        mensagem['nome'] = dadosModulo[i][2]
        mensagem['atualizador'] = dadosModulo[i][5]
        mensagem['data'] = dadosModulo[i][4].strftime('%Y-%m-%d %H:%M:%S')



        # recupera os perfis de onde participa
        camposDesejados = 'trc_moc_sequencia, trc_sigla, trc_nome'
        condicao = "INNER JOIN trc_trilhacapacitacao ON trc_trilhacapacitacao.trc_identificador = trc_moc_trilhacapacitacao_modulocapacitacao.trc_identificador "
        condicao = condicao + "WHERE moc_identificador = " + str(id)
        dadosTrilha, retorno, mensagemRetorno = acessoBanco.leDado('trc_moc_trilhacapacitacao_modulocapacitacao', condicao, camposDesejados)
        if retorno == 400:
            return False, {"message": "Erro no acesso ao banco de dados"}, {}

        listTrilha = []
        for j in range(len(dadosTrilha)):
            mensagemTrilha = {}
            mensagemTrilha['sequencia_trilha'] = dadosTrilha[j][0]
            mensagemTrilha['sigla'] = dadosTrilha[j][1]
            mensagemTrilha['nome'] = dadosTrilha[j][2]
            listTrilha.append(mensagemTrilha)
        mensagem['trilhas']  = listTrilha
    return True, {}, mensagem

def trataModuloIncluido(usu_identificador, usu_nome, sigla, nome):
    cheque = {}
    cheque['message'] = ''
    erro = False

    if sigla is None or type(sigla) is not str or len(sigla) < 1:
        cheque['message'] = 'Sigla é obrigatória e textual.'
        erro = True

    if nome is None or type(nome) is not str or len(nome) < 1:
        if not erro:
            cheque['message'] = 'Nome é obrigatório e textual.'
        else:
            cheque['message'] = cheque['message'] + ' - Nome é obrigatório e textual.'
        erro = True

    if erro:
        return cheque, 404

    # verifica se  os parãmetros informados são únicos
    camposDesejados = 'moc_identificador'
    condicao = "WHERE moc_sigla = '" + sigla + "' or moc_nome = '" + nome + "'"
    dados, retorno, mensagemRetorno = acessoBanco.leDado('moc_modulocapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        return {"message": "Já existe Módulo de Capacitação com um ou mais parâmetros fornecidos."}, 404

    # recupera o último identificador
    camposDesejados = 'max(moc_identificador)'
    dados, retorno, mensagemRetorno = acessoBanco.leDado('moc_modulocapacitacao', None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    camposDesejados = "moc_identificador, moc_sigla, moc_nome, moc_identificadoratualizacao, moc_dataatualizacao"
    valores = str(proximoNumero) + ",'" + sigla + "','" + nome + "'," + str(usu_identificador) + ",'" + agora + "'"
    dados, retorno, header = acessoBanco.insereDado('moc_modulocapacitacao', camposDesejados, valores)

    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem['id'] = proximoNumero
    mensagem['sigla'] = sigla
    mensagem['nome'] = nome
    mensagem['atualizador'] = usu_nome
    mensagem['data'] = agora


    return mensagem, 201

def trataModuloAlterado(id,usu_identificador, usu_nome, sigla, nome):
    cheque = {}
    cheque['message'] = ''
    erro = False
    altera = False

    if sigla is not None:
        if type(sigla) is not str or len(sigla) < 1:
            cheque['message'] = 'Sigla é obrigatória e textual.'
            erro = True
        else:
            altera = True

    if nome is not None:
        if type(nome) is not str or len(nome) < 1:
            if not erro:
                cheque['message'] = 'Nome é obrigatório e textual.'
            else:
                cheque['message'] = cheque['message'] + ' - Nome é obrigatório e textual.'
            erro = True
        else:
            altera = True

    if erro:
        return cheque, 404

    if not altera:
        return {"message": "Nada a ser alterado"}, 404

    # verifica se  existe o registro informado
    condicao = "WHERE moc_identificador = " + str(id)
    camposDesejados = 'moc_identificador, moc_sigla, moc_nome, moc_identificadoratualizacao, moc_dataatualizacao'
    dadosAtual, retorno, mensagemRetorno = acessoBanco.leDado('moc_modulocapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dadosAtual == []:
        return {"message": "Não existe Módulo com o identificador informado"}, 404

    if sigla is None:
        sigla = dadosAtual[0][1]

    if nome is None:
        nome = dadosAtual[0][2]

    # verifica se  os parãmetros informados são únicos
    camposDesejados = 'moc_identificador'
    condicao = "WHERE moc_sigla = '" + sigla + "' or moc_nome = '" + nome + "'"
    dados, retorno, mensagemRetorno = acessoBanco.leDado('moc_modulocapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        if dados[0][0] != id:
            return {"message": "Já existe Módulo de Capacitação com um ou mais parâmetros fornecidos."}, 404

    agora = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    condicao = "WHERE moc_identificador = " + str(id)
    valores = "moc_sigla = '" + sigla + "', moc_nome = '" + nome + "', moc_identificadoratualizacao = " + str(usu_identificador) + ", moc_dataatualizacao = '" + agora + "'"
    dados, retorno, header = acessoBanco.alteraDado('moc_modulocapacitacao', valores, condicao)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem['id'] = id
    mensagem['sigla'] = sigla
    mensagem['nome'] = nome
    mensagem['atualizador'] = usu_nome
    mensagem['data'] = agora

    return mensagem, 200

def trataModuloDeletado(identificador):

    if identificador is None or not acessoBanco.inteiro(identificador):
        return {'message': 'Identificador é obrigatório e numérico.'}, 404

    # verifica se esta transacao  existe

    camposDesejados = 'moc_identificador'
    condicao = "WHERE moc_identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.leDado('moc_modulocapacitacao', condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400
    if dados == []:
        return {"message": "Não existe Módulo com o identificador fornecido."}, 404


    # verifica se esta transacao não está associada a trilha de capacitação

    camposDesejados = 'trc_identificador'
    condicao = "WHERE moc_identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.leDado('trc_moc_trilhacapacitacao_modulocapacitacao', condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400
    if dados != []:
        return {"message": "Módulo associado a Trilha de Capacitação não pode ser excluído."}, 404

    # exclue

    condicao = "WHERE moc_identificador = " + str(identificador)
    dados, retorno, mensagem = acessoBanco.exclueDado('moc_modulocapacitacao', condicao)

    if retorno != 200:
        return {"message": mensagem}, retorno

    return {}, 200

def trilhaNovoLista():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header

    if request.method == 'POST':
        if not request.json:
            return {"message": "Dados de entrada não fornecidos"}, 404, {}

        token, dadosToken = gestaoAutenticacao.expandeToken()
        entrada = request.json
        sigla = entrada.get('sigla')
        nome = entrada.get('nome')
        perfil = entrada.get('perfil')
        resultadoFinal, retorno = trataTrilhaIncluida(dadosToken["sub"], dadosToken['name'],sigla, nome, perfil)
        return resultadoFinal, retorno, header
    elif request.method == 'GET':
        resultadoFinal, retorno = listaTrilha()
        return resultadoFinal, retorno, header

    return {"message":"Método invalido"}, 400, {}

def trilhaAtual(id):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    if request.method == 'PATCH':
        token, dadosToken = gestaoAutenticacao.expandeToken()

        #atualização de perfil
        if not request.json:
            return {'"message": "Dados de entrada não fornecidos"'}, 404, header

        entrada = request.json
        sigla = entrada.get('sigla')
        nome = entrada.get('nome')
        perfil = entrada.get('perfil')
        resultadoFinal, retorno = trataTrilhaAlterada(id, dadosToken["sub"], dadosToken['name'], sigla, nome, perfil)
        return resultadoFinal, retorno, header

    elif request.method == 'DELETE':
        resultadoFinal, retorno = trataTrilhaDeletada(id)
        return resultadoFinal, retorno, header

    elif request.method == 'GET':

        checa, mensagem, dados = trilhaEspecifica(id)
        if not checa:
            return {'message': 'Não foi possível recuperar dados deste modulo'}, 404, header
        return dados, 200, header

    return {"message":"Método invalido"}, 400, header

def listaTrilha():
    camposDesejados = 'trc_identificador, trc_sigla, trc_nome, pfu_sigla, trc_dataatualizacao,usu_nome'
    condicao = "INNER JOIN usu_usuario ON usu_identificador = trc_trilhacapacitacao.trc_identificadoratualizacao "
    condicao = condicao + "INNER JOIN pfu_perfilusuario ON pfu_perfilusuario.pfu_identificador = trc_trilhacapacitacao.pfu_identificador "
    dados, retorno, mensagemRetorno = acessoBanco.leDado('trc_trilhacapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    dadosRetorno = []

    for i in range(len(dados)):

        mensagem = {}
        mensagem['id'] = dados[i][0]
        mensagem['sigla'] = dados[i][1]
        mensagem['nome'] = dados[i][2]
        mensagem['perfil_associado'] = dados[i][3]
        mensagem['atualizador'] = dados[i][5]
        mensagem['data'] = dados[i][4].strftime('%Y-%m-%d %H:%M:%S')

        dadosRetorno.append(mensagem)
    dicRetorno = {}
    dicRetorno['trilhas'] = dadosRetorno
    return dicRetorno, 200

def trilhaEspecifica(id):
    camposDesejados = 'trc_identificador, trc_sigla, trc_nome, pfu_sigla, trc_dataatualizacao,usu_nome'
    condicao = "INNER JOIN usu_usuario ON usu_identificador = trc_trilhacapacitacao.trc_identificadoratualizacao "
    condicao = condicao + "INNER JOIN pfu_perfilusuario ON pfu_perfilusuario.pfu_identificador = trc_trilhacapacitacao.pfu_identificador "
    condicao = condicao + "WHERE trc_identificador = " + str(id)
    dadosTrilha, retorno, mensagemRetorno = acessoBanco.leDado('trc_trilhacapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return False, {"message": "Erro no acesso ao banco de dados"}, {}
    if retorno != 200:
        return False, {"message": "Não foi possivel recuperar os dados para esta trilha"}, {}

    dadosRetorno = []

    for i in range(len(dadosTrilha)):

        mensagem = {}
        mensagem['id'] = dadosTrilha[i][0]
        mensagem['sigla'] = dadosTrilha[i][1]
        mensagem['nome'] = dadosTrilha[i][2]
        mensagem['perfil_associado'] = dadosTrilha[i][3]
        mensagem['atualizador'] = dadosTrilha[i][5]
        mensagem['data'] = dadosTrilha[i][4].strftime('%Y-%m-%d %H:%M:%S')

        dadosRetorno.append(mensagem)

        # recupera os modulos de onde participa
        camposDesejados = 'trc_moc_sequencia, moc_sigla, moc_nome'
        condicao = "INNER JOIN moc_modulocapacitacao ON moc_modulocapacitacao.moc_identificador = trc_moc_trilhacapacitacao_modulocapacitacao.moc_identificador "
        condicao = condicao + "WHERE trc_identificador = " + str(id)
        dadosTrilha, retorno, mensagemRetorno = acessoBanco.leDado('trc_moc_trilhacapacitacao_modulocapacitacao', condicao, camposDesejados)
        if retorno == 400:
            return False, {"message": "Erro no acesso ao banco de dados"}, {}

        listTrilha = []
        for j in range(len(dadosTrilha)):
            mensagemTrilha = {}
            mensagemTrilha['sequencia_trilha'] = dadosTrilha[j][0]
            mensagemTrilha['sigla'] = dadosTrilha[j][1]
            mensagemTrilha['nome'] = dadosTrilha[j][2]
            listTrilha.append(mensagemTrilha)
        mensagem['modulos']  = listTrilha
    return True, {}, mensagem

def trataTrilhaIncluida(usu_identificador, usu_nome, sigla, nome, perfil):
    cheque = {}
    cheque['message'] = ''
    erro = False

    if sigla is None or type(sigla) is not str or len(sigla) < 1:
        cheque['message'] = 'Sigla é obrigatória e textual.'
        erro = True

    if nome is None or type(nome) is not str or len(nome) < 1:
        if not erro:
            cheque['message'] = 'Nome é obrigatório e textual.'
        else:
            cheque['message'] = cheque['message'] + ' - Nome é obrigatório e textual.'
        erro = True

    if perfil is None or not acessoBanco.inteiro(perfil):
        if not erro:
            cheque['message'] = 'Perfil é obrigatório e numérico.'
        else:
            cheque['message'] = cheque['message'] + ' - Perfil é obrigatório e numérico.'
        erro = True

    if erro:
        return cheque, 404

    # verifica se  os parãmetros informados são únicos
    camposDesejados = 'trc_identificador'
    condicao = "WHERE trc_sigla = '" + sigla + "' or trc_nome = '" + nome + "'"
    dados, retorno, mensagemRetorno = acessoBanco.leDado('trc_trilhacapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        return {"message": "Já existe Trilha de Capacitação com um ou mais parâmetros fornecidos."}, 404

    # verifica se  perfil existe
    camposDesejados = 'pfu_identificador'
    condicao = "WHERE pfu_identificador = " + str(perfil)
    dados, retorno, mensagemRetorno = acessoBanco.leDado('pfu_perfilusuario', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        return {"message": "Não existe Perfil de Usuário com código informado."}, 404


    # recupera o último identificador
    camposDesejados = 'max(trc_identificador)'
    dados, retorno, mensagemRetorno = acessoBanco.leDado('trc_trilhacapacitacao', None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    camposDesejados = "trc_identificador, trc_sigla, trc_nome, trc_identificadoratualizacao, trc_dataatualizacao, pfu_identificador"
    valores = str(proximoNumero) + ",'" + sigla + "','" + nome + "'," + str(usu_identificador) + ",'" + agora + "'," + str(perfil)
    dados, retorno, header = acessoBanco.insereDado('trc_trilhacapacitacao', camposDesejados, valores)

    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem['id'] = proximoNumero
    mensagem['sigla'] = sigla
    mensagem['nome'] = nome
    mensagem['perfil_associado'] = perfil
    mensagem['atualizador'] = usu_nome
    mensagem['data'] = agora

    return mensagem, 201

def trataTrilhaAlterada(id,usu_identificador, usu_nome, sigla, nome, perfil):
    cheque = {}
    cheque['message'] = ''
    erro = False
    altera = False

    if sigla is not None:
        if type(sigla) is not str or len(sigla) < 1:
            cheque['message'] = 'Sigla é obrigatória e textual.'
            erro = True
        else:
            altera = True

    if nome is not None:
        if type(nome) is not str or len(nome) < 1:
            if not erro:
                cheque['message'] = 'Nome é obrigatório e textual.'
            else:
                cheque['message'] = cheque['message'] + ' - Nome é obrigatório e textual.'
            erro = True
        else:
            altera = True

    if perfil is not None:
        if not acessoBanco.inteiro(perfil):
            if not erro:
                cheque['message'] = 'Perfil é obrigatório e numérico.'
            else:
                cheque['message'] = cheque['message'] + ' - Perfil é obrigatório e numérico.'
            erro = True
        else:
            altera = True

    if erro:
        return cheque, 404

    if not altera:
        return {"message": "Nada a ser alterado"}, 404

    # verifica se  existe o registro informado
    condicao = "WHERE trc_identificador = " + str(id)
    camposDesejados = 'trc_sigla, trc_nome, pfu_identificador, trc_identificadoratualizacao, trc_dataatualizacao'
    dadosAtual, retorno, mensagemRetorno = acessoBanco.leDado('trc_trilhacapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dadosAtual == []:
        return {"message": "Não existe Trilha com o identificador informado"}, 404

    if sigla is None:
        sigla = dadosAtual[0][0]

    if nome is None:
        nome = dadosAtual[0][1]

    if perfil is None:
        perfil = dadosAtual[0][2]

    # verifica se  os parãmetros informados são únicos
    camposDesejados = 'trc_identificador'
    condicao = "WHERE trc_sigla = '" + sigla + "' or trc_nome = '" + nome + "'"
    dados, retorno, mensagemRetorno = acessoBanco.leDado('trc_trilhacapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        if dados[0][0] != id:
            return {"message": "Já existe Trilha de Capacitação com um ou mais parâmetros fornecidos."}, 404

    agora = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    condicao = "WHERE trc_identificador = " + str(id)
    valores = "trc_sigla = '" + sigla + "', trc_nome = '" + nome + "', trc_identificadoratualizacao = " + str(usu_identificador) + ", trc_dataatualizacao = '" + agora + "'"
    valores = valores + ", pfu_identificador = " + str(perfil)
    dados, retorno, header = acessoBanco.alteraDado('trc_trilhacapacitacao', valores, condicao)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem['id'] = id
    mensagem['sigla'] = sigla
    mensagem['nome'] = nome
    mensagem['perfil_associado'] = perfil
    mensagem['atualizador'] = usu_nome
    mensagem['data'] = agora


    return mensagem, 200

def trataTrilhaDeletada(identificador):

    if identificador is None or not acessoBanco.inteiro(identificador):
        return {'message': 'Identificador é obrigatório e numérico.'}, 404

    # verifica se esta trilha  existe

    camposDesejados = 'trc_identificador'
    condicao = "WHERE trc_identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.leDado('trc_trilhacapacitacao', condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400
    if dados == []:
        return {"message": "Não existe Trilha com o identificador fornecido."}, 404

    # exclue

    condicao = "WHERE trc_identificador = " + str(identificador)
    dados, retorno, mensagem = acessoBanco.exclueDado('trc_trilhacapacitacao', condicao)

    if retorno != 200:
        return {"message": mensagem}, retorno

    return {}, 200

def trilhaQualifica(id):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    if not request.json:
        return {'"message": "Dados de entrada não fornecidos"'}, 404, header

    entrada = request.json
    modulo = entrada.get('modulo')

    if request.method == 'POST':
        seq = entrada.get('sequencia')

        token, dadosToken = gestaoAutenticacao.expandeToken()
        resultadoFinal, retorno = trataTrilhaQualificaIncluida(id, dadosToken["sub"], dadosToken['name'], modulo, seq)
        return resultadoFinal, retorno, header

    elif request.method == 'DELETE':
        resultadoFinal, retorno = trataTrilhaQualificaDeletada(id, modulo)
        return resultadoFinal, retorno, header

    return {"message":"Método invalido"}, 400, header

def trataTrilhaQualificaIncluida(id, usu_identificador, usu_nome, modulo, seq):
    cheque = {}
    cheque['message'] = ''
    erro = False

    if modulo is None or not acessoBanco.inteiro(modulo):
        cheque['message'] = 'Identificador do Móculo é obrigatório e numérico.'
        erro = True

    if seq is None or not acessoBanco.inteiro(seq):
        if not erro:
            cheque['message'] = 'Sequência é obrigatória e numérica.'
        else:
            cheque['message'] = cheque['message'] + ' - SeqUência é obrigatória e numérica.'
        erro = True

    if erro:
        return cheque, 404

    # verifica se  os parãmetros informados existem
    camposDesejados = 'trc_identificador'
    condicao = "WHERE trc_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado('trc_trilhacapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        return {"message": "Não existe Trilha de Capacitação com identificador fornecido"}, 404

    # verifica se  módulo existe
    camposDesejados = 'moc_identificador'
    condicao = "WHERE moc_identificador = " + str(modulo)
    dados, retorno, mensagemRetorno = acessoBanco.leDado('moc_modulocapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        return {"message": "Não existe Módulo com identificador informado."}, 404

    # verifica se  os dados para inclusão já existem na base
    camposDesejados = 'moc_identificador'
    condicao = "WHERE moc_identificador = " + str(modulo) + " and trc_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado('trc_moc_trilhacapacitacao_modulocapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        return {"message": "Já existe associação com os parâmetros informados."}, 404

    # verifica se  a sequencia já existe para a trilha fornecida
    camposDesejados = 'moc_identificador'
    condicao = "WHERE trc_moc_sequencia = " + str(seq) + " and trc_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado('trc_moc_trilhacapacitacao_modulocapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        return {"message": "Já existe a sequência para a trilha informada."}, 404


    agora = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    camposDesejados = "trc_identificador, moc_identificador, trc_moc_sequencia, trc_moc_identificadoratualizacao, trc_moc_dataatualizacao"
    valores = str(id) + "," + str(modulo) + "," + str(seq) + "," + str(usu_identificador) + ",'" + agora + "'"
    dados, retorno, header = acessoBanco.insereDado('trc_moc_trilhacapacitacao_modulocapacitacao', camposDesejados, valores)

    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem['trilha'] = id
    mensagem['modulo'] = modulo
    mensagem['sequencia'] = seq
    mensagem['atualizador'] = usu_nome
    mensagem['data'] = agora

    return mensagem, 201

def trataTrilhaQualificaDeletada(id, modulo):
    cheque = {}
    cheque['message'] = ''

    if modulo is None or not acessoBanco.inteiro(modulo):
        cheque['message'] = 'Identificador do Módulo é obrigatório e numérico.'
        return cheque, 404

    # verifica se  os parãmetros informados existem
    camposDesejados = 'moc_identificador'
    condicao = "WHERE moc_identificador = " + str(modulo) + " and trc_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado('trc_moc_trilhacapacitacao_modulocapacitacao', condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        return {"message": "Não existe associação com os parâmetros informados."}, 404

    condicao = "WHERE trc_identificador = " + str(id) + " and  moc_identificador = " + str(modulo)
    dados, retorno, header = acessoBanco.exclueDado('trc_moc_trilhacapacitacao_modulocapacitacao', condicao)

    if retorno != 200:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    return [], 200