import os

INSTANCES = ["https://openvk.su", "https://openvk.uk",  # OFFICIAL
             "https://social.fetbuk.ru", "https://vepurovk.xyz"]

DEFAULT_INSTANCE = os.environ.get("OPENVK_DEFAULT", INSTANCES[1])

SESSION_HEADERS = {"User-Agent": "python/openvk-api"}