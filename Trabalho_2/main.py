import argparse

from erros import ErroIFFARQL
from interpretador import CACHE_PADRAO, Interpretador


def apresentar(resultado):
    if resultado.mensagem:
        print(resultado.mensagem)
    for erro in resultado.erros:
        print(f"Erro: {erro}")
    return 1 if resultado.erros else 0


def main(argumentos=None):
    parser = argparse.ArgumentParser(description="Terminal do banco de dados IFFARQL.")
    parser.add_argument("--banco", help="Carrega um banco JSON antes dos comandos.")
    parser.add_argument("--arquivo", help="Executa um arquivo .txt e encerra.")
    parser.add_argument("--cache", default=str(CACHE_PADRAO), help="Arquivo do salvamento automático inicial.")
    opcoes = parser.parse_args(argumentos)
    interpretador = Interpretador(arquivo_cache=opcoes.cache)

    try:
        if opcoes.banco:
            apresentar(interpretador.executar_comando(f'CARREGARBD "{opcoes.banco}"'))
        if opcoes.arquivo:
            return apresentar(interpretador.executar_comando(f'CARREGARIFFARQL "{opcoes.arquivo}"'))
    except ErroIFFARQL as erro:
        print(f"Erro: {erro}")
        return 1

    print("IFFARQL - digite os comandos em caixa alta. Use SAIR para encerrar.")
    if interpretador.arquivo_ativo is None:
        print(f'Cache automático: "{interpretador.arquivo_cache}"')
        if interpretador.arquivo_cache.exists():
            print("Há um cache anterior. Para recuperá-lo, use CARREGARBD antes de criar tabelas.")

    while True:
        try:
            texto = input("IFFARQL> ")
            if texto.strip() == "SAIR":
                break
            if not texto.strip():
                continue
            apresentar(interpretador.executar_comando(texto))
        except ErroIFFARQL as erro:
            print(f"Erro: {erro}")
        except (EOFError, KeyboardInterrupt):
            print("\nSessão encerrada.")
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
