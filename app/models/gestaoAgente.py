# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao


def agentesMacro(uhe):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ""

    # verifica se existem agentes para a UHE
    camposDesejados = "age_agenteexterno.age_identificador, age_tipo, age_identificacao, age_endereco"
    condicao = "INNER JOIN pae_age_planoacaoemergencia_agenteexterno ON pae_age_planoacaoemergencia_agenteexterno.age_identificador = age_agenteexterno.age_identificador "
    condicao = (
        condicao
        + "INNER JOIN pae_planoacaoemergencia ON pae_planoacaoemergencia.pae_identificador = pae_age_planoacaoemergencia_agenteexterno.pae_identificador "
    )
    condicao = condicao + "WHERE pae_planoacaoemergencia.emp_identificador = " + str(uhe)
    dadosAgente, retorno, mensagemRetorno = acessoBanco.leDado("age_agenteexterno", condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosAgente) == 0:
        return {"message": "Esta UHE não possui agentes relacionados."}, 400, header

    # monta resposta
    dadosFinais = []
    for i in range(len(dadosAgente)):
        mensagemAgentes = {}
        mensagemAgentes["id"] = dadosAgente[i][0]
        mensagemAgentes["tipo"] = dadosAgente[i][1]
        mensagemAgentes["nome"] = dadosAgente[i][2]
        mensagemAgentes["endereco"] = dadosAgente[i][3]
        dadosFinais.append(mensagemAgentes)
    corpoMensagem = {}
    corpoMensagem["agentes"] = dadosFinais
    return corpoMensagem, 200, header


def agenteEspecifico(id_agente):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ""

    # recupera o dado do agente
    camposDesejados = "age_identificador, age_tipo, age_identificacao, age_endereco"
    condicao = "WHERE age_identificador = " + str(id_agente)
    dadosAgente, retorno, mensagemRetorno = acessoBanco.leDado("age_agenteexterno", condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosAgente) == 0:
        return {"message": "Esta UHE não possui agentes relacionados."}, 400, header

    # monta resposta
    mensagemAgentes = {}
    mensagemAgentes["id"] = dadosAgente[0][0]
    mensagemAgentes["tipo"] = dadosAgente[0][1]
    mensagemAgentes["nome"] = dadosAgente[0][2]
    mensagemAgentes["endereco"] = dadosAgente[0][3]
    corpoMensagem = {}
    corpoMensagem["agente"] = mensagemAgentes
    return corpoMensagem, 200, header
