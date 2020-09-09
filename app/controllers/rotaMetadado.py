# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoMetadado


@app.route("/seguranca_barragem/metadado/qualificado", methods=["GET"])
def api_metadado_qualificado():
    resultado, retorno, header = gestaoMetadado.metadadoQualificado()
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/metadado/selecionado", methods=["GET"])
def api_metadado_selecionado():
    resultado, retorno, header = gestaoMetadado.metadadoSelecionado()
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/metadado/total", methods=["GET"])
def api_metadado_total():
    resultado, retorno, header = gestaoMetadado.metadadoTotal()
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/metadado/validado", methods=["PATCH"])
def api_metadado_validado():
    resultado, retorno, header = gestaoMetadado.metadadoValidado()
    return jsonify(resultado), retorno, header
