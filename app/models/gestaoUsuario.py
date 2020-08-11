# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao, gestaoUsuario
from flask import request
import bcrypt
import datetime
from validate_email import validate_email

def trataLogin(usu_login, usu_senha):

    # valida parametros obrigatórios
    if usu_login is None or usu_senha is None or len(usu_login) < 4 or len(usu_senha) < 8:
        return {"message": "Usuário e/ou senha inválido(s)"}, 400, {}

    # realiza consulta no banco
    if inteiro(usu_login):
        condicao = "WHERE usu_autenticacao = 'ativo' and usu_celular = " + usu_login
    else:
        condicao = "WHERE usu_autenticacao = 'ativo' and usu_email = '" + usu_login + "'"
    dados, retorno, mensagemRetorno = acessoBanco.dado('usu_usuario', condicao, None, None)
    if retorno != 200:
        return {"message": "Erro de acesso ao banco"}, 404, {}

    # valida os dados do usuário
    volta = {}
    if dados == []:
        volta['message'] = 'Usuário não cadastrado'
    elif not bcrypt.checkpw(usu_senha.encode('utf-8'), dados[0]['usu_senha'].encode('utf-8')):
        volta['message'] = 'Senha não confere'
    elif dados[0]['usu_autenticacao'] != 'ativo':
        volta['message'] = 'Usuário inativo'

    if volta != {}:
        return volta, 400, {}

    agora = datetime.datetime.utcnow()
    dicionarioRetorno = {}
    dicionarioRetorno['sub'] = dados[0]['usu_identificador']
    dicionarioRetorno['id'] = dados[0]['usu_identificador']
    dicionarioRetorno['name'] = dados[0]['usu_nome']
    dicionarioRetorno['iat'] = agora
    dicionarioRetorno['exp'] = ''
    dicionarioRetorno['user_role_ids'] = []
    dicionarioRetorno['allowed_transactions'] = []
    dicionarioRetorno['email'] = dados[0]['usu_email']
    dicionarioRetorno['phone_number'] = dados[0]['usu_celular']
    dicionarioRetorno['active'] = True

    #recupera os perfis associados
    camposdesejados = 'usu_pfa_usuario_perfilacesso.pfa_identificador'
    tabela = 'usu_pfa_usuario_perfilacesso'
    condicao = 'INNER JOIN usu_usuario ON usu_usuario.usu_identificador = usu_pfa_usuario_perfilacesso.usu_identificador WHERE usu_usuario.usu_identificador = '
    condicao = condicao + str(dados[0]['usu_identificador'])

    dadosPerfil, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
    if retorno != 200 and retorno != 400:
        return {"message": "Erro de acesso ao banco"}, 404, {}

    if len(dadosPerfil) != 0:
        perfis =''
        listaPerfis = []
        for i in range(len(dadosPerfil)):
            perfis = perfis + str(dadosPerfil[i][0]) + ','
            listaPerfis.append(str(dadosPerfil[i][0]))
        perfis = perfis[0:-1]
        dicionarioRetorno['user_role_ids'] = listaPerfis

    #recupera as transacoes associadas
        camposdesejados = 'pfa_trn_perfilacesso_transacaosistema.trn_identificador'
        tabela = 'pfa_trn_perfilacesso_transacaosistema'
        condicao = 'INNER JOIN pfa_perfilacesso ON pfa_perfilacesso.pfa_identificador = pfa_trn_perfilacesso_transacaosistema.pfa_identificador WHERE pfa_perfilacesso.pfa_identificador IN '
        condicao = condicao + '(' + perfis + ')'
        dadosTransacao, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
        if retorno != 200 and retorno != 400:
            return {"message": "Erro de acesso ao banco"}, 404, {}

        if len(dadosTransacao) != 0:
            transacoes = '('
            for i in range(len(dadosTransacao)):
                transacoes = transacoes + str(dadosTransacao[i][0]) + ','
            transacoes = transacoes[0:-1] + ')'

        #recupera o código das transações associadas
            camposdesejados = 'trn_codigo'
            tabela = 'trn_transacaosistema'
            condicao = 'WHERE trn_identificador IN '
            condicao = condicao + transacoes
            dadosCodigo, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
            if retorno != 200 and retorno != 400:
                return {"message": "Erro de acesso ao banco"}, 404, {}

            codigoTransacao = []
            for i in range(len(dadosCodigo)):
                codigoTransacao.append('"' + str(dadosCodigo[i][0]) + '"')
            codigoTransacao = list(set(codigoTransacao))
            dicionarioRetorno['allowed_transactions'] = codigoTransacao

    # gera o token
    token = gestaoAutenticacao.geraToken(dicionarioRetorno)
    headerRetorno = {}
    headerRetorno['Authorization'] = 'Bearer ' + token
    return {"token": token }, 200, headerRetorno

