def assemble_dsn(host: str, port: int, user: str, password: str, database: str, is_async: bool) -> str:
    prefix = "postgresql+asyncpg" if is_async else "postgres"
    return f"{prefix}://{user}:{password}@{host}:{port}/{database}"
