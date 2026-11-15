"""
RESPIRO RJ - Sentinela do Calor
Global Solution FIAP 2026.2 (CitizenTech) - Differentieated Problem Solving- Modelagem Matemática

Problema: exposicao de vendedores ambulantes da Vila da Penha (Zona Norte do
Rio de Janeiro) ao calor extremo durante o horario de trabalho (7h as 18h).

Modelos usados:
  1) Temperatura ao longo do dia - funcao TRIGONOMETRICA ajustada a dados reais
     (estacao meteorologica do INMET), por minimos quadrados:
         T(t) = M + A * sen(2*pi*(t - phi) / 24)
  2) Sensacao termica - funcao POLINOMIAL do Heat Index (indice de calor)
     da NOAA / National Weather Service (regressao de Rothfusz, 1990):
         HI(T, UR) em graus F, convertido para graus C.
     Com a umidade UR fixa, HI vira um polinomio de 2o grau em T.

---------------------------------------------------------------------------
VARIAVEIS DO PROBLEMA (item 1a)
---------------------------------------------------------------------------
  t   -> hora do dia, em horas (h). Variavel independente.
         No contexto: 7 <= t <= 18 (expediente do ambulante).
  T   -> temperatura do ar, em graus Celsius (C). T = T(t).
  UR  -> umidade relativa do ar, em porcentagem (%). Parametro fixo do dia
         (media medida pelo INMET), ou variado na simulacao de cenarios.
  HI  -> indice de calor (sensacao termica), em graus Celsius (C).
         HI = HI(T, UR); no dia simulado, HI = HI(T(t)) -> funcao composta.
  M, A, phi -> parametros ajustados de T(t):
         M = temperatura media (C), A = amplitude (C),
         phi = deslocamento de fase (h).

---------------------------------------------------------------------------
JUSTIFICATIVA DA ESCOLHA DAS FUNCOES (item 1c)
---------------------------------------------------------------------------
  T(t) trigonometrica: a temperatura do ar segue um ciclo diario que se
    repete a cada 24 h (aquecimento pelo Sol de manha, pico no inicio da
    tarde, resfriamento a noite). Um fenomeno periodico, que oscila em torno
    de uma media, e descrito por uma funcao seno com periodo 24 h. Os
    parametros M, A e phi NAO sao inventados: sao obtidos por ajuste de
    minimos quadrados aos dados medidos pela estacao do INMET, e o R^2
    mostra a qualidade do ajuste.
  HI(T) polinomial: a sensacao termica nao e medida diretamente; ela e
    calculada a partir de T e UR. Usamos a equacao publicada pela NOAA /
    National Weather Service (Rothfusz, 1990), obtida por regressao
    polinomial sobre o estudo de conforto termico de Steadman (1979). Com UR
    fixa, ela vira um polinomio de 2o grau em T, o que representa bem o
    fato de que, no calor, a sensacao termica sobe cada vez mais rapido do
    que a temperatura (efeito da umidade sobre o suor).

Faixas do Sentinela do Calor (sensacao termica):
  NORMAL  < 32 C  |  ATENCAO 32 a 39 C  |  PERIGO > 39 C
  Pausa obrigatoria apos 1 h seguida em PERIGO.

Como usar:
  python calculo.py                 -> roda com os dados reais embutidos
                                       (INMET, Vila Militar, 19/01/2025)
  python calculo.py --hora 14.5     -> tambem calcula o nivel as 14h30
  python calculo.py --csv <arquivo do INMET> --data 2025-01-19 --anual
                                    -> (opcional) tambem conta os dias em
                                       PERIGO no ano inteiro
  python calculo.py --csv <arquivo do INMET> --data AAAA-MM-DD
                                    -> (opcional) analisa outro dia a partir
                                       do CSV de Dados Historicos do INMET

Dependencias: numpy, scipy, matplotlib  (pip install numpy scipy matplotlib)

Fontes:
  - INMET - Instituto Nacional de Meteorologia. Dados Historicos Anuais,
    estacao automatica A621 Rio de Janeiro - Vila Militar, 2025.
    https://portal.inmet.gov.br/dadoshistoricos
  - Rothfusz, L. P. (1990). The Heat Index "Equation". NWS Technical
    Attachment SR 90-23. NOAA / National Weather Service.
  - Steadman, R. G. (1979). The assessment of sultriness. Journal of Applied
    Meteorology, 18(7).

INTEGRANTES:
  Julio Cezar Almeida Santos ............ RM 574498
  Leticia Zamorano Viegas de Freitas .... RM 574728
  Alanny Vieira da Silva ................ RM 575901
"""

