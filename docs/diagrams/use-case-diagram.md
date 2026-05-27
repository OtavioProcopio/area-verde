flowchart LR

%% =========================
%% ATORES
%% =========================

ATENDENTE["Atendente / Usuário do Sistema"]
RESP_CAIXA["Responsável pelo Caixa"]
CLIENTE["Cliente do Bar"]

%% =========================
%% MÓDULO: ACESSO
%% =========================

subgraph ACESSO["Módulo: Acesso"]
    UC_ACESSAR(["Acessar sistema com senha"])
    UC_ALTERAR_SENHA(["Alterar senha de acesso"])
end

%% =========================
%% MÓDULO: PRODUTOS
%% =========================

subgraph PRODUTOS["Módulo: Produtos"]
    UC_CAD_CATEGORIA(["Cadastrar categoria"])
    UC_EDIT_CATEGORIA(["Editar categoria"])
    UC_CAD_PRODUTO(["Cadastrar produto"])
    UC_EDIT_PRODUTO(["Editar produto"])
    UC_INATIVAR_PRODUTO(["Inativar produto"])
    UC_CONSULTAR_PRODUTO(["Consultar produtos"])
    UC_DEF_ESTOQUE(["Definir controle de estoque"])
    UC_DEF_BAIXA(["Definir quantidade de baixa por venda"])
end

%% =========================
%% MÓDULO: ESTOQUE
%% =========================

subgraph ESTOQUE["Módulo: Estoque"]
    UC_VER_ESTOQUE(["Consultar estoque atual"])
    UC_ENTRADA_ESTOQUE(["Adicionar entrada de estoque"])
    UC_AJUSTE_ESTOQUE(["Ajustar estoque manualmente"])
    UC_VER_BAIXO(["Ver produtos com estoque baixo"])
    UC_MOV_ESTOQUE(["Consultar movimentos de estoque"])
    UC_ALERTA_NEGATIVO(["Visualizar alerta de estoque negativo"])
end

%% =========================
%% MÓDULO: COMANDAS
%% =========================

subgraph COMANDAS["Módulo: Comandas"]
    UC_CRIAR_COMANDA(["Criar comanda por nome/apelido"])
    UC_LISTAR_COMANDAS(["Listar comandas abertas"])
    UC_BUSCAR_COMANDA(["Buscar comanda"])
    UC_ABRIR_COMANDA(["Abrir detalhes da comanda"])
    UC_ADD_PRODUTO(["Adicionar produto à comanda"])
    UC_INC_ITEM(["Aumentar quantidade do item"])
    UC_DEC_ITEM(["Diminuir quantidade do item"])
    UC_REMOVER_ITEM(["Remover item da comanda"])
    UC_CANCELAR_COMANDA(["Cancelar comanda"])
    UC_RECALCULAR_TOTAL(["Recalcular total da comanda"])
    UC_BAIXAR_ESTOQUE(["Baixar estoque automaticamente"])
    UC_DEVOLVER_ESTOQUE(["Devolver estoque automaticamente"])
end

%% =========================
%% MÓDULO: PAGAMENTOS
%% =========================

subgraph PAGAMENTOS["Módulo: Pagamentos e Fechamento"]
    UC_FECHAR_COMANDA(["Fechar comanda"])
    UC_REG_PAGAMENTO(["Registrar pagamento"])
    UC_LISTAR_PAGAMENTOS(["Listar pagamentos da comanda"])
    UC_BLOQ_FIADO(["Bloquear FIADO no MVP"])
end

%% =========================
%% MÓDULO: FIADO
%% =========================

subgraph FIADO["Módulo: Fiado / Pendências"]
    UC_MARCAR_FIADO(["Marcar comanda como fiado"])
    UC_LISTAR_FIADOS(["Listar fiados pendentes"])
    UC_ALERTA_FIADO(["Destacar fiados com 7 dias ou mais"])
    UC_PAGAR_FIADO(["Registrar pagamento de fiado"])
    UC_CONSULTAR_HIST_FIADO(["Consultar histórico de fiados"])
end

%% =========================
%% MÓDULO: CAIXA
%% =========================

subgraph CAIXA["Módulo: Caixa Diário"]
    UC_ABRIR_CAIXA(["Abrir caixa do dia"])
    UC_VER_CAIXA(["Consultar caixa do dia"])
    UC_REG_SANGRIA(["Registrar sangria"])
    UC_REG_REFORCO(["Registrar reforço"])
    UC_FECHAR_CAIXA(["Fechar caixa"])
    UC_CALC_DINHEIRO(["Calcular dinheiro esperado"])
    UC_CALC_DIFERENCA(["Calcular diferença de caixa"])
end

%% =========================
%% MÓDULO: RELATÓRIOS
%% =========================

subgraph RELATORIOS["Módulo: Relatórios"]
    UC_REL_DIA(["Gerar relatório diário"])
    UC_REL_PAGAMENTO(["Gerar relatório por forma de pagamento"])
    UC_REL_PRODUTOS(["Gerar relatório de produtos mais vendidos"])
    UC_REL_FIADOS(["Gerar relatório de fiados"])
    UC_REL_ESTOQUE(["Gerar relatório de estoque baixo"])
    UC_REL_COMANDAS(["Gerar relatório de comandas"])
end

%% =========================
%% MÓDULO: CONFIGURAÇÕES
%% =========================

