# 🧠 Memória Bot

O **Memória Bot** é um jogo da memória desenvolvido com Django, JavaScript, HTML e CSS, no qual o jogador compete contra um bot. O projeto combina lógica de jogo, comunicação entre frontend e backend e testes automatizados.

🌐 **Jogue online:** https://memoria-bot.onrender.com

## ✨ Funcionalidades

- Tabuleiro interativo de jogo da memória.
- Partidas contra um bot.
- Diferentes níveis de dificuldade.
- Contabilização dos pares encontrados pelo jogador e pelo bot.
- Registro do estado da partida e das jogadas.
- Comunicação entre o frontend e o backend por meio de endpoints.
- Animações dos eventos do bot.
- Testes automatizados para verificar o funcionamento da lógica do jogo.

## 🛠️ Tecnologias utilizadas

- **Python** — linguagem principal do backend.
- **Django** — framework web utilizado para estruturar a aplicação.
- **JavaScript** — interatividade do tabuleiro e comunicação com o backend.
- **HTML5** — estrutura das páginas.
- **CSS3** — estilização e animações.
- **PostgreSQL** — banco de dados da aplicação em produção.
- **SQLite** — alternativa de banco de dados local, conforme a configuração do ambiente.
- **Git e GitHub** — versionamento e armazenamento do código.
- **Render** — hospedagem da aplicação.

## ⚙️ Como executar o projeto localmente

### 1. Pré-requisitos

Antes de começar, tenha instalado:

- Python 3.
- Git.
- pip.

### 2. Clone o repositório

```bash
git clone https://github.com/Evelly-Villar-10/memoria-bot.git
cd memoria-bot
```

### 3. Crie um ambiente virtual

No Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Execute as migrações

```bash
python manage.py migrate
```

### 6. Inicie o servidor

```bash
python manage.py runserver
```

Acesse no navegador:

http://127.0.0.1:8000/

## 🧪 Executando os testes

Para executar os testes automatizados do projeto, utilize:

```bash
python manage.py test
```

O Django executará os testes encontrados nos aplicativos configurados no projeto.

## 🚀 Publicação

A aplicação está hospedada no Render:

https://memoria-bot.onrender.com

O projeto utiliza um script `build.sh` para instalar as dependências, coletar os arquivos estáticos e executar as migrações do banco de dados durante a preparação da publicação.

## 📚 Objetivo do projeto

O projeto foi desenvolvido para praticar conceitos de desenvolvimento web, incluindo:

- Organização de uma aplicação com Django.
- Criação de views e URLs.
- Comunicação entre frontend e backend.
- Manipulação de dados e estado de uma partida.
- Desenvolvimento de lógica para um bot.
- Testes automatizados.
- Versionamento com Git e publicação de uma aplicação web.

---

Desenvolvido como projeto de aprendizado em programação e desenvolvimento web.