import argparse
import csv
import re
import sys

try:
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy.optimize import curve_fit
except ImportError:
    sys.exit("Instale as dependencias: pip install numpy scipy matplotlib")

# ---------------------------------------------------------------------------
# Parametros do problema
# ---------------------------------------------------------------------------
HORA_INICIO = 7.0         # inicio do expediente do ambulante (h)
HORA_FIM = 18.0           # fim do expediente (h)
LIMITE_ATENCAO = 32.0     # C
LIMITE_PERIGO = 39.0      # C
TEMPO_MAX_PERIGO = 1.0    # h seguidas em PERIGO antes da pausa
FUSO_RIO = -3             # Rio de Janeiro = UTC-3 (sem horario de verao)

# DADOS REAIS - INMET, estacao A621 Rio de Janeiro - Vila Militar,
# 19/01/2025 (dia de 2025 com maior sensacao termica medida no expediente).
# Horario local (UTC-3). Extraidos do CSV "INMET_SE_RJ_A621_RIO DE JANEIRO -
# VILA MILITAR_01-01-2025_A_31-12-2025.CSV" (colunas TEMPERATURA DO AR -
# BULBO SECO, HORARIA e UMIDADE RELATIVA DO AR, HORARIA).
DATA_PADRAO = "2025-01-19"
DADOS_HORAS = np.arange(7, 19, dtype=float)
DADOS_TEMPS = np.array([28.5, 30.2, 32.5, 34.8, 36.1, 37.2,
                        37.6, 37.6, 35.2, 35.1, 31.7, 29.6])
DADOS_UR = np.array([70, 62, 58, 55, 49, 42, 44, 48, 51, 50, 60, 64], dtype=float)


# ---------------------------------------------------------------------------
# 1. Leitura dos dados reais (CSV do INMET)
# ---------------------------------------------------------------------------
def _numero(texto):
    """Converte '31,4' ou '31.4' em float; retorna None se vazio/invalido."""
    texto = (texto or "").strip().replace(",", ".")
    try:
        valor = float(texto)
    except ValueError:
        return None
    return None if valor <= -9999 else valor  # INMET usa -9999 p/ falha


def _achar_coluna(cabecalho, palavras):
    for i, nome in enumerate(cabecalho):
        nome_up = nome.upper()
        if any(p in nome_up for p in palavras):
            return i
    return None


def ler_csv_inmet(caminho, data):
    """
    Le um CSV do INMET (Dados Historicos ou tabela da estacao) e devolve
    (horas_locais, temperaturas_C, umidades_%) do dia pedido, entre 7h e 18h.
    Aceita datas como 2025/01/15, 2025-01-15 ou 15/01/2025.
    """
    ano, mes, dia = data.split("-")
    datas_validas = {f"{ano}/{mes}/{dia}", f"{ano}-{mes}-{dia}", f"{dia}/{mes}/{ano}"}

    with open(caminho, encoding="latin-1") as f:
        linhas = list(csv.reader(f, delimiter=";"))

    # O cabecalho e a primeira linha que tem coluna de data e de hora
    idx_cab = None
    for i, linha in enumerate(linhas):
        texto = ";".join(linha).upper()
        if "DATA" in texto and "HORA" in texto:
            idx_cab = i
            break
    if idx_cab is None:
        sys.exit("Erro: nao encontrei o cabecalho (colunas Data/Hora) no CSV.")

    cab = linhas[idx_cab]
    c_data = _achar_coluna(cab, ["DATA"])
    c_hora = _achar_coluna(cab, ["HORA"])
    c_temp = _achar_coluna(cab, ["BULBO SECO", "TEMP. INS"])
    c_ur = _achar_coluna(cab, ["UMIDADE RELATIVA DO AR, HORARIA", "UMI. INS"])
    if None in (c_data, c_hora, c_temp, c_ur):
        sys.exit("Erro: nao encontrei as colunas de temperatura e umidade no CSV.")

    horas, temps, urs = [], [], []
    for linha in linhas[idx_cab + 1:]:
        if len(linha) <= max(c_data, c_hora, c_temp, c_ur):
            continue
        if linha[c_data].strip() not in datas_validas:
            continue
        digitos = re.sub(r"\D", "", linha[c_hora])[:2]  # '1300 UTC' -> '13'
        if not digitos:
            continue
        hora_local = (int(digitos) + FUSO_RIO) % 24
        t, u = _numero(linha[c_temp]), _numero(linha[c_ur])
        if t is None or u is None:
            continue
        if HORA_INICIO <= hora_local <= HORA_FIM:
            horas.append(hora_local)
            temps.append(t)
            urs.append(u)

    if len(horas) < 4:
        sys.exit(f"Erro: poucos dados validos para {data} (encontrei {len(horas)}).")

    ordem = np.argsort(horas)
    return (np.array(horas, float)[ordem], np.array(temps)[ordem],
            np.array(urs)[ordem])


