from process import Process, State

class EDFScheduler:
    """
    O Gerente da Fila. Implementa estritamente a política EDF (Earliest Deadline First).
    A regra do EDF é simples: Quem tiver o prazo mais próximo de estourar, roda primeiro.
    """
    def __init__(self):
        # Esta é a nossa Fila de Prontos (Ready Queue). 
        # Só entram aqui tarefas que não estão dormindo nem bloqueadas.
        self.ready_queue = []

    def add(self, process: Process):
        """
        Coloca um processo na fila de prontos.
        Seja porque ele acabou de acordar (novo período) ou sofreu preempção.
        """
        if process not in self.ready_queue:
            self.ready_queue.append(process)
        # Ao entrar na fila, garantimos que o estado dele "crachá" é READY
        process.state = State.READY

    def remove(self, process: Process):
        """
        Remove um processo da fila.
        Geralmente usado pelo main.py logo depois que o processo é escolhido para rodar.
        """
        if process in self.ready_queue:
            self.ready_queue.remove(process)

    def select_next(self) -> Process:
        """
        O coração do algoritmo EDF.
        Vasculha a fila de prontos e devolve a tarefa cujo deadline absoluto for o MENOR.
        Retorna None se a fila estiver vazia (momento IDLE).
        """
        if not self.ready_queue:
            return None
            
        # A função embutida min() do Python acha o menor item de uma lista.
        # O key=lambda ensina o min() que ele não deve comparar as tarefas em si,
        # mas sim olhar exclusivamente para a propriedade 'absolute_deadline' de cada uma.
        return min(self.ready_queue, key=lambda p: p.absolute_deadline)

if __name__ == "__main__":
    # Teste rápido
    print("Testando o Escalonador EDF...")
    scheduler = EDFScheduler()
    
    # Criando 3 tarefas fantasma só para testar a matemática da fila
    p1 = Process("T1", "dummy.asm", 0, 1, 10) # Deadline será 10
    p2 = Process("T2", "dummy.asm", 0, 1, 5)  # Deadline será 5
    p3 = Process("T3", "dummy.asm", 0, 1, 8)  # Deadline será 8
    
    scheduler.add(p1)
    scheduler.add(p2)
    scheduler.add(p3)
    
    # Pelo EDF, a T2 (deadline 5) deve ser a mais urgente, seguida de T3 e T1
    vencedor = scheduler.select_next()
    print(f"Tarefa na fila: {[p.name for p in scheduler.ready_queue]}")
    print(f"O vencedor do EDF (menor deadline) foi: {vencedor.name} (Deadline {vencedor.absolute_deadline})")
