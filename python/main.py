# ============================================================
#  GS CitizenTech · Computational Thinking with Python
#  Atividade: O Cérebro da CitizenTech
#
#  Equipe: Julio Cezar Almeida Santos - RM 574498 Letícia Zamorano Viegas de Freitas - RM 574728; Alanny Vieira da Silva - RM 575901
#  CitizenTech: Respiro RJ
#  Problema, em uma frase: Ambulantes da Vila da Penha trabalham
#  cerca de 11 horas por dia sob lonas abafadas e só percebem que
#  o calor ficou perigoso quando já estão passando mal.
# ============================================================
#
#
#  Partes do programa:
#    PARTE 1 - Dados            (12 leituras, das 7h às 18h)
#    PARTE 2 - Faixas           (os mesmos limites do circuito de Edge)
#    PARTE 3 - Classificação    (cada leitura recebe a sua própria faixa)
#    PARTE 4 - Menu             (loop que só termina no Sair)
#    PARTE 5 - Opções           (classificar, resumir, consultar, testar)
# ============================================================


# ------------------------------------------------------------
# PARTE 1 - DADOS
# A sensação térmica é medida debaixo da lona da barraca, uma leitura a cada hora, das 7h às 18h.
# Todos os dados são simulados pela equipe.
# ------------------------------------------------------------

nome_local = "Vila da Penha"
grandeza = "Sensação Térmica"
unidade = "°C"
hora_inicial= 7


leituras = [27, 29, 31, 34, 37, 41, 43, 42, 40, 37, 34, 31]


# ------------------------------------------------------------
# PARTE 2 - FAIXAS DE DECISÃO
# ------------------------------------------------------------

limite_atencao = 32.0   # 32 °C a 39 °C : ATENÇÃO
limite_perigo = 39.0    # acima de 39 °C: PERIGO
limite_minimo = 0       # abaixo de 0 °C: LEITURA INVÁLIDA
limite_maximo = 60      # acima de 60 °C: LEITURA INVÁLIDA
limite_pausa = 1        # horas seguidas em PERIGO até solicitar a pausa 

# AVISOS 

aviso_normal = "Calor sob controle. Mantenha a água por perto."
aviso_atencao = "Calor forte. Beba água com frequência."
aviso_perigo = "Calor perigoso! Faça uma pausa na sombra e beba água. Se sentir tontura, peça ajuda."
aviso_pausa = "Você está há 1 hora em calor perigoso. Pare agora e procure um Ponto de Respiro."
aviso_invalida = "Sensor sem leitura. Confira o aparelho."


# ------------------------------------------------------------
# PARTE 3 - CLASSIFICAÇÃO
# ------------------------------------------------------------

faixas = []
for valor in leituras:
    if valor < limite_minimo or valor > limite_maximo:
        faixa = "LEITURA INVÁLIDA"
    elif valor > limite_perigo:
        faixa = "PERIGO"
    elif valor >= limite_atencao:
        faixa = "ATENÇÃO"
    else:
        faixa = "NORMAL"
    faixas.append(faixa)

# ------------------------------------------------------------
# PARTE 4 - MENU
# ------------------------------------------------------------

print("================================")
print(f"  Respiro RJ · {nome_local}")     
print("================================")

