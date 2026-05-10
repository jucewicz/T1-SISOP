# Documentação Técnica: `main.py`

## Objetivo do Módulo
O `main.py` atua como o **Relógio Central e Orquestrador (Placa Mãe)** do simulador. 
Nenhuma das outras quatro classes (Assembler, Process, Scheduler, Executor) sabem da existência umas das outras de forma proativa. O `main.py` é o grande regente que dita o fluxo de dados entre elas, avançando o tempo a cada iteração do seu grande loop `while`.

## Estruturas de Destaque

### 1. O Loop do Tempo (`while time < sim_time:`)
Cada repetição desse loop `while` simula o decurso de **1 unidade de tempo (1 tick)**. Para que o EDF (Earliest Deadline First) funcione com perfeição, a ordem das checagens dentro de cada *tick* precisa ser cirurgicamente sequencial:

* **Passo 1 & 2 (Acordar Tarefas):** Antes de qualquer decisão, o sistema vasculha quem estava dormindo (WAITING) ou bloqueado (BLOCKED) e, se o tempo de descanso/bloqueio acabou, insere as tarefas de volta na fila (`READY`).
* **Passo 3 (Detector de Deadline Miss):** Fiscalizamos se alguém estourou o prazo. Isso é feito de forma independente de quem está executando no momento.
* **Passo 4 & 5 (Preempção EDF):** Aqui a mágica ocorre. Perguntamos ao Scheduler: *"Quem tem o menor deadline na fila?"*. Se for alguém diferente de quem está ocupando a CPU, arrancamos o ocupante atual e colocamos de volta na fila (Preempção em ação).
* **Passo 6 & 7 (Ação Bruta da CPU):** A tarefa dona da CPU perde 1 unidade do seu Orçamento de Computação (`ci`). A instrução é lida pelo `executor`. Se a tarefa pedir pra parar (SYSCALL 0), pedir I/O, ou esgotar seu orçamento `ci`, ela é mandada pra dormir, liberando a CPU para o próximo tick.

### 2. Trilha de Auditoria (Timeline)
Em vez de simplesmente cuspir coisas aleatoriamente na tela durante a simulação (o que ficaria uma bagunça caso houvesse comandos de Input/Output do usuário via teclado), nós apenas guardamos o nome do dono da CPU a cada tick no array `timeline`. 
Ao final do grande loop temporal, usamos esse array tanto para imprimir o log tick a tick quanto para desenhar o **Gráfico de Gantt**, formando uma malha visual maravilhosa.

## Conclusão Final
Com o `main.py` fechamos o círculo. O programa pode ser executado facilmente via:
`python main.py meu_cenario_config.json`
