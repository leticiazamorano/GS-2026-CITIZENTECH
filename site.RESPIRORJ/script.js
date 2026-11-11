

/* =========================================
   RESPIRA RJ - MONITORAMENTO TÉRMICO
   Global Solution 2026.2
========================================= */


const controleTemperatura = document.getElementById("controle-temperatura");
const temperaturaValor = document.getElementById("temperatura-valor");
const temperaturaSelecionada = document.getElementById("temperatura-selecionada");
const controleUmidade = document.getElementById("controle-umidade");
const umidadeValor = document.getElementById("umidade-valor");
const umidadeSelecionada = document.getElementById("umidade-selecionada");
const riscoValor = document.getElementById("risco-valor");
const riscoDescricao = document.getElementById("risco-descricao");
const alertaTitulo = document.getElementById("alerta-titulo");
const alertaMensagem = document.getElementById("alerta-mensagem");
const caixaAlerta = document.querySelector(".dashboard__alerta");
const botaoResfriamento = document.getElementById("botao-resfriamento");
const resfriamentoStatus = document.getElementById("resfriamento-status");
const caixaResfriamento = document.querySelector(".dashboard__resfriamento");
const sensacaoValor = document.getElementById("sensacao-valor");
const contadorPerigo = document.getElementById("contador-perigo");

const LIMITE_ATENCAO = 32;
const LIMITE_PERIGO = 39;
const INTERVALO_LEITURA = 2000;
const TEMPO_ATE_PAUSA = 20000;
const DURACAO_PAUSA = 15000;

let ultimasLeituras = [];
let estadoAtual = "NORMAL";
let ventilacaoLigada = false;
let inicioPerigo = null;
let inicioPausa = null;

function calcularSensacaoTermica(temperatura, umidade) {
    const t = temperatura * 1.8 + 32;
    let indice = 0.5 * (t + 61 + (t - 68) * 1.2 + umidade * 0.094);
    indice = (indice + t) / 2;

    if (indice >= 80) {
        indice = -42.379
            + 2.04901523 * t
            + 10.14333127 * umidade
            - 0.22475541 * t * umidade
            - 0.00683783 * t * t
            - 0.05481717 * umidade * umidade
            + 0.00122874 * t * t * umidade
            + 0.00085282 * t * umidade * umidade
            - 0.00000199 * t * t * umidade * umidade;

        if (umidade < 13 && t >= 80 && t <= 112) {
            indice -= ((13 - umidade) / 4) * Math.sqrt((17 - Math.abs(t - 95)) / 17);
        }
        if (umidade > 85 && t >= 80 && t <= 87) {
            indice += ((umidade - 85) / 10) * ((87 - t) / 5);
        }
    }
    return (indice - 32) / 1.8;
}

function calcularMedia(valor) {
    ultimasLeituras.push(valor);
    if (ultimasLeituras.length > 3) {
        ultimasLeituras.shift();
    }
    let soma = 0;
    for (let numero of ultimasLeituras) {
        soma += numero;
    }
    return soma / ultimasLeituras.length;
}

function classificarRisco(sensacao) {
    if (sensacao > LIMITE_PERIGO) {
        return "PERIGO";
    }
    if (sensacao >= LIMITE_ATENCAO) {
        return "ATENCAO";
    }
    return "NORMAL";
}

function atualizarAlerta() {
    if (estadoAtual === "NORMAL") {
        riscoValor.textContent = "Normal";
        riscoDescricao.textContent = "Calor sob controle";
        riscoValor.style.color = "#238B61";
        alertaTitulo.textContent = "💚 Temperatura normal";
        alertaMensagem.textContent = "Condição simulada normal. Mantenha a água por perto.";
        caixaAlerta.className = "dashboard__alerta normal";
    } else if (estadoAtual === "ATENCAO") {
        riscoValor.textContent = "Atenção";
        riscoDescricao.textContent = "Calor forte";
        riscoValor.style.color = "#D49A00";
        alertaTitulo.textContent = "⚠️ Atenção ao calor";
        alertaMensagem.textContent = "Calor forte na simulação. Beba água com frequência.";
        caixaAlerta.className = "dashboard__alerta atencao";
    } else if (estadoAtual === "PERIGO") {
        riscoValor.textContent = "Perigo";
        riscoDescricao.textContent = "Calor perigoso";
        riscoValor.style.color = "#D71920";
        alertaTitulo.textContent = "🚨 Perigo: calor intenso";
        alertaMensagem.textContent = "Calor perigoso na simulação! Ventilação simulada ligada. Beba água.";
        caixaAlerta.className = "dashboard__alerta alerta-elevado";
    } else if (estadoAtual === "PAUSA") {
        riscoValor.textContent = "Pausa";
        riscoDescricao.textContent = "Pausa de segurança simulada";
        riscoValor.style.color = "#D71920";
        alertaTitulo.textContent = "🚨 Hora de fazer uma pausa";
        alertaMensagem.textContent = "Simulação de pausa de segurança. Procure sombra, descanse e beba água.";
        caixaAlerta.className = "dashboard__alerta alerta-elevado";
    } else {
        riscoValor.textContent = "Leitura inválida";
        riscoDescricao.textContent = "Verifique os controles";
        riscoValor.style.color = "#D49A00";
        alertaTitulo.textContent = "⚠️ Falha na leitura";
        alertaMensagem.textContent = "Valor simulado inválido. Verifique os controles.";
        caixaAlerta.className = "dashboard__alerta atencao";
    }
}

