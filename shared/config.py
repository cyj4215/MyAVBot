from urllib.parse import quote_plus
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mysql_root_password: str = "change_me"
    mysql_user: str = "myavbot"
    mysql_password: str = "change_me"
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_database: str = "myavbot"

    redis_host: str = "localhost"
    redis_port: int = 6379

    telegram_bot_token: str = ""
    telegram_webhook_url: str = ""

    crawler_service_url: str = "http://localhost:8081"
    magnet_service_url: str = "http://localhost:8082"

    cloakbrowser_enabled: bool = True
    cloakbrowser_headless: bool = True

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{quote_plus(self.mysql_password)}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}"

    class Config:
        env_file = ".env"

settings = Settings()
