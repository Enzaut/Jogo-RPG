import threading
import random
import time
import os

# Funções auxiliares
def limpar_tela():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def introducao():
    print("\nBem-vindos ao Reino de Eldoria!\n")
    print("Vocês são bravos guerreiros em uma missão para salvar o reino das forças do mal.")
    print("Sua jornada os levará através de florestas sombrias, montanhas traiçoeiras e masmorras perigosas.")
    print("Preparem-se, escolham suas armas e embarquem nesta aventura épica!")
    input("\nPressione Enter para continuar...")
    limpar_tela()

# Funções principais do jogo
def escolher_arma(jogador):
    while True:
        print(f"\n{jogador['nome']}, escolha sua arma:")
        for i, arma in enumerate(armas_disponiveis):
            print(f"{i + 1}. {arma['nome']} (Ataque: {arma['ataque']}) - {arma['descricao']} (Especial: {arma['descricao_especial']})")
        escolha = input("Digite o número da arma escolhida: ")
        if escolha.isdigit():
            escolha = int(escolha) - 1
            if 0 <= escolha < len(armas_disponiveis):
                jogador["arma"] = armas_disponiveis[escolha]
                jogador["ataque"] = armas_disponiveis[escolha]["ataque"]
                jogador["vida_max"] += armas_disponiveis[escolha]["passiva_vida_extra"]
                jogador["vida"] = jogador["vida_max"]
                jogador["especial_pronto"] = False
                jogador["turnos_para_especial"] = 3
                print(f"\n{jogador['nome']} escolheu {armas_disponiveis[escolha]['nome']}.\n")
                input("\nPressione Enter para continuar...")
                limpar_tela()
                break
        print("Opção inválida. Tente novamente.")
        input("\nPressione Enter para continuar...")
        limpar_tela()

def acao_jogador(jogador, monstro):
    while True:
        turnos_especial = "Disponível!!" if jogador["especial_pronto"] else f"{jogador['turnos_para_especial']} turnos restantes"
        print(f"\n{jogador['nome']} ({jogador['vida']}/{jogador['vida_max']}), escolha sua ação: (1) Bater, (2) Defender, (3) Curar, (4) Especial ({turnos_especial})")
        acao = input("Digite o número da ação escolhida: ")
        if acao in ['1', '2', '3', '4']:
            if acao == '3' and jogador["curas_restantes"] <= 0:
                print("\nNão possui curas!\n")
            elif acao == '4' and not jogador["especial_pronto"]:
                print("\nEspecial não está pronto!\n")
            else:
                return acao
        else:
            print("\nAção inválida! Tente novamente.\n")

def realizar_ataque(jogador, monstro, semaforo):
    semaforo.acquire()
    dano = max(0, jogador["ataque"] - monstro["defesa"])
    if random.random() < jogador["arma"]["passiva_dobro_ataque"]:
        dano *= 2
        print(f"\n{jogador['nome']} conseguiu um ataque duplo!")
    monstro["vida"] = max(0, monstro["vida"] - dano)
    semaforo.release()
    time.sleep(1)
    print(f"\n{jogador['nome']} atacou {monstro['nome']} causando {dano} de dano. {monstro['nome']} ({monstro['vida']}/{monstro['vida_max']})\n")

def realizar_defesa(jogador):
    jogador["defendendo"] = True
    time.sleep(1)
    print(f"\n{jogador['nome']} se defendeu e reduzirá o dano do próximo ataque.\n")

def realizar_cura(jogador):
    jogador["vida"] = min(jogador["vida_max"], jogador["vida"] + 30)
    jogador["curas_restantes"] -= 1
    time.sleep(1)
    print(f"\n{jogador['nome']} se curou e agora tem {jogador['vida']} de vida.\n")

def realizar_especial(jogador, monstro, semaforo):
    semaforo.acquire()
    dano = jogador["ataque"] * 2  # Dano especial sendo o dobro do ataque normal
    monstro["vida"] = max(0, monstro["vida"] - dano)
    semaforo.release()
    time.sleep(1)
    print(f"\n{jogador['nome']} usou o especial {jogador['arma']['nome_especial']} causando {dano} de dano. {monstro['nome']} ({monstro['vida']}/{monstro['vida_max']})\n")
    jogador["especial_pronto"] = False
    jogador["turnos_para_especial"] = 3

