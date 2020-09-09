# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request
import datetime


def organizacaoGeral():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem["message"])
        return resultadoFinal, 400, header

    # realiza consulta no banco - grupo economico
    camposDesejados = "gec_identificador,gec_nome"
    dados, retorno, mensagemRetorno = acessoBanco.dado("gec_grupoeconomico", None, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header
    resultadoFinal["grupoeconomico"] = dados

    # realiza consulta no banco - companhia
    camposDesejados = "cia_identificador,cia_nome"
    dados, retorno, mensagemRetorno = acessoBanco.dado("cia_companhia", None, camposDesejados, None)
    if retorno != 200:
        return resultadoFinal, retorno, header
    resultadoFinal["companhia"] = dados

    # realiza consulta no banco - empreendimento
    camposDesejados = "emp_identificador,emp_nome"
    dados, retorno, mensagemRetorno = acessoBanco.dado("emp_empreendimento", None, camposDesejados, None)
    if retorno != 200:
        return resultadoFinal, retorno, header
    resultadoFinal["empreendimento"] = dados

    return resultadoFinal, retorno, header


def organizacaoCadastrado():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem["message"])
        return resultadoFinal, 400, header

    query_parameters = request.args
    nivel = query_parameters.get("nivel")
    nome = query_parameters.get("nome")

    if nivel is None or nome is None:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Nivel ou Nome não fornecido(s)"
        resultadoFinal = acessoBanco.montaRetorno(400, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = " "
        return resultadoFinal, 400, header

    resultado = acessoBanco.montaRetorno(200, "")
    if nivel == "grupoeconomico":
        condicao = "WHERE gec_nome = '" + nome + "'"
        resultadoFinal = montaGrupo(condicao, resultado, True)
    elif nivel == "companhia":
        condicao = "WHERE cia_nome = '" + nome + "'"
        resultadoFinal = montaCompanhia(condicao, resultado, True, True)
    elif nivel == "empreendimento":
        condicao = "WHERE emp_nome = '" + nome + "'"
        resultadoFinal = montaEmpreendimento(condicao, resultado, True)
    else:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Nivel " + nivel + " é inválido."
        resultadoFinal = acessoBanco.montaRetorno(400, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = " "
        return resultadoFinal, 400, header

    return resultadoFinal, 200, header


def organizacaoExcluido():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem["message"])
        return resultadoFinal, 400, header

    query_parameters = request.args
    nivel = query_parameters.get("nivel")
    nome = query_parameters.get("nome")

    if nivel is None or nome is None:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Nivel ou Nome não fornecido(s)"
        resultadoFinal = acessoBanco.montaRetorno(400, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = " "
        return resultadoFinal, 400, header

    resultado = acessoBanco.montaRetorno(200, "")
    if nivel == "grupoeconomico":
        condicao = "WHERE gec_nome = '" + nome + "'"
        # realiza consulta no banco - grupo economico
        camposDesejados = "gec_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.dado("gec_grupoeconomico", condicao, camposDesejados, None)
        if retorno != 200:
            resultadoGEC = []
            return resultadoGEC, retorno, header

        # recupera as companhias do grupo
        condicao = "WHERE gec_identificador in ("
        for i in range(len(dados)):
            condicao = condicao + str(dados[i]["gec_identificador"]) + ","
        condicao = condicao[0:-1] + ")"
        dados, retorno, mensagemRetorno = acessoBanco.dado("gec_cia_grupoeconomico_companhia", condicao, None, None)
        if retorno != 200:
            return resultado, retorno, header
        if dados != []:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Grupo econômico possui Companhia(s). Delete-a(s) previamente."
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header
        # deleta
        dados, retorno, mensagemRetorno = acessoBanco.exclueDado("gec_grupoeconomico", condicao)
        if retorno != 200:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Grupo Econômico não excluido."
            resultadoFinal = acessoBanco.montaRetorno(retorno, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, retorno, header
        else:
            listaMensagem = {}
            listaMensagem["acesso"] = "ok"
            listaMensagem["texto"] = "Grupo Econômico excluido."
            resultadoFinal = acessoBanco.montaRetorno(200, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 200, header

    elif nivel == "companhia":
        condicao = "WHERE cia_nome = '" + nome + "'"
        # realiza consulta no banco - companhia
        camposDesejados = "cia_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.dado("cia_companhia", condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        # recupera os empreendimentos da cia
        condicao = "WHERE cia_identificador in ("
        for i in range(len(dados)):
            condicao = condicao + str(dados[i]["cia_identificador"]) + ","
        condicao = condicao[0:-1] + ")"
        dados, retorno, mensagemRetorno = acessoBanco.dado("emp_empreendimento", condicao, None, None)
        if retorno != 200:
            return resultado, retorno, header
        if dados != []:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Companhia possui Empreendimento(s). Delete-o(s) previamente."
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header

        # deleta
        tabela = []
        condicaoNecessaria = []
        tabela.append("gec_cia_grupoeconomico_companhia")
        condicaoNecessaria.append(condicao)
        tabela.append("cia_companhia")
        condicaoNecessaria.append(condicao)

        dados, retorno, mensagemRetorno = acessoBanco.exclueDadoMultiplo(tabela, condicaoNecessaria)
        if retorno != 200:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Companhia não excluida."
            resultadoFinal = acessoBanco.montaRetorno(retorno, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, retorno, header

        else:
            listaMensagem = {}
            listaMensagem["acesso"] = "ok"
            listaMensagem["texto"] = "Companhia excluida."
            resultadoFinal = acessoBanco.montaRetorno(200, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 200, header

    elif nivel == "empreendimento":
        tabela = []
        condicaoNecessaria = []
        condicao = "WHERE emp_nome = '" + nome + "'"
        # realiza consulta no banco - empreendimento
        camposDesejados = "emp_identificador"
        dadosEmp, retorno, mensagemRetorno = acessoBanco.dado("emp_empreendimento", condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        # deleta os PAEs do empreendimento
        condicao = "WHERE emp_identificador in ("
        for i in range(len(dadosEmp)):
            condicao = condicao + str(dadosEmp[i]["emp_identificador"]) + ","
        condicao = condicao[0:-1] + ")"
        tabela.append("pae_planoacaoemergencia")
        condicaoNecessaria.append(condicao)

        # deleta empreendimento
        tabela.append("emp_empreendimento")
        condicaoNecessaria.append(condicao)
        dados, retorno, mensagemRetorno = acessoBanco.exclueDadoMultiplo(tabela, condicaoNecessaria)

        if retorno != 200:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem[
                "texto"
            ] = "Empreendimento não excluído. Verifique se possui PAE ativo e delete-o previamente."
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header
        else:
            listaMensagem = {}
            listaMensagem["acesso"] = "ok"
            listaMensagem["texto"] = "Empreendimento excluído."
            resultadoFinal = acessoBanco.montaRetorno(200, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 200, header
    else:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Nivel " + nivel + " é inválido."
        resultadoFinal = acessoBanco.montaRetorno(400, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = " "
        return resultadoFinal, 400, header


def organizacaoIncluido():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem["message"])
        return resultadoFinal, 400, header

    codificado, volta = gestaoAutenticacao.expandeToken()
    atual_usuario = volta["sub"]
    atual_data = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    query_parameters = request.args
    nivel = query_parameters.get("nivel")
    nome = query_parameters.get("nome")
    superior = query_parameters.get("superior")
    pae = query_parameters.get("pae")
    tipo = query_parameters.get("tipo")
    sigla = query_parameters.get("sigla")

    if nivel is None or nome is None:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Nivel ou Nome não fornecido(s)"
        resultadoFinal = acessoBanco.montaRetorno(400, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = " "
        return resultadoFinal, 400, header

    resultado = acessoBanco.montaRetorno(200, "")
    if nivel == "grupoeconomico":
        condicao = "WHERE gec_nome = '" + nome + "'"
        # realiza consulta no banco - grupo economico
        camposDesejados = "gec_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.dado("gec_grupoeconomico", condicao, camposDesejados, None)
        if retorno != 200:
            resultadoGEC = []
            return resultadoGEC, retorno, header

        if dados != []:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Já existe Grupo Econômico com este nome."
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header

        # inclui
        campo = "max(gec_identificador)"
        dados, retorno, mensagemRetorno = acessoBanco.leDado("gec_grupoeconomico", None, campo)
        if retorno != 200:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        proximoNumero = dados[0][0] + 1

        campos = "gec_identificador, gec_nome, gec_identificadoratualizacao, gec_dataatualizacao"
        valores = str(proximoNumero) + ",'" + nome + "'," + str(atual_usuario) + ",'" + atual_data + "'"
        dados, retorno, mensagemRetorno = acessoBanco.insereDado("gec_grupoeconomico", campos, valores)
        if retorno != 201:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        gecIncluido = {}
        gecIncluido["gec_identificador"] = proximoNumero
        resposta = acessoBanco.montaRetorno(201, "")
        resposta["aresposta"]["texto"] = ""
        resposta["retorno"] = gecIncluido
        return resposta, 201, header

    elif nivel == "companhia":
        if superior is None:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Nivel Superior não fornecido(s)"
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header

        condicao = "WHERE cia_nome = '" + nome + "'"
        # realiza consulta no banco - companhia
        camposDesejados = "cia_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.dado("cia_companhia", condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados != []:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Companhia já existente."
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header

        # verifica se o Grupo Econômico existe
        camposDesejados = "gec_identificador"
        condicao = "WHERE gec_nome = '" + superior + "'"
        dados, retorno, mensagemRetorno = acessoBanco.dado("gec_grupoeconomico", condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados == []:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Grupo Econômico inexistente"
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header
        gec_identificador = dados[0]["gec_identificador"]

        # inclui
        campo = "max(cia_identificador)"
        dados, retorno, mensagemRetorno = acessoBanco.leDado("cia_companhia", None, campo)
        if retorno != 200:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        if dados == []:
            proximoNumero = 1
        else:
            proximoNumero = dados[0][0] + 1

        tabela = []
        campos = []
        valores = []

        campos.append("cia_identificador, cia_nome, cia_identificadoratualizacao, cia_dataatualizacao")
        valores.append(str(proximoNumero) + ",'" + nome + "'," + str(atual_usuario) + ",'" + atual_data + "'")
        tabela.append("cia_companhia")

        campos.append(
            "cia_identificador, gec_identificador, gec_cia_identificadoratualizacao, gec_cia_dataatualizacao"
        )
        valores.append(
            str(proximoNumero) + "," + str(gec_identificador) + "," + str(atual_usuario) + ",'" + atual_data + "'"
        )
        tabela.append("gec_cia_grupoeconomico_companhia")
        dados, retorno, mensagemRetorno = acessoBanco.insereDadoMultiplo(tabela, campos, valores)
        if retorno != 201:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        ciaIncluido = {}
        ciaIncluido["cia_identificador"] = proximoNumero
        resposta = acessoBanco.montaRetorno(201, "")
        resposta["aresposta"]["texto"] = ""
        resposta["retorno"] = ciaIncluido
        return resposta, 201, header

    elif nivel == "empreendimento":

        if superior is None or tipo is None or pae is None or sigla is None:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem[
                "texto"
            ] = "Nivel Superior, Tipo do Empreendimento, Sigla e/ou Ativação do PAE não fornecido(s)"
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header

        if tipo not in ("UHE", "PCH"):
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Tipo de Empreendimento Invalido"
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header

        if pae not in ("S", "N"):
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Ativação de PAE Invalido"
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header

        condicao = "WHERE emp_nome = '" + nome + "' or emp_sigla = '" + sigla + "'"
        # realiza consulta no banco - empreendimento
        camposDesejados = "emp_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.dado("emp_empreendimento", condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados != []:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Nome e/ou Sigla do Empreendimento já existente(s)."
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header

        # verifica se a companhia existe
        camposDesejados = "cia_identificador"
        condicao = "WHERE cia_nome = '" + superior + "'"
        dados, retorno, mensagemRetorno = acessoBanco.dado("cia_companhia", condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados == []:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Companhia inexistente"
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header
        cia_identificador = dados[0]["cia_identificador"]

        # inclui
        campo = "max(emp_identificador)"
        dados, retorno, mensagemRetorno = acessoBanco.leDado("emp_empreendimento", None, campo)
        if retorno != 200:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        if dados == []:
            proximoEmpreendimento = 1
        else:
            proximoEmpreendimento = dados[0][0] + 1

        tabela = []
        campos = []
        valores = []

        campos.append(
            "emp_identificador, emp_nome, cia_identificador, emp_tipo, emp_sigla, emp_identificadoratualizacao, "
            + "emp_dataatualizacao"
        )
        valores.append(
            str(proximoEmpreendimento)
            + ",'"
            + nome
            + "',"
            + str(cia_identificador)
            + ",'"
            + tipo
            + "','"
            + sigla
            + "',"
            + str(atual_usuario)
            + ",'"
            + atual_data
            + "'"
        )
        tabela.append("emp_empreendimento")

        if pae == "S":
            campo = "max(pae_identificador)"
            dados, retorno, mensagemRetorno = acessoBanco.leDado("pae_planoacaoemergencia", None, campo)
            if retorno != 200:
                resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
                return resultadoFinal, retorno, header

            if dados == []:
                proximoNumero = 1
            else:
                proximoNumero = dados[0][0] + 1

            texto_pae = "PAE - " + sigla
            campos.append(
                "pae_identificador, emp_identificador, pae_texto, pae_identificadoratualizacao, pae_dataatualizacao"
            )
            valores.append(
                str(proximoNumero)
                + ","
                + str(proximoEmpreendimento)
                + ",'"
                + texto_pae
                + "',"
                + str(atual_usuario)
                + ",'"
                + atual_data
                + "'"
            )
            tabela.append("pae_planoacaoemergencia")

        dados, retorno, mensagemRetorno = acessoBanco.insereDadoMultiplo(tabela, campos, valores)
        if retorno != 201:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        empIncluido = {}
        empIncluido["emp_identificador"] = proximoEmpreendimento
        resposta = acessoBanco.montaRetorno(201, "")
        resposta["aresposta"]["texto"] = ""
        resposta["retorno"] = empIncluido
        return resposta, 201, header
    else:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Nivel " + nivel + " é inválido."
        resultadoFinal = acessoBanco.montaRetorno(400, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = " "
        return resultadoFinal, 400, header


def organizacaoAlterado():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(400, mensagem["message"])
        return resultadoFinal, 400, header

    codificado, volta = gestaoAutenticacao.expandeToken()
    atual_usuario = volta["sub"]
    atual_data = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    query_parameters = request.args
    nivel = query_parameters.get("nivel")
    nome = query_parameters.get("nome")
    novonome = query_parameters.get("novonome")
    superior = query_parameters.get("novosuperior")
    pae = query_parameters.get("novopae")
    tipo = query_parameters.get("novotipo")
    sigla = query_parameters.get("novasigla")

    if nivel is None or nome is None:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Nivel e/ou Nome não fornecido(s)"
        resultadoFinal = acessoBanco.montaRetorno(400, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = " "
        return resultadoFinal, 400, header

    resultado = acessoBanco.montaRetorno(200, "")
    if nivel == "grupoeconomico":
        if novonome is None:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Nada a alterar em Grupo Econômico"
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header

        # realiza consulta no banco - grupo economico
        condicao = "WHERE gec_nome = '" + nome + "'"
        camposDesejados = "gec_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.dado("gec_grupoeconomico", condicao, camposDesejados, None)
        if retorno != 200:
            resultadoGEC = []
            return resultadoGEC, retorno, header

        if dados == []:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Não existe Grupo Econômico com nome fornecido."
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header

        camposDesejados = "gec_identificador"
        condicao = "WHERE gec_nome = '" + novonome + "'"
        dados, retorno, mensagemRetorno = acessoBanco.dado("gec_grupoeconomico", condicao, camposDesejados, None)
        if retorno != 200:
            resultadoGEC = []
            return resultadoGEC, retorno, header

        if dados != []:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Já existe Grupo Econômico com novo nome fornecido."
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header
        # altera
        comando = (
            "gec_nome = '"
            + novonome
            + "', gec_identificadoratualizacao = "
            + str(atual_usuario)
            + ", gec_dataatualizacao = '"
            + atual_data
            + "'"
        )
        condicao = "WHERE gec_nome = '" + nome + "'"
        dados, retorno, mensagemRetorno = acessoBanco.alteraDado("gec_grupoeconomico", comando, condicao)
        if retorno != 200:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        gecAlterado = {}
        gecAlterado["gec_nome"] = novonome
        resposta = acessoBanco.montaRetorno(200, "")
        resposta["aresposta"]["texto"] = ""
        resposta["retorno"] = gecAlterado
        return resposta, 200, header

    elif nivel == "companhia":
        comando_gec = ""
        if superior is not None:
            # verifica se existe grupo economico com o nome indicado
            condicao = "WHERE gec_nome = '" + superior + "'"
            camposDesejados = "gec_identificador"
            dados, retorno, mensagemRetorno = acessoBanco.dado("gec_grupoeconomico", condicao, camposDesejados, None)
            if retorno != 200:
                resultadoGEC = []
                return resultadoGEC, retorno, header

            if dados == []:
                listaMensagem = {}
                listaMensagem["acesso"] = "nok"
                listaMensagem["texto"] = "Não existe Grupo Econômico com nome fornecido."
                resultadoFinal = acessoBanco.montaRetorno(400, "")
                resultadoFinal["retorno"] = listaMensagem
                resultadoFinal["aresposta"]["texto"] = " "
                return resultadoFinal, 400, header
            gec_identificador = dados[0]["gec_identificador"]
            comando_gec = ", gec_identificador = " + str(gec_identificador)

        # realiza consulta no banco - companhia
        condicao = "WHERE cia_nome = '" + nome + "'"
        camposDesejados = "cia_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.dado("cia_companhia", condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados == []:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Companhia inexistente."
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header
        cia_identificador = dados[0]["cia_identificador"]

        # verifica se o novo nome existe
        comando_novonome = ""
        if novonome is not None:
            condicao = "WHERE cia_nome = '" + novonome + "'"
            camposDesejados = "cia_identificador"
            dados, retorno, mensagemRetorno = acessoBanco.dado("cia_companhia", condicao, camposDesejados, None)
            if retorno != 200:
                resultado = []
                return resultado, retorno, header

            if dados != []:
                listaMensagem = {}
                listaMensagem["acesso"] = "nok"
                listaMensagem["texto"] = "Novo nome para Companhia já existente."
                resultadoFinal = acessoBanco.montaRetorno(400, "")
                resultadoFinal["retorno"] = listaMensagem
                resultadoFinal["aresposta"]["texto"] = " "
                return resultadoFinal, 400, header
            comando_novonome = ", cia_nome = '" + novonome + "'"

        # altera companhia
        tabela = []
        comandoNecessario = []
        condicaoNecessaria = []
        altera = False
        comando = comando_novonome
        if len(comando) > 4:
            comando = comando[1:]
            condicao = "WHERE cia_nome = '" + nome + "'"
            tabela.append("cia_companhia")
            comandoNecessario.append(comando)
            condicaoNecessaria.append(condicao)
            altera = True
        # altera relacao com grupo economico
        comando = comando_gec
        if len(comando) > 4:
            comando = (
                comando[1:]
                + ", cia_identificadoratualizacao = "
                + str(atual_usuario)
                + ", cia_dataatualizacao = '"
                + atual_data
                + "'"
            )
            condicao = "WHERE cia_identificador = " + str(cia_identificador)
            tabela.append("gec_cia_grupoeconomico_companhia")
            comandoNecessario.append(comando)
            condicaoNecessaria.append(condicao)
            altera = True
        if altera:
            dados, retorno, mensagemRetorno = acessoBanco.alteraDadoMultiplo(
                tabela, comandoNecessario, condicaoNecessaria
            )
            if retorno != 200:
                resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
                return resultadoFinal, retorno, header

        ciaAlterado = {}
        ciaAlterado["cia_nome"] = nome
        resposta = acessoBanco.montaRetorno(200, "")
        resposta["aresposta"]["texto"] = ""
        resposta["retorno"] = ciaAlterado
        return resposta, 200, header

    elif nivel == "empreendimento":

        comando_companhia = ""
        if superior is not None:
            # verifica se existe companhia com o nome indicado
            condicao = "WHERE cia_nome = '" + superior + "'"
            camposDesejados = "cia_identificador"
            dados, retorno, mensagemRetorno = acessoBanco.dado("cia_companhia", condicao, camposDesejados, None)
            if retorno != 200:
                resultadoCIA = []
                return resultadoCIA, retorno, header

            if dados == []:
                listaMensagem = {}
                listaMensagem["acesso"] = "nok"
                listaMensagem["texto"] = "Não existe Companhia com nome fornecido."
                resultadoFinal = acessoBanco.montaRetorno(400, "")
                resultadoFinal["retorno"] = listaMensagem
                resultadoFinal["aresposta"]["texto"] = " "
                return resultadoFinal, 400, header
            cia_identificador = dados[0]["cia_identificador"]
            comando_companhia = ", cia_identificador = " + str(cia_identificador)

        comando_tipo = ""
        if tipo is not None:
            if tipo not in ("UHE", "PCH"):
                listaMensagem = {}
                listaMensagem["acesso"] = "nok"
                listaMensagem["texto"] = "Tipo do Empreendimento Inválido"
                resultadoFinal = acessoBanco.montaRetorno(400, "")
                resultadoFinal["retorno"] = listaMensagem
                resultadoFinal["aresposta"]["texto"] = " "
                return resultadoFinal, 400, header
            else:
                comando_tipo = ", emp_tipo = '" + tipo + "'"

        if pae is not None:
            if pae not in ("S", "N"):
                listaMensagem = {}
                listaMensagem["acesso"] = "nok"
                listaMensagem["texto"] = "Ativação de PAE Invalido"
                resultadoFinal = acessoBanco.montaRetorno(400, "")
                resultadoFinal["retorno"] = listaMensagem
                resultadoFinal["aresposta"]["texto"] = " "
                return resultadoFinal, 400, header

        # realiza consulta no banco - empreendimento
        condicao = "WHERE emp_nome = '" + nome + "'"
        camposDesejados = "emp_identificador"
        dados, retorno, mensagemRetorno = acessoBanco.dado("emp_empreendimento", condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados == []:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Empreendimento inexistente."
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header
        emp_identificador = dados[0]["emp_identificador"]

        # verifica se o novo nome existe
        comando_novonome = ""
        if novonome is not None:
            condicao = "WHERE emp_nome = '" + novonome + "'"
            camposDesejados = "emp_identificador"
            dados, retorno, mensagemRetorno = acessoBanco.dado("emp_empreendimento", condicao, camposDesejados, None)
            if retorno != 200:
                resultado = []
                return resultado, retorno, header

            if dados != []:
                listaMensagem = {}
                listaMensagem["acesso"] = "nok"
                listaMensagem["texto"] = "Novo nome para Empreendimento já existente."
                resultadoFinal = acessoBanco.montaRetorno(400, "")
                resultadoFinal["retorno"] = listaMensagem
                resultadoFinal["aresposta"]["texto"] = " "
                return resultadoFinal, 400, header
            comando_novonome = ", emp_nome = '" + novonome + "'"

        # verifica se a nova sigla existe
        comando_novasigla = ""
        if sigla is not None:
            condicao = "WHERE emp_sigla = '" + sigla + "'"
            camposDesejados = "emp_identificador"
            dados, retorno, mensagemRetorno = acessoBanco.dado("emp_empreendimento", condicao, camposDesejados, None)
            if retorno != 200:
                resultado = []
                return resultado, retorno, header

            if dados != []:
                listaMensagem = {}
                listaMensagem["acesso"] = "nok"
                listaMensagem["texto"] = "Nova sigla para Empreendimento já existente."
                resultadoFinal = acessoBanco.montaRetorno(400, "")
                resultadoFinal["retorno"] = listaMensagem
                resultadoFinal["aresposta"]["texto"] = " "
                return resultadoFinal, 400, header
            comando_novasigla = ", emp_sigla = '" + sigla + "'"

        # altera
        tabela = []
        comandoNecessario = []
        condicaoNecessaria = []
        altera = False

        comando = comando_tipo + comando_companhia + comando_novonome + comando_novasigla

        if len(comando) > 4:
            comando = (
                comando[1:]
                + ", emp_identificadoratualizacao = "
                + str(atual_usuario)
                + ", emp_dataatualizacao = '"
                + atual_data
                + "'"
            )
            condicao = "WHERE emp_nome = '" + nome + "'"
            linha = "UPDATE emp_empreendimento SET " + comando + " " + condicao
            comandoNecessario.append(linha)
            altera = True

        if pae is not None:
            # verifica se existe pae com o nome indicado
            condicao = "WHERE emp_identificador = " + str(emp_identificador)
            camposDesejados = "pae_identificador"
            dados, retorno, mensagemRetorno = acessoBanco.dado(
                "pae_planoacaoemergencia", condicao, camposDesejados, None
            )

            if retorno != 200:
                resultado = []
                return resultado, retorno, header
            if dados == []:
                existePae = False
            else:
                existePae = True
                pae_identificador = dados[0]["pae_identificador"]

            if pae == "S":
                if not existePae:
                    campo = "max(pae_identificador)"
                    dados, retorno, mensagemRetorno = acessoBanco.leDado("pae_planoacaoemergencia", None, campo)
                    if retorno != 200:
                        resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
                        return resultadoFinal, retorno, header

                    if dados == []:
                        proximoNumero = 1
                    else:
                        proximoNumero = dados[0][0] + 1

                    texto_pae = "PAE - " + sigla
                    linha = (
                        "INSERT INTO pae_planoacaoemergencia "
                        + "(pae_identificador, emp_identificador, pae_texto, pae_identificadoratualizacao, "
                        + "pae_dataatualizacao) VALUES ("
                        + str(proximoNumero)
                        + ","
                        + str(emp_identificador)
                        + ",'"
                        + texto_pae
                        + "',"
                        + str(atual_usuario)
                        + ",'"
                        + atual_data
                        + "')"
                    )
                    comandoNecessario.append(linha)
                    altera = True
            elif pae == "N":
                if existePae:
                    linha = "DELETE FROM pae_planoacaoemergencia WHERE pae_identificador = " + str(pae_identificador)
                    comandoNecessario.append(linha)
                    altera = True

        if altera:
            dados, retorno, mensagemRetorno = acessoBanco.executaDadoMultiplo(comandoNecessario)
            if retorno != 200:
                resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
                return resultadoFinal, retorno, header
        else:
            listaMensagem = {}
            listaMensagem["acesso"] = "nok"
            listaMensagem["texto"] = "Nada a ser alterado."
            resultadoFinal = acessoBanco.montaRetorno(400, "")
            resultadoFinal["retorno"] = listaMensagem
            resultadoFinal["aresposta"]["texto"] = " "
            return resultadoFinal, 400, header

        empAlterado = {}
        empAlterado["emp_nome"] = nome
        resposta = acessoBanco.montaRetorno(200, "")
        resposta["aresposta"]["texto"] = ""
        resposta["retorno"] = empAlterado
        return resposta, 200, header

    else:
        listaMensagem = {}
        listaMensagem["acesso"] = "nok"
        listaMensagem["texto"] = "Nivel " + nivel + " é inválido."
        resultadoFinal = acessoBanco.montaRetorno(400, "")
        resultadoFinal["retorno"] = listaMensagem
        resultadoFinal["aresposta"]["texto"] = " "
        return resultadoFinal, 400, header


def montaGrupo(condicao, resultado, propagaFilho):
    # realiza consulta no banco - grupo economico
    camposDesejados = "gec_identificador,gec_nome"
    dados, retorno, mensagemRetorno = acessoBanco.dado("gec_grupoeconomico", condicao, camposDesejados, None)
    if retorno != 200:
        resultadoGEC = []
        return resultadoGEC
    resultado["grupoeconomico"] = dados

    # testa para ver se recupera os filhos
    if not propagaFilho:
        return resultado

    # recupera as companhias do grupo
    condicao = "WHERE gec_identificador in ("
    for i in range(len(dados)):
        condicao = condicao + str(dados[i]["gec_identificador"]) + ","
    condicao = condicao[0:-1] + ")"
    dados, retorno, mensagemRetorno = acessoBanco.dado("gec_cia_grupoeconomico_companhia", condicao, None, None)
    if retorno != 200:
        return resultado
    condicao = "WHERE cia_identificador in ("
    for i in range(len(dados)):
        condicao = condicao + str(dados[i]["cia_identificador"]) + ","
    condicao = condicao[0:-1] + ")"
    resultadoFinal = montaCompanhia(condicao, resultado, True, False)
    return resultadoFinal


def montaCompanhia(condicao, resultado, propagaFilho, propagaPai):
    # realiza consulta no banco - companhia

    camposDesejados = "cia_identificador,cia_nome"
    dadosCia, retorno, mensagemRetorno = acessoBanco.dado("cia_companhia", condicao, camposDesejados, None)

    if retorno != 200:
        resultadoFinal = []
        return resultadoFinal
    resultado["companhia"] = dadosCia

    # verifica se propaga os filhos
    if propagaFilho:
        condicao = "WHERE cia_identificador in ("
        for i in range(len(dadosCia)):
            condicao = condicao + str(dadosCia[i]["cia_identificador"]) + ","
        condicao = condicao[0:-1] + ")"
        resultado = montaEmpreendimento(condicao, resultado, False)

    # verifica se recupera os pais
    if propagaPai:
        condicao = "WHERE cia_identificador in ("
        for i in range(len(dadosCia)):
            condicao = condicao + str(dadosCia[i]["cia_identificador"]) + ","
        condicao = condicao[0:-1] + ")"
        dados, retorno, mensagemRetorno = acessoBanco.dado("gec_cia_grupoeconomico_companhia", condicao, None, None)
        if retorno != 200:
            return resultado
        condicao = "WHERE gec_identificador in ("
        for i in range(len(dados)):
            condicao = condicao + str(dados[i]["gec_identificador"]) + ","
        condicao = condicao[0:-1] + ")"
        resultado = montaGrupo(condicao, resultado, False)
    return resultado


def montaEmpreendimento(condicao, resultado, propagaPai):
    # realiza consulta no banco - companhia

    camposDesejados = "emp_identificador,emp_nome,emp_tipo,cia_identificador"
    dados, retorno, mensagemRetorno = acessoBanco.dado("emp_empreendimento", condicao, camposDesejados, None)
    if retorno != 200:
        resultadoFinal = []
        return resultadoFinal
    resultado["empreendimento"] = dados

    # verifica se propaga os pais
    if propagaPai:
        condicao = "WHERE cia_identificador in ("
        for i in range(len(dados)):
            condicao = condicao + str(dados[i]["cia_identificador"]) + ","
        condicao = condicao[0:-1] + ")"
        resultado = montaCompanhia(condicao, resultado, False, True)
    return resultado
