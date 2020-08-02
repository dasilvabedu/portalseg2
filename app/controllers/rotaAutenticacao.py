# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoAutenticacao

@app.route('/seguranca_barragem/tokens', methods=['GET','POST'])
def api_autenticacao_lista():
    resultado, retorno, header = gestaoAutenticacao.verificaToken()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/tokens/<int:id>', methods=['GET','PUT','DELETE'])
def api_autenticacao_gestao(id):
    resultado, retorno, header = gestaoAutenticacao.administraToken(id)
    return jsonify(resultado), retorno, header
