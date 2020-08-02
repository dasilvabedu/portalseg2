#!/usr/bin/python
# -*- coding: utf-8 -*-
import psycopg2
import os
from chatterbot import ChatBot
import datetime
import bcrypt
from app import config

# conecta ao servidor PostgreSQL
database_url = config.DATABASE_PROD_URL

def chatterbot(pergunta):

    bot = ChatBot(
        'midiasii',
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        database_uri=database_url)
    conta = 0

    while True:
        resposta = bot.get_response(pergunta)
        if float(resposta.confidence) > 0.5:
            break
        conta = conta + 1
        if conta > 5:
            resposta = None
            break

    return resposta

def dado(tabela, condicao=None, camposDesejados=None, limite = None):
    """ Lê uma tabela completa no Postgress """
    conn = None

    try:
    # conecta ao servidor PostgreSQL - Google cloud
        conn = psycopg2.connect(database_url)

    # conecta ao servidor PostgreSQL - Heroku
        #conn = psycopg2.connect(database_url, sslmode='require')

        if conn is None:
            return [], 404, "Conexão ao banco falhou"
    # criacao de cursor
        cur = conn.cursor()

    # executa o comando
        if (camposDesejados is None):
            colunas = "SELECT column_name, ordinal_position FROM information_schema.columns WHERE table_name = '" + tabela + "'"
            cur.execute(colunas)
            campos = ''
            recset = cur.fetchall()
            for rec in recset:
                campos = campos + rec[0] + ','
            if campos == '':
                cur.close()
                return [], 400, 'Tabela não encontrada'
            campos = campos[0:-1]
        else:
            campos = camposDesejados

        cada_campo = campos.split(',')
        campo_consulta = ''
        for nome_campo in cada_campo:
            if nome_campo != 'geom':
                campo_consulta = campo_consulta + nome_campo + ','
            else:
                campo_consulta = campo_consulta + 'ST_GeometryType(geom),'
        campo_consulta = campo_consulta[0:-1]

        comando = 'SELECT ' + campo_consulta + ' FROM ' + tabela

        if condicao is not None:
            comando = comando + ' ' + condicao
        if limite is not None:
            comando = comando + ' LIMIT ' + str(limite)
        resultado = []

        cur.execute(comando)
        recset = cur.fetchall()
        for rec in recset:
            registro = {}
            for i in range(len(cada_campo)):
                registro[cada_campo[i]] = rec[i]
            resultado.append(registro)
    # encerra conexao ao PostgreSQL
        cur.close()
        if resultado == []:
            return [], 200, ''
        else:
            return resultado, 200, ''

    except (Exception, psycopg2.DatabaseError) as error:
        return [], 404, 'Erro do sistema: ' + str(error)
    finally:
        if conn is not None:
            conn.close()

def alteraDado(tabela, valores, condicao=None):
    """ Atualiza uma tabela  no Postgress """
    conn = None

    try:
    # conecta ao servidor PostgreSQL - Google cloud
        conn = psycopg2.connect(database_url)

    # conecta ao servidor PostgreSQL - Heroku
        #conn = psycopg2.connect(database_url, sslmode='require')

        if conn is None:
            return [], 404, "Conexão ao banco falhou"
    # criacao de cursor
        cur = conn.cursor()

    # execucao de comando
        comando = "UPDATE " + tabela + " SET " + valores
        if condicao is not None:
            comando = comando + " " + condicao

        resultado = []
        cur.execute(comando)
        conn.commit()

    # encerra conexao ao PostgreSQL
        cur.close()
        return resultado, 200, ''

    except (Exception, psycopg2.DatabaseError) as error:
        return [], 404, 'Erro do sistema: ' + str(error)
    finally:
        if conn is not None:
            conn.close()

