# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request
import datetime
from math import sqrt


def rotasOrdenadas(uhe):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ""

    camposDesejados = "pae_identificador"
    condicao = "WHERE emp_identificador = " + str(uhe)
    dadosPAE, retorno, mensagemRetorno = acessoBanco.leDado("pae_planoacaoemergencia", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPAE) == 0:
        return {"rotas": []}, 200, header

    camposDesejados = "rot_identificador,rot_texto"
    condicao = "WHERE pae_identificador = " + str(dadosPAE[0][0])
    dadosRota, retorno, mensagemRetorno = acessoBanco.leDado("rot_rotaevacuacao", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosRota) == 0:
        return {"rotas": []}, 200, header

    corpoMensagem = {}
    montaRota = []

    for i in range(len(dadosRota)):
        trecho = []
        trecho_anterior = []
        trecho_nome = {}
        mensagemRota = {}
        mensagemRota["id_rota"] = int(dadosRota[i][0])
        mensagemRota["nome_rota"] = dadosRota[i][1]

        camposDesejados = "rot_tro_rotaevacuacao_trechorotaevacuacao.tro_identificador, tro_anterior, tro_logradouro"
        condicao = (
            "INNER JOIN tro_trechorotaevacuacao ON "
            + "rot_tro_rotaevacuacao_trechorotaevacuacao.tro_identificador =  tro_trechorotaevacuacao.tro_identificador"
            + " WHERE rot_tro_rotaevacuacao_trechorotaevacuacao.rot_identificador ="
            + str(dadosRota[i][0])
        )
        dadosTrecho, retorno, mensagemRetorno = acessoBanco.leDado(
            "rot_tro_rotaevacuacao_trechorotaevacuacao", condicao, camposDesejados
        )

        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header

        if len(dadosTrecho) == 0:
            temTrecho = False
            mensagemRota["trechos"] = []
        else:
            temTrecho = True
            for j in range(len(dadosTrecho)):
                trecho.append(dadosTrecho[j][0])
                trecho_anterior.append(dadosTrecho[j][1])
                trecho_nome[dadosTrecho[j][0]] = dadosTrecho[j][2]

        camposDesejados = (
            "rot_pns_rotaevacuacao_pontoseguranca.pns_identificador, "
            + "pns_identificacao,ST_AsText(pns_pontoseguranca.geom), "
            + "ST_AsText(ST_Transform(pns_pontoseguranca.geom,4326))"
        )
        condicao = (
            "INNER JOIN pns_pontoseguranca ON "
            + "rot_pns_rotaevacuacao_pontoseguranca.pns_identificador = pns_pontoseguranca.pns_identificador "
            + "WHERE rot_pns_rotaevacuacao_pontoseguranca.rot_identificador = "
            + str(dadosRota[i][0])
        )
        dadosPonto, retorno, mensagemRetorno = acessoBanco.leDado(
            "rot_pns_rotaevacuacao_pontoseguranca", condicao, camposDesejados
        )

        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header

        if len(dadosPonto) == 0:
            temPS = False
            mensagemRota["ponto_seguranca"] = []
        else:
            temPS = True
            detalhePontos = {}
            detalhePontos["id_ponto"] = int(dadosPonto[0][0])
            detalhePontos["nome_ponto"] = dadosPonto[0][1]
            x = dadosPonto[0][2].split(" ")[0][6:]
            y = dadosPonto[0][2].split(" ")[1][:-1]
            detalhePontos["x"] = float(x)
            detalhePontos["y"] = float(y)
            lat = dadosPonto[0][3].split(" ")[1][:-1]
            long = dadosPonto[0][3].split(" ")[0][6:]
            detalhePontos["lat"] = float(lat)
            detalhePontos["long"] = float(long)
            mensagemRota["ponto_seguranca"] = detalhePontos

        sequencia = 0
        montaTrecho = []

        if temTrecho:
            nivel = ordena(trecho, trecho_anterior)
            for m in sorted(set(nivel.values())):
                for n in nivel.keys():
                    if nivel[n] == m:
                        mensagemTrechos = {}
                        sequencia = sequencia + 1
                        mensagemTrechos["id_trecho"] = int(n)
                        mensagemTrechos["sequencia_trecho"] = int(sequencia)
                        mensagemTrechos["nome_trecho"] = trecho_nome[n]
                        montaTrecho.append(mensagemTrechos)

            mensagemRota["trechos"] = montaTrecho
        montaRota.append(mensagemRota)
    corpoMensagem["rotas"] = montaRota
    return corpoMensagem, 200, header

def rotasTotal(uhe):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ""

    camposDesejados = "pae_identificador"
    condicao = "WHERE emp_identificador = " + str(uhe)
    dadosPAE, retorno, mensagemRetorno = acessoBanco.leDado("pae_planoacaoemergencia", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPAE) == 0:
        return {"rotas": []}, 200, header

    camposDesejados = "rot_identificador,rot_texto"
    condicao = "WHERE pae_identificador = " + str(dadosPAE[0][0])
    dadosRota, retorno, mensagemRetorno = acessoBanco.leDado("rot_rotaevacuacao", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosRota) == 0:
        return {"rotas": []}, 200, header

    montaRota = []

    for i in range(len(dadosRota)):
        mensagemRota = {}
        mensagemRota["id_rota"] = int(dadosRota[i][0])
        mensagemRota["nome_rota"] = dadosRota[i][1]
        montaRota.append(mensagemRota)
    return montaRota, 200, header

