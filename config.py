from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "GreenRoots"
    APP_ENV: str = "development"

    SECRET_KEY: str
    DATABASE_URL: str
    ALLOWED_HOSTS: str = "localhost,127.0.0.1,.vercel.app"

    SESSION_HTTPS_ONLY: bool | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [
            host.strip()
            for host in self.ALLOWED_HOSTS.split(",")
            if host.strip()
        ]

    def model_post_init(self, __context):
        if self.SESSION_HTTPS_ONLY is None:
            self.SESSION_HTTPS_ONLY = (
                self.APP_ENV.lower() == "production"
            )


settings = Settings()