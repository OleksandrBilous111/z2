"""Testy bazy „Dojazd na uczelnię”. Uruchom: python se/test_moja_dziedzina.py
(plik moja_dziedzina.json musi leżeć w wiedza/). Wzór: test_silnik.py."""
import copy
from pathlib import Path

from silnik import wczytaj_baze, wnioskuj_w_przod, wnioskuj_wstecz

baza = wczytaj_baze(Path(__file__).parent.parent / "wiedza" / "moja_dziedzina.json")
CEL = baza["cel"]

# (nr, rodzaj, dane wejściowe, oczekiwana decyzja, oczekiwany ślad w przód albo None)
PRZYPADKI = [
    ("T1", "typowy",   {"odleglosc": 1.0, "pogoda": "dobra",  "czas": "dużo", "bagaz": "ciężki"}, "pieszo",    ["P1", "R2"]),
    ("T2", "typowy",   {"odleglosc": 3.2, "pogoda": "dobra",  "czas": "dużo", "bagaz": "lekki"},  "hulajnoga", ["P2", "R9"]),
    ("T3", "granica",  {"odleglosc": 1.5, "pogoda": "deszcz", "czas": "mało", "bagaz": "ciężki"}, "autobus",   ["P1", "R3"]),
    ("T4", "brak",     {"odleglosc": 8.0, "pogoda": "dobra",  "czas": "mało", "bagaz": "lekki"},  None,        ["P3"]),
    ("T5", "konflikt", {"odleglosc": 0.4, "pogoda": "dobra",  "czas": "mało", "bagaz": "lekki"},  "pieszo",    ["P1", "R0"]),
    ("T6", "granica",  {"odleglosc": 1.6, "pogoda": "deszcz", "czas": "mało", "bagaz": "ciężki"}, "taksówka",  ["P2", "R11"]),
    ("T7", "granica",  {"odleglosc": 0.5, "pogoda": "deszcz", "czas": "mało", "bagaz": "lekki"},  "pieszo",    ["P1", "R0"]),
    ("T8", "typowy",   {"odleglosc": 2.2, "pogoda": "mróz",   "czas": "dużo", "bagaz": "lekki"},  "autobus",   ["P2", "R15"]),
]


def uruchom(b, wejscie):
    """Zwraca (wynik w przód, ślad w przód, wynik wstecz, zadane pytania)."""
    fakty, slad = wnioskuj_w_przod(b, wejscie)
    zadane = []

    def zapytaj(atrybut, powod):
        zadane.append(atrybut)
        return wejscie[atrybut]

    wstecz = wnioskuj_wstecz(b, CEL, {}, zapytaj, [])
    return fakty.get(CEL), slad, wstecz, zadane


ok = 0
for nr, rodzaj, wejscie, oczekiwane, oczekiwany_slad in PRZYPADKI:
    w_przod, slad, wstecz, zadane = uruchom(baza, wejscie)
    w_przod_ok = w_przod == oczekiwane and (oczekiwany_slad is None or slad == oczekiwany_slad)
    wstecz_ok = wstecz == oczekiwane and len(zadane) == len(set(zadane))
    status = "OK " if w_przod_ok and wstecz_ok else "BŁĄD"
    ok += w_przod_ok and wstecz_ok
    print(f"[{status}] {nr} {rodzaj:8} {wejscie} -> w przód: {w_przod} ({' -> '.join(slad)}), "
          f"wstecz: {wstecz}, pytań: {len(zadane)}")

# Konflikt reguł (T5): R0 i R1 pasują jednocześnie. Wygrywa R0, bo stoi wyżej.
# Po przeniesieniu R0 na koniec listy wynik musi się zmienić na rower (R1).
przestawiona = copy.deepcopy(baza)
r0 = next(r for r in przestawiona["reguly"] if r["id"] == "R0")
przestawiona["reguly"].remove(r0)
przestawiona["reguly"].append(r0)
wejscie_konflikt = PRZYPADKI[4][2]
w_przod, slad, wstecz, _ = uruchom(przestawiona, wejscie_konflikt)
konflikt_ok = w_przod == "rower" and wstecz == "rower"
ok += konflikt_ok
print(f"[{'OK ' if konflikt_ok else 'BŁĄD'}] T5b R0 na końcu listy -> w przód: {w_przod} ({' -> '.join(slad)}), "
      f"wstecz: {wstecz}  (kolejność reguł zmienia wynik)")

print(f"\nZaliczone przypadki: {ok}/{len(PRZYPADKI) + 1}")
