import asyncio
from logic.database.config import database
from logic.database.data_migrations import main as migration
from sites.sites_get_update import get_parse_brands_models as parsing

if __name__ == "__main__":
    asyncio.run(parsing())
    asyncio.run(migration(database()))
