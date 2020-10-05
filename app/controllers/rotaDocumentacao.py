# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoDocumentacao


@app.route("/seguranca_barragem/documentos/<string:grupo>", methods=["GET"])
def api_documentacao_agrupado(grupo):
    resultado, retorno, header = gestaoDocumentacao.documentacaoAgrupado(grupo)
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/documentos", methods=["GET"])
def api_documentacao_lista():
    resultado, retorno, header = gestaoDocumentacao.documentacaoLista()
    return jsonify(resultado), retorno, header


@app.route("/seguranca_barragem/documento/<int:id>", methods=["GET","DELETE","PATCH"])
def list_objects(id):
    resultado, retorno, header = gestaoDocumentacao.documentacaoOriginalLeExcluiAltera(id)
    return jsonify(resultado), retorno, header

@app.route("/seguranca_barragem/documento", methods=["POST"])
def put_objects():
    resultado, retorno, header = gestaoDocumentacao.documentacaoOriginalInclui()
    return jsonify(resultado), retorno, header

@app.route("/seguranca_barragem/documento/chave", methods=["GET"])
def chave():
    resultado, retorno, header = gestaoDocumentacao.documentacaoOriginalChave()
    return jsonify(resultado), retorno, header