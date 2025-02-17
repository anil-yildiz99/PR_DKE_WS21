# PR_DKE_WS21
Implementierung von Informationssystemen in einem Bahnunternehmen.<br>

Verantwortlicher Fahrplansystem: Alexander Wolf<br>
Verantwortlicher Flottensystem: Anil Yildiz<br>
Verantwortlicher Streckensystem: Thomas Weißenbacher

Zum (erstmaligen) Starten des Systems:
1. Repository klonen
2. ./install.sh
3. ./run.sh

Bei weiteren Starts muss nur mehr run.sh ausgeführt werden.
Falls sich Dependencies ändern, kann install.sh erneut ausgeführt werden.

Bei keinen Parametern versucht run.sh alle Systeme zu starten.<br>
Es kann auch angegeben werden welche Systeme gestartet werden sollen.<br>
Reihenfolge der Parameter spielt keine Rolle.<br>
Parameter:<br>
fa (Fahrplansystem)<br>
fl (Flottensystem)<br>
st (Streckensystem)<br>
ti (Ticketsystem)<br>
q  (quiet - Keine Flask Informationen anzeigen)<br>

Also z.B. <br>
./run.sh fa q<br>
oder<br>
./run.sh st ti fl <br>

<br>
Admin-Login für lokales Fahrplansystem:<br>
Mitarbeiter-ID: 1<br>
Passwort: 1234<br>

<br>
Admin-Login für lokales Flottensystem:<br>
Mitarbeiter-Email: anil@hotmail.com<br>
Passwort: test<br>

<br>
Bis Februar 2022 ist das Fahrplansystem auch auf diesem VPS deployed:<br>
52.29.120.183
<br>
<br>
Technologie-Stack:<br>
Flask, Python, Jinja, SQLite<br>

