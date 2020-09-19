# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoUsuario


@app.route("/seguranca_barragem/users", methods=["POST", "GET"])
def api_usuario_users():
    resultado, retorno, header = gestaoUsuario.usuarioNovoLista()
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/users/<int:id>", methods=["GET", "PATCH", "DELETE"])
def api_usuario_atualiza(id):
    resultado, retorno, header = gestaoUsuario.usuarioAtual(id)
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/users/<int:id>/deactivate", methods=["PATCH"])
def api_usuario_inativo(id):
    resultado, retorno, header = gestaoUsuario.usuarioInativo(id)
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/users/recover", methods=["POST"])
def api_usuario_senha():
    resultado, retorno, header = gestaoUsuario.usuarioRecuperaSenha()
    return jsonify(resultado), retorno, header

@app.route("/seguranca_barragem/users/email", methods=["POST","GET"])
def api_usuario_email_inclui_lista():
    resultado, retorno, header = gestaoUsuario.emailIncluiLista()
    return jsonify(resultado), retorno, header

@app.route("/seguranca_barragem/users/email/<int:id>", methods=["DELETE"])
def api_usuario_email_exclui(id):
    resultado, retorno, header = gestaoUsuario.emailExclui(id)
    return jsonify(resultado), retorno, header

@app.route("/seguranca_barragem/users/telefone", methods=["POST","GET","DELETE"])
def api_usuario_telefone():
    resultado, retorno, header = gestaoUsuario.telefoneIncluiListaDeleta()
    return jsonify(resultado), retorno, header

