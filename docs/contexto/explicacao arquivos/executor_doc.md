# Documentação Técnica: `executor.py`

## Objetivo do Módulo
O `executor.py` funciona como a **ALU (Arithmetic Logic Unit)** e o cerne da CPU do nosso simulador. É o único arquivo que contém lógica matemática real e sabe o que as instruções do Assembly significam.

Ele não guarda estado nenhum (não é um Objeto/Classe). Ele recebe um paciente (`Process`), faz uma "cirurgia" rápida (altera os registradores e memória dele) baseado na linha atual, e o devolve para o Sistema Operacional.

## Estruturas de Destaque

### 1. A Função Auxiliar `resolve(operand, data)`
Para evitar ter que escrever `if/else` complexos dentro de cada operação (ADD, SUB, MULT...), isolamos o conceito de Modo de Endereçamento em uma micro-função:
* **Modo Imediato:** Se receber `#5`, o fatiamento de string (`operand[1:]`) arranca a cerquilha e o Python converte a string `"5"` para o número inteiro `5`.
* **Modo Direto:** Se não tiver `#`, ele entende que é o nome de uma variável e retorna diretamente a chave do Dicionário de dados `data[operand]`.

### 2. O Incremento do Program Counter (`pc += 1`)
A primeira coisa que o Executor faz depois de ler a instrução atual é avançar o ponteiro: `process.pc += 1`.
Isso foi feito propositalmente *antes* da execução dos comandos para simplificar os Saltos (Branches). Se for um comando normal (ADD), a instrução roda e o ponteiro já está pronto para o próximo ciclo. Se for um Salto Condicional (ex: `BRPOS`) e o salto for verdadeiro, nós simplesmente sobrescrevemos o PC (`process.pc = process.labels[operand]`) ignorando o +1 que demos antes. Uma manobra muito elegante.

### 3. Comunicação de Volta com o `main.py`
Para manter o Acoplamento Baixo (Low Coupling), o `executor.py` não tem permissão para travar processos ou interagir com a Fila do Scheduler. Por isso, a função sempre **retorna uma String** servindo como um "Recibo" para o Maestro (`main.py`):
* `"ok"`: A instrução era normal, gaste 1 tick de relógio da tarefa e continue.
* `"halt"`: A tarefa pediu `SYSCALL 0`. O Executor avisa o `main` para retirá-la da CPU e resetá-la para o próximo período.
* `"io"`: A tarefa pediu `SYSCALL 1 ou 2`. O Executor faz a leitura do teclado / impressão na tela usando o I/O do próprio Python, mas avisa o `main`: *"Ei, coloque esse cara de castigo bloqueado de 1 a 3 ticks"*.
