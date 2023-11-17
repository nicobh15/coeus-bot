# pylint: disable=all

import discord
from discord.ext import commands
import aiohttp
import os

from gb_request import get_book_info
from gr_request import get_book_reviews
from libgen_api import LibgenSearch

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

AVAILABLE_COMMANDS = {'!review': 'Get a review of a book given title', '!recommend': 'Get a recommendation for similar books given a title',
                      '!download': 'Download a book', '!info': 'Get detailed information about a book such as isbn, year of publication, etc'}

@bot.event 
async def on_ready():
    print(f"Logged in as {bot.user}.")
    
            
## TODO change the functions to be non blocking. 
# See https://stackoverflow.com/questions/65881761/discord-gateway-warning-shard-id-none-heartbeat-blocked-for-more-than-10-second
@bot.command(name='review', aliases=['rev'])
async def review(ctx, *, query: str):
    
    await ctx.send("Let me find that for you..")
    
    books = get_book_info(query)
    isbns = {}

    for book in books:
        for isbn in book['isbns']:
            if isbn:  # Ensure the isbn is not None
                isbns[isbn] = book

    highest_rating_count = -1
    best_book = None
    best_review = None
    
    ## Add sorting by levenshtein distance
    for isbn, book in isbns.items():
        review = get_book_reviews(isbn)
        
        if not review or len(review) == 0:
            continue

        rating_count = review[1]
        rating_count = (rating_count[0].replace(',', ''),rating_count[1])
        if int(rating_count[0]) > highest_rating_count:
            highest_rating_count = int(rating_count[0])
            best_book = book
            best_review = review

    if best_book and best_review:
        book_url = best_review[-1]
        
        embed = discord.Embed(
            title=best_book['title'],
            url=book_url, 
            description=f"**Author:** {best_book['authors'][0]}\n**Rating:** {best_review[0]}/5.0\n**Rating Count:** {best_review[1][0]} ratings",
            color=0x00ff00
        )
        
        embed.add_field(name="Summary", value=best_review[2][:1021]+'...', inline=False)

        await ctx.send("Here is what I found")
        await ctx.send(embed=embed)
    else:
        await ctx.send("No reviews found for the books queried.")

## TODO Implement recommendations
@bot.command(name='info', aliases=['i'])
async def info(ctx, *, query: str):
    pass

## TODO Implement recommendations
@bot.command(name='recommend', aliases=['rec'])
async def recommend(ctx, *, query: str):
    pass
    
    
## TODO Add filtering options by year, author, extension, etc
@bot.command(name='download', aliases=['d'])
async def download(ctx, *, query: str):
    await ctx.send("Let me find that for you... (This may take a bit)")
    tf = LibgenSearch()
    titles = tf.search_title(query)

    if not titles:
        await ctx.send("No books found")
        return

    item_to_download = titles[0]
    download_link = tf.resolve_download_links(item_to_download)["GET"]
    file_name = item_to_download['Title'] + '.' + item_to_download['Extension']

    ## Size Limits
    if ((item_to_download['Size'][-2:] == 'Mb' or item_to_download['Size'][-2:] == 'Mb') and float(item_to_download['Size'][:-3]) >= 25) or (item_to_download['Size'][-2:] == 'Gb' or item_to_download['Size'][-2:] == 'GB'):
        await ctx.send("File too large, sending link in dm")
        await ctx.author.send(download_link)
        return()
    
    async with aiohttp.ClientSession() as session:
        async with session.get(download_link) as resp:
            if resp.status == 200:
                with open(file_name, 'wb') as fd:
                    while True:
                        chunk = await resp.content.read(1024)
                        if not chunk:
                            break
                        fd.write(chunk)

    await ctx.send("Here you are", file=discord.File(file_name))
    os.remove(file_name)
    
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
bot.run(TOKEN)