def usuarioNovo():
    if not request.json:
        return {'"message": "Dados de entrada não fornecidos"'}, 400, {}

    entrada = request.json
    usu_celular = entrada.get('phone_number')
    usu_email = entrada.get('email')
    usu_senha = entrada.get('password')
    usu_nome = entrada.get('name')
    resultadoFinal, retorno, header = trataUsuarioIncluido(usu_celular, usu_email, usu_senha, usu_nome)
    return resultadoFinal, retorno, header

def usuarioAtual(id):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, {}

    if request.method == 'PATCH':
        #atualização de usuário
        if not request.json:
            return {'"message": "Dados de entrada não fornecidos"'}, 400, header

        entrada = request.json
        usu_celular = entrada.get('phone_number')
        usu_email = entrada.get('email')
        usu_senha = entrada.get('password')
        usu_nome = entrada.get('name')
        resultadoFinal, retorno = trataUsuarioAlterado(id, usu_celular, usu_email, usu_senha, usu_nome)
        return resultadoFinal, retorno, header
    elif request.method == 'DELETE':
        checa, mensagem = trataUsuarioDeletado(id)
        if not checa:
            return mensagem, 400, header
        return '',200, header
    return {"message":"Método invalido"}, 400, header

def usuarioInativo(id):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    campos = 'count(usu_identificador)'
    condicao = 'WHERE usu_identificador = ' + str(id)
    dados, retorno, mensagemRetorno = acessoBanco.leDado('usu_usuario', condicao, campos)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 404, header
    if dados[0][0] == 0:
        return {"message": "Usuário Inexistente"}, 400, header

    condicao = 'WHERE usu_identificador = ' + str(id)
    valores = "usu_autenticacao = 'inativo'"
    dados, retorno, mensagemRetorno = acessoBanco.alteraDado('usu_usuario', valores, condicao)
    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 404, header
    return {}, 200, {}

def usuarioExistente():
    if not request.json:
        return {'"message": "Dados de entrada não fornecidos"'}, 400, {}

    entrada = request.json
    usu_login = entrada.get('username')
    usu_senha = entrada.get('password')
    resultadoFinal, retorno, header = trataLogin(usu_login, usu_senha)
    return resultadoFinal, retorno, header

def usuarioTokenDesativado():

    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header

    campos = 'count(tki_identificador)'
    dados, retorno, mensagemRetorno = acessoBanco.leDado('tki_tokeninvalidado', None, campos)

    if retorno == 404:
        resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
        return {"message": "Erro de acesso ao banco"}, 404, header

    if dados[0][0] == 0:
        tki_identificador = 1
    else:
        campos = 'max(tki_identificador)'
        dados, retorno, mensagemRetorno = acessoBanco.leDado('tki_tokeninvalidado', None, campos)

        if retorno == 404:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return {"message": "Erro de acesso ao banco"}, 404, header

        tki_identificador = dados[0][0] + 1

    token, dadosToken = gestaoAutenticacao.expandeToken()
    campos = 'count(usu_identificador)'
    condicao = "WHERE usu_identificador = " + str(dadosToken['sub'])
    dados, retorno, mensagemRetorno = acessoBanco.leDado('usu_usuario', condicao, campos)
    if retorno == 404:
        resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
        return {"message": "Erro de acesso ao banco"}, 404, header

    if dados[0][0] == 0:
        return {"message": "Usuário foi apagado da base de dados"}, 400, {}

    campos = 'tki_identificador, usu_identificador, tki_token, tki_dataexpiracao, tki_identificadoratualizacao, tki_dataatualizacao'
    valores = str(tki_identificador) + "," + str(dadosToken['sub']) + ",'" + token + "','" + dadosToken['exp'].strftime('%Y-%m-%d %H:%M:%S')
    valores = valores + "'," + str(dadosToken['sub']) + ",'" + datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + "'"
    resultado, retorno, mensagem = acessoBanco.insereDado('tki_tokeninvalidado', campos, valores)
    if retorno != 201:
        return {"message": "Erro no acesso ao banco"},400,header
    return {}, 200, {}

