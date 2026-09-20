# Integração do IFFARQL - parte do Robson

## O que foi implementado

A parte do Robson recebe comandos textuais, identifica seus parâmetros e chama
as funções já existentes do grupo. Também executa arquivos `.txt`, salva e
carrega o banco e controla a confirmação das alterações em memória e em disco.

Foram usados a descrição oficial do Trabalho 2, o planejamento do grupo e o
guia de integração da Pessoa 2. Os arquivos das Pessoas 1 e 2 foram preservados.

| Arquivo novo | Responsabilidade |
| --- | --- |
| `tokenizador.py` | Separar trechos do comando e converter literais em `Token`. |
| `sintaxe.py` | Conferir a ordem dos elementos e produzir os parâmetros do comando. |
| `persistencia.py` | Representar o banco em JSON, validar e reconstruir tabelas e árvores, gravar arquivos. |
| `interpretador.py` | Manter a sessão, integrar as funções do grupo, executar transações e arquivos de comandos. |
| `main.py` | Receber entrada pelo terminal e apresentar resultados e erros. |
| `exemplos/` | Roteiros para demonstrar comandos válidos, carregamento e erros. |
| `testes/teste_*.py` novos | Verificar os módulos acima e sua integração. |

Os dados continuam armazenados em `ArvoreRegistros`. Listas e dicionários são
usados para parâmetros e para a representação temporária que será salva em
JSON. O arquivo não contém código Python executável e não é carregado com
`eval` ou `pickle`.

## Executar

Não foram adicionadas dependências externas. Na raiz do repositório:

```powershell
python -B Trabalho_2/main.py
```

O terminal inicia com um banco vazio. Digite `SAIR` para encerrar.

Um exemplo curto, digitado linha por linha:

```text
CRIATABELA cliente (nome TEXTO idade INTEIRO)
INSERIREM cliente VALOR ("Maria Silva" 20)
MOSTRADADOSDE cliente
ATUALIZATABELA cliente COM idade = idade + 1 ONDE id == 1
SALVARBD meu_banco.json
SAIR
```

Em uma nova execução, carregar o banco salvo:

```powershell
python -B Trabalho_2/main.py --banco meu_banco.json
```

Dentro do terminal também é possível usar `CARREGARBD meu_banco.json`, desde
que o banco atual não possua tabelas. Falhas na leitura preservam o estado atual.

## Executar arquivos de exemplo

Na raiz do repositório:

```powershell
python -B Trabalho_2/main.py --arquivo Trabalho_2/exemplos/comandos.txt
python -B Trabalho_2/main.py --arquivo Trabalho_2/exemplos/carregar.txt
python -B Trabalho_2/main.py --arquivo Trabalho_2/exemplos/erros.txt
```

O primeiro cria `Trabalho_2/exemplos/banco_exemplo.json`. O segundo o carrega
em uma nova sessão. O terceiro contém quatro erros propositais e encerra com
código de saída 1, mas executa as demais linhas válidas.

O mesmo carregamento está disponível no terminal:

```text
CARREGARIFFARQL Trabalho_2/exemplos/comandos.txt
```

Os arquivos devem usar UTF-8, com um comando por linha. Linhas vazias são
ignoradas. Um erro informa o caminho e o número da linha, e as próximas linhas
continuam sendo executadas. Os comandos anteriores bem-sucedidos permanecem
confirmados: o arquivo inteiro não é uma única transação.

Dentro de um `.txt`, caminhos relativos são resolvidos a partir da pasta desse
arquivo. No terminal, são relativos à pasta de onde o programa foi iniciado.
Caminhos com espaços devem ficar entre aspas. Arquivos podem carregar outros
arquivos; ciclos são rejeitados e o limite de aninhamento é 20.

## Como a interpretação funciona

1. `tokenizar()` percorre os caracteres. Espaços separam partes fora das aspas;
   dentro delas, pertencem ao texto. Operadores como `>=` permanecem inteiros.
2. `AnalisadorComando` avança por essas partes, exigindo palavras como `VALOR`,
   `COM` e `ONDE` nas posições corretas. Nenhuma alteração ocorre nessa etapa.
