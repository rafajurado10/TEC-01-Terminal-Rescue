#!/usr/bin/env python3
"""Cierre mensual reproducible de afiliados de Caja de Compensación.

Solo usa la biblioteca estándar de Python 3.8+ y datos incluidos en el kit.
Nunca mueve/modifica los CSV de entrada; genera output/ desde cero.
"""

import csv
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data"
OUTPUT = ROOT / "output"
ALLOWED_STATUSES = {"A": "ACTIVO", "I": "INACTIVO"}
ERROR_PATTERN = re.compile(r"\bCIE-\d{4}\b")


def read_csv(filename, delimiter=","):
    with (INPUT / filename).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=delimiter))


def normalize_date(value):
    """Devuelve YYYY-MM-DD o None para una fecha imposible o irreconocible."""
    value = (value or "").strip()
    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d"):
        try:
            return datetime.strptime(value, pattern).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def normalize_document(value):
    """Caja Oriente usa documentos numéricos con ceros a la izquierda."""
    normalized = (value or "").strip().lstrip("0")
    return normalized or "0"


def write_csv(filename, header, rows):
    with (OUTPUT / filename).open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def count_top_error():
    errors = Counter()
    for path in sorted((ROOT / "logs").glob("*.log")):
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                errors.update(ERROR_PATTERN.findall(line))
    if not errors:
        return "NINGUNO", 0
    # Orden secundario estable si hay empate.
    return sorted(errors.items(), key=lambda item: (-item[1], item[0]))[0]


def main():
    afiliados = read_csv("AFI_MAE.csv")
    empresas = {row["COD_EMP"].strip(): row for row in read_csv("EMPRESA.csv")}
    beneficiarios = read_csv("AFI_BEN.csv")
    aportes = read_csv("APORTES.csv")
    caja_oriente = read_csv("extracto_caja_oriente.csv", delimiter=";")

    OUTPUT.mkdir(exist_ok=True)
    # La primera fila de cada documento es la fuente oficial; se registran los duplicados.
    unicos = {}
    duplicados = set()
    for row in afiliados:
        documento = row["NRO_DOC"].strip()
        if documento in unicos:
            duplicados.add(documento)
        else:
            unicos[documento] = row

    # Una excepción por (tipo, documento), sin falsos duplicados por cruce.
    excepciones = set()
    def reportar(documento, tipo, detalle):
        excepciones.add((documento, tipo, detalle))

    for doc in duplicados:
        reportar(doc, "DUPLICADO", "Documento repetido en AFI_MAE; se usa la primera fila")

    conteo_beneficiarios = Counter()
    for row in beneficiarios:
        afiliado = row["NRO_DOC_AFI"].strip()
        doc_ben = row["NRO_DOC_BEN"].strip()
        if afiliado not in unicos:
            reportar(doc_ben, "BENEFICIARIO_HUERFANO", "No existe su afiliado en AFI_MAE")
        else:
            conteo_beneficiarios[afiliado] += 1

    ultimo_aporte = {}
    for row in aportes:
        doc = row["NRO_DOC"].strip()
        periodo = row["PERIODO"].strip()
        if re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", periodo):
            if periodo > ultimo_aporte.get(doc, ""):
                ultimo_aporte[doc] = periodo

    activos = []
    inactivos = 0
    for doc, row in unicos.items():
        estado = row["EST_AFI"].strip()
        codigo_empresa = row["COD_EMP"].strip()
        nombre = " ".join((row.get(key) or "").strip() for key in ("NOM1", "NOM2", "APE1", "APE2"))
        nombre = " ".join(nombre.split())

        if normalize_date(row.get("FEC_AFI")) is None:
            reportar(doc, "FECHA_INVALIDA", "Fecha de afiliacion imposible o formato desconocido")
        if estado not in ALLOWED_STATUSES:
            reportar(doc, "CODIGO_INVALIDO", "Estado de afiliado fuera de A/I")
            continue
        if estado == "I":
            inactivos += 1
            continue
        empresa = empresas.get(codigo_empresa)
        if not codigo_empresa or empresa is None:
            reportar(doc, "SIN_EMPRESA", "Afiliado activo sin empresa registrada")
            continue
        activos.append((doc, nombre, "ACTIVO", codigo_empresa,
                        empresa["NOM_EMP"].strip(), conteo_beneficiarios[doc],
                        ultimo_aporte.get(doc, "")))

    # Situación de Caja Oriente: VIGENTE=A y RETIRADO=I.
    equivalencias = {"VIGENTE": "A", "RETIRADO": "I"}
    for row in caja_oriente:
        doc = normalize_document(row["id_afiliado"])
        situacion = row["situacion"].strip().upper()
        original = unicos.get(doc)
        if original is None:
            reportar(doc, "CRUCE_NO_COINCIDE", "Afiliado de Caja Oriente ausente del maestro")
        elif equivalencias.get(situacion) != original["EST_AFI"].strip():
            reportar(doc, "CRUCE_NO_COINCIDE", "Situacion Caja Oriente diferente al estado local")

    write_csv("afiliados_activos.csv",
              ["documento", "nombre", "estado", "cod_empresa", "empresa", "beneficiarios", "ultimo_aporte"],
              activos)
    write_csv("excepciones.csv", ["documento", "tipo", "detalle"],
              sorted(excepciones, key=lambda item: (item[1], item[0], item[2])))
    with (OUTPUT / "totales.txt").open("w", encoding="utf-8") as f:
        f.write("total_afiliados={0}\nactivos={1}\ninactivos={2}\nexcepciones={3}\n".format(
            len(unicos), len(activos), inactivos, len(excepciones)))
    code, occurrences = count_top_error()
    with (OUTPUT / "top_error.txt").open("w", encoding="utf-8") as f:
        f.write("codigo_error={0}\nocurrencias={1}\n".format(code, occurrences))
    print("Cierre completado: {0} afiliados, {1} activos, {2} inactivos, {3} excepciones".format(
        len(unicos), len(activos), inactivos, len(excepciones)))
    print("Error mas frecuente: {0} ({1} apariciones)".format(code, occurrences))


if __name__ == "__main__":
    main()
