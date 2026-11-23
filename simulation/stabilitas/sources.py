"""Official reference acquisitions. None are fitted or used by the engine."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
import sys
from urllib.parse import urlencode
from urllib.request import urlopen
from zoneinfo import ZoneInfo

from demos.config import canonical, sha

SERIES = {
    "gdp": ("nama_10_gdp", {"na_item": "B1GQ", "unit": "CP_MEUR"}, "PIL nominale, milioni di EUR correnti"),
    "wages": ("nama_10_gdp", {"na_item": "D1", "unit": "CP_MEUR"}, "Retribuzioni e contributi, milioni di EUR correnti"),
    "consumption": ("nama_10_gdp", {"na_item": "P31_S14_S15", "unit": "CP_MEUR"}, "Consumi finali famiglie e ISP, milioni di EUR correnti"),
    "employment": ("lfsa_egan", {"age": "Y15-64", "sex": "T", "unit": "THS_PER", "citizen": "TOTAL"}, "Occupati 15–64 anni, migliaia di persone"),
    "prices": ("prc_hicp_aind", {"coicop": "CP00", "unit": "INX_A_AVG"}, "HICP totale medio annuo, indice della fonte"),
    "firms": ("sbs_sc_ovw", {"nace_r2": "B-S_X_O_S94", "size_emp": "TOTAL", "indic_sbs": "ENT_NR"}, "Imprese, numero, perimetro SBS da armonizzare"),
    "government": ("gov_10dd_edpt1", {"na_item": "GD", "unit": "PC_GDP", "sector": "S13"}, "Debito lordo amministrazioni pubbliche, % PIL"),
    "credit": ("nasa_10_f_bs", {"sector": "S11", "na_item": "F4", "finpos": "LIAB", "unit": "MIO_EUR"}, "Prestiti, passività società non finanziarie, milioni di EUR"),
}
BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"


def acquire(name, item, folder):
    dataset, filters, definition = item
    query = urlencode(dict(lang="en", geo="EU27_2020", sinceTimePeriod=2022, untilTimePeriod=2024, **filters))
    url = BASE + dataset + "?" + query
    result = {"dataset": dataset, "series": filters, "region": "EU27_2020", "period": "2022–2024", "url": url,
              "definition_and_unit": definition, "licence": "https://ec.europa.eu/eurostat/about-us/policies/copyright",
              "acquired": datetime.now(ZoneInfo("Europe/Rome")).date().isoformat(),
              "transformations": "Selezione UE-27 annuale; risposta JSON-stat inalterata",
              "use": "2022–2023 candidati per futura stima; 2024 riservato per futuro confronto; nessun fit in Stabilitas"}
    try:
        with urlopen(url, timeout=18) as response:
            raw = response.read()
        doc = json.loads(raw)
        if not doc.get("value"):
            raise ValueError("Nessuna cella nel perimetro richiesto")
        if set(doc["dimension"]["time"]["category"]["index"]) != {"2022", "2023", "2024"}:
            raise ValueError("Copertura temporale incompleta")
        path = f"{name}.json"
        (folder / path).write_bytes(raw)
        result.update(status="acquisito", file=path, sha256=sha(raw))
    except (OSError, ValueError, KeyError) as exc:
        result.update(status="non acquisito", problem=str(exc))
    return name, result


def main(folder):
    folder.mkdir(exist_ok=True, parents=True)
    with ThreadPoolExecutor(max_workers=5) as pool:
        manifest = dict(pool.map(lambda pair: acquire(*pair, folder), SERIES.items()))
    (folder / "manifest.json").write_bytes(canonical(manifest))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
