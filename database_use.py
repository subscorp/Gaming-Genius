import database, models

db = models.database
database.create_tables(db)
database.fill_easter_eggs(db)
database.fill_achievements(db)