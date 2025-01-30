import aiosqlite
from config import DB_NAME


async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
            user_id INTEGER PRIMARY KEY,
            question_index INTEGER,
            correct_answers INTEGER DEFAULT 0
        )''')
        await db.commit()


async def get_quiz_state(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT question_index, correct_answers FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0], results[1]
            else:
                return 0, 0


async def update_quiz_state(user_id, index, correct_answers):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, correct_answers) VALUES (?, ?, ?)', (user_id, index, correct_answers))
        await db.commit()

async def get_leaderboard(limit=10):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            'SELECT user_id, correct_answers FROM quiz_state ORDER BY correct_answers DESC LIMIT ?', (limit,)) as cursor:
           return await cursor.fetchall()