def analise_anual(caminho):
    """
    (Opcional, com --csv e --anual) Aplica o indice de calor as medicoes
    horarias de TODOS os dias do arquivo do INMET e conta quantos dias o
    ambulante teria ficado em PERIGO e quantos acionariam a pausa.
    """
    with open(caminho, encoding="latin-1") as f:
        linhas = list(csv.reader(f, delimiter=";"))
    idx = next(i for i, l in enumerate(linhas)
               if "DATA" in ";".join(l).upper() and "HORA" in ";".join(l).upper())
    cab = linhas[idx]
    c_d, c_h = _achar_coluna(cab, ["DATA"]), _achar_coluna(cab, ["HORA"])
    c_t = _achar_coluna(cab, ["BULBO SECO", "TEMP. INS"])
    c_u = _achar_coluna(cab, ["UMIDADE RELATIVA DO AR, HORARIA", "UMI. INS"])
    dias = {}
    for l in linhas[idx + 1:]:
        if len(l) <= max(c_d, c_h, c_t, c_u):
            continue
        dig = re.sub(r"\D", "", l[c_h])[:2]
        if not dig:
            continue
        h = (int(dig) + FUSO_RIO) % 24
        t, u = _numero(l[c_t]), _numero(l[c_u])
        if t is not None and u is not None and HORA_INICIO <= h <= HORA_FIM:
            dias.setdefault(l[c_d].strip(), {})[h] = (t, u)

    completos = perigo = pausa = 0
    por_mes = {}
    por_hora = {h: 0 for h in range(7, 19)}
    for data, med in dias.items():
        if len(med) < 12:
            continue
        completos += 1
        acima = [heat_index_c(*med[h]) > LIMITE_PERIGO for h in range(7, 19)]
        seguidas = maior = 0
        for a in acima:
            seguidas = seguidas + 1 if a else 0
            maior = max(maior, seguidas)
        if any(acima):
            perigo += 1
            mes = re.split(r"[/-]", data)[1]
            por_mes[mes] = por_mes.get(mes, 0) + 1
        if maior >= 2:  # 2 leituras horarias seguidas -> mais de 1 h em PERIGO
            pausa += 1
        for h, a in zip(range(7, 19), acima):
            por_hora[h] += int(a)

    print("\n" + "=" * 68)
    print("ANALISE ANUAL (todas as medicoes do arquivo)")
    print("=" * 68)
    print(f"Dias com dados completos (7h-18h): {completos}")
    print(f"Dias com pelo menos 1 hora em PERIGO: {perigo}")
    print(f"Dias que acionariam a pausa (> 1 h seguida em PERIGO): {pausa}")
    print("Dias em PERIGO por mes: " +
          ", ".join(f"{m}: {n}" for m, n in sorted(por_mes.items())))
    print("Vezes em PERIGO por hora do dia: " +
          ", ".join(f"{h}h: {n}" for h, n in por_hora.items() if n))


