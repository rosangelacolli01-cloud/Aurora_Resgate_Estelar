"""Aurora: Resgate Estelar — adaptação da dinâmica de IronManV2.

Instalação: pip install -r requirements.txt
Execução: python main.py
"""
import math
import random
import sys
import threading
from pathlib import Path

import pygame

from recursos.trabalho import maior_pontuador, salvar_pontuacao

# Mantém os arquivos dentro do projeto (inclusive no executável cx_Freeze).
BASE_DIR = Path(__file__).resolve().parent
BASES = BASE_DIR / "bases"
LOG = BASE_DIR / "log.dat"
LARGURA, ALTURA = 1000, 700
FPS = 60
BRANCO = (235, 245, 255)
AZUL = (92, 215, 244)
AMARELO = (255, 220, 80)
FUNDO_PAINEL = (8, 19, 46)


def falar(mensagem):
    """Narra sem travar o loop do Pygame; falhas de áudio não encerram o jogo."""
    def tarefa():
        try:
            import pyttsx3
            sintetizador = pyttsx3.init()
            sintetizador.setProperty("rate", 170)
            sintetizador.say(mensagem)
            sintetizador.runAndWait()
            sintetizador.stop()
        except Exception as erro:
            print("Narração indisponível:", erro)

    threading.Thread(target=tarefa, daemon=True).start()


def imagem(nome, tamanho=None):
    superficie = pygame.image.load(str(BASES / nome)).convert_alpha()
    return pygame.transform.smoothscale(superficie, tamanho) if tamanho else superficie


def texto(tela, fonte, conteudo, x, y, cor=BRANCO, centro=False):
    superficie = fonte.render(str(conteudo), True, cor)
    ret = superficie.get_rect(center=(x, y)) if centro else superficie.get_rect(topleft=(x, y))
    tela.blit(superficie, ret)
    return ret


def painel(tela, ret):
    pygame.draw.rect(tela, FUNDO_PAINEL, ret, border_radius=18)
    pygame.draw.rect(tela, (40, 113, 159), ret, 2, border_radius=18)


def botao(tela, fonte, legenda, ret, mouse):
    sobre = ret.collidepoint(mouse)
    pygame.draw.rect(tela, (38, 157, 204) if sobre else (22, 100, 151), ret, border_radius=14)
    pygame.draw.rect(tela, AZUL, ret, 2, border_radius=14)
    texto(tela, fonte, legenda, ret.centerx, ret.centery, BRANCO, True)