def leDado(tabela, condicao=None, camposDesejados=None):
    """ Lê uma tabela completa no Postgress """
    conn = None

    try:
    # conecta ao servidor PostgreSQL - Google cloud
        conn = psycopg2.connect(database_url)

    # conecta ao servidor PostgreSQL - Heroku
        #conn = psycopg2.connect(database_url, sslmode='require')

        if conn is None:
            return [], 404, "Conexão ao banco falhou"
    # criacao de cursor
        cur = conn.cursor()

    # execucao de comando
        if camposDesejados == None:
            comando = 'SELECT * FROM ' + tabela
        else:
            comando = "SELECT " + camposDesejados + " FROM " + tabela

        if condicao is not None:
            comando = comando + ' ' + condicao

        resultado = []
        cur.execute(comando)
        recset = cur.fetchall()
        for rec in recset:
            resultado.append(rec)

    # encerra conexao ao PostgreSQL
        cur.close()
        if resultado == []:
            return [], 400, 'Tabela e/ou campos inexistentes'
        else:
            return resultado, 200, ''

    except (Exception, psycopg2.DatabaseError) as error:
        return [], 404, 'Erro do sistema: ' + str(error)
    finally:
        if conn is not None:
            conn.close()

def insereDado(tabela, camposDesejados=None, valores=None):
    """ Atualiza uma tabela  no Postgress """
    conn = None
    try:
    # conecta ao servidor PostgreSQL - Google cloud
        conn = psycopg2.connect(database_url)

    # conecta ao servidor PostgreSQL - Heroku
        #conn = psycopg2.connect(database_url, sslmode='require')

        if conn is None:
            return [], 404, "Conexão ao banco falhou"
    # criacao de cursor
        cur = conn.cursor()

    # execucao de comando
        comando = "INSERT INTO " + tabela + " (" + camposDesejados + ") values (" + valores + ")"

        resultado = []
        cur.execute(comando)
        conn.commit()

    # encerra conexao ao PostgreSQL
        cur.close()
        return resultado, 201, ''

    except (Exception, psycopg2.DatabaseError) as error:
        return [], 404, 'Erro do sistema: ' + str(error)
    finally:
        if conn is not None:
            conn.close()

def exclueDado(tabela, condicao):
    """ Deleta registro de uma tabela  no Postgress """
    conn = None

    try:
    # conecta ao servidor PostgreSQL - Google cloud
        conn = psycopg2.connect(database_url)

    # conecta ao servidor PostgreSQL - Heroku
        #conn = psycopg2.connect(database_url, sslmode='require')

        if conn is None:
            return [], 404, "Conexão ao banco falhou"
    # criacao de cursor
        cur = conn.cursor()

    # execucao de comando
        comando = "DELETE FROM " + tabela
        if condicao is not None:
            comando = comando + ' ' + condicao
        resultado = []

        cur.execute(comando)
        conn.commit()

    # encerra conexao ao PostgreSQL
        cur.close()
        return resultado, 200, ""

    except (Exception, psycopg2.DatabaseError) as error:
        return [], 404, 'Erro do sistema: ' + str(error)
    finally:
        if conn is not None:
            conn.close()

def exclueMetadado(tabela):
    """ Exclue registro de mtt_metadadotabela e mta_metadadoatributo """
    conn = None

    try:
    # conecta ao servidor PostgreSQL - Google cloud
        conn = psycopg2.connect(database_url)
    # conecta ao servidor PostgreSQL - Heroku
        #conn = psycopg2.connect(database_url, sslmode='require')

        if conn is None:
            return [], 404, "Conexão ao banco falhou"
    # criacao de cursor
        cur = conn.cursor()

    # recupera os dados da tabela de metadados
        colunas = "SELECT mtt_identificador FROM mtt_metadadotabela WHERE mtt_tabela = '" + tabela + "'"
        cur.execute(colunas)
        recset = cur.fetchone()
        mtt_identificador = recset[0]

        comando = "DELETE FROM mta_metadadoatributo WHERE mtt_identificador = " + str(mtt_identificador)
        cur.execute(comando)

        comando = "DELETE FROM mtt_metadadotabela WHERE mtt_identificador = " + str(mtt_identificador)
        cur.execute(comando)

        conn.commit()

        resultado = []
        dicionario = {}
        dicionario['metadado'] = mtt_identificador
        resultado.append(dicionario)

    # encerra conexao ao PostgreSQL
        cur.close()
        if resultado == []:
            return [], 400, 'Tabela e/ou campos inexistentes'
        else:
            return resultado, 200, ''

    except (Exception, psycopg2.DatabaseError) as error:
        return [], 404, 'Erro do sistema: ' + str(error)
    finally:
        if conn is not None:
            conn.close()