# ---------------------------------------------------------------------------
# 2. Modelo 1 - Temperatura ao longo do dia (trigonometrica)
# ---------------------------------------------------------------------------
def temperatura(t, M, A, phi):
    """T(t) = M + A*sen(2*pi*(t - phi)/24), periodo de 24 h."""
    return M + A * np.sin(2 * np.pi * (t - phi) / 24)


def derivada_temperatura(t, M, A, phi):
    """T'(t) = A*(2*pi/24)*cos(2*pi*(t - phi)/24)  [C por hora]."""
    return A * (2 * np.pi / 24) * np.cos(2 * np.pi * (t - phi) / 24)


def ajustar_temperatura(horas, temps):
    """Ajuste por minimos quadrados (scipy.optimize.curve_fit)."""
    chute = [temps.mean(), (temps.max() - temps.min()) / 2, 8.0]
    (M, A, phi), _ = curve_fit(temperatura, horas, temps, p0=chute)
    if A < 0:                       # mesma curva escrita com A positivo
        A, phi = -A, phi + 12
    phi = phi % 24
    previsto = temperatura(horas, M, A, phi)
    ss_res = np.sum((temps - previsto) ** 2)
    ss_tot = np.sum((temps - temps.mean()) ** 2)
    r2 = 1 - ss_res / ss_tot
    return M, A, phi, r2


# ---------------------------------------------------------------------------
# 3. Modelo 2 - Sensacao termica (polinomial, NOAA/Rothfusz)
# ---------------------------------------------------------------------------
def c_para_f(c):
    return c * 9 / 5 + 32


def f_para_c(f):
    return (f - 32) * 5 / 9


def heat_index_c(temp_c, ur):
    """
    Indice de calor (sensacao termica) em C, pelo algoritmo da NOAA/NWS:
    formula simples para HI < 80 F; regressao de Rothfusz e ajustes acima disso.
    """
    T = c_para_f(np.asarray(temp_c, dtype=float))
    R = np.asarray(ur, dtype=float)

    simples = 0.5 * (T + 61.0 + (T - 68.0) * 1.2 + R * 0.094)

    rothfusz = (-42.379 + 2.04901523 * T + 10.14333127 * R
                - 0.22475541 * T * R - 0.00683783 * T ** 2
                - 0.05481717 * R ** 2 + 0.00122874 * T ** 2 * R
                + 0.00085282 * T * R ** 2 - 0.00000199 * T ** 2 * R ** 2)

    # Ajustes oficiais da NOAA
    ajuste_seco = np.where((R < 13) & (T >= 80) & (T <= 112),
                           -((13 - R) / 4) * np.sqrt(np.clip((17 - np.abs(T - 95)) / 17, 0, None)),
                           0.0)
    ajuste_umido = np.where((R > 85) & (T >= 80) & (T <= 87),
                            ((R - 85) / 10) * ((87 - T) / 5), 0.0)
    rothfusz = rothfusz + ajuste_seco + ajuste_umido

    media = (simples + T) / 2
    hi_f = np.where(media < 80, simples, rothfusz)
    return f_para_c(hi_f)


def coeficientes_hi(ur):
    """
    Com UR fixa, a regressao de Rothfusz vira HI(T) = a*T^2 + b*T + c (T em F).
    Retorna (a, b, c) - usado na analise do polinomio de 2o grau.
    """
    a = -0.00683783 + 0.00122874 * ur - 0.00000199 * ur ** 2
    b = 2.04901523 - 0.22475541 * ur + 0.00085282 * ur ** 2
    c = -42.379 + 10.14333127 * ur - 0.05481717 * ur ** 2
    return a, b, c


def classificar(hi):
    if hi > LIMITE_PERIGO:
        return "PERIGO"
    if hi >= LIMITE_ATENCAO:
        return "ATENCAO"
    return "NORMAL"