class Jogo:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
            self.audio = True
        except pygame.error:
            self.audio = False
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Aurora: Resgate Estelar")
        pygame.display.set_icon(pygame.image.load(str(BASES / "icone.png")))
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.Font(None, 31)
        self.fonte_p = pygame.font.Font(None, 25)
        self.fonte_g = pygame.font.Font(None, 76)
        self.fundo = imagem("fundo.png", (LARGURA, ALTURA))
        self.nave = imagem("nave.png", (156, 96))
        self.meteoro = imagem("meteoro.png", (83, 73))
        # Pequenas estrelas em primeiro plano criam efeito de profundidade.
        rng = random.Random(420)
        self.estrelas_proximas = [(rng.randrange(LARGURA), rng.randrange(ALTURA), rng.choice((1, 2))) for _ in range(85)]
        self.sonda = imagem("sonda.png", (65, 48))
        self.sons = {}
        if self.audio:
            for chave, nome in (("ponto", "ponto.wav"), ("morte", "colisao.wav")):
                try:
                    self.sons[chave] = pygame.mixer.Sound(str(BASES / nome))
                except pygame.error:
                    pass
        self.nome = ""
        self.estado = "nome"
        self.rodando = True
        self.botao_iniciar = pygame.Rect(365, 525, 270, 65)
        self.botao_reiniciar = pygame.Rect(365, 540, 270, 65)
        self.recorde = maior_pontuador(LOG)
        self.tempo_visual = 0.0
        self.fundo_x = 0.0
        self.reiniciar_variaveis()

    def som(self, chave):
        if chave in self.sons:
            self.sons[chave].play()

    def reiniciar_variaveis(self):
        # Tal como o IronManV2: jogador à esquerda e obstáculos vindos da direita.
        # Apenas a coordenada Y do jogador é modificada durante a partida.
        self.jogador = pygame.Rect(105, 310, 112, 67)
        self.meteoros = [pygame.Rect(1080, random.randint(90, 570), 65, 61)]
        self.segundo_meteoro_ativo = False
        self.velocidade = 270.0
        self.pontos = 0
        self.pausado = False
        self.partida_salva = False
        self.sonda_pos = pygame.Vector2(520, 165)
        self.sonda_vel = pygame.Vector2(65, -37)
        self.tempo_sonda = 0.0
        self.tempo_visual = 0.0
        self.fundo_x = 0.0

    def encerrar_partida(self):
        if self.estado == "jogando" and not self.partida_salva:
            salvar_pontuacao(self.nome, self.pontos, LOG)
            self.partida_salva = True
            self.recorde = maior_pontuador(LOG)

    def sair(self):
        self.encerrar_partida()
        self.rodando = False

    def eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.sair()
                continue
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                self.sair()
                continue
            if self.estado == "nome":
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_RETURN and self.nome.strip():
                        self.nome = self.nome.strip()
                        self.recorde = maior_pontuador(LOG)
                        self.estado = "boas_vindas"
                        falar("Bem-vindo, " + self.nome + ". Prepare-se para desviar dos meteoros!")
                    elif evento.key == pygame.K_BACKSPACE:
                        self.nome = self.nome[:-1]
                    elif evento.unicode.isprintable() and len(self.nome) < 25:
                        self.nome += evento.unicode
            elif self.estado == "boas_vindas":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if self.botao_iniciar.collidepoint(evento.pos):
                        self.reiniciar_variaveis()
                        self.estado = "jogando"
            elif self.estado == "jogando":
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                    self.pausado = not self.pausado
            elif self.estado == "fim":
                if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                    if self.botao_reiniciar.collidepoint(evento.pos):
                        self.reiniciar_variaveis()
                        self.estado = "jogando"

    def atualizar(self, dt):
        # A galáxia se move também nos menus, mas para inteiramente no PAUSE.
        if self.pausado and self.estado == "jogando":
            return
        self.tempo_visual += dt
        self.fundo_x = (self.fundo_x + 52 * dt) % LARGURA
        if self.estado != "jogando":
            return
        teclas = pygame.key.get_pressed()
        direcao = int(teclas[pygame.K_DOWN] or teclas[pygame.K_s]) - int(
            teclas[pygame.K_UP] or teclas[pygame.K_w]
        )
        self.jogador.y += round(direcao * 370 * dt)
        self.jogador.y = max(72, min(ALTURA - 85, self.jogador.y))
        # Cada meteoro desviado avança uma fase (a fase exibida começa em 1).
        # Depois da fase 15, há pelo menos dois meteoros simultaneamente.
        for meteoro in self.meteoros:
            meteoro.x -= round(self.velocidade * dt)
            if meteoro.right < 0:
                meteoro.x = random.randint(1050, 1220)
                meteoro.y = random.randint(90, ALTURA - 115)
                self.pontos += 1
                self.velocidade = min(650.0, self.velocidade + 12)
                self.som("ponto")
        if self.pontos >= 15 and not self.segundo_meteoro_ativo:
            self.segundo_meteoro_ativo = True
            self.meteoros.append(pygame.Rect(1550, random.randint(90, 570), 65, 61))

        # Objeto decorativo: movimento aleatório e SEM qualquer teste de colisão.
        self.tempo_sonda += dt
        if self.tempo_sonda > 1.2:
            self.tempo_sonda = 0.0
            self.sonda_vel = pygame.Vector2(random.randint(-85, 85), random.randint(-60, 60))
        self.sonda_pos += self.sonda_vel * dt
        if not 310 <= self.sonda_pos.x <= 850:
            self.sonda_vel.x *= -1
            self.sonda_pos.x = max(310, min(850, self.sonda_pos.x))
        if not 90 <= self.sonda_pos.y <= 540:
            self.sonda_vel.y *= -1
            self.sonda_pos.y = max(90, min(540, self.sonda_pos.y))

        # Rect.colliderect substitui a interseção manual de listas do IronManV2.
        if any(self.jogador.inflate(-30, -25).colliderect(m.inflate(-18, -15)) for m in self.meteoros):
            self.som("morte")
            self.encerrar_partida()
            self.estado = "fim"
            falar("Fim de jogo. Você fez " + str(self.pontos) + " pontos.")

    def desenhar_fundo(self):
        x = int(self.fundo_x)
        self.tela.blit(self.fundo, (-x, 0))
        self.tela.blit(self.fundo, (LARGURA - x, 0))
        # Estrelas próximas deslocam-se mais rápido que a galáxia (paralaxe).
        for px, py, r in self.estrelas_proximas:
            estrela_x = int((px - self.tempo_visual * (75 + r * 28)) % LARGURA)
            pygame.draw.circle(self.tela, (147, 205, 247), (estrela_x, py), r)
        # Saturno: anéis atrás do planeta e arco frontal sobre a atmosfera.
        saturno = pygame.Surface((150, 100), pygame.SRCALPHA)
        aneis = pygame.Rect(7, 30, 136, 38)
        pygame.draw.ellipse(saturno, (163, 54, 255), aneis, 11)
        pygame.draw.ellipse(saturno, (109, 255, 255), aneis.inflate(-7, -5), 3)
        pygame.draw.ellipse(saturno, (61, 18, 115), aneis.inflate(-16, -10), 2)
        pygame.draw.circle(saturno, (37, 222, 255), (75, 47), 29)
        # Faixas atmosféricas recortadas no disco do planeta.
        for dy in range(-28, 29):
            metade = int(math.sqrt(29 ** 2 - dy ** 2))
            faixa = math.sin(dy * 0.55) * 7
            luz = 1 - (dy + 29) / 125
            cor = tuple(max(0, min(255, int(c * luz + faixa))) for c in (67, 245, 255))
            pygame.draw.line(saturno, cor, (75 - metade, 47 + dy), (75 + metade, 47 + dy))
        pygame.draw.arc(saturno, (163, 54, 255), aneis, math.pi, math.tau, 11)
        pygame.draw.arc(saturno, (177, 255, 255), aneis.inflate(-7, -5), math.pi, math.tau, 3)
        pygame.draw.arc(saturno, (61, 18, 115), aneis.inflate(-16, -10), math.pi, math.tau, 2)
        # Um ciclo de oito segundos: planeta e anéis pulsam juntos.
        escala = 0.88 + 0.12 * math.sin(self.tempo_visual * math.tau / 8)
        saturno = pygame.transform.rotozoom(saturno, -20, escala)
        self.tela.blit(saturno, saturno.get_rect(center=(920, 84)))

    def desenhar_recorde(self, y):
        if self.recorde:
            nome, pontos, data, hora = self.recorde
            texto(self.tela, self.fonte, f"Recorde: {nome} — {pontos} pontos", 500, y, AMARELO, True)
            texto(self.tela, self.fonte_p, f"Partida: {data} às {hora}", 500, y + 35, BRANCO, True)
        else:
            texto(self.tela, self.fonte, "Nenhuma partida registrada ainda", 500, y, AMARELO, True)

    def desenhar(self):
        self.desenhar_fundo()
        if self.estado == "nome":
            painel(self.tela, pygame.Rect(190, 155, 620, 375))
            texto(self.tela, self.fonte_g, "AURORA", 500, 225, AZUL, True)
            texto(self.tela, self.fonte, "RESGATE ESTELAR", 500, 282, BRANCO, True)
            texto(self.tela, self.fonte, "Digite seu nome e pressione ENTER:", 500, 362, BRANCO, True)
            pygame.draw.rect(self.tela, (20, 47, 79), (290, 396, 420, 57), border_radius=10)
            texto(self.tela, self.fonte, self.nome + ("|" if pygame.time.get_ticks() // 500 % 2 else ""), 310, 411)
        elif self.estado == "boas_vindas":
            painel(self.tela, pygame.Rect(110, 100, 780, 515))
            texto(self.tela, self.fonte_g, "BEM-VINDO!", 500, 171, AZUL, True)
            texto(self.tela, self.fonte, f"Piloto: {self.nome}", 500, 240, AMARELO, True)
            texto(self.tela, self.fonte, "Sua nave precisa desviar dos meteoros pelo espaço.", 500, 291, BRANCO, True)
            texto(self.tela, self.fonte, "Use SETA CIMA / BAIXO ou W / S: somente eixo Y.", 500, 332, BRANCO, True)
            texto(self.tela, self.fonte_p, "Avance uma fase a cada meteoro desviado.", 500, 372, BRANCO, True)
            self.desenhar_recorde(422)
            botao(self.tela, self.fonte, "INICIAR PARTIDA", self.botao_iniciar, pygame.mouse.get_pos())
        elif self.estado == "jogando":
            self.tela.blit(self.sonda, self.sonda.get_rect(center=(int(self.sonda_pos.x), int(self.sonda_pos.y))))
            self.tela.blit(self.nave, self.jogador.move(-22, -15))
            for meteoro in self.meteoros:
                self.tela.blit(self.meteoro, meteoro.move(-9, -6))
            texto(self.tela, self.fonte, f"Piloto: {self.nome}", 25, 20)
            texto(self.tela, self.fonte, f"Fase: {self.pontos + 1}", 25, 55, AMARELO)
            texto(self.tela, self.fonte_p, "Pressione ESPAÇO para pausar", 18, ALTURA - 35, (162, 185, 205))
            if self.pausado:
                escurecer = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
                escurecer.fill((4, 9, 25, 185))
                self.tela.blit(escurecer, (0, 0))
                texto(self.tela, self.fonte_g, "jogo pausado", 500, 325, AMARELO, True)
                texto(self.tela, self.fonte, "Pressione ESPAÇO para continuar", 500, 395, BRANCO, True)
        elif self.estado == "fim":
            painel(self.tela, pygame.Rect(170, 125, 660, 500))
            texto(self.tela, self.fonte_g, "FIM DE JOGO", 500, 209, AMARELO, True)
            texto(self.tela, self.fonte, f"{self.nome}, sua pontuação: {self.pontos}", 500, 293, BRANCO, True)
            self.desenhar_recorde(376)
            texto(self.tela, self.fonte_p, "ESC para sair ou jogue novamente", 500, 466, BRANCO, True)
            botao(self.tela, self.fonte, "JOGAR NOVAMENTE", self.botao_reiniciar, pygame.mouse.get_pos())
        pygame.display.flip()

    def executar(self):
        try:
            while self.rodando:
                dt = min(self.relogio.tick(FPS) / 1000.0, 0.05)
                self.eventos()
                if not self.rodando:
                    break
                self.atualizar(dt)
                self.desenhar()
        finally:
            pygame.quit()


if __name__ == "__main__":
    Jogo().executar()
    sys.exit(0)
