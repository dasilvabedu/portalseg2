# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request
import bcrypt
import datetime
from validate_email import validate_email
from app import config
from random import randint
import requests
import json


def trataLogin(usu_login, usu_senha):

    # valida parametros obrigatórios
    if usu_login is None or usu_senha is None or len(usu_login) < 4 or len(usu_senha) < 8:
        return {"message": "Usuário e/ou senha inválido(s)"}, 400, {}

    # realiza consulta no banco
    if acessoBanco.inteiro(usu_login):
        condicao = "WHERE usu_autenticacao = 'ativo' and usu_celular = " + usu_login
    else:
        condicao = "WHERE usu_autenticacao = 'ativo' and usu_email = '" + usu_login + "'"
    dados, retorno, mensagemRetorno = acessoBanco.dado("usu_usuario", condicao, None, None)
    if retorno != 200:
        return {"message": "Erro de acesso ao banco ou de sistema"}, 400, {}

    # valida os dados do usuário
    volta = {}
    if dados == []:
        volta["message"] = "Usuário não cadastrado"
    elif not bcrypt.checkpw(usu_senha.encode("utf-8"), dados[0]["usu_senha"].encode("utf-8")):
        volta["message"] = "Senha não confere"
    elif dados[0]["usu_autenticacao"] != "ativo":
        volta["message"] = "Usuário inativo"

    if volta != {}:
        return volta, 404, {}

    agora = datetime.datetime.utcnow()
    dicionarioRetorno = {}
    dicionarioRetorno["sub"] = dados[0]["usu_identificador"]
    dicionarioRetorno["id"] = dados[0]["usu_identificador"]
    dicionarioRetorno["name"] = dados[0]["usu_nome"]
    dicionarioRetorno["iat"] = agora
    dicionarioRetorno["exp"] = ""
    dicionarioRetorno["user_role_ids"] = []
    dicionarioRetorno["allowed_transactions"] = []
    dicionarioRetorno["email"] = dados[0]["usu_email"]
    dicionarioRetorno["phone_number"] = dados[0]["usu_celular"]
    dicionarioRetorno["active"] = True

    # recupera os perfis associados
    camposdesejados = "usu_pfa_usuario_perfilacesso.pfa_identificador"
    tabela = "usu_pfa_usuario_perfilacesso"
    condicao = (
        "INNER JOIN usu_usuario ON usu_usuario.usu_identificador = usu_pfa_usuario_perfilacesso.usu_identificador "
        + "WHERE usu_usuario.usu_identificador = "
        + str(dados[0]["usu_identificador"])
    )

    dadosPerfil, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, {}

    if len(dadosPerfil) != 0:
        perfis = ""
        listaPerfis = []
        for i in range(len(dadosPerfil)):
            perfis = perfis + str(dadosPerfil[i][0]) + ","
            listaPerfis.append(str(dadosPerfil[i][0]))
        perfis = perfis[0:-1]
        dicionarioRetorno["user_role_ids"] = listaPerfis

        # recupera as transacoes associadas
        camposdesejados = "pfa_trn_perfilacesso_transacaosistema.trn_identificador"
        tabela = "pfa_trn_perfilacesso_transacaosistema"
        condicao = (
            "INNER JOIN pfa_perfilacesso ON "
            + "pfa_perfilacesso.pfa_identificador = pfa_trn_perfilacesso_transacaosistema.pfa_identificador "
            + "WHERE pfa_perfilacesso.pfa_identificador IN "
            + "(" + perfis + ")"
        )
        dadosTransacao, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, {}

        if len(dadosTransacao) != 0:
            transacoes = "("
            for i in range(len(dadosTransacao)):
                transacoes = transacoes + str(dadosTransacao[i][0]) + ","
            transacoes = transacoes[0:-1] + ")"

            # recupera o código das transações associadas
            camposdesejados = "trn_codigo"
            tabela = "trn_transacaosistema"
            condicao = "WHERE trn_identificador IN "
            condicao = condicao + transacoes
            dadosCodigo, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
            if retorno == 400:
                return {"message": "Erro de acesso ao banco"}, 400, {}

            codigoTransacao = []
            for i in range(len(dadosCodigo)):
                codigoTransacao.append(dadosCodigo[i][0])
            codigoTransacao = list(set(codigoTransacao))
            dicionarioRetorno["allowed_transactions"] = codigoTransacao

    # gera o token
    token = gestaoAutenticacao.geraToken(dicionarioRetorno)
    headerRetorno = {}
    headerRetorno["Authorization"] = "Bearer " + token
    return {"token": token}, 200, headerRetorno


def usuarioNovoLista():
    if request.method == "POST":
        if request.data == "" or request.json is None:
            return {"message": "Dados de entrada não fornecidos"}, 404, {}
        entrada = request.json
        usu_celular = entrada.get("phone_number")
        usu_email = entrada.get("email")
        usu_senha = entrada.get("password")
        usu_nome = entrada.get("name")
        resultadoFinal, retorno, header = trataUsuarioIncluido(usu_celular, usu_email, usu_senha, usu_nome)
        return resultadoFinal, retorno, header
    elif request.method == "GET":
        checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
        if not checa:
            return mensagem, 404, {}

        resultadoFinal, retorno = listaUsuario()
        return resultadoFinal, retorno, header

    return {"message": "Método invalido"}, 400, {}


def usuarioAtual(id):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 404, {}

    if request.method == "PATCH":
        token, dadosToken = gestaoAutenticacao.expandeToken()
        if dadosToken["sub"] != id:
            return {"message": "Não é possível alterar dados de outro usuário."}, 404, header

        # atualização de usuário
        if not request.json:
            return {'"message": "Dados de entrada não fornecidos"'}, 404, header

        entrada = request.json
        usu_celular = entrada.get("phone_number")
        usu_email = entrada.get("email")
        usu_senha = entrada.get("password")
        usu_nome = entrada.get("name")
        resultadoFinal, retorno = trataUsuarioAlterado(id, usu_celular, usu_email, usu_senha, usu_nome)
        return resultadoFinal, retorno, header
    elif request.method == "DELETE":
        token, dadosToken = gestaoAutenticacao.expandeToken()
        if dadosToken["sub"] != id:
            return {"message": "Não é possível alterar dados de outro usuário."}, 404, header

        checa, mensagem = trataUsuarioDeletado(id)
        if not checa:
            return mensagem, 404, header
        return "", 200, header
    elif request.method == "GET":

        checa, mensagem, dados = usuarioEspecifico(id)
        if not checa:
            return {"message": "Não foi possível recuperar dados deste usuario"}, 404, header
        return dados, 200, header

    return {"message": "Método invalido"}, 400, header


