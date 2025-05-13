# Fronius Load Management Monitoring (via Selenium + MQTT for Home Assistant)

This script monitors the output status of load management channels (e.g. 4-phase relay outputs) from a Fronius inverter via its local web interface. It uses Selenium to log in, load the load management page, and read the visual status indicators (green/red points) directly from the DOM.

Typical use case: monitoring the state of a 3-phase heating element (Ohm load) controlled via the inverter's relay outputs — but it can be used for any load connected via Fronius' load management system.

## Features

- Automated login to Fronius local web interface (tested with "Customer" user)
- DOM-based detection of relay status (up to 3 phases)
- MQTT publishing of state to Home Assistant
- Heartbeat/Watchdog topic with last update timestamp
- Lightweight long-running operation with minimal CPU/traffic
- Headless browser, no GUI required
- Optional: Trigger execution from HASS.Agent or Task Scheduler

## Requirements

- Python 3.10+
- Google Chrome + [matching chromedriver](https://chromedriver.chromium.org/downloads)
- Fronius inverter with local web interface (e.g. Gen24)
- MQTT broker (e.g. Mosquitto in Home Assistant)
- MQTT credentials

## Installation

1. Install Python dependencies:

   ```bash
   pip install selenium paho-mqtt

2. Download chromedriver.exe and place it in your script folder or system PATH.

3. Edit the script configuration:
- url = "http://192.168.X.X/"        # Inverter IP
- password = "PASSWORD"              # Customer password
- mqtt_broker = "192.168.X.X"        # MQTT broker IP
- mqtt_user = "youruser"
- mqtt_pass = "yourpassword"

## MQTT Topics
The script publishes:

loadmanagement/status/phase1 → on / off

loadmanagement/status/phase2 → on / off

loadmanagement/status/phase3 → on / off

loadmanagement/status/phase4 → on / off

loadmanagement/status/last_update → ISO timestamp of last update

## Example Home Assistant config:

mqtt:
  sensor:
    - name: Load Phase 1
      state_topic: "loadmanagement/status/phase1"
    - name: Load Phase 2
      state_topic: "loadmanagement/status/phase2"
    - name: Load Phase 3
      state_topic: "loadmanagement/status/phase3"
    - name: Load Phase 4
      state_topic: "loadmanagement/status/phase4"
    - name: Load Management Last Update
      state_topic: "loadmanagement/status/last_update"
      device_class: timestamp

## Notes
Fronius does not expose load management relay status via official API or Modbus – only via the web interface.

This script uses Selenium in headless mode to read the visual status from the DOM.

Designed to run continuously in the background (e.g. started via HASS.Agent, cron or autostart).

## License
MIT – feel free to use, modify, and share.

Contributions welcome – tested and maintained by a Home Assistant user for real-world load monitoring needs.