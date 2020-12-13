import models
 
def create_tables(database):
    TABLES = [
        models.Users, models.Achievements, models.EasterEggs, models.Leaderboard, models.UserAchievements,
        models.UserEasterEggs,
    ]

    with models.database.connection_context():
        models.database.create_tables(TABLES, safe=True)
        models.database.commit()


def fill_easter_eggs(db):
    names = ['didyouknowgaming?', 'reggie', 'pacman', 'nintendo power', 'portal', 'zelda 2', 'star fox']
    for name in names:
        easter_egg = models.EasterEggs(name=name)
        easter_egg.save()


def fill_achievements(db):
    names = (
        ("That's what you get for guessing...", '../static/guess.jpg'),
        ("That's just ok..", "../static/pass.jpg"),
        ('Excellent! you must be cheating...', "../static/crash.jpg"),
        ("Top of the game!", "../static/top_ten.jpg"),
        ("First easter egg! gotta catch 'em all!", "../static/addict.jpg"),
        ('Easter egg hunter!', "../static/hunter.jpg"),
        ("Completionist!", "../static/Completionist.jpg")
    )
    for name in names:
        achievement_name = name[0]
        uri = name[1]
        achievement = models.Achievements(achievement_name=achievement_name, uri=uri)
        achievement.save()


db = models.database
create_tables(db)
fill_easter_eggs(db)
fill_achievements(db)