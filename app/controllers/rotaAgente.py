# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoAgente


@app.route("/seguranca_barragem/agentes/<int:id>", methods=["GET"])
def api_agentes_macro(id):
    resultado, retorno, header = gestaoAgente.agentesMacro(id)
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/agente/<int:id>", methods=["GET"])
def api_agente_especifico(id):
    resultado, retorno, header = gestaoAgente.agenteEspecifico(id)
    return jsonify(resultado), retorno, header
