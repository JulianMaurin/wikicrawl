from environs import Env

env = Env()

STUB_OUTPUT_DIRECTORY: str = env("STUB_OUTPUT_DIRECTORY", "./output")

STUB_REDIS_KEY_PAGES_SEPARATOR: str = env("STUB_REDIS_KEY_PAGES_SEPARATOR", "|")

REDIS_HOST: str = env("REDIS_HOST", "localhost")
REDIS_PORT: int = env.int("REDIS_PORT", 6379)
