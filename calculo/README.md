# Matemática · O Cálculo que ajuda a decidir

Parte de **Differentiated Problem Solving (Modelagem Matemática)** da CitizenTech *Respiro RJ*.

## O que tem nesta pasta

| Arquivo | O que é |
|---|---|
| `calculo.py` | Código com os cálculos, as simulações e os gráficos |
| `relatorio_tecnico.pdf` | Relatório técnico: problema, modelo matemático, gráficos e interpretação |
| `grafico1_temperatura.png` | Temperatura do ar ao longo do dia (função trigonométrica ajustada aos dados) |
| `grafico2_sensacao_termica.png` | Sensação térmica do ambulante ao longo do expediente, com as faixas da Sentinela |
| `grafico3_hi_polinomio.png` | Sensação térmica em função da temperatura, para várias umidades (função polinomial) |
| `grafico4_cenarios.png` | Horas em PERIGO em cada cenário simulado (umidade e sombra) |
| `vila_militar_2025.CSV` | Dados horários do INMET de 2025 (opcional, só para `--csv` e `--anual`) |

## O modelo

- **Temperatura ao longo do dia (trigonométrica):** `T(t) = M + A · sen(2π(t − φ)/24)`, ajustada às medições reais do INMET (estação A621 Vila Militar, 19/01/2025, o dia de maior sensação térmica de 2025). R² = 0,979.
- **Sensação térmica (polinomial):** equação do Heat Index da NOAA/NWS (Rothfusz, 1990), que transforma temperatura e umidade em sensação térmica.
- **Composição:** `HI(T(t))` dá a sensação térmica hora a hora, classificada nas faixas da Sentinela do Calor: NORMAL abaixo de 32 °C, ATENÇÃO de 32 a 39 °C e PERIGO acima de 39 °C.

## Principais resultados

- No dia mais quente de 2025, o ambulante ficaria cerca de **7 horas em PERIGO** (das 9h22 às 16h20), e a pausa da Sentinela seria acionada.
- Em 2025, **48 dias** tiveram pelo menos 1 hora em PERIGO e **38 dias** acionariam a pausa, quase todos entre dezembro e março, das 11h às 15h.
- Com 70% de umidade, o PERIGO começa com apenas **31,5 °C** de temperatura do ar. Por isso a Sentinela mede temperatura **e** umidade.

## Como rodar

1. Instale as bibliotecas:

```bash
pip install numpy scipy matplotlib
```

2. Rode nesta pasta:

```bash
python calculo.py
```

O programa usa os dados reais do dia 19/01/2025, que já estão dentro do código, mostra os cálculos no terminal e salva os 4 gráficos.

Opções:

```bash
python calculo.py --hora 14.5                                      # nível de risco às 14h30
python calculo.py --csv vila_militar_2025.CSV --data 2025-01-19 --anual   # panorama do ano inteiro
```

## Fontes

- INMET – Dados Históricos Anuais 2025, estação A621 Rio de Janeiro – Vila Militar: https://portal.inmet.gov.br/dadoshistoricos
- Rothfusz, L. P. (1990). *The Heat Index "Equation"*. NOAA / National Weather Service.
- Steadman, R. G. (1979). *The assessment of sultriness*. Journal of Applied Meteorology, 18(7).
