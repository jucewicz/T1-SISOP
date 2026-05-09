# Documentação Técnica: `process.py`

## Objetivo do Módulo
O módulo `process.py` atua como o **Bloco de Controle de Processo (PCB - Process Control Block)**. Ele é uma classe puramente focada em guardar o estado de uma tarefa (seus dados, sua linha atual de execução, e suas regras de tempo real). Ele atua como uma "memória viva" de cada programa carregado.

## O que foi implementado

### 1. Classe `State` (Constantes de Estado)
Em vez de usar strings mágicas (que podem causar bugs de digitação), criamos uma classe simulando um *Enum* para travar os 5 estados possíveis que a máquina de estados do nosso simulador exige:
- `WAITING`: A tarefa completou seu trabalho e está dormindo, esperando o tempo passar para começar o seu próximo período.
- `READY`: A tarefa acordou (ou sofreu preempção) e está na fila do `scheduler`, aguardando por CPU.
- `RUNNING`: A tarefa é a dona absoluta do processador neste instante e está executando no `executor`.
- `BLOCKED`: A tarefa chamou I/O (Syscall 1 ou 2) e tomou um "castigo" de espera de 1 a 3 ticks de relógio.
- `TERMINATED`: A tarefa morreu de vez.

### 2. Classe `Process`
É o modelo de dados de fato. 

**A mágica da Inicialização (`__init__`):**
- Quando um objeto Processo nasce, ele imediatamente chama o método `parse_asm()` (do módulo `assembler.py`), mastigando o arquivo de texto e absorvendo para si próprio as instruções traduzidas e variáveis de memória originais (`init_data`).
- Ele inicializa os ponteiros do processador zerados: o Contador de Programa (`pc = 0`) e o Acumulador (`acc = 0`).
- Ele define as regras matemáticas iniciais do simulador:
  - `absolute_deadline` recebe o tempo da primeira chegada + o período (`arrival + pi`).
  - `remaining_ci` (O "budget" ou tempo computacional exigido para o loop) recebe o custo total `ci`.
  - `next_activation` dita quando o processo deverá sair do modo WAITING pela primeira vez (que é o próprio `arrival`).

**O método `start_new_period()`:**
Como o edital do trabalho pede a modelagem de um sistema de **tarefas periódicas**, sempre que um novo período $P_i$ começa, a CPU virtual precisa ser resetada para rodar o loop de novo. 
Esse método atua como o **Reboot da Tarefa**. Ele zera o `pc`, zera o `acc`, puxa um clone das variáveis do arquivo de novo para apagar lixo de memória anterior (`dict(self.init_data)`), renova todo o seu orçamento de processamento (`remaining_ci = ci`) e diz: *"Estou pronto para ir pra fila novamente"* (`State.READY`).

---

## Como isso se compara ao paradigma do Java ou C?

* **Atributos Públicos:** No Java, é de praxe usarmos modificadores `private` junto com dúzias de métodos getters/setters (`getPc()`, `setAcc(10)`) para forçar o Encapsulamento. Em Python, filosoficamente confia-se no programador. Nós não usamos setters. O `main.py` e o `executor.py` vão acessar o `t1.pc` e `t1.acc` diretamente e alterá-los em tempo de execução de forma limpa. Ela age quase como uma `struct` gigante do C cheia de poderes.
* **O Método `__repr__`:** Sabe quando você tenta dar um `System.out.println(meuObjeto)` no Java e ele imprime um lixo de memória ilegível (ex: `Process@1a2b3c`) a menos que você sobrescreva o `@Override public String toString()`? O método especial `def __repr__(self):` do Python faz exatamente a mesma coisa, ensinando ao `print()` como aquele objeto deve ser renderizado como texto na tela. Útil para debugar!
