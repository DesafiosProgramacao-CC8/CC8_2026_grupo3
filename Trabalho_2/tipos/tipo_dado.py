class TipoDado:
    def validar(self, valor):
        raise NotImplementedError
    
     # Executa uma operação permitida para o tipo de dado.
    def operar(self, valor_atual, operador, valor_operacao):

        raise NotImplementedError