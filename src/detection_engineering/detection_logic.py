"""
otx_to_attack_mapping.py [Detection Logic]
Simple pipeline:
 - fetch pulses from OTX (OTXv2)
 - fetch ATT&CK techniques via attackcti
 - map pulses -> techniques by heuristic keyword + fuzzy match
"""

import time
import json
from OTXv2 import OTXv2            # OTX Python SDK
from attackcti import attack_client
from rapidfuzz import fuzz, process
from dateutil import parser as dateparser

import requests

OTX_API_KEY = "b3b760a727df6da9eda4851e09c0e88fe5b3e383b154235ee6109e415e8af50f"  # set securely (env var recommended)

# -------------------------
# Helpers: fetch OTX pulses
# -------------------------
def fetch_otx_pulses(otx, max_pages=10, query="*",per_page=20):
    """
    Fetch pulses (paginated). Returns list of pulse dicts.
    Note: OTX SDK's search_pulses typically returns limited pages; adapt per account/subscriptions.
    """
    pulses = []
    #page = 1
    #while page <= max_pages:
    #    results = otx.search_pulses(page=page)  # method provided by OTX SDK
    #    if not results or 'results' not in results or len(results['results']) == 0:
    #        break
    #    pulses.extend(results['results'])
    #    page += 1
    #    # be polite to the API
    #    time.sleep(0.2)
    results = otx.search_pulses(query=query, max_results=max_pages)
    print(f"Debug: Fetched pulses result count: {len(results.get('results', []))}")
    if "results" in results:
        print("Debug: Fetched pulses keys:", results["results"][0].keys() if results["results"] else "No results")
        return results["results"]
    return []

def fetch_otx_pulses_raw(api_key, max_pages=5, per_page=20):
    headers = {"X-OTX-API-KEY": api_key}
    pulses = []
    for page in range(1, max_pages+1):
        url = f"https://otx.alienvault.com/api/v1/pulses/subscribed?page={page}&limit={per_page}"
        r = requests.get(url, headers=headers)
        data = r.json()
        print(f"Debug: Fetched raw pulses page {page}, count: {len(data.get('results', []))}")
        if not data.get("results"):
            break
        pulses.extend(data["results"])
        time.sleep(0.2)
    return pulses

# -------------------------
# Helpers: get pulse details
# -------------------------
def fetch_pulse_details(otx, pulse_id):
    """Get pulse details for a given pulse id"""
    return otx.get_pulse_details(pulse_id)  # returns dict with 'indicators', 'references', 'description', etc.

# -------------------------
# Helpers: fetch ATT&CK techniques via attackcti
# -------------------------
def fetch_attack_techniques():
    """
    Returns a list of technique objects with keys:
    - id (stix id), attack_id (eg T1059), name, description, platforms, detection, raw_stix
    """
    #ac = attack_client.AttackClient()
    ac = attack_client()  # ✅ instantiate directly
    # attack_client will download and cache the STIX content
    techniques = []
    all_techniques = ac.get_techniques()  # returns list of dicts
    for t in all_techniques:
        entry = {
            'stix_id': t.get('id'),
            'attack_id': t.get('external_references', [{}])[0].get('external_id'),
            'name': t.get('name'),
            'description': (t.get('description') or '')[:4000],  # truncate
            'platforms': t.get('x_mitre_platforms', []),
        }
        techniques.append(entry)
    return techniques

# -------------------------
# Mapping heuristics
# -------------------------
def build_search_corpus(techniques):
    """
    Build searchable corpus: map technique name + description -> technique obj.
    We'll use both exact token matching and fuzzy matching.
    """
    name_map = {}
    corpus = []
    for t in techniques:
        key = f"{t['name']} {t['description']}"
        corpus.append(key)
        name_map[key] = t
    return corpus, name_map

def map_pulse_to_techniques(pulse, corpus, name_map, top_n=5, fuzz_threshold=60):
    """
    Map a single pulse (or its textual content) to likely techniques.
    Returns list of (technique, score, match_text)
    """
    # collect candidate text from pulse
    texts = []
    if 'name' in pulse and pulse['name']:
        texts.append(pulse['name'])
    if 'description' in pulse and pulse['description']:
        texts.append(pulse['description'])
    # collect indicator strings (ioc values)
    if 'indicators' in pulse and isinstance(pulse['indicators'], list):
        for i in pulse['indicators']:
            # indicator sometimes is a dict with 'indicator' or 'type'
            val = i.get('indicator') or i.get('value') or i.get('type') or ''
            if val:
                texts.append(str(val))

    combined = " ".join(texts).lower()
    if not combined.strip():
        return []

    # First: simple token match (look for technique name tokens)
    candidates = []
    for key in corpus:
        # quick substring check on technique name
        tech_text = key.lower()
        # fuzzy match between combined pulse text and technique text
        score = fuzz.partial_ratio(combined, tech_text)
        if score >= fuzz_threshold:
            candidates.append((name_map[key], int(score), key))
    # If not enough candidates, return best fuzzy matches
    if len(candidates) < top_n:
        # use process.extract from rapidfuzz to get best matches
        best = process.extract(combined, corpus, scorer=fuzz.partial_ratio, limit=top_n)
        for match_text, score, _idx in best:
            t = name_map[match_text]
            # avoid duplicates
            if not any(t['stix_id'] == c[0]['stix_id'] for c in candidates):
                candidates.append((t, int(score), match_text))

    # sort descending by score and return top_n
    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)[:top_n]
    return candidates

# -------------------------
# Main pipeline
# -------------------------
"""Commented out main function to integrate with Detection Logic"""
""" def main():
    # Init OTX client
    otx = OTXv2(OTX_API_KEY)

    print("[*] fetching recent pulses from OTX...")
    pulses = fetch_otx_pulses(otx, max_pages=5)
    print(f"[*] fetched {len(pulses)} pulses (summary)")

    print("[*] fetching ATT&CK techniques via attackcti...")
    techniques = fetch_attack_techniques()
    print(f"[*] got {len(techniques)} techniques")

    corpus, name_map = build_search_corpus(techniques)

    # iterate pulses, get details and map
    mappings = []
    for p in pulses:
        pid = p.get('id') or p.get('pulse_id')
        details = fetch_pulse_details(otx, pid)
        # enrich: attach indicators if present (the OTX SDK may include them already)
        pulse_obj = {
            'id': pid,
            'name': details.get('name') or p.get('name'),
            'description': details.get('description') or p.get('description'),
            'indicators': details.get('indicators') or p.get('indicators') or []
        }
        candidates = map_pulse_to_techniques(pulse_obj, corpus, name_map, top_n=5, fuzz_threshold=60)
        mapped = []
        for (tech, score, match_text) in candidates:
            mapped.append({
                'attack_id': tech.get('attack_id'),
                'name': tech.get('name'),
                'score': score
            })
        mappings.append({
            'pulse_id': pid,
            'pulse_name': pulse_obj['name'],
            'mapped_techniques': mapped
        })

    # Output: write to JSON file
    with open('otx_attack_mappings.json', 'w', encoding='utf-8') as f:
        json.dump(mappings, f, indent=2, ensure_ascii=False)

    print("[*] finished. Output written to otx_attack_mappings.json")

if __name__ == "__main__":
    main() """