subgraph CONFIG["Módulo: Configurações"]
    UC_CONF_DIAS_FIADO(["Configurar dias para alerta de fiado"])
    UC_CONF_EST_NEG(["Configurar permissão de estoque negativo"])
    UC_CONF_DADOS_BAR(["Configurar dados básicos do bar"])
end

%% =========================
%% RELAÇÕES DOS ATORES
%% =========================

ATENDENTE --> UC_ACESSAR
ATENDENTE --> UC_CRIAR_COMANDA
ATENDENTE --> UC_LISTAR_COMANDAS
ATENDENTE --> UC_BUSCAR_COMANDA
ATENDENTE --> UC_ABRIR_COMANDA
ATENDENTE --> UC_ADD_PRODUTO
ATENDENTE --> UC_INC_ITEM
ATENDENTE --> UC_DEC_ITEM
ATENDENTE --> UC_REMOVER_ITEM
ATENDENTE --> UC_CANCELAR_COMANDA
ATENDENTE --> UC_FECHAR_COMANDA
ATENDENTE --> UC_LISTAR_PAGAMENTOS
ATENDENTE --> UC_MARCAR_FIADO
ATENDENTE --> UC_LISTAR_FIADOS
ATENDENTE --> UC_PAGAR_FIADO
ATENDENTE --> UC_CONSULTAR_PRODUTO
ATENDENTE --> UC_VER_ESTOQUE
ATENDENTE --> UC_ENTRADA_ESTOQUE
ATENDENTE --> UC_AJUSTE_ESTOQUE
ATENDENTE --> UC_VER_BAIXO

RESP_CAIXA --> UC_ABRIR_CAIXA
RESP_CAIXA --> UC_VER_CAIXA
RESP_CAIXA --> UC_REG_SANGRIA
RESP_CAIXA --> UC_REG_REFORCO
RESP_CAIXA --> UC_FECHAR_CAIXA
RESP_CAIXA --> UC_REL_DIA
RESP_CAIXA --> UC_REL_PAGAMENTO
RESP_CAIXA --> UC_REL_PRODUTOS
RESP_CAIXA --> UC_REL_FIADOS
RESP_CAIXA --> UC_REL_ESTOQUE
RESP_CAIXA --> UC_REL_COMANDAS

RESP_CAIXA --> UC_CAD_CATEGORIA
RESP_CAIXA --> UC_EDIT_CATEGORIA
RESP_CAIXA --> UC_CAD_PRODUTO
RESP_CAIXA --> UC_EDIT_PRODUTO
RESP_CAIXA --> UC_INATIVAR_PRODUTO
RESP_CAIXA --> UC_DEF_ESTOQUE
RESP_CAIXA --> UC_DEF_BAIXA

RESP_CAIXA --> UC_ALTERAR_SENHA
RESP_CAIXA --> UC_CONF_DIAS_FIADO
RESP_CAIXA --> UC_CONF_EST_NEG
RESP_CAIXA --> UC_CONF_DADOS_BAR

CLIENTE --> UC_CRIAR_COMANDA
CLIENTE --> UC_FECHAR_COMANDA
CLIENTE --> UC_MARCAR_FIADO
CLIENTE --> UC_PAGAR_FIADO

%% =========================
%% RELAÇÕES ENTRE CASOS
%% =========================

UC_ADD_PRODUTO --> UC_RECALCULAR_TOTAL
UC_ADD_PRODUTO --> UC_BAIXAR_ESTOQUE

UC_INC_ITEM --> UC_RECALCULAR_TOTAL
UC_INC_ITEM --> UC_BAIXAR_ESTOQUE

UC_DEC_ITEM --> UC_RECALCULAR_TOTAL
UC_DEC_ITEM --> UC_DEVOLVER_ESTOQUE

UC_REMOVER_ITEM --> UC_RECALCULAR_TOTAL
UC_REMOVER_ITEM --> UC_DEVOLVER_ESTOQUE

UC_CANCELAR_COMANDA --> UC_DEVOLVER_ESTOQUE

UC_FECHAR_COMANDA --> UC_REG_PAGAMENTO
UC_FECHAR_COMANDA --> UC_BLOQ_FIADO

UC_MARCAR_FIADO --> UC_ALERTA_FIADO
UC_LISTAR_FIADOS --> UC_ALERTA_FIADO

UC_REG_SANGRIA --> UC_CALC_DINHEIRO
UC_REG_REFORCO --> UC_CALC_DINHEIRO
UC_FECHAR_CAIXA --> UC_CALC_DINHEIRO
UC_FECHAR_CAIXA --> UC_CALC_DIFERENCA

UC_ENTRADA_ESTOQUE --> UC_MOV_ESTOQUE
UC_AJUSTE_ESTOQUE --> UC_MOV_ESTOQUE
UC_BAIXAR_ESTOQUE --> UC_MOV_ESTOQUE
UC_DEVOLVER_ESTOQUE --> UC_MOV_ESTOQUE

UC_VER_ESTOQUE --> UC_VER_BAIXO
UC_VER_ESTOQUE --> UC_ALERTA_NEGATIVO

UC_REL_DIA --> UC_REL_PAGAMENTO
UC_REL_DIA --> UC_REL_PRODUTOS
UC_REL_DIA --> UC_REL_FIADOS
UC_REL_DIA --> UC_REL_ESTOQUE