3. `converter_valor()` transforma somente os literais nos valores esperados
   pelas funções do grupo. `"20"` vira string, `20` vira inteiro e `20.0` vira
   float. O atributo `com_aspas` acompanha o valor.
4. `Interpretador` chama `criar_tabela`, `inserir_em`, `mostrar_dados`,
   `apagar_dados` ou a função de atualização adequada. As operações matemáticas
   continuam usando o método `operar()` dos tipos já implementados.

`re.fullmatch()` verifica o formato inteiro ou decimal antes da conversão.
`math.isfinite()` rejeita números decimais fora do intervalo representável.
Os booleanos são `True` e `False`. Datas chegam como strings entre aspas e são
validadas pelo tipo da coluna, não por uma tentativa de adivinhar seu tipo.

O adaptador chama `Texto.remover_acentos()`, já existente, nos valores destinados
a colunas TEXTO, inclusive em filtros e atualizações. Não remove acentos dos
nomes de arquivos. As validações de coluna, tipo e comparador também reutilizam
as funções existentes em `condicoes.py`.

Aspas duplas retas (`"`) e o par tipográfico (`“...”`) do PDF são aceitos.
Não há escapes para aspas dentro do valor. A sintaxe segue os exemplos oficiais:
colunas e valores separados por espaços, sem vírgulas ou ponto e vírgula final.
Nomes de tabelas e colunas usam letras ASCII, números e `_`, sem começar por
número. Comandos, tipos e palavras reservadas devem estar em caixa alta.

## Persistência, cache e atomicidade

O JSON tem versão de formato e guarda, para cada tabela:

- nome e colunas, com seus tipos e chaves estrangeiras;
- registros e seus IDs;
- `proximo_id`, inclusive quando o maior ID anterior já foi apagado.

O campo `id` da definição é recriado automaticamente por `Tabela`. O
carregamento verifica o formato, tipos, IDs duplicados, campos de cada registro,
referências e o próximo ID. As tabelas são criadas antes de verificar as FKs,
para que a ordem no JSON não determine se a leitura funciona. As árvores são
reconstruídas inserindo primeiro a mediana dos IDs, evitando uma árvore linear.

Uma alteração executa os seguintes passos:

1. Reconstrói uma cópia independente do estado atual.
2. Executa a operação nessa cópia, utilizando as funções do grupo.
3. Valida e grava o resultado em um arquivo temporário, na pasta do destino.
4. Executa `flush` e `fsync`, fecha o temporário e substitui o arquivo de destino
   com `os.replace`.
5. Publica as tabelas da cópia no banco da sessão.

Se a operação ou a gravação falhar antes da substituição, a cópia é descartada;
o banco original permanece em memória e o arquivo anterior é preservado.
Isso também evita publicar alterações parciais de uma função chamada.

Antes de um `SALVARBD` ou `CARREGARBD` explícito, o destino automático é
`Trabalho_2/.iffarql_cache.json`. Depois de um desses comandos, as alterações
seguintes são salvas no arquivo escolhido. O cache inicial deixa de ser
atualizado; ele não representa alterações posteriores feitas no arquivo ativo.

Para recuperar uma sessão que usava apenas cache:

```powershell
python -B Trabalho_2/main.py --banco Trabalho_2/.iffarql_cache.json
```

Não há recuperação automática ao abrir o terminal. Um aviso informa se há um
cache anterior; carregue-o antes de criar tabelas, pois novas alterações de uma
sessão vazia substituem o cache. `--cache caminho.json` permite escolher outro
destino inicial. Consultas não salvam arquivos.

## Testes

Na raiz, entre na pasta do Trabalho 2 e execute:

```powershell
cd Trabalho_2
python -B -m testes.teste_tokenizador
python -B -m testes.teste_sintaxe
python -B -m testes.teste_persistencia
python -B -m testes.teste_interpretador
python -B -m testes.teste_terminal
python -B -m testes.teste_completo
python -B -m testes.teste_completo_pessoa2
cd ..
```

Não use `-O`: os testes usam `assert`. O `-B` evita gerar bytecode. Os testes de
arquivos utilizam pastas temporárias e não alteram bancos do usuário. Incluem
falha simulada de gravação, rollback, IDs após exclusão e reinício, integridade
referencial, tipo dos valores, erros por linha e execução real do terminal em
outros processos.

