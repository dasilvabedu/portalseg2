# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request
import re

def chatterbotResposta():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    query_parameters = request.args
    pergunta = query_parameters.get('pergunta')
    if pergunta is None:
        return {"message": "Não fornecido o parâmetro de pesquisa"}, 400, header

    corpoMensagem = {}
    corpoMensagem['pergunta'] = pergunta

    resposta = acessoBanco.chatterbot(pergunta)

    if resposta is not None:
        corpoMensagem['resposta'] = str(resposta)
    else:
        corpoMensagem['resposta'] = 'Desculpas, mas não posso esclarecer esta questão.'

    return corpoMensagem, 200, header

