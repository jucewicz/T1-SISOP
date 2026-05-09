# TP1 - Plano de Implementação: Simulador EDF com Assembly Hipotético

## Contexto
Implementar um simulador de escalonamento **EDF (Earliest Deadline First)** em **Python 3** que:
1. Interpreta programas escritos em uma linguagem assembly hipotética (acumulador + PC)
2. Simula múltiplas tarefas periódicas com preempção
3. Exibe o timeline de execução tick a tick e sinaliza perdas de deadline

**Sobre `sch_pol`**: o PDF pede para declarar `sch_pol = 1`. Em vez disso, a política EDF será representada pela própria classe `EDFScheduler` — o escalonador **é** o EDF, sem variável de seleção. Isso é semanticamente correto e mais limpo.

---

## Linguagem: Python 3
- Parsing de texto simples com `split()` e `strip()`
- Estruturas de dados nativas (`list`, `dict`)
- Sem gerenciamento manual de memória
- `heapq` ou `min()` para fila de prioridade EDF
- Roda em qualquer plataforma (laboratório do prédio 32)

---

## Estrutura de Arquivos

```
tp1/
├── main.py         # Interface CLI e loop de simulação principal
├── assembler.py    # Parser da linguagem assembly hipotética
├── process.py      # Classe Process e enum de estados
├── scheduler.py    # Escalonador EDF (sem sch_pol)
├── executor.py     # Motor de execução de instruções
└── exemplos/
    ├── prog1.asm   # Programa da Figura 1 do PDF
    └── prog2.asm   # Segundo programa para teste de preempção
```

---

## Módulo 1: `assembler.py`

### Formato do arquivo `.asm`
```
.code
    LOAD variavel          # modo direto
    ponto1: SUB #1         # label + modo imediato
    SYSCALL 1
    BRPOS ponto1
    SYSCALL 0
.endcode
.data
    variavel 3
.enddata
```

### Regras de parsing:
- Linhas começando com `#` ou vazias → ignorar
- Comentários inline (`# ...`) → remover antes de processar
- **Labels**: formato `nome:` antes da instrução (ou sozinhos na linha)
  - Registrar `label_map[nome] = índice_da_instrução`
- **Operandos**:
  - `#5` → modo imediato, valor 5
  - `variavel` → modo direto, busca em `data[variavel]`
  - `label` → usado por instruções de salto

### Função principal:
```python
def parse_asm(filepath: str) -> tuple[list, dict, dict]:
    """
    Retorna:
      instructions : list de (mnemônico: str, operando: str | None)
      data         : dict {nome_var: valor_int}
      labels       : dict {nome_label: índice_instrução}
    """
```

### Exemplo de saída para a Figura 1:
```python
instructions = [
    ("LOAD", "variable"),      # índice 0
    ("SUB",  "#1"),            # índice 1  ← ponto1
    ("SYSCALL", "1"),          # índice 2
    ("BRPOS", "ponto1"),       # índice 3
    ("SYSCALL", "0"),          # índice 4
]
data   = {"variable": 3}
labels = {"ponto1": 1}
```

---

## Módulo 2: `process.py`

### Estados possíveis:
```python
class State:
    WAITING    = "WAITING"    # aguardando próxima ativação periódica
    READY      = "READY"      # na fila, pronto para executar
    RUNNING    = "RUNNING"    # ocupando a CPU
    BLOCKED    = "BLOCKED"    # bloqueado por SYSCALL 1 ou 2
    TERMINATED = "TERMINATED" # encerrado definitivamente (fora do escopo periódico)
```

### Classe Process:
```python
class Process:
    def __init__(self, name, asm_file, arrival, ci, pi):
        # --- Programa ---
        self.instructions, self.init_data, self.labels = parse_asm(asm_file)

        # --- Parâmetros EDF ---
        self.name    = name
        self.arrival = arrival   # instante de chegada
        self.ci      = ci        # tempo de computação (budget por período)
        self.pi      = pi        # período = deadline

        # --- Estado da CPU (preservado entre preempções, resetado entre períodos) ---
        self.pc  = 0
        self.acc = 0
        self.data = dict(self.init_data)

        # --- Estado de escalonamento ---
        self.state             = State.WAITING
        self.absolute_deadline = arrival + pi  # primeiro deadline absoluto
        self.remaining_ci      = ci            # budget restante no período atual
        self.blocked_until     = 0             # tempo de desbloqueio
        self.next_activation   = arrival       # quando a tarefa deve ser reativada
```

