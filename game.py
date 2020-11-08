from pathlib import Path

import pygame

MIDIAS = Path("media")

TAMANHO = (800, 600)
LARGURA, ALTURA = TAMANHO
tela = None

TAMANHO_NAVE = 64


class Objeto:

    cor = (255, 255, 255)
    base_image = None
    arquivo_imagem = "NAO EXISTE"

    def __init__(self, x, y, jogo):
        self.x = x
        self.y = y
        self.largura = TAMANHO_NAVE
        self.altura = TAMANHO_NAVE
        self.jogo = jogo
        self.lista = []
        self.carrega_imagem()
        self.cont = 0

    def carrega_imagem(self):
        if self.__class__.base_image:
            self.image = self.__class__.base_image

        caminho = MIDIAS / self.arquivo_imagem
        if not caminho.exists():
            self.image = None
            return
        print(f"Lendo do disco: {caminho}")
        imagem = pygame.image.load(str(caminho))
        self.image = pygame.transform.scale(imagem, (self.largura, self.altura))
        self.image.fill(self.cor, special_flags=pygame.BLEND_ADD)
        self.__class__.base_image = self.image

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)

    def atualiza(self):
        self.cont += 1

    def desenha(self):
        if not self.image:
            pygame.draw.rect(self.jogo.tela, self.cor, (self.x, self.y, self.largura, self.altura))
        else:
            self.jogo.tela.blit(self.image, self.rect)

    def acertado(self, forca):
        self.morrer()

    def morrer(self):
        self.lista.remove(self)


class Nave(Objeto):
    cor = (0, 255, 0)
    arquivo_imagem = "ship.png"

    def __init__(self, x, y, jogo):
        super().__init__(x, y, jogo)
        self.ultimo_tiro = 0
        self.tempo_entre_tiros = 30
        self.maximo_tiros = 3

    def atualiza(self):
        super().atualiza()
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LEFT]:
            self.x -= self.largura // 2
        if teclas[pygame.K_RIGHT]:
            self.x += self.largura // 2

        if teclas[pygame.K_SPACE]:
            if (
                (self.cont - self.ultimo_tiro) > self.tempo_entre_tiros and
                len(self.lista) < self.maximo_tiros
            ):
                tiro = TiroAmigo(self.x, self.y - self.altura, self.jogo)
                self.ultimo_tiro = self.cont

        if self.x < 0:
            self.x = 0
        elif self.x + self.largura > LARGURA:
            self.x = LARGURA - self.largura


class Inimigo(Objeto):
    cor = (192, 0, 0)

    arquivo_imagem = "invader01_00.png"

    def __init__(self, x, y, jogo):
        super().__init__(x, y, jogo)
        self.lista = jogo.inimigos

    def atualiza(self):
        super().atualiza()
        if self.cont % 4 == 0:
            self.x += self.largura // 2
            if self.x + self.largura > LARGURA:
                self.x = 0


class Tiro(Objeto):
    pass

class TiroAmigo(Tiro):
    cont = 0

    def __init__(self, x, y, jogo):

        super().__init__(x, y, jogo)

        self.lista = self.jogo.tiros_da_nave
        self.x += self.largura // 2 - self.largura // 16
        self.largura = self.largura // 8
        self.lista.append(self)

    def atualiza(self):
        super().atualiza()
        if not self.cont % 2:
            self.y -= self.altura // 2
        if self.y <= 0:
            self.morrer()
        for inimigo in self.jogo.inimigos:
            if self.rect.colliderect(inimigo.rect):
                inimigo.acertado(1)

class Jogo:

    def __init__(self):
        self.tela = pygame.display.set_mode(TAMANHO)
        self.pontos = 0

    def principal(self):
        self.nave = Nave(x=LARGURA // 2, y=ALTURA - TAMANHO_NAVE, jogo=self)
        self.inimigos = []
        self.tiros_da_nave = []
        self.tiros_inimigos = []

        total_inimigos = 7

        for i in range(total_inimigos):
            inimigo = Inimigo(
                x = i * (LARGURA / total_inimigos),
                y = TAMANHO_NAVE,
                jogo = self
            )
            self.inimigos.append(inimigo)

        fim_de_jogo = False

        while not fim_de_jogo:

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT or evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    fim_de_jogo = True
                #if evento.type == pygame.KEYDOWN:
                #    atualiza(evento)
            self.nave.atualiza()


            for inimigo in self.inimigos:
                inimigo.atualiza()

            for tiro in self.tiros_da_nave:
                tiro.atualiza()

            self.tela.fill((0, 0, 0))

            self.nave.desenha()
            for inimigo in self.inimigos:
                inimigo.desenha()
            for tiro in self.tiros_da_nave:
                tiro.desenha()

            pygame.display.flip()
            pygame.event.pump()
            pygame.time.delay(30)


jogo = Jogo()
jogo.principal()
pygame.quit()
