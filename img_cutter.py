import os
from PIL import Image, ImageDraw

def crop_between_blue_lines(input_folder, output_folder, color=(0, 102, 204)):
    """
    Adiciona duas linhas azuis horizontais em todas as imagens de um diretório
    e cria uma versão recortada contendo apenas a área entre as linhas.
    Evita reprocessar arquivos que já foram recortados anteriormente.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print("Nenhuma imagem encontrada na pasta de entrada.")
        return
    
    processados = 0
    ignorados = 0

    for filename in files:
        try:
            recorte_nome = f"recorte_{filename}"
            recorte_path = os.path.join(output_folder, recorte_nome)

            # Verifica se a imagem já foi recortada anteriormente
            if os.path.exists(recorte_path):
                print(f"Ignorado (já processado): {filename}")
                ignorados += 1
                continue

            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            width, height = img.size

            # Definições por tamanho
            if height > 4000:
                line1_y = 1150
                line2_y = 2150
                thickness = 30
            else:
                print(f"Tamanho de imagem não reconhecido: {filename} ({width}x{height})")
                continue

            # Adicionar linhas à imagem
            img_with_lines = img.copy()
            draw = ImageDraw.Draw(img_with_lines)
            for i in range(thickness):
                draw.line([(0, line1_y + i), (width, line1_y + i)], fill=color)
                draw.line([(0, line2_y + i), (width, line2_y + i)], fill=color)

            # Salvar imagem com linhas
            img_with_lines.save(os.path.join(output_folder, f"linhas_{filename}"))

            # Recortar e salvar
            cropped_img = img.crop((0, line1_y + thickness, width, line2_y))
            cropped_img.save(recorte_path)

            print(f"Processado: {filename}")
            processados += 1

        except Exception as e:
            print(f"Erro ao processar {filename}: {e}")
    
    print(f"\nProcessamento concluído! {processados} imagens novas processadas, {ignorados} já estavam prontas.")

# Exemplo de uso:
if __name__ == "__main__":
    input_dir = "imagens_originais"
    output_dir = "imagens_corrida"
    crop_between_blue_lines(input_dir, output_dir)
