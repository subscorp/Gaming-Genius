import database
import models

db = models.database
# db = connect(os.environ.get('DATABASE_URL')) # for heroku 
database.create_tables(db)
database.fill_easter_eggs(db)
database.fill_achievements(db)