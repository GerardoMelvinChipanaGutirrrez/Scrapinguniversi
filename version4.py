import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# ---------------- CONFIGURACIÓN ----------------
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# options.add_argument("--headless")  # opcional si no quieres ver el navegador
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

BASE_URL = "https://www.universidadperu.com/empresas/categorias.php"

# ---------------- FUNCIONES ----------------
def encontrar_ul_flexible():
    """Devuelve el elemento <ul> que contiene los enlaces, sin importar si hay <p> o no."""
    posibles_xpaths = [
        "//h2/following-sibling::p/following-sibling::ul",
        "//h2/following-sibling::ul",
        "//h1/following-sibling::p/following-sibling::ul",
        "//h1/following-sibling::ul"
    ]
    for xp in posibles_xpaths:
        try:
            return driver.find_element(By.XPATH, xp)
        except:
            continue
    return None

# ---------------- FLUJO PRINCIPAL ----------------
rubro_input = input("Ingrese el rubro (ejemplo: electricidad): ").strip().lower()
if not rubro_input:
    print("No ingresaste rubro. Saliendo.")
    driver.quit()
    raise SystemExit

driver.get(BASE_URL)
time.sleep(1)

# 1️⃣ Buscar enlace de la categoría
categoria_url = None
for a in driver.find_elements(By.CSS_SELECTOR, "a"):
    texto = a.text.strip().lower()
    if rubro_input in texto:
        categoria_url = a.get_attribute("href")
        print(f"✅ Categoría encontrada: {texto}")
        break

if not categoria_url:
    print(f"❌ No se encontró la categoría '{rubro_input}'.")
    driver.quit()
    raise SystemExit

# 2️⃣ Entrar a la categoría
driver.get(categoria_url)
time.sleep(1)

# 3️⃣ Extraer regiones
try:
    ul = driver.find_element(By.XPATH, "//h1/following-sibling::p/following-sibling::ul")
    regiones = ul.find_elements(By.TAG_NAME, "a")
    regiones_data = [(r.text.strip(), r.get_attribute("href")) for r in regiones if r.text.strip()]
except Exception as e:
    print("❌ No se pudieron obtener las regiones:", e)
    driver.quit()
    raise SystemExit

print(f"\n📍 Se encontraron {len(regiones_data)} regiones.\n")

# 4️⃣ Recorrer regiones, provincias, distritos y empresas
data = []

for nombre_region, url_region in regiones_data:
    print(f"🏞️ Región: {nombre_region}")
    driver.get(url_region)
    time.sleep(1)

    ul_prov = encontrar_ul_flexible()

    if not ul_prov:
        print("   ⚠️ No se encontró bloque de provincias.")
        continue

    provincias = ul_prov.find_elements(By.TAG_NAME, "a")
    provincias_data = [(p.text.strip(), p.get_attribute("href")) for p in provincias if p.text.strip()]

    for nombre_prov, url_prov in provincias_data:
        print(f"   🏙️ Provincia: {nombre_prov}")
        driver.get(url_prov)
        time.sleep(1)

        ul_dist = encontrar_ul_flexible()

        if not ul_dist:
            print("      ⚠️ No se encontró bloque de distritos.")
            continue

        distritos = ul_dist.find_elements(By.TAG_NAME, "a")
        distritos_data = [(d.text.strip(), d.get_attribute("href")) for d in distritos if d.text.strip()]

        for nombre_dist, url_dist in distritos_data:
            print(f"      🏘️ Distrito: {nombre_dist}")
            driver.get(url_dist)
            time.sleep(1)

            # 🏢 Buscar lista de empresas (razones sociales)
            ul_emp = encontrar_ul_flexible()
            if not ul_emp:
                print("         ⚠️ No se encontró bloque de empresas.")
                continue

            empresas = ul_emp.find_elements(By.TAG_NAME, "a")
            for e in empresas:
                nombre_empresa = e.text.strip()
                url_empresa = e.get_attribute("href")
                if nombre_empresa and url_empresa:
                    data.append({
                        "Región": nombre_region,
                        "Provincia": nombre_prov,
                        "Distrito": nombre_dist,
                        "Razón Social": nombre_empresa,
                        "URL_Empresa": url_empresa
                    })
                    print(f"         🏢 {nombre_empresa}")

# 5️⃣ Guardar resultados en Excel (.xlsx)
if data:
    df = pd.DataFrame(data)

    # Crear nombre de archivo Excel legible
    filename = f"empresas_{rubro_input.replace(' ', '_')}.xlsx"

    # Guardar en Excel con encabezados y ajuste automático de ancho
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Empresas")

        # Ajustar ancho de columnas automáticamente
        from openpyxl.utils import get_column_letter
        worksheet = writer.sheets["Empresas"]
        for i, col in enumerate(df.columns):
            max_length = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.column_dimensions[get_column_letter(i+1)].width = max_length

    print(f"\n✅ Se guardaron {len(data)} empresas en '{filename}' (formato Excel)")
else:
    print("⚠️ No se encontró ninguna empresa.")

driver.quit()