### Método `start_new_period(current_time)`:
```python
def start_new_period(self, current_time):
    """Chamado ao ativar tarefa para novo período."""
    self.pc           = 0
    self.acc          = 0
    self.data         = dict(self.init_data)
    self.remaining_ci = self.ci
    self.state        = State.READY
    # absolute_deadline já foi atualizado pelo scheduler antes desta chamada
```

---

## Módulo 3: `executor.py`

### Função principal:
```python
def execute_instruction(process) -> str:
    """
    Executa UMA instrução do processo.
    Retorna:
      'ok'   → instrução normal; pc já foi avançado
      'halt' → SYSCALL 0 (fim de período ou fim definitivo)
      'io'   → SYSCALL 1 ou 2 (deve bloquear)
    """
```

### Helper de resolução de operando:
```python
def resolve(operand: str, data: dict) -> int:
    """'#5' → 5 (imediato)  |  'x' → data['x'] (direto)"""
    if operand.startswith('#'):
        return int(operand[1:])
    return data[operand.lower()]
```

### Tabela de execução por instrução:

| Instrução      | Ação                                              | Avança PC? |
|----------------|---------------------------------------------------|------------|
| `ADD op`       | `acc += resolve(op)`                              | Sim        |
| `SUB op`       | `acc -= resolve(op)`                              | Sim        |
| `MULT op`      | `acc *= resolve(op)`                              | Sim        |
| `DIV op`       | `acc = int(acc / resolve(op))`                    | Sim        |
| `LOAD op`      | `acc = resolve(op)` (imediato ou direto)          | Sim        |
| `STORE op`     | `data[op] = acc` (apenas direto)                  | Sim        |
| `BRANY label`  | `pc = labels[label]`                              | Não        |
| `BRPOS label`  | `if acc > 0: pc = labels[label]` senão pc+=1      | Condicional|
| `BRZERO label` | `if acc == 0: pc = labels[label]` senão pc+=1     | Condicional|
| `BRNEG label`  | `if acc < 0: pc = labels[label]` senão pc+=1      | Condicional|
| `SYSCALL 0`    | return `'halt'`                                   | Não        |
| `SYSCALL 1`    | `print(acc)` + return `'io'`                      | Não        |
| `SYSCALL 2`    | `acc = int(input())` + return `'io'`              | Não        |

---

## Módulo 4: `scheduler.py` — EDF puro (sem `sch_pol`)

**Estratégia para evitar `sch_pol`**: a classe `EDFScheduler` encapsula a política de escalonamento. Não há variável numérica — instanciar `EDFScheduler` já é a escolha de política.

```python
class EDFScheduler:
    def __init__(self):
        self.ready_queue: list[Process] = []

    def add(self, process: Process):
        if process not in self.ready_queue:
            self.ready_queue.append(process)
        process.state = State.READY

    def remove(self, process: Process):
        self.ready_queue.remove(process)

    def select_next(self) -> Process | None:
        """EDF: retorna o processo com menor deadline absoluto."""
        if not self.ready_queue:
            return None
        return min(self.ready_queue, key=lambda p: p.absolute_deadline)

    def needs_preemption(self, running: Process) -> bool:
        """True se houver tarefa pronta com deadline menor que a em execução."""
        if not self.ready_queue:
            return False
        best = self.select_next()
        return best.absolute_deadline < running.absolute_deadline
```

---

## Módulo 5: `main.py` — Loop de Simulação

### Entrada (via arquivo JSON de configuração):
```json
{
  "tasks": [
    { "name": "T1", "file": "exemplos/prog1.asm", "arrival": 0, "ci": 3, "pi": 6 },
    { "name": "T2", "file": "exemplos/prog2.asm", "arrival": 2, "ci": 2, "pi": 8 }
  ]
}
```
Executar com: `python main.py config.json`

### Algoritmo do loop principal (pseudocódigo detalhado):

