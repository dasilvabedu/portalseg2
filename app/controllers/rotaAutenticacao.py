# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoAutenticacao, gestaoUsuario

@app.route('/seguranca_barragem/token', methods=['GET','DELETE'])
def api_autenticacao_atual():
    resultado, retorno, header = gestaoAutenticacao.trataTokenAtual()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/tokens', methods=['POST'])
def api_usuario_tokens():
    resultado, retorno, header = gestaoUsuario.usuarioExistente()
    return jsonify(resultado), retorno, header

