import asyncio
import re
import unicodedata
import difflib
import requests
import pandas as pd
from playwright.async_api import async_playwright  

CORTE_AUTO = 0.85
MAX_CONCORRENTES = 4   # quantas abas ao mesmo tempo

cidades_busca = [
    ("São Pau", "SP"), ("Vicosa", "MG"), ("Salva", "BA"),
    ("Vista boa", "RR"), ("Curitiba", "PR"), ("Planaltina", "GO"),
    ("Manaus", "AM"), ("Bom Jesus", "RS"), ("Florianópolis", "SC"),
    ("Belém", "PA"),
]

# ---------- Funções utilitárias (continuam síncronas: são rápidas e não usam rede/await) ----------
def normaliza(txt):
    txt = unicodedata.normalize("NFKD", txt).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", txt.lower()).strip()

def slug(txt):
    return re.sub(r"[^a-z0-9]+", "-", normaliza(txt)).strip("-")

_cache_uf = {}

def municipios_da_uf(uf):
    # Usa `requests` (bloqueante). Como é chamada ANTES do paralelismo (veja main),
    # não atrapalha o asyncio: o cache já estará preenchido quando as tarefas rodarem.
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

SEP = r"[\s\xa0]*"
PADROES = {
    "pop":  rf"População no último censo{SEP}([\d\.]+){SEP}pessoas{SEP}\[(\d{{4}})\]",
    "area": rf"Área Territorial{SEP}([\d\.,]+){SEP}km²{SEP}\[(\d{{4}})\]",
    "pib":  rf"PIB per capita{SEP}([\d\.,]+){SEP}R\${SEP}\[(\d{{4}})\]",  # confirme o rótulo
}

def extrai(texto, padrao):
    m = re.search(padrao, texto, re.IGNORECASE)
    return (m.group(1).strip(), m.group(2)) if m else (None, None)

def formato_numerico_ok(valor):
    return valor is not None and re.fullmatch(
        r"\d{1,3}(\.\d{3})*(,\d+)?|\d+(,\d+)?", valor) is not None


# ---------- [ASYNC] Tarefa que processa UMA cidade ----------
# `async def` transforma a função em corrotina: ela pode ser pausada nos `await`.
async def processa_cidade(contexto, semaforo, cidade_in, uf):
    linha = {
        "Cidade (informada)": cidade_in, "Cidade (oficial)": "N/A", "Estado": uf,
        "População": "N/A", "Ano população": "N/A",
        "Área (km²)": "N/A", "Ano área": "N/A",
        "PIB per capita": "N/A", "Ano PIB": "N/A",
        "Status": "",
    }

    # Validação local (sem rede, pois o cache já foi preenchido): não precisa de await
    cidade, status = valida_cidade(cidade_in, uf)
    if cidade is None:
        linha["Status"] = status
        return linha
    linha["Cidade (oficial)"] = cidade
    url = f"https://www.ibge.gov.br/cidades-e-estados/{uf.lower()}/{slug(cidade)}.html"

    # [ASYNC] O semáforo limita quantas tarefas entram neste bloco ao mesmo tempo.
    # As demais ficam aguardando aqui até alguma terminar e liberar a vaga.
    async with semaforo:
        print(f"Iniciando: {cidade} ({uf})")
        page = await contexto.new_page()  # [ASYNC] cada tarefa tem sua própria aba
        try:
            # [ASYNC] Toda chamada do Playwright que espera algo precisa de `await`.
            # Enquanto esta aba espera a rede, o asyncio roda as outras tarefas.
            await page.goto(url, timeout=60000)
            await page.wait_for_selector("text=pessoas", timeout=15000)

            titulos = await page.locator("h1").all_inner_texts()
            if not any(normaliza(cidade) == normaliza(t) for t in titulos):
                linha["Status"] = f"Página divergente (h1s: {titulos})"
                return linha

            texto = (await page.locator("body").inner_text()).replace("\xa0", " ")
            dados = {k: extrai(texto, p) for k, p in PADROES.items()}

            problemas = []
            for k, (val, _ano) in dados.items():
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
        finally:
            await page.close()  # [ASYNC] sempre fecha a aba, mesmo com erro
            print(f"Concluído: {cidade} ({uf}) -> {linha['Status']}")

    return linha


# ---------- [ASYNC] Função principal ----------
async def main():
    # Pré-carrega a lista oficial de cada UF ANTES do paralelismo.
    # Assim o `requests` (bloqueante) não roda dentro das tarefas e não trava o loop.
    for uf in {uf for _, uf in cidades_busca}:
        try:
            municipios_da_uf(uf)
        except Exception as e:
            print(f"Aviso: falha ao carregar lista de {uf}: {e}")

    semaforo = asyncio.Semaphore(MAX_CONCORRENTES)  # [ASYNC] criado dentro do loop

    # [ASYNC] `async with` em vez de `with`: abre e fecha o Playwright de forma assíncrona
    async with async_playwright() as pw:
        navegador = await pw.chromium.launch(headless=False)
        # Um único navegador e um único contexto; cada tarefa abre uma aba (page) nele.
        # É bem mais leve do que abrir um navegador por cidade.
        contexto = await navegador.new_context()

        # [ASYNC] Cria uma corrotina por cidade e as executa juntas.
        # O semáforo garante no máximo MAX_CONCORRENTES em andamento.
        # gather devolve os resultados na MESMA ORDEM da lista de entrada.
        tarefas = [processa_cidade(contexto, semaforo, c, uf) for c, uf in cidades_busca]
        resultados = await asyncio.gather(*tarefas)

        await contexto.close()
        await navegador.close()

    df = pd.DataFrame(resultados)
    df.to_csv("planilha_ibge.csv", index=False, sep=";", encoding="utf-8-sig")
    print("\n", df[["Cidade (informada)", "Cidade (oficial)", "População",
                    "Área (km²)", "PIB per capita", "Status"]])


# [ASYNC] Ponto de entrada: asyncio.run cria o loop de eventos e executa main()
if __name__ == "__main__":
    asyncio.run(main())