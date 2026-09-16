from erros import ErroIFFARQL
class BancoDados:

    def __init__(self):
        self.tabelas = {}

    def existe_tabela(self, nome):
        return nome in self.tabelas

    def adicionar_tabela(self, tabela):
        if self.existe_tabela(tabela.nome):
            raise ErroIFFARQL("Tabela já existe")

        self.tabelas[tabela.nome] = tabela

    def buscar_tabela(self, nome):
        if not self.existe_tabela(nome):
            raise ErroIFFARQL("Tabela não encontrada")

        return self.tabelas[nome]

    def apagar_tabela(self, nome):
        if not self.existe_tabela(nome):
            raise ErroIFFARQL("Tabela não encontrada")

        tabela = self.tabelas[nome]

        if hasattr(tabela, "registros") and len(tabela.registros) > 0:
            raise ErroIFFARQL("Não é possível apagar uma tabela que possui registros")

        del self.tabelas[nome]
