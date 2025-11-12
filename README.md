# Scraper - universidadperu.com

Este script extrae empresas de https://www.universidadperu.com/empresas/ por rubro.

Características:
- Intenta la URL directa: `https://www.universidadperu.com/empresas/<rubro>-categoria.php`.
- Si no encuentra resultados, busca el rubro en `categorias.php` (fallback).
- Recorre la paginación (`?pagina=N`) y extrae "Razón Social" y "RUC".
- Guarda en CSV (por defecto) o XLSX.

Requisitos
----------
Instalar dependencias (PowerShell):

```powershell
python -m pip install -r requirements.txt
```

Uso
---
Ejemplo en PowerShell:

```powershell
python scraping_universidadperu.py --rubro "restaurantes" --out empresas_restaurantes.csv
```

Guardar en XLSX:

```powershell
python scraping_universidadperu.py -r "restaurantes" -o empresas.xlsx -f xlsx
```

Notas
-----
- El scraping hace requests a la web; respeta las políticas del sitio y evita cargas excesivas.
- Si la estructura de la web cambia, puede ser necesario ajustar los selectores (tabla, clases, etc.).
