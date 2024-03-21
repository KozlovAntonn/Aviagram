from database.db_config import USER, PASSWORD, DBNAME, HOST
# from db_config import USER, PASSWORD, DBNAME, HOST
from datetime import datetime
import asyncpg

async def check_if_user_exist(user_id):
    conn = await asyncpg.connect(user=USER, password=PASSWORD, database=DBNAME, host=HOST)

    # try:
    query = 'SELECT COUNT(*) FROM "Users" WHERE user_id = $1'
    result = await conn.fetchval(query, user_id)

    return result > 0

    # finally:
    await conn.close()


async def push_user_info(user_id, username, user_firstname, user_lastname, language, currency):
    conn = await asyncpg.connect(user=USER, password=PASSWORD, database=DBNAME, host=HOST)

    try:
        registered_at = datetime.utcnow()
        query = '''
            INSERT INTO "Users" (user_id, username, first_name, second_name, language_code, currency_code, registered_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
        '''
        await conn.execute(query, user_id, username, user_firstname, user_lastname, language, currency, registered_at)

    finally:
        await conn.close()

async def get_user_info(user_id):
    conn = await asyncpg.connect(user=USER, password=PASSWORD, database=DBNAME, host=HOST)

    try:
        query = '''
            SELECT user_id, username, first_name, second_name, language_code, currency_code, registered_at
            FROM "Users"
            WHERE user_id = $1
        '''
        user_info = await conn.fetchrow(query, user_id)
        return user_info

    finally:
        await conn.close()

async def get_user_language(user_id):
    conn = await asyncpg.connect(user=USER, password=PASSWORD, database=DBNAME, host=HOST)

    try:
        query = '''
            SELECT language_code FROM "Users" WHERE user_id = $1
        '''
        user_info = await conn.fetchrow(query, user_id)
        return user_info['language_code']  # Extracting the value directly

    finally:
        await conn.close()




async def update_user_info(user_id, username, user_firstname, user_lastname, language, currency, interaction_time=None):
    conn = await asyncpg.connect(user=USER, password=PASSWORD, database=DBNAME, host=HOST)

    try:
        query = '''
            UPDATE "Users"
            SET
                username = $2,
                first_name = $3,
                second_name = $4,
                language_code = $5,
                currency_code = $6
            WHERE user_id = $1
        '''
        await conn.execute(query, user_id, username, user_firstname, user_lastname, language, currency)
        
    finally:
        await conn.close()


async def list_tables():
    conn = await asyncpg.connect(user=USER, password=PASSWORD, database=DBNAME, host=HOST)

    try:
        query = '''
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public';
        '''
        tables = await conn.fetch(query)

        # Print or return the list of table names
        for table in tables:
            print(table['table_name'])

    finally:
        await conn.close()






async def push_quick_search_parameters(user_id, departure_code, arrive_code, departure_dates, return_dates=None, people_amount=[1,0,0], flight_class="econom"):
    conn = await asyncpg.connect(user=USER, password=PASSWORD, database=DBNAME, host=HOST)

    try:
        created_at = datetime.utcnow()
        query = '''
            INSERT INTO "Quick_search_parameters" (user_id, departure_code, arrive_code, departure_dates, return_dates, people_amount, flight_class, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        '''
        await conn.execute(query, user_id, departure_code, arrive_code, departure_dates, return_dates, people_amount, flight_class, created_at)

    finally:
        await conn.close()


# 1) проверить есть ли этот пользователь уже в бд 

# 2) сохранить отправленный запрос в бд 
    
# 3) 
