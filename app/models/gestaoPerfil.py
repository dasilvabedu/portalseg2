# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request
import datetime


def qualificadorNovoLista(grupo):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header

    if grupo not in ("um", "dois", "tres", "quatro"):
        return {"message": "Grupo inválido"}, 404, header

    if request.method == "POST":
        if not request.json:
            return {"message": "Dados de entrada não fornecidos"}, 404, {}

        token, dadosToken = gestaoAutenticacao.expandeToken()

        entrada = request.json
        titulo = entrada.get("titulo")
        descricao = entrada.get("descricao")
        resultadoFinal, retorno = trataQualificadorIncluido(
            grupo, dadosToken["sub"], dadosToken["name"], titulo, descricao
        )
        return resultadoFinal, retorno, header
    elif request.method == "GET":
        resultadoFinal, retorno = listaQualificador(grupo)
        return resultadoFinal, retorno, header

    return {"message": "Método invalido"}, 400, {}


def qualificadorAtual(grupo, id):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    if grupo not in ("um", "dois", "tres", "quatro"):
        return {"message": "Grupo inválido"}, 404, header

    if request.method == "PATCH":
        token, dadosToken = gestaoAutenticacao.expandeToken()

        # atualização de perfil
        if not request.json:
            return {'"message": "Dados de entrada não fornecidos"'}, 404, header

        entrada = request.json
        titulo = entrada.get("titulo")
        descricao = entrada.get("descricao")
        resultadoFinal, retorno = trataQualificadorAlterado(
            grupo, dadosToken["sub"], dadosToken["name"], id, titulo, descricao
        )
        return resultadoFinal, retorno, header

    elif request.method == "DELETE":
        resultadoFinal, retorno = trataQualificadorDeletado(grupo, id)
        return resultadoFinal, retorno, header

    elif request.method == "GET":

        checa, dados, retorno = qualificadorEspecifico(grupo, id)
        if not checa:
            return {"message": "Não foi possível recuperar dados deste perfil"}, 404, header
        return dados, 200, header

    return {"message": "Método invalido"}, 400, header


def listaQualificador(grupo):
    prefixo = "ql" + grupo[0] + "_"
    nome = "qualificadorperfil" + grupo
    tabela = prefixo + nome

    camposDesejados = (
        prefixo
        + "identificador,"
        + prefixo
        + "titulo, "
        + prefixo
        + "descricao, usu_nome,"
        + prefixo
        + "dataatualizacao"
    )
    condicao = "INNER JOIN usu_usuario ON usu_identificador = " + tabela + "." + prefixo + "identificadoratualizacao"
    dados, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    dadosRetorno = []
    dicRetorno = {}
    for i in range(len(dados)):
        mensagem = {}
        mensagem["id"] = dados[i][0]
        mensagem["titulo"] = dados[i][1]
        mensagem["descricao"] = dados[i][2]
        mensagem["atualizador"] = dados[i][3]
        mensagem["data"] = dados[i][4].strftime("%Y-%m-%d %H:%M:%S")
        dadosRetorno.append(mensagem)
    dicRetorno["qualificadores"] = dadosRetorno
    return dicRetorno, 200


def qualificadorEspecifico(grupo, id):
    prefixo = "ql" + grupo[0] + "_"
    nome = "qualificadorperfil" + grupo
    tabela = prefixo + nome

    camposDesejados = (
        prefixo
        + "identificador,"
        + prefixo
        + "titulo, "
        + prefixo
        + "descricao, usu_nome,"
        + prefixo
        + "dataatualizacao"
    )
    condicao = "INNER JOIN usu_usuario ON usu_identificador = " + tabela + "." + prefixo + "identificadoratualizacao"
    condicao = condicao + " WHERE " + prefixo + "identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposDesejados)
    if retorno == 400:
        return False, {"message": "Erro no acesso ao banco de dados"}, retorno, []

    if dados == []:
        return False, {"message": "Não existe informações para o identificador fornecido"}, retorno, []

    for i in range(len(dados)):
        mensagem = {}
        mensagem["id"] = dados[i][0]
        mensagem["titulo"] = dados[i][1]
        mensagem["descricao"] = dados[i][2]
        mensagem["atualizador"] = dados[i][3]
        mensagem["data"] = dados[i][4].strftime("%Y-%m-%d %H:%M:%S")

    return True, mensagem, 200


