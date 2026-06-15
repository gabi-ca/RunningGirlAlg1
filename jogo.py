import pygame    #biblioteca principal do jogo
import sys       #para lidar com o fechamento da janela
import random    #para gerar obstáculos de forma aleatória
import os        #para trabalhar com arquivos e pastas, caminhos do sistema

'''Inicialização do Pygame'''
pygame.init()

'''Configurações da Tela'''
LARGURA = 800
ALTURA = 400
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Running Girl!")

'''Geometria do chão'''
ALTURA_GRAMA = 15
ALTURA_SOLO = 48
ALTURA_CHAO_TOTAL = ALTURA_GRAMA + ALTURA_SOLO
PISO = ALTURA - ALTURA_CHAO_TOTAL
ALTURA_AGUA = 10

'''Cores básicas'''
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZULCEU = (91, 163, 252)
VERDECHAO = (37, 227, 36)
SOLO_MARROM = (101, 67, 33)
AGUA_AZUL = (60, 140, 230)

'''Paleta do castelo (reino encantado)'''
CASTELO_LILAS = (180, 160, 220)
CASTELO_LILAS_ESC = (140, 120, 180)
CASTELO_TELHADO = (230, 140, 190)
BANDEIRA_VERMELHA = (230, 70, 90)

'''Posição dos castelos ao fundo (camada repetida em paralaxe)'''
CASTELO_Y_BASE = PISO - 110
CASTELO_TILE_LARGURA = 200

'''Paleta das árvores'''
TRONCO_MARROM = (120, 80, 50)
TRONCO_MARROM_ESC = (90, 58, 35)
COPA_VERDE_CLARO = (90, 200, 90)
COPA_VERDE_ESCURO = (50, 150, 60)

'''Paleta dos obstáculos'''
ESPINHO_ROXO = (160, 40, 200)
ESPINHO_ROXO_ESC = (110, 20, 150)
CAIXA_MARROM = (139, 94, 60)
CAIXA_MARROM_ESC = (94, 60, 38)
CAIXA_DETALHE = (210, 170, 110)
PASSARINHO_CORPO = (250, 140, 70)
PASSARINHO_CORPO_ESC = (200, 95, 40)
PASSARINHO_BARRIGA = (255, 230, 180)
PASSARINHO_BICO = (255, 210, 50)

'''Fontes'''
fonte_pontuacao = pygame.font.Font("fontefofa.ttf", 28)
fonte_titulo = pygame.font.Font("fontefofa.ttf", 48)
fonte_texto = pygame.font.Font("fontefofa.ttf", 24)
fonte_velocidade = pygame.font.Font("fontefofa.ttf", 18)

'''Sprite do jogador (de pé e agachado)'''
CAMINHO_BASE = os.path.dirname(os.path.abspath(__file__))
sprite_original = pygame.image.load(os.path.join(CAMINHO_BASE, "player.png")).convert_alpha()

