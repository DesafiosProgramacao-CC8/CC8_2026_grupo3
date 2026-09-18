from datetime import datetime, timedelta
from .tipo_dado import TipoDado
from erros import ErroIFFARQL

class Data(TipoDado):
    def validar(self, valor):
        if not isinstance(valor, str):
            return False

        if len(valor) != 10:
            return False

        partes = valor.split("/")

        if len(partes) != 3:
            return False

        dia, mes, ano = partes
        if not (dia.isdigit() and mes.isdigit() and ano.isdigit()):
            return False

        dia = int(dia)
        mes = int(mes)
        ano = int(ano)

        if ano < 0 or ano > 9999:
            return False

        if mes < 1 or mes > 12:
            return False

        if dia < 1 or dia > 31:
            return False    

        dias_por_mes = {
            1: 31,
            2: 29 if (ano % 4 == 0 and ano % 100 != 0) or (ano % 400 == 0) else 28,
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 30,
            10: 31,
            11: 30,
            12: 31
        }

        if dia < 1 or dia > dias_por_mes[mes]:
            return False

        return True

# Soma ou subtrai uma quantidade inteira de dias de uma DATA.

    def operar(self, valor_atual, operador, valor_operacao):

        if not isinstance(valor_operacao, int) or isinstance(valor_operacao, bool):

            raise ErroIFFARQL(

                "DATA somente pode ser operada com um valor INTEIRO."

            )

        # Confirma que a data original é válida antes de realizar a operação.
        if not self.validar(valor_atual):
            raise ErroIFFARQL(
                "Valor de DATA inválido."
            )

        data = datetime.strptime(
            valor_atual,
            "%d/%m/%Y"
        )
        if operador == "+":
            resultado = data + timedelta(
                days=valor_operacao
            )
        elif operador == "-":
            resultado = data - timedelta(
                days=valor_operacao
            )
        else:
            raise ErroIFFARQL(
                f"Operador '{operador}' não permitido para DATA."
            )

        return resultado.strftime(
            "%d/%m/%Y"
        )