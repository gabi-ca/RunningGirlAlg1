import pygame
import sys

# Inicialização do Pygame
pygame.init()

# Configurações da Tela
LARGURA = 800
ALTURA = 400
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Running Girl!")

# Cores
BRANCO = (255, 255, 255)
AZULCEU = (91, 163, 252)
VERMELHO = (255, 0, 0)
AZUL = (0, 0, 255)
VERDECHAO = (37, 227, 36)


# Variáveis do Jogador
jogador_tam = 40                    #tamanho do quadrado do jogador
jogador_x = 100                     #posição horizontal fixa do jogador
jogador_y = ALTURA - jogador_tam    #posição vertical inicial do jogador (no chão)
jogador_y_velocidade = 0            #velocidade vertical do jogador (inicialmente 0)
gravidade = 1.0
esta_no_chao = True

# Variáveis dos Obstáculos (Espinhos)
espinho_x = LARGURA                  #posição horizontal inicial do espinho (fora da tela)
espinho_y = ALTURA - 30              #posição vertical do espinho
espinho_largura = 30                 #largura do espinho  (tbm definem o hitbox do espinho)
espinho_altura = 30                  #altura do espinho   (colisão do espinho)
velocidade_jogo = 8                  #velocidade de movimento do jogo (60fps: 8 pixels por frame = 480 pixels por segundo)

# Controle de FPS
relogio = pygame.time.Clock()        #relogio para controlar a taxa de quadros do jogo (60 FPS)

# Loop Principal do Jogo
while True:
    tela.fill(AZULCEU)

    # Eventos (Pulo e Fechamento)
    for evento in pygame.event.get():    #verifica os eventos do jogo (teclado, mouse, etc.)
        if evento.type == pygame.QUIT:   #se o jogador clicar no "X" da janela, o jogo é fechado
            pygame.quit()
            sys.exit()
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and esta_no_chao:
                jogador_y_velocidade = -15
                esta_no_chao = False

    # Lógica do Jogador (Gravidade)
    jogador_y_velocidade += gravidade         #aplica a gravidade à velocidade vertical do jogador
    jogador_y += jogador_y_velocidade         #atualiza a posição vertical do jogador com base na velocidade
    if jogador_y >= ALTURA - jogador_tam:     #se o jogador atingir ou ultrapassar o chão, ele é reposicionado no chão
        jogador_y = ALTURA - jogador_tam      #e a velocidade é zerada para evitar que o jogador continue caindo
        jogador_y_velocidade = 0
        esta_no_chao = True
    espinhos = [
    {"x": 800},
    {"x": 1100},
    {"x": 1400}
    ]
    
    # Lógica dos Obstáculos
    espinho_x -= velocidade_jogo                            #move o espinho para a esquerda com base na velocidade do jogo
    if espinho_x < -espinho_largura:                        #se o espinho sair completamente da tela
        espinho_x = LARGURA                                 #ele volta para o início da tela

    # Colisões
    jogador_rect = pygame.Rect(jogador_x, jogador_y, jogador_tam, jogador_tam)
    espinho_rect = pygame.Rect(espinho_x, espinho_y, espinho_largura, espinho_altura)

    if jogador_rect.colliderect(espinho_rect):
        print("Game Over!")                     #reinicia a posição do espinho para não travar
        espinho_x = LARGURA 

    # Desenhos na tela
    pygame.draw.rect(tela, AZUL, jogador_rect)                       #jogador
    pygame.draw.polygon(tela, VERMELHO, [
        (espinho_x, espinho_y + espinho_altura), 
        (espinho_x + espinho_largura / 2, espinho_y), 
        (espinho_x + espinho_largura, espinho_y + espinho_altura)
    ])                                                               #espinho
    
    # Chão
    pygame.draw.line(tela, VERDECHAO, (5, ALTURA), (LARGURA, ALTURA), 5) 

    # Atualiza a tela e define taxa de quadros
    pygame.display.flip()
    relogio.tick(60)