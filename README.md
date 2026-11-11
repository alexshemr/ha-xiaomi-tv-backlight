# Xiaomi TV Backlight for Home Assistant

Optional local automation for [Xiaomi TV Backlight Control](https://github.com/alexshemr/xiaomi-tv-backlight-control).

The TV app primarily controls backlight from the remote, including reusing the
PatchWall button after replacing the Xiaomi launcher. This integration adds a
backlight number for automations. For example, dim the screen to its minimum when
sleep mode starts.

## Tested setup

- Xiaomi MiTV-MSSP1 (nino), Android TV 9, firmware PI.5925.
- Home Assistant Container 2026.10.1.
- Pairing by code, physical backlight control and synchronization with the TV app
  were tested. Other Xiaomi firmware must be checked for `picture_backlight`
  support.

## Install with HACS

1. Install the [TV APK](https://github.com/alexshemr/xiaomi-tv-backlight-control/releases)
   and complete its one-time permission setup.
2. In HACS, open **Custom repositories**.
3. Add `https://github.com/alexshemr/ha-xiaomi-tv-backlight` and select
   **Integration**.
4. Download **Xiaomi TV Backlight Control** and restart Home Assistant.

This is a HACS custom repository. Manual installation is also supported by
copying `custom_components/xiaomi_tv_backlight` to your HA configuration directory
and restarting.

## Pair

1. On the TV app, select **Find Home Assistant**, or enter the HA server URL.
2. Open **Pair with Home Assistant** to show a six-digit code.
3. In HA, open **Settings → Devices & services** and configure the discovered TV.
   Alternatively, use **Add integration → Xiaomi TV Backlight Control** and enter
   the TV IP address. For a custom port, enter the full API URL.
4. Enter the code before it expires.

Pairing expires in two minutes and closes after five unsuccessful attempts.
Re-pairing replaces the integration token, so an older pairing must be removed
and added again. No MQTT broker is required.

The app advertises its API through mDNS. Discovery requires multicast to reach
HA and the TV. Manual address entry works when mDNS is unavailable but direct
HTTP connectivity is allowed. The selected HA server address in the app is used
for the setup link. Control requests go directly from HA to the TV.

## Entities

| Entity | Behavior |
| --- | --- |
| Backlight number | 0–100%, step 1, current hardware backlight setting |
| Connection binary sensor | Diagnostic indication that the TV API responds |

The state updates every 15 seconds and after each command. When the TV is
unreachable, the number displays **0%** and Connection turns off. This fallback
does not report an actual hardware level. Commands are not queued for the next
wake-up. The integration cannot wake a TV whose network connection sleeps.

## Example automation

Create a Sleep mode toggle in HA, then adapt the entity IDs below to your setup.
The connection condition avoids sending a command to a sleeping or offline TV.

```yaml
alias: Dim TV when sleep mode starts
triggers:
  - trigger: state
    entity_id: input_boolean.sleep_mode
    to: "on"
conditions:
  - condition: state
    entity_id: binary_sensor.xiaomi_tv_connection
    state: "on"
actions:
  - action: number.set_value
    target:
      entity_id: number.xiaomi_tv_backlight
    data:
      value: 0
mode: single
```

Use the actual number and connection entity IDs created for your TV. This
automation changes only backlight and runs when the TV is reachable. Add a
separate automation to restore your preferred daytime level if desired.

## Migration and troubleshooting

After validating this integration, update dashboards and automations to use its
number entity and remove the previous REST sensor/template package. The TV API
keeps the legacy token compatible for migration.

If pairing fails, open the code screen again and verify port 8765 is reachable
from HA. If control fails, check the TV app has WRITE_SECURE_SETTINGS permission.
If a remote shortcut fails after reboot, enable the app accessibility service
and use TV app 0.4.1 or newer.

The app uses a local HTTP API with a dedicated TV token. Keep port 8765 on your
trusted LAN. Each TV has its own stable identity and token.

## Development checks

```sh
python -m pip install -r requirements-test.txt
python -m unittest discover -s tests -p 'test_*.py'
```

HTTP client tests cover authentication, pairing responses, invalid values and
read/write boundaries.

[Краткая инструкция на русском](README.ru.md)
