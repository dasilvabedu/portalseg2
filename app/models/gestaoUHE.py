# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request
import datetime

def rotasOrdenadas(uhe):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    camposDesejados = 'pae_identificador'
    condicao = "WHERE emp_identificador = " + str(uhe)
    dadosPAE, retorno, mensagemRetorno = acessoBanco.leDado('pae_planoacaoemergencia', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosPAE) == 0:
        return {"message": "Esta UHE não possui Plano de Ação de Emergência."}, 400, header

    camposDesejados = 'rot_identificador,rot_texto'
    condicao = "WHERE pae_identificador = " + str(dadosPAE[0][0])
    dadosRota, retorno, mensagemRetorno = acessoBanco.leDado('rot_rotaevacuacao', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosRota) == 0:
        return {"message": "Esta UHE não possui rota de evacuação definida."}, 400, header

    corpoMensagem = {}
    montaRota = []

    for i in range(len(dadosRota)):
        trecho = []
        trecho_anterior = []
        trecho_nome = {}
        mensagemRota = {}
        mensagemRota["id_rota"] = dadosRota[i][0]
        mensagemRota["nome_rota"] = dadosRota[i][1]

        camposDesejados = 'rot_tro_rotaevacuacao_trechorotaevacuacao.tro_identificador, tro_anterior, tro_logradouro'
        condicao = "INNER JOIN tro_trechorotaevacuacao ON rot_tro_rotaevacuacao_trechorotaevacuacao.tro_identificador =  tro_trechorotaevacuacao.tro_identificador WHERE rot_tro_rotaevacuacao_trechorotaevacuacao.rot_identificador =" + str(dadosRota[i][0])
        dadosTrecho, retorno, mensagemRetorno = acessoBanco.leDado('rot_tro_rotaevacuacao_trechorotaevacuacao', condicao, camposDesejados)

        if retorno == 404:
            return {"message": "Erro de acesso ao banco"}, 401, header

        if len(dadosTrecho) == 0:
            return {"message": "Esta UHE não possui trechos de rota de evacuação."}, 400, header
        for j in range(len(dadosTrecho)):
            trecho.append(dadosTrecho[j][0])
            trecho_anterior.append(dadosTrecho[j][1])
            trecho_nome[dadosTrecho[j][0]] = dadosTrecho[j][2]

        camposDesejados = 'rot_pns_rotaevacuacao_pontoseguranca.pns_identificador, pns_identificacao'
        condicao = "INNER JOIN pns_pontoseguranca ON rot_pns_rotaevacuacao_pontoseguranca.pns_identificador = pns_pontoseguranca.pns_identificador WHERE rot_pns_rotaevacuacao_pontoseguranca.rot_identificador = " + str(dadosRota[i][0])
        dadosPonto, retorno, mensagemRetorno = acessoBanco.leDado('rot_pns_rotaevacuacao_pontoseguranca', condicao, camposDesejados)

        if retorno == 404:
            return {"message": "Erro de acesso ao banco"}, 401, header

        if len(dadosPonto) == 0:
            return {"message": "Esta UHE não possui pontos de segurança."}, 400, header
        detalhePontos = {}
        detalhePontos['id_ponto'] = dadosPonto[0][0]
        detalhePontos['nome_ponto'] = dadosPonto[0][1]
        mensagemRota["ponto_seguranca"] = detalhePontos


        sequencia = 0
        montaTrecho = []

        nivel = ordena(trecho, trecho_anterior)
        for m in (sorted(set(nivel.values()))):
            for n in nivel.keys():
                if nivel[n] == m:
                    mensagemTrechos = {}
                    sequencia = sequencia + 1
                    mensagemTrechos["id_trecho"] = n
                    mensagemTrechos["sequencia_trecho"] = sequencia
                    mensagemTrechos["nome_trecho"] = trecho_nome[n]
                    montaTrecho.append(mensagemTrechos)

        mensagemRota["trechos"] = montaTrecho
        montaRota.append(mensagemRota)
    corpoMensagem["rotas"] = montaRota
    return corpoMensagem, 200, header

