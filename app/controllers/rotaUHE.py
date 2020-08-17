# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoUHE

@app.route('/seguranca_barragem/rotas/<int:id>', methods=['GET'])
def api_rotas_ordenadas(id):
    resultado, retorno, header = gestaoUHE.rotasOrdenadas(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/pontosuhe/<int:id>', methods=['GET'])
def api_rotas_pontosuhe(id):
    resultado, retorno, header = gestaoUHE.pontosUHE(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/pontosuhe/<int:id>/analyse', methods=['GET'])
def api_rotas_pontosuheanalise(id):
    resultado, retorno, header = gestaoUHE.pontosUHEAnalise(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/rota/<int:id>', methods=['GET'])
def api_rotas_rotaponto(id):
    resultado, retorno, header = gestaoUHE.rotaPontoEspecifico(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/pontos', methods=['GET','POST'])
def api_rotas_pontos():
    resultado, retorno, header = gestaoUHE.pontosUsuario()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/pontos/<int:id>', methods=['GET','DELETE','PATCH'])
def api_rotas_pontosatuais(id):
    resultado, retorno, header = gestaoUHE.pontosAtual(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/vazoes/<int:id>', methods=['GET'])
def api_vazoes(id):
    resultado, retorno, header = gestaoUHE.vazoesTotal(id)
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/vazao', methods=['GET'])
def api_vazao_especifica():
    resultado, retorno, header = gestaoUHE.vazaoEspecifica()
    return jsonify(resultado), retorno, header
