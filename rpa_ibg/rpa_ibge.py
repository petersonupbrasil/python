import re
import unicodedata
import difflib
import requests
import pandas as pd
from playwright.sync_api import sync_playwright

CORTE_AUTO = 0.85

cidades_busca = [
    ("São Paul", "SP"), ("Viçosa", "MG"), ("Salvad", "BA"),
    ("Boa Vista", "RR"), ("Curitiba", "PR"), ("Planaltina", "GO"),
    ("Manaus", "AM"), ("Bom Jesus", "RS"), ("Florianópolis", "SC"),
    ("Belém", "PA"),
]

def normaliza(txt):
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", txt.lower()).strip()

def slug(txt):
    return re.sub(r"[^a-z0-9]+", "-", normaliza(txt)).strip("-")

#Dicionário na memória para guardar os municípios já consultados por estado e evitar requisições repetidas
_cache_uf = {}

#Consulta a API REST oficial do IBGE
def municipios_da_uf(uf):
    if uf not in _cache_uf:
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        _cache_uf[uf] = {normaliza(m["nome"]): m["nome"] for m in r.json()}
    return _cache_uf[uf]

def valida_cidade(cidade, uf):
    try:
        oficiais = municipios_da_uf(uf)
    except Exception as e:
        return None, f"Erro ao consultar lista oficial da UF {uf}: {e}"

    chave = normaliza(cidade)
    if chave in oficiais:
        return oficiais[chave], "OK"

    parecidos = difflib.get_close_matches(chave, oficiais.keys(), n=1, cutoff=0.6)
    if not parecidos:
        return None, f"Cidade não encontrada em {uf}"

    sugestao = oficiais[parecidos[0]]
    sim = difflib.SequenceMatcher(None, chave, parecidos[0]).ratio()
    if sim >= CORTE_AUTO:
        return sugestao, f"Corrigida automaticamente de '{cidade}' para '{sugestao}'"
    return None, f"Cidade não encontrada (mais próxima: {sugestao}, semelhança {sim:.2f})"

# Cada padrão começa pelo RÓTULO exibido na página, depois valor, unidade e ano.
# [\s\xa0]* cobre quebras de linha e espaços não separáveis.
SEP = r"[\s\xa0]*"
PADROES = {
    "pop":  rf"População no último censo{SEP}([\d\.]+){SEP}pessoas{SEP}\[(\d{{4}})\]",
    "area": rf"Área Territorial{SEP}([\d\.,]+){SEP}km²{SEP}\[(\d{{4}})\]",
    # SUPOSIÇÃO: confirme o rótulo exato do PIB na página
    "pib":  rf"PIB per capita{SEP}([\d\.,]+){SEP}R\${SEP}\[(\d{{4}})\]",
}

def extrai(texto, padrao):
    m = re.search(padrao, texto, re.IGNORECASE)
    return (m.group(1).strip(), m.group(2)) if m else (None, None)

def formato_numerico_ok(valor):
    return valor is not None and re.fullmatch(
        r"\d{1,3}(\.\d{3})*(,\d+)?|\d+(,\d+)?", valor) is not None

resultados = []

#Inicializa a sessão do Playwright
with sync_playwright() as pw:
    navegador = pw.chromium.launch(headless=False)
    page = navegador.new_page()

    for cidade_in, uf in cidades_busca:
        print(f"Processando: {cidade_in} ({uf})")
        linha = {
            "Cidade (informada)": cidade_in, "Cidade (oficial)": "N/A", "Estado": uf,
            "População": "N/A", "Ano população": "N/A",
            "Área (km²)": "N/A", "Ano área": "N/A",
            "PIB per capita": "N/A", "Ano PIB": "N/A",
            "Status": "",
        }

        cidade, status = valida_cidade(cidade_in, uf)
        if cidade is None:
            linha["Status"] = status
            print("  ->", status)
            resultados.append(linha)
            continue

        linha["Cidade (oficial)"] = cidade
        url = f"https://www.ibge.gov.br/cidades-e-estados/{uf.lower()}/{slug(cidade)}.html"

        try:
            page.goto(url, timeout=60000)
            page.wait_for_selector("text=pessoas", timeout=15000)

            # CORREÇÃO: procura a cidade em QUALQUER h1 (o primeiro é o título do site)
            titulos = page.locator("h1").all_inner_texts()
            if not any(normaliza(cidade) == normaliza(t) for t in titulos):
                linha["Status"] = f"Página divergente (h1s: {titulos})"
                print("  ->", linha["Status"])
                resultados.append(linha)
                continue

            texto = page.locator("body").inner_text().replace("\xa0", " ")
            dados = {k: extrai(texto, p) for k, p in PADROES.items()}

            problemas = []
            for k, (val, ano) in dados.items():
                if not formato_numerico_ok(val):
                    dados[k] = (None, None)
                    problemas.append(k)

            linha.update({
                "População": dados["pop"][0] or "N/A",  "Ano população": dados["pop"][1] or "N/A",
                "Área (km²)": dados["area"][0] or "N/A", "Ano área": dados["area"][1] or "N/A",
                "PIB per capita": dados["pib"][0] or "N/A", "Ano PIB": dados["pib"][1] or "N/A",
            })
            linha["Status"] = status if not problemas else \
                f"{status} | Dados ausentes/inválidos: {', '.join(problemas)}"

        except Exception as e:
            linha["Status"] = f"Erro ao coletar: {e}"

        print("  ->", linha["Status"])
        resultados.append(linha)

    navegador.close()

df = pd.DataFrame(resultados)
df.to_csv("Planilha-IBGE.csv", index=False, sep=";", encoding="utf-8-sig")
print("\n", df[["Cidade (informada)", "Cidade (oficial)", "População", "Área (km²)", "PIB per capita", "Status"]])