def pontosUHE(uhe):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta['sub']

    # verifica se existem pontos na área de interesse da UHE
    camposDesejados = 'pni_identificador, pni_descricao, pni_endereco'
    condicao = "where ST_Within(pni_pontointeresse.geom, aoi_areainteresse.geom) and emp_identificador =  " + str(uhe)
    condicao = condicao + " and usu_identificador = " + str(usu_identificador)
    dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado('pni_pontointeresse,aoi_areainteresse', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosPontos) == 0:
        return {"message": "Este usuário não possui Pontos de Interesse para esta UHE."}, 400, header

# monta resposta
    dadosFinais = []
    for i in range(len(dadosPontos)):
        mensagemPontos = {}
        mensagemPontos["id"] = dadosPontos[i][0]
        mensagemPontos["nome"] = dadosPontos[i][1]
        mensagemPontos["endereco"] = dadosPontos[i][2]
        dadosFinais.append(mensagemPontos)

    corpoMensagem = {}
    corpoMensagem['pontos'] = dadosFinais
    return corpoMensagem, 200, header

def pontosUsuario():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta['sub']

    if request.method == 'GET':
    # verifica se existem pontos na área de interesse da UHE
        camposDesejados = 'pni_identificador, pni_descricao, pni_endereco'
        condicao = "WHERE usu_identificador = " + str(usu_identificador)
        dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado('pni_pontointeresse,aoi_areainteresse', condicao, camposDesejados)

        if retorno == 404:
            return {"message": "Erro de acesso ao banco"}, 401, header

        if len(dadosPontos) == 0:
            return {"message": "Este usuário não possui Pontos de Interesse cadastrados."}, 400, header

    # monta resposta
        dadosFinais = []
        for i in range(len(dadosPontos)):
            mensagemPontos = {}
            mensagemPontos["id"] = dadosPontos[i][0]
            mensagemPontos["nome"] = dadosPontos[i][1]
            mensagemPontos["endereco"] = dadosPontos[i][2]
            dadosFinais.append(mensagemPontos)

        corpoMensagem = {}
        corpoMensagem['pontos'] = dadosFinais
        return corpoMensagem, 200, header

    elif request.method == 'POST':
        entrada = request.json
        pni_descricao = entrada.get('descricao')
        pni_endereco = entrada.get('endereco')
        x = entrada.get('x')
        y = entrada.get('y')
        resultadoFinal, retorno = trataPontoIncluido(usu_identificador, pni_descricao, pni_endereco, x, y)
        return resultadoFinal, retorno, header

def pontosAtual(id_ponto):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta['sub']

    # verifica se o ponto existe
    camposDesejados = 'pni_identificador, pni_descricao, pni_endereco'
    condicao = "where pni_identificador =  " + str(id_ponto) + " and usu_identificador = " + str(usu_identificador)
    dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado('pni_pontointeresse', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosPontos) == 0:
        return {"message": "Ponto de Análise inexistente"}, 400, header


    if request.method == 'GET':
    # monta resposta
        mensagemPontos = {}
        mensagemPontos["id"] = dadosPontos[0][0]
        mensagemPontos["descricao"] = dadosPontos[0][1]
        mensagemPontos["endereco"] = dadosPontos[0][2]
        corpoMensagem = {}
        corpoMensagem['pontos'] = mensagemPontos
        return corpoMensagem, 200, header

    elif request.method == 'PATCH':
        entrada = request.json
        pni_descricao = entrada.get('descricao')
        pni_endereco = entrada.get('endereco')
        valores = ','
        condicao = "WHERE pni_identificador = " + str(id_ponto)

        mensagemPontos = {}
        mensagemPontos["id"] = id_ponto
        mensagemPontos["descricao"] = dadosPontos[0][1]
        mensagemPontos["endereco"] = dadosPontos[0][2]

        if pni_descricao is not None and len(pni_descricao) != 0:
            valores = valores + "pni_descricao = '" + pni_descricao + "',"
            mensagemPontos["descricao"] = pni_descricao
        if pni_endereco is not None and len(pni_endereco) != 0:
            valores = valores + "pni_endereco = '" + pni_endereco + "',"
            mensagemPontos["endereco"] = pni_endereco
        if len(valores) == 1:
            return {"message": "Nenhuma informação para alteração foi enviada."}, 400, header
        else:
            valores = valores [1:-1]
            dados, retorno, header = acessoBanco.alteraDado('pni_pontointeresse', valores, condicao)

        if retorno == 404:
            return {"message": "Erro de acesso ao banco"}, 401, header

        corpoMensagem = {}
        corpoMensagem['pontos'] = mensagemPontos
        return corpoMensagem, 200, header


    elif request.method == 'DELETE':
        condicao = "WHERE pni_identificador = " + str(id_ponto)
        dadosPontos, retorno, mensagemRetorno = acessoBanco.exclueDado('pni_pontointeresse', condicao)

        if retorno == 404:
            return {"message": "Erro de acesso ao banco"}, 401, header

        return {}, 200, header


