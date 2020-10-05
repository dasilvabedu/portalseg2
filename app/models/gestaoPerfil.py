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

def qualificadorUsuarioNovoListaDeleta():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header
    token, dadosToken = gestaoAutenticacao.expandeToken()

    if request.method == "POST":
        if not request.json:
            return {"message": "Dados de entrada não fornecidos"}, 404,  header

        token, dadosToken = gestaoAutenticacao.expandeToken()

        entrada = request.json
        grupo = entrada.get("grupo")
        listaIndice = (
            "empregado", "agente_interno",
            "agente_externo", "morador_zas",
            "frequentador_zas", "morador_zss",
            "frequentador_zss", "outro_interesse"
        )
        if grupo is None or type(grupo) is not str or grupo not in listaIndice:
            return {"message": "Grupo é obrigatório"}, 404,  header

        if grupo == listaIndice[0]:
            resultadoFinal, retorno = trataEmpregado(entrada, dadosToken["sub"])
        elif grupo == listaIndice[1]:
            resultadoFinal, retorno = trataAgenteInterno(entrada, dadosToken["sub"])
        elif grupo == listaIndice[2]:
            resultadoFinal, retorno = trataAgenteExterno(entrada, dadosToken["sub"])
        elif grupo == listaIndice[3]:
            resultadoFinal, retorno = trataMoradorZAS(entrada, dadosToken["sub"])
        elif grupo == listaIndice[4]:
            resultadoFinal, retorno = trataFrequentadorZAS(entrada, dadosToken["sub"])
        elif grupo == listaIndice[5]:
            resultadoFinal, retorno = trataMoradorZSS(entrada, dadosToken["sub"])
        elif grupo == listaIndice[6]:
            resultadoFinal, retorno = trataFrequentadorZSS(entrada, dadosToken["sub"])
        elif grupo == listaIndice[7]:
            resultadoFinal, retorno = trataOutroInteresse(entrada, dadosToken["sub"])

        return resultadoFinal, retorno, header

    elif request.method == "GET":
        retorno, resultadoFinal = dicionarioPerfil(dadosToken["sub"])
        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header

        retorno, resultadoFinal1 = dicionarioDemaisPerfis(dadosToken["sub"])
        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header
        result = {}
        result.update(resultadoFinal)
        result.update(resultadoFinal1)
        return result, 200, header

    elif request.method == "DELETE":
        if not request.json:
            return {"message": "Dados de entrada não fornecidos"}, 404,  header

        token, dadosToken = gestaoAutenticacao.expandeToken()

        entrada = request.json
        grupo = entrada.get("grupo")
        identificador = entrada.get("identificador")
        listaIndice = (
            "empregado", "agente_interno",
            "agente_externo", "morador_zas",
            "frequentador_zas", "morador_zss",
            "frequentador_zss", "outro_interesse"
        )
        listaTabela = (
            "use_usuarioempregado tb", "uai_usuarioagenteinterno tb",
            "uae_usuarioagenteexterno tb", "uma_usuariomoradorzas tb",
            "ufa_usuariofrequentadorzas tb", "ums_usuariomoradorzss tb",
            "ufs_usuariofrequentadorzss tb", "uou_usuariooutrointeresse tb"
        )

        if grupo is None or type(grupo) is not str or grupo not in listaIndice:
            return {"message": "Grupo é obrigatório"}, 404,  header

        if identificador is None or not acessoBanco.inteiro(identificador):
            return {"message": "Grupo é obrigatório"}, 404,  header

        for i in range(len(listaIndice)):
            if grupo == listaIndice[i]:
                condicao = (" WHERE usu_identificador = " + str(dadosToken["sub"]) +
                        " AND " + listaTabela[i][0:3] + "_identificador = " + str(identificador)
                        )
                resultadoFinal, retorno,mensagem = acessoBanco.exclueDado(listaTabela[i], condicao)
                break
        if retorno != 200:
            return mensagem, retorno, header
        else:
            return resultadoFinal, retorno, header

    return {"message": "Método invalido"}, 400, {}

