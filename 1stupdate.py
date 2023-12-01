import logging

from logic.fix_num import fix_num

fix_num()

import asyncio
from logic.database.config import database
from logic.database.data_migrations import main as migration
from sites.sites_get_update import get_parse_brands_models as parsing

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(lineno)d] [%(name)s] [%(message)s]",
    filename='logs/1st_update.log',
    filemode='a'
)

if __name__ == "__main__":
    asyncio.run(parsing())
    asyncio.run(migration(database()))