def pontosUHEAnalise(uhe):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta['sub']

    # verifica se existem pontos na área de interesse da UHE
    camposDesejados = 'pni_identificador, pni_descricao, pni_endereco'
    condicao = "where ST_Within(pni_pontointeresse.geom, aoi_areainteresse.geom) and emp_identificador =  " + str(uhe)
    condicao = condicao + " and usu_identificador = " + str(usu_identificador)
    dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado('pni_pontointeresse,aoi_areainteresse', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosPontos) == 0:
        return {"message": "Este usuário não possui Pontos de Interesse para esta UHE."}, 400, header

    #verifica a situação com relação à ZAS
    camposDesejados = 'pae_identificador'
    condicao = "WHERE emp_identificador = " + str(uhe)
    dadosPAE, retorno, mensagemRetorno = acessoBanco.leDado('pae_planoacaoemergencia', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosPAE) == 0:
        dadosPontosZAS = []
        dadosPontosZSS = []
    else:
        camposDesejados = 'pni_identificador, pni_descricao, zas_identificador, zas_texto'
        condicao = "where ST_Within(pni_pontointeresse.geom,zas_zonaautossalvamento.geom) and pae_identificador =  " + str(uhe)
        condicao = condicao + " and usu_identificador = " + str(usu_identificador)
        dadosPontosZAS, retorno, mensagemRetorno = acessoBanco.leDado('pni_pontointeresse,zas_zonaautossalvamento', condicao, camposDesejados)

        if retorno == 404:
            return {"message": "Erro de acesso ao banco"}, 401, header

    # verifica a situação com relação à ZSS

        camposDesejados = 'pni_identificador, pni_descricao, zss_identificador, zss_texto'
        condicao = "where ST_Within(pni_pontointeresse.geom,zss_zonasecundaria.geom) and pae_identificador =  " + str(uhe)
        condicao = condicao + " and usu_identificador = " + str(usu_identificador)
        dadosPontosZSS, retorno, mensagemRetorno = acessoBanco.leDado('pni_pontointeresse,zss_zonasecundaria', condicao, camposDesejados)

        if retorno == 404:
            return {"message": "Erro de acesso ao banco"}, 401, header

# monta os dicionários
    listaZAS= []
    for i in range(len(dadosPontosZAS)):
        listaZAS.append(dadosPontosZAS[i][0])
    listaZSS= {}
    for i in range(len(dadosPontosZSS)):
        listaZSS.append(dadosPontosZSS[i][0])

    # verifica a situação com relação ao Sosem - a implementar
    listaSosem= []

# monta resposta
    dadosFinais = []
    for i in range(len(dadosPontos)):
        mensagemPontos = {}
        mensagemPontos["id"] = dadosPontos[i][0]
        mensagemPontos["nome"] = dadosPontos[i][1]
        mensagemPontos["endereco"] = dadosPontos[i][2]
        if dadosPontos[i][0] in listaSosem:
            mensagemPontos["situacao_SOSEM"] = "Area a ser inundada"
        else:
            mensagemPontos["situacao_SOSEM"] = "Fora de área inundada"
        if dadosPontos[i][0] in listaZAS:
            mensagemPontos["situacao_PAE"] = 'Dentro da ZAS'
        elif dadosPontos[i][0] in listaZSS:
            mensagemPontos["situacao_PAE"] = 'Dentro da ZSS'
        else:
            mensagemPontos["situacao_PAE"] = 'Fora da ZAS e da ZSS'

        dadosFinais.append(mensagemPontos)

    corpoMensagem = {}
    corpoMensagem['pontos'] = dadosFinais
    return corpoMensagem, 200, header

