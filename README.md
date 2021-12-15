# PR_DKE_WS21
Implementierung von Informationssystemen in einem Bahnunternehmen.

Verantwortlicher Fahrplansystem: Alexander Wolf<br>
Verantwortlicher Flottensystem: Anil Yildiz<br>
Verantwortlicher Streckensystem: Thomas Weißenbacher

Zum (erstmaligen) Starten des Systems:
1. Repository klonen
2. ./install.sh
3. ./run.sh

Bei weiteren Starts muss nur mehr run.sh ausgeführt werden.
Falls sich Dependencies ändern, kann install.sh erneut ausgeführt werden.

Bei keinen Argumenten versucht run.sh alle Systeme zu starten.<br>
Es können auch die Systeme angegeben werden, die gestartet werden sollen.<br>
Reihenfolge der Argumente spielt keine Rolle.<br>
Argumente:<br>
fa (Fahrplansystem)<br>
fl (Flottensystem)<br>
st (Streckensystem)<br>
ti (Ticketsystem)<br>
q  (quiet - Keine Flask error messages anzeigen)<br>

Also z.B. <br>
./run.sh fa q<br>
oder<br>
./run.sh st ti fl <br>