## Limitações e pontos para conversar com o grupo

Na parte nova:

- Cada alteração copia o banco completo. É uma solução didática para
  atomicidade; bancos maiores exigiriam outra estratégia.
- Não há controle de acesso simultâneo ao mesmo arquivo, conforme a dispensa
  de concorrência no enunciado. Use uma sessão por arquivo.
- Decimais usam dígitos antes e depois do ponto. Não são aceitos expoentes,
  vírgula decimal ou escapes de aspas. Não há expressões aninhadas nem mais de
  uma condição `ONDE`. Uma operação de atualização usa a própria coluna e um
  valor literal, como `COM idade = idade + 1`.
- As tabelas são substituídas ao confirmar uma transação. Quem integra a classe
  deve consultar `interpretador.banco` novamente após cada comando, em vez de
  manter referências antigas a objetos de tabela ou registro.

Pontos observados nos módulos existentes, sem modificá-los:

- `Data.validar()` aceita `01/01/0000` e `1/001/2026`, embora o enunciado peça
  ano a partir de 0001 e formato exato `dd/mm/aaaa`. A persistência reutiliza
  esse validador; essa limitação também afeta os bancos carregados.
- Algumas validações de operações e de atualização de `id` em múltiplos `COM`
  dependem de haver registros. Por exemplo, uma operação BOOLEANO inválida em
  tabela vazia pode retornar zero alterações sem erro.
- A divisão de INTEIRO usa divisão em ponto flutuante internamente e pode
  perder precisão em números grandes: `9007199254740993 / 1` resulta em
  `9007199254740992` na implementação atual.
- O tipo DATA mantém anos bissextos, conforme a autorização do professor
  registrada no guia de integração da Pessoa 2. A descrição original do
  trabalho propunha desconsiderá-los.

## Como separar os commits

Os quatro primeiros grupos foram commitados separadamente e integrados à
`main`, preservando seus commits. O trabalho seguirá pela `main`. Os blocos
abaixo registram a divisão das alterações; não repita os commits já feitos.
O README de planejamento que ficou apenas local não está incluído nestes comandos.

Execute os grupos abaixo **na raiz do repositório**, na ordem indicada. Depois
de cada `git add`, confira `git diff --cached` antes de executar o commit.
Se aparecer algum arquivo além dos listados para a etapa, revise a seleção.

### 1. Tokenização

```powershell
git add -- Trabalho_2/tokenizador.py Trabalho_2/testes/teste_tokenizador.py
git diff --cached
git commit -m "implementa tokenizacao e conversao de valores IFFARQL"
```

### 2. Análise da sintaxe

```powershell
git add -- Trabalho_2/sintaxe.py Trabalho_2/testes/teste_sintaxe.py
git diff --cached
git commit -m "implementa analise da sintaxe dos comandos IFFARQL"
```

### 3. Persistência

```powershell
git add -- Trabalho_2/persistencia.py Trabalho_2/testes/teste_persistencia.py
git diff --cached
git commit -m "implementa persistencia JSON com preservacao de ids"
```

### 4. Integração e transações

```powershell
git add -- Trabalho_2/interpretador.py Trabalho_2/testes/teste_interpretador.py Trabalho_2/.gitignore
git diff --cached
git commit -m "integra comandos com autosave transacoes e arquivos txt"
```

### 5. Terminal, exemplos e documentação

```powershell
git add -- Trabalho_2/main.py Trabalho_2/testes/teste_terminal.py Trabalho_2/exemplos/comandos.txt Trabalho_2/exemplos/carregar.txt Trabalho_2/exemplos/erros.txt Trabalho_2/GUIA_ROBSON.md
git diff --cached
git commit -m "adiciona terminal exemplos e guia de uso do IFFARQL"
```

Depois dos commits revisados e dos testes passando, confira e envie a branch:

```powershell
git status
git log -5 --oneline
git push origin main
```

O push envia os commits da `main` local à `main` remota. Como essa branch é
compartilhada com o grupo, se o push for rejeitado, confira as alterações
remotas antes de continuar. Não use `--force` para sobrescrevê-las.
