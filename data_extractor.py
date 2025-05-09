import os
import pytesseract
import re
import pandas as pd
from PIL import Image
from PIL import Image

# Caminho do Tesseract (ajuste se necessário)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Função para processar uma imagem e extrair os dados
def extrair_km_por_zona(caminho_img):
        imagem = Image.open(caminho_img)

        # Recorte aproximado da região central onde aparece o número dos km
        largura, altura = imagem.size
        box = (
            largura * 0.35,  # esquerda
            altura * 0.20,   # topo
            largura * 0.65,  # direita
            altura * 0.35    # base
        )
        recorte_km = imagem.crop(box)

        texto_km = pytesseract.image_to_string(recorte_km, config='--psm 6')

        # Usa regex para encontrar decimal com ponto
        match = re.search(r'\d+\.\d+', texto_km)
        if match:
            return match.group()
        return ''

def extrair_dados(caminho_img):
    imagem = Image.open(caminho_img)
    texto = pytesseract.image_to_string(imagem, lang='eng')
    linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]

    dados = {
        'DataHora': '',
        'Distancia_km': '',
        'Ritmo_medio': '',
        'Tempo': '',
        'Calorias': '',
        'Passos': '',
        'Cadencia': '',
        'Passada': '',
        'Arquivo': os.path.basename(caminho_img)
    }

    try:
        # 1. Data e hora
        for linha in linhas:
            if "Corrida" in linha:
                partes = linha.split()
                if len(partes) >= 2:
                    dados['DataHora'] = f"{partes[0]} {partes[1]}"
                break

        dados["Distancia_km"] = extrair_km_por_zona(caminho_img)               

        # 2. Ritmo, tempo, calorias
        for linha in linhas:
            if "'" in linha or '"' in linha:
                partes = linha.split()
                if len(partes) >= 3:
                    dados['Ritmo_medio'] = partes[0]
                    dados['Tempo'] = partes[1]
                    dados['Calorias'] = partes[2]
                break

        # 3. Passos, cadência, passada
        for linha in linhas:
            partes = linha.split()
            if len(partes) == 3 and partes[0].isdigit():
                dados['Passos'] = partes[0]
                dados['Cadencia'] = partes[1]
                dados['Passada'] = partes[2]
                break

    except Exception as e:
        print(f"Erro ao processar {caminho_img}: {e}")

    return dados

# Função principal para atualizar a planilha incrementalmente
def atualizar_planilha(diretorio='./imagens_corrida', saida_csv='resultados_corrida.csv', saida_excel='resultados_corrida.xlsx'):
    # Carrega dados anteriores (se houver)
    if os.path.exists(saida_csv):
        df_existente = pd.read_csv(saida_csv)
    else:
        df_existente = pd.DataFrame()

    # Processa novas imagens
    novos_resultados = []
    arquivos_processados = set(df_existente['Arquivo']) if not df_existente.empty else set()

    for nome_arquivo in os.listdir(diretorio):
        if nome_arquivo.lower().endswith(('.jpg', '.jpeg', '.png')) and nome_arquivo not in arquivos_processados:
            caminho = os.path.join(diretorio, nome_arquivo)
            dados = extrair_dados(caminho)
            novos_resultados.append(dados)

    # Combina os dados antigos com os novos
    if novos_resultados:
        df_novo = pd.DataFrame(novos_resultados)
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)
        df_final.to_csv(saida_csv, index=False)
        df_final.to_excel(saida_excel, index=False)
        print(f"✅ {len(novos_resultados)} novas imagens processadas.")
    else:
        print("ℹ️ Nenhuma nova imagem encontrada.")

# Chamada principal
if __name__ == '__main__':
    atualizar_planilha()
