import datetime

from flask import request
from ..views import acessoBanco
import jwt
import datetime
from app import config

# obtem o 'SECRET_KEY'
chave = config.SECRET_KEY

#obtem o tempo de duração do Token
duracao = config.DURACAO_TOKEN

def geraToken(dados):
    # Gerando token com base em cadeia de caracteres aleatórias e definindo expiração

    dadosRole =  dados['user_role_ids']
    if len(dadosRole) == 0:
        roleString = '[]'
    else:
        roleString = '['
        for i in range(len(dadosRole)):
            roleString = roleString + str(dadosRole[i]) + ','
        roleString = roleString[0:-1] + ']'

    dadosTrans = dados['allowed_transactions']
    if len(dadosTrans) == 0:
        transString = '[]'
    else:
        transString = '['
        for i in range(len(dadosTrans)):
            transString = transString + str(dadosTrans[i]) + ','
        transString = transString[0:-1] + ']'

    agora = dados['iat']
    iat = int(agora.strftime('%Y%m%d%H%M%S%f'))

    dicionarioPayload = {}
    dicionarioPayload['sub'] = dados['sub']
    dicionarioPayload['name'] = dados['name']
    dicionarioPayload['iat'] = iat
    dicionarioPayload['user_role_ids'] = dados['user_role_ids']
    dicionarioPayload['allowed_transactions'] = dados['allowed_transactions']

    token = jwt.encode(dicionarioPayload, chave, algorithm='HS256')

    return token.decode('UTF-8')

def trataValidaToken():

    token = request.headers.get('Authorization')
    if not token:
        return False, {"message": "Header Authorization inexistente"}, {}

    prefixo = token[0:6]
    codificado = token[7:]
    if prefixo != 'Bearer':
        return False,{"message": "Header Authorization não é Bearer"}, {}

    try:
        header = {}
        header['Authorization'] = token
        volta = jwt.decode(codificado.encode('utf-8'), chave, algorithms='HS256')
        agora = datetime.datetime.utcnow()
        novoIat = int(agora.strftime('%Y%m%d%H%M%S%f'))
        difIat = novoIat - volta['iat']
        iatdt = datetime.datetime.strptime(str(volta['iat']),'%Y%m%d%H%M%S%f')
        expiracao = iatdt + datetime.timedelta(minutes=duracao)
        if expiracao < agora:
            return False, {"message": "Token Expirado"}, {}

        #verifica se o token está na lista de tokens invalidos
        campos = 'count(tki_identificador)'
        condicao = "WHERE tki_token = '" + codificado + "'"
        dados, retorno, mensagemRetorno = acessoBanco.leDado('tki_tokeninvalidado', condicao, campos)
        if retorno == 404:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return {"message": "Erro de acesso ao banco"}, 404, header
        if dados[0][0] != 0:
            return False, {"message": "Token na lista de inválidos"}, {}

        # gera novo token, se faltar menos que 25% do tempo
        quarto = int(duracao/4)
        expiracao = (iatdt + datetime.timedelta(minutes=quarto))
        if expiracao < agora:
            volta['iat'] = agora
            novoToken = geraToken(volta)
            header['X-New-Bearer-Token'] = novoToken
        return True, {}, header
    except:
       return False,{"message": "Token Inválido"},{}

def expandeToken():

    token = request.headers.get('Authorization')
    codificado = token[7:]
    volta = jwt.decode(codificado.encode('utf-8'), chave, algorithms='HS256')
    iatdt = datetime.datetime.strptime(str(volta['iat']),'%Y%m%d%H%M%S%f')
    expiracao = iatdt + datetime.timedelta(minutes=duracao)
    volta['exp'] = expiracao
    volta['iatdt'] = iatdt
    return codificado, volta



