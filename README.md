# Bazarr Translator

Bazarr Translator is an automation tool designed to check Bazarr's wanted movies/episodes list, find subtitles via opensubtitles.org, and use LibreTranslate to translate them to the correct language if needed. If no translation is found, it will attempt to use LibreTranslate to perform the translation and upload the subtitles.

## Requirements

- Docker
- Docker Compose (for easier setup)
- Cron (for automatic execution)
- LibreTranslate
- Sonarr
- Radarr
- Bazarr

## Docker Setup

#### Using Docker Compose

For an easy setup, you can use Docker Compose:

1. Run the following command to start the project using Docker Compose:

    ```bash
    docker-compose up -d
    ```

#### Using Docker CLI

Alternatively, you can run the project with Docker directly by using the following command:

```bash
sudo docker run \
        -e "LIBRETRANSLATE_ENABLED=true" \
        -e "LIBRETRANSLATE_SERVER=YOUR_LIBRETRANSLATE_SERVER_URL" \
        -e "BAZARR_SERVER=http://localhost:6767" \
        -e "BAZARR_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
        -e "RADARR_SERVER=http://localhost:7878" \
        -e "RADARR_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
        -e "SONARR_SERVER=http://localhost:8989" \
        -e "SONARR_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
        bazarrtranslator:latest
```

## Setting Up Cron for Automatic Execution

To ensure that the Bazarr Translator runs periodically, you can set up a cron job. Follow these steps:

#### Open Crontab

Edit your crontab configuration by running the following command:

```bash
crontab -e
```

#### Add Cron Job for Automatic Execution

Add the following line to run the Bazarr Translator every day at midnight (you can adjust the timing as per your needs):

```bash
0 0 * * * /usr/bin/docker run \
        -e "LIBRETRANSLATE_ENABLED=true" \
        -e "LIBRETRANSLATE_SERVER=YOUR_LIBRETRANSLATE_SERVER_URL" \
        -e "BAZARR_SERVER=http://localhost:6767" \
        -e "BAZARR_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
        -e "RADARR_SERVER=http://localhost:7878" \
        -e "RADARR_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
        -e "SONARR_SERVER=http://localhost:8989" \
        -e "SONARR_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
        bazarrtranslator:latest
```

This cron job will run the Docker container every day at midnight. You can modify the schedule based on your requirements (e.g., run it every hour by changing `0 0 * * *` to `0 * * * *`).

#### Save and Exit

After adding the cron job, save and exit the crontab editor. This will automatically schedule the task to run periodically.

## Environment Variables

Make sure to replace the placeholders with your actual values:

- `LIBRETRANSLATE_ENABLED`: Set to `true` to enable translation using LibreTranslate.
- `LIBRETRANSLATE_SERVER`: The URL of your LibreTranslate server (use a placeholder if you don't have one).
- `BAZARR_SERVER`: URL for your Bazarr server.
- `BAZARR_API_KEY`: Your Bazarr API key.
- `RADARR_SERVER`: URL for your Radarr server.
- `RADARR_API_KEY`: Your Radarr API key.
- `SONARR_SERVER`: URL for your Sonarr server.
- `SONARR_API_KEY`: Your Sonarr API key.

## Usage

Once the container is running (manually or automatically), the tool will automatically check for wanted movies/episodes in Bazarr. If no subtitles are found, it will use LibreTranslate to perform the translation and upload the translated subtitles.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
