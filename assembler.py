def parse_asm(filepath: str) -> tuple[list, dict, dict]:
    """
    Lê um arquivo .asm e o converte em estruturas de dados python.
    Retorna:
      instructions: lista de tuplas (mnemonico, operando)
      data: dicionário de variáveis {nome_var: valor_int}
      labels: dicionário de labels {nome_label: indice_da_instrucao}
    """
    instructions = []
    data = {}
    labels = {}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        section = None
        for line in f:
            # Divide a linha em palavras (tokens), ignorando espaços em branco extras
            tokens = line.split()
            
            # Pula linhas vazias
            if not tokens:
                continue
                
            # Se a primeira palavra começar com #, a linha inteira é um comentário
            if tokens[0].startswith('#'):
                continue
                
            # Identificação de blocos
            if tokens[0] == '.code':
                section = 'code'
                continue
            elif tokens[0] == '.endcode':
                section = None
                continue
            elif tokens[0] == '.data':
                section = 'data'
                continue
            elif tokens[0] == '.enddata':
                section = None
                continue
                
            # Processamento de variáveis (.data)
            if section == 'data':
                # Exemplo: variavel 3
                if len(tokens) >= 2:
                    var_name = tokens[0]
                    var_val = int(tokens[1])
                    data[var_name] = var_val
                    
            # Processamento de código (.code)
            elif section == 'code':
                # Verifica se a linha possui um Label (ex: "ponto1:")
                if tokens[0].endswith(':'):
                    label_name = tokens[0][:-1]  # Remove os ':' do final
                    # O label aponta para a próxima instrução a ser inserida
                    labels[label_name] = len(instructions)
                    tokens = tokens[1:] # Remove o label da lista de palavras para ler a instrução
                    
                # Se a linha só tinha o label e o resto era vazio ou comentário, ignora
                if not tokens or tokens[0].startswith('#'):
                    continue
                    
                # A instrução é garantidamente a primeira palavra (Mnemônico)
                mnemonic = tokens[0].upper()
                # O operando é a segunda palavra (se existir)
                operand = tokens[1] if len(tokens) > 1 else None
                
                instructions.append((mnemonic, operand))

    return instructions, data, labels

if __name__ == "__main__":
    # Teste rápido se o arquivo for executado diretamente
    print("Testando assembler.py com um arquivo falso...")
    with open("teste_temp.asm", "w") as temp:
        temp.write(""".code
    LOAD variable
    ponto1: SUB #1         # Subtrai do acc um valor constante (i.e. 1)
    SYSCALL 1
    BRPOS ponto1
    SYSCALL 0
.endcode
.data
    variable 3
.enddata""")
    
    inst, dt, lbl = parse_asm("teste_temp.asm")
    print(f"Instruções: {inst}")
    print(f"Variáveis: {dt}")
    print(f"Labels: {lbl}")
    
    import os
    os.remove("teste_temp.asm")
