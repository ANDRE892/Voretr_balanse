import asyncpg


async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        user='postgres',
        password='admin',
        database='water_balance',
        port=5432,
        host='localhost'
    )


async def create_user():
    conn = await pool.acquire()
    try:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                water INTEGER,
                weight INTEGER,
                age INTEGER,
                physical_activity INTEGER,
                sex TEXT,
                climatic_conditions TEXT,
                status_start INT
            );
            """
        )
    finally:
        await pool.release(conn)


async def get_or_create_user(user_id, username):
    conn = await pool.acquire()
    try:
        user_exists = await conn.fetchval(
            "SELECT 1 FROM users WHERE user_id = $1", user_id
        )

        if not user_exists:
            await conn.execute(
                """
                INSERT INTO users (user_id, username, water, weight, age, physical_activity, sex, climatic_conditions, status_start)
                VALUES ($1, $2, 0, 0, 0, 0, '', '', 0)
                """,
                user_id, username
            )
            return True
        return False
    finally:
        await pool.release(conn)


async def update_user_water_data(user_id, weight, age, physical_activity, sex, climatic_conditions,water_drunk):
    conn = await pool.acquire()
    try:
        await conn.execute(
            """
            UPDATE users
            SET
                weight = $1,
                age = $2,
                physical_activity = $3,
                sex = $4,
                climatic_conditions = $5,
                water = $6
            WHERE user_id = $7
            """,
            weight, age, physical_activity, sex, climatic_conditions, water_drunk, user_id
        )
    finally:
        await pool.release(conn)

async def get_user_progress(user_id: int):
    conn = await pool.acquire()
    try:
        query = """
        SELECT water, weight, age, physical_activity, sex, climatic_conditions
        FROM users
        WHERE user_id = $1
        """
        user_data = await conn.fetchrow(query, user_id)

        if not user_data:
            return "Данных о вашем прогрессе не найдено. Пожалуйста, начните с ввода своих данных."

        weight = user_data['weight']
        age = user_data['age']
        physical_activity = user_data['physical_activity']
        sex = user_data['sex']
        climatic_conditions = user_data['climatic_conditions']
        water_drunk = user_data['water']

        daily_goal = weight * 30

        if age > 60:
            daily_goal *= 0.9

        if physical_activity > 30:
            daily_goal += (physical_activity // 30) * 300

        if climatic_conditions == "да":
            daily_goal *= 1.2

        if sex == "женский":
            daily_goal *= 0.9

        remaining_water = max(daily_goal - water_drunk, 0)

        progress = (
            f"Ваш прогресс:\n"
            f"- Норма воды в день: {daily_goal:.0f} мл\n"
            f"- Уже выпито: {water_drunk:.0f} мл\n"
            f"- Осталось выпить: {remaining_water:.0f} мл\n\n"
            "Продолжайте следить за водным балансом!"
        )
        return progress
    finally:
        await pool.release(conn)

async def get_user_data(user_id: int):
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            "SELECT weight, age, physical_activity, sex, climatic_conditions FROM users WHERE user_id = $1", user_id
        )
    return result
