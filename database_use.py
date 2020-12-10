import database, models
from playhouse.db_url import connect
import os

# db = models.database
db = connect(os.environ.get('DATABASE_URL')) 
database.create_tables(db)
database.fill_easter_eggs(db)
database.fill_achievements(db)