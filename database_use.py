import database, models
from playhouse.db_url import connect

db = connect(os.environ.get('postgres://lxjtrjtfimkbzj:cd691f8132b9ca1aaa722074876098a3668b8a36a75b8b52eac64cc8b12fed83@ec2-3-218-123-191.compute-1.amazonaws.com:5432/d3aesmaed08di8')) 
database.create_tables(db)
database.fill_easter_eggs(db)
database.fill_achievements(db)