def ataque_monstro(jogadores, monstro):
    for jogador in jogadores:
        if jogador["vida"] > 0:
            dano = max(0, monstro["ataque"] - jogador["defesa"])
            if jogador["defendendo"]:
                dano = max(0, dano // 2)
                jogador["defendendo"] = False
            jogador["vida"] = max(0, jogador["vida"] - dano)
            time.sleep(1)
            print(f"{monstro['nome']} atacou {jogador['nome']} causando {dano} de dano.\n")

def loot(monstro, jogador):
    item = random.choice(itens_disponiveis)
    jogador["inventario"].append(item)
    if monstro:
        print(f"\n{monstro['nome']} deixou cair {item['nome']}. {jogador['nome']} pegou o item.\n")
    else:
        print(f"\nVocês encontraram {item['nome']} em um baú de tesouro. {jogador['nome']} pegou o item.\n")
    if item["tipo"] == "cura":
        jogador["poções_de_vida"] += 1

def mostrar_inventario(jogador):
    print(f"\nInventário de {jogador['nome']}:")
    for idx, item in enumerate(jogador["inventario"]):
        print(f"{idx + 1}. {item['nome']}")
    print(f"Poções de vida: {jogador['poções_de_vida']}")
    print("\n")

def evento_aleatorio(jogadores):
    evento = random.choice([e for e in eventos_aleatorios if e["tipo"] != "mercador"])
    print(f"\nEvento: {evento['descricao']}\n")
    if evento["tipo"] == "armadilha":
        for jogador in jogadores:
            jogador["vida"] = max(0, jogador["vida"] - 10)
            print(f"{jogador['nome']} perdeu 10 de vida.")
    elif evento["tipo"] == "tesouro":
        for jogador in jogadores:
            loot(monstro=None, jogador=jogador)
    input("\nPressione Enter para continuar...")
    limpar_tela()

def mercador(jogadores):
    for jogador in jogadores:
        print(f"\n{jogador['nome']}, bem-vindo ao mercador!")
        mostrar_inventario(jogador)
        venda = input("Deseja vender itens? (s/n): ").lower()
        if venda == 's':
            while jogador["inventario"]:
                mostrar_inventario(jogador)
                escolha = int(input("Escolha o número do item para vender ou 0 para sair: ")) - 1
                if escolha == -1:
                    break
                item = jogador["inventario"].pop(escolha)
                jogador["ouro"] += item.get("valor", 0)
                print(f"Você vendeu {item['nome']} por {item.get('valor', 0)} ouro.")
            input("\nPressione Enter para continuar...")
            limpar_tela()
        compra = input("Deseja comprar melhorias? (s/n): ").lower()
        if compra == 's':
            while True:
                print("\nMelhorias disponíveis:")
                for i, melhoria in enumerate(melhorias_disponiveis):
                    print(f"{i + 1}. {melhoria['nome']} - {melhoria['valor']} ouro")
                escolha = int(input("Escolha a melhoria para comprar ou 0 para sair: ")) - 1
                if escolha == -1:
                    break
                melhoria = melhorias_disponiveis[escolha]
                if jogador["ouro"] >= melhoria["valor"]:
                    jogador["ouro"] -= melhoria["valor"]
                    jogador[melhoria["atributo"]] += melhoria["bonus"]
                    print(f"{jogador['nome']} comprou {melhoria['nome']} e melhorou {melhoria['atributo']} em {melhoria['bonus']}.")
                else:
                    print("Ouro insuficiente.")
        input("\nPressione Enter para continuar...")
        limpar_tela()

def encontro_monstro(jogadores, semaforo):
    monstro = random.choice(monstros_disponiveis)
    monstro["vida"] = monstro["vida_max"]
    print(f"\nVocês encontraram um {monstro['nome']}! Preparem-se para a batalha!\n")
    while monstro["vida"] > 0 and any(j["vida"] > 0 for j in jogadores):
        for jogador in jogadores:
            if jogador["vida"] > 0:
                acao = acao_jogador(jogador, monstro)
                if acao == '1':
                    realizar_ataque(jogador, monstro, semaforo)
                elif acao == '2':
                    realizar_defesa(jogador)
                elif acao == '3':
                    realizar_cura(jogador)
                elif acao == '4':
                    realizar_especial(jogador, monstro, semaforo)
                jogador["turnos_para_especial"] -= 1
                if jogador["turnos_para_especial"] <= 0:
                    jogador["especial_pronto"] = True
        ataque_monstro(jogadores, monstro)
    if monstro["vida"] == 0:
        print(f"\nVocês derrotaram {monstro['nome']}!\n")
        for jogador in jogadores:
            loot(monstro, jogador)
    else:
        print("\nTodos os jogadores foram derrotados...\n")
    input("\nPressione Enter para continuar...")
    limpar_tela()

def turno_jogador(jogadores, semaforo):
    while True:
        for jogador in jogadores:
            if jogador["vida"] > 0:
                if random.random() < 0.2:
                    evento_aleatorio(jogadores)
                elif random.random() < 0.2:
                    mercador(jogadores)
                else:
                    encontro_monstro(jogadores, semaforo)

# Dados do jogo
armas_disponiveis = [
    {"nome": "Espada Longa", "ataque": 15, "descricao": "Uma espada de longo alcance.", "nome_especial": "Golpe Fatal", "descricao_especial": "Dano massivo a um único inimigo.", "passiva_dobro_ataque": 0.1, "passiva_vida_extra": 0},
    {"nome": "Machado de Guerra", "ataque": 20, "descricao": "Um machado pesado que causa grandes danos.", "nome_especial": "Fúria do Machado", "descricao_especial": "Ataque devastador em todos os inimigos.", "passiva_dobro_ataque": 0.2, "passiva_vida_extra": 0},
    {"nome": "Arco Longo", "ataque": 12, "descricao": "Um arco com flechas afiadas.", "nome_especial": "Chuva de Flechas", "descricao_especial": "Ataque múltiplo que atinge todos os inimigos.", "passiva_dobro_ataque": 0.05, "passiva_vida_extra": 0},
]

itens_disponiveis = [
    {"nome": "Poção de Vida", "tipo": "cura", "valor": 20},
    {"nome": "Espada Curta", "tipo": "arma", "ataque": 10, "valor": 10},
    {"nome": "Escudo de Madeira", "tipo": "defesa", "defesa": 5, "valor": 5},
]

eventos_aleatorios = [
    {"tipo": "armadilha", "descricao": "Vocês caíram em uma armadilha e perderam 10 de vida."},
    {"tipo": "tesouro", "descricao": "Vocês encontraram um baú de tesouro com itens valiosos!"},
]

monstros_disponiveis = [
    {"nome": "Goblin", "vida_max": 30, "vida": 30, "ataque": 9, "defesa": 2},
    {"nome": "Ogro", "vida_max": 50, "vida": 50, "ataque": 12, "defesa": 5},
    {"nome": "Fantasma", "vida_max": 20, "vida": 20, "ataque": 8, "defesa": 7},
    {"nome": "Lobo", "vida_max": 40, "vida": 40, "ataque": 15, "defesa": 2},
    {"nome": "Pertubado", "vida_max": 60, "vida": 60, "ataque": 12, "defesa": 0}
]

melhorias_disponiveis = [
    {"nome": "Aumento de Ataque", "atributo": "ataque", "bonus": 5, "valor": 50},
    {"nome": "Aumento de Defesa", "atributo": "defesa", "bonus": 5, "valor": 40},
    {"nome": "Aumento de Vida", "atributo": "vida_max", "bonus": 10, "valor": 50},
]

# Execução do jogo
def main():
    introducao()
    jogadores = [
        {"nome": "Jogador 1", "vida_max": 100, "vida": 100, "ataque": 10, "defesa": 5, "curas_restantes": 3, "inventario": [], "ouro": 100, "poções_de_vida": 0, "defendendo": False, "arma": None, "especial_pronto": False, "turnos_para_especial": 3},
        {"nome": "Jogador 2", "vida_max": 100, "vida": 100, "ataque": 10, "defesa": 5, "curas_restantes": 3, "inventario": [], "ouro": 100, "poções_de_vida": 0, "defendendo": False, "arma": None, "especial_pronto": False, "turnos_para_especial": 3}
    ]

    for jogador in jogadores:
        escolher_arma(jogador)

    semaforo = threading.Semaphore()
    turno_jogador_thread = threading.Thread(target=turno_jogador, args=(jogadores, semaforo))
    turno_jogador_thread.start()
    turno_jogador_thread.join()

if __name__ == "__main__":
    main()