def qualificadorUsuarioUnico(grupo):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header
    token, dadosToken = gestaoAutenticacao.expandeToken()

    listaIndice = (
        "empregado", "agente_interno",
        "agente_externo", "morador_zas",
        "frequentador_zas", "morador_zss",
        "frequentador_zss", "outro_interesse",
        "escolaridade", "entendimento",
        "necessidade"
    )

    if grupo not in listaIndice:
        return {"message": "Grupo inválido"}, 404,  header

    if grupo in ("escolaridade", "entendimento", "necessidade"):
        retorno, resultadoFinal = dicionarioPerfil(dadosToken["sub"],grupo)
    else:
        retorno, resultadoFinal = dicionarioDemaisPerfis(dadosToken["sub"],grupo)


    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    return resultadoFinal, retorno, header



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

def dicionarioPerfil(usuario,grupo=None):
    resultadoFinal = {}
    listaNumero = ("dois", "tres", "quatro")
    listaIndice = ("entendimento", "escolaridade", "necessidade")
    for i in range(len(listaNumero)):
        if grupo is None or grupo == listaIndice[i]:
            prefixo = listaNumero[i][0]
            tabela1 = "uq" + prefixo + "_usuarioqualificadorperfil" + listaNumero[i] + " uq"
            tabela2 = "ql" + prefixo + "_qualificadorperfil" + listaNumero[i] + " ql"
            tabela = tabela1 + "," + tabela2
            camposDesejados = (
                    "ql.ql" + prefixo + "_identificador, "
                    "ql" + prefixo + "_titulo, "
                    "ql" + prefixo + "_descricao "
            )
            condicao = (
                    "  WHERE usu_identificador = " + str(usuario) +
                    " AND uq.ql" + prefixo + "_identificador = " +
                    "ql.ql" + prefixo + "_identificador"
            )
            dadosDetalhe, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposDesejados)
            if retorno == 400:
                return 400, {"message": "Erro de acesso ao banco"}
            listaDetalhe = []
            for j in range(len(dadosDetalhe)):
                detalhe = {}
                detalhe["identificador"] = dadosDetalhe[j][0]
                detalhe["titulo"] = dadosDetalhe[j][1]
                detalhe["descricao"] = dadosDetalhe[j][2]
                listaDetalhe.append(detalhe)
            resultadoFinal[listaIndice[i]] = listaDetalhe
    return 200, resultadoFinal