def trataUsuarioIncluido(usu_celular, usu_email, usu_senha, usu_nome):

    cheque = {}
    cheque['message'] = ''
    erro = False

    if usu_senha is None or len(usu_senha) < 8:
        cheque['message'] = 'Senha é obrigatória, com tamanho mínimo de 8 caracteres'
        erro = True

    if (usu_celular is None or len(usu_celular) == 0) and (usu_email is None or len(usu_email) == 0 ):
        if not erro:
            cheque['message'] = 'Celular e Senha não podem ser ambos nulos'
        else:
            cheque['message'] = cheque['message'] + ' - Celular e Senha não podem ser ambos nulos'
        erro = True

    if usu_celular is not None and len(usu_celular) > 0:
        if not inteiro(usu_celular):
            if not erro:
                cheque['message'] = 'Celular deve ser numérico'
            else:
                cheque['message'] = cheque['message'] + ' - Celular deve ser numérico'
            erro = True
        elif int(usu_celular) < 10000000000 or int(usu_celular) > 99000000000:
            if not erro:
                cheque['message'] = 'Celular deve possuir 9 dígitos'
            else:
                cheque['message'] = cheque['message'] + ' - Celular deve possuir 9 dígitos'
            erro = True

    if usu_nome is None or len(usu_nome) < 1:
        if not erro:
            cheque['message'] = 'Nome do usuário é obrigatorio'
        else:
            cheque['message'] = cheque['message'] + ' - Nome do usuário é obrigatorio'
        erro = True

    if usu_email is not None and len(usu_celular) > 0:
        if not validate_email(usu_email):
            if not erro:
                cheque['message'] = 'Email invalido'
                erro = True
            else:
                cheque['message'] = cheque['message'] + ' - Email invalido'
            erro = True

    if erro:
        return cheque, 400, {}

    if usu_celular is not None:
        condicao = "WHERE usu_celular = " + str(usu_celular)
        if usu_email is not None:
            condicao = condicao + " or usu_email = '" + usu_email + "'"
    else:
        condicao = "WHERE usu_email = '" + usu_email + "'"

    camposDesejados = 'usu_autenticacao'
    dados, retorno, mensagemRetorno = acessoBanco.leDado('usu_usuario', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro no acesso ao banco de dados"}, retorno,{}

    if dados != []:
        autentica = ' '
        for i in range(len(dados)):
            if 'ativo' in dados[i]:
                autentica = 'ativo'
        if autentica == 'ativo':
            cheque['message'] = 'Celular ou e-mail já cadastrado com usuário ativo'
            return cheque, 400, {}

    dados, retorno, header = acessoBanco.insereUsuario(usu_celular, usu_email, usu_senha, usu_nome)
    print (str(retorno))
    if retorno != 201:
        return {"message": "Erro no acesso ao banco de dados"}, 404, {}

    # gera o token
    token = gestaoAutenticacao.geraToken(dados)
    dados.pop('exp')
    dados.pop('sub')
    dados.pop('iat')
    dados.pop('user_role_ids')
    dados.pop('allowed_transactions')
    headerRetorno = {}
    headerRetorno['Authorization'] = 'Bearer ' + token

    return dados, 201, headerRetorno

def trataUsuarioAlterado(id, usu_celular, usu_email, usu_senha, usu_nome):

    usu_identificador = id

    cheque = {}
    erro = False
    alteracao = False

    if usu_celular is not None and len(usu_celular) > 0:
        if not inteiro(usu_celular):
            if not erro:
                cheque['message'] ='Celular deve ser numérico'
            else:
                cheque['message'] = cheque['message'] + ' # Celular deve ser numérico'
            erro = True
        elif int(usu_celular) < 10000000000 or int(usu_celular) > 99000000000:
            if not erro:
                cheque['message'] ='Celular deve possuir 9 dígitos'
            else:
                cheque['message'] = cheque['message'] + ' # Celular deve possuir 9 dígitos'
            erro = True
        else:
            alteracao = True

    if usu_email is not None and len(usu_email) > 0:
        if validate_email(usu_email):
             alteracao = True
        else:
            if not erro:
                cheque['message'] = 'Email invalido'
            else:
                cheque['message'] = cheque['message'] + ' # Email invalido'
            erro = True

    if usu_nome is not None and len(usu_nome) > 0:
        alteracao = True

    if erro:
        return cheque, 400

    if not alteracao:
        cheque['message'] = 'Não existe(m) alteração(ões) a realizar'
        return cheque, 400

    campos = 'usu_celular, usu_email, usu_senha, usu_nome, usu_autenticacao'
    condicao = "WHERE usu_identificador = " + str(usu_identificador)
    dados, retorno, mensagemRetorno = acessoBanco.leDado('usu_usuario', condicao, campos)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco de dados"}, retorno

    if dados == []:
        cheque['message'] = 'Usuário não cadastrado'
        return cheque, 400

    if dados[0][4] != 'ativo':
        cheque['message'] = 'Usuário inativo'
        return cheque, 400

    usu_celular_ant = dados[0][0]
    usu_email_ant = dados[0][1]
    usu_senha_ant = dados[0][2]
    usu_nome_ant = dados[0][3]

    agora = datetime.datetime.utcnow()
    iat = agora.isoformat().replace('T', ' ') + 'Z'

    dicionarioRetorno = {}
    dicionarioRetorno['id'] = id
    dicionarioRetorno['name'] = usu_nome_ant
    dicionarioRetorno['email'] = usu_email_ant
    dicionarioRetorno['phone_number'] = usu_celular_ant
    dicionarioRetorno['active'] = True

    if usu_celular is not None:
        condicao = "WHERE usu_celular = " + str(usu_celular) + " AND usu_identificador <> " + str(usu_identificador)
        campos = ("usu_identificador")
        dados, retorno, mensagemRetorno = acessoBanco.leDado('usu_usuario', condicao, campos)

        if retorno == 404:
            return {"message": "Erro de acesso ao banco de dados"}, retorno

        if dados != []:
            cheque['message'] = 'Celular está cadastrado em nome de outro usuário'
            erro = True

        if usu_email is not None:
            condicao = "WHERE usu_email = '" + usu_email + "' AND usu_identificador <> " + str(usu_identificador)
            campos = ("usu_identificador")
            dicionarioRetorno['email'] = usu_email
            dados, retorno, mensagemRetorno = acessoBanco.leDado('usu_usuario', condicao, campos)

            if retorno == 404:
                return {"message": "Erro de acesso ao banco de dados"}, retorno

            if dados != []:
                if erro:
                    cheque['message'] = cheque['message'] + ' - Email já cadastrado em nome de outro usuário'
                else:
                    cheque['message'] = 'Email já cadastrado em nome de outro usuário'
                    erro = True

        if erro:
            return cheque, 400

    comando_cel = ''
    comando_email = ''
    comando_senha = ''
    comando_nome = ''

    if usu_celular is not None:
        dicionarioRetorno['phone_number'] = usu_celular
        comando_cel = ",usu_celular = " + str(usu_celular)

    if usu_email is not None:
        dicionarioRetorno['email'] = usu_email
        comando_email = ", usu_email = '" + usu_email + "'"

    if usu_senha is not None:
        if usu_senha != usu_senha_ant:
            comando_senha = ", usu_senha = '" + usu_senha + "'"

    if usu_nome is not None:
        if usu_nome != usu_nome_ant:
            dicionarioRetorno['name'] = usu_nome
            comando_nome = ", usu_nome = '" + usu_nome + "'"

    comando = comando_cel + comando_email + comando_senha + comando_nome
    if len(comando) == 0:
        return dicionarioRetorno, 200

    comando = comando [1:] + ", usu_dataatualizacao = '" + iat + "'"
    condicao = "WHERE usu_identificador = " + str(usu_identificador)
    dados, retorno, mensagemRetorno = acessoBanco.alteraDado('usu_usuario', comando, condicao)
    if retorno != 200:
        return {"message": "Erro de acesso ao banco de dados"}, retorno


    return dicionarioRetorno, 200

def trataUsuarioDeletado(id):

    usu_identificador = id

    condicao = "WHERE usu_identificador = " + str(usu_identificador)
    dados, retorno, mensagemRetorno = acessoBanco.leDado('usu_usuario', condicao, None)

    if retorno == 404:
        return False, {"message": "Erro de acesso ao banco de dados"}

    if dados == []:
        return False, {"message": "Usuário não cadastrado"}

    checa, mensagemRetorno = acessoBanco.exclueUsuario(usu_identificador)
    if not checa:
        return False, mensagemRetorno

    return True, {}

def inteiro(valor):
    try:
         int(valor)
    except ValueError:
         return False
    return True

def usuarioTransacaoValidada():
    checa, header = gestaoAutenticacao.validaToken()
    if not checa:
        resultadoFinal = acessoBanco.montaRetorno(401, 'Token inválido ou expirado')
        return resultadoFinal, 401, header

    query_parameters = request.args
    usu_login = query_parameters.get('login')
    trn_transacao = query_parameters.get('transacao')

    # valida parametros obrigatórios
    if usu_login is None or trn_transacao is None:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Usuário e/ou transação não fornecido(s)'
        resultadoFinal = acessoBanco.montaRetorno(400, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ' '
        return resultadoFinal, 400, header

    # realiza consulta no banco
    if inteiro(usu_login):
        condicao = "WHERE usu_autenticacao = 'ativo' and usu_celular = " + usu_login
    else:
        condicao = "WHERE usu_autenticacao = 'ativo' and usu_email = '" + usu_login + "'"
    camposDesejados = 'usu_identificador'
    dados, retorno, mensagemRetorno = acessoBanco.leDado('usu_usuario', condicao, camposDesejados)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno == 404:
        return resultadoFinal, retorno, header

    if dados == []:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Usuário não cadastrado'
        resultadoFinal = acessoBanco.montaRetorno(400, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ' '
        return resultadoFinal, 400, header

    usu_identificador = dados[0][0]

    #recupera os perfis associados
    camposdesejados = 'usu_pfa_usuario_perfilacesso.pfa_identificador'
    tabela = 'usu_pfa_usuario_perfilacesso'
    condicao = 'INNER JOIN usu_usuario ON usu_usuario.usu_identificador = usu_pfa_usuario_perfilacesso.usu_identificador WHERE usu_usuario.usu_identificador = '
    condicao = condicao + str(usu_identificador)
    dadosPerfil, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
    if retorno != 200:
        return resultadoFinal, retorno, header

    if dadosPerfil == []:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Usuário não possui perfil associado'
        resultadoFinal = acessoBanco.montaRetorno(400, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ''
        return resultadoFinal, 400, header
    else:
        perfis = ''
        for i in range(len(dadosPerfil)):
             perfis = perfis + str(dadosPerfil[i][0]) + ','
    perfis = perfis[0:-1]

    #recupera as transacoes associadas
    camposdesejados = 'pfa_trn_perfilacesso_transacaosistema.trn_identificador'
    tabela = 'pfa_trn_perfilacesso_transacaosistema'
    condicao = 'INNER JOIN pfa_perfilacesso ON pfa_perfilacesso.pfa_identificador = pfa_trn_perfilacesso_transacaosistema.pfa_identificador WHERE pfa_perfilacesso.pfa_identificador IN '
    condicao = condicao + '(' + perfis + ')'
    dadosTransacao, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
    if retorno != 200:
        return resultadoFinal, retorno, header

    if dadosTransacao == []:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Usuário não possui perfil com transação associada'
        resultadoFinal = acessoBanco.montaRetorno(400, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ''
        return resultadoFinal, 400, header
    else:
        transacoes = '('
        for i in range(len(dadosTransacao)):
            transacoes = transacoes + str(dadosTransacao[i][0]) + ','
    transacoes = transacoes[0:-1] + ')'

    #recupera o código das transações associadas
    camposdesejados = 'trn_codigo'
    tabela = 'trn_transacaosistema'
    condicao = 'WHERE trn_identificador IN '
    condicao = condicao + transacoes
    dadosCodigo, retorno, mensagemRetorno = acessoBanco.leDado(tabela, condicao, camposdesejados)
    if retorno != 200:
        return resultadoFinal, retorno, header

    for i in range(len(dadosCodigo)):
        if trn_transacao == (str(dadosCodigo[i][0])):
            listaMensagem = {}
            listaMensagem['acesso'] = 'ok'
            listaMensagem['texto'] = 'Transação validada'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ''
            return resultadoFinal, 200, header

    listaMensagem = {}
    listaMensagem['acesso'] = 'nok'
    listaMensagem['texto'] = 'Transacao não permitida para usuário'
    resultadoFinal = acessoBanco.montaRetorno(400, '')
    resultadoFinal['retorno'] = listaMensagem
    resultadoFinal['aresposta']['texto'] = ''
    return resultadoFinal, 400, header