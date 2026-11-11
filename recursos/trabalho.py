"""Funções auxiliares do projeto Aurora: Resgate Estelar."""
from datetime import datetime
from pathlib import Path


def salvar_pontuacao(nome, pontos, arquivo="log.dat"):
    """Registra uma partida em arquivo texto e retorna o registro salvo."""
    agora = datetime.now()
    nome = " ".join(str(nome).replace(";", " ").split())[:35] or "Anônimo"
    registro = (nome, int(pontos), agora.strftime("%d/%m/%Y"), agora.strftime("%H:%M:%S"))
    caminho = Path(arquivo)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("a", encoding="utf-8") as f:
        f.write(";".join(map(str, registro)) + "\n")
    return registro


def maior_pontuador(arquivo="log.dat"):
    """Retorna (nome, pontos, data, hora), ignorando linhas inválidas."""
    campeao = None
    caminho = Path(arquivo)
    if not caminho.exists():
        return None
    with caminho.open("r", encoding="utf-8") as f:
        for linha in f:
            partes = linha.strip().split(";")
            if len(partes) != 4:
                continue
            nome, pontos, data, hora = partes
            try:
                pontos = int(pontos)
                datetime.strptime(data + " " + hora, "%d/%m/%Y %H:%M:%S")
            except ValueError:
                continue
            if campeao is None or pontos > campeao[1]:
                campeao = (nome, pontos, data, hora)
    return campeao