def dicionarioDemaisPerfis(usuario,grupo=None):
    resultadoFinal = {}
    listaTabela = (
        "use_usuarioempregado tb", "uai_usuarioagenteinterno tb, emp_empreendimento fk",
        "uae_usuarioagenteexterno tb, emp_empreendimento fk, age_agenteexterno ou",
        "uma_usuariomoradorzas tb, emp_empreendimento fk",
        "ufa_usuariofrequentadorzas tb, emp_empreendimento fk", "ums_usuariomoradorzss tb, emp_empreendimento fk",
        "ufs_usuariofrequentadorzss tb, emp_empreendimento fk", "uou_usuariooutrointeresse tb, emp_empreendimento fk"
    )
    listaIndice = (
        "empregado", "agente_interno",
        "agente_externo", "morador_zas",
        "frequentador_zas", "morador_zss",
        "frequentador_zss", "outro_interesse"
    )
    camposEmpregado = (
        "use_identificador", "use_area", "use_funcao"
    )
    camposAgenteInterno = (
        "uai_identificador", "uai_papel",
        "uai_complemento", "fk.emp_nome"
    )
    camposAgenteExterno = (
        "uae_identificador", "uae_papel", "uae_complemento",
        "fk.emp_nome", "ou.age_identificacao"
    )
    camposMoradorZAS = (
        "uma_identificador", "uma_cep", "uma_logradouro",
        "uma_numero", "uma_complemento", 'uma_bairro', "uma_municipio",
        "fk.emp_nome"
    )
    camposFrequentadorZAS = (
        "ufa_identificador", "ufa_local", "fk.emp_nome"
    )
    camposMoradorZSS = (
        "ums_identificador", "ums_cep", "ums_logradouro", "ums_numero",
        "ums_complemento", "ums_bairro", "ums_municipio", "fk.emp_nome"
    )
    camposFrequentadorZSS = (
        "ufs_identificador", "ufs_local", "fk.emp_nome"
    )
    camposOutroInteresse = (
        "uou_identificador", "uou_complemento", "fk.emp_nome"
    )
    condicaoEmpregado = (
        ""
    )
    condicaoAgenteInterno = (
        " AND tb.emp_identificador = fk.emp_identificador"
    )
    condicaoAgenteExterno = (
        " AND tb.age_identificador = ou.age_identificador AND tb.emp_identificador = fk.emp_identificador"
    )
    condicaoMoradorZAS = (
        " AND tb.emp_identificador = fk.emp_identificador"
    )
    condicaoFrequentadorZAS = (
        " AND tb.emp_identificador = fk.emp_identificador"
    )
    condicaoMoradorZSS = (
        " AND tb.emp_identificador = fk.emp_identificador"
    )
    condicaoFrequentadorZSS = (
        " AND tb.emp_identificador = fk.emp_identificador"
    )
    condicaoOutroInteresse = (
        " AND tb.emp_identificador = fk.emp_identificador"
    )

    nomesEmpregado = (
        "identificador", "area", "funcao"
    )
    nomesAgenteInterno = (
        "identificador", "papel",
        "complemento", "empreendimento"
    )
    nomesAgenteExterno = (
        "identificador", "papel", "complemento",
        "empreendimento", "agente"
    )
    nomesMoradorZAS = (
        "identificador", "cep", "logradouro",
        "numero", "complemento", 'bairro', "municipio",
        "empreendimento"
    )
    nomesFrequentadorZAS = (
        "identificador", "local", "empreendimento"
    )
    nomesMoradorZSS = (
        "identificador", "cep", "logradouro", "numero",
        "complemento", "bairro", "municipio", "empreendimento"
    )
    nomesFrequentadorZSS = (
        "identificador", "local", "empreendimento"
    )
    nomesOutroInteresse = (
        "identificador", "complemento", "empreendimento"
    )

    listaCampos = {}
    listaCampos["empregado"] = camposEmpregado
    listaCampos["agente_interno"] = camposAgenteInterno
    listaCampos["agente_externo"] = camposAgenteExterno
    listaCampos["morador_zas"] = camposMoradorZAS
    listaCampos["frequentador_zas"] = camposFrequentadorZAS
    listaCampos["morador_zss"] = camposMoradorZSS
    listaCampos["frequentador_zss"] = camposFrequentadorZSS
    listaCampos["outro_interesse"] = camposOutroInteresse

    listaCondicoes = {}
    listaCondicoes["empregado"] = condicaoEmpregado
    listaCondicoes["agente_interno"] = condicaoAgenteInterno
    listaCondicoes["agente_externo"] = condicaoAgenteExterno
    listaCondicoes["morador_zas"] = condicaoMoradorZAS
    listaCondicoes["frequentador_zas"] = condicaoFrequentadorZAS
    listaCondicoes["morador_zss"] = condicaoMoradorZSS
    listaCondicoes["frequentador_zss"] = condicaoFrequentadorZSS
    listaCondicoes["outro_interesse"] = condicaoOutroInteresse

    listaNomes = {}
    listaNomes["empregado"] = nomesEmpregado
    listaNomes["agente_interno"] = nomesAgenteInterno
    listaNomes["agente_externo"] = nomesAgenteExterno
    listaNomes["morador_zas"] = nomesMoradorZAS
    listaNomes["frequentador_zas"] = nomesFrequentadorZAS
    listaNomes["morador_zss"] = nomesMoradorZSS
    listaNomes["frequentador_zss"] = nomesFrequentadorZSS
    listaNomes["outro_interesse"] = nomesOutroInteresse

    for i in range(0, 8):
        if grupo is None or listaIndice[i] == grupo:
            tabela = listaTabela[i]
            camposDesejados = ""
            for j in range(len(listaCampos[listaIndice[i]])):
                camposDesejados = camposDesejados + "," + listaCampos[listaIndice[i]][j]

            condicao = (
                    "  WHERE usu_identificador = " + str(usuario) + listaCondicoes[listaIndice[i]]
            )

            dadosDetalhe, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposDesejados[1:])
            if retorno == 400:
                return 400, {"message": "Erro de acesso ao banco"}
            listaDetalhe = []
            for j in range(len(dadosDetalhe)):
                detalhe = {}
                for k in range(len(listaCampos[listaIndice[i]])):
                    detalhe[listaNomes[listaIndice[i]][k]] = dadosDetalhe[j][k]
                listaDetalhe.append(detalhe)
            resultadoFinal[listaIndice[i]] = listaDetalhe
    return 200, resultadoFinal

