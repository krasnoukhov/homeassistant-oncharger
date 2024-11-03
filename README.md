# Home Assistant Oncharger EV integration

The Oncharger integration pulls data from either local network or Oncharger cloud.

Tested with:
* [32A one-phase Wi-Fi charger](https://oncharger.com.ua/ua/p1422951216-oncharger-gbt-32a.html)

## Highlights

### Have your charger sensors at a glance

<img src="https://github.com/krasnoukhov/homeassistant-oncharger/assets/944286/cf51f9e0-54d9-41ae-809e-9439d65de051" alt="sensors" width="400">

### Charge your car at the maximum power

* If you have a smart meter that reports current on the phase to a specific entity in HA
* This entity can be used to have this integration auto-adjust Oncharger current up to a specific threshold

<img src="https://github.com/krasnoukhov/homeassistant-oncharger/assets/944286/a809fe0f-c10d-4d22-a8e2-35469fff9ad9" alt="boost" width="400">

For three-phase charger your entity should represent the maximum current on any of the phases.
You can use "Combine the state of several sensors" helper for that.

### Use the UI to set up integration

<img src="https://github.com/krasnoukhov/homeassistant-oncharger/assets/944286/4d152f06-bf6f-4656-90c8-462e814c1494" alt="setup" width="400">

## Installation

### Via HACS

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=krasnoukhov&repository=homeassistant-oncharger&category=Integration)

* Search for "Oncharger" on HACS tab in Home Assistant
* Click on three dots and use the "Download" option
* Follow the steps
* Restart Home Assistant

### Manual Installation (not recommended)

* Copy the entire `custom_components/oncharger/` directory to your server's `<config>/custom_components` directory
* Restart Home Assistant
