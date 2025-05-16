import os

from discord_webhook import DiscordWebhook

sent_missing_env_var_message = False


def log_discord_message(message: str, log_console: bool = True):
    if log_console:
        print(message)

    discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    if discord_webhook_url is not None:
        DiscordWebhook(url=discord_webhook_url, content=message).execute()
    else:
        global sent_missing_env_var_message
        if not sent_missing_env_var_message:
            sent_missing_env_var_message = True
            print('The environment variable DISCORD_WEBHOOK_URL should be set in order for discord logs to work.')
