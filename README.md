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

## Impacto Social e ODS

O projeto está alinhado ao ODS 8 (Trabalho Decente e Crescimento Econômico), especificamente à Meta 8.3, ao fortalecer a eficiência operacional de um pequeno escritório de contabilidade. Isso possibilita que pequenos empreendedores locais recebam um atendimento mais ágil e com menor risco de multas, contribuindo para a formalização e a saúde financeira de micro e pequenas empresas da comunidade.