# ---------------------------------------------------------------------------
# 4. Analise matematica e simulacao
# ---------------------------------------------------------------------------
def intervalos_acima(t, valores, limite):
    """Lista de intervalos (inicio, fim) em que valores > limite."""
    acima = valores > limite
    intervalos, inicio = [], None
    for ti, a in zip(t, acima):
        if a and inicio is None:
            inicio = ti
        elif not a and inicio is not None:
            intervalos.append((inicio, ti))
            inicio = None
    if inicio is not None:
        intervalos.append((inicio, t[-1]))
    return intervalos


def hora_fmt(h):
    hh = int(h)
    mm = int(round((h - hh) * 60))
    if mm == 60:
        hh, mm = hh + 1, 0
    return f"{hh:02d}h{mm:02d}"


def simular_dia(params, ur, reducao_temp=0.0):
    """Simula a sensacao termica no expediente; reducao_temp = cenario de sombra."""
    t = np.linspace(HORA_INICIO, HORA_FIM, 1101)  # passo de ~36 s
    temp = temperatura(t, *params) - reducao_temp
    hi = heat_index_c(temp, ur)
    perigo = intervalos_acima(t, hi, LIMITE_PERIGO)
    atencao = intervalos_acima(t, hi, LIMITE_ATENCAO)
    total_perigo = sum(f - i for i, f in perigo)
    maior_perigo = max((f - i for i, f in perigo), default=0.0)
    return {"t": t, "temp": temp, "hi": hi, "perigo": perigo,
            "atencao": atencao, "total_perigo": total_perigo,
            "maior_perigo": maior_perigo,
            "pausa": maior_perigo > TEMPO_MAX_PERIGO}


def analisar(params, r2, ur):
    M, A, phi = params
    print("\n" + "=" * 68)
    print("MODELO 1 - TEMPERATURA  T(t) = M + A*sen(2*pi*(t - phi)/24)")
    print("=" * 68)
    print(f"M = {M:.2f} C (media diaria) | A = {A:.2f} C (amplitude) | phi = {phi:.2f} h")
    print(f"Qualidade do ajuste: R^2 = {r2:.4f}")

    # Dominio e imagem
    t = np.linspace(HORA_INICIO, HORA_FIM, 1101)
    temp = temperatura(t, *params)
    print("\nDominio matematico: todos os reais | Dominio no contexto: t em [7, 18] h")
    print(f"Imagem matematica: [{M - A:.2f}; {M + A:.2f}] C")
    print(f"Imagem no expediente: [{temp.min():.2f}; {temp.max():.2f}] C")

    # Crescimento / decrescimento: T'(t) = 0 em t = phi + 6 (max) e phi + 18 (min)
    t_max = (phi + 6) % 24
    t_min = (phi + 18) % 24
    print(f"\nT'(t) = 0 em t = {hora_fmt(t_max)} (maximo) e t = {hora_fmt(t_min)} (minimo)")
    if HORA_INICIO < t_max < HORA_FIM:
        print(f"Crescente em [07h00; {hora_fmt(t_max)}) e decrescente em "
              f"({hora_fmt(t_max)}; 18h00]")
    else:
        print("O maximo fica fora do expediente; ver grafico.")
    print(f"Temperatura maxima: {M + A:.2f} C as {hora_fmt(t_max)}")
    taxa = derivada_temperatura(t, *params)
    print(f"Maior taxa de aquecimento: {taxa.max():.2f} C/h as {hora_fmt(t[taxa.argmax()])}")

    print("\n" + "=" * 68)
    print(f"MODELO 2 - SENSACAO TERMICA (NOAA/Rothfusz) com UR = {ur:.0f}%")
    print("=" * 68)
    a, b, c = coeficientes_hi(ur)
    print(f"HI(T) = {a:.5f}*T^2 {b:+.5f}*T {c:+.3f}   (T e HI em F)")
    vertice_f = -b / (2 * a)
    tipo = "minimo" if a > 0 else "maximo"
    print(f"Parabola com concavidade {'para cima' if a > 0 else 'para baixo'}; "
          f"vertice ({tipo}) em T = {f_para_c(vertice_f):.1f} C")
    vertice_c = f_para_c(vertice_f)
    if a > 0:
        print(f"Intervalos: DECRESCENTE para T < {vertice_c:.1f} C e "
              f"CRESCENTE para T > {vertice_c:.1f} C")
    else:
        print(f"Intervalos: CRESCENTE para T < {vertice_c:.1f} C e "
              f"DECRESCENTE para T > {vertice_c:.1f} C")
    print("Dominio de validade (NOAA): sensacao termica a partir de ~27 C (80 F),")
    print(f"ou seja, o vertice ({vertice_c:.1f} C) fica FORA da faixa em que a formula vale.")
    print("Na faixa valida (calor), HI e CRESCENTE em T: "
          "mais temperatura -> mais sensacao termica.")
    t_temp = np.linspace(27, 42, 301)
    hi_temp = heat_index_c(t_temp, ur)
    print(f"Imagem de HI para T em [27; 42] C: [{hi_temp.min():.1f}; {hi_temp.max():.1f}] C")

    sim = simular_dia(params, ur)
    print(f"\nSensacao termica no expediente: {sim['hi'].min():.1f} a {sim['hi'].max():.1f} C")
    if sim["hi"].max() > 57:
        print("Aviso: acima de ~57 C (135 F) a regressao da NOAA extrapola; "
              "trate esses valores como 'perigo extremo', nao como valor exato.")
    for nome, ints in (("ATENCAO (>= 32 C)", sim["atencao"]), ("PERIGO (> 39 C)", sim["perigo"])):
        if ints:
            txt = ", ".join(f"{hora_fmt(i)} as {hora_fmt(f)}" for i, f in ints)
            print(f"Periodo em {nome}: {txt}")
        else:
            print(f"Periodo em {nome}: nenhum")
    print(f"Tempo total em PERIGO: {sim['total_perigo']:.2f} h "
          f"(maior periodo seguido: {sim['maior_perigo']:.2f} h)")
    print("Pausa obrigatoria acionada? " + ("SIM" if sim["pausa"] else "NAO"))
    return sim


