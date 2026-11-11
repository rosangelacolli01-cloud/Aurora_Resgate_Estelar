# Aurora: Resgate Estelar

**Projeto da disciplina Pensamento Computacional — professor Marcos Roberto dos Santos.**

## Desenvolvedores e RAs
- **[Rosangela Colli]** — RA: **[1140142]**
- **[Julia Buffon]** — RA: **[1140323]**

> Preencher com os dados verdadeiros da dupla antes de entregar.

## História e mecânica
Em uma região distante do espaço, a piloto da nave **Aurora** precisa atravessar um campo de meteoros e manter a missão de resgate em andamento. A nave fica no lado esquerdo da tela e se desloca **apenas verticalmente (eixo Y)**. Meteoros atravessam o espaço: a cada meteoro evitado, o jogador recebe um ponto e avança uma fase; após a fase 15, aparecem dois meteoros simultaneamente. Uma colisão encerra a partida. Uma pequena sonda faz movimentos aleatórios apenas como enfeite, enquanto uma estrela amarela pulsa no céu.

A dinâmica de jogador + obstáculos horizontais e o ciclo início/jogo/fim foram adaptados da referência [IronManV2](https://github.com/profmarcossantos/IronManV2), com cenário de galáxia em movimento e paralaxe, nave detalhada, sprites, efeitos sonoros, interface e tema substituídos por recursos originais.

## Tecnologias
- **Python 3.10+** — programação e arquivos padrão (`pathlib`, `datetime`, `math`, `random`, `threading`).
- **Pygame 2** — janela, gráficos, eventos, controles, colisões, áudio e FPS.
- **pyttsx3** — narração local de boas-vindas e fim da partida.
- **cx_Freeze** — geração do executável por `python setup.py build`.
- **Pillow (somente na preparação dos PNGs)** — os assets já estão gerados em `bases/`; **não é necessária** para executar o jogo.

## Instalação e execução
Na pasta do projeto, execute:

```bash
python -m pip install -r requirements.txt
python main.py
```

Digite seu nome na janela e pressione **ENTER**. Na tela seguinte, clique no **único botão INICIAR PARTIDA**. A janela não possui um botão próprio de fechar; use o X padrão do sistema.

### Comandos
- **↑ / ↓** ou **W / S**: mover a nave exclusivamente para cima e para baixo.
- **ESPAÇO**: pausar/retomar; a pausa congela movimentos e animações.
- **Fases**: cada meteoro desviado vale 1 ponto; após passar da fase 15 surgem dois meteoros na tela.
- **ESC**: encerrar o aplicativo em qualquer tela.
- **X da janela**: encerrar o aplicativo.

A pontuação é registrada ao ocorrer a colisão e também se o jogador encerrar uma partida em andamento. O arquivo `log.dat` é criado automaticamente na raiz e cada linha tem `Nome;Pontos;DD/MM/AAAA;HH:MM:SS`. O recorde é lido desse arquivo na tela de boas-vindas e na de fim de jogo. Em caso de empate, vence a primeira pontuação registrada. Não há registro duplicado para a mesma partida.

A voz utiliza o mecanismo instalado no sistema. Se o ambiente não tiver um mecanismo de voz compatível, o jogo continua normalmente.

## Gerar executável

```bash
python setup.py build
```

O executável será criado na pasta `build/`, dentro de um subdiretório identificado pela plataforma. **Execute o aplicativo preservando os arquivos da pasta `bases/` que acompanham o build.** É necessário gerar o build no sistema operacional de destino (Windows para `.exe` Windows). A pasta `build/` deve ser incluída no commit final, conforme solicitado pelo professor. O resultado do build depende de `cx_Freeze` e do ambiente local; não é um executável pré-compilado incluído neste ZIP.

## Organização
```text
Aurora_Resgate_Estelar/
├── main.py
├── setup.py
├── requirements.txt
├── README.md
├── .gitignore
├── bases/
│   ├── fundo.png
│   ├── nave.png
│   ├── meteoro.png
│   ├── sonda.png
│   ├── icone.png
│   ├── ponto.wav
│   └── colisao.wav
└── recursos/
    ├── __init__.py
    └── trabalho.py
```

## Histórico sugerido de 5 commits (criar de verdade via Git)

1. `feat: iniciar projeto Aurora com estrutura e assets originais`
2. `feat: implementar tela de nome e boas-vindas com recorde`
3. `feat: adicionar movimento vertical, meteoros e pontuação`
4. `feat: implementar pausa, sonda decorativa, estrela pulsante e voz`
5. `feat: registrar partidas, finalizar README e incluir executável build`

> O ZIP contém o projeto final, **não um histórico Git fabricado**. Para atender à avaliação, esses commits precisam ser realizados enquanto desenvolvem as etapas, em versões progressivas reais. A dupla deve compartilhar o GitHub com `profmarcossantos` (ou `marcos.santos@atitus.edu.br`) e com um colega, que deverá fazer seu próprio commit.
