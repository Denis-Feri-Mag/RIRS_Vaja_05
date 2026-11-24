# 07. Pregled projekta

Pregledal sem projekt Glass, prebral dokumentacijo in kodo ter aplikacijo pognal lokalno z Flask, PostgreSQL in Vite. Ob zagonu v projektu ni bilo testov in tudi ne nastavitve za lint.

## US-01 Rezervacija mize z opombo

Prijavljen gost lahko rezervira mizo z datumom, uro, številom oseb in opombo. Rezervacija je potrjena in vidna na seznamu. Trajanja ni mogoče vnesti, vedno je 120 minut, miza pa je zasedena za celoten dan po UTC, ne samo za termin.

Ocena: delno ustreza.

## US-02 Pregled rezervacij in opomb

Natakar izbere dan in vidi samo potrjene rezervacije: uro, mizo, gosta in opombo. Odpovedanih ni na seznamu. Ure so izpisane po UTC, kar se ujema z vnosom.

Ocena: ustreza.

## US-03 Naročilo na mizi

Natakar zasede mizo, odpre eno naročilo, tudi brez rezervacije, in doda postavke s statusom čaka ter ceno iz jedilnika. Vmesnik ne poveže naročila z rezervacijo, zaloga pa se zmanjša šele ob zaključku, zato isto jed lahko doda večkrat, tudi če količina preseže zalogo.

Ocena: delno ustreza.

## US-04 Kuhinjski pregled

Kuhar vidi jedi iz kuhinje po mizah, brez pijač. Zaslon se osveži vsakih 5 sekund, zaključeno naročilo izgine. Jedi se shranijo kot hod 1, zato se več hodov v praksi ne zgodi.

Ocena: ustreza.

## US-05 Status jedi v teku strežbe

Kuhar jed označi samo kot pripravljeno, natakar vidi status in jo označi kot postreženo, ko je pripravljena. Pijačo iz bara postreže sam.

Ocena: ustreza.

## US-06 Zaključek naročila in sprostitev mize

Zaključi se lahko samo odprto naročilo. Aplikacija sešteje znesek, zapiše transakcijo prodaje, zmanjša zalogo, naročilo označi kot zaključeno in mizo sprosti.

Ocena: ustreza.

## US-07 Skladišče in razpoložljivost robe

Kuhar vidi samo zalogo kuhinje, natakar vidi kuhinjo in bar, razprodane postavke ni mogoče dodati, količine ročno ne vpisujeta. Prikazana zaloga ne upošteva odprtih naročil.

Ocena: delno ustreza.

## Povzetek MVP

| Zgodba | Ocena |
| --- | --- |
| US-01 | delno ustreza |
| US-02 | ustreza |
| US-03 | delno ustreza |
| US-04 | ustreza |
| US-05 | ustreza |
| US-06 | ustreza |
| US-07 | delno ustreza |

## Ostale zgodbe

US-12 odpoved rezervacije deluje v celoti. Delno sta pokrita US-09, kjer je samo pregled prodaje, US-13, kjer je jedilnik viden šele po prijavi, in US-14, kjer hoda ni mogoče izbrati, ker se jed shrani kot hod 1. Ni implementirano: US-08 nabava, US-10 obračun, US-11 urejanje jedilnika, US-15 prenos naročila in US-16 izvoz v PDF.

## Dodatno

Administrator lahko ureja račune natakarjev in kuharjev. Status rezervirana je v modelu, v kodi pa se nikoli ne nastavi.
