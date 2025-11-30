**Minimizador de AFD**

Projeto para apresentação acadêmica: minimizador de Autômato Finito Determinístico (AFD) em Python.

**Resumo**: Este projeto lê um AFD definido em JSON, aplica o algoritmo de minimização (método de preenchimento de tabela), gera um JSON com o AFD minimizado e produz imagens (PNG) do autômato original e do minimizado. Também imprime e ilustra a tabela de marcação usada no processo — ideal para uso em slides de apresentação.

**Arquivos do repositório**
- **`minimizador_afd.py`**: Código principal que implementa todas as etapas (carregar JSON, remover estados inalcançáveis, executar preenchimento de tabela, formar classes de equivalência, construir AFD minimizado, gerar imagens e salvar JSON).
- **`afd_entrada.json`**: Exemplo de AFD de entrada usado para testes.
- **`afd_minimizado.json`**: (gerado) saída com o AFD minimizado.
- **`afd_original.png`**, **`afd_minimizado.png`**: (gerados) imagens dos autômatos.

**Objetivos do README / apresentação**
- Explicar o que o projeto faz e por que é útil.
- Descrever passo a passo o algoritmo implementado e as funções principais.
- Mostrar instruções de execução e dependências.

**Como executar**
1. Crie (ou ative) um ambiente virtual Python e instale dependências:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# ou (se não existir requirements.txt):
pip install graphviz
```

2. Instale o Graphviz nativo no sistema (necessário para gerar PNGs):
- Windows: baixe e instale de https://graphviz.org/download/
- Certifique-se de que o diretório `bin` do Graphviz esteja no `PATH` do sistema.

3. Execute o minimizador passando o JSON de entrada (ou sem argumentos para usar `afd_entrada.json`):

```powershell
python minimizador_afd.py afd_entrada.json
```

Após execução você verá impressões da tabela de marcação, histórico de marcações e o resumo. Os arquivos de saída serão gravados na mesma pasta.

**Formato do JSON de entrada**
O AFD deve ter a seguinte estrutura (exemplo mínimo):

```json
{
  "estados": ["q0", "q1", "q2"],
  "alfabeto": ["a", "b"],
  "estado_inicial": "q0",
  "estados_finais": ["q2"],
  "transicoes": {
    "q0": {"a": "q1", "b": "q0"},
    "q1": {"a": "q2", "b": "q0"},
    "q2": {"a": "q2", "b": "q2"}
  }
}
```

**Explicação do algoritmo e funções principais (arquivo `minimizador_afd.py`)**
- **Carregamento e estruturas**
  - `__init__(caminho_json)`: lê o JSON e inicializa estruturas (estados, alfabeto, transições, estado inicial e finais).
  - `_carregar_json(caminho)`, `_salvar_json(dados, caminho)`: I/O em JSON com encoding UTF-8.

- **Etapa 1 — Remoção de estados inalcançáveis**
  - `_encontrar_estados_alcancaveis()`: BFS a partir do estado inicial para coletar estados alcançáveis.
  - `_remover_estados_inalcancaveis()`: atualiza listas e transições removendo estados inalcançáveis (pré-processamento importante).

- **Etapa 2 — Preenchimento de tabela (Table-Filling Algorithm)**
  - `_inicializar_tabela()`: cria todos os pares de estados (somente triangular inferior superiorizado por lista) e define como não marcados.
  - `_marcar_pares_triviais()`: marca imediatamente pares onde um é final e o outro não (pois são distinguíveis).
  - `_marcar_pares_iterativamente()`: itera marcando pares quando existe um símbolo cujo par de destinos já foi marcado. Mantém histórico de iterações para visualização.
  - `exibir_tabela_marcacao()`: imprime a tabela em formato de matriz triangular inferior (X = distinguível, - = equivalente). Essa saída é ideal para slides — copie a tabela e cole em um slide ou gere screenshot.

- **Etapa 3 — Construção do AFD minimizado**
  - `_encontrar_classes_equivalencia()`: a partir dos pares não marcados agrupa estados equivalentes (classes de equivalência).
  - `_construir_afd_minimizado(classes)`: cria nomes para classes (ex.: `{q1,q3}`), determina novo estado inicial, novos estados finais e novas transições (usando um representante por classe).

- **Visualização**
  - `gerar_imagem_automato(afd_dados, nome_arquivo, titulo)`: gera um PNG usando a biblioteca `graphviz` (Python) + Graphviz nativo. Agrupa símbolos com mesmo destino em um rótulo de aresta (ex.: `a,b`).

- **Método orquestrador**
  - `minimizar(diretorio_saida)`: executa todo o fluxo: remoção de inalcançáveis, inicialização e marcação da tabela, construção do novo AFD, gravação do JSON e geração de imagens.


