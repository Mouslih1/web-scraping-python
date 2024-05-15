from bs4 import BeautifulSoup
import requests
import mysql.connector

# import chromedriver_autoinstaller
# from selenium import webdriver

# chromedriver_autoinstaller.install()

# options = webdriver.ChromeOptions()
# options.add_argument('--headless') 
# driver = webdriver.Chrome(options=options)


conn = mysql.connector.connect(
    host="localhost",
    user="maro",
    password="1111",
    database="cbs-sports"
)

base_url = "https://www.cbssports.com/nba/"
base_url_details = "https://www.cbssports.com/"
page_number = 1
cursor = conn.cursor()

while True:

    url = base_url + "/" + str(page_number) + "/"
    url_details = base_url_details
    page_source = requests.get(url)
    soup = BeautifulSoup(page_source.text, "html.parser")

    liens = soup.find_all("div", class_ = "article-list-pack-image")

    if not liens:
        break

    for lien in liens:

        a = lien.find("a", href=True)['href']
        page_source_details = requests.get(url_details + str(a))
        soup_for_details = BeautifulSoup(page_source_details.text, "html.parser")

        title = soup_for_details.find("h1", class_ = "Article-headline")

        if not title:
            break

        cursor.execute("SELECT title FROM news WHERE title LIKE %s", (title.text, ))
        existing_article = cursor.fetchone()

        # print(existing_article)
        
        if existing_article:

            print(f"Article with title '{title.text}' already exists in the database. Skipping...")
            continue 

        author = soup_for_details.find("span", class_ = "ArticleAuthor-nameText")

        if author:
            author_name = author.find("a")

            if author_name:
                author_name_text = author_name.text
            else: 
                author_name_text = "None"
        else:
            author_name_text = author.text
           

        figure_img = soup_for_details.find("img", class_= "Article-featuredImageImg")

        if figure_img:
            figure_img_src = figure_img['data-lazy']
        else:
            figure_img_src = "None"
    
        div_of_paragraphs = soup_for_details.find("div", class_ = "Article-bodyContent")

        if div_of_paragraphs:
            paragraphs = div_of_paragraphs.find_all("p")
        else:
            break

        description = ' '.join([p.get_text() for p in paragraphs])

        # print(title_text)
        # print(page_number)
        # print(f"author: {author_name_text}")
        # print(f"img: {figure_img_src}")
        # print(f"description: {description}") 
        
        sql = "INSERT INTO news (title, author, path, description) VALUES (%s,%s,%s,%s)"
        values = (title.text, author_name_text, figure_img_src, description)
        cursor.execute(sql, values)

    if page_number == 2:
        break

    page_number += 1

conn.commit()
print("data scraped and inserted in database successfully.")

cursor.close()
conn.close()
# print(liens)
    









