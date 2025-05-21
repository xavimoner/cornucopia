#!/bin/bash

# Script per concatenar arxius Python i Shell amb paràmetres configurables
# Ús: ./tot_el_codi.sh [directori_origen] [fitxer_sortida]
# ./tot_el_codi.sh cornucopia/frontend frontend_code.txt
# ./tot_el_codi.sh cornucopia/backend backend_code.txt
# ./tot_el_codi.sh cornucopia tot_el_projecte.txt
# Verificació de paràmetres
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Error: Paràmetres incorrectes"
    echo "Ús: $0 <directori_origen> <fitxer_sortida>"
    echo "Exemple: $0 cornucopia/frontend resultat.txt"
    exit 1
fi

# Configuració
DIRECTORI_BASE="/home/xavi/GDRIVE/TFM/CODI/cornucopia"
DIRECTORI_ORIGEN="${DIRECTORI_BASE}/$1"
FITXER_SORTIDA="$2"

# Verificar si el directori existeix
if [ ! -d "$DIRECTORI_ORIGEN" ]; then
    echo "Error: El directori $DIRECTORI_ORIGEN no existeix"
    exit 1
fi

# Netejar l'arxiu de sortida si existeix
> "$FITXER_SORTIDA"

# Processar arxius
echo "Processant arxius de $DIRECTORI_ORIGEN..."
find "$DIRECTORI_ORIGEN" -type f \( -name "*.py" -o -name "*.sh" \) | while read -r arxiu; do
    echo -e "\n\n### ARXIU: ${arxiu#$DIRECTORI_BASE/} ###\n" >> "$FITXER_SORTIDA"
    cat "$arxiu" >> "$FITXER_SORTIDA"
    echo "✔ Afegit: ${arxiu#$DIRECTORI_BASE/}"
done

# Resultat final
LINEES=$(wc -l < "$FITXER_SORTIDA")
ARXIUS=$(grep -c "^### ARXIU:" "$FITXER_SORTIDA")

echo -e "\nResum:"
echo "• Directori processat: $DIRECTORI_ORIGEN"
echo "• Fitxer generat: $FITXER_SORTIDA"
echo "• Arxius concatenats: $ARXIUS"
echo "• Línies totals: $LINEES"
