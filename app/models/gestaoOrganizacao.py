# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao
from flask import request

def organizacaoGeral():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    # realiza consulta no banco - grupo economico
    camposDesejados = 'gec_identificador,gec_nome'
    dados, retorno, mensagemRetorno = acessoBanco.dado('gec_grupoeconomico', None, camposDesejados, None)
    resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
    if retorno != 200:
        return resultadoFinal, retorno, header
    resultadoFinal['grupoeconomico'] = dados

    # realiza consulta no banco - companhia
    camposDesejados = 'cia_identificador,cia_nome'
    dados, retorno, mensagemRetorno = acessoBanco.dado('cia_companhia', None, camposDesejados, None)
    if retorno != 200:
        return resultadoFinal, retorno, header
    resultadoFinal['companhia'] = dados

    # realiza consulta no banco - empreendimento
    camposDesejados = 'emp_identificador,emp_nome'
    dados, retorno, mensagemRetorno = acessoBanco.dado('emp_empreendimento', None, camposDesejados, None)
    if retorno != 200:
        return resultadoFinal, retorno, header
    resultadoFinal['empreendimento'] = dados

    return resultadoFinal, retorno, header

def organizacaoCadastrado():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    query_parameters = request.args
    nivel = query_parameters.get('nivel')
    nome = query_parameters.get('nome')

    if nivel is None or nome is None:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Nivel ou Nome não fornecido(s)'
        resultadoFinal = acessoBanco.montaRetorno(200, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ' '
        return resultadoFinal, 200, header

    resultado = acessoBanco.montaRetorno(200, '')
    if nivel == "grupoeconomico":
        condicao = "WHERE gec_nome = '" + nome + "'"
        resultadoFinal = montaGrupo(condicao,resultado, True)
    elif nivel == "companhia":
        condicao = "WHERE cia_nome = '" + nome + "'"
        resultadoFinal = montaCompanhia(condicao,resultado, True, True)
    elif nivel == "empreendimento":
        condicao = "WHERE emp_nome = '" + nome + "'"
        resultadoFinal = montaEmpreendimento(condicao,resultado, True)
    else:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Nivel ' + nivel + ' é inválido.'
        resultadoFinal = acessoBanco.montaRetorno(200, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ' '
        return resultadoFinal, 200, header

    return resultadoFinal, 200, header

def organizacaoExcluido():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    query_parameters = request.args
    nivel = query_parameters.get('nivel')
    nome = query_parameters.get('nome')

    if nivel is None or nome is None:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Nivel ou Nome não fornecido(s)'
        resultadoFinal = acessoBanco.montaRetorno(200, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ' '
        return resultadoFinal, 200, header

    resultado = acessoBanco.montaRetorno(200, '')
    if nivel == "grupoeconomico":
        condicao = "WHERE gec_nome = '" + nome + "'"
        # realiza consulta no banco - grupo economico
        camposDesejados = 'gec_identificador'
        dados, retorno, mensagemRetorno = acessoBanco.dado('gec_grupoeconomico', condicao, camposDesejados, None)
        if retorno != 200:
            resultadoGEC = []
            return resultadoGEC, retorno,''

        # recupera as companhias do grupo
        condicao = 'WHERE gec_identificador in ('
        for i in range(len(dados)):
            condicao = condicao + str(dados[i]['gec_identificador']) + ','
        condicao = condicao[0:-1] + ')'
        dados, retorno, mensagemRetorno = acessoBanco.dado('gec_cia_grupoeconomico_companhia', condicao, None, None)
        if retorno != 200:
            return resultado, retorno,''
        if dados != []:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Grupo econômico possui Companhia(s). Delete-a(s) previamente.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header
        # deleta
        dados, retorno, mensagemRetorno = acessoBanco.exclueDado('gec_grupoeconomico', condicao)
        if retorno != 200:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Grupo Econômico não excluido.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header
        else:
            listaMensagem = {}
            listaMensagem['acesso'] = 'ok'
            listaMensagem['texto'] = 'Grupo Econômico excluido.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

    elif nivel == "companhia":
        condicao = "WHERE cia_nome = '" + nome + "'"
        # realiza consulta no banco - companhia
        camposDesejados = 'cia_identificador'
        dados, retorno, mensagemRetorno = acessoBanco.dado('cia_companhia', condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno,''

        # recupera os empreendimentos da cia
        condicao = 'WHERE cia_identificador in ('
        for i in range(len(dados)):
            condicao = condicao + str(dados[i]['cia_identificador']) + ','
        condicao = condicao[0:-1] + ')'
        dados, retorno, mensagemRetorno = acessoBanco.dado('emp_empreendimento', condicao, None, None)
        if retorno != 200:
            return resultado, retorno,''
        if dados != []:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Companhia possui Empreendimento(s). Delete-o(s) previamente.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

        # deleta
        dados, retorno, mensagemRetorno = acessoBanco.exclueDado('gec_cia_grupoeconomico_companhia', condicao)
        if retorno != 200:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Companhia não excluida.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header
        dados, retorno, mensagemRetorno = acessoBanco.exclueDado('cia_companhia', condicao)
        if retorno != 200:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Companhia não excluida.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header
        else:
            listaMensagem = {}
            listaMensagem['acesso'] = 'ok'
            listaMensagem['texto'] = 'Companhia excluida.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

    elif nivel == "empreendimento":
        condicao = "WHERE emp_nome = '" + nome + "'"
        # realiza consulta no banco - empreendimento
        camposDesejados = 'emp_identificador'
        dadosEmp, retorno, mensagemRetorno = acessoBanco.dado('emp_empreendimento', condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno,''

        # deleta os PAEs do empreendimento
        condicao = 'WHERE emp_identificador in ('
        for i in range(len(dadosEmp)):
            condicao = condicao + str(dadosEmp[i]['emp_identificador']) + ','
        condicao = condicao[0:-1] + ')'
        dados, retorno, mensagemRetorno = acessoBanco.exclueDado('pae_planoacaoemergencia', condicao)

        if retorno != 200:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'PAES do Empreendimento possui dados. Empreendimento não excluído.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

        # deleta empreendimento
        dados, retorno, mensagemRetorno = acessoBanco.exclueDado('emp_empreendimento', condicao)

        if retorno != 200:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Empreendimento não excluído.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header
        else:
            listaMensagem = {}
            listaMensagem['acesso'] = 'ok'
            listaMensagem['texto'] = 'Empreendimento excluído.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header
    else:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Nivel ' + nivel + ' é inválido.'
        resultadoFinal = acessoBanco.montaRetorno(200, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ' '
        return resultadoFinal, 200, header

def organizacaoIncluido():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    query_parameters = request.args
    nivel = query_parameters.get('nivel')
    nome = query_parameters.get('nome')
    superior = query_parameters.get('superior')
    pae = query_parameters.get('pae')
    tipo = query_parameters.get('tipo')

    if nivel is None or nome is None:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Nivel ou Nome não fornecido(s)'
        resultadoFinal = acessoBanco.montaRetorno(200, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ' '
        return resultadoFinal, 200, header

    resultado = acessoBanco.montaRetorno(200, '')
    if nivel == "grupoeconomico":
        condicao = "WHERE gec_nome = '" + nome + "'"
        # realiza consulta no banco - grupo economico
        camposDesejados = 'gec_identificador'
        dados, retorno, mensagemRetorno = acessoBanco.dado('gec_grupoeconomico', condicao, camposDesejados, None)
        if retorno != 200:
            resultadoGEC = []
            return resultadoGEC, retorno, header

        if dados != []:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Já existe Grupo Econômico com este nome.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

        # inclui
        campo = 'max(gec_identificador)'
        dados, retorno, mensagemRetorno = acessoBanco.leDado('gec_grupoeconomico', None, campo)
        if retorno != 200:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        proximoNumero = dados[0][0] + 1

        campos = 'gec_identificador, gec_nome'
        valores = str(proximoNumero) + ",'" + nome + "'"
        dados, retorno, mensagemRetorno = acessoBanco.insereDado('gec_grupoeconomico', campos, valores)
        if retorno != 201:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        gecIncluido = {}
        gecIncluido['usu_identificador'] = proximoNumero
        resposta = acessoBanco.montaRetorno(201, '')
        resposta['aresposta']['texto'] = ''
        resposta['retorno'] = gecIncluido
        return resposta, 201, header

    elif nivel == "companhia":
        if superior is None :
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Nivel Superior não fornecido(s)'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

        condicao = "WHERE cia_nome = '" + nome + "'"
        # realiza consulta no banco - companhia
        camposDesejados = 'cia_identificador'
        dados, retorno, mensagemRetorno = acessoBanco.dado('cia_companhia', condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados != []:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Companhia já existente.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

        # verifica se o Grupo Econômico existe
        camposDesejados = 'gec_identificador'
        condicao = "WHERE gec_nome = '" + superior + "'"
        dados, retorno, mensagemRetorno = acessoBanco.dado('gec_grupoeconomico', condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados == []:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Grupo Econômico inexistente'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header
        gec_identificador = dados[0]['gec_identificador']

        # inclui
        campo = 'max(cia_identificador)'
        dados, retorno, mensagemRetorno = acessoBanco.leDado('cia_companhia', None, campo)
        if retorno != 200:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        proximoNumero = dados[0][0] + 1

        campos = 'cia_identificador, cia_nome'
        valores = str(proximoNumero) + ",'" + nome + "'"
        dados, retorno, mensagemRetorno = acessoBanco.insereDado('cia_companhia', campos, valores)
        if retorno != 201:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        campos = 'cia_identificador, gec_identificador'
        valores = str(proximoNumero) + "," + str(gec_identificador)
        dados, retorno, mensagemRetorno = acessoBanco.insereDado('gec_cia_grupoeconomico_companhia', campos, valores)
        if retorno != 201:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        ciaIncluido = {}
        ciaIncluido['cia_identificador'] = proximoNumero
        resposta = acessoBanco.montaRetorno(201, '')
        resposta['aresposta']['texto'] = ''
        resposta['retorno'] = ciaIncluido
        return resposta, 201, header

    elif nivel == "empreendimento":
        if superior is None or tipo is None or pae is None:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Nivel Superior, Tipo do Empreendimento ou Ativação do PAE não fornecido(s)'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

        if tipo not in ('UHE','PCH'):
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Tipo de Empreendimento Invalido'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

        if pae not in ('S','N'):
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Ativação de PAE Invalido'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

        condicao = "WHERE emp_nome = '" + nome + "'"
        # realiza consulta no banco - empreendimento
        camposDesejados = 'emp_identificador'
        dados, retorno, mensagemRetorno = acessoBanco.dado('emp_empreendimento', condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados != []:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Empreendimento já existente.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

        # verifica se a companhia existe
        camposDesejados = 'cia_identificador'
        condicao = "WHERE cia_nome = '" + superior + "'"
        dados, retorno, mensagemRetorno = acessoBanco.dado('cia_companhia', condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados == []:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Companhia inexistente'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header
        cia_identificador = dados[0]['cia_identificador']

        # inclui
        campo = 'max(emp_identificador)'
        dados, retorno, mensagemRetorno = acessoBanco.leDado('emp_empreendimento', None, campo)
        if retorno != 200:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        proximoEmpreendimento = dados[0][0] + 1

        campos = 'emp_identificador, emp_nome, cia_identificador, emp_tipo'
        valores = str(proximoEmpreendimento) + ",'" + nome + "'," + str(cia_identificador) + ",'" + tipo + "'"
        dados, retorno, mensagemRetorno = acessoBanco.insereDado('emp_empreendimento', campos, valores)
        if retorno != 201:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        if pae == 'S':
            campo = 'max(pae_identificador)'
            dados, retorno, mensagemRetorno = acessoBanco.leDado('pae_planoacaoemergencia', None, campo)
            if retorno != 200:
                resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
                return resultadoFinal, retorno, header
            proximoNumero = dados[0][0] + 1

            campos = 'pae_identificador, emp_identificador'
            valores = str(proximoNumero) + "," + str(proximoEmpreendimento)
            dados, retorno, mensagemRetorno = acessoBanco.insereDado('pae_planoacaoemergencia', campos, valores)
            if retorno != 201:
                resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
                return resultadoFinal, retorno, header

        empIncluido = {}
        empIncluido['emp_identificador'] = proximoEmpreendimento
        resposta = acessoBanco.montaRetorno(201, '')
        resposta['aresposta']['texto'] = ''
        resposta['retorno'] = empIncluido
        return resposta, 201, header
    else:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Nivel ' + nivel + ' é inválido.'
        resultadoFinal = acessoBanco.montaRetorno(200, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ' '
        return resultadoFinal, 200, header

def organizacaoAlterado():
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    query_parameters = request.args
    nivel = query_parameters.get('nivel')
    nome = query_parameters.get('nome')
    novonome = query_parameters.get('novonome')
    superior = query_parameters.get('novosuperior')
    pae = query_parameters.get('novopae')
    tipo = query_parameters.get('novotipo')

    if nivel is None or nome is None:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Nivel e/ou Nome não fornecido(s)'
        resultadoFinal = acessoBanco.montaRetorno(200, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ' '
        return resultadoFinal, 200, header

    resultado = acessoBanco.montaRetorno(200, '')
    if nivel == "grupoeconomico":
        if novonome is None:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Nada a alterar em Grupo Econômico'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

        # realiza consulta no banco - grupo economico
        condicao = "WHERE gec_nome = '" + nome + "'"
        camposDesejados = 'gec_identificador'
        dados, retorno, mensagemRetorno = acessoBanco.dado('gec_grupoeconomico', condicao, camposDesejados, None)
        if retorno != 200:
            resultadoGEC = []
            return resultadoGEC, retorno, header

        if dados == []:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Não existe Grupo Econômico com nome fornecido.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header

        camposDesejados = 'gec_identificador'
        condicao = "WHERE gec_nome = '" + novonome + "'"
        dados, retorno, mensagemRetorno = acessoBanco.dado('gec_grupoeconomico', condicao, camposDesejados, None)
        if retorno != 200:
            resultadoGEC = []
            return resultadoGEC, retorno, header

        if dados != []:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Já existe Grupo Econômico com novo nome fornecido.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header
        # altera
        comando = "gec_nome = '" + novonome + "'"
        condicao = "WHERE gec_nome = '" + nome +"'"
        dados, retorno, mensagemRetorno = acessoBanco.alteraDado('gec_grupoeconomico', comando, condicao)
        if retorno != 200:
            resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
            return resultadoFinal, retorno, header

        gecAlterado = {}
        gecAlterado['gec_nome'] = novonome
        resposta = acessoBanco.montaRetorno(200, '')
        resposta['aresposta']['texto'] = ''
        resposta['retorno'] = gecAlterado
        return resposta, 200, header

    elif nivel == "companhia":
        comando_gec = ''
        if superior is not None:
            # verifica se existe grupo economico com o nome indicado
            condicao = "WHERE gec_nome = '" + superior + "'"
            camposDesejados = 'gec_identificador'
            dados, retorno, mensagemRetorno = acessoBanco.dado('gec_grupoeconomico', condicao, camposDesejados, None)
            if retorno != 200:
                resultadoGEC = []
                return resultadoGEC, retorno, header

            if dados == []:
                listaMensagem = {}
                listaMensagem['acesso'] = 'nok'
                listaMensagem['texto'] = 'Não existe Grupo Econômico com nome fornecido.'
                resultadoFinal = acessoBanco.montaRetorno(200, '')
                resultadoFinal['retorno'] = listaMensagem
                resultadoFinal['aresposta']['texto'] = ' '
                return resultadoFinal, 200, header
            gec_identificador = dados[0]['gec_identificador']
            comando_gec = ", gec_identificador = " + str(gec_identificador)

        # realiza consulta no banco - companhia
        condicao = "WHERE cia_nome = '" + nome + "'"
        camposDesejados = 'cia_identificador'
        dados, retorno, mensagemRetorno = acessoBanco.dado('cia_companhia', condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados == []:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Companhia inexistente.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header
        cia_identificador = dados[0]['cia_identificador']

        # verifica se o novo nome existe
        comando_novonome = ''
        if novonome is not None:
            condicao = "WHERE cia_nome = '" + novonome + "'"
            camposDesejados = 'cia_identificador'
            dados, retorno, mensagemRetorno = acessoBanco.dado('cia_companhia', condicao, camposDesejados, None)
            if retorno != 200:
                resultado = []
                return resultado, retorno, header

            if dados != []:
                listaMensagem = {}
                listaMensagem['acesso'] = 'nok'
                listaMensagem['texto'] = 'Novo nome para Companhia já existente.'
                resultadoFinal = acessoBanco.montaRetorno(200, '')
                resultadoFinal['retorno'] = listaMensagem
                resultadoFinal['aresposta']['texto'] = ' '
                return resultadoFinal, 200, header
            comando_novonome = ", cia_nome = '" + novonome + "'"

        # altera companhia
        comando = comando_novonome
        if len(comando) > 4:
            comando = comando[1:]
            condicao = "WHERE cia_nome = '" + nome + "'"
            dados, retorno, mensagemRetorno = acessoBanco.alteraDado('cia_companhia', comando, condicao)
            if retorno != 200:
                resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
                return resultadoFinal, retorno, header

        # altera relacao com grupo economico
        comando = comando_gec
        if len(comando) > 4:
            comando = comando[1:]
            condicao = "WHERE cia_identificador = " + str(cia_identificador)
            dados, retorno, mensagemRetorno = acessoBanco.alteraDado('gec_cia_grupoeconomico_companhia', comando, condicao)
            if retorno != 200:
                resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
                return resultadoFinal, retorno, header

        ciaAlterado = {}
        ciaAlterado['cia_nome'] = nome
        resposta = acessoBanco.montaRetorno(200, '')
        resposta['aresposta']['texto'] = ''
        resposta['retorno'] = ciaAlterado
        return resposta, 200, header

    elif nivel == "empreendimento":
        comando_companhia = ''
        if superior is not None:
            #verifica se existe companhia com o nome indicado
            condicao = "WHERE cia_nome = '" + superior + "'"
            camposDesejados = 'cia_identificador'
            dados, retorno, mensagemRetorno = acessoBanco.dado('cia_companhia', condicao, camposDesejados, None)
            if retorno != 200:
                resultadoCIA = []
                return resultadoCIA, retorno, header

            if dados == []:
                listaMensagem = {}
                listaMensagem['acesso'] = 'nok'
                listaMensagem['texto'] = 'Não existe Companhia com nome fornecido.'
                resultadoFinal = acessoBanco.montaRetorno(200, '')
                resultadoFinal['retorno'] = listaMensagem
                resultadoFinal['aresposta']['texto'] = ' '
                return resultadoFinal, 200, header
            cia_identificador = dados[0]['cia_identificador']
            comando_companhia = ", cia_identificador = " + str(cia_identificador)

        comando_tipo = ''
        if tipo is not None:
            if tipo not in ('UHE','PCH'):
                listaMensagem = {}
                listaMensagem['acesso'] = 'nok'
                listaMensagem['texto'] = 'Tipo do Empreendimento Inválido'
                resultadoFinal = acessoBanco.montaRetorno(200, '')
                resultadoFinal['retorno'] = listaMensagem
                resultadoFinal['aresposta']['texto'] = ' '
                return resultadoFinal, 200, header
            else:
                comando_tipo = ", emp_tipo = '" + tipo + "'"

        comando_pae = ''
        if pae is not None:
            if pae not in ('S','N'):
                listaMensagem = {}
                listaMensagem['acesso'] = 'nok'
                listaMensagem['texto'] = 'Ativação de PAE Invalido'
                resultadoFinal = acessoBanco.montaRetorno(200, '')
                resultadoFinal['retorno'] = listaMensagem
                resultadoFinal['aresposta']['texto'] = ' '
                return resultadoFinal, 200, header

        # realiza consulta no banco - empreendimento
        condicao = "WHERE emp_nome = '" + nome + "'"
        camposDesejados = 'emp_identificador'
        dados, retorno, mensagemRetorno = acessoBanco.dado('emp_empreendimento', condicao, camposDesejados, None)
        if retorno != 200:
            resultado = []
            return resultado, retorno, header

        if dados == []:
            listaMensagem = {}
            listaMensagem['acesso'] = 'nok'
            listaMensagem['texto'] = 'Empreendimento inexistente.'
            resultadoFinal = acessoBanco.montaRetorno(200, '')
            resultadoFinal['retorno'] = listaMensagem
            resultadoFinal['aresposta']['texto'] = ' '
            return resultadoFinal, 200, header
        emp_identificador = dados[0]['emp_identificador']

        # verifica se o novo nome existe
        comando_novonome = ''
        if novonome is not None:
            condicao = "WHERE emp_nome = '" + novonome + "'"
            camposDesejados = 'emp_identificador'
            dados, retorno, mensagemRetorno = acessoBanco.dado('emp_empreendimento', condicao, camposDesejados, None)
            if retorno != 200:
                resultado = []
                return resultado, retorno, header

            if dados != []:
                listaMensagem = {}
                listaMensagem['acesso'] = 'nok'
                listaMensagem['texto'] = 'Novo nome para Empreendimento já existente.'
                resultadoFinal = acessoBanco.montaRetorno(200, '')
                resultadoFinal['retorno'] = listaMensagem
                resultadoFinal['aresposta']['texto'] = ' '
                return resultadoFinal, 200, header
            comando_novonome = ", emp_nome = '" + novonome + "'"

        # altera
        comando = comando_tipo + comando_companhia + comando_novonome
        if len(comando) > 4:
            comando = comando[1:]
            condicao = "WHERE emp_nome = '" + nome +"'"
            dados, retorno, mensagemRetorno = acessoBanco.alteraDado('emp_empreendimento', comando, condicao)
            if retorno != 200:
                resultadoFinal = acessoBanco.montaRetorno(retorno, mensagemRetorno)
                return resultadoFinal, retorno, header

        empAlterado = {}
        empAlterado['emp_nome'] = nome
        resposta = acessoBanco.montaRetorno(200, '')
        resposta['aresposta']['texto'] = ''
        resposta['retorno'] = empAlterado
        return resposta, 200, header

    else:
        listaMensagem = {}
        listaMensagem['acesso'] = 'nok'
        listaMensagem['texto'] = 'Nivel ' + nivel + ' é inválido.'
        resultadoFinal = acessoBanco.montaRetorno(200, '')
        resultadoFinal['retorno'] = listaMensagem
        resultadoFinal['aresposta']['texto'] = ' '
        return resultadoFinal, 200, header

def montaGrupo(condicao, resultado, propagaFilho):
    # realiza consulta no banco - grupo economico
    camposDesejados = 'gec_identificador,gec_nome'
    dados, retorno, mensagemRetorno = acessoBanco.dado('gec_grupoeconomico', condicao, camposDesejados, None)
    if retorno != 200:
        resultadoGEC = []
        return resultadoGEC
    resultado['grupoeconomico'] = dados

    # testa para ver se recupera os filhos
    if not propagaFilho:
        return resultado

    #recupera as companhias do grupo
    condicao = 'WHERE gec_identificador in ('
    for i in range(len(dados)):
        condicao = condicao + str(dados[i]['gec_identificador']) + ','
    condicao = condicao[0:-1] + ')'
    dados, retorno, mensagemRetorno = acessoBanco.dado('gec_cia_grupoeconomico_companhia', condicao, None, None)
    if retorno != 200:
        return resultado
    condicao = 'WHERE cia_identificador in ('
    for i in range(len(dados)):
        condicao = condicao + str(dados[i]['cia_identificador']) + ','
    condicao = condicao[0:-1] + ')'
    resultadoFinal = montaCompanhia(condicao, resultado, True, False)
    return resultadoFinal

def montaCompanhia(condicao, resultado, propagaFilho, propagaPai):
    # realiza consulta no banco - companhia

    camposDesejados = 'cia_identificador,cia_nome'
    dadosCia, retorno, mensagemRetorno = acessoBanco.dado('cia_companhia', condicao, camposDesejados, None)

    if retorno != 200:
        resultadoFinal = []
        return resultadoFinal
    resultado['companhia'] = dadosCia

    # verifica se propaga os filhos
    if propagaFilho:
        condicao = 'WHERE cia_identificador in ('
        for i in range(len(dadosCia)):
            condicao = condicao + str(dadosCia[i]['cia_identificador']) + ','
        condicao = condicao[0:-1] + ')'
        resultado = montaEmpreendimento(condicao, resultado, False)

    #verifica se recupera os pais
    if propagaPai:
        condicao = 'WHERE cia_identificador in ('
        for i in range(len(dadosCia)):
            condicao = condicao + str(dadosCia[i]['cia_identificador']) + ','
        condicao = condicao[0:-1] + ')'
        dados, retorno, mensagemRetorno = acessoBanco.dado('gec_cia_grupoeconomico_companhia', condicao, None, None)
        if retorno != 200:
            return resultado
        condicao = 'WHERE gec_identificador in ('
        for i in range(len(dados)):
            condicao = condicao + str(dados[i]['gec_identificador']) + ','
        condicao = condicao[0:-1] + ')'
        resultado = montaGrupo(condicao, resultado, False)
    return resultado

def montaEmpreendimento(condicao, resultado, propagaPai):
    # realiza consulta no banco - companhia

    camposDesejados = 'emp_identificador,emp_nome,emp_tipo,cia_identificador'
    dados, retorno, mensagemRetorno = acessoBanco.dado('emp_empreendimento', condicao, camposDesejados, None)
    if retorno != 200:
        resultadoFinal = []
        return resultadoFinal
    resultado['empreendimento'] = dados

    #verifica se propaga os pais
    if propagaPai:
        condicao = 'WHERE cia_identificador in ('
        for i in range(len(dados)):
            condicao = condicao + str(dados[i]['cia_identificador']) + ','
        condicao = condicao[0:-1] + ')'
        resultado = montaCompanhia(condicao, resultado, False, True)
    return resultado