# A/C Thermostat Controller

This project is designed to control Samsung SmartThings A/C units using a Python script. The script can automatically manage the temperature settings based on predefined schedules and modes.

## Features

- Automatically adjusts the temperature of A/C units based on predefined schedules.
- Supports multiple modes (e.g., winter, summer, off).
- Allows manual temperature setting for all units.

## Installation

1. Clone the repository

2. Install all required depencies:
   - `requests`
   - `toml`

3. Copy the example configuration files and edit them:
    ```sh
    cp configs/credentials.toml.example configs/credentials.toml
    cp configs/config.toml.example configs/config.toml
    ```

4. Edit `configs/credentials.toml` to include your SmartThings API token:
    ```toml
    token = "YOUR_SMARTTHINGS_API_TOKEN"
    ```

5. Edit `configs/config.toml` to configure your A/C units and schedules.

## Usage

1. Run the main script:
    ```sh
    python src/main.py
    ```

2. The script will automatically adjust the temperature settings based on the current time and the configured schedules.

## License

All right are reserved.
You don't have a license unless specifically granted.