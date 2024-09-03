# Fooocus API Client
_a simple wrapper for [Fooocus](https://github.com/lllyasviel/Fooocus) that you can use to add image generation to your Discord or Telegram channel_

## In this repository:

- **bot_discord.py** a basic Discord bot that responds to '/focus' prompts with an image based on the prompt

- **bot_telegram.py** a basic Telegram bot that responds to '/focus' prompts with an image based on the prompt

- **chroma_calls.py** chromadb functions to store and retrieve the different styles.
  Will use a distance function to determine the best matching style based on the prompt

- **fc_methods.py** methods to generate an image from the Fooocus API,
  and change & store some config settings

- **fc_settings.py** a large array with all valid "styles",
  and a default config for the Fooocus API

- **or_calls.py** calls to the OpenRouter API to "enrich" the prompt

- **requirements.txt** libraries you need to install to run the code samples

- **utilities.py** functions for web- and file I/O