def usuarioInativo(id):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 404, ""

    campos = "count(usu_identificador)"
    condicao = "WHERE usu_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, campos)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header
    if dados[0][0] == 0:
        return {"message": "Usuário Inexistente"}, 404, header

    condicao = "WHERE usu_identificador = " + str(id)
    valores = "usu_autenticacao = 'inativo'"
    dados, retorno, mensagemRetorno = acessoBanco.alteraDado("usu_usuario", valores, condicao)
    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header
    return {}, 200, {}

def usuarioAtivo(id):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 404, ""

    campos = "count(usu_identificador)"
    condicao = "WHERE usu_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, campos)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header
    if dados[0][0] == 0:
        return {"message": "Usuário Inexistente"}, 404, header

    condicao = "WHERE usu_identificador = " + str(id)
    valores = "usu_autenticacao = 'ativo'"
    dados, retorno, mensagemRetorno = acessoBanco.alteraDado("usu_usuario", valores, condicao)
    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header
    return {}, 200, {}

def usuarioExistente():
    if not request.json:
        return {'"message": "Dados de entrada não fornecidos"'}, 404, {}

    entrada = request.json
    print(entrada)
    print(type(entrada))
    usu_login = entrada.get("username")
    usu_senha = entrada.get("password")
    resultadoFinal, retorno, header = trataLogin(usu_login, usu_senha)
    return resultadoFinal, retorno, header


def usuarioTokenDesativado(header):

    campos = "count(tki_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("tki_tokeninvalidado", None, campos)

    if retorno == 400:
        resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
        return {"message": "Erro de acesso ao banco"}, 400, header

    if dados[0][0] == 0:
        tki_identificador = 1
    else:
        campos = "max(tki_identificador)"
        dados, retorno, mensagemRetorno = acessoBanco.leDado("tki_tokeninvalidado", None, campos)

        if retorno == 400:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return {"message": "Erro de acesso ao banco"}, 400, header

        tki_identificador = dados[0][0] + 1

    token, dadosToken = gestaoAutenticacao.expandeToken()
    campos = "count(usu_identificador)"
    condicao = "WHERE usu_identificador = " + str(dadosToken["sub"])
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, campos)
    if retorno == 400:
        resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
        return {"message": "Erro de acesso ao banco"}, 400, header

    if dados[0][0] == 0:
        return {"message": "Usuário foi apagado da base de dados"}, 404, {}

    campos = (
        "tki_identificador, usu_identificador, tki_token, tki_dataexpiracao, tki_identificadoratualizacao, "
        + "tki_dataatualizacao"
    )
    valores = (
        str(tki_identificador)
        + ","
        + str(dadosToken["sub"])
        + ",'"
        + token
        + "','"
        + dadosToken["exp"].strftime("%Y-%m-%d %H:%M:%S")
    )
    valores = (
        valores + "'," + str(dadosToken["sub"]) + ",'" + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + "'"
    )
    resultado, retorno, mensagem = acessoBanco.insereDado("tki_tokeninvalidado", campos, valores)
    if retorno == 400:
        return {"message": "Erro no acesso ao banco"}, 400, header
    return {}, 200, {}


def trataUsuarioIncluido(usu_celular, usu_email, usu_senha, usu_nome):

    cheque = {}
    cheque["message"] = ""
    erro = False

    if usu_senha is None or len(usu_senha) < 8:
        cheque["message"] = "Senha é obrigatória, com tamanho mínimo de 8 caracteres"
        erro = True

    if (usu_celular is None or len(usu_celular) == 0) and (usu_email is None or len(usu_email) == 0):
        if not erro:
            cheque["message"] = "Celular e Senha não podem ser ambos nulos"
        else:
            cheque["message"] = cheque["message"] + " - Celular e Senha não podem ser ambos nulos"
        erro = True

    if usu_celular is not None and len(usu_celular) > 0:
        if not acessoBanco.inteiro(usu_celular):
            if not erro:
                cheque["message"] = "Celular deve ser numérico"
            else:
                cheque["message"] = cheque["message"] + " - Celular deve ser numérico"
            erro = True
        elif int(usu_celular) < 10000000000 or int(usu_celular) > 99000000000:
            if not erro:
                cheque["message"] = "Celular deve possuir 9 dígitos"
            else:
                cheque["message"] = cheque["message"] + " - Celular deve possuir 9 dígitos"
            erro = True

    if usu_nome is None or len(usu_nome) < 1:
        if not erro:
            cheque["message"] = "Nome do usuário é obrigatorio"
        else:
            cheque["message"] = cheque["message"] + " - Nome do usuário é obrigatorio"
        erro = True

    if usu_email is not None and len(usu_email) > 0:
        if not validate_email(usu_email):
            if not erro:
                cheque["message"] = "Email invalido"
                erro = True
            else:
                cheque["message"] = cheque["message"] + " - Email invalido"
            erro = True

    if erro:
        return cheque, 404, {}

    if usu_celular is not None:
        condicao = "WHERE usu_celular = " + str(usu_celular)
        if usu_email is not None:
            condicao = condicao + " or usu_email = '" + usu_email + "'"
    else:
        condicao = "WHERE usu_email = '" + usu_email + "'"

    camposDesejados = "usu_autenticacao"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno, {}

    if dados != []:
        autentica = " "
        for i in range(len(dados)):
            if "ativo" in dados[i]:
                autentica = "ativo"
        if autentica == "ativo":
            cheque["message"] = "Celular ou e-mail já cadastrado com usuário ativo"
            return cheque, 404, {}

    dados, retorno, header = acessoBanco.insereUsuario(usu_celular, usu_email, usu_senha, usu_nome)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400, {}

    # gera o token
    token = gestaoAutenticacao.geraToken(dados)
    dados.pop("exp")
    dados.pop("sub")
    dados.pop("iat")
    dados.pop("user_role_ids")
    dados.pop("allowed_transactions")
    headerRetorno = {}
    headerRetorno["Authorization"] = "Bearer " + token

    return dados, 201, headerRetorno


