# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoMetadado


@app.route('/seguranca_barragem/metadado', methods=['GET'])
def nada():
    return '''<h1>Acesso à base de Segurança de Barragens</h1>
<p>Endpoints disponíveis:</p>
<p>/seguranca_barragem/metadado/total?campos=(lista de campos) - recupera todos os registros da tabela MTT_MetadadoTabela. Se os campos forem fornecidos, traz apenas estes campos</p>
<p>/seguranca_barragem/metadado/selecionado?mtt_identificador=(identificador)&mtt_tabela=(tabela)&campos=(lista de campos) - recupera os campos da MTT_MetadadoTabela referente ao identificador ou tabela informado</p>
<p>/seguranca_barragem/metadado/qualificado?mtt_identificador=(identificador)&mtt_tabela=(tabela) - recupera os campos da MTT_MetadadoTabela e MTA_MetadadoAtributo referente ao identificador ou tabela informado</p>
<p>/seguranca_barragem/dado/qualificado?mtt_identificador=(identificador)&mtt_tabela=(tabela)&limite=(quantidade de dados a recuperar) - recupera os metadados da MTT_MetadadoTabela e MTA_MetadadoAtributo e os dados da tabela referente ao identificador ou tabela informado</p>
<p>/seguranca_barragem/dado/extenso?mtt_identificador=(identificador)&mtt_tabela=(tabela)&limite=(quantidade de dados a recuperar) - recupera os metadados da MTT_MetadadoTabela e MTA_MetadadoAtributo e os dados da tabela referente ao identificador ou tabela informado</p>'''

@app.route('/seguranca_barragem/metadado/aptoexclusao', methods=['GET'])
def api_metadado_aptoexclusao():
    resultado, retorno = gestaoMetadado.metadadoAptoExclusao()
    return jsonify(resultado), retorno

@app.route('/seguranca_barragem/metadado/atualizado', methods=['POST'])
def api_metadado_atualizado():
    resultado, retorno = gestaoMetadado.metadadoAtualizado()
    return jsonify(resultado), retorno

@app.route('/seguranca_barragem/metadado/excluido', methods=['DELETE'])
def api_metadado_excluido():
    resultado, retorno = gestaoMetadado.metadadoExcluido()
    return jsonify(resultado), retorno

@app.route('/seguranca_barragem/metadado/inserido', methods=['POST'])
def api_metadado_inserido():
    resultado, retorno = gestaoMetadado.metadadoInserido()
    return jsonify(resultado), retorno

@app.route('/seguranca_barragem/metadado/qualificado', methods=['GET'])
def api_metadado_qualificado():
    resultado, retorno, header = gestaoMetadado.metadadoQualificado()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/metadado/selecionado', methods=['GET'])
def api_metadado_selecionado():
    resultado, retorno = gestaoMetadado.metadadoSelecionado()
    return jsonify(resultado), retorno

@app.route('/seguranca_barragem/metadado/total', methods=['GET'])
def api_metadado_total():
    resultado, retorno, header = gestaoMetadado.metadadoTotal()
    return jsonify(resultado), retorno, header

@app.route('/seguranca_barragem/metadado/validado', methods=['GET'])
def api_metadado_validado():
    resultado, retorno = gestaoMetadado.metadadoValidado()
    return jsonify(resultado), retorno

@app.route('/seguranca_barragem/metadado/atributo/validado', methods=['GET'])
def api_metadado_atributo_validado():
    resultado, retorno = gestaoMetadado.metadadoAtributoValidado()
    return jsonify(resultado), retorno