from condicoes import avaliar_condicao
from erros import ErroIFFARQL
from condicoes import avaliar_condicao, buscar_coluna, validar_token

# Mostra um registro com todos os seus campos, incluindo o id.
def exibir_registro(registro):
    print(registro.valores)

# Mostra os registros de uma tabela, podendo aplicar uma condição ONDE.
def mostrar_dados(banco, nome_tabela, nome_coluna=None, operador=None, token=None):
    tabela = banco.buscar_tabela(nome_tabela)
    registros = tabela.arvore.listar_registros()
    registros_encontrados = 0

    for registro in registros:
        # Sem ONDE, todos os registros devem ser mostrados.
        if nome_coluna is None:
            exibir_registro(registro)
            registros_encontrados += 1

        # Com ONDE, mostra somente os registros que atendem à condição.
        else:
            atende_condicao = avaliar_condicao(
                tabela,
                registro,
                nome_coluna,
                operador,
                token
            )

            if atende_condicao:
                exibir_registro(registro)
                registros_encontrados += 1
    if registros_encontrados == 0:
        print("Nenhum registro encontrado.")

# Verifica se um registro está sendo referenciado por uma chave estrangeira.
def registro_esta_referenciado(banco, nome_tabela, id_registro):
    for tabela in banco.tabelas.values():
        for coluna in tabela.colunas:
            if coluna.chave_estrangeira == nome_tabela:
                registros = tabela.arvore.listar_registros()
                for registro in registros:
                    if registro.valores[coluna.nome] == id_registro:
                        return True
    return False

# Remove registros de uma tabela, podendo aplicar uma condição ONDE.
def apagar_dados(banco, nome_tabela, nome_coluna=None, operador=None, token=None):
    tabela = banco.buscar_tabela(nome_tabela)
    registros = tabela.arvore.listar_registros()
    ids_para_remover = []

    for registro in registros:
        # Sem ONDE, todos os registros são selecionados para remoção.
        if nome_coluna is None:
            ids_para_remover.append(registro.id)

        # Com ONDE, seleciona somente os registros que atendem à condição.
        else:
            atende_condicao = avaliar_condicao(tabela, registro, nome_coluna, operador, token )

            if atende_condicao:
                ids_para_remover.append(registro.id)

    # Antes de remover, verifica se algum registro está sendo referenciado.
    for id_registro in ids_para_remover:
        if registro_esta_referenciado(banco, nome_tabela, id_registro):
            raise ErroIFFARQL(
                f"O registro de id {id_registro} não pode ser removido "
                "porque está sendo referenciado por outra tabela."
            )

    # Somente depois de validar todos os registros, realiza as remoções.
    for id_registro in ids_para_remover:
        tabela.arvore.remover(id_registro)

    return len(ids_para_remover)

# Atualiza o valor de uma coluna nos registros que atendem à condição ONDE.
def atualizar_dados(banco, nome_tabela, nome_coluna_atualizar, novo_token, nome_coluna_condicao=None, operador=None, token_condicao=None):
    tabela = banco.buscar_tabela(nome_tabela)

    # O campo id é automático e nunca pode ser modificado.
    if nome_coluna_atualizar == "id":
        raise ErroIFFARQL(
            "O campo id não pode ser alterado."
        )
    
    coluna = buscar_coluna(
        tabela,
        nome_coluna_atualizar
    )

    novo_valor = novo_token.obter_valor()

    # Impede a atualização de uma coluna com valor nulo.
    if novo_valor is None:
        raise ErroIFFARQL(
            "Valores nulos não são permitidos."
        )

    # Valida o tipo e o uso de aspas do novo valor.
    validar_token(
        coluna,
        novo_token
    )

    registros = tabela.arvore.listar_registros()
    registros_para_atualizar = []

    # Primeiro seleciona todos os registros que deverão ser atualizados.
    for registro in registros:
        # Sem ONDE, todos os registros são selecionados.
        if nome_coluna_condicao is None:
            registros_para_atualizar.append(registro)

        # Com ONDE, seleciona somente os registros que atendem à condição.
        else:
            atende_condicao = avaliar_condicao(
                tabela,
                registro,
                nome_coluna_condicao,
                operador,
                token_condicao
            )
            if atende_condicao:
                registros_para_atualizar.append(registro)

    # Se a coluna atualizada for FK, valida todas as referências antes de alterar.
    if coluna.chave_estrangeira is not None:
        tabela_referenciada = banco.buscar_tabela(
            coluna.chave_estrangeira
        )
        registro_referenciado = tabela_referenciada.arvore.buscar(
            novo_valor
        )
        if registro_referenciado is None:
            raise ErroIFFARQL(
                "Chave estrangeira inexistente."
            )

    # Somente depois das validações aplica a atualização.
    for registro in registros_para_atualizar:
        registro.valores[nome_coluna_atualizar] = novo_valor

    return len(registros_para_atualizar)