def insereMetadado(tabela):
    """ Lê uma tabela completa no Postgress """
    conn = None

    try:
    # conecta ao servidor PostgreSQL - Google cloud
        conn = psycopg2.connect(database_url)

    # conecta ao servidor PostgreSQL - Heroku
        #conn = psycopg2.connect(database_url, sslmode='require')

        if conn is None:
            return [], 404, "Conexão ao banco falhou"
    # criacao de cursor
        cur = conn.cursor()

    # recupera os dados da tabela
        colunas = "SELECT column_name, ordinal_position, data_type FROM information_schema.columns WHERE table_name = '" + tabela + "'"
        cur.execute(colunas)
        dadosAtributo = []
        tipoTabela = 'convencional'

        recset = cur.fetchall()
        for rec in recset:
            if rec[0] == 'geom':
                tipoTabela = 'espacial'
            apoio=[]
            apoio.append(rec[0])
            apoio.append(rec[1])
            apoio.append(rec[2])
            dadosAtributo.append(apoio)
        if dadosAtributo == '':
            cur.close()
            return [], 400, 'Tabela não encontrada'

    # Recupera o ultimo valor dos identficadores
        comandoMetadado = "SELECT max(mtt_identificador) FROM mtt_metadadotabela"
        comandoAtributo = "SELECT max(mta_identificador) FROM mta_metadadoatributo"
        resultado = []

        cur.execute(comandoMetadado)
        proximoNumeroMetadado = cur.fetchone()[0] + 1

        cur.execute(comandoAtributo)
        atualNumeroAtributo = cur.fetchone()[0]

    # insere o registro em mtt_metadadotabela
        comando = "INSERT INTO mtt_metadadotabela (mtt_identificador, mtt_tabela, mtt_tipo) values (" + str(proximoNumeroMetadado) + ",'" + \
                  tabela + "','" + tipoTabela + "')"
        cur.execute(comando)

    # insere os registro em mta_metadadoatributo
        for dados in dadosAtributo:
            atualNumeroAtributo = atualNumeroAtributo + 1
            comando = "INSERT INTO mta_metadadoatributo (mtt_identificador, mta_identificador, mta_atributo, mta_sequencia, mta_tipo, mta_editavel) values (" + \
                      str(proximoNumeroMetadado) + "," + str(atualNumeroAtributo) + ",'" + dados[0] + "'," + str(dados[1]) +  ",'"+ dados[2] +"','não')"
            cur.execute(comando)
        conn.commit()

        dicionario = {}
        dicionario['metadado'] = proximoNumeroMetadado
        dicionario['atributo'] = atualNumeroAtributo
        resultado.append(dicionario)

    # encerra conexao ao PostgreSQL
        cur.close()
        if resultado == []:
            return [], 400, 'Dados inexistentes com estes parâmetros'
        else:
            return resultado, 201, ''

    except (Exception, psycopg2.DatabaseError) as error:
        return [], 404, 'Erro do sistema: ' + str(error)
    finally:
        if conn is not None:
            conn.close()