def trataEmpregado(entrada, usuario):
    cheque = {}
    cheque["message"] = ""
    erro = False
    area = entrada.get("area")
    funcao = entrada.get("funcao")

    if area is None or type(area) is not str or len(area) < 1:
        cheque["message"] = "Área é obrigatoria e textual."
        erro = True

    if funcao is None or type(funcao) is not str or len(funcao) < 1:
        if not erro:
            cheque["message"] = "Função é obrigatória e textual."
        else:
            cheque["message"] = cheque["message"] + " - Função é obrigatória e textual."
        erro = True

    if erro:
        return cheque, 404

    # recupera o último identificador
    camposDesejados = "max(use_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("use_usuarioempregado", None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        proximoNumero = 1
    else:
        proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = (
        "use_identificador, use_area, use_funcao, usu_identificador, use_identificadoratualizacao, use_dataatualizacao"
    )
    valores = (
        str(proximoNumero)
        + ",'"
        + area
        + "','"
        + funcao
        + "',"
        + str(usuario)
        + ","
        + str(usuario)
         + ",'"
        + agora
        + "'"
    )
    dados, retorno, header = acessoBanco.insereDado("use_usuarioempregado", camposDesejados, valores)

    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}
    mensagem["id"] = proximoNumero

    return mensagem, 201

def trataAgenteInterno(entrada, usuario):
    cheque = {}
    cheque["message"] = ""
    erro = False
    complemento = entrada.get("complemento")
    empreendimento = entrada.get("empreendimento")
    papel = entrada.get("papel")

    if papel is None or type(papel) is not str or len(papel) < 1:
        cheque["message"] = "Papel é obrigatorio e textual."
        erro = True

    if complemento is None or type(complemento) is not str or len(complemento) < 1:
        complemento = ""

    if empreendimento is None or not acessoBanco.inteiro(empreendimento):
        if not erro:
            cheque["message"] = "Empreendimento é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Empreendimento é obrigatório e numérico."
        erro = True

    if erro:
        return cheque, 404

    # recupera o último identificador
    camposDesejados = "max(uai_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("uai_usuarioagenteinterno", None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        proximoNumero = 1
    else:
        proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = (
        "uai_identificador, uai_papel, uai_complemento, emp_identificador,"
        "usu_identificador, uai_identificadoratualizacao, uai_dataatualizacao"
    )
    valores = (
        str(proximoNumero)
        + ",'"
        + papel
        + "','"
        + complemento
        + "',"
        + str(empreendimento)
        + ","
        + str(usuario)
        + ","
        + str(usuario)
        + ",'"
        + agora
        + "'"
    )
    dados, retorno, header = acessoBanco.insereDado("uai_usuarioagenteinterno", camposDesejados, valores)

    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}
    mensagem["id"] = proximoNumero

    return mensagem, 201

def trataAgenteExterno(entrada, usuario):
    cheque = {}
    cheque["message"] = ""
    erro = False
    agente = entrada.get("agente")
    complemento = entrada.get("complemento")
    empreendimento = entrada.get("empreendimento")
    papel = entrada.get("papel")

    if papel is None or type(papel) is not str or len(papel) < 1:
        cheque["message"] = "Papel é obrigatorio e textual."
        erro = True

    if complemento is None or type(complemento) is not str or len(complemento) < 1:
        complemento = ""

    if agente is None or not acessoBanco.inteiro(agente):
        if not erro:
            cheque["message"] = "Agente é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Agente é obrigatório e numérico."
        erro = True

    if empreendimento is None or not acessoBanco.inteiro(empreendimento):
        if not erro:
            cheque["message"] = "Empreendimento é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Empreendimento é obrigatório e numérico."
        erro = True


    if erro:
        return cheque, 404

    # recupera o último identificador
    camposDesejados = "max(uae_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("uae_usuarioagenteexterno", None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        proximoNumero = 1
    else:
        proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = (
        "uae_identificador, uae_papel, uae_complemento, usu_identificador, emp_identificador,"
        "age_identificador, uae_identificadoratualizacao, uae_dataatualizacao"
    )
    valores = (
        str(proximoNumero)
        + ",'"
        + papel
        + "','"
        + complemento
        + "',"
        + str(usuario)
        + ","
        + str(empreendimento)
        + ","
        + str(agente)
        + ","
        + str(usuario)
        + ",'"
        + agora
        + "'"
    )
    dados, retorno, header = acessoBanco.insereDado("uae_usuarioagenteexterno", camposDesejados, valores)

    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}
    mensagem["id"] = proximoNumero

    return mensagem, 201