def pontosUHE(uhe):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta["sub"]

    # verifica se existem pontos na área de interesse da UHE
    camposDesejados = (
        "pni_identificador, pni_descricao, pni_endereco, "
        + "ST_AsText(pni_pontointeresse.geom), ST_AsText(ST_Transform(pni_pontointeresse.geom,4326))"
    )
    condicao = "where ST_Within(pni_pontointeresse.geom, aoi_areainteresse.geom) and emp_identificador =  " + str(uhe)
    condicao = condicao + " and usu_identificador = " + str(usu_identificador)
    dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado(
        "pni_pontointeresse,aoi_areainteresse", condicao, camposDesejados
    )

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPontos) == 0:
        return {"pontos": []}, 200, header

    # monta resposta
    dadosFinais = []
    for i in range(len(dadosPontos)):
        mensagemPontos = {}
        mensagemPontos["id"] = int(dadosPontos[i][0])
        mensagemPontos["nome"] = dadosPontos[i][1]
        mensagemPontos["endereco"] = dadosPontos[i][2]
        x = dadosPontos[i][3].split(" ")[0][6:]
        y = dadosPontos[i][3].split(" ")[1][:-1]
        mensagemPontos["x"] = float(x)
        mensagemPontos["y"] = float(y)
        lat = dadosPontos[i][4].split(" ")[1][:-1]
        long = dadosPontos[i][4].split(" ")[0][6:]
        mensagemPontos["lat"] = float(lat)
        mensagemPontos["long"] = float(long)
        dadosFinais.append(mensagemPontos)

    corpoMensagem = {}
    corpoMensagem["pontos"] = dadosFinais
    return corpoMensagem, 200, header

def pontosUsuario():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta["sub"]

    if request.method == "GET":
        # recupera os pontos de análise do usuário
        camposDesejados = (
            "pni_identificador, pni_descricao, pni_endereco,ST_AsText(pni_pontointeresse.geom), "
            + "ST_AsText(ST_Transform(pni_pontointeresse.geom,4326))"
        )
        condicao = "WHERE usu_identificador = " + str(usu_identificador)
        dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado("pni_pontointeresse", condicao, camposDesejados)

        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header

        if len(dadosPontos) == 0:
            return {"pontos": []}, 200, header

        # monta resposta
        dadosFinais = []
        for i in range(len(dadosPontos)):
            mensagemPontos = {}
            mensagemPontos["id"] = int(dadosPontos[i][0])
            mensagemPontos["nome"] = dadosPontos[i][1]
            mensagemPontos["endereco"] = dadosPontos[i][2]
            x = dadosPontos[i][3].split(" ")[0][6:]
            y = dadosPontos[i][3].split(" ")[1][:-1]
            mensagemPontos["x"] = float(x)
            mensagemPontos["y"] = float(y)
            lat = dadosPontos[i][4].split(" ")[1][:-1]
            long = dadosPontos[i][4].split(" ")[0][6:]
            mensagemPontos["lat"] = float(lat)
            mensagemPontos["long"] = float(long)
            dadosFinais.append(mensagemPontos)

        corpoMensagem = {}
        corpoMensagem["pontos"] = dadosFinais
        return corpoMensagem, 200, header

    elif request.method == "POST":

        entrada = request.json

        pni_descricao = entrada.get("descricao")
        pni_endereco = entrada.get("endereco")
        y = entrada.get("long")
        x = entrada.get("lat")
        resultadoFinal, retorno = trataPontoIncluido(usu_identificador, pni_descricao, pni_endereco, x, y)
        return resultadoFinal, retorno, header

def pontosAtual(id_ponto):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ""

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta["sub"]

    # verifica se o ponto existe
    camposDesejados = (
        "pni_identificador, pni_descricao, pni_endereco,ST_AsText(pni_pontointeresse.geom), "
        + "ST_AsText(ST_Transform(pni_pontointeresse.geom,4326))"
    )
    condicao = "where pni_identificador =  " + str(id_ponto) + " and usu_identificador = " + str(usu_identificador)
    dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado("pni_pontointeresse", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPontos) == 0:
        return {"pontos": []}, 200, header

    if request.method == "GET":
        # monta resposta
        mensagemPontos = {}
        mensagemPontos["id"] = dadosPontos[0][0]
        mensagemPontos["descricao"] = dadosPontos[0][1]
        mensagemPontos["endereco"] = dadosPontos[0][2]
        x = dadosPontos[0][3].split(" ")[0][6:]
        y = dadosPontos[0][3].split(" ")[1][:-1]
        mensagemPontos["x"] = float(x)
        mensagemPontos["y"] = float(y)
        lat = dadosPontos[0][4].split(" ")[1][:-1]
        long = dadosPontos[0][4].split(" ")[0][6:]
        mensagemPontos["lat"] = float(lat)
        mensagemPontos["long"] = float(long)
        corpoMensagem = {}
        corpoMensagem["pontos"] = mensagemPontos
        return corpoMensagem, 200, header

    elif request.method == "PATCH":
        entrada = request.json
        pni_descricao = None
        pni_endereco = None

        pni_descricao = entrada.get("descricao")
        pni_endereco = entrada.get("endereco")
        valores = ","
        condicao = "WHERE pni_identificador = " + str(id_ponto)

        mensagemPontos = {}
        mensagemPontos["id"] = id_ponto
        mensagemPontos["descricao"] = dadosPontos[0][1]
        mensagemPontos["endereco"] = dadosPontos[0][2]

        erro = False
        mensagemErro = ""
        if pni_descricao is not None:
            if type(pni_descricao) is str and len(pni_descricao) != 0:
                valores = valores + "pni_descricao = '" + pni_descricao + "',"
                mensagemPontos["descricao"] = pni_descricao
            else:
                mensagemErro = "Descrição deve ser textual"
                erro = True

        if pni_endereco is not None:
            if type(pni_endereco) is str and len(pni_endereco) != 0:
                valores = valores + "pni_endereco = '" + pni_endereco + "',"
                mensagemPontos["endereco"] = pni_endereco
            else:
                if erro:
                    mensagemErro = mensagemErro + " # Endereço deve ser textual"
                else:
                    mensagemErro = "Endereço deve ser textual"
                    erro = True

        if erro:
            return {"message": mensagemErro}, 404, header

        if len(valores) == 1:
            return {"message": "Nenhuma informação para alteração foi enviada."}, 404, header
        else:
            valores = valores[1:-1]
            dados, retorno, header = acessoBanco.alteraDado("pni_pontointeresse", valores, condicao)

        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header

        corpoMensagem = {}
        corpoMensagem["pontos"] = mensagemPontos
        return corpoMensagem, 200, header

    elif request.method == "DELETE":
        condicao = "WHERE pni_identificador = " + str(id_ponto)
        dadosPontos, retorno, mensagemRetorno = acessoBanco.exclueDado("pni_pontointeresse", condicao)

        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header

        return {}, 200, header

