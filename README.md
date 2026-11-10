# EFICON - Sistema de Gestão Contábil Simplificado

MVP (Produto Mínimo Viável) desenvolvido para a EFICON Contabilidade, uma empresa familiar com cerca de 70 anos de atuação. O sistema foi criado para solucionar gargalos operacionais na rotina contábil, com foco no controle de obrigações acessórias e na centralização de documentos, reduzindo o risco de multas e sobrecarga de trabalho.

## Funcionalidades Principais

- Autenticação Segura: Login com proteção de rotas (Flask-Login) e senhas criptografadas (hash).
- Painel de Obrigações: Visualização de obrigações com alertas visuais (Atrasadas, Vencem em Breve, Pendentes, Concluídas) e atualização de status em tempo real (AJAX).
- Gestão de Clientes: Cadastro e importação em massa de clientes via arquivo .txt, incluindo dados societários (Sócio, CPF, Inscrição Estadual, ICMS).
- Controle de Obrigações: Cadastro de obrigações acessórias com prazos e classificação automática.
- Centralização de Documentos: Upload e listagem de arquivos anexados aos clientes.
- Qualidade e Integração Contínua: Testes automatizados (Pytest) com 83% de cobertura e pipeline de Integração Contínua (GitHub Actions).

## Acesso à Aplicação

A aplicação está publicada e acessível publicamente no Render:
Link: https://eficom-mvp-contabil.onrender.com

Nota: O plano gratuito do Render coloca a aplicação em modo de espera após 15 minutos de inatividade. Caso o primeiro acesso demore, aguarde cerca de 30 segundos para o servidor inicializar.

## Tecnologias Utilizadas

- Linguagem: Python 3.12
- Framework Web: Flask
- Banco de Dados: SQLite (via SQLAlchemy)
- Autenticação: Flask-Login e Werkzeug Security
- Frontend: HTML5, CSS3, JavaScript (Fetch API)
- Testes: Pytest e Pytest-Cov
- CI/CD: GitHub Actions
- Deploy: Render

## Como Executar Localmente

1. Clone o repositório:
   git clone https://github.com/Jessica-Storgatto/eficom-mvp-contabil.git
   cd eficom-mvp-contabil

2. Crie e ative um ambiente virtual:
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate

3. Instale as dependências:
   pip install -r requirements.txt

4. Execute a aplicação:
   python app.py

5. Acesse no navegador: http://127.0.0.1:5000

## Credenciais de Acesso Padrão (MVP)

- E-mail: gestora@eficom.com.br
- Senha: 123456

## Como Executar os Testes

Para rodar os testes unitários e de integração, utilize:
python -m pytest --cov=. --cov-report=term-missing

## ARQUITETURA E ESTRUTURA DO PROJETO
```
eficom-mvp-contabil/
├── app.py                      # Ponto de entrada: inicializa Flask, configura SECRET_KEY, Banco e LoginManager
├── models.py                   # Camada de Persistência: define as tabelas (Cliente, Documento, Obrigacao, Usuario) via SQLAlchemy
├── regras.py                   # Camada de Negócio: funções puras de cálculo de prazo e classificação de status
├── routes.py                   # Camada de Controle: define todas as rotas (URLs), manipula requisições HTTP e chama as regras
├── requirements.txt            # Lista de dependências Python (Flask, SQLAlchemy, Pytest, Gunicorn)
├── Procfile                    # Arquivo de configuração de deploy para o Render (comando do Gunicorn)
├── README.md                   # Documentação do projeto, instruções de uso e arquitetura
├── .gitignore                  # Lista de arquivos que não devem ser enviados ao GitHub (ex: venv, .db)
├── .coverage                   # Arquivo gerado automaticamente pelo Pytest-Cov
│
├── instance/                   # Pasta gerada automaticamente pelo Flask
│   └── eficom.db               # Banco de dados SQLite (onde os dados reais são armazenados)
│
├── uploads/                    # Pasta gerada automaticamente pelo sistema
│   └── (arquivos enviados)     # Armazena fisicamente os documentos anexados pela gestora
│
├── static/                     # Arquivos estáticos (Frontend)
│   └── style.css               # Folha de estilos global (design, cores e responsividade)
│
├── templates/                  # Camada de Apresentação (HTML + Jinja2)
│   ├── base.html               # Layout mestre (cabeçalho, menu de navegação, fontes Montserrat)
│   ├── login.html              # Tela 1: Autenticação de usuário
│   ├── painel.html             # Tela 2: Painel de obrigações (cartões de resumo e tabela interativa com JS)
│   ├── cadastro_obrigacao.html # Tela de formulário para nova obrigação
│   ├── clientes.html           # Tela de listagem de clientes e exclusão
│   ├── importar_clientes.html  # Tela de upload de arquivo .txt para importação em massa
│   ├── upload_documento.html   # Tela de envio de arquivos
│   └── documentos_enviados.html# Tela de listagem e download dos documentos recebidos
│
├── tests/                      # Camada de Qualidade (Testes Automatizados)
│   ├── test_prazos.py          # Testes unitários (regras de negócio isoladas)
│   └── test_integracao.py      # Testes de integração (conexão com banco e persistência)
│
└── .github/
    └── workflows/
        └── ci.yml              # Pipeline de Integração Contínua (GitHub Actions)
```

## Principais Decisões Arquiteturais

1. Separação de Responsabilidades (SoC): O arquivo regras.py não sabe o que é um HTML ou um banco de dados. Ele apenas recebe datas e retorna strings de status. Isso permite que os testes unitários rodem em milissegundos sem precisar simular um navegador;

2. Flask Blueprints (routes.py): As rotas foram agrupadas em um Blueprint chamado main, o que permite escalar o projeto (ex: se no futuro houver uma área de relatórios, ela pode ter seu próprio arquivo de rotas);

3. SQLAlchemy (ORM): A camada de persistência usa o padrão Object-Relational Mapping. Isso significa que não escrevemos SQL puro no código, o que evita vulnerabilidades como SQL Injection e facilita a futura migração para um banco PostgreSQL em produção.

## Impacto Social e ODS

O projeto está alinhado ao ODS 8 (Trabalho Decente e Crescimento Econômico), especificamente à Meta 8.3, ao fortalecer a eficiência operacional de um pequeno escritório de contabilidade. Isso possibilita que pequenos empreendedores locais recebam um atendimento mais ágil e com menor risco de multas, contribuindo para a formalização e a saúde financeira de micro e pequenas empresas da comunidade.