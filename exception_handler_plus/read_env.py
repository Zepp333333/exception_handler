import os
from typing import Optional


def read_env_as_int(env_var_name: str) -> Optional[int]:
    if env_var := os.getenv(env_var_name):
        try:
            return int(env_var)
        except ValueError:
            pass
    return None