opcao = ""
while opcao != "0":
    print()
    print("1 - Ver todas as leituras classificadas")
    print("2 - Resumo do dia")
    print("3 - Consultar uma leitura")
    print("4 - Testar uma sensação térmica")
    print("0 - Sair")
    opcao = input("Escolha uma opção: ").strip()

    # --------------------------------------------------------
    # PARTE 5 - OPÇÕES
    # --------------------------------------------------------

    if opcao == "1":
        print()
        print(f"{grandeza} debaixo da lona em  {nome_local}:")
        sequencia=0
        for posicao in range(len(leituras)):
            hora = hora_inicial + posicao 
            valor = leituras[posicao]
            faixa = faixas[posicao]

            if faixa == "PERIGO":
                sequencia= sequencia +1
            else:
                sequencia = 0

            if sequencia == limite_pausa:
                print(f"  {hora:02d}h: {valor} {unidade} -> {faixa} -> HORA DA PAUSA")
            else:
               print(f"  {hora:02d}h: {valor} {unidade} -> {faixa}")

    elif opcao == "2":
        soma = 0
        qtd_validas = 0
        maior = -1
        hora_maior = 0
        qtd_perigo = 0
        qtd_atencao = 0
        qtd_invalidas = 0
        sequencia = 0
        maior_sequencia = 0
        inicio_sequencia = 0
        inicio_maior_sequencia = 0
        qtd_pausas = 0
        
        for posicao in range(len(leituras)):
            hora = hora_inicial + posicao
            valor = leituras[posicao]
            faixa = faixas[posicao]

            if faixa == "LEITURA INVÁLIDA":
                qtd_invalidas = qtd_invalidas + 1
            else:
                soma = soma + valor
                qtd_validas = qtd_validas + 1
                if valor > maior:
                    maior = valor
                    hora_maior = hora

            if faixa == "ATENÇÃO":
                qtd_atencao = qtd_atencao + 1

            if faixa == "PERIGO":
                qtd_perigo = qtd_perigo + 1
                if sequencia == 0:
                    inicio_sequencia = hora
                sequencia = sequencia + 1
                if sequencia == limite_pausa:
                    qtd_pausas = qtd_pausas + 1
                if sequencia > maior_sequencia:
                    maior_sequencia = sequencia
                    inicio_maior_sequencia = inicio_sequencia
            else:
                sequencia = 0

        print()
        if qtd_validas == 0:
            print("Nenhuma leitura válida hoje.")
            print(f"AVISO: {aviso_invalida}")
        else:
            media = soma / qtd_validas
            percentual_perigo = qtd_perigo / qtd_validas * 100

            print(f"Média do dia: {media:.1f} {unidade}")
            print(f"Maior valor: {maior} {unidade} às {hora_maior}h")
            print(f"Horas em ATENÇÃO: {qtd_atencao}")
            print(f"Horas em PERIGO: {qtd_perigo} de {qtd_validas} ({percentual_perigo:.0f}%)")
            if maior_sequencia > 0:
                fim_maior_sequencia = inicio_maior_sequencia + maior_sequencia - 1
                print(f"Maior sequência em PERIGO: {maior_sequencia} hora(s) seguidas, "
                      f"das {inicio_maior_sequencia}h às {fim_maior_sequencia}h")
            else:
                print("Maior sequência em PERIGO: nenhuma")
            print(f"Alertas de pausa: {qtd_pausas}")
            if qtd_invalidas > 0:
                print(f"Leituras inválidas (fora das contas): {qtd_invalidas}")

            # O aviso final usa o mesmo texto da página e da Sentinela.
            if qtd_pausas > 0:
                print(f"AVISO: {aviso_pausa}")
            elif qtd_perigo > 0:
                print(f"AVISO: {aviso_perigo}")
            elif media >= limite_atencao:
                print(f"AVISO: {aviso_atencao}")
            else:
                print(f"AVISO: {aviso_normal}")

    elif opcao == "3":
        hora_final = hora_inicial + len(leituras) - 1
        texto = input(f"Horário da leitura ({hora_inicial} a {hora_final}): ").strip()
        while not texto.isdigit() or int(texto) < hora_inicial or int(texto) > hora_final:
            print("Horário inválido. Digite só a hora, por exemplo 13.")
            texto = input(f"Horário da leitura ({hora_inicial} a {hora_final}): ").strip()

        posicao = int(texto) - hora_inicial
        valor = leituras[posicao]
        faixa = faixas[posicao]

        print(f"{texto}h: {valor} {unidade} -> {faixa}")
        if faixa == "LEITURA INVÁLIDA":
            print(f"AVISO: {aviso_invalida}")
        elif faixa == "PERIGO":
            print(f"AVISO: {aviso_perigo}")
        elif faixa == "ATENÇÃO":
            print(f"AVISO: {aviso_atencao}")
        else:
            print(f"AVISO: {aviso_normal}")

    elif opcao == "4":
        texto = input(f"Digite a sensação térmica em {unidade} (ex.: 35 ou 35,5): ").strip()
        texto = texto.replace(",", ".")
        while not texto.replace(".", "", 1).isdigit():
            print("Valor inválido. Digite só o número, por exemplo 35 ou 35,5.")
            texto = input(f"Digite a sensação térmica em {unidade}: ").strip()
            texto = texto.replace(",", ".")

        valor = float(texto)
        if valor < limite_minimo or valor > limite_maximo:
            print(f"{valor} {unidade} -> LEITURA INVÁLIDA")
            print(f"AVISO: {aviso_invalida}")
        elif valor > limite_perigo:
            print(f"{valor} {unidade} -> PERIGO")
            print(f"AVISO: {aviso_perigo}")
        elif valor >= limite_atencao:
            print(f"{valor} {unidade} -> ATENÇÃO")
            print(f"AVISO: {aviso_atencao}")
        else:
            print(f"{valor} {unidade} -> NORMAL")
            print(f"AVISO: {aviso_normal}")

    elif opcao == "0":
        print("Até logo! Respiro RJ: cuide de você no calor.")

    else:
        print("Opção inválida. Escolha um número do menu.")
