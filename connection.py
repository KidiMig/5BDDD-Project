import oracledb, os
from dotenv import load_dotenv

load_dotenv()

print('DATABASE_USER', os.getenv('DATABASE_USER'))
print('DATABASE_PASSWORD', os.getenv('DATABASE_PASSWORD'))
print('DATABASE_DSN', os.getenv('DATABASE_DSN'))

# Connexion à la base de données Oracle
conn = oracledb.connect(user=os.getenv('DATABASE_USER'),
                        password=os.getenv('DATABASE_PASSWORD'),
                        dsn=os.getenv('DATABASE_DSN'))
