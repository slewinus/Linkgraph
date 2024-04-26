import os
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from datetime import datetime

color_title = '#008DA2'  # Couleur du titre
color_text = '#031930'  # Couleur des textes
data_colors = ['#76C5BC','#48B77D','#4BBABB','#008DA2','#A9D249','#2B2171','#EAD83F','#EA504C']  # Couleurs des données

file_path = input("Veuillez entrer le chemin complet du fichier Excel : ")

column_headers = ['Zonage FTTO', 'Choix Zonage FTTH - FTTO', 'Choix Zonage FTTH - FTTO - 4G']

output_folder = 'rapports'
os.makedirs(output_folder, exist_ok=True)

logo_path = "logo.png"

try:
    df = pd.read_excel(file_path, sheet_name='Eligibilité_globale')
    print("Fichier Excel chargé avec succès.")
except Exception as e:
    print(f"Erreur lors du chargement du fichier Excel : {e}")
    exit()
current_date = datetime.now().strftime('%Y_%m_%d')
pdf_file_path = os.path.join(output_folder, f'Rapport_Analyse_{current_date}.pdf')
c = canvas.Canvas(pdf_file_path, pagesize=letter)

figsize = (8, 6)
title_fontsize = 18
autopct_fontsize = 12

for header in column_headers:
    if header in df.columns:
        value_counts = df[header].value_counts()
        if not value_counts.empty and value_counts.sum() > 0:
            plt.figure(figsize=figsize)
            patches, texts, autotexts = plt.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=90, colors=data_colors[:len(value_counts)])

            for text in texts:
                text.set_color(color_text)
                text.set_fontsize(autopct_fontsize)
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(autopct_fontsize)

            plt.title(f'Répartition pour {header}', fontsize=title_fontsize, color=color_title)
            plt.axis('equal')

            img_file_path = os.path.join(output_folder, f'{header.replace(" - ", "_").replace(" ", "_")}.png')
            plt.savefig(img_file_path, bbox_inches='tight')
            plt.close()

            c.setFont("Helvetica-Bold", title_fontsize)
            c.setFillColor(color_title)
            c.drawCentredString(letter[0] / 2, letter[1] - inch * 1.25, header)
            c.drawImage(img_file_path, letter[0] / 2 - figsize[0] * inch / 2, letter[1] / 2 - figsize[1] * inch / 2 + 0.75 * inch, width=figsize[0] * inch, height=figsize[1] * inch, preserveAspectRatio=True)
            c.setFont("Helvetica", 9)
            c.setFillColor(color_text)
            c.drawImage(logo_path, inch * 0.5, inch * 0.5, width=1 * inch, height=0.5 * inch, preserveAspectRatio=True)
            c.drawString(2 * inch, inch * 0.5, f"Date de création : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            c.showPage()
        else:
            print(f"Aucune donnée à grapher pour {header}.")
    else:
        print(f"La colonne {header} n'a pas été trouvée dans le fichier.")

c.save()
print(f"Le fichier PDF a été généré avec succès : {pdf_file_path}")
