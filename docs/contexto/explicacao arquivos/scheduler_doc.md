# Documentação Técnica: `scheduler.py`

## Objetivo do Módulo
O módulo `scheduler.py` é o núcleo de tomada de decisão do sistema operacional virtual. Enquanto o `process.py` apenas guarda os dados e o `executor.py` faz a conta bruta, o **Escalonador** decide a ordem em que as tarefas terão o privilégio de usar a CPU.

Neste projeto, implementamos **exclusivamente a política EDF** (Earliest Deadline First / Prazo Mais Curto Primeiro).

## A simplicidade do EDF e a ausência da variável `sch_pol`
O PDF do trabalho solicitou a criação de uma variável numérica (`sch_pol = 1`) para selecionar a política. Do ponto de vista de Engenharia de Software Orientada a Objetos, nós transformamos essa "flag" genérica em uma Classe Concreta (`EDFScheduler`). 
Se no futuro o professor pedisse para implementar *Round Robin*, nós criaríamos a classe `RoundRobinScheduler` e trocaríamos no `main.py`, sem precisar encher o código de `if sch_pol == 1... else if sch_pol == 2...`.

## Como foi implementado no Python?

A classe possui uma única responsabilidade: Gerenciar a `ready_queue` (Fila de Prontos).

### 1. Métodos `add` e `remove`
Não guardam segredo. Se uma tarefa acorda do seu período de sono (WAITING) ou sofre preempção, ela toma um `add()`. Quando ela é escolhida para usar a CPU, ela sofre um `remove()` (pois quem está rodando na CPU não fica ocupando assento na sala de espera).

### 2. A Matemática Pura (`select_next`)
Em Java, para descobrir quem é o objeto dentro de um ArrayList que possui a menor propriedade numérica X, você precisaria criar uma interface `Comparator<Process>` ou implementar `Comparable` na classe `Process`, fazer um loop gigante ou usar a pesada Stream API (`list.stream().min(...)`).

**No Python, toda essa lógica é condensada em uma única linha matadora:**
```python
return min(self.ready_queue, key=lambda p: p.absolute_deadline)
```
**Traduzindo para desenvolvedores Java/C:**
- `min()` é a função nativa do Python construída em C puro, extremamente rápida, que vasculha um Array atrás do menor elemento.
- `key=` é o "Comparator".
- `lambda p: p.absolute_deadline` é uma **Função Anônima** inline. Lê-se: *"Para cada processo `p` na fila, pegue a variável `absolute_deadline` dele e use isso como base de comparação numérica"*.

Se houver empate (duas tarefas com deadlines iguais chegando ao mesmo tempo), a função `min` vai pegar a que foi inserida primeiro na lista por padrão (First In First Out entre os empatados).

### Conclusão
Com míseras 30 linhas de código, eliminamos a necessidade de for loop complexo, garantimos O(n) na busca do próximo candidato e encapsulamos totalmente a política matemática do edital!
