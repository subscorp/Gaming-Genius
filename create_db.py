import models


def create_tables(db):
    TABLES = [
        models.Users, models.Achievements, models.EasterEggs, models.Leaderboard, models.UserAchievements,
        models.UserEasterEggs,
    ]

    with models.db.connection_context():
        models.db.create_tables(TABLES, safe=True)
        models.db.commit()
        
# db = models.database
# db = connect(os.environ.get('DATABASE_URL')) # for heroku 
# database.create_tables(db)
# database.fill_easter_eggs(db)
# database.fill_achievements(db)