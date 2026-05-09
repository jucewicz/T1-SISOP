# Documentação Técnica: `assembler.py`

## Objetivo do Módulo
O `assembler.py` atua como o **Parser / Tradutor** do nosso simulador. A responsabilidade exclusiva dele é ler um arquivo de texto contendo o código Assembly hipotético e converter o texto bruto em estruturas de dados fáceis de serem iteradas pelo motor do simulador em Python.

Este módulo **não executa** o código, ele apenas realiza a análise léxica e constrói as áreas de memória e de instruções.

---

## Assinatura Principal
```python
def parse_asm(filepath: str) -> tuple[list, dict, dict]:
```

### O que ele devolve (Retorno)
Ao invocar essa função, o simulador recebe três estruturas:
1. **`instructions` (Lista de Tuplas):** Cada tupla representa `(Mnemônico, Operando)`. Se não houver operando, será `None`. Exemplo: `[('LOAD', 'variavel'), ('SUB', '#1')]`.
2. **`data` (Dicionário):** Representa a memória estática inicial da tarefa. Mapeia o nome da variável para o seu valor numérico. Exemplo: `{'variavel': 3}`.
3. **`labels` (Dicionário):** Mapeia os pontos de salto (labels) para o **índice numérico** da linha da instrução na lista `instructions`. Exemplo: `{'ponto1': 1}` (significa que um salto para `ponto1` deve apontar o Program Counter para a instrução 1).

---

## Como o Parser Funciona (Fluxo Interno)

1. **Separação por Blocos (`.code` e `.data`)**:
   O arquivo é lido linha a linha e o parser utiliza uma flag `section` que guarda qual bloco estamos lendo no momento, garantindo que variáveis não se misturem com código executável.

2. **Tokenização (`split()`)**:
   Em vez de usar expressões regulares complexas, o código quebra cada linha usando `tokens = line.split()`. Isso elimina múltiplos espaços em branco ou tabulações desnecessárias automaticamente.

3. **Resolução Inteligente do `#` (Comentário vs Imediato)**:
   A linguagem hipotética deste trabalho possui uma armadilha: o caractere `#` é usado tanto para comentários (ex: `# Isso é um comentário`) quanto para designar operandos em Modo Imediato (ex: `SUB #1`).
   
   **Como o `assembler` resolve:**
   Como a sintaxe define o `#` imediato "grudado" ao número, a tokenização os mantém juntos na Posição 1 (`tokens[1]`). Qualquer `#` solto a partir da Posição 2 em diante é considerado comentário. Na prática, lemos `tokens[0]` e `tokens[1]` e **ignoramos completamente** o restante do array de tokens, limpando comentários inline de forma performática.

4. **Resolução de Labels Preditiva**:
   Quando a primeira palavra termina em `:` (ex: `ponto1:`), ela é tratada como Label. Em vez de percorrer a lista duas vezes, o Label é mapeado preditivamente apontando para `len(instructions)`. Como vetores são indexados em 0, o tamanho atual da lista aponta perfeitamente para o índice da *próxima* instrução a ser inserida. Em seguida, o label é cortado da lista de tokens (`tokens = tokens[1:]`) para que o resto da linha seja analisado normalmente.
