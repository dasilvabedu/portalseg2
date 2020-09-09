# -*- coding: utf-8 -*-

from app import app
from flask import jsonify
from ..models import gestaoChatterbot


@app.route("/seguranca_barragem/chatterbot", methods=["GET"])
def api_chatterbot_resposta():
    resultado, retorno, header = gestaoChatterbot.chatterbotResposta()
    return jsonify(resultado), retorno, header
