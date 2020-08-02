# -*- coding: utf-8 -*-

from app import app
from flask import jsonify

@app.errorhandler(404)
def page_not_found(e):
    mensagem = {}
    mensagem['codigo'] = 404
    mensagem['mensagem'] = 'Funcionalidade nao encontrada'
    mensagem['texto'] = 'Mensagem original: ' + str(e)
    resultado = {}
    resultado['aresposta'] = mensagem
    return jsonify(resultado), 404
