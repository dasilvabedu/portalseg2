# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoPerfil


@app.route("/seguranca_barragem/qualificadores/<string:grupo>", methods=["POST", "GET"])
def api_qualificadores(grupo):
    resultado, retorno, header = gestaoPerfil.qualificadorNovoLista(grupo)
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/qualificadores/<string:grupo>/<int:id>", methods=["GET", "PATCH", "DELETE"])
def api_qualificadores_individuo(grupo, id):
    resultado, retorno, header = gestaoPerfil.qualificadorAtual(grupo, id)
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/acessos", methods=["POST", "GET"])
def api_acessos():
    resultado, retorno, header = gestaoPerfil.acessoNovoLista()
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/acessos/<int:id>", methods=["GET", "PATCH", "DELETE"])
def api_acessos_individuo(id):
    resultado, retorno, header = gestaoPerfil.acessoAtual(id)
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/perfis", methods=["POST", "GET"])
def api_perfis():
    resultado, retorno, header = gestaoPerfil.perfilNovoLista()
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/perfis/<int:id>", methods=["GET", "PATCH", "DELETE"])
def api_perfis_individuo(id):
    resultado, retorno, header = gestaoPerfil.perfilAtual(id)
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/transacoes", methods=["POST", "GET"])
def api_transacoes():
    resultado, retorno, header = gestaoPerfil.transacaoNovoLista()
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/transacoes/<int:id>", methods=["GET", "PATCH", "DELETE"])
def api_transacoes_individuo(id):
    resultado, retorno, header = gestaoPerfil.transacaoAtual(id)
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/acessos/<int:id>/qualifica", methods=["POST", "DELETE"])
def api_perfis_qualifica(id):
    resultado, retorno, header = gestaoPerfil.acessoQualifica(id)
    return jsonify(resultado), retorno, header
