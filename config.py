import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Config:
    bot_token: str
    admin_id: int
    channel_id: int
    channel_link: str



def load_config() -> Config:
    return Config(
        bot_token=os.getenv("BOT_TOKEN", ""),
        admin_id=int(os.getenv("ADMIN_ID", "0")),
        channel_id=int(os.getenv("CHANNEL_ID", "0")),
        channel_link=os.getenv("CHANNEL_LINK", "https://t.me/"),
    )
