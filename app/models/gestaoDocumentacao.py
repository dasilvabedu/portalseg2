# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request
from .. import config
import boto3
import random


def documentacaoGeral():
    camposDesejados = "doc_grupo,doc_nome,doc_descricao,doc_arquivo"
    condicao = "WHERE doc_grupo = 'geral'"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("doc_documentacaoassociada", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, retorno, {}
    if dados == []:
        return {}, 200, {}

    retorna = []
    for i in range(len(dados)):
        lista = {}
        lista["grupo"] = dados[i][0]
        lista["nome"] = dados[i][1]
        lista["descricao"] = dados[i][2]
        lista["arquivo"] = dados[i][3]
        retorna.append(lista)

    listaMensagem = {}
    listaMensagem["documentos"] = retorna
    return listaMensagem, retorno, {}


def documentacaoAgrupado(grupo=None):
    nomeUHE = []
    if grupo == "geral":
        header = {}
        camposDesejados = "doc_grupo,doc_nome,doc_descricao,doc_arquivo, doc_identificador"
        condicao = "WHERE doc_grupo = '" + grupo + "'"
        dados, retorno, mensagemRetorno = acessoBanco.leDado("doc_documentacaoassociada", condicao, camposDesejados)

    else:
        checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
        if not checa:
            return mensagem, 400, header
        query_parameters = request.args
        uhe = query_parameters.get("emp")
        print (grupo, " - ", uhe)
        if uhe is not None:
            if not acessoBanco.inteiro(uhe):
                return {"message": "Parâmetros 'emp' inválido"}, 404, header
            else:
                camposDesejados = "emp_nome"
                condicao = (
                        "WHERE emp_identificador = "
                        + str(uhe)
                )
                dadosUHE, retorno, mensagemRetorno = acessoBanco.leDado(
                    "emp_empreendimento",
                    condicao,
                    camposDesejados,
                )
                if retorno == 400:
                    return {"message": "Erro de acesso ao banco"}, 400, header
                elif retorno != 200:
                    return {"message": "Empreendimento não existe"}, 404, header
                nomeUHE.append([dadosUHE[0][0]])
                camposDesejados = "a.doc_grupo,a.doc_nome,a.doc_descricao,a.doc_arquivo, a.doc_identificador"
                condicao = (
                        "WHERE a.doc_grupo = '"
                        + grupo
                        + "' and a.doc_identificador = b.doc_identificador and b.emp_identificador = "
                        + str(uhe)
                )
                dados, retorno, mensagemRetorno = acessoBanco.leDado(
                    "doc_documentacaoassociada as a, doc_emp_documentacaoassociada_empreendimento as b",
                    condicao,
                    camposDesejados,
                )
                if retorno == 400:
                    return {"message": "Erro de acesso ao banco"}, 400, header
        else:
            camposDesejados = "a.doc_grupo,a.doc_nome,a.doc_descricao,a.doc_arquivo, a.doc_identificador"
            condicao = (
                "WHERE a.doc_grupo = '"
                + grupo
                + "'"
            )
            dados, retorno, mensagemRetorno = acessoBanco.leDado(
                "doc_documentacaoassociada as a",
                condicao,
                camposDesejados,
            )
            if retorno == 400:
                return {"message": "Erro de acesso ao banco"}, 400, header

            nomeUHE = []
            for i in range(len(dados)):
                camposDesejados = "e.emp_nome"
                condicao = (
                        "WHERE b.doc_identificador = "
                        + str(dados[i][4]) +
                        " AND b.emp_identificador = e.emp_identificador"
                )
                dadosUHE, retorno, mensagemRetorno = acessoBanco.leDado(
                    "doc_emp_documentacaoassociada_empreendimento as b, emp_empreendimento as e",
                    condicao,
                    camposDesejados,
                )
                print(dadosUHE, " - ", retorno)
                if retorno == 400:
                    return {"message": "Erro de acesso ao banco"}, 400, header
                elif retorno != 200:
                    nomeUHE.append(["Todos os empreendimentos"])
                else:
                    listUHE = []
                    for j in range(len(dadosUHE)):
                        listUHE.append(dadosUHE[j][0])
                    nomeUHE.append(listUHE)
    print(nomeUHE, ' - ', len(nomeUHE))

    retorna = []
    print(len(dados))
    for i in range(len(dados)):
        print (i)
        lista = {}
        lista["grupo"] = dados[i][0]
        if grupo != "geral":
            lista["empreendimento"] = nomeUHE[i]
        else:
            lista["empreendimento"] = ["Todos os empreendimentos"]
        lista["titulo"] = dados[i][1]
        lista["descricao"] = dados[i][2]
        lista["arquivo"] = dados[i][3]
        lista["identificador"] = dados[i][4]
        retorna.append(lista)

    listaMensagem = {}
    listaMensagem["documentos"] = retorna
    return listaMensagem, 200, header


def documentacaoLista():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header
    camposDesejados = "doc_grupo,doc_nome,doc_descricao,doc_arquivo, doc_identificador "
    dados, retorno, mensagemRetorno = acessoBanco.leDado("doc_documentacaoassociada", None, camposDesejados)

    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, retorno, {}
    if dados == []:
        return [], 200, {}

    retorna = []
    for i in range(len(dados)):
        lista = {}
        lista["grupo"] = dados[i][0]
        lista["nome"] = dados[i][1]
        lista["descricao"] = dados[i][2]
        lista["arquivo"] = dados[i][3]
        lista["identificador"] = dados[i][4]
        nomeUHE = []

        camposDesejados = "e.emp_nome"
        condicao = (
                "WHERE b.doc_identificador = "
                + str(dados[i][4]) +
                " AND b.emp_identificador = e.emp_identificador"
        )
        dadosUHE, retorno, mensagemRetorno = acessoBanco.leDado(
            "doc_emp_documentacaoassociada_empreendimento as b, emp_empreendimento as e",
            condicao,
            camposDesejados,
        )
        print(dadosUHE, " - ", retorno)
        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header
        elif retorno != 200:
            nomeUHE.append(["Todos os empreendimentos"])
        else:
            listUHE = []
            for j in range(len(dadosUHE)):
                listUHE.append(dadosUHE[j][0])
            nomeUHE.append(listUHE)

        lista["empreendimento"] = nomeUHE
        retorna.append(lista)

    listaMensagem = {}
    listaMensagem["documentos"] = retorna

    # monta combo grupo
    comboGrupo = ["geral", "operacao", "pae", "sosem"]
    listaMensagem["combo_grupo"] = comboGrupo

    # monta combo empreendimento
    camposDesejados = "e.emp_nome"
    condicao = None
    dadosUHE, retorno, mensagemRetorno = acessoBanco.leDado(
        "emp_empreendimento as e",
        condicao,
        camposDesejados,
    )
    listaUHE = []
    if retorno == 400:
        return {"message": "Erro de acesso ao banco"}, 400, header
    for j in range(len(dadosUHE)):
        listaUHE.append(dadosUHE[j][0])
    listaUHE.append("Todos os empreendimentos")
    listaMensagem["combo_empreendimento"] = listaUHE
    retorna.append(lista)

    return listaMensagem, retorno, {}

def documentacaoOriginalChave():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header
    chave = str(random.randint(1000000, 9999999))
    listaMensagem = {}
    listaMensagem["arquivo"] = chave
    return listaMensagem, 200, header

def documentacaoOriginalInclui():
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta["sub"]

    entrada = request.json

    grupo = entrada.get("grupo")
    nome = entrada.get("nome")
    descricao = entrada.get("descricao")
    empreendimento = entrada.get("empreendimento")
    documento = entrada.get("arquivo")

    print(entrada)


    cheque = {}
    cheque["message"] = ""
    erro = False

    if grupo is None or grupo not in ("geral","pae", "sosem","operacao"):
        cheque["message"] = "Grupo inválido"
        erro = True

    if nome is None:
        if not erro:
            cheque["message"] = "Nome é obrigatório e textual"
        else:
            cheque["message"] = cheque["message"] + " - Nome é obrigatório e textual"
        erro = True
    else:
        if type(nome) is not str or len(nome) < 2:
            if not erro:
                cheque["message"] = "Nome é obrigatório e textual"
            else:
                cheque["message"] = cheque["message"] + " - Nome é obrigatório e textual"
            erro = True

    if descricao is None:
        if not erro:
            cheque["message"] = "Descrição é obrigatória e textual"
        else:
            cheque["message"] = cheque["message"] + " - Descrição é obrigatória e textual"
        erro = True
    else:
        if type(descricao) is not str or len(descricao) < 2:
            if not erro:
                cheque["message"] = "Descrição é obrigatória e textual"
            else:
                cheque["message"] = cheque["message"] + " - Descrição é obrigatória e textual"
            erro = True

    if empreendimento is None:
        if not erro:
            cheque["message"] = "Lista de empreendimento é obrigatória"
        else:
            cheque["message"] = cheque["message"] + " - Lista de empreendimento é obrigatória"
        erro = True
    else:
        if type(empreendimento) is not list or len(empreendimento) == 0:
            if not erro:
                cheque["message"] = "Lista de empreendimento inválida"
            else:
                cheque["message"] = cheque["message"] + " - Lista de empreendimento inválida"
            erro = True

    if documento is None or len(documento) < 2:
        if not erro:
            cheque["message"] = "Arquivo é obrigatório"
        else:
            cheque["message"] = cheque["message"] + " - Arquivo é obrigatório"
        erro = True

    if erro:
        return cheque, 404, header

# verifica se o documento já está associado a outro registro no banco
    camposDesejados = "doc_identificador"
    condicao = (
            "WHERE (doc_grupo = '" + grupo
            + "' AND doc_nome = '" + nome
            + "') OR doc_arquivo = '" + config.AWS_PATH + documento + "'"
    )
    dados, retorno, mensagemRetorno = acessoBanco.leDado("doc_documentacaoassociada", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno, {}

    if dados != []:
        return {"message": "Grupo/Nome e Arquivo devem ser únicos na base de dados"}, 404, header

    # verifica se o documento está no Amazon
    if not documentoAmazon(config.SUBPASTA_AMAZON + documento):
        return {"message": "Documento não está armazenado no servidor de documentos"}, 404, header

    # verifica se os empreendimentos existem
    listaEmpreendimento = []

    camposDesejados = "emp_identificador"
    for i in range(len(empreendimento)):
        if empreendimento[i] == "Todos os empreendimentos":
            listaEmpreendimento.append(0)
        else:
            condicao = (
                    "WHERE emp_nome = '" + empreendimento[i]
                    + "'"
            )
            dados, retorno, mensagemRetorno = acessoBanco.leDado("emp_empreendimento", condicao, camposDesejados)

            if retorno == 400:
                return {"message": "Erro no acesso ao banco de dados"}, retorno, header

            if dados != []:
                return {"message": "Empreendimento inválido"}, 404, header
            listaEmpreendimento.append(dados[i][0])

    # atualiza a base
    dados, retorno, mensagemRetorno = acessoBanco.insereDocumento(
        grupo, nome, descricao, listaEmpreendimento, config.AWS_PATH + documento, usu_identificador
    )
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno, header

    if retorno != 201:
        return {"message": "Erro no armazenamento"}, 404,header
    return {}, 201, header

def documentacaoOriginalLeExcluiAltera(id):
    checa, mensagem, header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, header

    codificado, volta = gestaoAutenticacao.expandeToken()
    usu_identificador = volta["sub"]

    # verifica se o documento existe
    camposDesejados = (
            "doc_grupo, doc_nome, doc_descricao, doc_identificadoratualizacao, "
            + "doc_dataatualizacao, doc_arquivo, usu_nome"
    )
    condicao = "WHERE doc_identificador = " + str(id) + " AND a.doc_identificadoratualizacao = u.usu_identificador"
    dados, retorno, mensagemRetorno = acessoBanco.leDado("doc_documentacaoassociada a, usu_usuario u", condicao,
                                                         camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno, {}

    if dados == []:
        return {"message": "Documento inexistente"}, 404, header

    if request.method == "GET":
        mensagemRetorno = {}
        mensagemRetorno["grupo"] = dados[0][0]
        mensagemRetorno["nome"] = dados[0][1]
        mensagemRetorno["descricao"] = dados[0][2]
        mensagemRetorno["atualizador"] = dados[0][6]
        mensagemRetorno["data"] = dados[0][4]
        mensagemRetorno["arquivo"] = dados[0][5]


        listaUHE = []

        camposDesejados = "e.emp_nome"
        condicao = (
                "WHERE b.doc_identificador = "
                + str(id) +
                " AND b.emp_identificador = e.emp_identificador"
        )
        dadosUHE, retorno, mensagemVolta = acessoBanco.leDado(
            "doc_emp_documentacaoassociada_empreendimento as b, emp_empreendimento as e",
            condicao,
            camposDesejados,
        )
        print(dadosUHE, " - ", retorno)
        if retorno == 400:
            return {"message": "Erro de acesso ao banco"}, 400, header
        elif retorno != 200:
            listaUHE.append("Todos os empreendimentos")
        else:
            for j in range(len(dadosUHE)):
                listaUHE.append(dadosUHE[j][0])
        print(listaUHE)
        mensagemRetorno["empreendimento"] = listaUHE

        return mensagemRetorno, 200, header
    elif request.method == "DELETE":
        dadosDel, retorno, mensagemRetorno = acessoBanco.exclueDocumento(id)
        if retorno == 400:
            return {"message": "Erro no acesso ao banco"}, 400, header
        elif retorno == 200:
            documento = config.SUBPASTA_AMAZON + dados[0][5].split(config.AWS_PATH)[1]
            print(documento)
            volta = excluiAmazon(documento)
            if not volta:
                return {"message": "Não foi possível excluir o arquivo no servidor de documentos"}, 404, header
            else:
                return {}, 200, header
    elif request.method == "PATCH":
        dados, retorno = trataAlteraDocumento(id, usu_identificador)
        if retorno == 400:
            return {"message": "Erro no acesso ao banco"}, 400, header
        else:
            return dados, retorno, header

def trataAlteraDocumento(id, usuario):
    entrada = request.json

    grupo = entrada.get("grupo")
    nome = entrada.get("nome")
    descricao = entrada.get("descricao")
    empreendimento = entrada.get("empreendimento")

    cheque = {}
    cheque["message"] = ""
    erro = False
    temAlteracao = False

    if grupo is not None:
        if grupo not in ("geral","pae", "sosem","operacao"):
            cheque["message"] = "Grupo inválido"
            erro = True
        else:
            temAlteracao

    if nome is not None:
        if type(nome) is not str or len(nome) < 2:
            if not erro:
                cheque["message"] = "Nome é obrigatório e textual"
            else:
                cheque["message"] = cheque["message"] + " - Nome é obrigatório e textual"
            erro = True
        else:
            temAlteracao = True

    if descricao is not None:
        if type(descricao) is not str or len(descricao) < 2:
            if not erro:
                cheque["message"] = "Descrição é obrigatória e textual"
            else:
                cheque["message"] = cheque["message"] + " - Descrição é obrigatória e textual"
            erro = True
        else:
            temAlteracao = True

    if empreendimento is not None:
        if type(empreendimento) is not list or len(empreendimento) == 0:
            if not erro:
                cheque["message"] = "Lista de empreendimento inválida"
            else:
                cheque["message"] = cheque["message"] + " - Lista de empreendimento inválida"
            erro = True
        else:
            temAlteracao = True

    if erro:
        return cheque, 404
    if not temAlteracao:
        return {"message": "Nada a ser alterado"}, 404

    # recupera o documento
    camposDesejados = "doc_grupo, doc_nome, doc_descricao"
    condicao = (
            "WHERE doc_identificador = " + str(id)
    )
    dados, retorno, mensagemRetorno = acessoBanco.leDado("doc_documentacaoassociada", condicao, camposDesejados)
    if retorno == 400:
        return mensagemRetorno, 400
    elif retorno != 200:
        return {"message": "Registro Inexistente"}, 404

    #recupera os empreendimentos associados
    camposDesejados = "emp_identificador"
    condicao = (
            "WHERE doc_identificador = " + str(id)
    )
    dadosEmp, retorno, mensagemRetorno = acessoBanco.leDado("doc_emp_documentacaoassociada_empreendimento", condicao, camposDesejados)
    if retorno == 400:
        return mensagemRetorno, 400

    #combina os dados
    if grupo is None:
        grupo = dados[0][0]
    if nome is None:
        nome = dados[0][1]
    if descricao is None:
        descricao = dados[0][2]

# verifica se o documento existe
    camposDesejados = "doc_identificador"
    condicao = (
            "WHERE (doc_grupo = '" + grupo
            + "' AND doc_nome = '" + nome
            + "')"
    )
    dadosVer, retorno, mensagemRetorno = acessoBanco.leDado("doc_documentacaoassociada", condicao, camposDesejados)

    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if dadosVer != []:
        return {"message": "Grupo/Nome e Arquivo devem ser únicos na base de dados"}, 404

    # verifica se os empreendimentos existem
    listaEmpreendimento = []
    camposDesejados = "emp_identificador"
    if empreendimento is not None:
        for i in range(len(empreendimento)):
            if empreendimento[i] == 'Todos os empreendimentos':
                listaEmpreendimento.append(0)
            else:
                condicao = (
                        "WHERE emp_nome = '" + empreendimento[i]
                        + "'"
                )
                dados, retorno, mensagemRetorno = acessoBanco.leDado("emp_empreendimento", condicao, camposDesejados)

                if retorno == 400:
                    return {"message": "Erro no acesso ao banco de dados"}, retorno

                if dados == []:
                    return {"message": "Empreendimento inválido"}, 404
                listaEmpreendimento.append(dados[i][0])

    # atualiza a base
    dados, retorno, mensagemRetorno = acessoBanco.alteraDocumento(
        id, grupo, nome, descricao, listaEmpreendimento, usuario
    )
    if retorno == 400:
        return {"message": "Erro no acesso ao banco de dados"}, retorno

    if retorno != 200:
        return {"message": "Erro no armazenamento"}, 404
    return {}, 200

def documentoAmazon(documento):
    s3 = boto3.client(
        's3',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
    )
    try:
        s3.head_object(Bucket=config.AWS_STORAGE_BUCKET_NAME, Key=documento)
        return True
    except:
        return False

def excluiAmazon(documento):
    s3 = boto3.client(
        's3',
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
    )
    try:
        s3.delete_object(Bucket=config.AWS_STORAGE_BUCKET_NAME, Key=documento)
        return True
    except:
        return False


