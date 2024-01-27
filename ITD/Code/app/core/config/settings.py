from os import environ

from dotenv import load_dotenv

from app.utils.singleton import SingletonMeta

AUTH_STR: str = "/auth"
API_STR: str = "/api"
USERS_STR: str = "/users"
NOTIFICATIONS_STR: str = "/notifications"
TOKEN_URL: str = f"{API_STR}{AUTH_STR}/token"
EXPIRE_HOURS_USER_ACTIONS_TOKEN: int = 24 * 7  # 1 week
ENV_FILE_PATH: str = "APP_ENV"

if not load_dotenv(dotenv_path=environ[ENV_FILE_PATH]):
    raise FileNotFoundError(f"{environ[ENV_FILE_PATH]} file not found")
APP_DEBUG: bool = environ["APP_DEBUG"] == "1"


class SystemSettings(metaclass=SingletonMeta):
    ROOT_URL: str
    FRONTEND_URL: str

    def __init__(self):
        env_path = environ[ENV_FILE_PATH]
        if not load_dotenv(dotenv_path=env_path):
            raise FileNotFoundError(f"{env_path} file not found")
        try:
            self.ROOT_URL = environ["ROOT_URL"]
            self.FRONTEND_URL = environ["FRONTEND_URL"]
        except KeyError as e:
            raise KeyError(f"Missing environment variable: {e}")


class SecuritySettings(metaclass=SingletonMeta):
    SECRET_KEY: str

    def __init__(self):
        env_path = environ[ENV_FILE_PATH]
        if not load_dotenv(dotenv_path=env_path):
            raise FileNotFoundError(f"{env_path} file not found")
        try:
            self.SECRET_KEY = environ["SECRET_KEY"]
        except KeyError as e:
            raise KeyError(f"Missing environment variable: {e}")


class DatabaseSettings(metaclass=SingletonMeta):
    HOST: str
    PORT: int
    ROOT_USERNAME: str
    ROOT_PASSWORD: str
    USER_COLLECTION: str = "users"
    USER_ACTIONS_TOKEN_COLLECTION: str = "user_actions_tokens"
    AUTHENTICATION_TOKEN_COLLECTION: str = "authentication_tokens"
    NOTIFICATION_COLLECTION: str = "notifications"

    @property
    def connection_url(self) -> str:
        if APP_DEBUG:
            return f"mongodb://{self.ROOT_USERNAME}:{self.ROOT_PASSWORD}@{self.HOST}:{self.PORT}"
        return f"mongodb+srv://{self.ROOT_USERNAME}:{self.ROOT_PASSWORD}@{self.HOST}"

    def __init__(self):
        env_path = environ[ENV_FILE_PATH]
        if not load_dotenv(dotenv_path=env_path):
            raise FileNotFoundError(f"{env_path} file not found")
        try:
            if APP_DEBUG:
                self.HOST = environ["DB_HOST_DEV"]
                self.PORT = int(environ["DB_PORT_DEV"])
                self.ROOT_USERNAME = environ["DB_ROOT_USERNAME_DEV"]
                self.ROOT_PASSWORD = environ["DB_ROOT_PASSWORD_DEV"]
            else:
                self.HOST = environ["DB_HOST_PROD"]
                self.PORT = int(environ["DB_PORT_PROD"])
                self.ROOT_USERNAME = environ["DB_ROOT_USERNAME_PROD"]
                self.ROOT_PASSWORD = environ["DB_ROOT_PASSWORD_PROD"]
        except KeyError as e:
            raise KeyError(f"Missing environment variable: {e}")


class EmailSettings(metaclass=SingletonMeta):
    SMTP_SERVER: str
    SMTP_PORT: int
    EMAIL_ADDRESS: str
    EMAIL_PASSWORD: str
    SENDER_NAME: str

    def __init__(self):
        env_path = environ[ENV_FILE_PATH]
        if not load_dotenv(dotenv_path=env_path):
            raise FileNotFoundError(f"{env_path} file not found")
        try:
            self.SMTP_SERVER = environ["SMTP_SERVER"]
            self.SMTP_PORT = int(environ["SMTP_PORT"])
            self.EMAIL_ADDRESS = environ["EMAIL_ADDRESS"]
            self.EMAIL_PASSWORD = environ["EMAIL_PASSWORD"]
            self.SENDER_NAME = environ["SENDER_NAME"]
        except KeyError as e:
            raise KeyError(f"Missing environment variable: {e}")
