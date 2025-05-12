import easyocr

reader = easyocr.Reader(['pt'])  # ou ['en']
results = reader.readtext(r'imagens_corrida\recorte_1745978618905.jpg')

for bbox, text, conf in results:
    print(f"Texto: {text} | Confiança: {conf}")
    

def montar_dados_ocr(lista_texto):
    dados = {}
    
    dados["data_hora"] = lista_texto[0].split(" Corrida")[0].replace('.', ':')
    dados["atividade"] = "Corrida"
    
    dados["distancia_km"] = float(lista_texto[1])
    
    dados["ritmo_medio"] = {
        "valor": lista_texto[3],
        "unidade": "min/km"
    }
    dados["tempo_usado"] = {
        "valor": lista_texto[4].replace('.', ':'),
        "formato": "hh:mm:ss"
    }
    dados["calorias"] = {
        "valor": float(lista_texto[5]),
        "unidade": "kcal"
    }
    dados["passos"] = {
        "valor": int(lista_texto[9]),
        "unidade": "passos"
    }
    dados["cadencia_media"] = {
        "valor": int(lista_texto[10]),
        "unidade": "passos/min"
    }
    dados["passada_media"] = {
        "valor": int(lista_texto[11]),
        "unidade": "cm"
    }
    
    return dados

