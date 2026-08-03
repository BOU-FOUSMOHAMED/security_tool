"""Service HTTP minimaliste qui exécute un scan nmap et renvoie le résultat en JSON."""

import os
import subprocess
import threading
import time
import xml.etree.ElementTree as ET

from flask import Flask, jsonify, request

app = Flask(__name__)

NMAP_PATH = os.environ.get("NMAP_PATH", "nmap")
SCAN_TIMEOUT = int(os.environ.get("SCAN_TIMEOUT", 120))

_lock = threading.Lock()


def parse_scan(xml_text):
    """Extrait ports ouverts, état et durée depuis la sortie XML de nmap."""
    root = ET.fromstring(xml_text)
    result = {"host": "", "status": "down", "ports": [], "duration": 0.0}

    stats = root.find("runstats/finished")
    if stats is not None:
        result["duration"] = float(stats.get("elapsed", 0))

    host = root.find("host")
    if host is None:
        return result
    result["status"] = host.findtext("status/@state") or "down"
    addr = host.find("address")
    if addr is not None:
        result["host"] = addr.get("addr", "")

    for port in root.findall("host/ports/port"):
        state = port.findtext("state/@state")
        if state != "open":
            continue
        result["ports"].append({
            "port": port.get("portid"),
            "protocol": port.get("protocol"),
            "service": port.findtext("service/@name", ""),
        })
    return result


@app.get("/")
def index():
    return jsonify(service="nmap-scan-service", usage="GET /scan?target=<host>")


@app.get("/health")
def health():
    return jsonify(status="ok")


@app.get("/scan")
def scan():
    target = (request.args.get("target") or "").strip()
    if not target:
        return jsonify(error="parametre 'target' requis"), 400

    if not _lock.acquire(timeout=SCAN_TIMEOUT):
        return jsonify(error="scan déjà en cours"), 429
    try:
        start = time.monotonic()
        proc = subprocess.run(
            ["nmap","-Pn","-sT","-n","oX","-", target],
            capture_output=True, text=True, timeout=SCAN_TIMEOUT,
        )
        result = parse_scan(proc.stdout)
        result["elapsed"] = round(time.monotonic() - start, 2)
        if proc.returncode not in (0, 1):
            return jsonify(error="échec nmap", detail=proc.stderr.strip()), 502
        return jsonify({
        "result": result,
        
        
    })
    except FileNotFoundError:
        return jsonify(error="nmap introuvable"), 503
    except subprocess.TimeoutExpired:
        return jsonify(error="scan interrompu (timeout)"), 504
    except ET.ParseError:
        return jsonify(error="sortie nmap illisible"), 502
    finally:
        _lock.release()


if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", 5000)),
        threaded=False,
    )


