# Fotobox

Eigenständige Fotobox-Anwendung: Kunde wählt ein Foto-Paket, bezahlt per
Karte über einen SumUp-Solo-Kartenleser, macht danach beliebig oft ein
Probefoto mit einer Fujifilm-X-T-Kamera (gPhoto2-Tethering) und druckt das
gewählte Bild über einen CUPS-Drucker aus.

## Voraussetzungen (Raspberry Pi 4/5, Raspberry Pi OS)

```bash
sudo apt install libgphoto2-dev libcups2-dev python3-pip
pip3 install -r requirements.txt
```

## Konfiguration

Beim ersten Start wird unter `~/.fotobox/config.yaml` eine Beispiel-Config
angelegt (aus `config/default_config.yaml`). Darin müssen mindestens
eingetragen werden, bevor die App produktiv läuft:

- `printer.cups_printer_name` (Name der CUPS-Warteschlange, `lpstat -p`)
- `sumup.api_key`, `sumup.merchant_code` (SumUp-Konto → Settings → For
  Developers → API Keys)
- `sumup.reader_id` (wird einmalig im Admin-Bereich am Gerät durch Koppeln
  des Solo-Readers ermittelt, siehe unten)

Preise/Pakete stehen unter `packages:` und können direkt in der Datei oder
über den Admin-Bereich am Gerät bearbeitet werden.

**Hinweis zur SumUp Cloud API:** Die in `payment/sumup_client.py`
verwendeten Endpunkt-Pfade und Feldnamen folgen dem öffentlich
dokumentierten Aufbau der SumUp Cloud API, konnten aber beim Erstellen
dieses Clients nicht direkt gegen `developer.sumup.com/api` verifiziert
werden (die Seite blockiert automatisierte Anfragen). **Vor dem
Produktiveinsatz unbedingt mit einem eigenen SumUp-Entwicklerkonto in der
Sandbox testen** und die Anfragen bei Bedarf an die aktuelle API-Referenz
anpassen.

## Ohne Hardware entwickeln/testen

```yaml
general:
  mock_hardware: true
```

Damit werden Kamera, Drucker und SumUp durch Attrappen ersetzt (`camera
immer "verbunden"`, Zahlung schlägt nie fehl, Druckaufträge werden nur
geloggt) – der komplette Ablauf lässt sich so am Bildschirm durchklicken.

```bash
python3 -m fotobox.main --config ./dev_config.yaml
```

## Admin-Bereich

Vom Startbildschirm aus: 5x schnell hintereinander in die untere linke Ecke
tippen. Ohne gesetzte PIN ist der Zugang zunächst offen; unter "PIN ändern"
sollte beim Ersteinrichten sofort eine PIN gesetzt werden. Im Admin-Bereich:
Preise/Kopien pro Paket, Drucker, SumUp-Zugangsdaten und Reader-Kopplung.

## Autostart im Kiosk-Modus

```bash
cp deploy/fotobox.service /etc/systemd/system/
sudo systemctl enable --now fotobox.service
```

`deploy/kiosk.sh` startet die App im Vollbild und blendet Mauszeiger/
Bildschirmschoner aus (benötigt `unclutter`, `xset`).

## Tests

```bash
pytest fotobox/tests
```

Deckt Config-Validierung, die Status-Maschine (kompletter Ablauf inkl.
Wiederholen/Timeout) sowie den SumUp-Client und Admin-Bereich (gegen Mocks)
ab. Die Kivy-Oberfläche selbst braucht einen Bildschirm/echtes Display und
lässt sich nur manuell bzw. auf dem Zielgerät testen.
