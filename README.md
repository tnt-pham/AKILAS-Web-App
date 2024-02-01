Dieses Projekt wurde entworfen und getestet auf Windows 10 mit der Python-Version 3.8.17.  
Schau gerne auf [GitHub](https://github.com/tnt-pham/AKILAS-GUI) vorbei für Updates!

## BESCHREIBUNG
Diese Web-App bietet eine Lernplattform für Schulkinder. Es gibt zwei Aufgaben, eine zu Textverständnis und eine zu Argumentation. Nachfolgend ist wird die Installation und Ausführung beschrieben. Es wird vor allem auf den Inhalt der Datei BA.pdf verwiesen, da sie ausführliche Erläuterungen zu den Funktionen enthält. Die Funktionsweise befindet sich in Kapitel 4.1. BA.pdf befindet sich im gleichen Ordner wie diese README.

##  REQUIREMENTS
Schritt 0:  
- Erstelle und aktiviere eine neue conda-Umgebung.  
> conda create -n myenv python=3.8  

> conda activate myenv  

Schritt 1:  
- Installiere die erforderlichen Bibliotheken.  
-- Stelle sicher, dass der folgende Befehl auf der Kommandozeile im Hauptverzeichnis des Projekts ausgeführt wird.  
> python -m pip install -r requirements.txt  

Schritt 2:  
- Öffne die interaktive Pythonumgebung mit dem Befehl `python` und lade das NLTK-Package herunter.  
> import nltk  

> nltk.download('punkt')  

Schritt 3:  
- In der Datei BA.pdf werden einige technische Details beschrieben wie zum Beispiel  
-- das Setup im Kapitel 4.2.2 Infrastruktur  
-- Informationen zu den einzelnen Dateien im Kapitel 4.2.3 Ordnerstruktur  

Schritt 4:  
- Ist das Setup gelungen, sodass die Evaluationsmodelle auf einem Server liegen und der Port getunnelt wurde, so kann die Web-App gestartet werden.  
-- Der folgende Befehl wird nun auf der Kommandozeile im Hauptverzeichnis des Projekts ausgeführt.  
> flask run  

Schritt 5:  
- Unter dem folgenden Link kann die Web-App im Browser betrachtet werden:  
-- `http://127.0.0.1:5000/`  

## INFRASTRUKTUR

Das folgende Schaubild stellt die Beziehung zu den anderen verwendeten Programmen dar. Mehr dazu in der Datei BA.pdf im Kapitel 4.2.2 zu Infrastruktur.  

<img src="\static\img\Infrastruktur_Schaubild.png" width="70%" />  


## AUTOR
Thomas N. T. Pham  
University of Potsdam, February 1st, 2024  
[My Github](https://github.com/tnt-pham/AKILAS-GUI)  
For more information or questions, feel free to contact pham.tnt@proton.me
