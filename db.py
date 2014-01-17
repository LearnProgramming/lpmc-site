import psycopg2
import momoko

import config

db = momoko.Pool(dsn="dbname={} user={}".format(config.db.database, config.db.user), size=1)