def listaUsuario():

    camposDesejados = "usu_identificador, usu_nome, usu_celular, usu_email, usu_autenticacao"
 #   condicao = "WHERE usu_autenticacao = 'ativo'"
    condicao = None
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    dadosRetorno = []
    dicRetorno = {}
    for i in range(len(dados)):
        mensagem = {}
        mensagem["id"] = dados[i][0]
        mensagem["name"] = dados[i][1]
        mensagem["phone_number"] = dados[i][2]
        mensagem["email"] = dados[i][3]
        if dados[i][4] == "ativo":
            mensagem["active"] = True
        else:
            mensagem["active"] = False
        mensagem["status"] = dados[i][4]
        dadosRetorno.append(mensagem)
    dicRetorno["users"] = dadosRetorno
    return dicRetorno, 200


def trataUsuarioAlterado(id, usu_celular, usu_email, usu_senha, usu_nome):

    usu_identificador = id

    cheque = {}
    erro = False
    alteracao = False
    senhaCriptografada = None

    if usu_celular is not None and len(usu_celular) > 0:
        if not acessoBanco.inteiro(usu_celular):
            if not erro:
                cheque["message"] = "Celular deve ser numérico"
            else:
                cheque["message"] = cheque["message"] + " # Celular deve ser numérico"
            erro = True
        elif int(usu_celular) < 10000000000 or int(usu_celular) > 99000000000:
            if not erro:
                cheque["message"] = "Celular deve possuir 9 dígitos"
            else:
                cheque["message"] = cheque["message"] + " # Celular deve possuir 9 dígitos"
            erro = True
        else:
            alteracao = True

    if usu_email is not None and len(usu_email) > 0:
        if validate_email(usu_email):
            alteracao = True
        else:
            if not erro:
                cheque["message"] = "Email invalido"
            else:
                cheque["message"] = cheque["message"] + " # Email invalido"
            erro = True

    if usu_nome is not None and len(usu_nome) > 0:
        alteracao = True

    if usu_senha is not None:
        if len(usu_senha) < 8:
            if not erro:
                cheque["message"] = "Senha deve possuin pelo menos 8 caracteres."
            else:
                cheque["message"] = cheque["message"] + " # Senha deve possuin pelo menos 8 caracteres."
            erro = True
        else:
            salt = bcrypt.gensalt(rounds=12)
            senhaCriptografada = bcrypt.hashpw(usu_senha.encode("utf-8"), salt).decode("utf-8")
            alteracao = True

    if erro:
        return cheque, 404

    if not alteracao:
        cheque["message"] = "Não existe(m) alteração(ões) a realizar"
        return cheque, 404

    campos = "usu_celular, usu_email, usu_senha, usu_nome, usu_autenticacao"
    condicao = "WHERE usu_identificador = " + str(usu_identificador)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, campos)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco de dados"}, retorno

    if dados == []:
        cheque["message"] = "Usuário não cadastrado"
        return cheque, 404

    if dados[0][4] != "ativo":
        cheque["message"] = "Usuário inativo"
        return cheque, 404

    usu_celular_ant = dados[0][0]
    usu_email_ant = dados[0][1]
    usu_senha_ant = dados[0][2]
    usu_nome_ant = dados[0][3]

    agora = datetime.datetime.utcnow()
    iat = agora.isoformat().replace("T", " ") + "Z"

    dicionarioRetorno = {}
    dicionarioRetorno["id"] = id
    dicionarioRetorno["name"] = usu_nome_ant
    dicionarioRetorno["email"] = usu_email_ant
    dicionarioRetorno["phone_number"] = usu_celular_ant
    dicionarioRetorno["active"] = True

    if usu_celular is not None:
        condicao = "WHERE usu_celular = " + str(usu_celular) + " AND usu_identificador <> " + str(usu_identificador)
        campos = "usu_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, campos)

        if retorno == 400:
            return {"message": "Erro de acesso ao banco de dados"}, retorno

        if dados != []:
            cheque["message"] = "Celular está cadastrado em nome de outro usuário"
            erro = True

        if usu_email is not None:
            condicao = "WHERE usu_email = '" + usu_email + "' AND usu_identificador <> " + str(usu_identificador)
            campos = "usu_identificador"
            dicionarioRetorno["email"] = usu_email
            dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, campos)

            if retorno == 400:
                return {"message": "Erro de acesso ao banco de dados"}, retorno

            if dados != []:
                if erro:
                    cheque["message"] = cheque["message"] + " - Email já cadastrado em nome de outro usuário"
                else:
                    cheque["message"] = "Email já cadastrado em nome de outro usuário"
                    erro = True

        if erro:
            return cheque, 404

    comando_cel = ""
    comando_email = ""
    comando_senha = ""
    comando_nome = ""

    if usu_celular is not None:
        dicionarioRetorno["phone_number"] = usu_celular
        comando_cel = ",usu_celular = " + str(usu_celular)

    if usu_email is not None:
        dicionarioRetorno["email"] = usu_email
        comando_email = ", usu_email = '" + usu_email + "'"

    if senhaCriptografada is not None:
        if senhaCriptografada != usu_senha_ant:
            comando_senha = ", usu_senha = '" + senhaCriptografada + "'"

    if usu_nome is not None:
        if usu_nome != usu_nome_ant:
            dicionarioRetorno["name"] = usu_nome
            comando_nome = ", usu_nome = '" + usu_nome + "'"

    comando = comando_cel + comando_email + comando_senha + comando_nome
    if len(comando) == 0:
        return dicionarioRetorno, 200

    comando = comando[1:] + ", usu_dataatualizacao = '" + iat + "'"
    condicao = "WHERE usu_identificador = " + str(usu_identificador)
    dados, retorno, mensagemRetorno = acessoBanco.alteraDado("usu_usuario", comando, condicao)
    if retorno != 200:
        return {"message": "Erro de acesso ao banco de dados"}, retorno

    return dicionarioRetorno, 200


