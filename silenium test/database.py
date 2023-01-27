import aiosqlite

source = 'https://aiosqlite.omnilib.dev/en/stable/'
conn = await aiosqlite.connect('auto_db')
cur = conn.cursor()


cur.execute("""CREATE TABLE brands (
    id       INTEGER      PRIMARY KEY AUTOINCREMENT,
    [unique] TEXT (0, 32) UNIQUE
                          NOT NULL,
    av_by    TEXT (0, 32) UNIQUE,
    abw_by   TEXT (0, 32) UNIQUE
)""")

cur.execute("""CREATE TABLE models (
    id       INTEGER      PRIMARY KEY AUTOINCREMENT,
    brand_id INTEGER      REFERENCES brands (id) ON DELETE CASCADE,
    [unique] TEXT (0, 32) UNIQUE
                          NOT NULL,
    av_by    TEXT (0, 32) UNIQUE,
    abw_by   TEXT (0, 32) UNIQUE
);
)""")