def exclueMetadadoAtributo(lista):
    """ Lê uma tabela completa no Postgress """
    conn = None

    try:

    # conecta ao servidor PostgreSQL - Google cloud
        conn = psycopg2.connect(database_url)

    # conecta ao servidor PostgreSQL - Heroku
        #conn = psycopg2.connect(database_url, sslmode='require')

        if conn is None:
            return [], 404, "Conexão ao banco falhou"
    # criacao de cursor
        cur = conn.cursor()

        for k in lista:
            tabela = k.split("###")[0]
            atributo = k.split("###")[1]

    # Recupera o identificador da tabela
            comandoTabela = "SELECT mtt_identificador FROM mtt_metadadotabela WHERE mtt_tabela = '" + tabela + "'"
            resultado = []
            cur.execute(comandoTabela)
            mtt_identificador = cur.fetchone()[0]

    # deleta o atributo
            comando = "DELETE FROM mta_metadadoatributo WHERE mtt_identificador = " + str(mtt_identificador) + " AND mta_atributo = '" + atributo + "'"
            cur.execute(comandoTabela)

        conn.commit()

        dicionario = {}
        resultado.append(dicionario)

    # encerra conexao ao PostgreSQL
        cur.close()
        if resultado == []:
            return [], 400, 'Dados inexistentes com estes parâmetros'
        else:
            return resultado, 201, ''

    except (Exception, psycopg2.DatabaseError) as error:
        return [], 404, 'Erro do sistema: ' + str(error)
    finally:
        if conn is not None:
            conn.close()

def insereMetadadoAtributo(lista):
    """ Lê uma tabela completa no Postgress """
    conn = None
    try:

        # conecta ao servidor PostgreSQL - Google cloud
        conn = psycopg2.connect(database_url)

        # conecta ao servidor PostgreSQL - Heroku
        # conn = psycopg2.connect(database_url, sslmode='require')

        if conn is None:
            return [], 404, "Conexão ao banco falhou"

        # criacao de cursor
        cur = conn.cursor()

        for k in lista:
            tabela = k.split("###")[0]
            atributo = k.split("###")[1]

            # recupera os dados da tabela
            colunas = "SELECT column_name, ordinal_position, data_type FROM information_schema.columns WHERE table_name = '" + tabela + "' AND column_name = '" + atributo + "'"
            cur.execute(colunas)
            dadosAtributo = []

            recset = cur.fetchall()
            for rec in recset:
                apoio = []
                apoio.append(rec[0])
                apoio.append(rec[1])
                apoio.append(rec[2])
                dadosAtributo.append(apoio)
            if dadosAtributo == []:
                cur.close()
                return [], 400, 'Tabela não encontrada'

            # Recupera o identificador da tabela
            comandoTabela = "SELECT mtt_identificador FROM mtt_metadadotabela WHERE mtt_tabela = '" + tabela + "'"
            resultado = []
            cur.execute(comandoTabela)
            mtt_identificador = cur.fetchone()[0]
            # Recupera o ultimo valor dos identificadores
            comandoAtributo = "SELECT max(mta_identificador) FROM mta_metadadoatributo"
            resultado = []

            cur.execute(comandoAtributo)
            atualNumeroAtributo = cur.fetchone()[0]
            # insere os registro em mta_metadadoatributo
            for dados in dadosAtributo:
                atualNumeroAtributo = atualNumeroAtributo + 1
                comando = "INSERT INTO mta_metadadoatributo (mtt_identificador, mta_identificador, mta_atributo, mta_sequencia, mta_tipo, mta_editavel) values (" + \
                          str(mtt_identificador) + "," + str(atualNumeroAtributo) + ",'" + dados[0] + "'," + str(
                    dados[1]) + ",'" + dados[2] + "','não')"
                cur.execute(comando)
        conn.commit()

        dicionario = {}
        dicionario['atributo'] = atualNumeroAtributo
        resultado.append(dicionario)

        # encerra conexao ao PostgreSQL
        cur.close()
        if resultado == []:
            return [], 400, 'Dados inexistentes com estes parâmetros'
        else:
            return resultado, 201, ''

    except (Exception, psycopg2.DatabaseError) as error:
        return [], 404, 'Erro do sistema: ' + str(error)
    finally:
        if conn is not None:
            conn.close()

