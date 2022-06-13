from environs import Env

env = Env()

DATABASE_USER: str = env("DATABASE_USER")
DATABASE_PASSWORD: str = env("DATABASE_PASSWORD")
DATABASE_URL: str = env("DATABASE_URL")
