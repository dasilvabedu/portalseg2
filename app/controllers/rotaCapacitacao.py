# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoCapacitacao

@app.route('/seguranca_barragem/modulos', methods=['POST','GET'])
def api_modulos():
    resultado, retorno, header = gestaoCapacitacao.moduloNovoLista()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/modulos/<int:id>', methods=['GET','PATCH','DELETE'])
def api_modulos_individuo(id):
    resultado, retorno, header = gestaoCapacitacao.moduloAtual(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/trilhas', methods=['POST','GET'])
def api_trilhas():
    resultado, retorno, header = gestaoCapacitacao.trilhaNovoLista()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/trilhas/<int:id>', methods=['GET','PATCH','DELETE'])
def api_trilhas_individuo(id):
    resultado, retorno, header = gestaoCapacitacao.trilhaAtual(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/trilhas/<int:id>/qualifica', methods=['POST','DELETE'])
def api_trilhas_qualifica(id):
    resultado, retorno, header = gestaoCapacitacao.trilhaQualifica(id)
    return jsonify(resultado), retorno, header