def leMetadado(mtt_identificador,mtt_tabela,camposDesejados, atributosDesejado):
    query = "WHERE"
    if mtt_identificador:
        query = query + ' mtt_identificador=' + mtt_identificador +' AND'
    if mtt_tabela:
        query = query + " mtt_tabela='" + mtt_tabela +"' AND"
    if not (mtt_identificador or mtt_tabela):
        query = None
    else:
        query = query[:-4] + ';'

    resultadoAtributo = []
    resultadoTabela, retorno, mensagemRetorno = dado('mtt_metadadotabela', query, camposDesejados, None)
    if retorno != 200:
        return resultadoTabela, resultadoAtributo, retorno, mensagemRetorno

    if atributosDesejado:
        identificado = resultadoTabela[0]['mtt_identificador']
        query = 'WHERE mtt_identificador = ' + str(identificado)
        resultadoAtributo, retorno, mensagemRetorno = dado('mta_metadadoatributo', query, None, None)
    return resultadoTabela, resultadoAtributo, retorno, mensagemRetorno

def montaRetorno(retorno, mensagemRetorno):
    mensagem = {}
    mensagem['codigo'] = retorno
    mensagem['texto'] = 'Mensagem original: ' + mensagemRetorno
    if retorno == 200:
        mensagem['mensagem'] = 'Requisicao plenamente atendida'
    elif retorno == 201:
        mensagem['mensagem'] = 'Registro incluido'
    elif retorno == 400:
        mensagem['mensagem'] = 'Erro: condições de acesso inválidas'
    elif retorno == 401:
        mensagem['mensagem'] = 'Erro: acesso não autorizado'
    elif retorno == 404:
        mensagem['mensagem'] = 'Erro: acesso banco de dados'
    else:
        mensagem['mensagem'] = 'Erro: não identificado'
    resultado = {}
    resultado['aresposta'] = mensagem
    return resultado

def ordenaDicionario(atributoCampos, resultadoDado):
    # monta lista ordenada da sequencia de atributos
    tradutor = {}
    sequencia = 'ABCDEFGHIJKLMNPPQRSTU'
    for i in range(0, len(atributoCampos)):
        indice = atributoCampos[i]['mta_sequencia']
        valor = sequencia[indice - 1] + ' - '
        if atributoCampos[i]['mta_descricao'] is not None:
            valor = valor + atributoCampos[i]['mta_descricao']
        tradutor[atributoCampos[i]['mta_atributo']] = valor

    resultadoMontado = []
    for i in range(0, len(resultadoDado)):
        registro = {}
        listaChaves = resultadoDado[i].keys()

        for chave in listaChaves:
            novaChave = tradutor[chave] + ' (' + chave + ')'
            registro[novaChave] = resultadoDado[i][chave]
        resultadoMontado.append(registro)
    return resultadoMontado

