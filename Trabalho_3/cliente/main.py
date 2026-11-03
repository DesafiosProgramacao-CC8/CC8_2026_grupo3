# Ponto de entrada da aplicação cliente IFFARCHAT.
import sys
from pathlib import Path

#Permite importar o pacote Trabalho_3, como no servidor.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from interface import JanelaIFFARChat


def main():
    app = JanelaIFFARChat()
    app.mainloop()


if __name__ == "__main__":
    main()
