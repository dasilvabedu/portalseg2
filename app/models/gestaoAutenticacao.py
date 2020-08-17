import datetime

from flask import request
from ..views import acessoBanco
from ..models import gestaoUsuario
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
    print(dadosTrans)
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

def trataValidaToken(existe=None):

    token = request.headers.get('Authorization')
    if not token and existe is None:
        return False, {"message": "Header Authorization inexistente"}, {}

    if not token:
        token = 'Bearer ' + existe

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
            header['X-New-Bearer-Token'] = 'Bearer ' + novoToken
        return True, {}, header
    except:
       return False,{"message": "Token Inválido"},{}

def trataTokenAtual():

    if request.method == 'DELETE':
        checa, mensagem, header = trataValidaToken()
        if not checa:
            return mensagem, 400, header
        mensagem,retorno, novoheader = gestaoUsuario.usuarioTokenDesativado(header)
        return mensagem,retorno, novoheader
    elif request.method == 'GET':
        mensagem, retorno, novoheader = complementaToken()
        return mensagem, retorno, novoheader
    else:
        return {'message':'Método inválido'}, 400, header

def invalidaToken(token, dadosToken, header):

    # recupera o próximo identificador
    campo = 'max(tki_identificador)'
    dados, retorno, mensagemRetorno = acessoBanco.leDado('tki_tokeninvalidado', None, campo)
    if retorno != 200:
        resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
        return resultadoFinal, retorno, {}
    if dados[0][0] is None:
        proximoNumero = 1
    else:
        proximoNumero = dados[0][0] + 1

    # trata dos dados de sistema e inclui usuário
    agora = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    campos = 'tki_identificador, usu_identificador, tki_token, tki_dataexpiracao, tki_identificadoratualizacao, tki_dataatualizacao'
    valores = str(proximoNumero) + "," + dadosToken['sub'] + ",'" + token +"','" + dadosToken['iat'] + "'," + str(dadosToken['sub']) + ",'" + agora + "'"
    print (campos)
    print(valores)

    dados, retorno, mensagemRetorno = acessoBanco.insereDado('tki_tokeninvalidado', campos, valores)
    if retorno != 201:
        return 'Erro acesso ao banco', 400, header
    return '', 200, {}

def complementaToken(existe=None):
    existeToken = request.headers.get('Authorization')
    if existeToken is not None:
        checa, mensagem, header = trataValidaToken()
        if not checa:
            return mensagem, 400, header
        token, dadosToken = expandeToken()
    else:
        query_parameters = request.args
        existe = query_parameters.get('t')
        if existe is None:
            return {'message':'Token obrigatorio'},400,{}

        checa, mensagem, header = trataValidaToken(existe)
        if not checa:
            return mensagem, 400, header
        token, dadosToken = expandeToken(existe)


    mensagem = {}
    campo = 'usu_celular,usu_email,usu_autenticacao'
    condicao = "WHERE usu_identificador = " + str(dadosToken['sub'])
    dados, retorno, mensagemRetorno = acessoBanco.leDado('usu_usuario', condicao, campo)
    dadosToken['phone_number'] = str(dados[0][0])
    dadosToken['email'] = str(dados[0][1])
    if dados[0][2] == 'ativo':
        dadosToken['active'] = True
    else:
        dadosToken['active'] = False

    # recupera os celulares adicionais
    campo = 'uca_celular'
    condicao = "WHERE usu_identificador = " + str(dadosToken['sub'])
    dados, retorno, mensagemRetorno = acessoBanco.leDado('uca_celularadicional', condicao, campo)
    if retorno != 200:
        return {'message':'Erro de acesso ao banco'}, 400, header
    codigo = []
    for i in range(len(dados)):
        codigo.append(str(dados[i][0]))
    codigo = list(set(codigo))
    dadosToken['phone_others'] = codigo

    # recupera os emails adicionais
    campo = 'uea_email'
    condicao = "WHERE usu_identificador = " + str(dadosToken['sub'])
    dados, retorno, mensagemRetorno = acessoBanco.leDado('uea_emailadicional', condicao, campo)
    if retorno != 200:
        return {'message':'Erro de acesso ao banco'}, 400, header
    codigo = []
    for i in range(len(dados)):
        codigo.append(dados[i][0])
    codigo = list(set(codigo))
    dadosToken['email_others'] = codigo

    # recupera os nomes dos perfis de acesso
    codigo = []
    for perfil in dadosToken['user_role_ids']:
        campo = 'pfa_descricao'
        condicao = "WHERE pfa_identificador = " + perfil
        dados, retorno, mensagemRetorno = acessoBanco.leDado('pfa_perfilacesso', condicao, campo)
        if retorno != 200:
            return {'message':'Erro de acesso ao banco'}, 400, header
        codigo.append(dados[0][0])
    dadosToken['user_role_names'] = codigo

    #recupera os empreendimentos
    camposDesejados = 'emp_sigla, emp_nome,  usu_emp_usuario_empreendimento.emp_identificador'
    condicao = "INNER JOIN emp_empreendimento ON  usu_emp_usuario_empreendimento.emp_identificador = emp_empreendimento.emp_identificador "
    condicao = condicao + "where usu_identificador =  " + str(dadosToken['sub'])
    dados, retorno, mensagemRetorno = acessoBanco.leDado('usu_emp_usuario_empreendimento', condicao, camposDesejados)
    print(dados)
    sigla = []
    nome = []
    codigo = []
    for i in range(len(dados)):
        sigla.append(dados[i][0])
        nome.append(dados[i][1])
        codigo.append(str(dados[i][2]))
    dadosToken['site_codes'] = sigla
    dadosToken['site_names'] = nome
    dadosToken['site_ids'] = codigo

    #recupera os perfis de usuario
    camposDesejados = 'pfu_sigla, pfu_descricao'
    condicao = "INNER JOIN pfu_perfilusuario ON  usu_pfu_usuario_perfilusuario.pfu_identificador = pfu_perfilusuario.pfu_identificador "
    condicao = condicao + "where usu_identificador =  " + str(dadosToken['sub'])
    dados, retorno, mensagemRetorno = acessoBanco.leDado('usu_pfu_usuario_perfilusuario', condicao, camposDesejados)
    print(dados)
    sigla = []
    nome = []
    for i in range(len(dados)):
        sigla.append(dados[i][0])
        nome.append(dados[i][1])
    dadosToken['trainning_codes'] = sigla
    dadosToken['trainning_names'] = nome

    #prepara a volta
    dadosToken.pop('exp')
    dadosToken.pop('iat')
    dadosToken.pop('iatdt')
    return dadosToken, 200, header

def expandeToken(codificado=None):
    existeToken = request.headers.get('Authorization')
    if existeToken is not None:
        codificado = existeToken[7:]
    elif codificado is None:
        return {'message':'Token obrigatorio'},400,{}

    volta = jwt.decode(codificado.encode('utf-8'), chave, algorithms='HS256')
    iatdt = datetime.datetime.strptime(str(volta['iat']),'%Y%m%d%H%M%S%f')
    expiracao = iatdt + datetime.timedelta(minutes=duracao)
    volta['exp'] = expiracao
    volta['iatdt'] = iatdt
    return codificado, volta



