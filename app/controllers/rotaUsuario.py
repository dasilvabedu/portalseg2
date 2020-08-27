# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoUsuario

@app.route('/seguranca_barragem/users', methods=['POST','GET'])
def api_usuario_users():
    resultado, retorno, header = gestaoUsuario.usuarioNovoLista()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/users/<int:id>', methods=['GET','PATCH','DELETE'])
def api_usuario_atualiza(id):
    resultado, retorno, header = gestaoUsuario.usuarioAtual(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/users/<int:id>/deactivate', methods=['PATCH'])
def api_usuario_inativo(id):
    resultado, retorno, header = gestaoUsuario.usuarioInativo(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/users/recover', methods=['POST'])
def api_usuario_senha():
    resultado, retorno, header = gestaoUsuario.usuarioRecuperaSenha()
    return jsonify(resultado), retorno, header
