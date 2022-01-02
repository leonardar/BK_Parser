import json
import random
import platform
import hashlib
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

# определяем ОС для дальнейшей настройки selenium Chrome
def get_system_prefix():
    if platform.system() == 'Linux':
        return 'linux'
    elif platform.system() == 'Darwin':
        return 'mac'
    return 'exe'

# Заполняем файлы sports, events, announcements для удобного чтения и изучения информации
def category_fill(category):
    category_dict = data[category]
    category_keys = set()

    for item in category_dict:
        for key in item.keys():
            category_keys.add(key)

    with open(f"{category}.csv", mode="w", encoding='utf-8') as w_file:
        header = ''
        for key in category_keys:
            header += f'{key} \t '
        header += '\n'
        w_file.write(header)

        for item in category_dict:
            header = ''
            for key in category_keys:
                if key in item.keys():
                    header += f'{item[key]} \t '
                else:
                    header += f'none \t '
            header += '\n'
            w_file.write(header)


# Получаем все футбольные live-матчи и записываем в словарь по названию игроков
def parse_games(sports, announcements, events):
    football_ids = []
    football_games = {}

    for game in sports:
        try:
            if game['parentId'] == 1:
                football_ids.append(game['id'])
        except KeyError:
            pass

    for game in announcements:
        for game_id in football_ids:
            if game['segmentId'] == game_id:
                team1 = game['team1']
                team2 = game['team2']
                gamer_name = f'{team1} - {team2}'
                gamer_id = hashlib.md5(gamer_name.encode("utf-8")).hexdigest()
                football_games.update({gamer_id: gamer_name})

    for game in events:
        for game_id in football_ids:
            try:
                if game['sportId'] == game_id and game['name'] == '':
                    team1 = game['team1']
                    team2 = game['team2']
                    gamer_name = f'{team1} - {team2}'
                    gamer_id = hashlib.md5(gamer_name.encode("utf-8")).hexdigest()
                    football_games.update({gamer_id: gamer_name})
            except KeyError:
                pass
    return football_games


# Проверяем наличие случайно выбранного футбольного live-матча
def check_random_match(random_match):
    driver.get('https://www.fonbet.ru/live')
    time.sleep(3)

    flag = 0
    while True:
        try:
            search_button = driver.find_element(By.XPATH, '/html/body/div[1]/div/header/div[2]/div/div[2]/a')
            driver.execute_script("arguments[0].click();", search_button)
            search_button_input = driver.find_element(By.XPATH, '/html/body/div[4]/div/div/input')
            search_button_input.send_keys(random_match)
            break
        except NoSuchElementException:
            flag += 1
            if flag == 5:
                print('Попытки исчерпаны, перезапустите программу')
                driver.close()
                return

    try:
        random_match_link = driver.find_element(By.XPATH,
                                                '/html/body/div[4]/div/div[2]/div/div/div[2]/a').get_attribute('href')
        driver.get(random_match_link)
        time.sleep(3)
        print(f'Матч {random_match} ещё не окончен')
        driver.close()
    except NoSuchElementException:
        print('Матч завершён')
        driver.close()


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.headless = False
    options.add_argument('window-size=1920,1080')
    prefix = get_system_prefix()
    service = Service(f'./chromedriver.{prefix}')
    driver = webdriver.Chrome(
        service=service,
        options=options
    )
    driver.maximize_window()

    driver.get(f'https://line14.bkfon-resources.com/live/currentLine/ru')
    driver.implicitly_wait(5)
    response = driver.find_element(By.TAG_NAME, "pre").text
    data = json.loads(response)

    category_fill('sports')
    category_fill('events')
    category_fill('announcements')

    sports = data['sports']
    announcements = data['announcements']
    events = data['events']

    result = parse_games(sports, announcements, events)
    print(json.dumps(result, indent=4, ensure_ascii=False, sort_keys=True))

    # Выбираем случайный матч из списка live-матчей
    random_match = result[random.choice(list(result.keys()))]
    # Проверяем состояние матча на текущий момент
    check_random_match(random_match)
