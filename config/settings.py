from pydantic_settings import BaseSettings

from config.utils import assemble_dsn


class Settings(BaseSettings):
    db_host: str = "db_host"
    db_port: int = 5432
    db_name: str = "db_name"
    db_user: str = "db_user"
    db_password: str = "db_password"
    company_items_per_page: int = 10
    api_key: str = "api_key"

    @property
    def db_dsn(self) -> str:
        return assemble_dsn(
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_password,
            database=self.db_name,
            is_async=True,
        )
