import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self) -> None:
        self.soar_url = os.environ.get(
            "SOAR_URL", "https://awnsoar.soar.splunkcloud.com"
        ).rstrip("/")
        self.token = os.environ.get("SOAR_MCP_TOKEN") or os.environ.get("SOAR_TOKEN")
        self.verify_ssl = os.environ.get("SOAR_VERIFY_SSL", "true").lower() != "false"
        self.timeout = float(os.environ.get("SOAR_TIMEOUT", "30"))

    def require_token(self) -> str:
        if not self.token:
            raise RuntimeError(
                "No SOAR API token found. Set SOAR_MCP_TOKEN (or SOAR_TOKEN) in "
                "the environment or a .env file."
            )
        return self.token


config = Config()