def rotaPontoEspecifico(ponto):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta['sub']

    mensagemPontoEspecifico = {}
    # verifica se o ponto específico existe e se ele está na ZAS
    camposDesejados = 'pni_identificador'
    condicao = "where pni_identificador =  " + str(ponto)
    dadosPontos, retorno, mensagemRetorno = acessoBanco.leDado('pni_pontointeresse', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosPontos) == 0:
        return {"message": "Ponto de Análiste inexistente."}, 400, header

    #verifica a situação com relação à ZAS
    camposDesejados = 'pni_identificador, pni_descricao, zas_identificador, zas_texto, pae_identificador'
    condicao = "where ST_Within(pni_pontointeresse.geom,zas_zonaautossalvamento.geom) and pni_identificador =  " + str(ponto)
    dadosPontosZAS, retorno, mensagemRetorno = acessoBanco.leDado('pni_pontointeresse,zas_zonaautossalvamento', condicao, camposDesejados)

    if retorno == 404:
            return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosPontosZAS) == 0:
        return {"message": "Ponto de Análise não está na ZAS."}, 400, header

    detalhePontoAnalise = {}
    detalhePontoAnalise['id_ponto'] = dadosPontosZAS[0][0]
    detalhePontoAnalise['nome_ponto'] = dadosPontosZAS[0][1]
    detalhePontoAnalise['ZAS'] = dadosPontosZAS[0][3]
    mensagemPontoEspecifico["ponto_analise"] = detalhePontoAnalise
    # obtem o trecho da rota mais próximo

    camposDesejados = "pni_pontointeresse.pni_identificador, st_distance(pni_pontointeresse.geom,tro_trechorotaevacuacao.geom) as distancia,"
    camposDesejados = camposDesejados + "tro_identificador"
    condicao = "where pni_pontointeresse.pni_identificador = " + str(ponto) + " order by distancia limit 1 "
    dadosPontosRota, retorno, mensagemRetorno = acessoBanco.leDado('pni_pontointeresse, tro_trechorotaevacuacao', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosPontosRota) == 0:
        return {"message": "Não foi localizada Rota de Evacuação para este Ponto de Análise."}, 400, header

    #recupera uma rota que contenha o trecho
    camposDesejados = 'rot_identificador'
    condicao = "WHERE tro_identificador = " + str(dadosPontosRota[0][2])
    dadosRota, retorno, mensagemRetorno = acessoBanco.leDado('rot_tro_rotaevacuacao_trechorotaevacuacao', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosRota) == 0:
        return {"message": "Não foi localizada a Rota de Evacuação."}, 400, header

    #recupera os trechos de rota
    trecho = []
    trecho_anterior = []
    trecho_nome = {}

    camposDesejados = 'tro_identificador, tro_anterior'
    condicao = "WHERE rot_identificador = " + str(dadosRota[0][0])
    dadosTrecho, retorno, mensagemRetorno = acessoBanco.leDado('rot_tro_rotaevacuacao_trechorotaevacuacao', condicao, camposDesejados)

    camposDesejados = 'rot_tro_rotaevacuacao_trechorotaevacuacao.tro_identificador, tro_anterior, tro_logradouro'
    condicao = "INNER JOIN tro_trechorotaevacuacao ON rot_tro_rotaevacuacao_trechorotaevacuacao.tro_identificador =  tro_trechorotaevacuacao.tro_identificador WHERE rot_identificador =" + str(dadosRota[0][0])
    dadosTrecho, retorno, mensagemRetorno = acessoBanco.leDado('rot_tro_rotaevacuacao_trechorotaevacuacao', condicao,
                                                               camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosTrecho) == 0:
        return {"message": "Esta UHE não possui trechos de rota de evacuação."}, 400, header

    for j in range(len(dadosTrecho)):
        trecho.append(dadosTrecho[j][0])
        trecho_anterior.append(dadosTrecho[j][1])
        trecho_nome[dadosTrecho[j][0]] = dadosTrecho[j][2]

    #encontra o caminho
    caminho= navega(trecho, trecho_anterior, dadosPontosRota[0][2])

    montaTrecho = []
    sequencia = 0
    for i in range(len(caminho)):
        mensagemTrechos = {}
        sequencia = sequencia + 1
        mensagemTrechos["id_trecho"] = caminho[i]
        mensagemTrechos["sequencia_trecho"] = sequencia
        mensagemTrechos["nome_trecho"] = trecho_nome[caminho[i]]
        montaTrecho.append(mensagemTrechos)
    mensagemPontoEspecifico["trechos"] = montaTrecho


    #recupera o ponto de segurança da rota
    camposDesejados = 'rot_pns_rotaevacuacao_pontoseguranca.pns_identificador, pns_identificacao'
    condicao = "INNER JOIN pns_pontoseguranca ON rot_pns_rotaevacuacao_pontoseguranca.pns_identificador = pns_pontoseguranca.pns_identificador WHERE rot_pns_rotaevacuacao_pontoseguranca.rot_identificador = " + str(
        dadosRota[0][0])
    dadosPonto, retorno, mensagemRetorno = acessoBanco.leDado('rot_pns_rotaevacuacao_pontoseguranca', condicao,
                                                              camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosPonto) == 0:
        return {"message": "Esta UHE não possui pontos de segurança."}, 400, header
    detalhePontoSeguranca = {}
    detalhePontoSeguranca['id_ponto'] = dadosPonto[0][0]
    detalhePontoSeguranca['nome_ponto'] = dadosPonto[0][1]
    mensagemPontoEspecifico["ponto_seguranca"] = detalhePontoSeguranca

    #recupera os dados da rota
    camposDesejados = 'rot_texto'
    condicao = "WHERE rot_identificador = " + str(dadosRota[0][0])
    dadosRotaEspec, retorno, mensagemRetorno = acessoBanco.leDado('rot_rotaevacuacao', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosRotaEspec) == 0:
        return {"message": "Esta UHE não possui rota."}, 400, header

    detalheRota = {}
    detalheRota['id_rota'] = dadosRota[0][0]
    detalheRota['nome_rota'] = dadosRotaEspec[0][0]
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
    caminho  = []
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
    cheque['message'] = ''
    erro = False

    if pni_descricao is None or len(pni_descricao) < 8:
        cheque['message'] = 'A descrição do Ponto de Análise é obrigatória'
        erro = True

    if x is not None and len(x) > 0:
        if not real(x):
            if not erro:
                cheque['message'] = "Coordenada 'X' é obrigatória e em formato real"
            else:
                cheque['message'] = cheque['message'] + " - Coordenada 'X' é obrigatória e em formato real"
            erro = True

    if y is not None and len(y) > 0:
        if not real(y):
            if not erro:
                cheque['message'] = "Coordenada 'Y' é obrigatória e em formato real"
            else:
                cheque['message'] = cheque['message'] + " - Coordenada 'Y' é obrigatória e em formato real"
            erro = True

    if erro:
        return cheque, 400

    camposDesejados = 'max(pni_identificador)'
    dados, retorno, mensagemRetorno = acessoBanco.leDado('pni_pontointeresse', None, camposDesejados)

    if retorno == 404:
        return {"message": "Erro no acesso ao banco de dados"}, retorno,{}

    if dados[0][0] is None:
        proximoNumero = 1
    else:
        proximoNumero = dados[0][0]  + 1

    if pni_endereco is None or len(pni_endereco) == 0:
        camposDesejados = 'pni_identificador, pni_descricao, usu_identificador, pni_identificadoratualizacao, pni_dataatualizacao, geom'
        valores = str(proximoNumero) + ",'" + pni_descricao + "'," + str(usu_identificador)
        valores = valores + ',' + str(usu_identificador) + ",'" + datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        valores = valores + "'," + "ST_GeomFromText('POINT(" + str(x) + " " + str(y) + ")', 3857)"
        pni_endereco = ''
    else:
        camposDesejados = 'pni_identificador, pni_descricao, pni_endereco, usu_identificador, pni_identificadoratualizacao, pni_dataatualizacao, geom'
        valores = str(proximoNumero)  + ",'" + pni_descricao + "','" + pni_endereco + "'," + str(usu_identificador)
        valores = valores + ',' + str(usu_identificador) + ",'" + datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        valores = valores + "'," + "ST_GeomFromText('POINT(" + str(x) + " " + str(y) + ")', 3857)"

    dados, retorno, header = acessoBanco.insereDado('pni_pontointeresse', camposDesejados, valores)
    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 404

    mensagemPontos = {}
    mensagemPontos["id"] = proximoNumero
    mensagemPontos["nome"] = pni_descricao
    mensagemPontos["endereco"] = pni_endereco
    mensagemPontos["x"] = x
    mensagemPontos["y"] = y

    corpoMensagem ={}
    corpoMensagem['ponto'] = mensagemPontos
    return corpoMensagem, 201


def real(value):
    try:
         float(value)
    except ValueError:
         return False
    return True