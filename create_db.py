import models
import database
 
def create_tables(database):
    TABLES = [
        models.Users, models.Achievements, models.EasterEggs, models.Leaderboard, models.UserAchievements,
        models.UserEasterEggs,
    ]

    with models.database.connection_context():
        models.database.create_tables(TABLES, safe=True)
        models.database.commit()
        
db = models.database
create_tables(db)
# database.fill_easter_eggs(db)
database.fill_achievements(db)