def trataUsuarioDeletado(id):

    usu_identificador = id

    condicao = "WHERE usu_identificador = " + str(usu_identificador)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, None)

    if retorno == 400:
        return False, {"message": "Erro de acesso ao banco de dados"}

    if dados == []:
        return False, {"message": "Usuário não cadastrado"}

    checa, mensagemRetorno = acessoBanco.exclueUsuario(usu_identificador)
    if not checa:
        return False, mensagemRetorno

    return True, {}


def usuarioTransacaoValidada():
    checa, header = gestaoAutenticacao.validaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(404, "Token inválido ou expirado")
        return resultadoFinal, 404, header

    query_parameters = request.args
    usu_login = query_parameters.get("login")
    trn_transacao = query_parameters.get("transacao")

    # valida parametros obrigatórios
    if usu_login is None or trn_transacao is None:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Usuário e/ou transação não fornecido(s)"
        resultadoFinal = acessoBanco.montaRetorno(404, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = " "
        return resultadoFinal, 404, header

    # realiza consulta no banco
    if acessoBanco.inteiro(usu_login):
        condicao = "WHERE usu_autenticacao = 'ativo' and usu_celular = " + usu_login
    else:
        condicao = "WHERE usu_autenticacao = 'ativo' and usu_email = '" + usu_login + "'"
    camposDesejados = "usu_identificador"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, camposDesejados)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno == 400:
        return resultadoFinal, retorno, header

    if dados == []:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Usuário não cadastrado"
        resultadoFinal = acessoBanco.montaRetorno(404, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = " "
        return resultadoFinal, 404, header

    usu_identificador = dados[0][0]

    # recupera os perfis associados
    camposdesejados = "usu_pfa_usuario_perfilacesso.pfa_identificador"
    tabela = "usu_pfa_usuario_perfilacesso"
    condicao = (
        "INNER JOIN usu_usuario ON usu_usuario.usu_identificador = usu_pfa_usuario_perfilacesso.usu_identificador "
        + "WHERE usu_usuario.usu_identificador = "
        + str(usu_identificador)
    )
    dadosPerfil, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
    if retorno == 400:
        return resultadoFinal, retorno, header

    if dadosPerfil == []:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Usuário não possui perfil associado"
        resultadoFinal = acessoBanco.montaRetorno(404, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = ""
        return resultadoFinal, 404, header
    else:
        perfis = ""
        for i in range(len(dadosPerfil)):
            perfis = perfis + str(dadosPerfil[i][0]) + ","
    perfis = perfis[0:-1]

    # recupera as transacoes associadas
    camposdesejados = "pfa_trn_perfilacesso_transacaosistema.trn_identificador"
    tabela = "pfa_trn_perfilacesso_transacaosistema"
    condicao = (
        "INNER JOIN pfa_perfilacesso ON "
        + "pfa_perfilacesso.pfa_identificador = pfa_trn_perfilacesso_transacaosistema.pfa_identificador "
        + "WHERE pfa_perfilacesso.pfa_identificador IN "
        + "(" + perfis + ")"
    )
    dadosTransacao, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
    if retorno == 400:
        return resultadoFinal, retorno, header

    if dadosTransacao == []:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Usuário não possui perfil com transação associada"
        resultadoFinal = acessoBanco.montaRetorno(404, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = ""
        return resultadoFinal, 404, header
    else:
        transacoes = "("
        for i in range(len(dadosTransacao)):
            transacoes = transacoes + str(dadosTransacao[i][0]) + ","
    transacoes = transacoes[0:-1] + ")"

    # recupera o código das transações associadas
    camposdesejados = "trn_codigo"
    tabela = "trn_transacaosistema"
    condicao = "WHERE trn_identificador IN "
    condicao = condicao + transacoes
    dadosCodigo, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
    if retorno == 400:
        return resultadoFinal, retorno, header

    for i in range(len(dadosCodigo)):
        if trn_transacao == (str(dadosCodigo[i][0])):
            listaMensagem = {}
            listaMensagem["acesso"] = "ok"
            listaMensagem["texto"] = "Transação validada"
            resultadoFinal = acessoBanco.montaRetorno(200, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = ""
            return resultadoFinal, 200, header

    listaMensagem = {}
    listaMensagem["acesso"] = "nok"
    listaMensagem["texto"] = "Transacao não permitida para usuário"
    resultadoFinal = acessoBanco.montaRetorno(404, "")
    resultadoFinal["retorno"] = listaMensagem
    resultadoFinal["aresposta"]["texto"] = ""
    return resultadoFinal, 404, header


def usuarioEspecifico(id):

    mensagem = {}
    dadosToken = {}
    campo = "usu_celular,usu_email, usu_autenticacao, usu_nome"
    condicao = "WHERE usu_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, campo)
    if retorno != 200:
        return False, mensagemRetorno, []

    dadosToken["phone_number"] = str(dados[0][0])
    dadosToken["email"] = str(dados[0][1])
    if dados[0][2] == "ativo":
        dadosToken["active"] = True
    else:
        dadosToken["active"] = False
    dadosToken["name"] = dados[0][3]

    # recupera os celulares adicionais
    campo = "uca_celular"
    condicao = "WHERE usu_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("uca_celularadicional", condicao, campo)
    if retorno == 400:
        return False, mensagemRetorno, []
    codigo = []
    for i in range(len(dados)):
        codigo.append(str(dados[i][0]))
    codigo = list(set(codigo))
    dadosToken["phone_others"] = codigo

    # recupera os emails adicionais
    campo = "uea_email"
    condicao = "WHERE usu_identificador = " + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("uea_emailadicional", condicao, campo)
    if retorno == 400:
        return False, {"message": "Erro de acesso ao banco"}, []
    codigo = []
    for i in range(len(dados)):
        codigo.append(dados[i][0])
    codigo = list(set(codigo))
    dadosToken["email_others"] = codigo

    # recupera os perfis de acesso
    camposDesejados = "pfa_perfilacesso.pfa_identificador, pfa_descricao"
    condicao = (
        "INNER JOIN pfa_perfilacesso ON  "
        + "usu_pfa_usuario_perfilacesso.pfa_identificador = pfa_perfilacesso.pfa_identificador "
        + "where usu_identificador =  " + str(id)
    )
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_pfa_usuario_perfilacesso", condicao, camposDesejados)
    if retorno == 400:
        return False, {"message": "Erro de acesso ao banco"}, []

    sigla = []
    nome = []
    for i in range(len(dados)):
        sigla.append(dados[i][0])
        nome.append(dados[i][1])
    dadosToken["user_role_ids"] = sigla
    dadosToken["user_role_names"] = nome

    # recupera os empreendimentos
    camposDesejados = "emp_sigla, emp_nome,  usu_emp_usuario_empreendimento.emp_identificador"
    condicao = (
        "INNER JOIN emp_empreendimento ON  "
        + "usu_emp_usuario_empreendimento.emp_identificador = emp_empreendimento.emp_identificador "
        + "where usu_identificador =  " + str(id)
    )
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_emp_usuario_empreendimento", condicao, camposDesejados)
    if retorno == 400:
        return False, {"message": "Erro de acesso ao banco"}, []

    sigla = []
    nome = []
    codigo = []
    for i in range(len(dados)):
        sigla.append(dados[i][0])
        nome.append(dados[i][1])
        codigo.append(str(dados[i][2]))
    dadosToken["site_codes"] = sigla
    dadosToken["site_names"] = nome
    dadosToken["site_ids"] = codigo

    # recupera os perfis de usuario
    camposDesejados = "pfu_sigla, pfu_descricao"
    condicao = (
        "INNER JOIN pfu_perfilusuario ON  "
        + "usu_pfu_usuario_perfilusuario.pfu_identificador = pfu_perfilusuario.pfu_identificador "
        + "where usu_identificador =  " + str(id)
    )
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_pfu_usuario_perfilusuario", condicao, camposDesejados)
    if retorno == 400:
        return False, {"message": "Erro de acesso ao banco"}, []

    sigla = []
    nome = []
    for i in range(len(dados)):
        sigla.append(dados[i][0])
        nome.append(dados[i][1])
    dadosToken["trainning_codes"] = sigla
    dadosToken["trainning_names"] = nome

    # prepara a volta

    return True, 200, dadosToken


def usuarioRecuperaSenha():
    if not request.json:
        return {'"message": "Dados de entrada não fornecidos"'}, 400, {}

    entrada = request.json
    usu_login = entrada.get("username")

    if usu_login is None:
        return {"message": "Parâmetro não fonecido"}, 404, {}
    if acessoBanco.inteiro(usu_login):
        condicao = "WHERE usu_celular = " + str(usu_login)
    else:
        condicao = "WHERE usu_email = '" + usu_login + "'"

    camposDesejados = "usu_identificador, usu_celular, usu_email, usu_nome, usu_autenticacao"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco de dados"}, 400, {}

    if dados == []:
        return {"message": "Usuário não cadastrado"}, 404, {}

    if dados[0][4] != "ativo":
        return {"message": "Usuário inativo não pode recuperar senha. O cadastro deve ser refeito."}, 404, {}

    body_mensagem = {}
    lista_urns = []
    texto = "mailto:" + dados[0][2]
    lista_urns.append(texto)
    texto = "tel: +55" + str(dados[0][1])
    lista_urns.append(texto)
    body_mensagem["urns"] = lista_urns
    dic_codigo = {}
    codigo = randint(100000, 999999)
    dic_codigo["codigo"] = codigo
    body_mensagem["params"] = dic_codigo
    body_mensagem["flow"] = config.FLOW_MENSAGEM
    body = json.dumps(body_mensagem)

    header = {}
    header["Authorization"] = config.HEADER_MENSAGEM
    header["Content-Type"] = "application/json"

    res = requests.post(config.CAMINHO_MENSAGEM, data=body, headers=header)

    if res.status_code != 201:
        return {"message": "Não foi possível enviar o código"}, 404, {}

    dadosNovo, retorno, header = novoToken(dados[0][0], dados[0][1], dados[0][2], dados[0][3])

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, 400, {}

    # gera o token
    token = gestaoAutenticacao.geraToken(dadosNovo)

    headerRetorno = {}
    headerRetorno["Authorization"] = "Bearer " + token

    mensagem = {}
    mensagem["code"] = codigo
    mensagem["id"] = dados[0][0]
    mensagem["phone_number"] = dados[0][1]
    mensagem["email"] = dados[0][2]
    mensagem["name"] = dados[0][3]
    mensagem["token"] = "Bearer " + token

    return mensagem, 200, headerRetorno


def novoToken(usu_identificador, usu_celular, usu_email, usu_nome):

    # trata dos dados recebidos
    agora = datetime.datetime.utcnow()

    dicionarioRetorno = {}
    dicionarioRetorno["sub"] = usu_identificador
    dicionarioRetorno["id"] = usu_identificador
    dicionarioRetorno["name"] = usu_nome
    dicionarioRetorno["iat"] = agora
    dicionarioRetorno["exp"] = ""
    dicionarioRetorno["user_role_ids"] = []
    dicionarioRetorno["allowed_transactions"] = []
    dicionarioRetorno["email"] = usu_email
    dicionarioRetorno["phone_number"] = usu_celular
    dicionarioRetorno["active"] = True

    # recupera os perfis associados
    camposdesejados = "usu_pfa_usuario_perfilacesso.pfa_identificador"
    tabela = "usu_pfa_usuario_perfilacesso"
    condicao = (
        "INNER JOIN usu_usuario ON "
        + "usu_usuario.usu_identificador = usu_pfa_usuario_perfilacesso.usu_identificador "
        + "WHERE usu_usuario.usu_identificador = "
        + str(usu_identificador)
    )

    dadosPerfil, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
    if retorno != 200:
        return {}, retorno, {}

    if len(dadosPerfil) != 0:
        perfis = ""
        listaPerfis = []
        for i in range(len(dadosPerfil)):
            perfis = perfis + str(dadosPerfil[i][0]) + ","
            listaPerfis.append(str(dadosPerfil[i][0]))
        perfis = perfis[0:-1]
        dicionarioRetorno["user_role_ids"] = listaPerfis

        # recupera as transacoes associadas
        camposdesejados = "pfa_trn_perfilacesso_transacaosistema.trn_identificador"
        tabela = "pfa_trn_perfilacesso_transacaosistema"
        condicao = (
            "INNER JOIN pfa_perfilacesso ON "
            + "pfa_perfilacesso.pfa_identificador = pfa_trn_perfilacesso_transacaosistema.pfa_identificador "
            + "WHERE pfa_perfilacesso.pfa_identificador IN "
            + "(" + perfis + ")"
        )
        dadosTransacao, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, {}

        if len(dadosTransacao) != 0:
            transacoes = "("
            for i in range(len(dadosTransacao)):
                transacoes = transacoes + str(dadosTransacao[i][0]) + ","
            transacoes = transacoes[0:-1] + ")"

            # recupera o código das transações associadas
            camposdesejados = "trn_codigo"
            tabela = "trn_transacaosistema"
            condicao = "WHERE trn_identificador IN "
            condicao = condicao + transacoes
            dadosCodigo, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
            if retorno == 400:
                return {"message": "Erro de acesso ao banco"}, 400, {}

            codigoTransacao = []
            for i in range(len(dadosCodigo)):
                codigoTransacao.append(dadosCodigo[i][0])
            codigoTransacao = list(set(codigoTransacao))
            dicionarioRetorno["allowed_transactions"] = codigoTransacao

    return dicionarioRetorno, 200, {}

def emailIncluiLista():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 404, {}
    token, dadosToken = gestaoAutenticacao.expandeToken()

    if request.method == "GET":
        resultado,lista = dicionarioEmail(dadosToken["sub"])
        if resultado == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header
        resultadoFinal = {}
        resultadoFinal['email_others'] = lista
        return resultadoFinal, 200, header

    elif request.method == "POST":
        if not request.json:
            return {"message": "Dados de entrada não fornecidos"}, 404, header
        entrada = request.json
        listaEmails = entrada.get("email_others")
        if listaEmails is None:
            return {"message": "Lista de Emails obrigatoria"}, 404, header
        erro = False
        cheque = {}
        for i in range(len(listaEmails)):
            if not validate_email(listaEmails[i]):
                if erro == False:
                    cheque["message"] = "Email " + str(i+1) + " é inválido"
                    erro = True
                else:
                   cheque["message"] = cheque["message"] + "  - Email " + str(i+1) + " é inválido"

        if erro:
            return cheque, 404, header

        # recupera o próximo identificador
        campo = "max(uea_identificador)"
        dados, retorno, mensagemRetorno = acessoBanco.leDado("uea_emailadicional", None, campo)
        if retorno != 200:
            return mensagemRetorno, retorno, header
        if dados[0][0] is None:
            identificadorAtual = 0
        else:
            identificadorAtual = dados[0][0]

        agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        for i in range(len(listaEmails)):
            campo = "uea_identificador"
            condicao = " WHERE usu_identificador = " + str(dadosToken["sub"]) + " AND uea_email = '" + listaEmails[i] + "'"
            dados, retorno, mensagemRetorno = acessoBanco.leDado("uea_emailadicional", condicao, campo)
            if retorno == 400:
                return mensagemRetorno, retorno, header
            if retorno == 404:
                identificadorAtual = identificadorAtual + 1
                campos = (
                    "uea_identificador, uea_email, usu_identificador, uea_identificadoratualizacao,"
                    "uea_dataatualizacao"
                )
                valores = (
                    str(identificadorAtual)
                    + ",'" + listaEmails[i]  + "'"
                    + "," + str(dadosToken["sub"])
                    + "," + str(dadosToken["sub"])
                    + ",'" + str(agora) + "'"
                )
                dados, retorno, mensagemRetorno = acessoBanco.insereDado("uea_emailadicional", campos, valores)
                if retorno == 400:
                    return mensagemRetorno, retorno, header
        return {}, 201, header

def atualizaPerfil():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 404, {}
    token, dadosToken = gestaoAutenticacao.expandeToken()

    if not request.json:
        return {"message": "Dados de entrada não fornecidos"}, 404, header

    entrada = request.json
    usuario = entrada.get("user_id")
    listaPerfis = entrada.get("roles_id")

    cheque = {}
    erro = False

    if usuario is None or not acessoBanco.inteiro(usuario):
        cheque["message"] = "Código de usuário obrigatório"
        erro = True
    else:
        # verifica se existe o usurio
        campo = "usu_nome"
        condicao = " WHERE usu_identificador = " + str(usuario)
        dados, retorno, mensagemRetorno = acessoBanco.leDado("usu_usuario", condicao, campo)
        if retorno == 400:
            return mensagemRetorno, retorno, header
        elif retorno != 200:
            cheque["message"] = "Usuário inexistente"
            erro = True

    if listaPerfis is None or len(listaPerfis) == 0 or type(listaPerfis) is not list:
        if not erro:
            cheque["message"] = "Lista de Perfis de Acesso é obrigatoria"
        else:
            cheque["message"] = cheque["message"] + " - Lista de Perfis de Acesso é obrigatoria"
        erro = True
    else:
        for i in range(len(listaPerfis)):
            if not acessoBanco.inteiro(listaPerfis[i]):
                if erro == False:
                    cheque["message"] = "Id do Perfil de Acesso " + str(i+1) + " é inválido"
                    erro = True
                else:
                   cheque["message"] = cheque["message"] + "  - Id do Perfil de Acesso " + str(i+1) + " é inválido"

            # verifica se existe o perfil de acesso
            campo = "pfa_identificaor"
            condicao = " WHERE pfa_identificador = " + str(listaPerfis[i])
            dados, retorno, mensagemRetorno = acessoBanco.leDado("pfa_perfilacesso", condicao, campo)
            if retorno == 400:
                return mensagemRetorno, retorno, header
            elif retorno != 200:
                if erro == False:
                    cheque["message"] = "Id do Perfil de Acesso " + str(i + 1) + " inexistente"
                    erro = True
                else:
                    cheque["message"] = cheque["message"] + "  - Id do Perfil de Acesso " + str(i + 1) + " inexistente"

    if erro:
        return cheque, 404, header

    # atualiza os dados
    dados, retorno, mensagemRetorno = acessoBanco.atualizaAcesso(usuario, listaPerfis, dadosToken['sub'])
    return mensagemRetorno, retorno, header

def telefoneIncluiListaDeleta():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 404, {}
    token, dadosToken = gestaoAutenticacao.expandeToken()

    if request.method == "GET":
        resultado,listaCelular = dicionarioCelular(dadosToken["sub"])
        if resultado == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header

        resultado,listaTelefone = dicionarioTelefone(dadosToken["sub"])
        if resultado == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header
        listaFinal = []
        if listaCelular != []:
            listaFinal = listaCelular
        listaFinal = listaFinal + listaTelefone

        resultadoFinal = {}
        resultadoFinal['general_phone_others'] = listaFinal
        return resultadoFinal, 200, header

    elif request.method == "POST":
        if not request.json:
            return {"message": "Dados de entrada não fornecidos"}, 404, header
        entrada = request.json
        listaTelefones = entrada.get("general_phone_others")
        if listaTelefones is None:
            return {"message": "Lista de Telefones obrigatoria"}, 404, header
        retorno, mensagem, listaCelular, listaFixo = validaTelefone(listaTelefones)
        if retorno == 404:
            return mensagem, 404, header

        # inclui celular
        for i in range(len(listaCelular)):
            campo = "max(uca_identificador)"
            dados, retorno, mensagemRetorno = acessoBanco.leDado("uca_celularadicional", None, campo)
            if retorno != 200:
                return mensagemRetorno, retorno, header
            if dados[0][0] is None:
                identificadorAtual = 0
            else:
                identificadorAtual = dados[0][0]

            agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            campo = "uca_identificador"
            condicao = (
                    " WHERE usu_identificador = " + str(dadosToken["sub"]) +
                    " AND uca_celular = " + str(listaCelular[i])
            )
            dados, retorno, mensagemRetorno = acessoBanco.leDado("uca_celularadicional", condicao, campo)
            if retorno == 400:
                return mensagemRetorno, retorno, header
            if retorno == 404:
                identificadorAtual = identificadorAtual + 1
                campos = (
                    "uca_identificador, uca_celular, usu_identificador, uca_identificadoratualizacao,"
                    "uca_dataatualizacao"
                )
                valores = (
                        str(identificadorAtual)
                        + "," + str(listaCelular[i]) + ""
                        + "," + str(dadosToken["sub"])
                        + "," + str(dadosToken["sub"])
                        + ",'" + str(agora) + "'"
                )
                dados, retorno, mensagemRetorno = acessoBanco.insereDado("uca_celularadicional", campos, valores)
                if retorno == 400:
                    return mensagemRetorno, retorno, header

        # inclui fixo
        for i in range(len(listaFixo)):
            campo = "max(uta_identificador)"
            dados, retorno, mensagemRetorno = acessoBanco.leDado("uta_telefoneadicional", None, campo)
            if retorno != 200:
                return mensagemRetorno, retorno, header
            if dados[0][0] is None:
                identificadorAtual = 0
            else:
                identificadorAtual = dados[0][0]

            agora = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            campo = "uta_identificador"
            condicao = (
                    " WHERE usu_identificador = " + str(dadosToken["sub"]) +
                    " AND uta_telefone = " + str(listaFixo[i]["numero"]) +
                    " AND uta_ramal = '" + listaFixo[i]["ramal"] + "'"
            )
            dados, retorno, mensagemRetorno = acessoBanco.leDado("uta_telefoneadicional", condicao, campo)
            if retorno == 400:
                return mensagemRetorno, retorno, header
            if retorno == 404:
                identificadorAtual = identificadorAtual + 1
                campos = (
                    "uta_identificador, uta_telefone, uta_ramal,"
                    "usu_identificador, uta_identificadoratualizacao,"
                    "uta_dataatualizacao"
                )
                valores = (
                        str(identificadorAtual)
                        + "," + str(listaFixo[i]["numero"])
                        + ",'" + str(listaFixo[i]["ramal"]) + "'"
                        + "," + str(dadosToken["sub"])
                        + "," + str(dadosToken["sub"])
                        + ",'" + str(agora) + "'"
                )
                dados, retorno, mensagemRetorno = acessoBanco.insereDado("uta_telefoneadicional", campos, valores)
                if retorno == 400:
                    return mensagemRetorno, retorno, header
        return {}, 201, header

    elif request.method == "DELETE":
        if not request.json:
            return {"message": "Dados de entrada não fornecidos"}, 404, header
        entrada = request.json

        listaTelefones = entrada.get("general_phone_others")
        if listaTelefones is None:
            return {"message": "Lista de Telefones obrigatoria"}, 404, header

        retorno, mensagem, listaCelular, listaFixo = validaTelefoneExcluir(listaTelefones)
        if retorno == 404:
            return mensagem, 404, header

        # exclui celular
        for i in range(len(listaCelular)):
            condicao = (
                    " WHERE uca_identificador = " + str(listaCelular[i]) +
                    " AND usu_identificador = " + str(dadosToken["sub"])
            )
            dados, retorno, mensagemRetorno = acessoBanco.exclueDado("uca_celularadicional", condicao)
            if retorno == 400:
                return mensagemRetorno, retorno, header
            elif retorno == 404:
                return {"message": "Identificador de Celular inexistente"}, 404, header

        # exclui fixo
        for i in range(len(listaFixo)):
            condicao = (
                    " WHERE uta_identificador = " + str(listaFixo[i]) +
                    " AND usu_identificador = " + str(dadosToken["sub"])
            )
            dados, retorno, mensagemRetorno = acessoBanco.exclueDado("uta_telefoneadicional", condicao)
            if retorno == 400:
                return mensagemRetorno, retorno, header
            elif retorno == 404:
                return {"message": "Identificador de Telefone Fixo inexistente"}, 404, header

        return {}, 200, header

def emailExclui(id):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 404, {}
    token, dadosToken = gestaoAutenticacao.expandeToken()

    # exclui o elemento
    condicao = " WHERE uea_identificador = " + str(id)  + " AND usu_identificador = " + str(dadosToken["sub"])
    dados, retorno, mensagemRetorno = acessoBanco.exclueDado("uea_emailadicional", condicao)
    if retorno == 400:
        return mensagemRetorno, retorno, header
    elif retorno == 404:
        return {"message": "Identificador inexistente"}, 404, header
    return {}, 200, header

def dicionarioCelular(sub):
    # recupera os celulares adicionais
    codigo = []
    campo = "uca_identificador,uca_celular"
    condicao = "WHERE usu_identificador = " + str(sub)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("uca_celularadicional", condicao, campo)
    if retorno == 400:
        return 400, codigo
    for i in range(len(dados)):
        detalhe = {}
        detalhe['identificador'] = str(dados[i][0])
        detalhe['tipo'] = "celular"
        detalhe['telefone'] = str(dados[i][1])
        detalhe["ramal"] = ""
        codigo.append(detalhe)
    return 200, codigo

def dicionarioEmail(sub):
    # recupera os emails adicionais
    codigo = []
    campo = "uea_identificador,uea_email"
    condicao = "WHERE usu_identificador = " + str(sub)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("uea_emailadicional", condicao, campo)
    if retorno == 400:
        return 400, codigo
    for i in range(len(dados)):
        detalhe = {}
        detalhe['identificador'] = str(dados[i][0])
        detalhe['email'] = str(dados[i][1])
        codigo.append(detalhe)
    return 200, codigo

def dicionarioTelefone(sub):
    # recupera os telefones adicionais
    codigo = []
    campo = "uta_identificador,uta_telefone, uta_ramal"
    condicao = "WHERE usu_identificador = " + str(sub)
    dados, retorno, mensagemRetorno = acessoBanco.leDado("uta_telefoneadicional", condicao, campo)
    if retorno == 400:
        return 400, codigo
    if len(dados) == 0:
        return 200, codigo
    for i in range(len(dados)):
        detalhe = {}
        detalhe['identificador'] = str(dados[i][0])
        detalhe['tipo'] = "fixo"
        detalhe['telefone'] = str(dados[i][1])
        detalhe["ramal"] = str(dados[i][2])
        codigo.append(detalhe)
    return 200, codigo

def validaTelefone(listaTelefones):

    erro = False
    cheque = {}
    listaCelular = []
    listaFixo = []

    for i in range(len(listaTelefones)):
        if not "tipo" in listaTelefones[i] or listaTelefones[i]["tipo"] not in ("celular","fixo"):
            if not erro:
                cheque["message"] = "Registro " + str(i+1) + " - Tipo deve ser 'celular' ou 'fixo'"
            else:
                cheque["message"] = cheque["message"] + " # Registro " + str(i+1) + " - Tipo deve ser 'celular' ou 'fixo'"
            erro = True

        if not "numero" in listaTelefones[i] or not acessoBanco.inteiro(listaTelefones[i]["numero"]):
            if not erro:
                cheque["message"] = "Registro " + str(i+1) + " - Número do telefone inválido"
            else:
                cheque["message"] = cheque["message"] + " # Registro " + str(i+1) + " - Número do telefone inválido"
            erro = True

    if erro:
            return 404, cheque, listaCelular, listaFixo

    for i in range(len(listaTelefones)):
        if listaTelefones[i]["tipo"] == "celular":
            listaCelular.append(int(listaTelefones[i]["numero"]))
        else:
            detalhe = {}
            detalhe["numero"] = listaTelefones[i]["numero"]
            if "ramal" in listaTelefones[i]:
                detalhe["ramal"] = listaTelefones[i]["ramal"]
            else:
                detalhe["ramal"] = ""
            listaFixo.append(detalhe)

    return 200, {}, listaCelular, listaFixo

def validaTelefoneExcluir(listaTelefones):

    erro = False
    cheque = {}
    listaCelular = []
    listaFixo = []

    for i in range(len(listaTelefones)):
        if not "tipo" in listaTelefones[i] or listaTelefones[i]["tipo"] not in ("celular","fixo"):
            if not erro:
                cheque["message"] = "Registro " + str(i+1) + " - Tipo deve ser 'celular' ou 'fixo'"
            else:
                cheque["message"] = cheque["message"] + " # Registro " + str(i+1) + " - Tipo deve ser 'celular' ou 'fixo'"
            erro = True

        if not "identificador" in listaTelefones[i] or not acessoBanco.inteiro(listaTelefones[i]["identificador"]):
            if not erro:
                cheque["message"] = "Registro " + str(i+1) + " - Identificador inválido"
            else:
                cheque["message"] = cheque["message"] + " # Registro " + str(i+1) + " - Identificador inválido"
            erro = True

    if erro:
            return 404, cheque, listaCelular, listaFixo


    for i in range(len(listaTelefones)):
        if listaTelefones[i]["tipo"] == "celular":
            listaCelular.append(int(listaTelefones[i]["identificador"]))
        else:
            listaFixo.append(int(listaTelefones[i]["identificador"]))

    return 200, {}, listaCelular, listaFixo