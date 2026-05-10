from process import Process

def resolve(operand: str, data: dict) -> int:
    """
    Função auxiliar para descobrir o valor de um operando.
    Se ele começar com '#', é o próprio número (Modo Imediato). Ex: '#5' -> 5.
    Se não, é o nome de uma variável (Modo Direto). Vai buscar na memória. Ex: 'var' -> data['var'].
    """
    if operand.startswith('#'):
        return int(operand[1:])  # Ignora o '#' e converte o resto pra inteiro
    
    # Se a variável não existir na memória, retorna 0 por segurança
    return data.get(operand, 0)

def execute_instruction(process: Process) -> str:
    """
    O "Motor" da CPU. 
    Lê a instrução atual baseada no PC (Program Counter) do processo,
    executa a matemática, atualiza a memória e avança o PC.
    
    Retornos possíveis para o main.py:
    - 'ok'   : Executou de boa, pode continuar.
    - 'halt' : Bateu no SYSCALL 0 (Fim do programa).
    - 'io'   : Bateu no SYSCALL 1 ou 2 (Precisa bloquear de 1 a 3 ticks).
    """
    # Proteção: Se por acaso o PC passar do limite de linhas do código
    if process.pc >= len(process.instructions):
        return 'halt'

    # Busca a instrução exata usando o PC como índice
    inst = process.instructions[process.pc]
    mnemonic = inst[0]
    operand = inst[1]

    # Avançamos o PC para a próxima linha por padrão.
    # Se for uma instrução de salto (BRANY, etc), ela vai sobrescrever esse valor abaixo.
    process.pc += 1

    if mnemonic == "ADD":
        process.acc += resolve(operand, process.data)
        
    elif mnemonic == "SUB":
        process.acc -= resolve(operand, process.data)
        
    elif mnemonic == "MULT":
        process.acc *= resolve(operand, process.data)
        
    elif mnemonic == "DIV":
        val = resolve(operand, process.data)
        if val != 0:
            process.acc = process.acc // val # Divisão inteira no Python
            
    elif mnemonic == "LOAD":
        process.acc = resolve(operand, process.data)
        
    elif mnemonic == "STORE":
        # STORE obrigatoriamente salva em uma variável, então o operando é direto
        process.data[operand] = process.acc
        
    elif mnemonic == "BRANY":
        process.pc = process.labels[operand]
        
    elif mnemonic == "BRPOS":
        if process.acc > 0:
            process.pc = process.labels[operand]
            
    elif mnemonic == "BRZERO":
        if process.acc == 0:
            process.pc = process.labels[operand]
            
    elif mnemonic == "BRNEG":
        if process.acc < 0:
            process.pc = process.labels[operand]
            
    elif mnemonic == "SYSCALL":
        syscall_code = int(operand) if operand else 0
        
        if syscall_code == 0:
            # Encerramento do programa
            return 'halt'
            
        elif syscall_code == 1:
            # Impressão na tela
            print(f"[{process.name} - OUTPUT]: {process.acc}")
            return 'io'
            
        elif syscall_code == 2:
            # Leitura do teclado. O input trava a execução do Python até o usuário digitar.
            user_input = input(f"[{process.name} - INPUT] Digite um número inteiro: ")
            try:
                process.acc = int(user_input)
            except ValueError:
                # Tratamento de erro caso o usuário digite texto
                process.acc = 0 
            return 'io'
            
    return 'ok'

if __name__ == "__main__":
    # Pequeno teste isolado para a ALU
    from process import Process
    from assembler import parse_asm
    import os
    
    with open("teste_exec.asm", "w") as f:
        f.write(".code\nLOAD #10\nSUB #2\nSTORE x\nSYSCALL 1\nSYSCALL 0\n.endcode\n.data\nx 0\n.enddata")
        
    p = Process("T_TESTE", "teste_exec.asm", 0, 10, 10)
    
    print("Estado inicial:", p.acc, p.data)
    
    # Vamos rodar até encontrar o 'halt'
    while True:
        status = execute_instruction(p)
        if status == 'halt':
            print("Programa terminou (halt).")
            break
        elif status == 'io':
            print("Operação de I/O executada!")
            
    print("Estado Final (x deve ser 8):", p.acc, p.data)
    os.remove("teste_exec.asm")
