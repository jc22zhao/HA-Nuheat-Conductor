## ⚠️ Project Status: Looking for a New Maintainer

I no longer have access to Nuheat Conductor thermostats, and I will no longer be actively developing or maintaining this integration.

The code is functional as of the last release, but I won't be fixing bugs, or adding features going forward.

If you're interested in taking over maintenance of this project, please reach out via [GitHub Issues](https://github.com/SmilesGalore/HA-Nuheat-Conductor/issues) or [Discussions](https://github.com/SmilesGalore/HA-Nuheat-Conductor/discussions) — I'm happy to hand off the repository or add you as a collaborator.

---

# Nuheat Conductor Thermostat Integration for Home Assistant

A custom Home Assistant integration for Nuheat Conductor radiant heating thermostats. Control and monitor your Nuheat Conductor heating systems directly from Home Assistant.

This integration is for **Nuheat Conductor** thermostats. For Nuheat Signature thermostats, please use the official [Nuheat Integration](https://www.home-assistant.io/integrations/nuheat/) in Home Assistant.

## Features

* ⚡ **Real-time Push Notifications** - Instant state updates via SignalR WebSocket connection — changes in the Nuheat app appear in Home Assistant almost immediately
* 🌡️ **Full Climate Control** - Set target temperatures, heating modes, and presets through Home Assistant's climate platform
* 🔐 **Secure OAuth2 Authentication** - Browser-based OAuth2 Authorization Code flow — no API keys required
* 📊 **Live Monitoring** - Current temperature, heating status, and connection state
* 🗓️ **Schedule & Hold Support** - Auto (schedule), Hold, and Permanent Hold presets
  * Please note: currently the Nuheat API does not allow access to viewing, editing, or adding schedules created in the Nuheat Conductor app. Using Auto will apply the schedule that is currently selected in the Nuheat Conductor app.
* 👥 **Group Control** - Manage Home/Away modes for groups
* 🔌 **Offline Resilience** - Offline thermostats remain visible with last known settings; automations continue to run for online thermostats
* 🔄 **Auto-discovery** - Automatically discovers all thermostats and groups on your Nuheat account
* 🔁 **Automatic Reconnection** - SignalR connection recovers automatically after network interruptions, with 90-second polling as a fallback

## Prerequisites

* Home Assistant instance (core-2024.1.0 or later)
* Nuheat Conductor thermostat system
* Nuheat account credentials

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots menu (top right) → **Custom repositories**
3. Add repository URL: `https://github.com/SmilesGalore/HA-Nuheat-Conductor`
4. Select category: **Integration**
5. Click **Add**
6. Find "Nuheat Conductor" in HACS and click **Download**
7. Restart Home Assistant

### Manual Installation

1. Download or clone this repository
2. Copy the `nuheat_conductor` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

Your directory structure should look like:

```
config/
├── custom_components/
│   └── nuheat_conductor/
│       ├── __init__.py
│       ├── climate.py
│       ├── config_flow.py
│       ├── const.py
│       ├── manifest.json
│       ├── signalr.py
│       └── strings.json
```

## Configuration

### Adding the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Nuheat Conductor"
4. Click on the integration to begin setup
5. You'll be redirected to Nuheat's login page in your browser
6. Enter your Nuheat credentials and authorize Home Assistant
7. You'll be redirected back to Home Assistant with the integration configured

### OAuth2 Setup

This integration uses OAuth2 Authorization Code flow for secure authentication:

* No need to enter credentials directly in Home Assistant
* Tokens are securely stored and automatically refreshed
* Authorization happens in your web browser

**Important:** For the best experience during OAuth setup:
* Login to Home Assistant in a browser to complete the setup
* Do not setup from the Home Assistant mobile app, as OAuth will open in your device's browser
* Use the same device and browser throughout the entire setup process

## Usage

Once configured, your Nuheat thermostats and groups will appear as climate entities in Home Assistant.

### Thermostat Presets

Each thermostat supports three presets:

| Preset | Description |
|--------|-------------|
| **Auto** | Thermostat follows its Nuheat schedule |
| **Hold** | Holds the current temperature until the next scheduled event |
| **Permanent Hold** | Holds the temperature indefinitely until manually changed |

When you adjust the temperature:
- If the thermostat is on **Auto**, it switches to **Hold** automatically
- If it's already on **Hold** or **Permanent Hold**, it stays on that preset
- If no schedule is configured, changes always use **Permanent Hold**

### Group Control

Thermostat groups appear as separate climate entities with Home/Away presets:

| Preset | Description |
|--------|-------------|
| **Home** | Disables away mode — thermostats follow their normal schedules |
| **Away** | Enables away mode — thermostats switch to the group's away setpoint |

### Basic Automation Examples

**Set Temperature:**

```yaml
service: climate.set_temperature
target:
  entity_id: climate.nuheat_living_room
data:
  temperature: 22
```

**Set Preset Mode:**

```yaml
service: climate.set_preset_mode
target:
  entity_id: climate.nuheat_living_room
data:
  preset_mode: "Permanent Hold"
```

**Set Group Away:**

```yaml
service: climate.set_preset_mode
target:
  entity_id: climate.group_main_floor
data:
  preset_mode: "Away"
```

**View in Lovelace:**

```yaml
type: thermostat
entity: climate.nuheat_living_room
```

### Available HVAC Modes

* `heat` - Heating enabled
* `off` - Heating disabled (sets thermostat to minimum temperature)

### Offline Thermostat Behaviour

When a thermostat goes offline:
- The entity remains visible in Home Assistant with last known settings
- The entity shows `connection_status: Offline` in its attributes
- Temperature and preset controls remain available — commands are silently skipped for offline thermostats but **do not prevent automations from continuing** to update other thermostats
- The entity is only marked fully unavailable after 3 consecutive failed API polls

## Real-time Updates

This integration uses **SignalR WebSocket push notifications** to receive instant updates from Nuheat's servers. When you make a change in the Nuheat app or on the thermostat itself, Home Assistant reflects the change almost immediately — no waiting for the next poll cycle.

If the SignalR connection is unavailable (e.g. during network interruptions), the integration automatically falls back to polling every 90 seconds, and reconnects SignalR as soon as possible.

## API Endpoints

This integration connects to:

* **Identity Server:** `https://identity.nam.mynuheat.com`
* **API Server:** `https://api.nam.mynuheat.com`
* **Notification Hub:** `https://api.nam.mynuheat.com/v1/changenotifications`

## Troubleshooting

### OAuth Authentication Issues

#### "Already in progress" Error After Failed Setup

**Symptoms:**
* Setup fails during OAuth redirect
* When you try to add the integration again, you see "Configuration flow is already in progress"

**Solution:**
1. **Restart Home Assistant** to clear the stuck flow state
2. After restart, try adding the integration again
3. Use the same device and browser throughout the entire setup process

**Prevention:**
* Always use the Home Assistant web interface (not mobile app) for initial setup
* Keep the browser window open during OAuth flow
* Ensure a stable internet connection during setup

#### OAuth Redirect Fails

**Symptoms:**
* Browser redirects to Nuheat but doesn't return to Home Assistant

**Solution:**
1. Verify your Home Assistant external URL is configured correctly:
   * Go to **Settings** → **System** → **Network** → **External URL**
2. If using Nabu Casa Cloud, ensure your subscription is active
3. Try using the local network URL instead of external URL during setup
4. Restart Home Assistant and try again

#### Setting Up on iPhone / iOS (Nuheat App Interference)

**Symptoms:**
* OAuth redirect opens the Nuheat app instead of completing in the browser
* The Nuheat app asks about Alexa authorization
* After dismissing, you see an "authentication disallowed" error in Home Assistant

**Cause:**
iOS Universal Links intercept the Nuheat identity server URL and redirect it to the Nuheat app, which is designed for Alexa authentication — not Home Assistant. This happens in both Safari and the Home Assistant app on iOS.

**Solutions (in order of preference):**

1. **Use a desktop/laptop browser** *(recommended)* — Complete the initial setup from a computer browser. Once configured, the integration runs normally and you can control thermostats from your phone as usual. Setup only needs to be done once.

2. **Temporarily uninstall the Nuheat app** — Without the app installed, iOS cannot redirect to it and Safari will complete the OAuth flow normally. Reinstall the Nuheat app after the integration is configured.

3. **Try Firefox on iOS** — Firefox handles Universal Links differently from Safari and may complete the OAuth flow without redirecting to the Nuheat app.

### Integration Not Appearing

**Solution:**
1. Ensure all files are in `config/custom_components/nuheat_conductor/` (including `signalr.py`)
2. Restart Home Assistant completely (not just reload)
3. Check logs at **Settings** → **System** → **Logs** and search for "nuheat"

### Authentication Failures

**Solution:**
1. Verify your Nuheat credentials at [mynuheat.com](https://www.mynuheat.com)
2. Try removing and re-adding the integration:
   * **Settings** → **Devices & Services** → **Nuheat Conductor** → three dots → **Delete**
   * Restart Home Assistant
   * Add the integration again

### No Thermostats Discovered

**Solution:**
1. Verify your thermostats are visible in the Nuheat mobile app
2. Check that thermostats are online and communicating
3. Enable debug logging (see below) and look for API errors
4. Try reloading the integration: **Settings** → **Devices & Services** → **Nuheat Conductor** → **⋮** → **Reload**

### SignalR Not Connecting

If you see repeated "SignalR disconnected. Reconnecting..." messages in the logs:
1. Check your Home Assistant server has outbound WebSocket access to `api.nam.mynuheat.com`
2. The integration will continue to function via 90-second polling while SignalR is unavailable
3. SignalR will reconnect automatically — no action required

### Logs and Debugging

To enable detailed logging for troubleshooting, add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.nuheat_conductor: debug
```

Then restart Home Assistant and check logs at **Settings** → **System** → **Logs**.

## Support

Note: This project is no longer actively maintained (see status above).

* **Issues:** [GitHub Issues](https://github.com/SmilesGalore/HA-Nuheat-Conductor/issues)
* **Discussions:** [GitHub Discussions](https://github.com/SmilesGalore/HA-Nuheat-Conductor/discussions)
* **Home Assistant Community:** [Home Assistant Forums](https://community.home-assistant.io/)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

* Thanks to the Home Assistant community for their excellent documentation
* Nuheat for providing API access and SignalR notification support
* All contributors who help improve this integration

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial integration and is not affiliated with, endorsed by, or supported by Nuheat. Use at your own risk.

---

**Current Version:** 1.0.0-beta.9 (final release, unmaintained)
