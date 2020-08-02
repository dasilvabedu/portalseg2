# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoUsuario, gestaoAutenticacao

@app.route('/seguranca_barragem/users', methods=['POST'])
def api_usuario_users():
    resultado, retorno, header = gestaoUsuario.usuarioNovo()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/tokens', methods=['POST'])
def api_usuario_tokens():
    resultado, retorno, header = gestaoUsuario.usuarioExistente()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/token', methods=['DELETE'])
def api_usuario_token():
    resultado, retorno, header = gestaoUsuario.usuarioTokenDesativado()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/users/<int:id>', methods=['PATCH','DELETE'])
def api_usuario_atualiza(id):
    resultado, retorno, header = gestaoUsuario.usuarioAtual(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/users/<int:id>/deactivate', methods=['PATCH'])
def api_usuario_inativo(id):
    resultado, retorno, header = gestaoUsuario.usuarioInativo(id)
    return jsonify(resultado), retorno, header