function atualizarResfriamento() {
    if (ventilacaoLigada) {
        resfriamentoStatus.textContent = "Ventilação simulada ativada automaticamente";
        botaoResfriamento.textContent = "Simulação de ventilação ligada";
        botaoResfriamento.setAttribute("aria-pressed", "true");
        caixaResfriamento.classList.add("ativo");
    } else {
        resfriamentoStatus.textContent = "Aguardando condição de perigo";
        botaoResfriamento.textContent = "Simulação de ventilação desligada";
        botaoResfriamento.setAttribute("aria-pressed", "false");
        caixaResfriamento.classList.remove("ativo");
    }
}

botaoResfriamento.disabled = true;

function atualizarMonitoramento() {
    const temperatura = Number(controleTemperatura.value);
    const umidade = Number(controleUmidade.value);
    const agora = Date.now();

    temperaturaValor.textContent = temperatura + "°C";
    temperaturaSelecionada.textContent = temperatura + "°C";
    umidadeValor.textContent = umidade + "%";
    umidadeSelecionada.textContent = umidade + "%";

    if (!Number.isFinite(temperatura) || !Number.isFinite(umidade) ||
        temperatura < 0 || temperatura > 60 || umidade < 0 || umidade > 100) {
        estadoAtual = "INVALIDA";
        ventilacaoLigada = false;
        inicioPerigo = null;
        inicioPausa = null;
        ultimasLeituras = [];
        sensacaoValor.textContent = "--°C";
        atualizarAlerta();
        atualizarResfriamento();
        return;
    }

    const sensacao = calcularSensacaoTermica(temperatura, umidade);
    const sensacaoMedia = calcularMedia(sensacao);
    sensacaoValor.textContent = sensacaoMedia.toFixed(1) + "°C";
    const classificacao = classificarRisco(sensacaoMedia);
    ventilacaoLigada = classificacao === "PERIGO";

    if (estadoAtual === "PAUSA") {
        if (agora - inicioPausa < DURACAO_PAUSA) {
            atualizarAlerta();
            atualizarResfriamento();
            return;
        }
        estadoAtual = classificacao;
        inicioPerigo = classificacao === "PERIGO" ? agora : null;
        inicioPausa = null;
        atualizarAlerta();
        atualizarResfriamento();
        return;
    }

    if (classificacao === "PERIGO") {
        if (inicioPerigo === null) {
            inicioPerigo = agora;
        }
        if (agora - inicioPerigo >= TEMPO_ATE_PAUSA) {
            estadoAtual = "PAUSA";
            inicioPausa = agora;
            inicioPerigo = null;
        } else {
            estadoAtual = "PERIGO";
        }
    } else {
        inicioPerigo = null;
        estadoAtual = classificacao;
    }

    atualizarAlerta();
    atualizarResfriamento();
}

function atualizarContador() {
    const agora = Date.now();

    if (estadoAtual === "PAUSA" && inicioPausa !== null) {
        const restante = Math.max(0, Math.ceil((DURACAO_PAUSA - (agora - inicioPausa)) / 1000));
        contadorPerigo.textContent = "Pausa simulada: faltam " + restante + " segundos";
    } else if (estadoAtual === "PERIGO" && inicioPerigo !== null) {
        const decorrido = Math.floor((agora - inicioPerigo) / 1000);
        contadorPerigo.textContent = "Em perigo simulado há " + decorrido + " segundos";
    } else if (estadoAtual === "INVALIDA") {
        contadorPerigo.textContent = "Leitura simulada inválida. Verifique os controles.";
    } else {
        contadorPerigo.textContent = "Aguardando condição de perigo";
    }
}

controleTemperatura.addEventListener("input", function() {
    temperaturaSelecionada.textContent = controleTemperatura.value + "°C";
});

controleUmidade.addEventListener("input", function() {
    umidadeSelecionada.textContent = controleUmidade.value + "%";
});

const horaInicio = document.getElementById("hora-inicio");
const horaFim = document.getElementById("hora-fim");
const botaoAnalisar = document.getElementById("botao-analisar");
const resultadoDia = document.getElementById("resultado-dia");

const temperaturasDia = {
    7: 27, 8: 29, 9: 31, 10: 34,
    11: 37, 12: 41, 13: 43, 14: 42,
    15: 40, 16: 37, 17: 34, 18: 31
};

function analisarMeuDia() {
    const inicio = Number(horaInicio.value);
    const fim = Number(horaFim.value);

    if (inicio >= fim) {
        resultadoDia.innerHTML = "<h3>Horário inválido</h3><p>O horário de término deve ser maior que o de início.</p>";
        return;
    }

    let horasPerigo = 0;
    for (let hora = inicio; hora < fim; hora++) {
        if (temperaturasDia[hora] > 39) {
            horasPerigo++;
        }
    }

    if (horasPerigo > 0) {
        resultadoDia.innerHTML = `
            <h3>☀️ ${horasPerigo} hora(s) em perigo</h3>
            <p>Durante seu expediente, ${horasPerigo} hora(s) apresentam temperaturas simuladas acima de 39°C. Procure sombra, beba água e faça pausas regulares.</p>
        `;
    } else {
        resultadoDia.innerHTML = `
            <h3>💚 Nenhuma hora em perigo</h3>
            <p>Nos horários selecionados, os dados simulados não apresentam temperaturas acima de 39°C. Continue se hidratando e se protegendo do calor.</p>
        `;
    }
}

botaoAnalisar.addEventListener("click", analisarMeuDia);

const botaoTema = document.getElementById("alternar-tema");
botaoTema.addEventListener("click", function() {
    document.body.classList.toggle("tema-escuro");
    if (document.body.classList.contains("tema-escuro")) {
        botaoTema.textContent = "☀️";
    } else {
        botaoTema.textContent = "🌙";
    }
});

atualizarMonitoramento();
atualizarContador();
setInterval(atualizarMonitoramento, INTERVALO_LEITURA);
setInterval(atualizarContador, 1000);