def trataQualificadorIncluido(grupo, usu_identificador, usu_nome, titulo, descricao):
    cheque = {}
    cheque["message"] = ""
    erro = False

    if titulo is None or type(titulo) is not str or len(titulo) < 1:
        cheque["message"] = "Título é obrigatorio e textual."
        erro = True

    if descricao is None or type(descricao) is not str or len(descricao) < 1:
        if not erro:
            cheque["message"] = "Descrição é obrigatória e textual."
        else:
            cheque["message"] = cheque["message"] + " - Descrição é obrigatória e textual."
        erro = True

    if erro:
        return cheque, 404

    prefixo = "ql" + grupo[0] + "_"
    nome = "qualificadorperfil" + grupo
    tabela = prefixo + nome

    # verifica se titulo e descricao são únicos
    condicao = "WHERE " + prefixo + "titulo = '" + titulo + "' or " + prefixo + "descricao = '" + descricao + "'"
    camposDesejados = prefixo + "identificador"
    dados, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        cheque["message"] = "Título e descrição devem ser únicos na base"
        return cheque, 404

    # recupera o último identificador
    camposDesejados = "max(" + prefixo + "identificador" + ")"
    dados, retorno, mensagemRetorno = acessoBanco.leDado(tabela, None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = (
        prefixo
        + "identificador,"
        + prefixo
        + "titulo,"
        + prefixo
        + "descricao,"
        + prefixo
        + "identificadoratualizacao,"
        + prefixo
        + "dataatualizacao"
    )
    valores = (
        str(proximoNumero) + ",'" + titulo + "','" + descricao + "'," + str(usu_identificador) + ",'" + agora + "'"
    )
    dados, retorno, header = acessoBanco.insereDado(tabela, camposDesejados, valores)
    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem["id"] = proximoNumero
    mensagem["titulo"] = titulo
    mensagem["descricao"] = descricao
    mensagem["atualizador"] = usu_nome
    mensagem["data"] = agora

    return mensagem, 201


def trataQualificadorAlterado(grupo, usu_identificador, usu_nome, identificador, titulo, descricao):
    cheque = {}
    cheque["message"] = ""
    erro = False
    altera = False

    if identificador is None or not acessoBanco.inteiro(identificador):
        cheque["message"] = "Identificador é obrigatório e numérico."
        erro = True

    if titulo is not None:
        if type(titulo) is not str or len(titulo) < 1:
            if not erro:
                cheque["message"] = "Título deve ser textual."
            else:
                cheque["message"] = cheque["message"] + " - Título deve ser textual."
            erro = True
        else:
            altera = True

    if descricao is not None:
        if type(descricao) is not str or len(descricao) < 1:
            if not erro:
                cheque["message"] = "Descrição deve ser textual."
            else:
                cheque["message"] = cheque["message"] + " - Descrição deve ser textual."
            erro = True
        else:
            altera = True

    if erro:
        return cheque, 404

    if not altera:
        return {"messasge": "Nada a ser alterado"}, 404

    prefixo = "ql" + grupo[0] + "_"
    nome = "qualificadorperfil" + grupo
    tabela = prefixo + nome

    # verifica se novo titulo e descricao são únicos
    condicao = "WHERE "
    if titulo is not None:
        condicao = condicao + prefixo + "titulo = '" + titulo + "'"
        if descricao is not None:
            condicao = condicao + " or " + prefixo + "descricao = '" + descricao + "'"
    else:
        condicao = condicao + prefixo + "descricao = '" + descricao + "'"

    camposDesejados = prefixo + "identificador, " + prefixo + "titulo, " + prefixo + "descricao"
    dadosIniciais, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dadosIniciais != [] and dadosIniciais[0][0] != identificador:
        cheque["message"] = "Título e descrição devem ser únicos na base"
        return cheque, 404

    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    valores = ""
    if titulo is not None:
        valores = valores + prefixo + "titulo = '" + titulo + "',"
    if descricao is not None:
        valores = valores + prefixo + "descricao = '" + descricao + "',"
    valores = (
        valores
        + prefixo
        + "identificadoratualizacao = "
        + str(usu_identificador)
        + ", "
        + prefixo
        + "dataatualizacao = '"
        + agora
        + "'"
    )
    condicao = "WHERE " + prefixo + "identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.alteraDado(tabela, valores, condicao)

    if retorno != 200:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem["id"] = identificador
    if titulo is not None:
        mensagem["titulo"] = titulo
    if descricao is not None:
        mensagem["descricao"] = descricao

    mensagem["atualizador"] = usu_nome
    mensagem["data"] = agora

    return mensagem, 200


def trataQualificadorDeletado(grupo, identificador):

    if identificador is None or not acessoBanco.inteiro(identificador):
        return {"message": "Identificador é obrigatório e numérico."}, 404

    prefixo = "ql" + grupo[0] + "_"
    nome = "qualificadorperfil" + grupo
    tabela = prefixo + nome

    condicao = "WHERE " + prefixo + "identificador = " + str(identificador)
    dados, retorno, mensagem = acessoBanco.exclueDado(tabela, condicao)

    if retorno != 200:
        return {"message": mensagem}, retorno

    return {}, 200


def acessoNovoLista():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header

    if request.method == "POST":
        if not request.json:
            return {"message": "Dados de entrada não fornecidos"}, 404, {}

        token, dadosToken = gestaoAutenticacao.expandeToken()

        entrada = request.json
        descricao = entrada.get("descricao")

        resultadoFinal, retorno = trataAcessoIncluido(dadosToken["sub"], dadosToken["name"], descricao)
        return resultadoFinal, retorno, header
    elif request.method == "GET":
        resultadoFinal, retorno = listaAcesso()
        return resultadoFinal, retorno, header

    return {"message": "Método invalido"}, 400, {}


def acessoAtual(id):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    if request.method == "PATCH":
        token, dadosToken = gestaoAutenticacao.expandeToken()

        # atualização de perfil
        if not request.json:
            return {'"message": "Dados de entrada não fornecidos"'}, 404, header

        entrada = request.json
        titulo = entrada.get("titulo")
        descricao = entrada.get("descricao")
        resultadoFinal, retorno = trataAcessoAlterado(dadosToken["sub"], dadosToken["name"], id, descricao)
        return resultadoFinal, retorno, header

    elif request.method == "DELETE":
        resultadoFinal, retorno = trataAcessoDeletado(id)
        return resultadoFinal, retorno, header

    elif request.method == "GET":

        checa, mensagem, dados = acessoEspecifico(id)
        if not checa:
            return {"message": "Não foi possível recuperar dados deste perfil"}, 404, header
        return dados, 200, header

    return {"message": "Método invalido"}, 400, header


def listaAcesso():

    camposDesejados = "pfa_identificador, pfa_descricao, pfa_dataatualizacao, usu_nome"
    condicao = "INNER JOIN usu_usuario ON usu_identificador = pfa_perfilacesso.pfa_identificadoratualizacao"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("pfa_perfilacesso", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno
    dicRetorno = {}
    dadosRetorno = []
    for i in range(len(dados)):
        mensagem = {}
        mensagem["id"] = dados[i][0]
        mensagem["descricao"] = dados[i][1]
        mensagem["atualizador"] = dados[i][3]
        mensagem["data"] = dados[i][2].strftime("%Y-%m-%d %H:%M:%S")
        transacoes = {}

        # recupera as transacoes associadas
        camposDesejados = "trn_codigo, trn_descricao "
        condicao = (
            "INNER JOIN trn_transacaosistema ON  "
            + "trn_transacaosistema.trn_identificador = pfa_trn_perfilacesso_transacaosistema.trn_identificador "
            + "where pfa_identificador =  " + str(dados[i][0])
        )
        dadosTransacao, retorno, mensagemRetorno = acessoBanco.leDado(
            "pfa_trn_perfilacesso_transacaosistema", condicao, camposDesejados
        )
        if retorno == 400:
            return {"message": "Erro no acesso ao banco de dados"}, retorno

        sigla = []
        nome = []
        for i in range(len(dadosTransacao)):
            sigla.append(dadosTransacao[i][0])
            nome.append(dadosTransacao[i][1])
        mensagem["transacoes_codigos"] = sigla
        mensagem["transacoes_nomes"] = nome
        dadosRetorno.append(mensagem)
    dicRetorno["acessos"] = dadosRetorno
    return dicRetorno, 200


def acessoEspecifico(id):

    camposDesejados = "pfa_identificador, pfa_descricao, pfa_dataatualizacao, usu_nome"
    condicao = "INNER JOIN usu_usuario ON usu_identificador = pfa_perfilacesso.pfa_identificadoratualizacao "
    condicao = condicao + "WHERE pfa_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("pfa_perfilacesso", condicao, camposDesejados)
    if retorno == 400:
        return False, {"message": "Erro no acesso ao banco de dados"}, {}

    dadosRetorno = []
    for i in range(len(dados)):
        mensagem = {}
        mensagem["id"] = dados[i][0]
        mensagem["descricao"] = dados[i][1]
        mensagem["atualizador"] = dados[i][3]
        mensagem["data"] = dados[i][2].strftime("%Y-%m-%d %H:%M:%S")
        transacoes = {}

        # recupera as transacoes associadas
        camposDesejados = "trn_codigo, trn_descricao "
        condicao = (
            "INNER JOIN trn_transacaosistema ON  "
            + "trn_transacaosistema.trn_identificador = pfa_trn_perfilacesso_transacaosistema.trn_identificador "
            + "where pfa_identificador =  " + str(dados[i][0])
        )
        dadosTransacao, retorno, mensagemRetorno = acessoBanco.leDado(
            "pfa_trn_perfilacesso_transacaosistema", condicao, camposDesejados
        )
        if retorno == 400:
            return False, {"message": "Erro no acesso ao banco de dados"}, {}
        sigla = []
        nome = []
        for i in range(len(dadosTransacao)):
            sigla.append(dadosTransacao[i][0])
            nome.append(dadosTransacao[i][1])
        mensagem["transacoes_codigos"] = sigla
        mensagem["transacoes_nomes"] = nome

    return True, {}, mensagem


def trataAcessoIncluido(usu_identificador, usu_nome, descricao):
    if descricao is None or type(descricao) is not str or len(descricao) < 1:
        return {"message": "Descrição é obrigatória e textual."}, 404

    # verifica se  descricao é única
    condicao = "WHERE pfa_descricao = '" + descricao + "'"
    camposDesejados = "pfa_identificador"
    condicao = "WHERE pfa_descricao = '" + descricao + "'"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("pfa_perfilacesso", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        return {"message": "Descrição é obrigatória e deve ser única na base."}, 404

    # recupera o último identificador
    camposDesejados = "max(pfa_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("pfa_perfilacesso", None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = "pfa_identificador, pfa_descricao, pfa_identificadoratualizacao,pfa_dataatualizacao"
    valores = str(proximoNumero) + ",'" + descricao + "'," + str(usu_identificador) + ",'" + agora + "'"
    dados, retorno, header = acessoBanco.insereDado("pfa_perfilacesso", camposDesejados, valores)
    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem["id"] = proximoNumero
    mensagem["descricao"] = descricao
    mensagem["atualizador"] = usu_nome
    mensagem["data"] = agora

    return mensagem, 201


def trataAcessoAlterado(usu_identificador, usu_nome, identificador, descricao):

    cheque = {}
    cheque["message"] = ""
    erro = False
    altera = False

    if identificador is None or not acessoBanco.inteiro(identificador):
        cheque["message"] = "Identificador é obrigatório e numérico."
        erro = True

    if descricao is not None:
        if type(descricao) is not str or len(descricao) < 1:
            if not erro:
                cheque["message"] = "Descrição deve ser textual."
            else:
                cheque["message"] = cheque["message"] + " - Descrição deve ser textual."
            erro = True
        else:
            altera = True

    if erro:
        return cheque, 404

    if not altera:
        return {"messasge": "Nada a ser alterado"}, 404

    # verifica se nova descricao é única
    condicao = "WHERE pfa_descricao = '" + descricao + "'"
    camposDesejados = "pfa_identificador, pfa_descricao"
    dadosIniciais, retorno, mensagemRetorno = acessoBanco.leDado("pfa_perfilacesso", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno
    if dadosIniciais != [] and dadosIniciais[0][0] != identificador:
        cheque["message"] = "Descrição deve ser única na base"
        return cheque, 404

    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    valores = (
        "pfa_descricao = '"
        + descricao
        + "', pfa_identificadoratualizacao = "
        + str(usu_identificador)
        + ", pfa_dataatualizacao = '"
        + agora
        + "'"
    )
    condicao = "WHERE pfa_identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.alteraDado("pfa_perfilacesso", valores, condicao)
    if retorno != 200:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem["id"] = identificador
    mensagem["descricao"] = descricao
    mensagem["atualizador"] = usu_nome
    mensagem["data"] = agora

    return mensagem, 200


def trataAcessoDeletado(identificador):

    if identificador is None or not acessoBanco.inteiro(identificador):
        return {"message": "Identificador é obrigatório e numérico."}, 404

    # verifica se este perfil não está associado a usuário ou transacao

    camposDesejados = "usu_identificador"
    condicao = "WHERE pfa_identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.leDado("usu_pfa_usuario_perfilacesso", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400
    if dados != []:
        return {"message": "Perfil associado a usuário não pode ser excluido."}, 404

    camposDesejados = "trn_identificador"
    condicao = "WHERE pfa_identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.leDado("pfa_trn_perfilacesso_transacaosistema", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400
    if dados != []:
        return {"message": "Perfil associado a transação não pode ser excluido."}, 404

    # exclue

    condicao = "WHERE pfa_identificador = " + str(identificador)
    dados, retorno, mensagem = acessoBanco.exclueDado("pfa_perfilacesso", condicao)
    if retorno != 200:
        return {"message": mensagem}, retorno

    return {}, 200


def perfilNovoLista():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header

    if request.method == "POST":
        if not request.json:
            return {"message": "Dados de entrada não fornecidos"}, 404, {}

        token, dadosToken = gestaoAutenticacao.expandeToken()
        entrada = request.json
        sigla = entrada.get("sigla")
        descricao = entrada.get("descricao")
        qual_um = entrada.get("qualificador_um")
        qual_dois = entrada.get("qualificador_dois")
        qual_tres = entrada.get("qualificador_tres")
        qual_quatro = entrada.get("qualificador_quatro")
        resultadoFinal, retorno = trataPerfilIncluido(
            dadosToken["sub"], dadosToken["name"], sigla, descricao, qual_um, qual_dois, qual_tres, qual_quatro
        )
        return resultadoFinal, retorno, header
    elif request.method == "GET":
        resultadoFinal, retorno = listaPerfil()
        return resultadoFinal, retorno, header

    return {"message": "Método invalido"}, 400, {}


def perfilAtual(id):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    if request.method == "PATCH":
        token, dadosToken = gestaoAutenticacao.expandeToken()

        # atualização de perfil
        if not request.json:
            return {'"message": "Dados de entrada não fornecidos"'}, 404, header

        entrada = request.json
        sigla = entrada.get("sigla")
        descricao = entrada.get("descricao")
        qual_um = entrada.get("qualificador_um")
        qual_dois = entrada.get("qualificador_dois")
        qual_tres = entrada.get("qualificador_tres")
        qual_quatro = entrada.get("qualificador_quatro")
        resultadoFinal, retorno = trataPerfilAlterado(
            id, dadosToken["sub"], dadosToken["name"], sigla, descricao, qual_um, qual_dois, qual_tres, qual_quatro
        )
        return resultadoFinal, retorno, header

    elif request.method == "DELETE":
        resultadoFinal, retorno = trataPerfilDeletado(id)
        return resultadoFinal, retorno, header

    elif request.method == "GET":

        checa, mensagem, dados = perfilEspecifico(id)
        if not checa:
            return {"message": "Não foi possível recuperar dados deste perfil"}, 404, header
        return dados, 200, header

    return {"message": "Método invalido"}, 400, header


def listaPerfil():
    camposDesejados = (
        "pfu_identificador, pfu_sigla, pfu_descricao, qlu_identificador, qld_identificador, qlt_identificador,"
    )
    camposDesejados = camposDesejados + " qlq_identificador, pfu_dataatualizacao,usu_nome"
    condicao = "INNER JOIN usu_usuario ON usu_identificador = pfu_perfilusuario.pfu_identificadoratualizacao"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("pfu_perfilusuario", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    dadosRetorno = []

    for i in range(len(dados)):
        mensagem = {}
        mensagem["id"] = dados[i][0]
        mensagem["sigla"] = dados[i][1]
        mensagem["descricao"] = dados[i][2]
        mensagem["qualificador_um_codigo"] = dados[i][3]
        mensagem["qualificador_dois_codigo"] = dados[i][4]
        mensagem["qualificador_tres_codigo"] = dados[i][5]
        mensagem["qualificador_quatro_codigo"] = dados[i][6]
        mensagem["atualizador"] = dados[i][8]
        mensagem["data"] = dados[i][7].strftime("%Y-%m-%d %H:%M:%S")

        for grupo in ("um", "dois", "tres", "quatro"):
            prefixo = "ql" + grupo[0] + "_"
            nome = "qualificadorperfil" + grupo
            tabela = prefixo + nome
            valor = mensagem["qualificador_" + grupo + "_codigo"]
            camposDesejados = prefixo + "titulo, " + prefixo + "descricao"
            condicao = "WHERE " + prefixo + "identificador = " + str(valor)
            dadosQual, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposDesejados)
            if retorno == 400:
                return {"message": "Erro no acesso ao banco de dados"}, retorno
            mensagem["qualificador_" + grupo + "_titulo"] = dadosQual[0][0]
            mensagem["qualificador_" + grupo + "_descricao"] = dadosQual[0][1]
        dadosRetorno.append(mensagem)
    dicRetorno = {}
    dicRetorno["perfis"] = dadosRetorno
    return dicRetorno, 200


def perfilEspecifico(id):
    camposDesejados = (
        "pfu_identificador, pfu_sigla, pfu_descricao, qlu_identificador, qld_identificador, qlt_identificador,"
    )
    camposDesejados = camposDesejados + " qlq_identificador, pfu_dataatualizacao,usu_nome"
    condicao = "INNER JOIN usu_usuario ON usu_identificador = pfu_perfilusuario.pfu_identificadoratualizacao "
    condicao = condicao + "WHERE pfu_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("pfu_perfilusuario", condicao, camposDesejados)
    if retorno == 400:
        return False, {"message": "Erro no acesso ao banco de dados"}, {}
    if retorno != 200:
        return False, {"message": "Não foi possivel recuperar os dados para este perfil"}, {}

    for i in range(len(dados)):

        mensagem = {}
        mensagem["id"] = dados[i][0]
        mensagem["sigla"] = dados[i][1]
        mensagem["descricao"] = dados[i][2]
        mensagem["qualificador_um_codigo"] = dados[i][3]
        mensagem["qualificador_dois_codigo"] = dados[i][4]
        mensagem["qualificador_tres_codigo"] = dados[i][5]
        mensagem["qualificador_quatro_codigo"] = dados[i][6]
        mensagem["atualizador"] = dados[i][8]
        mensagem["data"] = dados[i][7].strftime("%Y-%m-%d %H:%M:%S")

        for grupo in ("um", "dois", "tres", "quatro"):
            prefixo = "ql" + grupo[0] + "_"
            nome = "qualificadorperfil" + grupo
            tabela = prefixo + nome
            valor = mensagem["qualificador_" + grupo + "_codigo"]
            camposDesejados = prefixo + "titulo, " + prefixo + "descricao"
            condicao = "WHERE " + prefixo + "identificador = " + str(valor)
            dadosQual, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposDesejados)
            if retorno == 400:
                return {"message": "Erro no acesso ao banco de dados"}, retorno
            mensagem["qualificador_" + grupo + "_titulo"] = dadosQual[0][0]
            mensagem["qualificador_" + grupo + "_descricao"] = dadosQual[0][1]

    return True, {}, mensagem


def trataPerfilIncluido(usu_identificador, usu_nome, sigla, descricao, qual_um, qual_dois, qual_tres, qual_quatro):
    cheque = {}
    cheque["message"] = ""
    erro = False

    if sigla is None or type(sigla) is not str or len(sigla) < 1:
        cheque["message"] = "Sigla é obrigatoria e textual."
        erro = True

    if descricao is None or type(descricao) is not str or len(descricao) < 1:
        if not erro:
            cheque["message"] = "Descrição é obrigatória e textual."
        else:
            cheque["message"] = cheque["message"] + " - Descrição é obrigatória e textual."
        erro = True

    if qual_um is None or not acessoBanco.inteiro(qual_um):
        if not erro:
            cheque["message"] = "Qualificador Um é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Qualificador Um é obrigatório e numérico."
        erro = True

    if qual_dois is None or not acessoBanco.inteiro(qual_dois):
        if not erro:
            cheque["message"] = "Qualificador Dois é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Qualificador Dois é obrigatório e numérico."
        erro = True

    if qual_tres is None or not acessoBanco.inteiro(qual_tres):
        if not erro:
            cheque["message"] = "Qualificador Três é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Qualificador Três é obrigatório e numérico."
        erro = True

    if qual_quatro is None or not acessoBanco.inteiro(qual_quatro):
        if not erro:
            cheque["message"] = "Qualificador Quatro é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Qualificador Quatro é obrigatório e numérico."
        erro = True

    if erro:
        return cheque, 404

    # verifica se  qualificadores existem
    condicao = "WHERE qlu_identificador = " + str(qual_um)
    camposDesejados = "qlu_identificador"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("qlu_qualificadorperfilum", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        return {"message": "Qualificador Um não existe na base de dados."}, 404

    condicao = "WHERE qld_identificador = " + str(qual_dois)
    camposDesejados = "qld_identificador"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("qld_qualificadorperfildois", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        return {"message": "Qualificador Dois não existe na base de dados."}, 404

    condicao = "WHERE qlt_identificador = " + str(qual_tres)
    camposDesejados = "qlt_identificador"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("qlt_qualificadorperfiltres", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        return {"message": "Qualificador Três não existe na base de dados."}, 404

    condicao = "WHERE qlq_identificador = " + str(qual_quatro)
    camposDesejados = "qlq_identificador"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("qlq_qualificadorperfilquatro", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        return {"message": "Qualificador Quatro não existe na base de dados."}, 404

    # verifica se  os parãmetros informados são únicos
    camposDesejados = "pfu_identificador"
    condicao = "WHERE pfu_descricao = '" + descricao + "' or pfu_sigla = '" + sigla + "' or "
    condicao = condicao + "(qlu_identificador = " + str(qual_um) + " and qld_identificador = " + str(qual_dois)
    condicao = (
        condicao + " and qlt_identificador = " + str(qual_tres) + " and qlq_identificador = " + str(qual_quatro) + ")"
    )
    dados, retorno, mensagemRetorno = acessoBanco.leDado("pfu_perfilusuario", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        return {"message": "Já existe Perfil de Usuário com um ou mais parâmetros fornecidos."}, 404

    # recupera o último identificador
    camposDesejados = "max(pfu_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("pfu_perfilusuario", None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = (
        "pfu_identificador, pfu_sigla, pfu_descricao, qlu_identificador, qld_identificador, qlt_identificador, "
        + "qlq_identificador, pfu_identificadoratualizacao, pfu_dataatualizacao"
    )
    valores = (
        str(proximoNumero)
        + ",'"
        + sigla
        + "','"
        + descricao
        + "',"
        + str(qual_um)
        + ","
        + str(qual_dois)
        + ","
        + str(qual_tres)
        + ","
        + str(qual_quatro)
        + ","
        + str(usu_identificador)
        + ",'"
        + agora
        + "'"
    )
    dados, retorno, header = acessoBanco.insereDado("pfu_perfilusuario", camposDesejados, valores)

    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem["id"] = proximoNumero
    mensagem["sigla"] = sigla
    mensagem["descricao"] = descricao
    mensagem["qualificador_um_codigo"] = qual_um
    mensagem["qualificador_dois_codigo"] = qual_dois
    mensagem["qualificador_tres_codigo"] = qual_tres
    mensagem["qualificador_quatro_codigo"] = qual_quatro
    mensagem["atualizador"] = usu_nome
    mensagem["data"] = agora

    return mensagem, 201


def trataPerfilAlterado(id, usu_identificador, usu_nome, sigla, descricao, qual_um, qual_dois, qual_tres, qual_quatro):
    cheque = {}
    cheque["message"] = ""
    erro = False
    altera = False

    if sigla is not None:
        if type(sigla) is not str or len(sigla) < 1:
            cheque["message"] = "Sigla é obrigatoria e textual."
            erro = True
        else:
            altera = True

    if descricao is not None:
        if type(descricao) is not str or len(descricao) < 1:
            if not erro:
                cheque["message"] = "Descrição é obrigatória e textual."
            else:
                cheque["message"] = cheque["message"] + " - Descrição é obrigatória e textual."
            erro = True
        else:
            altera = True

    if qual_um is not None:
        if not acessoBanco.inteiro(qual_um):
            if not erro:
                cheque["message"] = "Qualificador Um é obrigatório e numérico."
            else:
                cheque["message"] = cheque["message"] + " - Qualificador Um é obrigatório e numérico."
            erro = True
        else:
            altera = True

    if qual_dois is not None:
        if not acessoBanco.inteiro(qual_dois):
            if not erro:
                cheque["message"] = "Qualificador Dois é obrigatório e numérico."
            else:
                cheque["message"] = cheque["message"] + " - Qualificador Dois é obrigatório e numérico."
            erro = True
        else:
            altera = True

    if qual_tres is not None:
        if not acessoBanco.inteiro(qual_tres):
            if not erro:
                cheque["message"] = "Qualificador Três é obrigatório e numérico."
            else:
                cheque["message"] = cheque["message"] + " - Qualificador Três é obrigatório e numérico."
            erro = True
        else:
            altera = True

    if qual_quatro is not None:
        if not acessoBanco.inteiro(qual_quatro):
            if not erro:
                cheque["message"] = "Qualificador Quatro é obrigatório e numérico."
            else:
                cheque["message"] = cheque["message"] + " - Qualificador Quatro é obrigatório e numérico."
            erro = True
        else:
            altera = True

    if erro:
        return cheque, 404

    if not altera:
        return {"message": "Nada a ser alterado"}, 404

    # verifica se  existe o registro informado
    condicao = "WHERE pfu_identificador = " + str(id)
    camposDesejados = (
        "pfu_sigla, pfu_descricao, qlu_identificador, qld_identificador, qlt_identificador, qlq_identificador"
    )
    dadosAtual, retorno, mensagemRetorno = acessoBanco.leDado("pfu_perfilusuario", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dadosAtual == []:
        return {"message": "Não existe perfil com o identificador informado"}, 404

    if sigla is None:
        sigla = dadosAtual[0][0]

    if descricao is None:
        descricao = dadosAtual[0][1]

    if qual_um is None:
        qual_um = dadosAtual[0][2]
    else:
        condicao = "WHERE qlu_identificador = " + str(qual_um)
        camposDesejados = "qlu_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.leDado("qlu_qualificadorperfilum", condicao, camposDesejados)
        if retorno == 400:
            return {"message": "Erro no acesso ao banco de dados"}, retorno

        if dados == []:
            return {"message": "Qualificador Um não existe na base de dados."}, 404

    if qual_dois is None:
        qual_dois = dadosAtual[0][3]
    else:
        condicao = "WHERE qld_identificador = " + str(qual_dois)
        camposDesejados = "qld_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.leDado("qld_qualificadorperfildois", condicao, camposDesejados)
        if retorno == 400:
            return {"message": "Erro no acesso ao banco de dados"}, retorno

        if dados == []:
            return {"message": "Qualificador Dois não existe na base de dados."}, 404

    if qual_tres is None:
        qual_tres = dadosAtual[0][4]
    else:
        condicao = "WHERE qlt_identificador = " + str(qual_tres)
        camposDesejados = "qlt_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.leDado("qlt_qualificadorperfiltres", condicao, camposDesejados)
        if retorno == 400:
            return {"message": "Erro no acesso ao banco de dados"}, retorno

        if dados == []:
            return {"message": "Qualificador Três não existe na base de dados."}, 404

    if qual_quatro is None:
        qual_quatro = dadosAtual[0][5]
    else:
        condicao = "WHERE qlq_identificador = " + str(qual_quatro)
        camposDesejados = "qlq_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.leDado("qlq_qualificadorperfilquatro", condicao, camposDesejados)
        if retorno == 400:
            return {"message": "Erro no acesso ao banco de dados"}, retorno

        if dados == []:
            return {"message": "Qualificador Quatro não existe na base de dados."}, 404

    # verifica se  os parãmetros informados são únicos
    camposDesejados = "pfu_identificador"
    condicao = "WHERE pfu_descricao = '" + descricao + "' or pfu_sigla = '" + sigla + "' or "
    condicao = condicao + "(qlu_identificador = " + str(qual_um) + " and qld_identificador = " + str(qual_dois)
    condicao = (
        condicao + " and qlt_identificador = " + str(qual_tres) + " and qlq_identificador = " + str(qual_quatro) + ")"
    )
    dados, retorno, mensagemRetorno = acessoBanco.leDado("pfu_perfilusuario", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        if dados[0][0] != id:
            return {"message": "Já existe Perfil de Usuário com um ou mais parâmetros fornecidos."}, 404

    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    condicao = "WHERE pfu_identificador = " + str(id)
    valores = (
        "pfu_sigla = '" + sigla + "', pfu_descricao = '" + descricao + "', qlu_identificador = " + str(qual_um) + ","
    )
    valores = (
        valores
        + "qld_identificador = "
        + str(qual_dois)
        + ", qlt_identificador = "
        + str(qual_tres)
        + ", qlq_identificador = "
        + str(qual_quatro)
        + ","
    )
    valores = (
        valores
        + "pfu_identificadoratualizacao = "
        + str(usu_identificador)
        + ", pfu_dataatualizacao = '"
        + agora
        + "'"
    )
    dados, retorno, header = acessoBanco.alteraDado("pfu_perfilusuario", valores, condicao)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem["id"] = id
    mensagem["sigla"] = sigla
    mensagem["descricao"] = descricao
    mensagem["qualificador_um_codigo"] = qual_um
    mensagem["qualificador_dois_codigo"] = qual_dois
    mensagem["qualificador_tres_codigo"] = qual_tres
    mensagem["qualificador_quatro_codigo"] = qual_quatro
    mensagem["atualizador"] = usu_nome
    mensagem["data"] = agora

    return mensagem, 200


def trataPerfilDeletado(identificador):

    if identificador is None or not acessoBanco.inteiro(identificador):
        return {"message": "Identificador é obrigatório e numérico."}, 404

    # verifica se este perfil não existe

    camposDesejados = "pfu_identificador"
    condicao = "WHERE pfu_identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.leDado("pfu_perfilusuario", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400
    if dados == []:
        return {"message": "Não existe perfil com o identificador fornecido."}, 404

    # verifica se este perfil não está associado a usuário ou trilha de capacitacao

    camposDesejados = "usu_identificador"
    condicao = "WHERE pfu_identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.leDado("usu_pfu_usuario_perfilusuario", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400
    if dados != []:
        return {"message": "Perfil associado a usuário não pode ser excluido."}, 404

    camposDesejados = "trc_identificador"
    condicao = "WHERE pfu_identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.leDado("trc_trilhacapacitacao", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400
    if dados != []:
        return {"message": "Perfil associado a trilha de capacitação não pode ser excluido."}, 404

    # exclue

    condicao = "WHERE pfu_identificador = " + str(identificador)
    dados, retorno, mensagem = acessoBanco.exclueDado("pfu_perfilusuario", condicao)

    if retorno != 200:
        return {"message": mensagem}, retorno

    return {}, 200


def transacaoNovoLista():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header

    if request.method == "POST":
        if not request.json:
            return {"message": "Dados de entrada não fornecidos"}, 404, {}

        token, dadosToken = gestaoAutenticacao.expandeToken()
        entrada = request.json
        codigo = entrada.get("codigo")
        descricao = entrada.get("descricao")
        resultadoFinal, retorno = trataTransacaoIncluida(dadosToken["sub"], dadosToken["name"], codigo, descricao)
        return resultadoFinal, retorno, header
    elif request.method == "GET":
        resultadoFinal, retorno = listaTransacao()
        return resultadoFinal, retorno, header

    return {"message": "Método invalido"}, 400, {}


def transacaoAtual(id):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    if request.method == "PATCH":
        token, dadosToken = gestaoAutenticacao.expandeToken()

        # atualização de perfil
        if not request.json:
            return {'"message": "Dados de entrada não fornecidos"'}, 404, header

        entrada = request.json
        codigo = entrada.get("codigo")
        descricao = entrada.get("descricao")
        resultadoFinal, retorno = trataTransacaoAlterada(id, dadosToken["sub"], dadosToken["name"], codigo, descricao)
        return resultadoFinal, retorno, header

    elif request.method == "DELETE":
        resultadoFinal, retorno = trataTransacaoDeletada(id)
        return resultadoFinal, retorno, header

    elif request.method == "GET":

        checa, mensagem, dados = transacaoEspecifica(id)
        if not checa:
            return {"message": "Não foi possível recuperar dados desta transação"}, 404, header
        return dados, 200, header

    return {"message": "Método invalido"}, 400, header


def listaTransacao():
    camposDesejados = (
        "trn_identificador, trn_descricao, trn_codigo, trn_identificadoratualizacao, trn_dataatualizacao,usu_nome"
    )
    condicao = "INNER JOIN usu_usuario ON usu_identificador = trn_transacaosistema.trn_identificadoratualizacao"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("trn_transacaosistema", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    dadosRetorno = []

    for i in range(len(dados)):

        mensagem = {}
        mensagem["id"] = dados[i][0]
        mensagem["descricao"] = dados[i][1]
        mensagem["codigo"] = dados[i][2]
        mensagem["atualizador"] = dados[i][5]
        mensagem["data"] = dados[i][4].strftime("%Y-%m-%d %H:%M:%S")

        dadosRetorno.append(mensagem)
    dicRetorno = {}
    dicRetorno["transacoes"] = dadosRetorno
    return dicRetorno, 200


def transacaoEspecifica(id):
    camposDesejados = (
        "trn_identificador, trn_descricao, trn_codigo, trn_identificadoratualizacao, trn_dataatualizacao,usu_nome"
    )
    condicao = "INNER JOIN usu_usuario ON usu_identificador = trn_transacaosistema.trn_identificadoratualizacao "
    condicao = condicao + "WHERE trn_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("trn_transacaosistema", condicao, camposDesejados)
    if retorno == 400:
        return False, {"message": "Erro no acesso ao banco de dados"}, {}
    if retorno != 200:
        return False, {"message": "Não foi possivel recuperar os dados para este perfil"}, {}

    for i in range(len(dados)):
        mensagem = {}
        mensagem["id"] = dados[i][0]
        mensagem["descricao"] = dados[i][1]
        mensagem["codigo"] = dados[i][2]
        mensagem["atualizador"] = dados[i][5]
        mensagem["data"] = dados[i][4].strftime("%Y-%m-%d %H:%M:%S")

    return True, {}, mensagem


def trataTransacaoIncluida(usu_identificador, usu_nome, codigo, descricao):
    cheque = {}
    cheque["message"] = ""
    erro = False

    if codigo is None or type(codigo) is not str or len(codigo) < 1:
        cheque["message"] = "Código é obrigatorio e textual."
        erro = True

    if descricao is None or type(descricao) is not str or len(descricao) < 1:
        if not erro:
            cheque["message"] = "Descrição é obrigatória e textual."
        else:
            cheque["message"] = cheque["message"] + " - Descrição é obrigatória e textual."
        erro = True

    if erro:
        return cheque, 404

    # verifica se  os parãmetros informados são únicos
    camposDesejados = "trn_identificador"
    condicao = "WHERE trn_descricao = '" + descricao + "' or trn_codigo = '" + codigo + "'"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("trn_transacaosistema", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        return {"message": "Já existe Transação de Sistema com um ou mais parâmetros fornecidos."}, 404

    # recupera o último identificador
    camposDesejados = "max(trn_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("trn_transacaosistema", None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = "trn_identificador, trn_codigo, trn_descricao, trn_identificadoratualizacao, trn_dataatualizacao"
    valores = (
        str(proximoNumero) + ",'" + codigo + "','" + descricao + "'," + str(usu_identificador) + ",'" + agora + "'"
    )
    dados, retorno, header = acessoBanco.insereDado("trn_transacaosistema", camposDesejados, valores)

    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem["id"] = proximoNumero
    mensagem["codigo"] = codigo
    mensagem["descricao"] = descricao
    mensagem["atualizador"] = usu_nome
    mensagem["data"] = agora

    return mensagem, 201


def trataTransacaoAlterada(id, usu_identificador, usu_nome, codigo, descricao):
    cheque = {}
    cheque["message"] = ""
    erro = False
    altera = False

    if codigo is not None:
        if type(codigo) is not str or len(codigo) < 1:
            cheque["message"] = "Código é obrigatório e textual."
            erro = True
        else:
            altera = True

    if descricao is not None:
        if type(descricao) is not str or len(descricao) < 1:
            if not erro:
                cheque["message"] = "Descrição é obrigatória e textual."
            else:
                cheque["message"] = cheque["message"] + " - Descrição é obrigatória e textual."
            erro = True
        else:
            altera = True

    if erro:
        return cheque, 404

    if not altera:
        return {"message": "Nada a ser alterado"}, 404

    # verifica se  existe o registro informado
    condicao = "WHERE trn_identificador = " + str(id)
    camposDesejados = "trn_identificador, trn_descricao, trn_codigo, trn_identificadoratualizacao, trn_dataatualizacao"
    dadosAtual, retorno, mensagemRetorno = acessoBanco.leDado("trn_transacaosistema", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dadosAtual == []:
        return {"message": "Não existe transação com o identificador informado"}, 404

    if codigo is None:
        codigo = dadosAtual[0][2]

    if descricao is None:
        descricao = dadosAtual[0][1]

    # verifica se  os parãmetros informados são únicos
    camposDesejados = "trn_identificador"
    condicao = "WHERE trn_descricao = '" + descricao + "' or trn_codigo = '" + codigo + "'"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("trn_transacaosistema", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        if dados[0][0] != id:
            return {"message": "Já existe Transação de Sistema com um ou mais parâmetros fornecidos."}, 404

    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    condicao = "WHERE trn_identificador = " + str(id)
    valores = (
        "trn_codigo = '"
        + codigo
        + "', trn_descricao = '"
        + descricao
        + "', trn_identificadoratualizacao = "
        + str(usu_identificador)
        + ", trn_dataatualizacao = '"
        + agora
        + "'"
    )
    dados, retorno, header = acessoBanco.alteraDado("trn_transacaosistema", valores, condicao)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem["id"] = id
    mensagem["codigo"] = codigo
    mensagem["descricao"] = descricao
    mensagem["atualizador"] = usu_nome
    mensagem["data"] = agora

    return mensagem, 200


def trataTransacaoDeletada(identificador):

    if identificador is None or not acessoBanco.inteiro(identificador):
        return {"message": "Identificador é obrigatório e numérico."}, 404

    # verifica se esta transacao  existe

    camposDesejados = "trn_identificador"
    condicao = "WHERE trn_identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.leDado("trn_transacaosistema", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400
    if dados == []:
        return {"message": "Não existe transação com o identificador fornecido."}, 404

    # verifica se esta transacao não está associada a perfil de acesso

    camposDesejados = "pfa_identificador"
    condicao = "WHERE trn_identificador = " + str(identificador)
    dados, retorno, header = acessoBanco.leDado("pfa_trn_perfilacesso_transacaosistema", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400
    if dados != []:
        return {"message": "Transação associada a Perfil de Acesso não pode ser excluída."}, 404

    # exclue

    condicao = "WHERE trn_identificador = " + str(identificador)
    dados, retorno, mensagem = acessoBanco.exclueDado("trn_transacaosistema", condicao)
    if retorno != 200:
        return {"message": mensagem}, retorno

    return {}, 200


def acessoQualifica(id):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    if not request.json:
        return {'"message": "Dados de entrada não fornecidos"'}, 404, header

    entrada = request.json
    transacao = entrada.get("transacao")

    if request.method == "POST":
        token, dadosToken = gestaoAutenticacao.expandeToken()
        resultadoFinal, retorno = trataAcessoQualificaIncluido(id, dadosToken["sub"], dadosToken["name"], transacao)
        return resultadoFinal, retorno, header

    elif request.method == "DELETE":
        resultadoFinal, retorno = trataAcessoQualificaDeletado(id, transacao)
        return resultadoFinal, retorno, header

    return {"message": "Método invalido"}, 400, header


def trataAcessoQualificaIncluido(id, usu_identificador, usu_nome, transacao):
    cheque = {}

    if transacao is None or not acessoBanco.inteiro(transacao):
        cheque["message"] = "Identificador de Transação é obrigatório e numérico."
        return cheque, 404

    # verifica se  os parâmetros informados existem
    camposDesejados = "pfa_identificador"
    condicao = "WHERE pfa_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("pfa_perfilacesso", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        return {"message": "Não existe Perfil de Acesso com identificador fornecido"}, 404

    # verifica se  transacao existe
    camposDesejados = "trn_identificador"
    condicao = "WHERE trn_identificador = " + str(transacao)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("trn_transacaosistema", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        return {"message": "Não existe Transação com identificador informado."}, 404

    # verifica se  os dados para inclusão já existem na base
    camposDesejados = "pfa_identificador"
    condicao = "WHERE trn_identificador = " + str(transacao) + " and pfa_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado(
        "pfa_trn_perfilacesso_transacaosistema", condicao, camposDesejados
    )
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados != []:
        return {"message": "Já existe associação com os parâmetros informados."}, 404

    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = "pfa_identificador, trn_identificador, pfa_trn_identificadoratualizacao, pfa_trn_dataatualizacao"
    valores = str(id) + "," + str(transacao) + "," + str(usu_identificador) + ",'" + agora + "'"
    dados, retorno, header = acessoBanco.insereDado("pfa_trn_perfilacesso_transacaosistema", camposDesejados, valores)
    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}

    mensagem["perfil"] = id
    mensagem["transacao"] = transacao
    mensagem["atualizador"] = usu_nome
    mensagem["data"] = agora

    return mensagem, 201


def trataAcessoQualificaDeletado(id, transacao):
    cheque = {}
    cheque["message"] = ""

    if transacao is None or not acessoBanco.inteiro(transacao):
        cheque["message"] = "Identificador da Transação é obrigatório e numérico."
        return cheque, 404

    # verifica se  os parãmetros informados existem
    camposDesejados = "trn_identificador"
    condicao = "WHERE trn_identificador = " + str(transacao) + " and pfa_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado(
        "pfa_trn_perfilacesso_transacaosistema", condicao, camposDesejados
    )
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        return {"message": "Não existe associação com os parâmetros informados."}, 404

    condicao = "WHERE pfa_identificador = " + str(id) + " and  trn_identificador = " + str(transacao)
    dados, retorno, header = acessoBanco.exclueDado("pfa_trn_perfilacesso_transacaosistema", condicao)
    if retorno != 200:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    return [], 200
