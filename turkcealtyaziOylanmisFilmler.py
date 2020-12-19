#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import json
from time import sleep

options = Options()
options.headless = True

myname = "*"
mypass = "*"

driver_path = "~/Downloads/geckodriver"
login_page = "https://turkcealtyazi.org/login.php"
home_page = "https://turkcealtyazi.org/index.php"
voted_page = "https://turkcealtyazi.org/myvotes.php?p=1"


def login(driver):
    username = myname
    password = mypass
    driver = driver

    driver.get(login_page)

    username_textbox = driver.find_element_by_css_selector(
        "input.regclass:nth-child(3)"
    )
    username_textbox.send_keys(username)

    password_textbox = driver.find_element_by_css_selector(
        "input.regclass:nth-child(7)"
    )
    password_textbox.send_keys(password)

    login_button = driver.find_element_by_css_selector(
        ".nblock > div:nth-child(2) > div:nth-child(8) > div:nth-child(2) > input:nth-child(2)"
    )
    login_button.click()

    if driver.current_url == home_page:
        print("Login Successful!")


def getContent(link, driver):
    driver = driver
    driver.get(link)
    content = driver.page_source
    return content


def getPoint(link, driver):
    driver_point = driver
    driver_point.get(link)
    cnt = driver_point.page_source
    point_sp = bs(cnt, "lxml")
    point = point_sp.find("span", attrs={"class": "nPuanDel"}).find_next("span")
    if point:
        puan = float(point.text)
    else:
        puan = 0
    return puan


def saveToJson(movieDict, name):
    json_format = json.dumps(movieDict, indent=4)
    # if we want to add an existing file we must write 'a' otherwise 'w'
    with open(f"votedjsons/{name}.json", "w") as outfile:
        json.dump(movieDict, outfile)


def extract_films(content, movieList, driver):
    soup = bs(content, "lxml")
    films = soup.find_all("td", attrs={"width": "25%"})
    for film in films:
        title = film.find_all("a")[-1].get("title")
        link = film.find_all("a")[-1].get("href")
        film_id = link.split("/")[-2]
        print(title)
        exact_link = f"https://turkcealtyazi.org{link}"
        my_puan = getPoint(exact_link, driver)
        sleep(5)
        movieList.append(
            {"Title": title, "Link": exact_link, "Id": film_id, "Puanım": my_puan}
        )


def main():
    driver = webdriver.Firefox(options=options, executable_path=driver_path)
    login(driver)
    total_pages = 16
    movieDict = dict()
    movieDict["Movies"] = list()

    for page in range(1, total_pages + 1):
        print(f"Now page: {page}")
        link = f"https://turkcealtyazi.org/myvotes.php?p={page}"
        content = getContent(link, driver)
        extract_films(content, movieDict["Movies"], driver)
        saveToJson(movieDict, f'Page{page}')
        sleep(10)
    saveToJson(movieDict, "MyVotesFinal")
    s = bs(content, "lxml")
    film_adet = s.find("td", attrs={"height": "30"}).text
    print(film_adet)
    driver.quit()


if __name__ == "__main__":
    main()
