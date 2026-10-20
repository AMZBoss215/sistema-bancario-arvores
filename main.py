from __future__ import annotations
import sys
import random
from typing import Optional, List, Any
from modelos import ContaBancaria
from avl import ArvoreAVL

def _obter_classe_rubro_negra() -> Optional[Any]:
    try:
        import importlib
        return getattr(importlib.import_module("rubro_negra"), "ArvoreRubroNegra", None)
    except Exception:
        return None


class SistemaBancarioCLI:
    def __init__(self) -> None:
        self.arvore_avl: ArvoreAVL = ArvoreAVL()
        cls_rb = _obter_classe_rubro_negra()
        self.arvore_rb: Optional[Any] = cls_rb() if cls_rb is not None else None
        self.tipo_estrutura: str = "AVL"
        self.modo_detalhado: bool = False

    @property
    def arvore_ativa(self) -> Any:
        if self.tipo_estrutura == "AVL":
            return self.arvore_avl
        return self.arvore_rb

    def limpar_tela_visual(self) -> None:
        print("\n" + "-" * 70)

    def cabecalho(self) -> None:
        self.limpar_tela_visual()
        print("         SISTEMA BANCARIO - ARVORES BALANCEADAS (AED II)")
        print(f"Estrutura Ativa: [ {self.tipo_estrutura} ] | Modo Detalhado: [ {'ATIVADO' if self.modo_detalhado else 'DESATIVADO'} ]")
        print(f"Total de Contas: {self.arvore_ativa.tamanho} | Altura Atual: {self.arvore_ativa.altura}")
        print("-" * 70)

    def alternar_modo_detalhado(self) -> None:
        self.modo_detalhado = not self.modo_detalhado
        self.arvore_avl.modo_detalhado = self.modo_detalhado
        if self.arvore_rb is not None:
            self.arvore_rb.modo_detalhado = self.modo_detalhado
        status = "ATIVADO" if self.modo_detalhado else "DESATIVADO"
        print(f"\nModo Detalhado alterado para: [ {status} ]")
        input("\nPressione ENTER para continuar...")

    def alternar_estrutura(self) -> None:
        if self.tipo_estrutura == "AVL":
            if self.arvore_rb is None:
                print("\nA Arvore Rubro-Negra ainda esta em desenvolvimento na branch da equipe.")
                input("\nPressione ENTER para continuar...")
                return
            self.tipo_estrutura = "RUBRO-NEGRA"
        else:
            self.tipo_estrutura = "AVL"
        print(f"\nEstrutura ativa alterada para: [ {self.tipo_estrutura} ]")
        input("\nPressione ENTER para continuar...")

    def ler_inteiro(self, prompt: str) -> Optional[int]:
        while True:
            valor = input(prompt).strip()
            if not valor:
                return None
            try:
                num = int(valor)
                if num <= 0:
                    print("Por favor, digite um numero inteiro positivo maior que zero.")
                    continue
                return num
            except ValueError:
                print("Entrada invalida. Digite apenas numeros inteiros.")

    def ler_float(self, prompt: str) -> float:
        while True:
            valor = input(prompt).strip().replace(",", ".")
            if not valor:
                return 0.0
            try:
                num = float(valor)
                if num < 0:
                    print("O saldo nao pode ser negativo.")
                    continue
                return num
            except ValueError:
                print("Valor invalido. Digite um valor monetario valido.")

    def cadastrar_conta(self) -> None:
        self.cabecalho()
        print(">>> 1. CADASTRAR CONTA BANCARIA (INSERIR)")
        numero = self.ler_inteiro("Numero da conta: ")
        if numero is None:
            print("Operacao cancelada.")
            input("\nPressione ENTER para voltar...")
            return

        titular = input("Nome do titular: ").strip()
        if not titular:
            titular = f"Titular {numero}"

        agencia = input("Agencia (padrao 0001): ").strip()
        if not agencia:
            agencia = "0001"

        print("Tipos de Conta: [1] Corrente | [2] Poupanca | [3] Salario")
        opcao_tipo = input("Selecione o tipo (1/2/3) [padrao 1]: ").strip()
        mapa_tipos = {"1": "Corrente", "2": "Poupanca", "3": "Salario"}
        tipo = mapa_tipos.get(opcao_tipo, "Corrente")

        saldo = self.ler_float("Saldo inicial (R$): ")

        nova_conta = ContaBancaria(numero, titular, agencia, tipo, saldo)
        logs_iniciais = len(self.arvore_ativa.estatisticas.logs_detalhados)

        sucesso = self.arvore_ativa.inserir(nova_conta)

        if sucesso:
            print(f"\n[SUCESSO] Conta {numero} ({titular}) cadastrada com sucesso!")
            if self.modo_detalhado:
                print("\n--- Eventos do Modo Detalhado ---")
                logs_novos = self.arvore_ativa.estatisticas.logs_detalhados[logs_iniciais:]
                for log in logs_novos:
                    print(" ", log)
                print("\n--- Estrutura Resultante ---")
                self.arvore_ativa.exibir_arvore()
        else:
            print(f"\n[AVISO] A conta com numero {numero} ja existe no sistema. Chaves duplicadas sao rejeitadas.")

        input("\nPressione ENTER para voltar ao menu...")

    def buscar_conta(self) -> None:
        self.cabecalho()
        print(">>> 2. BUSCAR CONTA POR NUMERO")
        numero = self.ler_inteiro("Digite o numero da conta a ser buscada: ")
        if numero is None:
            return

        comps_antes = self.arvore_ativa.estatisticas.comparacoes
        conta = self.arvore_ativa.buscar(numero)
        comps_gastas = self.arvore_ativa.estatisticas.comparacoes - comps_antes

        if conta is not None:
            print("\n" + "=" * 50)
            print("CONTA ENCONTRADA:")
            print(f" Numero da Conta : {conta.numero_conta}")
            print(f" Titular         : {conta.titular}")
            print(f" Agencia         : {conta.agencia}")
            print(f" Tipo de Conta   : {conta.tipo}")
            print(f" Saldo Atual     : R$ {conta.saldo:,.2f}")
            print("=" * 50)
            print(f"Custo da Busca: {comps_gastas} nos visitados no caminho.")
        else:
            print(f"\n[NAO ENCONTRADA] Nenhuma conta com numero {numero} foi localizada.")
            print(f"Nos visitados ate confirmar inexistencia: {comps_gastas}")

        input("\nPressione ENTER para voltar ao menu...")

    def remover_conta(self) -> None:
        self.cabecalho()
        print(">>> 3. REMOVER CONTA POR NUMERO")
        numero = self.ler_inteiro("Digite o numero da conta que deseja remover: ")
        if numero is None:
            return

        logs_iniciais = len(self.arvore_ativa.estatisticas.logs_detalhados)
        removida = self.arvore_ativa.remover(numero)

        if removida is not None:
            print(f"\n[SUCESSO] Conta {numero} ({removida.titular}) removida com sucesso!")
            if self.modo_detalhado:
                print("\n--- Eventos de Rebalanceamento ---")
                logs_novos = self.arvore_ativa.estatisticas.logs_detalhados[logs_iniciais:]
                for log in logs_novos:
                    print(" ", log)
                print("\n--- Estrutura Resultante ---")
                self.arvore_ativa.exibir_arvore()
        else:
            print(f"\n[ERRO] A conta com numero {numero} nao foi encontrada para remocao.")

        input("\nPressione ENTER para voltar ao menu...")

    def exibir_arvore(self) -> None:
        self.cabecalho()
        print(">>> 4. DESENHO DA ESTRUTURA NO TERMINAL\n")
        self.arvore_ativa.exibir_arvore()
        input("\nPressione ENTER para voltar ao menu...")

    def listar_em_ordem(self) -> None:
        self.cabecalho()
        print(">>> 5. LISTAR CONTAS EM ORDEM (CRESCENTE POR NUMERO)\n")
        contas: List[ContaBancaria] = self.arvore_ativa.caminhamento_em_ordem()
        if not contas:
            print("Nenhuma conta cadastrada.")
        else:
            print(f"{'CONTA':<10} | {'TITULAR':<25} | {'AGENCIA':<8} | {'TIPO':<12} | {'SALDO':<15}")
            print("-" * 75)
            for c in contas:
                print(f"{c.numero_conta:<10} | {c.titular:<25} | {c.agencia:<8} | {c.tipo:<12} | R$ {c.saldo:>12,.2f}")
            print("-" * 75)
            print(f"Total de registros listados: {len(contas)}")
        input("\nPressione ENTER para voltar ao menu...")

    def listar_outros_caminhamentos(self) -> None:
        self.cabecalho()
        print(">>> 6. CAMINHAMENTOS PRE-ORDEM E POS-ORDEM\n")
        pre = self.arvore_ativa.caminhamento_pre_ordem()
        pos = self.arvore_ativa.caminhamento_pos_ordem()

        print("A. Pre-Ordem (Raiz -> Esquerda -> Direita):")
        print("   " + (" -> ".join(str(c.numero_conta) for c in pre) if pre else "Vazia"))

        print("\nB. Pos-Ordem (Esquerda -> Direita -> Raiz):")
        print("   " + (" -> ".join(str(c.numero_conta) for c in pos) if pos else "Vazia"))

        input("\nPressione ENTER para voltar ao menu...")

    def consultar_extremos(self) -> None:
        self.cabecalho()
        print(">>> 7. MENOR E MAIOR CHAVE ARMAZENADA\n")
        menor = self.arvore_ativa.obter_menor()
        maior = self.arvore_ativa.obter_maior()

        if menor is not None and maior is not None:
            print(f"Menor Chave : Conta {menor.numero_conta} - Titular: {menor.titular}")
            print(f"Maior Chave : Conta {maior.numero_conta} - Titular: {maior.titular}")
        else:
            print("A arvore esta vazia.")

        input("\nPressione ENTER para voltar ao menu...")

    def exibir_metricas_arvore(self) -> None:
        self.cabecalho()
        print(">>> 8. ALTURA, QUANTIDADE DE NOS E BALANCEAMENTO\n")
        print(f"Estrutura              : {self.tipo_estrutura}")
        print(f"Total de Nos           : {self.arvore_ativa.tamanho}")
        print(f"Altura da Arvore       : {self.arvore_ativa.altura}")
        if self.arvore_ativa.raiz is not None and hasattr(self.arvore_ativa.raiz, "fator_balanceamento"):
            print(f"Fator de Balanceamento : {self.arvore_ativa.raiz.fator_balanceamento} (Raiz)")
        input("\nPressione ENTER para voltar ao menu...")

    def exibir_estatisticas_rotacoes(self) -> None:
        self.cabecalho()
        print(">>> 9. ESTATISTICAS DE REBALANCEAMENTO (METRICAS OBRIGATORIAS)\n")
        est = self.arvore_ativa.estatisticas
        print(f"Rotacoes Simples a Direita (LL)  : {est.rotacoes_simples_direita}")
        print(f"Rotacoes Simples a Esquerda (RR) : {est.rotacoes_simples_esquerda}")
        print(f"Rotacoes Duplas Esquerda-Direita : {est.rotacoes_duplas_esq_dir}")
        print(f"Rotacoes Duplas Direita-Esquerda : {est.rotacoes_duplas_dir_esq}")
        print("-" * 50)
        print(f"TOTAL GERAL DE ROTACOES          : {est.total_rotacoes}")
        print(f"TOTAL DE RECOLORACOES (RN)       : {est.recoloracoes}")
        print(f"TOTAL DE COMPARACOES REALIZADAS  : {est.comparacoes}")
        input("\nPressione ENTER para voltar ao menu...")

    def validar_propriedades_formais(self) -> None:
        self.cabecalho()
        print(">>> 10. VALIDACAO MATEMATICA FORMAL DA ESTRUTURA\n")
        valido, mensagem = self.arvore_ativa.validar_propriedades()
        if valido:
            print("[STATUS: APROVADO]")
            print(f"Laudo: {mensagem}")
            print("Todos os nos satisfazem |FB| <= 1 e a ordenacao de busca binaria.")
        else:
            print("[STATUS: REPROVADO - VIOLACAO ENCONTRADA]")
            print(f"Detalhes: {mensagem}")
        input("\nPressione ENTER para voltar ao menu...")

    def submenu_defesa(self) -> None:
        while True:
            self.cabecalho()
            print(">>> 13. MENU DE CARGA RAPIDA PARA DEFESA COM O PROFESSOR\n")
            print("1. Carregar Sequencia da Aula 4 (Slide 74: [30, 20, 40, 10, 5, 50, 35, 55])")
            print("2. Demonstrar Caso LL (Insercao: [5, 3, 1])")
            print("3. Demonstrar Caso RR (Insercao: [1, 3, 5])")
            print("4. Demonstrar Caso LR (Insercao: [20, 10, 15])")
            print("5. Demonstrar Caso RL (Insercao: [10, 20, 15])")
            print("6. Gerar e Inserir 15 Contas Aleatorias Realistas")
            print("7. Limpar Arvore Atual (Reset)")
            print("0. Voltar ao Menu Principal")
            print("-" * 70)

            op = input("Selecione uma opcao: ").strip()

            if op == "0":
                break
            elif op == "1":
                seq = [30, 20, 40, 10, 5, 50, 35, 55]
                print(f"\nCarregando sequencia: {seq}...")
                for num in seq:
                    self.arvore_ativa.inserir(ContaBancaria(num, f"Titular {num}", "0001", "Corrente", 100.0 * num))
                print("Carga concluida com sucesso!")
                self.arvore_ativa.exibir_arvore()
                input("\nPressione ENTER para continuar...")
            elif op == "2":
                self.arvore_avl = ArvoreAVL(modo_detalhado=True)
                for num in [5, 3, 1]:
                    self.arvore_avl.inserir(ContaBancaria(num, f"Titular {num}", "0001", "Corrente", 100.0))
                print("\nCaso LL executado com sucesso (SD no 5)!")
                self.arvore_avl.exibir_arvore()
                input("\nPressione ENTER para continuar...")
            elif op == "3":
                self.arvore_avl = ArvoreAVL(modo_detalhado=True)
                for num in [1, 3, 5]:
                    self.arvore_avl.inserir(ContaBancaria(num, f"Titular {num}", "0001", "Corrente", 100.0))
                print("\nCaso RR executado com sucesso (SE no 1)!")
                self.arvore_avl.exibir_arvore()
                input("\nPressione ENTER para continuar...")
            elif op == "4":
                self.arvore_avl = ArvoreAVL(modo_detalhado=True)
                for num in [20, 10, 15]:
                    self.arvore_avl.inserir(ContaBancaria(num, f"Titular {num}", "0001", "Corrente", 100.0))
                print("\nCaso LR executado com sucesso (Dupla ED no 20)!")
                self.arvore_avl.exibir_arvore()
                input("\nPressione ENTER para continuar...")
            elif op == "5":
                self.arvore_avl = ArvoreAVL(modo_detalhado=True)
                for num in [10, 20, 15]:
                    self.arvore_avl.inserir(ContaBancaria(num, f"Titular {num}", "0001", "Corrente", 100.0))
                print("\nCaso RL executado com sucesso (Dupla DE no 10)!")
                self.arvore_avl.exibir_arvore()
                input("\nPressione ENTER para continuar...")
            elif op == "6":
                random.seed()
                nomes = ["Alice", "Bernardo", "Clara", "Daniel", "Eduardo", "Fernanda", "Gabriel", "Helena", "Igor", "Juliana"]
                sobrenomes = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira", "Ferreira", "Costa"]
                numeros = random.sample(range(100, 999), 15)
                for num in numeros:
                    tit = f"{random.choice(nomes)} {random.choice(sobrenomes)}"
                    tipo = random.choice(["Corrente", "Poupanca", "Salario"])
                    saldo = round(random.uniform(500.0, 25000.0), 2)
                    self.arvore_ativa.inserir(ContaBancaria(num, tit, "0001", tipo, saldo))
                print(f"\n15 contas inseridas com sucesso: {sorted(numeros)}")
                self.arvore_ativa.exibir_arvore()
                input("\nPressione ENTER para continuar...")
            elif op == "7":
                self.arvore_avl = ArvoreAVL(modo_detalhado=self.modo_detalhado)
                cls_rb = _obter_classe_rubro_negra()
                if cls_rb is not None:
                    self.arvore_rb = cls_rb(modo_detalhado=self.modo_detalhado)
                print("\nArvore limpa com sucesso!")
                input("\nPressione ENTER para continuar...")

    def executar(self) -> None:
        while True:
            self.cabecalho()
            print("1.  Cadastrar Conta Bancaria (Inserir)")
            print("2.  Buscar Conta por Numero")
            print("3.  Remover Conta por Numero")
            print("4.  Exibir Desenho da Arvore no Terminal")
            print("5.  Listar Contas em Ordem (Caminhamento Em-Ordem)")
            print("6.  Listar Caminhamentos Alternativos (Pre e Pos-Ordem)")
            print("7.  Consultar Menor e Maior Chave")
            print("8.  Exibir Altura e Quantidade de Nos")
            print("9.  Exibir Estatisticas de Rebalanceamento")
            print("10. Validar Propriedades Formais da Arvore")
            print("11. Alternar Modo Detalhado [ON/OFF]")
            print("12. Alternar Estrutura Ativa (AVL <-> Rubro-Negra)")
            print("13. Menu de Carga Rapida para a Defesa com o Professor")
            print("0.  Sair do Sistema")
            print("-" * 70)

            opcao = input("Digite a opcao desejada: ").strip()

            if opcao == "0":
                print("\nEncerrando o Sistema Bancario. Ate logo!")
                sys.exit(0)
            elif opcao == "1":
                self.cadastrar_conta()
            elif opcao == "2":
                self.buscar_conta()
            elif opcao == "3":
                self.remover_conta()
            elif opcao == "4":
                self.exibir_arvore()
            elif opcao == "5":
                self.listar_em_ordem()
            elif opcao == "6":
                self.listar_outros_caminhamentos()
            elif opcao == "7":
                self.consultar_extremos()
            elif opcao == "8":
                self.exibir_metricas_arvore()
            elif opcao == "9":
                self.exibir_estatisticas_rotacoes()
            elif opcao == "10":
                self.validar_propriedades_formais()
            elif opcao == "11":
                self.alternar_modo_detalhado()
            elif opcao == "12":
                self.alternar_estrutura()
            elif opcao == "13":
                self.submenu_defesa()
            else:
                print("\nOpcao invalida. Tente novamente.")
                input("\nPressione ENTER para continuar...")


if __name__ == "__main__":
    app = SistemaBancarioCLI()
    app.executar()
