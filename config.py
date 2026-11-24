<<<<<<< HEAD

=======
>>>>>>> 6c520a0 (Perbaikan PDF)
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "GreenRoots"
    APP_ENV: str = "development"

    SECRET_KEY: str
    DATABASE_URL: str

    SESSION_HTTPS_ONLY: bool | None = None

<<<<<<< HEAD
    # Allowed hosts untuk localhost dan deployment
    ALLOWED_HOSTS: str = "localhost,127.0.0.1"

=======
>>>>>>> 6c520a0 (Perbaikan PDF)
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    def model_post_init(self, __context):
        if self.SESSION_HTTPS_ONLY is None:
            self.SESSION_HTTPS_ONLY = (
                self.APP_ENV.lower() == "production"
            )

<<<<<<< HEAD
    @property
    def allowed_hosts_list(self) -> list[str]:
        return [
            host.strip()
            for host in self.ALLOWED_HOSTS.split(",")
            if host.strip()
        ]


settings = Settings()
=======

settings = Settings()
>>>>>>> 6c520a0 (Perbaikan PDF)
