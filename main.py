import json
import random
import sys
from process import Process, State
from scheduler import EDFScheduler
from executor import execute_instruction

def load_config(filepath: str):
    """
    Carrega o arquivo JSON e cria todos os Processos.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    processes = []
    for t in data["tasks"]:
        p = Process(t["name"], t["file"], t["arrival"], t["ci"], t["pi"])
        processes.append(p)
        
    return processes, data.get("simulation_time", 30)

def main():
    # Se o usuário passar o arquivo JSON por argumento de linha de comando, usamos ele.
    # Caso contrário, procuramos pelo padrão 'config.json'
    config_file = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    
    try:
        processes, sim_time = load_config(config_file)
    except FileNotFoundError:
        print(f"Erro: Arquivo {config_file} não encontrado.")
        return
        
    scheduler = EDFScheduler()
    running_process = None
    time = 0
    timeline = [] # Guardará a string com o nome de quem rodou a cada tick
    
    print(f"=== INICIANDO SIMULAÇÃO EDF POR {sim_time} TICKS ===")
    
    # O Loop Principal de Simulação (1 repetição = 1 Tick de relógio)
    while time < sim_time:
        
        # [PASSO 1] — Acordar tarefas dormindo (Ativações Periódicas)
        for p in processes:
            if p.state == State.WAITING and p.next_activation <= time:
                # PDF: O deadline coincide com o período. Logo, Deadline Absoluto = Instante de ativação + Período.
                p.absolute_deadline = p.next_activation + p.pi
                p.start_new_period()
                scheduler.add(p)
                
        # [PASSO 2] — Desbloqueio de I/O
        for p in processes:
            if p.state == State.BLOCKED and p.blocked_until == time:
                # O bloqueio acabou! A tarefa volta pra fila mantendo seu deadline atual.
                scheduler.add(p)
                
        # [PASSO 3] — Detectar Deadline Misses
        for p in processes:
            if p.state in (State.READY, State.RUNNING, State.BLOCKED):
                # Se o relógio atingiu ou passou do deadline e a tarefa ainda não foi pra WAITING
                if time == p.absolute_deadline:
                    print(f"*** DEADLINE MISS: {p.name} perdeu o prazo no instante t={time} ***")
                        
        # [PASSO 4, 5 e 6] — Decisão de Escalonamento (EDF)
        # Observa quem é o processo mais urgente que está na Fila de Prontos
        best_in_queue = scheduler.select_next()
        
        if running_process is None:
            # Se a CPU está ociosa, simplesmente pegue o melhor da fila
            if best_in_queue is not None:
                running_process = best_in_queue
                scheduler.remove(running_process)
                running_process.state = State.RUNNING
        else:
            # Se a CPU está ocupada, verifica se quem está na fila é MAIS urgente
            if best_in_queue is not None:
                if best_in_queue.absolute_deadline < running_process.absolute_deadline:
                    # Ocorreu Preempção! Tira o atual e coloca de volta na fila
                    if running_process.state == State.RUNNING:
                        scheduler.add(running_process)
                    # Coloca o novo vencedor na CPU
                    running_process = best_in_queue
                    scheduler.remove(running_process)
                    running_process.state = State.RUNNING
            
        # [PASSO 7] — Rodar o Motor! Executar UMA linha de código na CPU.
        cpu_owner = "IDLE"
        if running_process is not None:
            cpu_owner = running_process.name
            # Avisa a CPU pra rodar o PC atual
            result = execute_instruction(running_process)
            
            # Subtrai 1 unidade de tempo do budget (Ci) da tarefa, conforme regra do PDF
            running_process.remaining_ci -= 1
            
            if result == 'halt':
                # Bateu SYSCALL 0. O programa fez o que precisava. Vai dormir até o prox período.
                running_process.next_activation = running_process.absolute_deadline
                running_process.state = State.WAITING
                running_process = None
                
            elif result == 'io':
                # Bateu SYSCALL 1 ou 2. PDF manda bloquear aleatoriamente de 1 a 3 ticks.
                block_time = random.randint(1, 3)
                running_process.blocked_until = time + block_time
                running_process.state = State.BLOCKED
                running_process = None
                
            elif running_process.remaining_ci <= 0:
                # PDF Caso (i): A tarefa tem seu tempo de computação alcançado.
                # Gastou todo o 'Ci' que pediu, hora de ir dormir.
                running_process.next_activation = running_process.absolute_deadline
                running_process.state = State.WAITING
                running_process = None
                
        # [PASSO 8] — Registrar na Timeline do Gráfico de Gantt
        timeline.append(cpu_owner)
            
        time += 1 # O "Tic-Tac" do relógio mestre

    # Finalização: Impressão dos Gráficos
    print("\n=== TIMELINE DETALHADA ===")
    for t, p_name in enumerate(timeline):
        print(f"t={t:02d}: [{p_name}]")
        
    print("\n=== GRÁFICO DE GANTT ===")
    # Desenha a régua de números (ex: 012345678901234)
    regua = "      |"
    for t in range(sim_time):
        regua += str(t % 10)
    print(regua)
    
    # Desenha a linha de execução de cada processo
    for p in processes:
        linha = f"{p.name:4} |"
        for t in range(sim_time):
            if timeline[t] == p.name:
                linha += "#"
            else:
                linha += "."
        print(linha)

if __name__ == "__main__":
    main()
