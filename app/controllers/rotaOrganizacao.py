# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoOrganizacao

@app.route('/seguranca_barragem/organizacao/geral', methods=['GET'])
def api_organizacao_geral():
    resultado, retorno, header = gestaoOrganizacao.organizacaoGeral()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/organizacao/cadastrado', methods=['GET'])
def api_organizacao_cadastrado():
    resultado, retorno, header = gestaoOrganizacao.organizacaoCadastrado()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/organizacao/incluido', methods=['GET','POST'])
def api_organizacao_incluido():
    resultado, retorno, header = gestaoOrganizacao.organizacaoIncluido()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/organizacao/alterado', methods=['GET','PUT'])
def api_organizacao_alterado():
    resultado, retorno, header = gestaoOrganizacao.organizacaoAlterado()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/organizacao/excluido', methods=['GET','PUT'])
def api_organizacao_excluido():
    resultado, retorno, header = gestaoOrganizacao.organizacaoExcluido()
    return jsonify(resultado), retorno, header