def pontosUHEAnalise(uhe):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ""

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta["sub"]

    # verifica se existem pontos na área de interesse da UHE
    camposDesejados = (
        "pni_identificador, pni_descricao, pni_endereco, ST_AsText(pni_pontointeresse.geom), "
        + "ST_AsText(ST_Transform(pni_pontointeresse.geom,4326))"
    )
    condicao = "where ST_Within(pni_pontointeresse.geom, aoi_areainteresse.geom) and emp_identificador =  " + str(uhe)
    condicao = condicao + " and usu_identificador = " + str(usu_identificador)
    dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado(
        "pni_pontointeresse,aoi_areainteresse", condicao, camposDesejados
    )

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPontos) == 0:
        return {"pontos": []}, 200, header

    # verifica a situação com relação à ZAS
    camposDesejados = "pae_identificador"
    condicao = "WHERE emp_identificador = " + str(uhe)
    dadosPAE, retorno, mensagemRetorno = acessoBanco.leDado("pae_planoacaoemergencia", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPAE) == 0:
        dadosPontosZAS = []
        dadosPontosZSS = []
    else:
        pae_identificador = dadosPAE[0][0]
        camposDesejados = "pni_identificador, pni_descricao, zas_identificador, zas_texto"
        condicao = (
            "where ST_Within(pni_pontointeresse.geom,zas_zonaautossalvamento.geom) and pae_identificador =  "
            + str(pae_identificador)
        )
        condicao = condicao + " and usu_identificador = " + str(usu_identificador)
        dadosPontosZAS, retorno, mensagemRetorno = acessoBanco.leDado(
            "pni_pontointeresse,zas_zonaautossalvamento", condicao, camposDesejados
        )

        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header

        # verifica a situação com relação à ZSS

        camposDesejados = "pni_identificador, pni_descricao, zss_identificador, zss_texto"
        condicao = "where ST_Within(pni_pontointeresse.geom,zss_zonasecundaria.geom) and pae_identificador =  " + str(
            pae_identificador
        )
        condicao = condicao + " and usu_identificador = " + str(usu_identificador)
        dadosPontosZSS, retorno, mensagemRetorno = acessoBanco.leDado(
            "pni_pontointeresse,zss_zonasecundaria", condicao, camposDesejados
        )

        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header

    # monta os dicionários
    listaZAS = []
    for i in range(len(dadosPontosZAS)):
        listaZAS.append(dadosPontosZAS[i][0])
    listaZSS = {}
    for i in range(len(dadosPontosZSS)):
        listaZSS.append(dadosPontosZSS[i][0])

    # verifica a situação com relação ao Sosem
    camposDesejados = "vaz_identificador, vaz_datahora, vaz_vazaoconsiderada"
    condicao = "WHERE emp_identificador = " + str(uhe) + " order by vaz_datahora"
    dadosVazao, retorno, mensagemRetorno = acessoBanco.leDado("vaz_vazaodefluente", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    menorData = datetime.datetime.strptime("2900-12-31 23:59:59", "%Y-%m-%d %H:%M:%S")
    maiorData = datetime.datetime.strptime("2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

    if dadosVazao == []:
        listaSosem = []
    else:
        vazoes = "("
        vazoesLista = []
        for i in range(len(dadosVazao)):
            if dadosVazao[i][1] > maiorData:
                maiorData = dadosVazao[i][1]
            if dadosVazao[i][1] < menorData:
                menorData = dadosVazao[i][1]
            if dadosVazao[i][2] not in vazoesLista:
                vazoes = vazoes + str(dadosVazao[i][2]) + ","
                vazoesLista.append(dadosVazao[i][2])
        vazoes = vazoes[:-1] + ")"
        camposDesejados = "pni_identificador, pni_descricao, man_identificador, man_vazao"
        condicao = (
            "where ST_Within(pni_pontointeresse.geom,man_manchainundacao.geom) and emp_identificador =  "
            + str(uhe)
            + " and usu_identificador = " + str(usu_identificador) + " and man_vazao in " + vazoes
        )
        dadosPontoSosem, retorno, mensagemRetorno = acessoBanco.leDado(
            "pni_pontointeresse,man_manchainundacao", condicao, camposDesejados
        )
        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header

        listaSosem = []
        dataSosem = []
        vazaoSosem = []
        if dadosPontoSosem == []:
            listaSosem = []
        else:
            for i in range(len(dadosPontoSosem)):
                for j in range(len(dadosVazao)):
                    if dadosPontoSosem[i][3] == dadosVazao[j][2]:
                        listaSosem.append(dadosPontoSosem[i][0])
                        dataSosem.append(dadosVazao[j][1])
                        vazaoSosem.append(dadosPontoSosem[i][3])
                        break

    # verifica se existe alguma vazão que inunda os pontos

    # monta resposta
    dadosFinais = []
    for i in range(len(dadosPontos)):
        mensagemPontos = {}
        mensagemPontos["id"] = dadosPontos[i][0]
        mensagemPontos["nome"] = dadosPontos[i][1]
        mensagemPontos["endereco"] = dadosPontos[i][2]
        if dadosPontos[i][0] in listaSosem:
            for j in range(len(listaSosem)):
                if dadosPontos[i][0] == listaSosem[j]:
                    mensagemPontos["situacao_SOSEM"] = (
                        "Dentro de área inundada - vazão: "
                        + str(vazaoSosem[j])
                        + " m3/s - data/hora: "
                        + dataSosem[j].strftime("%d-%m-%Y %H:%M:%S")
                    )
                    break
        else:
            mensagemPontos["situacao_SOSEM"] = "Fora de área a ser inundada"
        if dadosPontos[i][0] in listaZAS:
            mensagemPontos["situacao_PAE"] = "Dentro da ZAS"
        elif dadosPontos[i][0] in listaZSS:
            mensagemPontos["situacao_PAE"] = "Dentro da ZSS"
        else:
            mensagemPontos["situacao_PAE"] = "Fora da ZAS e da ZSS"
        x = dadosPontos[i][3].split(" ")[0][6:]
        y = dadosPontos[i][3].split(" ")[1][:-1]
        mensagemPontos["x"] = float(x)
        mensagemPontos["y"] = float(y)
        lat = dadosPontos[i][4].split(" ")[1][:-1]
        long = dadosPontos[i][4].split(" ")[0][6:]
        mensagemPontos["lat"] = float(lat)
        mensagemPontos["long"] = float(long)
        dadosFinais.append(mensagemPontos)

    corpoMensagem = {}
    corpoMensagem["pontos"] = dadosFinais
    return corpoMensagem, 200, header

def vazaoEspecifica():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta["sub"]

    vazao = None
    uhe = None

    query_parameters = request.args
    vazao = query_parameters.get("vazao")
    uhe = query_parameters.get("usina")

    if vazao is None or len(vazao) < 1 or uhe is None or len(uhe) < 1:
        return {"message": "Parâmetros 'vazao' e 'usina' obrigatórios"}, 401, {}

    # verifica se existem pontos na área de interesse da UHE
    camposDesejados = (
        "pni_identificador, pni_descricao, pni_endereco, ST_AsText(pni_pontointeresse.geom), "
        + "ST_AsText(ST_Transform(pni_pontointeresse.geom,4326))"
    )
    condicao = (
        "where ST_Within(pni_pontointeresse.geom, aoi_areainteresse.geom) and emp_identificador =  "
        + str(uhe)
        + " and usu_identificador = " + str(usu_identificador)
    )
    dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado(
        "pni_pontointeresse,aoi_areainteresse", condicao, camposDesejados
    )

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPontos) == 0:
        return {"pontos": []}, 200, header

    # verifica a situação com relação ao Sosem
    camposDesejados = "pni_identificador, pni_descricao, man_identificador"
    condicao = "where ST_Within(pni_pontointeresse.geom,man_manchainundacao.geom) and emp_identificador =  " + str(uhe)
    condicao = condicao + " and usu_identificador = " + str(usu_identificador) + " and man_vazao = " + vazao
    dadosPontoSosem, retorno, mensagemRetorno = acessoBanco.leDado(
        "pni_pontointeresse,man_manchainundacao", condicao, camposDesejados
    )
    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    listaSosem = []
    if dadosPontoSosem != []:
        for i in range(len(dadosPontoSosem)):
            listaSosem.append(dadosPontoSosem[i][0])

    # monta resposta
    dadosFinais = []
    for i in range(len(dadosPontos)):
        mensagemPontos = {}
        mensagemPontos["id"] = int(dadosPontos[i][0])
        mensagemPontos["nome"] = dadosPontos[i][1]
        mensagemPontos["endereco"] = dadosPontos[i][2]
        if dadosPontos[i][0] in listaSosem:
            mensagemPontos["situacao_SOSEM"] = "Dentro de área inundada "
        else:
            mensagemPontos["situacao_SOSEM"] = "Fora de área inundada "
        x = dadosPontos[i][3].split(" ")[0][6:]
        y = dadosPontos[i][3].split(" ")[1][:-1]
        mensagemPontos["x"] = float(x)
        mensagemPontos["y"] = float(y)
        lat = dadosPontos[i][4].split(" ")[1][:-1]
        long = dadosPontos[i][4].split(" ")[0][6:]
        mensagemPontos["lat"] = float(lat)
        mensagemPontos["long"] = float(long)
        dadosFinais.append(mensagemPontos)

    corpoMensagem = {}
    corpoMensagem["pontos"] = dadosFinais
    return corpoMensagem, 200, header

def vazoesTotal(uhe):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ""

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta["sub"]

    # recupera as vazões
    listaSosem = []
    camposDesejados = "vaz_identificador, vaz_datahora, vaz_vazaoprevista, vaz_situacaososem, vaz_vazaoconsiderada"
    condicao = "WHERE emp_identificador = " + str(uhe) + " order by vaz_datahora"
    dadosVazao, retorno, mensagemRetorno = acessoBanco.leDado("vaz_vazaodefluente", condicao, camposDesejados)
    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    menorData = datetime.datetime.strptime("2900-12-31 23:59:59", "%Y-%m-%d %H:%M:%S")
    maiorData = datetime.datetime.strptime("2000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

    if dadosVazao != []:
        for i in range(len(dadosVazao)):
            if dadosVazao[i][1] > maiorData:
                maiorData = dadosVazao[i][1]
            if dadosVazao[i][1] < menorData:
                menorData = dadosVazao[i][1]

    # monta resposta
    mensagemPeriodo = {}
    mensagemPeriodo["comeco"] = menorData.strftime("%d-%m-%Y %H:%M:%S")
    mensagemPeriodo["final"] = maiorData.strftime("%d-%m-%Y %H:%M:%S")

    corpoMensagem = {}
    corpoMensagem["periodo"] = mensagemPeriodo

    dadosFinais = []
    for i in range(len(dadosVazao)):
        mensagemVazoes = {}
        mensagemVazoes["id"] = int(dadosVazao[i][0])
        mensagemVazoes["data"] = dadosVazao[i][1].strftime("%d-%m-%Y %H:%M:%S")
        mensagemVazoes["vazao_prevista"] = float(dadosVazao[i][2])
        mensagemVazoes["situacao_sosem"] = dadosVazao[i][3]
        mensagemVazoes["vazao_considerada"] = float(dadosVazao[i][4])
        dadosFinais.append(mensagemVazoes)

    corpoMensagem["vazoes"] = dadosFinais
    return corpoMensagem, 200, header

def rotaPontoEspecifico(ponto):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ""

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta["sub"]

    mensagemPontoEspecifico = {}
    # verifica se o ponto específico existe e se ele está na ZAS
    camposDesejados = (
        "pni_identificador,ST_AsText(pni_pontointeresse.geom), ST_AsText(ST_Transform(pni_pontointeresse.geom,4326))"
    )
    condicao = "where pni_identificador =  " + str(ponto)
    dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado("pni_pontointeresse", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPontos) == 0:
        return {"ponto_analise": [], "ponto_seguranca": [], "rota": [], "trechos": []}, 200, header

    # verifica a situação com relação à ZAS
    camposDesejados = "pni_identificador, pni_descricao, zas_identificador, zas_texto, pae_identificador"
    condicao = (
        "where ST_Within(pni_pontointeresse.geom,zas_zonaautossalvamento.geom) and pni_identificador =  "
        + str(ponto)
    )
    dadosPontosZAS, retorno, mensagemRetorno = acessoBanco.leDado(
        "pni_pontointeresse,zas_zonaautossalvamento", condicao, camposDesejados
    )

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPontosZAS) == 0:
        return {"ponto_analise": [], "ponto_seguranca": [], "rota": [], "trechos": []}, 200, header

    detalhePontoAnalise = {}
    detalhePontoAnalise["id_ponto"] = int(dadosPontosZAS[0][0])
    detalhePontoAnalise["nome_ponto"] = dadosPontosZAS[0][1]
    detalhePontoAnalise["ZAS"] = dadosPontosZAS[0][3]
    x = dadosPontos[0][1].split(" ")[0][6:]
    y = dadosPontos[0][1].split(" ")[1][:-1]
    detalhePontoAnalise["x"] = float(x)
    detalhePontoAnalise["y"] = float(y)
    lat = dadosPontos[0][2].split(" ")[1][:-1]
    long = dadosPontos[0][2].split(" ")[0][6:]
    detalhePontoAnalise["lat"] = float(lat)
    detalhePontoAnalise["long"] = float(long)
    mensagemPontoEspecifico["ponto_analise"] = detalhePontoAnalise

    # obtem o trecho da rota mais próximo

    camposDesejados = "pni_pontointeresse.pni_identificador, st_distance(pni_pontointeresse.geom,tro_trechorotaevacuacao.geom) as distancia, "
    camposDesejados = camposDesejados + "tro_identificador"
    condicao = "where pni_pontointeresse.pni_identificador = " + str(ponto) + " order by distancia limit 1 "
    dadosPontosRota, retorno, mensagemRetorno = acessoBanco.leDado(
        "pni_pontointeresse, tro_trechorotaevacuacao", condicao, camposDesejados
    )

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPontosRota) == 0:
        return {"ponto_analise": [], "ponto_seguranca": [], "rota": [], "trechos": []}, 200, header

    # recupera uma rota que contenha o trecho
    camposDesejados = "rot_identificador"
    condicao = "WHERE tro_identificador = " + str(dadosPontosRota[0][2])
    dadosRota, retorno, mensagemRetorno = acessoBanco.leDado(
        "rot_tro_rotaevacuacao_trechorotaevacuacao", condicao, camposDesejados
    )

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosRota) == 0:
        return {"ponto_analise": [], "ponto_seguranca": [], "rota": [], "trechos": []}, 200, header

    # recupera os trechos de rota
    trecho = []
    trecho_anterior = []
    trecho_nome = {}

    camposDesejados = "rot_tro_rotaevacuacao_trechorotaevacuacao.tro_identificador, tro_anterior, tro_logradouro"
    condicao = (
        "INNER JOIN tro_trechorotaevacuacao ON "
        + "rot_tro_rotaevacuacao_trechorotaevacuacao.tro_identificador =  tro_trechorotaevacuacao.tro_identificador "
        + "WHERE rot_identificador ="
        + str(dadosRota[0][0])
    )
    dadosTrecho, retorno, mensagemRetorno = acessoBanco.leDado(
        "rot_tro_rotaevacuacao_trechorotaevacuacao", condicao, camposDesejados
    )

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosTrecho) == 0:
        return {"message": "Esta UHE não possui trechos de rota de evacuação."}, 404, header

    for j in range(len(dadosTrecho)):
        trecho.append(dadosTrecho[j][0])
        trecho_anterior.append(dadosTrecho[j][1])
        trecho_nome[dadosTrecho[j][0]] = dadosTrecho[j][2]

    # encontra o caminho
    caminho = navega(trecho, trecho_anterior, dadosPontosRota[0][2])

    montaTrecho = []
    sequencia = 0
    for i in range(len(caminho)):
        mensagemTrechos = {}
        sequencia = sequencia + 1
        mensagemTrechos["id_trecho"] = int(caminho[i])
        mensagemTrechos["sequencia_trecho"] = int(sequencia)
        mensagemTrechos["nome_trecho"] = trecho_nome[caminho[i]]
        montaTrecho.append(mensagemTrechos)
    mensagemPontoEspecifico["trechos"] = montaTrecho

    # recupera o ponto de segurança da rota
    camposDesejados = (
        "rot_pns_rotaevacuacao_pontoseguranca.pns_identificador, pns_identificacao, "
        + "ST_AsText(pns_pontoseguranca.geom), ST_AsText(ST_Transform(pns_pontoseguranca.geom,4326))"
    )
    condicao = (
        "INNER JOIN pns_pontoseguranca ON "
        + "rot_pns_rotaevacuacao_pontoseguranca.pns_identificador = pns_pontoseguranca.pns_identificador "
        + "WHERE rot_pns_rotaevacuacao_pontoseguranca.rot_identificador = "
        + str(dadosRota[0][0])
    )
    dadosPonto, retorno, mensagemRetorno = acessoBanco.leDado(
        "rot_pns_rotaevacuacao_pontoseguranca", condicao, camposDesejados
    )

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPonto) == 0:
        return {"message": "Esta UHE não possui pontos de segurança."}, 404, header
    detalhePontoSeguranca = {}
    detalhePontoSeguranca["id_ponto"] = int(dadosPonto[0][0])
    detalhePontoSeguranca["nome_ponto"] = dadosPonto[0][1]
    x = dadosPonto[0][2].split(" ")[0][6:]
    y = dadosPonto[0][2].split(" ")[1][:-1]
    detalhePontoSeguranca["x"] = float(x)
    detalhePontoSeguranca["y"] = float(y)
    lat = dadosPonto[0][3].split(" ")[1][:-1]
    long = dadosPonto[0][3].split(" ")[0][6:]
    detalhePontoSeguranca["lat"] = float(lat)
    detalhePontoSeguranca["long"] = float(long)
    mensagemPontoEspecifico["ponto_seguranca"] = detalhePontoSeguranca

    # recupera os dados da rota
    camposDesejados = "rot_texto"
    condicao = "WHERE rot_identificador = " + str(dadosRota[0][0])
    dadosRotaEspec, retorno, mensagemRetorno = acessoBanco.leDado("rot_rotaevacuacao", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosRotaEspec) == 0:
        return {"message": "Esta UHE não possui rota."}, 404, header

    detalheRota = {}
    detalheRota["id_rota"] = int(dadosRota[0][0])
    detalheRota["nome_rota"] = dadosRotaEspec[0][0]
    mensagemPontoEspecifico["rota"] = detalheRota

    # prepara o retorno

    corpoMensagem = {}
    return mensagemPontoEspecifico, 200, header