# inclusao inicial de usuario
def insereUsuario(usu_celular, usu_email, usu_senha, usu_nome):
    """ Insere usuário e perfil inicial no Postgress """
    conn = None
    try:

        conn = psycopg2.connect(database_url)

        if conn is None:
            return [], 404, "Conexão ao banco falhou"

        # criacao de cursor
        cur = conn.cursor()

        #recupera o próximo identificador
        campo = 'max(usu_identificador)'
        dados, retorno, mensagemRetorno = leDado('usu_usuario', None, campo)
        if retorno != 200:
            resultadoFinal = montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, ''

        proximoNumero = dados[0][0] + 1

        # trata dos dados de sistema e inclui usuário
        agora = datetime.datetime.utcnow()
        iat = agora.strftime('%Y-%m-%d %H:%M:%S')
        salt = bcrypt.gensalt(rounds=12)
        senhaCriptografada = bcrypt.hashpw(usu_senha.encode('utf-8'), salt).decode('utf-8')

        campos = 'usu_identificador, usu_senha, usu_autenticacao, usu_nome, usu_identificadoratualizacao, usu_dataatualizacao '
        valores = str(proximoNumero) + ",'" + str(senhaCriptografada) + "','ativo','" + usu_nome + "'," + str(proximoNumero) + ",'" + iat + "'"
        if usu_celular is not None:
            campos = campos + ',usu_celular'
            valores = valores + "," + str(usu_celular)
        if usu_email is not None:
            campos = campos + ',usu_email'
            valores = valores + ",'" + usu_email + "'"

        dados, retorno, mensagemRetorno = insereDado('usu_usuario', campos, valores)
        if retorno != 201:
            resultadoFinal = montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, ''

        # inclui perfil
        campos = 'usu_identificador, pfa_identificador'
        valores = str(proximoNumero) + ", 2"
        dados, retorno, mensagemRetorno = insereDado('usu_pfa_usuario_perfilacesso', campos, valores)
        if retorno != 201:
            resultadoFinal = montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, ''

        dicionarioRetorno = {}
        dicionarioRetorno['sub'] = proximoNumero
        dicionarioRetorno['id'] = proximoNumero
        dicionarioRetorno['name'] = usu_nome
        dicionarioRetorno['iat'] = agora
        dicionarioRetorno['exp'] = ''
        dicionarioRetorno['user_role_ids'] = [2]
        dicionarioRetorno['allowed_transactions'] = []
        dicionarioRetorno['email'] = usu_email
        dicionarioRetorno['phone_number'] = usu_celular
        dicionarioRetorno['active'] = True

        # recupera as transacoes associadas
        camposdesejados = 'pfa_trn_perfilacesso_transacaosistema.trn_identificador'
        tabela = 'pfa_trn_perfilacesso_transacaosistema'
        condicao = 'INNER JOIN pfa_perfilacesso ON pfa_perfilacesso.pfa_identificador = pfa_trn_perfilacesso_transacaosistema.pfa_identificador WHERE pfa_perfilacesso.pfa_identificador = 2'

        dadosTransacao, retorno, mensagemRetorno = leDado(tabela, condicao, camposdesejados)
        if retorno == 404:
            resultadoFinal = montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, ''

        if dadosTransacao == []:
            conn.commit()
            return dicionarioRetorno, 201, ''
        else:
            transacoes = '('
            for i in range(len(dadosTransacao)):
                transacoes = transacoes + str(dadosTransacao[i][0]) + ','
        transacoes = transacoes[0:-1] + ')'

        # recupera o código das transações associadas
        camposdesejados = 'trn_codigo'
        tabela = 'trn_transacaosistema'
        condicao = 'WHERE trn_identificador IN '
        condicao = condicao + transacoes
        dadosCodigo, retorno, mensagemRetorno = leDado(tabela, condicao, camposdesejados)
        if retorno != 200:
            resultadoFinal = montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, ''

        codigoTransacao = []
        for i in range(len(dadosCodigo)):
            codigoTransacao.append('"' + str(dadosCodigo[i][0]) + '"')
        codigoTransacao = list(set(codigoTransacao))
        dicionarioRetorno['allowed_transactions'] = codigoTransacao

        conn.commit()

        return dicionarioRetorno, retorno, ''

        # encerra conexao ao PostgreSQL

        cur.close()

        resultado = {}
        resultado['usu_identificador'] = proximoNumero
        return resultado, 201, ''

    except (Exception, psycopg2.DatabaseError) as error:
        return [], 404, 'Erro do sistema: ' + str(error)
    finally:
        if conn is not None:
            conn.close()

def exclueUsuario(usu_identificador):
    """ Deleta usuário e perfis iniciais no Postgress """
    conn = None
    try:

        conn = psycopg2.connect(database_url)

        if conn is None:
            return False, {"message": "Conexão ao banco falhou"}

        # criacao de cursor
        cur = conn.cursor()

         # exclue perfil de acesso
        comando = 'DELETE FROM usu_pfa_usuario_perfilacesso WHERE usu_identificador=' + str(usu_identificador)
        cur.execute(comando)

         # exclue perfil de usuario
#        comando = 'DELETE FROM usu_pfu_usuario_perfilusuario WHERE usu_identificador=' + str(usu_identificador)
#        cur.execute(comando)

         # exclue usuário
        comando = 'DELETE FROM usu_usuario WHERE usu_identificador=' + str(usu_identificador)
        cur.execute(comando)

        conn.commit()

        return True, {}

        # encerra conexao ao PostgreSQL

        cur.close()


    except (Exception, psycopg2.DatabaseError) as error:
        return False, {"message": "Erro interno"}
    finally:
        if conn is not None:
            conn.close()

