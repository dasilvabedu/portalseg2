# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoMorador


@app.route('/seguranca_barragem/moradores/<int:id>', methods=['GET'])
def api_moradores_macro(id):
    resultado, retorno, header = gestaoMorador.moradoresMacro(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/morador/<int:id>', methods=['GET'])
def api_morador_especifico(id):
    resultado, retorno, header = gestaoMorador.moradorEspecifico(id)
    return jsonify(resultado), retorno, header
