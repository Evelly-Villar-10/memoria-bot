// ---------- elementos da página ----------
const painelLobby = document.getElementById("painel-lobby");
const secaoJogo = document.getElementById("jogo");
const tabuleiro = document.getElementById("tabuleiro");
const mensagem = document.getElementById("mensagem");
const placarJogador = document.getElementById("placar-jogador");
const placarBot = document.getElementById("placar-bot");
const contadorJogadas = document.getElementById("jogadas");
const botaoFim = document.getElementById("botao-fim");

const SIMBOLOS = { S: "♠", H: "♥", D: "♦", C: "♣" };
const NOMES = { 1: "A", 11: "J", 12: "Q", 13: "K" };

// ---------- o que o JavaScript lembra ----------
let partidaId = null;
let ocupado = false;     // true enquanto uma jogada está sendo enviada ou animada
let cartasEl = [];       // os 24 botões do tabuleiro, na ordem das posições
let placar = { jogador: 0, bot: 0 };

// ---------- ferramentas ----------
function pegarCookie(nome) {
  const achado = document.cookie.split("; ").find((c) => c.startsWith(nome + "="));
  return achado ? decodeURIComponent(achado.split("=")[1]) : "";
}

function esperar(ms) {
  return new Promise((resolver) => setTimeout(resolver, ms));
}

function dizer(texto) {
  mensagem.textContent = texto;
}

async function enviar(url, dados) {
  const resposta = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": pegarCookie("csrftoken"),
    },
    body: JSON.stringify(dados),
  });
  const corpo = await resposta.json().catch(() => ({}));
  if (!resposta.ok) {
    throw new Error(corpo.erro || "Algo deu errado. Recarregue a página.");
  }
  return corpo;
}

// ---------- desenhar as cartas ----------
function textoCarta(codigo) {
  const valor = parseInt(codigo.slice(0, -1), 10);
  const naipe = codigo.slice(-1);
  return (NOMES[valor] || valor) + SIMBOLOS[naipe];
}

function mostrarFace(pos, codigo) {
  const el = cartasEl[pos];
  el.textContent = textoCarta(codigo);
  el.classList.add("virada");
  el.classList.toggle("vermelha", "HD".includes(codigo.slice(-1)));
}

function esconder(pos) {
  const el = cartasEl[pos];
  el.textContent = "";
  el.classList.remove("virada", "vermelha");
}

function marcarPar(pos, dono) {
  cartasEl[pos].classList.add("par-" + dono);
  cartasEl[pos].disabled = true;
}

function atualizarPlacar() {
  placarJogador.textContent = placar.jogador;
  placarBot.textContent = placar.bot;
}

// Redesenha o tabuleiro inteiro a partir do que o servidor informou.
function desenhar(partida) {
  tabuleiro.innerHTML = "";
  cartasEl = [];

  partida.cartas.forEach((codigo, pos) => {
    const el = document.createElement("button");
    el.type = "button";
    el.className = "carta";
    el.addEventListener("click", () => clicar(pos));
    tabuleiro.appendChild(el);
    cartasEl.push(el);

    if (codigo !== null) {
      mostrarFace(pos, codigo);
      if (partida.dono[pos]) marcarPar(pos, partida.dono[pos]);
    }
  });

  placar = { ...partida.placar };
  atualizarPlacar();
  contadorJogadas.textContent = partida.jogadas;
}

// ---------- reproduzir os eventos do servidor ----------
async function animar(eventos) {
  let vezDe = "jogador";

  for (const ev of eventos) {
    if (ev.tipo === "virar") {
      vezDe = ev.quem;
      mostrarFace(ev.pos, ev.carta);
      if (ev.quem === "bot") {
        dizer("O bot virou uma carta...");
        await esperar(900);
      } else {
        await esperar(300);
      }
    } else if (ev.tipo === "erro") {
      dizer(vezDe === "jogador" ? "Não formou par. Vez do bot..." : "O bot errou. Sua vez!");
      await esperar(1000);
      ev.pos.forEach(esconder);
    } else if (ev.tipo === "par") {
      ev.pos.forEach((p) => marcarPar(p, ev.dono));
      placar[ev.dono] += 1;
      atualizarPlacar();
      dizer(ev.dono === "jogador" ? "Par! Jogue de novo." : "O bot fez um par!");
      await esperar(800);
    } else if (ev.tipo === "fim") {
      mostrarFim(ev.resultado);
    }
  }
}

function mostrarFim(resultado) {
  const textos = {
    vitoria: "🎉 Você venceu!",
    derrota: "😢 O bot venceu.",
    empate: "🤝 Empate!",
  };
  dizer(textos[resultado]);
  botaoFim.hidden = false;
}

// ---------- ações do jogador ----------
async function clicar(pos) {
  if (ocupado) return;
  if (cartasEl[pos].classList.contains("virada")) return;

  ocupado = true;
  try {
    const dados = await enviar(`/api/partidas/${partidaId}/virar/`, { posicao: pos });
    await animar(dados.eventos);
    desenhar(dados.partida);   // confere com o servidor

    if (dados.partida.status !== "fim") {
      dizer(dados.partida.viradas.length === 1
        ? "Escolha a segunda carta."
        : "Sua vez: escolha uma carta.");
    }
  } catch (erro) {
    dizer(erro.message);
  }
  ocupado = false;
}

async function iniciar(dificuldade) {
  if (ocupado) return;
  ocupado = true;
  try {
    const dados = await enviar("/api/partidas/", { dificuldade });
    partidaId = dados.partida.id;
    painelLobby.hidden = true;
    secaoJogo.hidden = false;
    botaoFim.hidden = true;
    desenhar(dados.partida);
    dizer("Sua vez: escolha uma carta.");
  } catch (erro) {
    alert(erro.message);
  }
  ocupado = false;
}

// ---------- ligar os botões ----------
document.querySelectorAll("[data-dificuldade]").forEach((botao) => {
  botao.addEventListener("click", () => iniciar(botao.dataset.dificuldade));
});

botaoFim.addEventListener("click", () => location.reload());