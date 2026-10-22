# Dojazd na uczelnię — system ekspertowy (IWiMU, Z2)

Autor: Oleksandr Bilous · nr albumu 105799 · gr. 5

System doradza studentowi sposób dojazdu na zajęcia: **pieszo, rower, hulajnoga, autobus albo taksówka**.
Bierze pod uwagę odległość do uczelni, pogodę, zapas czasu i bagaż. Wiedza (21 reguł) leży w pliku
`wiedza/moja_dziedzina.json`, a silnik `se/silnik.py` wnioskuje na niej w przód i wstecz.

## Uruchomienie

Wszystkie polecenia uruchamiasz z głównego katalogu repozytorium:

```
python se/sprawdz_format.py wiedza/moja_dziedzina.json   # format bazy: 0 błędów, same [TAK]
python se/test_silnik.py                                 # autotest silnika: 5/5
python se/test_moja_dziedzina.py                         # testy mojej bazy: 9/9
python se/silnik.py                                      # w przód + konsultacja wstecz
```

## Struktura bazy

| Poziom | Atrybuty |
|---|---|
| wejście | `odleglosc` (liczba, km, zakres 0,2–20), `pogoda` (dobra / deszcz / mróz), `czas` (mało / dużo), `bagaz` (lekki / ciężki) |
| wniosek pośredni | `dystans` (blisko ≤ 1,5 km / daleko 1,5–6 km / bardzo_daleko > 6 km) — reguły P1–P3 |
| cel | `decyzja` (pieszo / rower / hulajnoga / autobus / taksówka) — reguły R0–R17 |

Łańcuch: `odleglosc` → `dystans` → `decyzja`, np. P1 (`odleglosc <= 1.5` → `dystans = blisko`), potem R2
(`dystans = blisko` ORAZ `pogoda = dobra` ORAZ `czas = dużo` → `decyzja = pieszo`).

## Konsultacja w trybie wstecz

```
> python se/silnik.py
=== Wnioskowanie w przód ===
Wynik: hulajnoga | reguły: P2 -> R9

=== Wnioskowanie wstecz ===
Jaka jest odległość do uczelni (km)? 1,2
Jaka jest pogoda? (dobra/deszcz/mróz) dobra
Ile masz zapasu czasu przed zajęciami? (mało/dużo) dużo
Polecam: pieszo
Reguły: P1 -> R2
```

**Dlaczego te pytania?** Silnik zaczyna od celu `decyzja` i sprawdza reguły po kolei. Pierwsza jest R0
(`odleglosc <= 0.5` ORAZ `bagaz = lekki`), więc najpierw pyta o odległość; 1,2 km nie spełnia
pierwszego warunku, więc R0 odpada od razu, bez pytania o bagaż. W R1 warunek `dystans = blisko` to
wniosek pośredni — silnik ustala go regułą P1 z już znanej odległości (bez nowego pytania), a potem
pyta o pogodę i czas. Przy „dużo” R1 odpada, a R2 korzysta z zapamiętanych odpowiedzi i daje „pieszo”.
**O bagaż system nie zapytał wcale**, bo na krótkiej trasie przy dobrej pogodzie bagaż nie wpływa na
decyzję — 3 pytania zamiast 4.

## Kolejność reguł (strategia rozwiązywania konfliktów)

Wygrywa pierwsza pasująca reguła, dlatego reguła R0 („do 500 m z lekkim bagażem zawsze pieszo”) stoi
przed R1–R6: dla 0,4 km, dobrej pogody i mało czasu pasują jednocześnie R0 (pieszo) i R1 (rower), a
wygrywa R0, bo na tak krótkiej trasie wyjmowanie roweru albo czekanie na autobus trwa dłużej niż cały
spacer. Po przeniesieniu R0 na koniec listy wynik zmienia się na „rower” (test T5b).

## Dane bez odpowiedzi (luka w bazie)

Dla trasy powyżej 6 km, przy małym zapasie czasu i lekkim bagażu (np. 8 km, mało, lekki) żadna reguła
decyzji nie pasuje i system zwraca `None` (test T4). To świadoma luka: ekspert nie wskazał jednoznacznej
odpowiedzi (autobus może nie zdążyć, taksówka dla lekkiego bagażu jest droga). Do uzupełnienia po
weryfikacji bazy na spotkaniu 3.

## Zmiany względem Z1

- dodano regułę R0 (bardzo krótka trasa, ≤ 0,5 km, z lekkim bagażem → pieszo) — zmienia wynik dwóch
  liści drzewa dla najkrótszych tras,
- dodano trzecią wartość wniosku `dystans = bardzo_daleko` (> 6 km, poza zakresem przykładów z Z1)
  z regułami P3, R16, R17; zakres `odleglosc` rozszerzono do 20 km,
- reguły P1, P2 i R1–R15 przepisano z drzewa Z1 bez zmian znaczenia (P2 ograniczono z góry do 6 km).
