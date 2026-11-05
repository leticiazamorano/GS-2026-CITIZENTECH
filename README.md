# Respiro RJ

Global Solution 2026.2 · CitizenTech · Engenharia de Software, 1º ano · FIAP Rio de Janeiro

## Ficha da CitizenTech

| Campo | Resposta |
|---|---|
| **Nome da CitizenTech** | Respiro RJ |
| **Cidade e bairro** | Rio de Janeiro, Vila da Penha (Zona Norte) |
| **Cidadão beneficiado** | Vendedores ambulantes que trabalham em barracas na rua |
| **Problema, em uma frase** | Ambulantes da Vila da Penha trabalham cerca de 11 horas por dia sob lonas abafadas e só percebem que o calor ficou perigoso quando já estão passando mal. |
| **Como funciona** | A Sentinela do Calor, instalada na barraca, mede a temperatura e a umidade debaixo da lona e acende uma luz verde, amarela ou vermelha conforme o risco. No calor perigoso, liga o ventilador da barraca sozinha. Depois de 1 hora seguida em perigo, pisca e dá um bipe pedindo uma pausa de 5 minutos ali mesmo, sem o ambulante largar as vendas. O site explica o risco, simula o alerta e dá dicas para se proteger. |
| **O que cada parte faz** | **Python:** analisa as leituras do dia, as horas em perigo e quando pausar. **Sentinela (Edge):** mede, alerta e liga o ventilador na barraca, sem internet. **Site:** informa, simula o alerta e dá dicas de proteção. **Matemática:** modela a curva de calor do dia. |
| **Link do repositório** | [COLAR O LINK] |
| **Indicador de impacto** | Horas por dia em calor perigoso e pausas recomendadas a tempo (no dia simulado: 4 horas em perigo, 1 alerta de pausa). |
| **ODS conectados** | **ODS 3** (Saúde e bem-estar): avisa antes que o calor cause tontura ou exaustão. **ODS 8** (Trabalho decente): protege quem trabalha na rua. **ODS 11** (Cidades sustentáveis): Pontos de Respiro tornam o espaço público mais seguro. **ODS 13** (Ação contra a mudança do clima): adaptação às ondas de calor. |

## O que tem neste repositório

| Pasta ou arquivo | O que tem |
|---|---|
| `python/` | Programa em Python que analisa as leituras de calor do dia e mostra o aviso |
| `site/` | Landing page do projeto (HTML, CSS e JavaScript) |
| `Integrantes.md` | Nome completo e RM da equipe |
| `AI.md` | Como a IA foi usada no site |

## Equipe

| Nome | RM |
|---|---|
| Julio Cezar Almeida Santos | 574498 |
| Letícia Zamorano Viegas de Freitas | 574728 |
| Alanny Vieira da Silva | 575901 |
