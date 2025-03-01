import asyncpg
import discord
from discord.ext import commands
import config
import database
import models
import commands_list
from database import engine, SessionLocal, Base, DATABASE_URL


# Создание таблиц в базе данных
#Base.metadata.create_all(bind=engine)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
#чекнуть intents all

bot = commands.Bot(command_prefix='!', intents=intents)

#Подключение к базе данных
async def create_db_pool():
    bot.pg_pool = await asyncpg.create_pool(DATABASE_URL)
    print("Пул подключений к базе данных создан.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Создание таблицы, если она не существует
    try:
        async with bot.pg_pool.acquire() as connection:
            print("Подключение к базе данных установлено.")
            await connection.execute('''
                    CREATE TABLE IF NOT EXISTS tickets (
                        ticket_id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        username TEXT NOT NULL,
                        message TEXT NOT NULL
                    )
                ''')
            print("Таблица tickets создана или уже существует.")
    except Exception as e:
        print(f"Ошибка при создании таблицы: {e}")
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def hello(ctx):
    await ctx.send("Я бот для тех поддержки =) ")

@bot.command()
async def commands(ctx):
    embed = discord.Embed(title="Список команд", color=0x00ff00)
    for command, description in commands_list.commands.items():
        embed.add_field(name=f'!{command}', value=description, inline=False)
    await ctx.send(embed=embed)

# Команда для создания тикета
#@bot.command(name="createticket")
@bot.command(name="createticket")
async def create_ticket(ctx, *, message: str):
    user = ctx.author
    try:
        async with bot.pg_pool.acquire() as connection:
            # Вставляем данные в таблицу tickets
            await connection.execute('''
                    INSERT INTO tickets (user_id, username, message)
                    VALUES ($1, $2, $3)
                ''', user.id, user.name, message)
            await ctx.send(f"Тикет создан и сохранен в базе данных.")
    except Exception as e:
        await ctx.send(f"Ошибка при создании тикета: {e}")

# Команда для просмотра всех тикетов
@bot.command(name="viewtickets")
async def view_tickets(ctx):
    try:
        async with bot.pg_pool.acquire() as connection:
            # Получаем все тикеты из таблицы
            records = await connection.fetch('SELECT ticket_id, user_id, username, message FROM tickets')
            if records:
                embed = discord.Embed(title="Список тикетов:\n", color=0x00ff00)
                for record in records:
                    embed.add_field(name=f"ID: {record['ticket_id']}", value=f"User ID: {record['user_id']}\nПользователь: {record['username']}\nСообщение: {record['message']}", inline=False)
                await ctx.send(embed=embed)
            else:
                await ctx.send("Тикетов нет в базе данных.")
    except Exception as e:
        await ctx.send(f"Произошла ошибка при просмотре тикетов: {e}")
        print(f"Ошибка при просмотре тикетов: {e}")

@bot.command()
async def close(ctx, ticket_id: int):
    try:
        async with bot.pg_pool.acquire() as connection:
            # Проверяем, существует ли тикет
            ticket = await connection.fetchrow('SELECT ticket_id FROM tickets WHERE ticket_id = $1', ticket_id)
            if ticket:
                # Удаляем тикет
                await connection.execute('DELETE FROM tickets WHERE ticket_id = $1', ticket_id)
                await ctx.send(f"Тикет с ID {ticket_id} закрыт и удален.")
            else:
                await ctx.send(f"Тикет с ID {ticket_id} не найден.")
    except Exception as e:
        await ctx.send(f"Произошла ошибка при закрытии тикета: {e}")
        print(f"Ошибка при закрытии тикета: {e}")

# Запуск бота
async def start_bot():
    await create_db_pool()  # Создаём пул подключений
    await bot.start(config.DISCORD_TOKEN)  # Запускаем бота

# Запуск асинхронного цикла
import asyncio
asyncio.run(start_bot())

#bot.run(config.DISCORD_TOKEN)