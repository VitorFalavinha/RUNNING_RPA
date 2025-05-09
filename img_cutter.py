import os
from PIL import Image, ImageDraw

def crop_between_blue_lines(input_folder, output_folder, color=(0, 102, 204)):
    """
    Adiciona duas linhas azuis horizontais em todas as imagens de um diretório
    e cria uma versão recortada contendo apenas a área entre as linhas.
    As posições das linhas variam conforme a altura da imagem.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not files:
        print("Nenhuma imagem encontrada na pasta de entrada.")
        return
    
    for filename in files:
        try:
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path)
            width, height = img.size

            # Definições por tamanho
            if height > 4000:
                line1_y = 1150   # Ex: 19.5% de 4323
                line2_y = 2150  # Ex: 36% de 4323
                thickness = 30  # ~0.7% de 4323
            else:
                print(f"Tamanho de imagem não reconhecido: {filename} ({width}x{height})")
                continue

            # Adicionar linhas na imagem
            img_with_lines = img.copy()
            draw = ImageDraw.Draw(img_with_lines)
            for i in range(thickness):
                draw.line([(0, line1_y + i), (width, line1_y + i)], fill=color)
                draw.line([(0, line2_y + i), (width, line2_y + i)], fill=color)

            # Salvar imagem com linhas
            img_with_lines.save(os.path.join(output_folder, f"linhas_{filename}"))

            # Recortar a imagem original
            cropped_img = img.crop((0, line1_y + thickness, width, line2_y))
            cropped_img.save(os.path.join(output_folder, f"recorte_{filename}"))

            print(f"Processado: {filename}")

        except Exception as e:
            print(f"Erro ao processar {filename}: {e}")
    
    print(f"\nProcessamento concluído! {len(files)} imagens analisadas.")

# Exemplo de uso:
if __name__ == "__main__":
    input_dir = "imagens_originais"
    output_dir = "imagens_recortadas"
    crop_between_blue_lines(input_dir, output_dir)
