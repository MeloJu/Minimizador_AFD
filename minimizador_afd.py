# ============================================================================
# MINIMIZADOR DE AUTÔMATO FINITO DETERMINÍSTICO (AFD)
# Projeto para apresentação acadêmica
# ============================================================================
# Este programa implementa o algoritmo de minimização de AFD usando o 
# método de preenchimento de tabela (Table-Filling Algorithm)
# ============================================================================

import json                          # Para ler e escrever arquivos JSON
import os                            # Para manipulação de caminhos de arquivos
from typing import Dict, List, Set, Tuple, Any  # Para type hints
from itertools import combinations   # Para gerar pares de estados
from graphviz import Digraph         # Para gerar imagens do autômato

# ============================================================================
# CLASSE PRINCIPAL: MinimizadorAFD
# ============================================================================

class MinimizadorAFD:
    """
    Classe responsável por minimizar um Autômato Finito Determinístico (AFD).
    
    O algoritmo utilizado é o método de preenchimento de tabela, que marca
    pares de estados distinguíveis iterativamente até que nenhuma nova
    marcação seja possível.
    """
    
    def __init__(self, caminho_json: str):
        """
        Inicializa o minimizador carregando o AFD de um arquivo JSON.
        
        Parâmetros:
            caminho_json (str): Caminho para o arquivo JSON contendo o AFD
        """
        # Carrega o AFD do arquivo JSON
        self.afd = self._carregar_json(caminho_json)
        
        # Extrai os componentes do AFD
        self.estados: List[str] = self.afd['estados']           # Lista de estados
        self.alfabeto: List[str] = self.afd['alfabeto']         # Símbolos do alfabeto
        self.estado_inicial: str = self.afd['estado_inicial']   # Estado inicial
        self.estados_finais: Set[str] = set(self.afd['estados_finais'])  # Estados de aceitação
        self.transicoes: Dict = self.afd['transicoes']          # Função de transição
        
        # Estruturas para o processo de minimização
        self.tabela_marcacao: Dict[Tuple[str, str], bool] = {}  # Tabela de pares marcados
        self.historico_marcacoes: List[Dict] = []               # Histórico para visualização
        
    def _carregar_json(self, caminho: str) -> Dict:
        """
        Carrega e retorna o conteúdo de um arquivo JSON.
        
        Parâmetros:
            caminho (str): Caminho do arquivo JSON
            
        Retorna:
            Dict: Dicionário com os dados do AFD
        """
        # Abre o arquivo com encoding UTF-8 para suportar caracteres especiais
        with open(caminho, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)
    
    def _salvar_json(self, dados: Dict, caminho: str) -> None:
        """
        Salva um dicionário em um arquivo JSON.
        
        Parâmetros:
            dados (Dict): Dados a serem salvos
            caminho (str): Caminho do arquivo de destino
        """
        # Salva com indentação para melhor legibilidade
        with open(caminho, 'w', encoding='utf-8') as arquivo:
            json.dump(dados, arquivo, indent=4, ensure_ascii=False)
    
    # ========================================================================
    # ETAPA 1: REMOÇÃO DE ESTADOS INALCANÇÁVEIS
    # ========================================================================
    
    def _encontrar_estados_alcancaveis(self) -> Set[str]:
        """
        Encontra todos os estados alcançáveis a partir do estado inicial.
        
        Utiliza busca em largura (BFS) para percorrer todos os estados
        que podem ser atingidos através das transições.
        
        Retorna:
            Set[str]: Conjunto de estados alcançáveis
        """
        # Conjunto de estados já visitados (começa com o estado inicial)
        alcancaveis = {self.estado_inicial}
        
        # Fila para BFS (começa com o estado inicial)
        fila = [self.estado_inicial]
        
        # Processa enquanto houver estados na fila
        while fila:
            # Remove o primeiro estado da fila
            estado_atual = fila.pop(0)
            
            # Para cada símbolo do alfabeto
            for simbolo in self.alfabeto:
                # Obtém o próximo estado através da transição
                if estado_atual in self.transicoes and simbolo in self.transicoes[estado_atual]:
                    proximo_estado = self.transicoes[estado_atual][simbolo]
                    
                    # Se o estado ainda não foi visitado
                    if proximo_estado not in alcancaveis:
                        # Marca como alcançável
                        alcancaveis.add(proximo_estado)
                        # Adiciona à fila para processar suas transições
                        fila.append(proximo_estado)
        
        return alcancaveis
    
    def _remover_estados_inalcancaveis(self) -> None:
        """
        Remove estados que não são alcançáveis a partir do estado inicial.
        
        Esta é uma etapa de pré-processamento importante para a minimização.
        """
        # Encontra estados alcançáveis
        alcancaveis = self._encontrar_estados_alcancaveis()
        
        # Imprime informações sobre estados removidos
        inalcancaveis = set(self.estados) - alcancaveis
        if inalcancaveis:
            print(f"\n[ETAPA 1] Estados inalcançáveis removidos: {inalcancaveis}")
        else:
            print("\n[ETAPA 1] Nenhum estado inalcançável encontrado.")
        
        # Atualiza a lista de estados
        self.estados = [e for e in self.estados if e in alcancaveis]
        
        # Atualiza os estados finais
        self.estados_finais = self.estados_finais & alcancaveis
        
        # Atualiza as transições (remove transições de estados inalcançáveis)
        novas_transicoes = {}
        for estado in self.estados:
            if estado in self.transicoes:
                novas_transicoes[estado] = self.transicoes[estado]
        self.transicoes = novas_transicoes
    
    # ========================================================================
    # ETAPA 2: ALGORITMO DE PREENCHIMENTO DE TABELA
    # ========================================================================
    
    def _inicializar_tabela(self) -> None:
        """
        Inicializa a tabela de marcação para o algoritmo de minimização.
        
        Cria uma entrada para cada par de estados (sem repetição).
        Todos os pares começam como não marcados (False).
        """
        # Para cada par único de estados
        for i in range(len(self.estados)):
            for j in range(i + 1, len(self.estados)):
                # Ordena o par para garantir consistência
                par = (self.estados[i], self.estados[j])
                # Inicializa como não marcado
                self.tabela_marcacao[par] = False
    
    def _obter_par_ordenado(self, e1: str, e2: str) -> Tuple[str, str]:
        """
        Retorna um par de estados ordenado de forma consistente.
        
        Parâmetros:
            e1 (str): Primeiro estado
            e2 (str): Segundo estado
            
        Retorna:
            Tuple[str, str]: Par ordenado (menor, maior)
        """
        # Encontra os índices dos estados na lista
        idx1 = self.estados.index(e1) if e1 in self.estados else -1
        idx2 = self.estados.index(e2) if e2 in self.estados else -1
        
        # Retorna ordenado pelo índice na lista
        if idx1 < idx2:
            return (e1, e2)
        else:
            return (e2, e1)
    
    def _marcar_pares_triviais(self) -> None:
        """
        Marca pares onde um estado é final e outro não é final.
        
        Esta é a primeira passagem do algoritmo - estados finais e não-finais
        são distinguíveis pois aceitam linguagens diferentes.
        """
        print("\n[ETAPA 2.1] Marcando pares trivialmente distinguíveis (final vs não-final):")
        
        pares_marcados = []
        
        # Para cada par na tabela
        for par in self.tabela_marcacao:
            e1, e2 = par
            
            # Verifica se um é final e outro não
            e1_final = e1 in self.estados_finais
            e2_final = e2 in self.estados_finais
            
            if e1_final != e2_final:
                # Marca o par como distinguível
                self.tabela_marcacao[par] = True
                pares_marcados.append(par)
        
        # Exibe os pares marcados
        for par in pares_marcados:
            print(f"   Par {par} marcado (um é final, outro não)")
        
        # Salva no histórico
        self.historico_marcacoes.append({
            'etapa': 'Marcação Trivial',
            'pares_marcados': pares_marcados.copy(),
            'descricao': 'Pares onde um estado é final e outro não'
        })
    
    def _marcar_pares_iterativamente(self) -> None:
        """
        Marca pares iterativamente baseado nas transições.
        
        Um par (p, q) é marcado se existe um símbolo 'a' tal que o par
        (δ(p,a), δ(q,a)) já está marcado como distinguível.
        """
        print("\n[ETAPA 2.2] Marcando pares iterativamente por transições:")
        
        iteracao = 0
        houve_mudanca = True
        
        # Continua enquanto houver novas marcações
        while houve_mudanca:
            houve_mudanca = False
            iteracao += 1
            pares_marcados_iteracao = []
            
            print(f"\n   --- Iteração {iteracao} ---")
            
            # Para cada par não marcado
            for par in self.tabela_marcacao:
                # Pula se já está marcado
                if self.tabela_marcacao[par]:
                    continue
                
                e1, e2 = par
                
                # Para cada símbolo do alfabeto
                for simbolo in self.alfabeto:
                    # Obtém os estados de destino
                    destino1 = self.transicoes.get(e1, {}).get(simbolo)
                    destino2 = self.transicoes.get(e2, {}).get(simbolo)
                    
                    # Se algum destino não existe, pula
                    if destino1 is None or destino2 is None:
                        continue
                    
                    # Se os destinos são diferentes
                    if destino1 != destino2:
                        # Obtém o par ordenado dos destinos
                        par_destino = self._obter_par_ordenado(destino1, destino2)
                        
                        # Se o par de destinos está marcado
                        if par_destino in self.tabela_marcacao and self.tabela_marcacao[par_destino]:
                            # Marca o par atual
                            self.tabela_marcacao[par] = True
                            pares_marcados_iteracao.append(par)
                            houve_mudanca = True
                            print(f"   Par {par} marcado (transição '{simbolo}' leva a {par_destino} que é distinguível)")
                            break
            
            # Salva no histórico
            if pares_marcados_iteracao:
                self.historico_marcacoes.append({
                    'etapa': f'Iteração {iteracao}',
                    'pares_marcados': pares_marcados_iteracao.copy(),
                    'descricao': 'Marcação por transições distinguíveis'
                })
        
        print(f"\n   Algoritmo convergiu após {iteracao} iterações.")
    
    # ========================================================================
    # ETAPA 3: CONSTRUÇÃO DO AFD MINIMIZADO
    # ========================================================================
    
    def _encontrar_classes_equivalencia(self) -> List[Set[str]]:
        """
        Encontra as classes de equivalência a partir da tabela de marcação.
        
        Estados no mesmo conjunto são equivalentes (não estão marcados na tabela).
        
        Retorna:
            List[Set[str]]: Lista de conjuntos de estados equivalentes
        """
        print("\n[ETAPA 3] Encontrando classes de equivalência:")
        
        # Inicialmente, cada estado é sua própria classe
        classes: List[Set[str]] = [{e} for e in self.estados]
        
        # Para cada par não marcado, une as classes
        for par, marcado in self.tabela_marcacao.items():
            if not marcado:
                e1, e2 = par
                
                # Encontra as classes de cada estado
                classe1 = None
                classe2 = None
                
                for classe in classes:
                    if e1 in classe:
                        classe1 = classe
                    if e2 in classe:
                        classe2 = classe
                
                # Se estão em classes diferentes, une-as
                if classe1 is not None and classe2 is not None and classe1 != classe2:
                    # Une as classes
                    nova_classe = classe1 | classe2
                    classes.remove(classe1)
                    classes.remove(classe2)
                    classes.append(nova_classe)
        
        # Exibe as classes encontradas
        for i, classe in enumerate(classes):
            print(f"   Classe {i + 1}: {classe}")
        
        return classes
    
    def _construir_afd_minimizado(self, classes: List[Set[str]]) -> Dict:
        """
        Constrói o AFD minimizado a partir das classes de equivalência.
        
        Parâmetros:
            classes (List[Set[str]]): Classes de equivalência
            
        Retorna:
            Dict: AFD minimizado no formato JSON
        """
        print("\n[ETAPA 4] Construindo AFD minimizado:")
        
        # Cria nomes para os novos estados (usando os estados unidos)
        def nome_classe(classe: Set[str]) -> str:
            """Gera um nome para a classe baseado nos estados que contém."""
            return '{' + ','.join(sorted(classe)) + '}'
        
        # Mapeia cada estado antigo para sua nova classe
        estado_para_classe: Dict[str, str] = {}
        for classe in classes:
            nome = nome_classe(classe)
            for estado in classe:
                estado_para_classe[estado] = nome
        
        # Cria a lista de novos estados
        novos_estados = [nome_classe(c) for c in classes]
        print(f"   Novos estados: {novos_estados}")
        
        # Encontra o novo estado inicial
        novo_estado_inicial = estado_para_classe[self.estado_inicial]
        print(f"   Novo estado inicial: {novo_estado_inicial}")
        
        # Encontra os novos estados finais
        novos_estados_finais = list(set(
            estado_para_classe[ef] for ef in self.estados_finais
        ))
        print(f"   Novos estados finais: {novos_estados_finais}")
        
        # Cria as novas transições
        novas_transicoes: Dict[str, Dict[str, str]] = {}
        
        for classe in classes:
            nome_origem = nome_classe(classe)
            novas_transicoes[nome_origem] = {}
            
            # Usa um representante da classe para determinar as transições
            representante = list(classe)[0]
            
            for simbolo in self.alfabeto:
                if representante in self.transicoes and simbolo in self.transicoes[representante]:
                    destino_antigo = self.transicoes[representante][simbolo]
                    destino_novo = estado_para_classe[destino_antigo]
                    novas_transicoes[nome_origem][simbolo] = destino_novo
        
        print("   Novas transições criadas.")
        
        # Monta o AFD minimizado
        afd_minimizado = {
            'estados': novos_estados,
            'alfabeto': self.alfabeto,
            'estado_inicial': novo_estado_inicial,
            'estados_finais': novos_estados_finais,
            'transicoes': novas_transicoes
        }
        
        return afd_minimizado
    
    # ========================================================================
    # VISUALIZAÇÃO: TABELA DE MARCAÇÃO
    # ========================================================================
    
    def exibir_tabela_marcacao(self) -> str:
        """
        Exibe a tabela de marcação de forma visual.
        
        Retorna:
            str: Representação textual da tabela
        """
        print("\n" + "=" * 60)
        print("TABELA DE MARCAÇÃO (MATRIZ TRIANGULAR INFERIOR)")
        print("=" * 60)
        
        # Calcula a largura máxima para formatação
        largura = max(len(e) for e in self.estados) + 2
        
        # Monta a tabela como string
        linhas = []
        
        # Cabeçalho
        cabecalho = " " * largura + "|"
        for i in range(len(self.estados) - 1):
            cabecalho += f" {self.estados[i]:^{largura}} |"
        linhas.append(cabecalho)
        linhas.append("-" * len(cabecalho))
        
        # Linhas da tabela
        for i in range(1, len(self.estados)):
            linha = f" {self.estados[i]:<{largura}}|"
            for j in range(i):
                par = self._obter_par_ordenado(self.estados[i], self.estados[j])
                if par in self.tabela_marcacao:
                    marcado = "X" if self.tabela_marcacao[par] else "-"
                else:
                    marcado = "?"
                linha += f" {marcado:^{largura}} |"
            linhas.append(linha)
        
        # Imprime e retorna
        tabela_str = "\n".join(linhas)
        print(tabela_str)
        print("\nLegenda: X = Distinguível, - = Equivalente")
        
        return tabela_str
    
    # ========================================================================
    # VISUALIZAÇÃO: GERAÇÃO DE IMAGEM DO AUTÔMATO
    # ========================================================================
    
    def gerar_imagem_automato(self, afd_dados: Dict, nome_arquivo: str, titulo: str = "") -> str:
        """
        Gera uma imagem PNG do autômato usando Graphviz.
        
        Parâmetros:
            afd_dados (Dict): Dados do AFD
            nome_arquivo (str): Nome base do arquivo de saída
            titulo (str): Título opcional para o grafo
            
        Retorna:
            str: Caminho do arquivo gerado
        """
        # Cria o grafo direcionado
        dot = Digraph(comment=titulo if titulo else 'AFD')
        dot.attr(rankdir='LR')  # Layout da esquerda para direita
        
        # Adiciona título se fornecido
        if titulo:
            dot.attr(label=titulo, fontsize='16')
        
        # Adiciona um nó invisível para a seta do estado inicial
        dot.node('', shape='none', width='0', height='0')
        
        # Adiciona os estados
        for estado in afd_dados['estados']:
            # Verifica se é estado final (círculo duplo)
            if estado in afd_dados['estados_finais']:
                dot.node(estado, estado, shape='doublecircle')
            else:
                dot.node(estado, estado, shape='circle')
        
        # Adiciona a seta para o estado inicial
        dot.edge('', afd_dados['estado_inicial'])
        
        # Adiciona as transições
        for origem, transicoes in afd_dados['transicoes'].items():
            # Agrupa transições com mesmo destino
            destinos: Dict[str, List[str]] = {}
            for simbolo, destino in transicoes.items():
                if destino not in destinos:
                    destinos[destino] = []
                destinos[destino].append(simbolo)
            
            # Cria as arestas
            for destino, simbolos in destinos.items():
                # Junta os símbolos com vírgula
                rotulo = ','.join(sorted(simbolos))
                dot.edge(origem, destino, label=rotulo)
        
        # Salva a imagem
        caminho = dot.render(nome_arquivo, format='png', cleanup=True)
        print(f"\n   Imagem gerada: {caminho}")
        
        return caminho
    
    # ========================================================================
    # MÉTODO PRINCIPAL: MINIMIZAR
    # ========================================================================
    
    def minimizar(self, diretorio_saida: str = ".") -> Dict:
        """
        Executa o processo completo de minimização do AFD.
        
        Parâmetros:
            diretorio_saida (str): Diretório para salvar os arquivos de saída
            
        Retorna:
            Dict: AFD minimizado
        """
        print("\n" + "=" * 70)
        print("        MINIMIZAÇÃO DE AUTÔMATO FINITO DETERMINÍSTICO (AFD)")
        print("=" * 70)
        
        print("\n[INFO] AFD Original:")
        print(f"   Estados: {self.estados}")
        print(f"   Alfabeto: {self.alfabeto}")
        print(f"   Estado inicial: {self.estado_inicial}")
        print(f"   Estados finais: {self.estados_finais}")
        
        # Etapa 1: Remove estados inalcançáveis
        self._remover_estados_inalcancaveis()
        
        # Etapa 2: Algoritmo de preenchimento de tabela
        print("\n[ETAPA 2] Iniciando algoritmo de preenchimento de tabela...")
        
        # Inicializa a tabela de marcação
        self._inicializar_tabela()
        
        # Marca pares triviais (final vs não-final)
        self._marcar_pares_triviais()
        
        # Exibe tabela após marcação trivial
        self.exibir_tabela_marcacao()
        
        # Marca pares iterativamente
        self._marcar_pares_iterativamente()
        
        # Exibe tabela final
        print("\n" + "=" * 60)
        print("TABELA DE MARCAÇÃO FINAL")
        print("=" * 60)
        self.exibir_tabela_marcacao()
        
        # Etapa 3: Encontra classes de equivalência
        classes = self._encontrar_classes_equivalencia()
        
        # Etapa 4: Constrói AFD minimizado
        afd_minimizado = self._construir_afd_minimizado(classes)
        
        # Salva o AFD minimizado em JSON
        caminho_json_saida = os.path.join(diretorio_saida, "afd_minimizado.json")
        self._salvar_json(afd_minimizado, caminho_json_saida)
        print(f"\n[SAÍDA] AFD minimizado salvo em: {caminho_json_saida}")
        
        # Gera imagem do AFD original
        afd_original = {
            'estados': self.afd['estados'],
            'alfabeto': self.afd['alfabeto'],
            'estado_inicial': self.afd['estado_inicial'],
            'estados_finais': self.afd['estados_finais'],
            'transicoes': self.afd['transicoes']
        }
        self.gerar_imagem_automato(
            afd_original, 
            os.path.join(diretorio_saida, "afd_original"),
            "AFD Original"
        )
        
        # Gera imagem do AFD minimizado
        self.gerar_imagem_automato(
            afd_minimizado,
            os.path.join(diretorio_saida, "afd_minimizado"),
            "AFD Minimizado"
        )
        
        # Resumo final
        print("\n" + "=" * 70)
        print("                           RESUMO")
        print("=" * 70)
        print(f"   Estados originais: {len(self.afd['estados'])}")
        print(f"   Estados minimizados: {len(afd_minimizado['estados'])}")
        print(f"   Redução: {len(self.afd['estados']) - len(afd_minimizado['estados'])} estado(s)")
        print("=" * 70)
        
        return afd_minimizado


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    Função principal que executa o minimizador de AFD.
    """
    import sys
    
    # Verifica argumentos da linha de comando
    if len(sys.argv) < 2:
        # Usa arquivo padrão se nenhum for especificado
        caminho_entrada = "afd_entrada.json"
        print(f"[AVISO] Nenhum arquivo especificado. Usando '{caminho_entrada}'")
    else:
        caminho_entrada = sys.argv[1]
    
    # Verifica se o arquivo existe
    if not os.path.exists(caminho_entrada):
        print(f"[ERRO] Arquivo não encontrado: {caminho_entrada}")
        print("\nCrie um arquivo JSON com a seguinte estrutura:")
        print("""
{
    "estados": ["q0", "q1", "q2", ...],
    "alfabeto": ["a", "b", ...],
    "estado_inicial": "q0",
    "estados_finais": ["q2", ...],
    "transicoes": {
        "q0": {"a": "q1", "b": "q0"},
        "q1": {"a": "q2", "b": "q0"},
        ...
    }
}
        """)
        return
    
    # Diretório de saída (mesmo do arquivo de entrada)
    diretorio_saida = os.path.dirname(os.path.abspath(caminho_entrada))
    if not diretorio_saida:
        diretorio_saida = "."
    
    # Cria e executa o minimizador
    try:
        minimizador = MinimizadorAFD(caminho_entrada)
        afd_minimizado = minimizador.minimizar(diretorio_saida)
        print("\n[SUCESSO] Minimização concluída!")
    except Exception as e:
        print(f"\n[ERRO] Falha na minimização: {e}")
        raise


# ============================================================================
# PONTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    main()