```
Cria EDFScheduler
Cria lista de processes no estado WAITING
running_process = None
time = 0
timeline = []

ENQUANTO existem processos não-TERMINATED:

  [PASSO 1 — Ativações periódicas]
  Para cada process em WAITING:
      SE process.next_activation <= time:
          process.absolute_deadline = process.next_activation + process.pi
          process.start_new_period(time)
          scheduler.add(process)

  [PASSO 2 — Desbloquear processos]
  Para cada process em BLOCKED:
      SE process.blocked_until <= time:
          scheduler.add(process)   # deadline permanece o mesmo

  [PASSO 3 — Detectar deadline misses]
  Para cada process (exceto TERMINATED e WAITING):
      SE time > process.absolute_deadline:
          PRINT "*** DEADLINE MISS: {process.name} no instante t={time} ***"

  [PASSO 4 — Selecionar próxima tarefa (EDF)]
  next_proc = scheduler.select_next()

  [PASSO 5 — Preempção se necessário]
  SE running_process != None E running_process != next_proc:
      # Preempção: tarefa atual volta para fila de prontos
      scheduler.add(running_process)   # estado → READY, deadline preservado
      running_process = None

  [PASSO 6 — Colocar nova tarefa em execução]
  SE next_proc != None:
      scheduler.remove(next_proc)
      next_proc.state = RUNNING
      running_process = next_proc

  [PASSO 7 — Executar UMA instrução]
  SE running_process != None:
      result = execute_instruction(running_process)
      running_process.remaining_ci -= 1

      SE result == 'halt':
          # SYSCALL 0: fim deste período
          running_process.next_activation   = running_process.absolute_deadline
          running_process.absolute_deadline += running_process.pi
          running_process.state              = WAITING
          running_process                    = None

      SENÃO SE result == 'io':
          # SYSCALL 1 ou 2: bloquear por 1-3 unidades de tempo
          block_time = random.randint(1, 3)
          running_process.blocked_until = time + block_time
          running_process.state         = BLOCKED
          running_process               = None

      SENÃO SE running_process.remaining_ci <= 0:
          # Budget do período esgotado (caso i do PDF)
          running_process.next_activation   = running_process.absolute_deadline
          running_process.absolute_deadline += running_process.pi
          running_process.state              = WAITING
          running_process                    = None

  [PASSO 8 — Registrar no timeline]
  nome = running_process.name SE running_process != None SENÃO "IDLE"
  timeline.append((time, nome))
  time += 1

Exibir timeline e Gantt ao final
```

### Saída esperada:
```
=== SIMULAÇÃO EDF ===
t= 0: [T1]
t= 1: [T1]
t= 2: [T2]  <- preempção (deadline T2 < deadline T1)
t= 3: [T2]
t= 4: [T1]
t= 5: IDLE
t= 6: [T1]
...
*** DEADLINE MISS: T1 no instante t=9 ***

=== GANTT ===
     0123456789...
T1:  ##.##.##...
T2:  ..##....##.
```

---

## Ordem de Implementação

1. **`assembler.py`** — parser do assembly
   - Testar manualmente com o programa da Figura 1 do PDF
2. **`executor.py`** — execução instrução a instrução
   - Testar sem scheduler: rodar um programa sozinho até SYSCALL 0
3. **`process.py`** — classe de processo com todos os campos
4. **`scheduler.py`** — EDFScheduler com testes de ordenação por deadline
5. **`main.py`** — loop de simulação completo + I/O

---

## Verificação / Testes

| Caso de teste | O que verificar |
|---|---|
| Programa da Figura 1 (1 tarefa) | Executa loop 3x (variável=3), imprime 2,1,0, termina |
| 2 tarefas sem sobreposição | Timeline mostra cada tarefa no seu período sem preempção |
| 2 tarefas com preempção EDF | Tarefa com deadline menor interrompe a outra |
| SYSCALL 1 e 2 | Tarefa vai para BLOCKED por 1-3 ticks e retorna |
| Deadline miss intencional | `ci > pi` → deve detectar e imprimir aviso |
| Bloqueio + preempção juntos | Tarefa bloqueada + outra tarefa chega com deadline menor |
