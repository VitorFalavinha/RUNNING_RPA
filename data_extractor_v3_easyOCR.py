import easyocr
import pandas as pd
import os

# Inicializa o leitor do EasyOCR
reader = easyocr.Reader(['pt'])

# Pasta com as imagens
pasta_imagens = 'imagens_corrida'

# Caminhos dos arquivos de saída
ARQUIVO_CSV = "corridas.csv"
ARQUIVO_XLSX = "corridas.xlsx"

# Função para processar uma imagem
def extrair_dados_ocr(caminho_imagem, nome_arquivo):
    results = reader.readtext(caminho_imagem)
    textos = [text for (_, text, _) in results]

    try:
        dados = {
            "arquivo": nome_arquivo,
            "data_hora": textos[0].split(" Corrida")[0].replace('.', ':'),
            "atividade": "Corrida",
            "distancia_km": float(textos[1]),
            "ritmo_medio": textos[3],
            "tempo_usado": textos[4].replace('.', ':'),
            "calorias_kcal": float(textos[5]),
            "passos": int(textos[9]),
            "cadencia_media_step_min": int(textos[10]),
            "passada_media_cm": int(textos[11])
        }
        return dados
    except Exception as e:
        print(f"Erro ao processar {nome_arquivo}: {e}")
        return None

# Carrega dados anteriores, se existirem
if os.path.exists(ARQUIVO_CSV):
    df_existente = pd.read_csv(ARQUIVO_CSV)
    if 'arquivo' not in df_existente.columns:
        df_existente['arquivo'] = None  # garante a existência da coluna
    arquivos_processados = set(df_existente['arquivo'].dropna().tolist())
else:
    df_existente = pd.DataFrame(columns=['arquivo'])
    arquivos_processados = set()

# Lista para armazenar os novos dados
novos_dados = []

# Processa apenas imagens ainda não registradas
for nome_arquivo in os.listdir(pasta_imagens):
    if nome_arquivo.lower().endswith(('.jpg', '.jpeg', '.png')) and nome_arquivo not in arquivos_processados:
        caminho = os.path.join(pasta_imagens, nome_arquivo)
        dados = extrair_dados_ocr(caminho, nome_arquivo)
        if dados:
            novos_dados.append(dados)

# Se houver novos dados, atualiza os arquivos
if novos_dados:
    df_novos = pd.DataFrame(novos_dados)
    df_total = pd.concat([df_existente, df_novos], ignore_index=True)
    df_total.to_csv(ARQUIVO_CSV, index=False, encoding='utf-8')
    df_total.to_excel(ARQUIVO_XLSX, index=False, engine='openpyxl')
    print(f"{len(novos_dados)} novas corridas adicionadas.")
else:
    print("Nenhuma nova imagem detectada. Arquivos mantidos inalterados.")
