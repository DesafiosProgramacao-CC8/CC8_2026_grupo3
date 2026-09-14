from .tipo_dado import TipoDado

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
