from assembler import parse_asm

class State:
    WAITING    = "WAITING"    # Dormindo, aguardando o próximo período Pi
    READY      = "READY"      # Na fila do Scheduler, pronto para assumir a CPU
    RUNNING    = "RUNNING"    # Sendo executado na CPU neste exato instante
    BLOCKED    = "BLOCKED"    # Travado esperando I/O (SYSCALL 1 ou 2)
    TERMINATED = "TERMINATED" # Encerrado definitivamente

class Process:
    def __init__(self, name: str, asm_file: str, arrival: int, ci: int, pi: int):
        # Configurações base do trabalho
        self.name = name
        self.arrival = arrival
        self.ci = ci  # Tempo de computação (budget por período / WCET)
        self.pi = pi  # Período (que o trabalho afirma ser igual ao deadline relativo)

        # Parsing do Assembly - É aqui que a gente invoca o tradutor que fizemos!
        self.instructions, self.init_data, self.labels = parse_asm(asm_file)

        # Estado da CPU virtual (Contexto)
        self.pc = 0
        self.acc = 0
        # Criamos um clone do dicionário original para a memória não viciar entre períodos
        self.data = dict(self.init_data)

        # Estado de Escalonamento (Variáveis do EDF)
        self.state = State.WAITING
        # O primeiro deadline é a soma do instante de chegada com o período
        self.absolute_deadline = arrival + pi
        # remaining_ci é o "cronômetro" de quantas instruções faltam neste período
        self.remaining_ci = ci
        self.blocked_until = 0
        # Guarda o relógio de quando a tarefa vai precisar acordar de novo
        self.next_activation = arrival

    def start_new_period(self):
        """
        Chamado pelo main.py quando um novo período Pi se inicia.
        Isso funciona como o "Reboot" do programa para a sua próxima execução periódica.
        """
        self.pc = 0
        self.acc = 0
        self.data = dict(self.init_data) # Restaura a memória original
        self.remaining_ci = self.ci      # Renova o budget
        self.state = State.READY         # Volta para a fila!

    def __repr__(self):
        # Isso é equivalente ao toString() do Java, útil para debugar com print()
        return f"Process({self.name}, state={self.state}, deadline={self.absolute_deadline}, rem_ci={self.remaining_ci})"

if __name__ == "__main__":
    # Teste rápido de sanidade
    import os
    with open("teste_process.asm", "w") as f:
        f.write(".code\nLOAD x\n.endcode\n.data\nx 5\n.enddata")
    
    p = Process("T1", "teste_process.asm", arrival=2, ci=3, pi=10)
    print("Processo criado:")
    print(p)
    print(f"Instruções: {p.instructions}")
    print(f"Memória Inicial: {p.data}")
    
    p.start_new_period()
    print("\nApós iniciar novo período:")
    print(p)
    
    os.remove("teste_process.asm")
