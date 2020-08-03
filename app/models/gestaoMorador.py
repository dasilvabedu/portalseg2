# -*- coding: utf-8 -*-

from ..views import acessoBanco
from ..models import gestaoAutenticacao

def moradoresMacro(uhe):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    # verifica se existem agentes para a UHE
    camposDesejados = 'pro_propriedade.pro_identificador, pro_endereco, pro_tipo, pro_uso, pro_proprietario, pro_telefonefixo, pro_telefonecelular, pro_email, pro_frequenciauso, '
    camposDesejados = camposDesejados + 'pro_formaacesso, pro_condicaoacesso, pro_estadoconservacao, pro_quantidadeedificacao'
    condicao = "INNER JOIN pae_planoacaoemergencia ON pae_planoacaoemergencia.pae_identificador = pro_propriedade.pae_identificador "
    condicao = condicao + "WHERE pae_planoacaoemergencia.emp_identificador = " + str(uhe)
    dadosMorador, retorno, mensagemRetorno = acessoBanco.leDado('pro_propriedade', condicao, camposDesejados)

    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosMorador) == 0:
        return {"message": "Esta UHE não possui moradores cadastrados."}, 400, header

 # monta resposta
    dadosFinais = []
    for i in range(len(dadosMorador)):
        mensagemMoradores = {}
        mensagemMoradores["id"] = dadosMorador[i][0]
        mensagemMoradores["endereco"] = dadosMorador[i][1]
        mensagemMoradores["tipo"] = dadosMorador[i][2]
        mensagemMoradores["uso"] = dadosMorador[i][3]
        mensagemMoradores["prop"] = dadosMorador[i][4]
        mensagemMoradores["tel_fixo"] = dadosMorador[i][5]
        mensagemMoradores["tel_celular"] = dadosMorador[i][6]
        mensagemMoradores["email"] = dadosMorador[i][7]
        mensagemMoradores["freq_uso"] = dadosMorador[i][8]
        mensagemMoradores["forma_acesso"] = dadosMorador[i][9]
        mensagemMoradores["cond_acesso"] = dadosMorador[i][10]
        mensagemMoradores["conservacao"] = dadosMorador[i][11]
        mensagemMoradores["qtde_edif"] = dadosMorador[i][12]
        dadosFinais.append(mensagemMoradores)

    corpoMensagem = {}
    corpoMensagem['moradores'] = dadosFinais
    return corpoMensagem, 200, header

def moradorEspecifico(id_morador):
    checa, mensagem,  header = gestaoAutenticacao.trataValidaToken()
    if not checa:
        return mensagem, 400, ''

    # recupera o dado do morador
    camposDesejados = 'pro_identificador, pro_endereco, pro_tipo, pro_uso, pro_proprietario, pro_telefonefixo, pro_telefonecelular, pro_email, pro_frequenciauso, '
    camposDesejados = camposDesejados + 'pro_formaacesso, pro_condicaoacesso, pro_estadoconservacao, pro_quantidadeedificacao'
    condicao = "WHERE pro_identificador = " + str(id_morador)
    dadosMorador, retorno, mensagemRetorno = acessoBanco.leDado('pro_propriedade', condicao, camposDesejados)
    if retorno == 404:
        return {"message": "Erro de acesso ao banco"}, 401, header

    if len(dadosMorador) == 0:
        return {"message": "Esta UHE não possui agentes relacionados."}, 400, header

 # monta resposta
    mensagemMoradores = {}
    mensagemMoradores["id"] = dadosMorador[0][0]
    mensagemMoradores["endereco"] = dadosMorador[0][1]
    mensagemMoradores["tipo"] = dadosMorador[0][2]
    mensagemMoradores["uso"] = dadosMorador[0][3]
    mensagemMoradores["tel_fixo"] = dadosMorador[0][4]
    mensagemMoradores["tel_celular"] = dadosMorador[0][5]
    mensagemMoradores["email"] = dadosMorador[0][6]
    mensagemMoradores["freq_uso"] = dadosMorador[0][7]
    mensagemMoradores["forma_acesso"] = dadosMorador[0][8]
    mensagemMoradores["cond_acesso"] = dadosMorador[0][9]
    mensagemMoradores["conservacao"] = dadosMorador[0][10]
    mensagemMoradores["qtde_edif"] = dadosMorador[0][11]

    corpoMensagem = {}
    corpoMensagem['morador'] = mensagemMoradores
    return corpoMensagem, 200, header
