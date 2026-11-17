FARMAPET — APLICATIVO ACADÊMICO
================================

EQUIPE
- Ana Luiza Laet
- Éwelin Marcele
- Mikaelly Ketilley
- Thatiana Aragão

ARQUIVOS
- app.py: código principal do aplicativo Streamlit.
- farmacologia.py: funções matemáticas separadas e reutilizáveis.
- test_farmacologia.py: testes unitários dos cálculos.
- logo.svg: símbolo vetorial original do FarmaPet.
- requirements.txt: bibliotecas necessárias.
- dados_demonstracao.csv: conjunto de dados fictícios para testar gráficos e tabelas.
- REFERENCIAS_ABNT.md: referências científicas e técnicas consultadas.

REQUISITOS
- Python 3.10 ou superior (recomendado 3.11).
- Acesso à internet para instalar as dependências. O aplicativo não consulta bases externas em tempo real.

COMO EXECUTAR NO WINDOWS
1. Instale o Python em https://www.python.org/downloads/ (marque “Add Python to PATH”).
2. Extraia todos os arquivos da pasta ZIP.
3. Abra o Prompt de Comando dentro da pasta do projeto.
4. Execute: python -m venv .venv
5. Execute: .venv\Scripts\activate
6. Execute: pip install -r requirements.txt
7. Execute os testes: python -m unittest -v test_farmacologia.py
8. Execute: streamlit run app.py
9. O navegador abrirá o FarmaPet. Se não abrir, acesse http://localhost:8501.

COMO EXECUTAR NO macOS / LINUX
1. Abra o Terminal na pasta do projeto.
2. Execute: python3 -m venv .venv
3. Execute: source .venv/bin/activate
4. Execute: pip install -r requirements.txt
5. Execute os testes: python3 -m unittest -v test_farmacologia.py
6. Execute: streamlit run app.py
7. O navegador abrirá o FarmaPet. Se não abrir, acesse http://localhost:8501.

TESTE DE DEMONSTRAÇÃO
- Abra “Análise e resultados”.
- Clique em “Carregar dados fictícios de demonstração”.
- Confira os gráficos e a tabela. Esses dados são explicitamente fictícios.
- Para testar o cálculo, abra “Calculadora”, insira peso, dose prescrita e concentração.
- Para testar exportação, abra “Relatórios” após realizar um cálculo.

OBSERVAÇÕES IMPORTANTES
- A dose deve vir de prescrição veterinária. O aplicativo não recomenda nem escolhe dose.
- A calculadora executa matemática com os valores digitados; não avalia segurança clínica.
- A consulta de interações é parcial. Ausência de alerta não significa ausência de interação.
- Os registros ficam apenas na sessão do Streamlit e não são sincronizados nem armazenados em banco de dados.
- Não inserir dados pessoais identificáveis.
- Não há integração ativa com PubMed, NCBI, DrugBank ou outras bases nesta versão. Os links levam às páginas originais.
- Não há modelo de IA integrado. Interpretações descritivas são cálculos estatísticos simples sobre os registros da sessão.
- Antes de qualquer uso clínico, o conteúdo deve ser revisado por profissional habilitado e a aplicação submetida a testes adicionais.
