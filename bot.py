import asyncio
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
import telepot
import telepot.aio
from telepot.aio.loop import MessageLoop
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver

async def handle(msg):
    global chat_id
    # These are some useful variables
    content_type, chat_type, chat_id = telepot.glance(msg)
    # Log variables
    print(content_type, chat_type, chat_id)
    pprint(msg)
    #username = msg['chat']['first_name']
    # Check that the content type is text and not the starting
    if content_type == 'text':
        match msg['text']:
            case '/block_dylan':
                menu = await getMenuFBPhoto('https://www.facebook.com/blockhelsinki')
                await postMenuPhoto(menu)
            case '/fazer_postitalo':
                menu = await getMenuFazerJson()
                await postMenu(menu)
            case '/latorre_fratello':
                menu = await getMenuTorreScrape('fratello')
                await postMenu(menu)
            case '/latorre_lasipalatsi':
                menu = await getMenuTorreScrape('lasipalatsi')
                await postMenu(menu)
            case '/pompier_albertinkatu':
                menu = await getMenuPompierScrape('albertinkatu')
                await postMenu(menu)
            case '/pompier_espa':
                menu = await getMenuPompierScrape('espa')
                await postMenu(menu)
            case '/zucchini':
                menu = await getMenuFBPhoto('https://www.facebook.com/Kasvisravintola-Zucchini-2033302090217984/')
                await postMenuPhoto(menu)
            case _:
                return "Incorrect location."

        # if msg['text'] == '/loc1':
        #     #menu = await getMenuFazerJson()
        #     #menu = await getMenuPompierScrape('albertinkatu')
        #     #menu = await getMenuPompierScrape('espa')
        #     menu = await getMenuTorreScrape('lasipalatsi')
        #     await postMenu(menu)

async def createHeadlessFirefoxBrowser():
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    return webdriver.Firefox(options=options)

async def postMenu(menu):
    try:
        await bot.sendMessage(chat_id, menu)
    except:
        await bot.sendMessage(chat_id, 'Something went wrong...')

async def postMenuPhoto(menu):
    try:
        await bot.sendPhoto(chat_id, menu)
    except:
        await bot.sendMessage(chat_id, 'Something went wrong...')

async def getMenuFazerJson():
    baseUrl = 'https://www.foodandco.fi/modules/json/json/Index?costNumber=3134&language=en'
    jsonInfo = json.loads(requests.get(baseUrl).content)['MenusForDays'][0]
    date = datetime.strptime(jsonInfo['Date'], '%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%y')
    open = jsonInfo['LunchTime']
    jsonMenu = jsonInfo['SetMenus'][0]['Components']
    menu = 'Fazer Postitalo ' + date + '\n' + 'Open ' + open + '\n'
    for food in jsonMenu:
        menu += '\n' + food.replace('\n', '').replace('()', '').strip()
    return menu

async def getMenuPompierScrape(loc):
    url = 'https://pompier.fi/' + loc + '/'
    driver = await createHeadlessFirefoxBrowser()
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        location = soup.find('a', {'href': url}).text
        data = soup.find('div', {'class': 'lounaslista'})
        date = data.find('h2').text
        menu = data.find('p').text
        message = location + '\n' + date + '\n\n' + menu
        return message
    except:
        await bot.sendMessage(chat_id, 'Something went wrong...')

async def getMenuTorreScrape(loc):
    url = 'https://www.latorre.fi/en/location/' + loc
    driver = await createHeadlessFirefoxBrowser()
    try:
        message = date = menu = "x"
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        location = soup.find('h1', {'class': 'heading text-white margin-bottom--none'}).text
        data = soup.find('div', {'id': 'lunch'})
        date = data.find('div', {'class': 'lunch-block__description small-12 large-10 large-offset-1 columns margin--bottom--mini'}).text
        menu = data.find('div', {'class':'menu-item small-12 large-10 large-offset-1 columns end padding--top--mini'})

        foods = menu.find_all('h2', {'class': 'menu-item__title'})
        prices = menu.find_all('h6', {'class': 'menu-item__price'})
        food_list = list(filter(None, [food.get_text().strip() for food in foods])) 
        price_list = list(filter(lambda price: '€' in price, [price.get_text().strip() for price in prices]))
        menu = '\n'.join(' '.join(row) for row in zip(food_list, price_list))
        message = location + '\n' + date.strip() + '\n\n' + menu
        return message
    except:
        await bot.sendMessage(chat_id, 'Something went wrong...')

async def getMenuFBPhoto(baseUrl):
    driver = await createHeadlessFirefoxBrowser()
    try:
        driver.get(baseUrl)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        images = soup.find_all('img', alt=True)
        for image in images:
            if 'text' in image.get('alt'):
                return image.get('src')
    except:
        await bot.sendMessage(chat_id, 'Something went wrong...')

# Program startup
load_dotenv()
TOKEN = os.getenv('TOKEN')
bot = telepot.aio.Bot(TOKEN)
loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot, handle).run_forever())
print('Listening ...')

# Keep the program running
loop.run_forever()