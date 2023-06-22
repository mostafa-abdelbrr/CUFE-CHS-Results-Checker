import requests
import discord
from discord.ext import tasks, commands
from bs4 import BeautifulSoup
from tabulate import tabulate
import asyncio
import os
SERVER_ID = 0
TOKEN = ''
username = ''
password = ''
async def checkResults():
    login_url = 'https://std.eng.cu.edu.eg/login.aspx'  # Replace with the actual login URL
    data = {
        '__EVENTTARGET': 'ctl03',
        '__EVENTARGUMENT': 'Button1|event|Click',
        'txtUsername': username,
        'txtPassword': password,
    }

    # Create a session to persist cookies
    session = requests.Session()

    # Perform the login request
    response = session.post(login_url, data=data)

    # Check if the login was successful
    if response.status_code == 200 and 'تم غلق الحساب بواسطة شئون الطلاب' not in response.text:
        print("Login successful")
        # print(response.text)  # Print the content of the protected page
        # Now you can use the session object to make subsequent requests
        # For example, let's make a GET request to a protected page
        protected_page_url = 'https://std.eng.cu.edu.eg/SIS/Modules/MetaLoader.aspx?path=~/SIS/Modules/Student/MyResult/Transcript/Transcript.ascx'  # Replace with the actual protected page URL
        response = session.get(protected_page_url)

        # Check the response
        if response.status_code == 200:
            print("Access to protected page successful")
            soup = BeautifulSoup(response.content, 'html.parser')
            tables = soup.find_all('table')  # Assuming there is a single table in the HTML content
            spring2023_flag = False
            table_data = []
            if len(tables) > 2:
                for table in tables[0:2]:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        row_data = []
                        for cell in cells:
                            # if cell.text == 'Spring-2023':
                            #     spring2023_flag = True
                            row_data.append(cell.text)
                        # if (table == tables[1] and spring2023_flag) or table != tables[1]:
                        table_data.append(row_data)
                # Pretty print the table data
                headers = table_data[0]
                data = table_data[1:]
                results = tabulate(data, headers=headers, tablefmt="grid")
                # if 'unknown' in response.text.lower():
                #     # filename = 'Spring_2023_Results.txt'
                #     # with open(filename, 'w') as resultsFile:
                #     #     resultsFile.write(results)
                #     # await bot.results_channel.send(file=discord.File(filename))
                #     # os.remove(filename)
                #     print('Site is up, no results yet.')
                #     return False
                # else:
                filename = 'Spring_2023_Results.txt'
                with open(filename, 'w') as resultsFile:
                    resultsFile.write(results)
                await bot.results_channel.send('Results are OUT!', file=discord.File(filename))
                os.remove(filename)
                table_data = []
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all('td')
                        row_data = []
                        for cell in cells:
                            row_data.append(cell.text)
                        table_data.append(row_data)
                    # Pretty print the table data
                    headers = table_data[0]
                    data = table_data[1:]
                    full_results = tabulate(data, headers=headers, tablefmt="grid")
                    filename = 'Spring_2023_Full_Results.txt'
                    with open(filename, 'w') as resultsFile:
                        resultsFile.write(results)
                    await bot.results_channel.send('Full transcript.', file=discord.File(filename))
                    os.remove(filename)
                    checker_task.stop()
                    return True

            # print(response.text)  # Print the content of the protected page
        else:
            return "Access to protected page failed"
            # print(response.text)  # Print the content of the protected page
    elif 'تم غلق الحساب بواسطة شئون الطلاب' in response.text:
        print('Account is locked.')
    else:
        print("Login failed")


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(seconds=1)
# @tasks.loop(minutes=1)
async def checker_task():
    await checkResults()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    bot.Emptiness = bot.get_guild(SERVER_ID)
    bot.results_channel = discord.utils.get(bot.Emptiness.text_channels, name='cufe-results')
    checker_task.start()

@bot.command('start')
async def start_task(ctx):
    checker_task.start()
    await ctx.send("Background task started.")

@bot.command('stop')
async def stop_task(ctx):
    checker_task.stop()
    await ctx.send("Background task stopped.")

bot.run(TOKEN)