def trataMoradorZAS(entrada, usuario):
    cheque = {}
    cheque["message"] = ""
    erro = False
    bairro = entrada.get("bairro")
    cep = entrada.get("cep")
    empreendimento = entrada.get("empreendimento")
    logradouro = entrada.get("logradouro")
    municipio = entrada.get("municipio")
    numero = entrada.get("numero")
    complemento = entrada.get("complemento")

    if logradouro is None or type(logradouro) is not str or len(logradouro) < 1:
        cheque["message"] = "Logradouro é obrigatorio e textual."
        erro = True

    if complemento is None or type(complemento) is not str or len(complemento) < 1:
        complemento = ""

    if bairro is None or type(bairro) is not str or len(bairro) < 1:
        bairro = ""

    if cep is None or not acessoBanco.inteiro(cep):
        cep = 0

    if numero is None or not acessoBanco.inteiro(numero):
        numero = 0

    if municipio is None or type(municipio) is not str or len(municipio) < 1:
        if not erro:
            cheque["message"] = "Municipio é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Municipio é obrigatório e numérico."
        erro = True

    if empreendimento is None or not acessoBanco.inteiro(empreendimento):
        if not erro:
            cheque["message"] = "Empreendimento é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Empreendimento é obrigatório e numérico."
        erro = True

    if erro:
        return cheque, 404

    # recupera o último identificador
    camposDesejados = "max(uma_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("uma_usuariomoradorzas", None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        proximoNumero = 1
    else:
        proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = (
        "uma_identificador, uma_cep, uma_logradouro, uma_numero, uma_complemento, "
        "uma_bairro, uma_municipio, emp_identificador, usu_identificador, "
        "uma_identificadoratualizacao, uma_dataatualizacao"
    )
    valores = (
        str(proximoNumero)
        + ","
        + str(cep)
        + ",'"
        + logradouro
        + "',"
        + str(numero)
        + ",'"
        + complemento
        + "','"
        + bairro
        + "','"
        + municipio
        + "',"
        + str(empreendimento)
        + ","
        + str(usuario)
        + ","
        + str(usuario)
        + ",'"
        + agora
        + "'"
    )

    dados, retorno, header = acessoBanco.insereDado("uma_usuariomoradorzas", camposDesejados, valores)
    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}
    mensagem["id"] = proximoNumero

    return mensagem, 201

def trataMoradorZSS(entrada, usuario):
    cheque = {}
    cheque["message"] = ""
    erro = False
    bairro = entrada.get("bairro")
    cep = entrada.get("cep")
    empreendimento = entrada.get("empreendimento")
    logradouro = entrada.get("logradouro")
    municipio = entrada.get("municipio")
    numero = entrada.get("numero")
    complemento = entrada.get("complemento")

    if logradouro is None or type(logradouro) is not str or len(logradouro) < 1:
        cheque["message"] = "Logradouro é obrigatorio e textual."
        erro = True

    if complemento is None or type(complemento) is not str or len(complemento) < 1:
        complemento = ""

    if bairro is None or type(bairro) is not str or len(bairro) < 1:
        bairro = ""

    if cep is None or not acessoBanco.inteiro(cep):
        cep = 0

    if numero is None or not acessoBanco.inteiro(numero):
        numero = 0

    if municipio is None or type(municipio) is not str or len(municipio) < 1:
        if not erro:
            cheque["message"] = "Municipio é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Municipio é obrigatório e numérico."
        erro = True

    if empreendimento is None or not acessoBanco.inteiro(empreendimento):
        if not erro:
            cheque["message"] = "Empreendimento é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Empreendimento é obrigatório e numérico."
        erro = True

    if erro:
        return cheque, 404

    # recupera o último identificador
    camposDesejados = "max(ums_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("ums_usuariomoradorzss", None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        proximoNumero = 1
    else:
        proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = (
        "ums_identificador, ums_cep, ums_logradouro, ums_numero, ums_complemento,"
        "ums_bairro, ums_municipio, emp_identificador, usu_identificador, "
        "ums_identificadoratualizacao, ums_dataatualizacao"
    )
    valores = (
        str(proximoNumero)
        + ","
        + str(cep)
        + ",'"
        + logradouro
        + "',"
        + str(numero)
        + ",'"
        + complemento
        + "','"
        + bairro
        + "','"
        + municipio
        + "',"
        + str(empreendimento)
        + ","
        + str(usuario)
        + ","
        + str(usuario)
        + ",'"
        + agora
        + "'"
    )

    dados, retorno, header = acessoBanco.insereDado("ums_usuariomoradorzss", camposDesejados, valores)
    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}
    mensagem["id"] = proximoNumero

    return mensagem, 201

