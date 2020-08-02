# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoDado

@app.route('/seguranca_barragem/dado', methods=['GET'])
def home():
    return '''<h1>Acesso à base de Segurança de Barragens</h1>
<p>Endpoints disponíveis:</p>
<p>/seguranca_barragem/metadado/total?campos=(lista de campos) - recupera todos os registros da tabela MTT_MetadadoTabela. Se os campos forem fornecidos, traz apenas estes campos</p>
<p>/seguranca_barragem/metadado/selecionado?mtt_identificador=(identificador)&mtt_tabela=(tabela)&campos=(lista de campos) - recupera os campos da MTT_MetadadoTabela referente ao identificador ou tabela informado</p>
<p>/seguranca_barragem/metadado/qualificado?mtt_identificador=(identificador)&mtt_tabela=(tabela) - recupera os campos da MTT_MetadadoTabela e MTA_MetadadoAtributo referente ao identificador ou tabela informado</p>
<p>/seguranca_barragem/dado/qualificado?mtt_identificador=(identificador)&mtt_tabela=(tabela)&limite=(quantidade de dados a recuperar) - recupera os metadados da MTT_MetadadoTabela e MTA_MetadadoAtributo e os dados da tabela referente ao identificador ou tabela informado</p>
<p>/seguranca_barragem/dado/extenso?mtt_identificador=(identificador)&mtt_tabela=(tabela)&limite=(quantidade de dados a recuperar) - recupera os metadados da MTT_MetadadoTabela e MTA_MetadadoAtributo e os dados da tabela referente ao identificador ou tabela informado</p>'''

@app.route('/seguranca_barragem/dado/extenso', methods=['GET'])
def api_dado_extenso():
    resultado, retorno = gestaoDado.dadoExtenso()
    return jsonify(resultado), retorno

@app.route('/seguranca_barragem/dado/convencional/atualizado', methods=['GET','POST'])
def api_dado_convencional_atualizado():
    resultado, retorno = gestaoDado.dadoConvencionalAtualizado()
    return jsonify(resultado), retorno


@app.route('/seguranca_barragem/dado/excluido', methods=['GET','PUT'])
def api_dado_excluido():
    resultado, retorno = gestaoDado.dadoExcluido()
    return jsonify(resultado), retorno

@app.route('/seguranca_barragem/dado/qualificado', methods=['GET'])
def api_dado_qualificado():
    resultado, retorno = gestaoDado.dadoQualificado()
    return jsonify(resultado), retorno