SPRITE_TAM = 60
sprite_jogador = pygame.transform.scale(sprite_original, (SPRITE_TAM, SPRITE_TAM))
sprite_jogador_agachado = pygame.transform.scale(sprite_original, (SPRITE_TAM, SPRITE_TAM // 2))

'''Geometria do obstáculo "passarinho" (pode ser evitado agachando ou pulando)'''
PASSARINHO_ALTURA = 24
PASSARINHO_LARGURA = 36
PASSARINHO_Y = PISO - 56

'''Overlay escuro usado na tela de Game Over'''
overlay_game_over = pygame.Surface((LARGURA, ALTURA))
overlay_game_over.set_alpha(150)
overlay_game_over.fill(PRETO)

'''Variáveis do Jogador'''
jogador_x = 100             # posição horizontal fixa do jogador
gravidade = 1.0
PULO_FORCA = -15

'''Configuração da dificuldade progressiva'''
VELOCIDADE_INICIAL = 5.0
VELOCIDADE_MAX = 16.0
INCREMENTO_POR_FAIXA = 0.5
FAIXA_PONTOS = 1000

'''Margem para evitar que obstáculos de chão e trechos de água surjam sobrepostos'''
MARGEM_SEGURANCA = 60

'''Distância extra somada ao próximo obstáculo de chão logo após um trecho de água'''
EXTRA_APOS_AGUA = 80

'''Controle de FPS'''
relogio = pygame.time.Clock()


def hitbox_jogador():
    #de pé: inset de 6px no sprite (acompanha melhor o contorno do personagem);
    #agachado: metade da altura, rente ao chão
    if esta_agachado:
        return pygame.Rect(jogador_x + 6, PISO - (SPRITE_TAM // 2) + 3, SPRITE_TAM - 12, (SPRITE_TAM // 2) - 6)
    return pygame.Rect(jogador_x + 6, int(jogador_y) + 6, SPRITE_TAM - 12, SPRITE_TAM - 12)


def hitbox_obstaculo(obs):
    #caixas de colisão menores que o retângulo de desenho, acompanhando a
    #forma visível de cada obstáculo (o espinho é um triângulo, por exemplo)
    x, y = int(obs["x"]), obs["y"]
    largura, altura = obs["largura"], obs["altura"]
    if obs["tipo"] == "espinho":
        return pygame.Rect(x + 5, y + 10, largura - 10, altura - 10)
    elif obs["tipo"] == "bloco":
        return pygame.Rect(x + 2, y + 2, largura - 4, altura - 4)
    else:  # passarinho
        return pygame.Rect(x + 4, y + 4, largura - 8, altura - 8)


def desenhar_jogador():
    if esta_agachado:
        tela.blit(sprite_jogador_agachado, (jogador_x, PISO - SPRITE_TAM // 2))
    else:
        tela.blit(sprite_jogador, (jogador_x, int(jogador_y)))


def gerar_obstaculo(x):
    tipo = random.choice(["espinho", "bloco", "passarinho"])
    if tipo == "espinho":
        return {"tipo": tipo, "x": float(x), "y": PISO - 30, "largura": 30, "altura": 30}
    elif tipo == "bloco":
        return {"tipo": tipo, "x": float(x), "y": PISO - 60, "largura": 36, "altura": 60}
    else:  # passarinho: voa na altura do tronco do jogador, pode ser evitado agachando ou pulando
        return {"tipo": tipo, "x": float(x), "y": PASSARINHO_Y, "largura": PASSARINHO_LARGURA, "altura": PASSARINHO_ALTURA}


def desenhar_obstaculo(obs):
    x, y = int(obs["x"]), obs["y"]
    largura, altura = obs["largura"], obs["altura"]

    if obs["tipo"] == "espinho":
        pygame.draw.polygon(tela, ESPINHO_ROXO_ESC, [
            (x - 2, y + altura), (x + largura / 2, y - 2), (x + largura + 2, y + altura)
        ])
        pygame.draw.polygon(tela, ESPINHO_ROXO, [
            (x, y + altura), (x + largura / 2, y), (x + largura, y + altura)
        ])

    elif obs["tipo"] == "bloco":
        pygame.draw.rect(tela, CAIXA_MARROM_ESC, (x, y, largura, altura))
        pygame.draw.rect(tela, CAIXA_MARROM, (x + 3, y + 3, largura - 6, altura - 6))
        pygame.draw.line(tela, CAIXA_MARROM_ESC, (x + 3, y + 3), (x + largura - 3, y + altura - 3), 3)
        pygame.draw.line(tela, CAIXA_MARROM_ESC, (x + largura - 3, y + 3), (x + 3, y + altura - 3), 3)
        for canto in [(x + 5, y + 5), (x + largura - 5, y + 5), (x + 5, y + altura - 5), (x + largura - 5, y + altura - 5)]:
            pygame.draw.circle(tela, CAIXA_DETALHE, canto, 2)

    else:  # passarinho: ave em pixel art - pode ser evitada agachando ou pulando
        cy = y + altura // 2

        # cauda (penas traseiras, lado direito - sentido do voo)
        pygame.draw.polygon(tela, PASSARINHO_CORPO_ESC, [
            (x + largura - 8, y + 6), (x + largura, y + 2), (x + largura, y + 14), (x + largura - 8, y + altura - 4)
        ])

        # corpo (sombra por baixo, corpo claro por cima, peito)
        pygame.draw.ellipse(tela, PASSARINHO_CORPO_ESC, (x + 8, y + 6, largura - 12, altura - 6))
        pygame.draw.ellipse(tela, PASSARINHO_CORPO, (x + 6, y + 4, largura - 12, altura - 8))
        pygame.draw.ellipse(tela, PASSARINHO_BARRIGA, (x + 10, cy, largura - 20, altura // 2 - 2))

        # asa batendo (alterna posição para dar sensação de voo)
        if (pygame.time.get_ticks() // 100) % 2 == 0:
            pontos_asa = [(x + 14, y + 8), (x + 24, y), (x + 24, y + 10)]
        else:
            pontos_asa = [(x + 14, y + 10), (x + 24, y + 14), (x + 24, y + altura)]
        pygame.draw.polygon(tela, PASSARINHO_CORPO_ESC, pontos_asa)

        # bico apontando para a frente do voo (esquerda)
        pygame.draw.polygon(tela, PASSARINHO_BICO, [
            (x + 6, cy - 3), (x + 6, cy + 3), (x - 2, cy)
        ])

        # olho
        pygame.draw.circle(tela, PRETO, (x + 12, cy - 2), 2)


def calcular_gap(velocidade):
    fator = velocidade / VELOCIDADE_INICIAL
    return int(300 * fator), int(500 * fator)


def calcular_gap_agua(velocidade):
    fator = velocidade / VELOCIDADE_INICIAL
    return int(800 * fator), int(1250 * fator)


def atualizar_velocidade(pontos):
    incrementos = pontos // FAIXA_PONTOS
    return min(VELOCIDADE_INICIAL + incrementos * INCREMENTO_POR_FAIXA, VELOCIDADE_MAX)


def desenhar_camada_repetida(desenhar_tile, offset, tile_largura, y_base):
    x = -offset
    while x < LARGURA:
        desenhar_tile(x, y_base)
        x += tile_largura


def desenhar_tile_castelo(x, y_base):
    # torres laterais com telhado cônico e bandeira
    for tx in (x + 20, x + 220):
        pygame.draw.rect(tela, CASTELO_LILAS, (tx, y_base, 30, 110))
        pygame.draw.rect(tela, CASTELO_LILAS_ESC, (tx + 24, y_base, 6, 110))
        pygame.draw.polygon(tela, CASTELO_TELHADO, [(tx - 5, y_base), (tx + 15, y_base - 25), (tx + 35, y_base)])
        pygame.draw.line(tela, BANDEIRA_VERMELHA, (tx + 15, y_base - 25), (tx + 15, y_base - 35), 2)
        pygame.draw.polygon(tela, BANDEIRA_VERMELHA, [(tx + 15, y_base - 35), (tx + 28, y_base - 31), (tx + 15, y_base - 27)])

    # torre central
    pygame.draw.rect(tela, CASTELO_LILAS, (x + 110, y_base + 10, 60, 100))
    pygame.draw.polygon(tela, CASTELO_TELHADO, [(x + 105, y_base + 10), (x + 140, y_base - 20), (x + 175, y_base + 10)])
    pygame.draw.line(tela, BANDEIRA_VERMELHA, (x + 140, y_base - 20), (x + 140, y_base - 32), 2)
    pygame.draw.polygon(tela, BANDEIRA_VERMELHA, [(x + 140, y_base - 32), (x + 154, y_base - 28), (x + 140, y_base - 24)])

    # janelas
    for wx in (x + 122, x + 150):
        pygame.draw.rect(tela, CASTELO_LILAS_ESC, (wx, y_base + 40, 8, 12))


def desenhar_tile_arvore(x, y_base):
    cx = x + 100
    pygame.draw.rect(tela, TRONCO_MARROM, (cx - 10, y_base - 40, 20, 40))
    pygame.draw.rect(tela, TRONCO_MARROM_ESC, (cx + 6, y_base - 40, 4, 40))

    pygame.draw.rect(tela, COPA_VERDE_ESCURO, (cx - 30, y_base - 70, 60, 25))
    pygame.draw.rect(tela, COPA_VERDE_CLARO, (cx - 22, y_base - 78, 44, 25))
    pygame.draw.rect(tela, COPA_VERDE_ESCURO, (cx - 15, y_base - 95, 30, 22))


def desenhar_segmentos_agua():
    for seg in segmentos_agua:
        x, largura = int(seg["x"]), int(seg["largura"])
        pygame.draw.rect(tela, AZULCEU, (x, PISO, largura, ALTURA_CHAO_TOTAL))
        pygame.draw.rect(tela, AGUA_AZUL, (x, ALTURA - ALTURA_AGUA, largura, ALTURA_AGUA))


def desenhar_fundo():
    tela.fill(AZULCEU)
    desenhar_camada_repetida(desenhar_tile_castelo, scroll_castelos, CASTELO_TILE_LARGURA, CASTELO_Y_BASE)
    desenhar_camada_repetida(desenhar_tile_arvore, scroll_arvores, 200, PISO)
    pygame.draw.rect(tela, VERDECHAO, (0, PISO, LARGURA, ALTURA_GRAMA))
    pygame.draw.rect(tela, SOLO_MARROM, (0, PISO + ALTURA_GRAMA, LARGURA, ALTURA_SOLO))
    desenhar_segmentos_agua()


def desenhar_pontuacao():
    texto_sombra = fonte_pontuacao.render(f"Pontos: {int(pontuacao)}", True, PRETO)
    tela.blit(texto_sombra, (11, 11))
    texto = fonte_pontuacao.render(f"Pontos: {int(pontuacao)}", True, BRANCO)
    tela.blit(texto, (10, 10))

    vel_sombra = fonte_velocidade.render(f"Velocidade: {velocidade_jogo:.1f}", True, PRETO)
    tela.blit(vel_sombra, (11, 45))
    vel_texto = fonte_velocidade.render(f"Velocidade: {velocidade_jogo:.1f}", True, BRANCO)
    tela.blit(vel_texto, (10, 44))


def desenhar_tela_inicio():
    desenhar_fundo()
    tela.blit(overlay_game_over, (0, 0))

    titulo = fonte_titulo.render("Running Girl!", True, BRANCO)
    tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 100)))

    inicio_msg = fonte_texto.render("Pressione ESPAÇO para começar", True, BRANCO)
    tela.blit(inicio_msg, inicio_msg.get_rect(center=(LARGURA // 2, ALTURA // 2 - 50)))

    linhas = [
        "ESPAÇO: pular espinhos e caixas",
        "ESPAÇO (2x no ar): salto duplo para atravessar a água",
        "SETA BAIXO / S ou ESPAÇO: agache ou pule para evitar o passarinho",
    ]
    for i, linha in enumerate(linhas):
        texto = fonte_texto.render(linha, True, BRANCO)
        tela.blit(texto, texto.get_rect(center=(LARGURA // 2, ALTURA // 2 + i * 30)))


def desenhar_tela_game_over():
    tela.blit(overlay_game_over, (0, 0))

    titulo = fonte_titulo.render("GAME OVER", True, BRANCO)
    tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 40)))

    pontos = fonte_texto.render(f"Pontuação final: {int(pontuacao)}", True, BRANCO)
    tela.blit(pontos, pontos.get_rect(center=(LARGURA // 2, ALTURA // 2 + 10)))

    instrucao = fonte_texto.render("Pressione R para reiniciar", True, BRANCO)
    tela.blit(instrucao, instrucao.get_rect(center=(LARGURA // 2, ALTURA // 2 + 45)))


def reiniciar_jogo():
    global jogador_y, jogador_y_velocidade, esta_no_chao, esta_agachado, pulo_duplo_usado
    global obstaculos, distancia_proximo_obstaculo
    global segmentos_agua, distancia_proximo_agua
    global velocidade_jogo, pontuacao
    global scroll_arvores
    global scroll_castelos
    global estado_jogo

    jogador_y = float(PISO - SPRITE_TAM)
    jogador_y_velocidade = 0.0
    esta_no_chao = True
    esta_agachado = False
    pulo_duplo_usado = False

    obstaculos = []
    distancia_proximo_obstaculo = 400

    segmentos_agua = []
    distancia_proximo_agua = 700

    velocidade_jogo = VELOCIDADE_INICIAL
    pontuacao = 0.0

    scroll_arvores = 0.0
    scroll_castelos = 0.0

    estado_jogo = "jogando"


'''Inicialização do estado do jogo'''
reiniciar_jogo()
estado_jogo = "inicio"

'''Loop Principal do Jogo'''
while True:
    '''Eventos (Pulo, Reinício e Fechamento)'''
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if estado_jogo == "inicio":
                if evento.key == pygame.K_SPACE:
                    reiniciar_jogo()
            elif estado_jogo == "jogando":
                if evento.key == pygame.K_SPACE and not esta_agachado:
                    if esta_no_chao:
                        jogador_y_velocidade = PULO_FORCA
                        esta_no_chao = False
                        pulo_duplo_usado = False
                    elif not pulo_duplo_usado:
                        jogador_y_velocidade = PULO_FORCA
                        pulo_duplo_usado = True
            elif estado_jogo == "game_over":
                if evento.key == pygame.K_r:
                    reiniciar_jogo()

    if estado_jogo == "jogando":
        '''Agachar: seta para baixo ou tecla S, só funciona no chão'''
        teclas = pygame.key.get_pressed()
        esta_agachado = (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) and esta_no_chao

        '''Lógica do Jogador (Gravidade)'''
        jogador_y_velocidade += gravidade
        jogador_y += jogador_y_velocidade
        if jogador_y >= PISO - SPRITE_TAM:
            sobre_agua = any(
                seg["x"] < jogador_x + SPRITE_TAM and seg["x"] + seg["largura"] > jogador_x
                for seg in segmentos_agua
            )
            if not sobre_agua:
                jogador_y = PISO - SPRITE_TAM
                jogador_y_velocidade = 0
                esta_no_chao = True
                pulo_duplo_usado = False

        '''Lógica dos Obstáculos: move, remove os que saíram da tela e cria novos'''
        for obs in obstaculos:
            obs["x"] -= velocidade_jogo
        obstaculos = [o for o in obstaculos if o["x"] + o["largura"] > 0]

        distancia_proximo_obstaculo -= velocidade_jogo
        if distancia_proximo_obstaculo <= 0:
            sobrepoe_agua = any(
                s["x"] < LARGURA + MARGEM_SEGURANCA and s["x"] + s["largura"] > LARGURA - MARGEM_SEGURANCA
                for s in segmentos_agua
            )
            if sobrepoe_agua:
                distancia_proximo_obstaculo = MARGEM_SEGURANCA
            else:
                obstaculos.append(gerar_obstaculo(LARGURA))
                gap_min, gap_max = calcular_gap(velocidade_jogo)
                distancia_proximo_obstaculo = random.randint(gap_min, gap_max)

        '''Lógica dos segmentos de água: move, remove os que saíram da tela e cria novos'''
        for seg in segmentos_agua:
            seg["x"] -= velocidade_jogo
        segmentos_agua = [s for s in segmentos_agua if s["x"] + s["largura"] > 0]

        distancia_proximo_agua -= velocidade_jogo
        if distancia_proximo_agua <= 0:
            sobrepoe_obstaculo = any(
                o["x"] < LARGURA + MARGEM_SEGURANCA and o["x"] + o["largura"] > LARGURA - MARGEM_SEGURANCA
                for o in obstaculos
            )
            if sobrepoe_obstaculo:
                distancia_proximo_agua = MARGEM_SEGURANCA
            else:
                largura_agua = velocidade_jogo * random.uniform(38, 46)
                segmentos_agua.append({"x": float(LARGURA), "largura": largura_agua})
                gap_min, gap_max = calcular_gap_agua(velocidade_jogo)
                distancia_proximo_agua = random.randint(gap_min, gap_max)
                # Garante que o próximo obstáculo de chão não surja muito perto da água
                distancia_proximo_obstaculo += EXTRA_APOS_AGUA

        '''Pontuação e dificuldade progressiva'''
        pontuacao += velocidade_jogo
        velocidade_jogo = atualizar_velocidade(pontuacao)

        '''Rolagem do cenário (paralaxe)'''
        scroll_arvores = (scroll_arvores + velocidade_jogo * 0.5) % 200
        scroll_castelos = (scroll_castelos + velocidade_jogo * 0.2) % CASTELO_TILE_LARGURA

        '''Colisões'''
        jogador_rect = hitbox_jogador()
        for obs in obstaculos:
            if jogador_rect.colliderect(hitbox_obstaculo(obs)):
                estado_jogo = "game_over"

        # Colisão com a água: game over apenas ao tocar a faixa azul na base da tela
        if jogador_rect.bottom >= ALTURA - ALTURA_AGUA:
            for seg in segmentos_agua:
                if jogador_rect.right > seg["x"] and jogador_rect.left < seg["x"] + seg["largura"]:
                    estado_jogo = "game_over"

    '''Desenhos na tela'''
    if estado_jogo == "inicio":
        desenhar_tela_inicio()
    else:
        desenhar_fundo()
        for obs in obstaculos:
            desenhar_obstaculo(obs)
        desenhar_jogador()
        desenhar_pontuacao()

        if estado_jogo == "game_over":
            desenhar_tela_game_over()

    '''Atualiza a tela e define taxa de quadros'''
    pygame.display.flip()
    relogio.tick(60)