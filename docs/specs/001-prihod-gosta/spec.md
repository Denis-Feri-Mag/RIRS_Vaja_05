# 001 Prihod gosta

## Zgodba

Kot natakar želim označiti, da je gost rezervacije prispel, da vem, kdo je že v lokalu, in da gost te rezervacije ne more več odpovedati.

Zgodbe še ni med US-01 do US-16. V modelu `Rezervacija` je status `gost_prisel` že predviden, v kodi pa se nikoli ne nastavi. Na strani Moje rezervacije je napis za ta status že pripravljen. Natakar na seznamu dneva vidi samo potrjene rezervacije in jih lahko samo zaključi.

## Zahteve

1. Natakar lahko pri potrjeni rezervaciji označi prihod gosta.
2. Po oznaki ima rezervacija status `gost_prisel`.
3. Seznam rezervacij dneva pokaže potrjene in tiste, kjer je gost že prispel. Pri vsaki je viden status.
4. Dokler rezervacija ni zaključena, ista miza na isti dan ni prosta za novo rezervacijo. To velja tudi za status `gost_prisel`.
5. Gost take rezervacije ne more več odpovedati.
6. Natakar lahko rezervacijo po prihodu še vedno zaključi. Zaključek sprosti mizo, kot že velja zdaj.
7. Gost, kuhar in neregistriran uporabnik prihoda ne morejo označiti. Administrator sme, ker dekorator `samo` to že dovoli tudi pri drugih potih natakarja.
8. Gost na strani Moje rezervacije vidi status "gost je prišel". Gumba za odpoved pri tej rezervaciji ni.

Nova shema ali sprememba `init_db.py` ni potrebna, ker status v modelu že obstaja.

## Sprejemni kriteriji

1. `POST /api/rezervacije/{id}/prihod` z žetonom natakarja pri rezervaciji s statusom `potrjena` vrne 200 in `"status": "gost_prisel"`.
2. Isti klic pri rezervaciji, ki ni `potrjena`, vrne 400. Če rezervacija ne obstaja, vrne 404.
3. Klic z žetonom gosta ali kuharja vrne 403. Brez žetona vrne 401.
4. `GET /api/rezervacije/dan?datum=...` vrne potrjene rezervacije in rezervacije s statusom `gost_prisel` za ta dan. Odpovedane in zaključene niso na seznamu. V JSON je polje `status`.
5. Ko ima miza tisti dan rezervacijo s statusom `gost_prisel`, nova rezervacija iste mize istega dne vrne 409.
6. `POST /api/rezervacije/{id}/odpoved` z žetonom gosta pri statusu `gost_prisel` vrne 400. Rezervacija ostane `gost_prisel`.
7. `POST /api/rezervacije/{id}/zakljucek` z žetonom natakarja pri statusu `gost_prisel` vrne 200 in `"status": "zakljucena"`.
8. Na strani natakarja je pri potrjeni rezervaciji gumb za oznako prihoda. Ko je gost prispel, je to razvidno in ostane gumb za zaključek.
9. Na strani Moje rezervacije se rezervacija s statusom `gost_prisel` izpiše z besedilom "gost je prišel" in brez gumba Odpovej.
10. Za novo pot in vmesnik obstajajo testi v `backend/tests` in na frontendu, po konvencijah v `AGENTS.md`.
