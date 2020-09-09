# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoDado


@app.route("/seguranca_barragem/dado/extenso", methods=["GET"])
def api_dado_extenso():
    resultado, retorno, header = gestaoDado.dadoExtenso()
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/dado/convencional/atualizado", methods=["PATCH"])
def api_dado_convencional_atualizado():
    resultado, retorno, header = gestaoDado.dadoConvencionalAtualizado()
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/dado/qualificado", methods=["GET"])
def api_dado_qualificado():
    resultado, retorno, header = gestaoDado.dadoQualificado()
    return jsonify(resultado), retorno, header