def ordena(trecho, trecho_anterior):

    anterior = {}
    posterior = {}
    inicio = []
    nivel = {}

    for i in range(len(trecho)):
        anterior[trecho[i]] = trecho_anterior[i]
        nivel[trecho[i]] = 0
        if trecho_anterior[i] == 0:
            inicio.append(trecho[i])
        posterior[trecho_anterior[i]] = []

    for i in range(len(trecho)):
        posterior[trecho_anterior[i]].append(trecho[i])

    for k in range(len(inicio)):
        pilha = []
        pilha.append(inicio[k])
        empilha = True
        while empilha:
            if (len(pilha)) == 0:
                break
            elemento = pilha[len(pilha) - 1]

            if elemento not in posterior.keys():
                pilha.remove(elemento)
            else:
                filhos = posterior[elemento]
                for j in range(len(filhos)):
                    pilha.append(filhos[j])
                    nivel[filhos[j]] = nivel[elemento] + 1
                x = posterior.pop(elemento)

    return nivel

def navega(trecho, trecho_anterior, inicio):

    anterior = {}
    posterior = {}
    caminho = []
    caminho.append(inicio)
    comeco = inicio
    nivel = {}

    for i in range(len(trecho)):
        anterior[trecho[i]] = trecho_anterior[i]

    empilha = True
    while empilha:
        if anterior[comeco] == 0:
            break
        else:
            caminho.append(anterior[comeco])
            comeco = anterior[comeco]

    return caminho

