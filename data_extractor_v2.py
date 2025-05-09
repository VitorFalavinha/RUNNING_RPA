import os
import pytesseract
import re
import pandas as pd
from PIL import Image, ImageEnhance, ImageFilter

# Caminho do Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- Funcoes auxiliares ---
def preprocessar_imagem(imagem):
    imagem = imagem.convert('L')  # escala de cinza
    imagem = imagem.filter(ImageFilter.MedianFilter())
    enhancer = ImageEnhance.Contrast(imagem)
    imagem = enhancer.enhance(2)  # aumenta contraste
    return imagem

def formatar_ritmo(ritmo_str):
    match = re.search(r'(\d{1,2})[\'\u00B0\s]?(\d{2})[\"”]?', ritmo_str)
    if match:
        minutos, segundos = match.groups()
        return f"{int(minutos):02}:{int(segundos):02}"
    elif re.fullmatch(r'\d{4}', ritmo_str):
        return f"{ritmo_str[:2]}:{ritmo_str[2:]}"
    return None

def inferir_ritmo(tempo_str, distancia):
    try:
        h, m, s = [int(t) for t in tempo_str.split(':')]
        total_seg = h * 3600 + m * 60 + s
        ritmo_seg = total_seg / float(distancia)
        return f"{int(ritmo_seg // 60):02}:{int(ritmo_seg % 60):02}"
    except:
        return ''

def validar_intervalo(valor, minimo, maximo):
    try:
        val = float(valor)
        return minimo <= val <= maximo
    except:
        return False

def extrair_km_por_bbox(imagem):
    data = pytesseract.image_to_data(imagem, output_type=pytesseract.Output.DICT)

    palavras = data['text']
    lefts = data['left']
    tops = data['top']

    km_indices = [i for i, palavra in enumerate(palavras) if palavra.strip().lower() == 'km']

    for km_idx in km_indices:
        km_top = tops[km_idx]
        km_left = lefts[km_idx]

        # Procurar valores acima do "km", alinhados horizontalmente
        candidatos = []
        for i, texto in enumerate(palavras):
            if i == km_idx:
                continue
            if not texto.strip():
                continue

            # Procurar por padrão de número decimal
            if re.match(r'^\d+[.,]?\d*$', texto.strip()):
                delta_top = km_top - tops[i]
                delta_left = abs(lefts[i] - km_left)

                # Deve estar acima e mais ou menos alinhado
                if 0 < delta_top < 100 and delta_left < 60:
                    candidatos.append((delta_top, texto.strip()))

        if candidatos:
            # Retornar o candidato mais próximo acima
            candidatos.sort()
            valor = candidatos[0][1].replace(',', '.')
            print(f"[DEBUG] Valor de KM extraído via bbox: {valor}")
            return valor

    return ''


# --- Funcao principal de extracao ---
def extrair_dados(caminho_img):
    imagem = Image.open(caminho_img)
    imagem = preprocessar_imagem(imagem)
    texto = pytesseract.image_to_string(imagem, lang='eng')
    linhas = [linha.strip() for linha in texto.split('\n') if linha.strip()]

    dados = {
        'DataHora': '', 'Distancia_km': '', 'Ritmo_medio': '', 'Tempo': '',
        'Calorias': '', 'Passos': '', 'Cadencia': '', 'Passada': '',
        'Observacoes': '', 'Arquivo': os.path.basename(caminho_img)
    }

    distancia_km = extrair_km_por_bbox(imagem)
    print(distancia_km)

    
    try:
        for linha in linhas:
            if "Corrida" in linha:
                partes = linha.split()
                if len(partes) >= 2:
                    dados['DataHora'] = f"{partes[0]} {partes[1]}"
                break

        

        for linha in linhas:
            if any(x in linha for x in ["'", '"', "°"]):
                partes = linha.split()
                if len(partes) >= 3:
                    dados['Ritmo_medio'] = formatar_ritmo(partes[0]) or partes[0]
                    dados['Tempo'] = partes[1] if ':' in partes[1] else ''
                    dados['Calorias'] = partes[2]
                break

        for linha in linhas:
            partes = linha.split()
            if len(partes) == 3 and partes[0].isdigit():
                dados['Passos'] = partes[0]
                dados['Cadencia'] = partes[1]
                dados['Passada'] = partes[2]
                break

        # Inferencia e validacao
        obs = []
        if not dados['Ritmo_medio'] and dados['Tempo'] and dados['Distancia_km']:
            ritmo = inferir_ritmo(dados['Tempo'], dados['Distancia_km'])
            dados['Ritmo_medio'] = ritmo
            obs.append('Ritmo inferido')

        if not validar_intervalo(dados['Passada'], 50, 300):
            obs.append('Passada fora do intervalo esperado')

        if not dados['Tempo']:
            obs.append('Tempo não extraído')

        dados['Observacoes'] = '; '.join(obs) if obs else ''

    except Exception as e:
        dados['Observacoes'] = f"Erro: {e}"

    return dados

# --- Atualizacao de planilha ---
def atualizar_planilha(diretorio='./imagens_corrida', saida_csv='resultados_corrida.csv', saida_excel='resultados_corrida.xlsx'):
    if os.path.exists(saida_csv):
        df_existente = pd.read_csv(saida_csv)
    else:
        df_existente = pd.DataFrame()

    novos_resultados = []
    arquivos_processados = set(df_existente['Arquivo']) if not df_existente.empty else set()

    for nome_arquivo in os.listdir(diretorio):
        if nome_arquivo.lower().endswith(('.jpg', '.jpeg', '.png')) and nome_arquivo not in arquivos_processados:
            caminho = os.path.join(diretorio, nome_arquivo)
            dados = extrair_dados(caminho)
            novos_resultados.append(dados)

    if novos_resultados:
        df_novo = pd.DataFrame(novos_resultados)
        df_final = pd.concat([df_existente, df_novo], ignore_index=True)
        df_final.to_csv(saida_csv, index=False)
        df_final.to_excel(saida_excel, index=False)
        print(f"✅ {len(novos_resultados)} novas imagens processadas.")
    else:
        print("ℹ️ Nenhuma nova imagem encontrada.")

if __name__ == '__main__':
    atualizar_planilha()