def cenarios(params, ur_base):
    print("\n" + "=" * 68)
    print("SIMULACAO DE CENARIOS")
    print("=" * 68)
    print(f"{'Cenario':<38}{'HI max (C)':>11}{'h PERIGO':>10}{'Pausa':>8}")
    linhas = []
    for ur in (50, 60, 70, 80):
        s = simular_dia(params, ur)
        linhas.append((f"Umidade {ur}%", s))
    for red in (1.0, 2.0, 3.0):
        s = simular_dia(params, ur_base, reducao_temp=red)
        linhas.append((f"Sombra -{red:.0f} C (HIPOTETICO), UR {ur_base:.0f}%", s))
    for nome, s in linhas:
        print(f"{nome:<38}{s['hi'].max():>11.1f}{s['total_perigo']:>10.2f}"
              f"{'SIM' if s['pausa'] else 'NAO':>8}")
    print("Obs.: a reducao de temperatura pela sombra e um cenario hipotetico;\n"
          "so cite um valor real no relatorio se houver fonte.")
    return linhas


def validar(horas, temps, urs, params, ur):
    """Compara o modelo (UR fixa) com a sensacao termica calculada a partir
    da temperatura e da umidade MEDIDAS em cada hora (validacao)."""
    print("\n" + "=" * 68)
    print("VALIDACAO: sensacao termica medida x modelo")
    print("=" * 68)
    print(f"{'Hora':<6}{'T med':>7}{'UR med':>8}{'HI med':>8}{'HI mod':>8}{'Nivel (med)':>13}")
    hi_med = heat_index_c(temps, urs)
    hi_mod = heat_index_c(temperatura(horas, *params), ur)
    for h, t, u, a, b in zip(horas, temps, urs, hi_med, hi_mod):
        print(f"{int(h):02d}h{t:>9.1f}{u:>8.0f}{a:>8.1f}{b:>8.1f}{classificar(a):>13}")
    horas_perigo = int(np.sum(hi_med > LIMITE_PERIGO))
    erro = np.mean(np.abs(hi_mod - hi_med))
    print(f"Horas medidas em PERIGO: {horas_perigo} | erro medio do modelo: {erro:.1f} C")
    print("Obs.: a umidade cai a tarde, entao usar a UR media do dia tende a\n"
          "superestimar a sensacao termica no pico (limitacao do modelo).")
    return hi_med


