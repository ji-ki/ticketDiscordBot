import discord
from discord.ext import commands
import config
import models
from database import engine, SessionLocal, Base

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

#@bot.event
#async def on_ready():
#    print(f'Logged in as {bot.user.name}')


# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def hello(ctx):
    await ctx.send("Я бот для тех поддержки =) ")

@bot.command()
async def ticket(ctx, *, arg):
    # Логика создания тикета
    db = next(get_db())
    new_ticket = models.Ticket(title=arg, description="No description provided")
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    await ctx.send(f'Created ticket with ID {new_ticket.id}')

@bot.command()
async def close(ctx, ticket_id: int):
    # Логика закрытия тикета
    db = next(get_db())
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if ticket:
        ticket.status = 'closed'
        db.commit()
        await ctx.send(f'Ticket {ticket_id} has been closed.')
    else:
        await ctx.send(f'Ticket {ticket_id} not found.')


bot.run(config.DISCORD_TOKEN)