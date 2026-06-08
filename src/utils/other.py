from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


def n_print(data):
    print("\n\n\n\n\n\n", data, "\n\n\n\n\n\n")