def calcular_hora(params, ur, hora):
    temp = temperatura(hora, *params)
    hi = float(heat_index_c(temp, ur))
    print(f"\nConsulta {hora_fmt(hora)}: T = {temp:.1f} C | "
          f"sensacao = {hi:.1f} C | nivel = {classificar(hi)}")


# ---------------------------------------------------------------------------
# 5. Graficos
# ---------------------------------------------------------------------------
def faixas(ax):
    ax.axhspan(0, LIMITE_ATENCAO, color="#7fc97f", alpha=0.15, label="NORMAL (< 32 C)")
    ax.axhspan(LIMITE_ATENCAO, LIMITE_PERIGO, color="#fdc086", alpha=0.25,
               label="ATENCAO (32-39 C)")
    ax.axhspan(LIMITE_PERIGO, 80, color="#f0027f", alpha=0.12, label="PERIGO (> 39 C)")


def graficos(horas, temps, params, r2, ur, sim, linhas_cenario, sufixo, hi_med=None):
    t = np.linspace(HORA_INICIO, HORA_FIM, 500)
    M, A, phi = params

    # Grafico 1 - dados reais x funcao ajustada
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.scatter(horas, temps, color="black", zorder=3, label="Dados medidos")
    ax.plot(t, temperatura(t, *params), color="#d95f02", lw=2.2,
            label=f"T(t) = {M:.1f} + {A:.1f}·sen(2π(t − {phi:.1f})/24)   R² = {r2:.3f}")
    t_max = (phi + 6) % 24
    if HORA_INICIO <= t_max <= HORA_FIM:
        ax.plot(t_max, M + A, "v", color="#d95f02", ms=10)
        ax.annotate(f"Máximo: {M + A:.1f} °C às {hora_fmt(t_max)}", (t_max, M + A),
                    xytext=(10, 8), textcoords="offset points")
    ax.set_ylim(min(temps.min(), (temperatura(t, *params)).min()) - 1, max(temps.max(), M + A) + 1.5)
    ax.set_title("Respiro RJ – Temperatura do ar ao longo do dia (modelo trigonométrico)")
    ax.set_xlabel("Hora do dia (h)")
    ax.set_ylabel("Temperatura do ar (°C)")
    ax.set_xticks(range(7, 19))
    ax.grid(alpha=0.3)
    ax.legend(loc="lower center")
    fig.tight_layout()
    fig.savefig(f"grafico1_temperatura{sufixo}.png", dpi=150)

    # Grafico 2 - sensacao termica com faixas de risco
    fig, ax = plt.subplots(figsize=(10, 5.5))
    faixas(ax)
    ax.plot(sim["t"], sim["temp"], "--", color="gray", label="Temperatura do ar T(t)")
    ax.plot(sim["t"], sim["hi"], color="#b2182b", lw=2.4,
            label=f"Sensação térmica HI(T(t)), UR = {ur:.0f}% (modelo)")
    if hi_med is not None:
        ax.scatter(horas, hi_med, color="black", zorder=3, s=25,
                   label="Sensação térmica com T e UR medidas (INMET)")
    for i, f in sim["perigo"]:
        ax.axvspan(i, f, color="#b2182b", alpha=0.08)
        ax.annotate(f"PERIGO {hora_fmt(i)}–{hora_fmt(f)}", ((i + f) / 2, LIMITE_PERIGO + 1),
                    ha="center", fontsize=9, color="#b2182b")
    topo = max(sim["hi"].max(), hi_med.max() if hi_med is not None else 0)
    ax.set_ylim(min(sim["temp"].min(), sim["hi"].min()) - 2, topo + 5)
    ax.set_title("Respiro RJ – Sensação térmica do ambulante e níveis do Sentinela do Calor")
    ax.set_xlabel("Hora do dia (h)")
    ax.set_ylabel("Temperatura / sensação térmica (°C)")
    ax.set_xticks(range(7, 19))
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(f"grafico2_sensacao_termica{sufixo}.png", dpi=150)

    # Grafico 3 - HI como funcao da temperatura (polinomio) para varias umidades
    fig, ax = plt.subplots(figsize=(10, 5.5))
    faixas(ax)
    temp_eixo = np.linspace(27, 42, 300)
    for u in (50, 60, 70, 80):
        ax.plot(temp_eixo, heat_index_c(temp_eixo, u), lw=2, label=f"HI(T) com UR = {u}%")
    ax.plot(temp_eixo, temp_eixo, ":", color="black", label="Referência: HI = T")
    ax.set_ylim(25, 65)
    ax.set_title("Respiro RJ – Sensação térmica em função da temperatura (polinômio NOAA)")
    ax.set_xlabel("Temperatura do ar (°C)")
    ax.set_ylabel("Sensação térmica (°C)")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(f"grafico3_hi_polinomio{sufixo}.png", dpi=150)

    # Grafico 4 - cenarios
    fig, ax = plt.subplots(figsize=(10, 5.5))
    nomes = [n for n, _ in linhas_cenario]
    valores = [s["total_perigo"] for _, s in linhas_cenario]
    cores = ["#2166ac"] * 4 + ["#999999"] * (len(nomes) - 4)
    barras = ax.barh(nomes, valores, color=cores)
    ax.axvline(TEMPO_MAX_PERIGO, color="#b2182b", ls="--",
               label="Limite de 1 h seguida (pausa)")
    ax.bar_label(barras, fmt="%.2f h", padding=3)
    ax.invert_yaxis()
    ax.set_title("Respiro RJ – Horas em PERIGO por cenário simulado")
    ax.set_xlabel("Tempo total em PERIGO no expediente (h)")
    ax.set_ylabel("Cenário")
    ax.grid(axis="x", alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(f"grafico4_cenarios{sufixo}.png", dpi=150)

    print(f"\nGraficos salvos: grafico1..4{sufixo}.png")


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
def main():
    p = argparse.ArgumentParser(description="Respiro RJ - modelagem do calor")
    p.add_argument("--csv", help="(opcional) CSV de dados horarios do INMET")
    p.add_argument("--data", help="dia a analisar com --csv, formato AAAA-MM-DD")
    p.add_argument("--ur", type=float, help="umidade relativa fixa (%%); padrao = media do dia")
    p.add_argument("--anual", action="store_true",
                   help="com --csv: conta os dias em PERIGO no ano inteiro")
    p.add_argument("--hora", type=float, help="hora para consulta, ex.: 14.5 = 14h30")
    p.add_argument("--sem-janela", action="store_true", help="so salva os graficos")
    args = p.parse_args()

    if args.csv:
        if not args.data:
            sys.exit("Informe --data AAAA-MM-DD junto com --csv.")
        horas, temps, urs = ler_csv_inmet(args.csv, args.data)
        ur = args.ur if args.ur is not None else float(urs.mean())
        sufixo = ""
        print(f"Dados reais: {args.csv} | dia {args.data} | {len(horas)} medicoes")
        if args.anual:
            analise_anual(args.csv)
    else:
        horas, temps, urs = DADOS_HORAS, DADOS_TEMPS, DADOS_UR
        ur = args.ur if args.ur is not None else float(urs.mean())
        sufixo = ""
        print("Dados reais: INMET A621 Rio de Janeiro - Vila Militar | dia "
              f"{DATA_PADRAO} | {len(horas)} medicoes (embutidas no codigo)")

    print("\nHora | Temp. medida (C) | Umidade (%)")
    for h, tm, u in zip(horas, temps, urs):
        print(f"{int(h):02d}h  | {tm:16.1f} | {u:11.0f}")

    M, A, phi, r2 = ajustar_temperatura(horas, temps)
    params = (M, A, phi)
    sim = analisar(params, r2, ur)
    hi_med = validar(horas, temps, urs, params, ur)
    linhas = cenarios(params, ur)
    if args.hora is not None:
        calcular_hora(params, ur, args.hora)
    graficos(horas, temps, params, r2, ur, sim, linhas, sufixo, hi_med)

    if not args.sem_janela:
        plt.show()


if __name__ == "__main__":
    main()
