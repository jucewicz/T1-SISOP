# Simulador de Escalonamento EDF (Earliest Deadline First)

Este projeto é um simulador de Sistemas Operacionais focado na política de escalonamento de tempo real **EDF (Earliest Deadline First)**. Ele é capaz de ler arquivos de código Assembly hipotético, interpretá-los, e simular o compartilhamento de uma única CPU entre múltiplas tarefas periódicas, com preempção e suporte a I/O.

---

## Pré-requisitos e Compilação

**Linguagem:** Python 3.x

Como o projeto foi desenvolvido inteiramente em Python, **não há etapa de compilação**. O código é interpretado diretamente pela máquina virtual do Python, dispensando o uso de Makefiles ou compiladores externos (como o `gcc` do C ou `javac` do Java).

Certifique-se apenas de ter o Python instalado na sua máquina. Você pode verificar executando no terminal:
```bash
python --version
```

---

## Como Executar o Simulador

Para iniciar a simulação, basta executar o arquivo principal (`main.py`), passando o arquivo de configuração de cenário como argumento:

```bash
python main.py config.json
```

Se você executar apenas `python main.py` sem passar argumentos, o simulador tentará procurar automaticamente por um arquivo chamado `config.json` no mesmo diretório.

---

## Como Configurar o Cenário (JSON)

O estado inicial do simulador, bem como as propriedades de tempo real de cada tarefa, são definidos através de um arquivo `JSON`.

**Exemplo de um `config.json`:**
```json
{
  "simulation_time": 20,
  "tasks": [
    {
      "name": "T1",
      "file": "prog1.asm",
      "arrival": 0,
      "ci": 3,
      "pi": 6
    },
    {
      "name": "T2",
      "file": "prog2.asm",
      "arrival": 2,
      "ci": 2,
      "pi": 8
    }
  ]
}
```

### Dicionário de Variáveis:
* `simulation_time`: Quantos *ticks* de relógio a simulação deve durar antes de gerar o Gráfico de Gantt.
* `name`: O nome de batismo da tarefa (Usado para o gráfico e para alertas de Deadline).
* `file`: O caminho para o arquivo de texto contendo o código Assembly da tarefa.
* `arrival`: Instante de carga (em *ticks*) indicando a primeira vez que a tarefa entra na Fila de Prontos.
* `ci`: Tempo de computação total exigido pela tarefa em um ciclo (Worst Case Execution Time).
* `pi`: O Período da tarefa. Conforme a premissa de que *di = Pi*, este valor também define o Deadline Relativo da tarefa a cada ciclo.

---

## Regras do Código Assembly

Os arquivos referenciados no campo `file` devem ser arquivos de texto contendo um código Assembly.

**Estrutura Obrigatória:**
```assembly
.code
  LOAD variavel
  ADD #5
  SYSCALL 0
.endcode
.data
  variavel 10
.enddata
```

**Modos de Endereçamento:**
* **Direto:** Passando o nome da variável. Ex: `LOAD var` (Busca na área `.data`).
* **Imediato:** Passando o símbolo `#`. Ex: `ADD #1` (Adiciona o número inteiro 1).

**Aviso sobre Encerramento:**
É fundamental que todo programa contenha a instrução `SYSCALL 0` como última instrução do bloco `.code` para avisar a CPU que o programa finalizou seu serviço para o período atual.