def trataPontoIncluido(usu_identificador, pni_descricao, pni_endereco, x, y):

    cheque = {}
    cheque["message"] = ""
    erro = False

    if pni_descricao is None or type(pni_descricao) is not str or len(pni_descricao) < 2:
        cheque["message"] = "A descrição do Ponto de Análise é obrigatória e textual"
        erro = True

    if x is None:
        if not erro:
            cheque["message"] = "Latitude é obrigatória e em formato real"
        else:
            cheque["message"] = cheque["message"] + " - Latitude é obrigatória e em formato real"
        erro = True
    else:
        if not real(x):
            if not erro:
                cheque["message"] = "Latitude é obrigatória e em formato real"
            else:
                cheque["message"] = cheque["message"] + " - Latitude é obrigatória e em formato real"
            erro = True

    if y is None:
        if not erro:
            cheque["message"] = "Longitude é obrigatória e em formato real"
        else:
            cheque["message"] = cheque["message"] + " - Longitude é obrigatória e em formato real"
        erro = True
    else:
        if not real(y):
            if not erro:
                cheque["message"] = "Longitude é obrigatória e em formato real"
            else:
                cheque["message"] = cheque["message"] + " - Longitude é obrigatória e em formato real"
            erro = True

    if erro:
        return cheque, 404

    comando = (
        "SELECT ST_AsText(ST_Transform(ST_GeomFromText('POINT("
        + str(y)
        + " "
        + str(x)
        + ")',4326), 3857)) As wgs_geom "
    )
    dados, retorno, header = acessoBanco.executaComando(comando)
    if retorno != 200:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    wgs_geom = dados[0][0]

    # verifica a situação com relação à AOI
    camposDesejados = "aoi_identificador, emp_identificador"
    condicao = "WHERE ST_Intersects(geom, ST_GeomFromText('" + wgs_geom + "', 3857))"
    dadosPontosAOI, retorno, mensagemRetorno = acessoBanco.leDado("aoi_areainteresse", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400

    if len(dadosPontosAOI) == 0:
        return {"message": "Ponto de Análise não está em área de interesse de nenhum empreendimento."}, 404

    # inclui
    camposDesejados = "max(pni_identificador)"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("pni_pontointeresse", None, camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno, {}

    if dados[0][0] is None:
        proximoNumero = 1
    else:
        proximoNumero = dados[0][0] + 1

    if pni_endereco is None or len(pni_endereco) == 0:
        camposDesejados = (
            "pni_identificador, pni_descricao, usu_identificador, pni_identificadoratualizacao, "
            + "pni_dataatualizacao, geom"
        )
        valores = (
            str(proximoNumero) + ",'" + pni_descricao + "'," + str(usu_identificador)
            + "," + str(usu_identificador) + ",'" + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            + "'," + "ST_GeomFromText('" + wgs_geom + "', 3857)"
        )
        pni_endereco = ""
    else:
        camposDesejados = (
            "pni_identificador, pni_descricao, pni_endereco, usu_identificador, pni_identificadoratualizacao, "
            + "pni_dataatualizacao, geom"
        )
        valores = (
            str(proximoNumero) + ",'" + pni_descricao + "','" + pni_endereco + "'," + str(usu_identificador)
            + "," + str(usu_identificador) + ",'" + datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            + "'," + "ST_GeomFromText('" + wgs_geom + "', 3857)"
        )

    dados, retorno, header = acessoBanco.insereDado("pni_pontointeresse", camposDesejados, valores)
    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 400

    mensagemPontos = {}
    mensagemPontos["id"] = proximoNumero
    mensagemPontos["nome"] = pni_descricao
    mensagemPontos["endereco"] = pni_endereco
    mensagemPontos["lat"] = float(x)
    mensagemPontos["long"] = float(y)
    mensagemPontos["empreendimento"] = dadosPontosAOI[0][1]

    corpoMensagem = {}
    corpoMensagem["ponto"] = mensagemPontos
    return corpoMensagem, 201

def real(value):
    try:
        float(value)
    except ValueError:
        return False
    return True

def pontosRotaTotal(rota):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta["sub"]

    # verifica se existem pontos para a rota informada

    camposDesejados = (
        "pnr_identificador, "
        + "ST_AsText(geom), ST_AsText(ST_Transform(geom,4326))"
    )
    condicao = "WHERE rot_identificador = " + str(rota)
    dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado(
        "pnr_pontorotaevacuacao", condicao, camposDesejados
    )

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPontos) == 0:
        return {"pontos": []}, 200, header

    # monta resposta
    dadosFinais = []
    for i in range(len(dadosPontos)):
        mensagemPontos = {}
        mensagemPontos["id"] = int(dadosPontos[i][0])
        x = dadosPontos[i][1].split(" ")[0][6:]
        y = dadosPontos[i][1].split(" ")[1][:-1]
        mensagemPontos["x"] = float(x)
        mensagemPontos["y"] = float(y)
        lat = dadosPontos[i][2].split(" ")[1][:-1]
        long = dadosPontos[i][2].split(" ")[0][6:]
        mensagemPontos["lat"] = float(lat)
        mensagemPontos["long"] = float(long)
        dadosFinais.append(mensagemPontos)

    print (dadosFinais)
    corpoMensagem = {}
    corpoMensagem["pontos"] = dadosFinais
    return corpoMensagem, 200, header

def pontoRotaEspecifico(ponto):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta["sub"]

    # recupera a rota do ponto especificado

    camposDesejados = "rot_identificador, pnr_sequencia"
    condicao = "WHERE pnr_identificador = " + str(ponto)
    dadoPonto, retorno, mensagemRetorno = acessoBanco.leDado(
        "pnr_pontorotaevacuacao", condicao, camposDesejados
    )

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadoPonto) == 0:
        return {"pontos": [], "detalhes": []}, 200, header

    rota = int(dadoPonto[0][0])

    # recupera a rota do ponto especificado

    camposDesejados = (
        "pnr_identificador, pnr_sequencia, pnr_anterior, pnr_fotografia, pnr_cobertura, pnr_largura, pnr_altitude,"
        + "ST_AsText(geom), ST_AsText(ST_Transform(geom,4326))"
    )
    condicao = "WHERE rot_identificador = " + str(rota)
    dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado(
        "pnr_pontorotaevacuacao", condicao, camposDesejados
    )

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header

    if len(dadosPontos) == 0:
        return {"pontos": [], "detalhes": []}, 200, header

    # monta dicionario
    dicPontos = {}
    for i in range(len(dadosPontos)):
        mensagemPontos = {}
        mensagemPontos["id"] = int(dadosPontos[i][0])
        mensagemPontos["sequencia"] = dadosPontos[i][1]
        mensagemPontos["anterior"] = dadosPontos[i][2]
        mensagemPontos["fotografia"] = dadosPontos[i][3]
        mensagemPontos["cobertura"] = dadosPontos[i][4]
        mensagemPontos["largura"] = float(dadosPontos[i][5])
        mensagemPontos["altitude"] = float(dadosPontos[i][6])
        x = dadosPontos[i][7].split(" ")[0][6:]
        y = dadosPontos[i][7].split(" ")[1][:-1]
        mensagemPontos["x"] = float(x)
        mensagemPontos["y"] = float(y)
        lat = dadosPontos[i][8].split(" ")[1][:-1]
        long = dadosPontos[i][8].split(" ")[0][6:]
        mensagemPontos["lat"] = float(lat)
        mensagemPontos["long"] = float(long)
        dicPontos[dadosPontos[i][1]] = mensagemPontos

    # monta resposta
    sequencia = int(dadoPonto[0][1])
    qtde = 0
    distanciaTotal = 0
    pontos = []
    alt_max = -1
    alt_min = 1000000000000000000
    while sequencia != 0:
        qtde = qtde + 1
        mensagemPontos = {}
        mensagemPontos["id"] = dicPontos[sequencia]["id"]
        mensagemPontos["sequencia"] = dicPontos[sequencia]["sequencia"]
        mensagemPontos["anterior"] = dicPontos[sequencia]["anterior"]
        mensagemPontos["fotografia"] = dicPontos[sequencia]["fotografia"]
        mensagemPontos["cobertura"] = dicPontos[sequencia]["cobertura"]
        mensagemPontos["largura"] = dicPontos[sequencia]["largura"]
        mensagemPontos["altitude"] = dicPontos[sequencia]["altitude"]
        mensagemPontos["x"] = dicPontos[sequencia]["x"]
        mensagemPontos["y"] = dicPontos[sequencia]["y"]
        mensagemPontos["lat"] = dicPontos[sequencia]["lat"]
        mensagemPontos["long"] = dicPontos[sequencia]["long"]
        mensagemPontos["distancia"] = distanciaTotal

        if alt_max < dicPontos[sequencia]["altitude"]:
            alt_max = dicPontos[sequencia]["altitude"]

        if alt_min > dicPontos[sequencia]["altitude"]:
            alt_min = dicPontos[sequencia]["altitude"]

        pontos.append(mensagemPontos)
        anterior = dicPontos[sequencia]["anterior"]
        if anterior != 0:
            deltaX = dicPontos[sequencia]["x"] - dicPontos[anterior]["x"]
            deltaY = dicPontos[sequencia]["y"] - dicPontos[anterior]["y"]
            distanciaTotal = distanciaTotal + sqrt(deltaX**2 + deltaY**2)
        sequencia = anterior

    final = {}
    detalhes = {}
    detalhes["quantidade_pontos"] = qtde
    detalhes["altura_maxima"] = alt_max
    detalhes["altura_minima"] = alt_min
    detalhes["distancia_total"] = distanciaTotal
    detalhes["imagem_largura"] = 8192
    detalhes["imagem_altura"] = 4096
    final['detalhes'] = detalhes
    final['pontos'] = pontos

    return final, 200, header