def trataFrequentadorZAS(entrada, usuario):
    cheque = {}
    cheque["message"] = ""
    erro = False
    local = entrada.get("local")
    empreendimento = entrada.get("empreendimento")


    if local is None or type(local) is not str or len(local) < 1:
        cheque["message"] = "Local é obrigatorio e textual."
        erro = True

    if empreendimento is None or not acessoBanco.inteiro(empreendimento):
        if not erro:
            cheque["message"] = "Empreendimento é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Empreendimento é obrigatório e numérico."
        erro = True

    if erro:
        return cheque, 404

    # recupera o último identificador
    camposDesejados = "max(ufa_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("ufa_usuariofrequentadorzas", None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        proximoNumero = 1
    else:
        proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = (
        "ufa_identificador, ufa_local, emp_identificador, usu_identificador,"
        "ufa_identificadoratualizacao, ufa_dataatualizacao"
    )
    valores = (
        str(proximoNumero)
        + ",'"
        + local
        + "',"
        + str(empreendimento)
        + ","
        + str(usuario)
        + ","
        + str(usuario)
        + ",'"
        + agora
        + "'"
    )

    dados, retorno, header = acessoBanco.insereDado("ufa_usuariofrequentadorzas", camposDesejados, valores)
    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}
    mensagem["id"] = proximoNumero

    return mensagem, 201

def trataFrequentadorZSS(entrada, usuario):
    cheque = {}
    cheque["message"] = ""
    erro = False
    local = entrada.get("local")
    empreendimento = entrada.get("empreendimento")


    if local is None or type(local) is not str or len(local) < 1:
        cheque["message"] = "Local é obrigatorio e textual."
        erro = True

    if empreendimento is None or not acessoBanco.inteiro(empreendimento):
        if not erro:
            cheque["message"] = "Empreendimento é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Empreendimento é obrigatório e numérico."
        erro = True

    if erro:
        return cheque, 404

    # recupera o último identificador
    camposDesejados = "max(ufs_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("ufs_usuariofrequentadorzss", None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        proximoNumero = 1
    else:
        proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = (
        "ufs_identificador, ufs_local, emp_identificador, usu_identificador,"
        "ufs_identificadoratualizacao, ufs_dataatualizacao"
    )
    valores = (
        str(proximoNumero)
        + ",'"
        + local
        + "',"
        + str(empreendimento)
        + ","
        + str(usuario)
        + ","
        + str(usuario)
        + ",'"
        + agora
        + "'"
    )

    dados, retorno, header = acessoBanco.insereDado("ufs_usuariofrequentadorzss", camposDesejados, valores)
    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}
    mensagem["id"] = proximoNumero

    return mensagem, 201

def trataOutroInteresse(entrada, usuario):
    cheque = {}
    cheque["message"] = ""
    erro = False
    complemento = entrada.get("complemento")
    empreendimento = entrada.get("empreendimento")

    if complemento is None or type(complemento) is not str or len(complemento) < 1:
        cheque["message"] = "Complemento é obrigatorio e textual."
        erro = True

    if empreendimento is None or not acessoBanco.inteiro(empreendimento):
        if not erro:
            cheque["message"] = "Empreendimento é obrigatório e numérico."
        else:
            cheque["message"] = cheque["message"] + " - Empreendimento é obrigatório e numérico."
        erro = True

    if erro:
        return cheque, 404

    # recupera o último identificador
    camposDesejados = "max(uou_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("uou_usuariooutrointeresse", None, camposDesejados)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dados == []:
        proximoNumero = 1
    else:
        proximoNumero = dados[0][0] + 1
    agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    camposDesejados = (
        "uou_identificador, uou_complemento, usu_identificador, emp_identificador,"
        "uou_identificadoratualizacao, uou_dataatualizacao"
    )
    valores = (
        str(proximoNumero)
        + ",'"
        + complemento
        + "',"
        + str(usuario)
        + ","
        + str(empreendimento)
        + ","
        + str(usuario)
        + ",'"
        + agora
        + "'"
    )

    dados, retorno, header = acessoBanco.insereDado("uou_usuariooutrointeresse", camposDesejados, valores)
    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    # gera o retorno
    mensagem = {}
    mensagem["id"] = proximoNumero

    return mensagem, 201