# Import Splinter, BeautifulSoup and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

from webdriver_manager.firefox import GeckoDriverManager

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': GeckoDriverManager().install()}
    browser = Browser('firefox', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(), 
        "hemispheres" : hemisphere_data(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


#Scrape Mars News
def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)
    
    # Optional delay for loading the page
    ##browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)
    browser.is_element_present_by_css('div.list_text', wait_time=1)
    
    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    #Add try/except for error handling
    try:
        ##slide_elem = news_soup.select_one('ul.item_list li.slide')
        slide_elem = news_soup.select_one('div.list_text')
        #begin scraping
        slide_elem.find("div", class_='content_title')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()
    
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None
    
    return news_title, news_p

#Scrape Featured Image
def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    #Add try/except for error handling:
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
        
    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# Fact scraping
def mars_facts():

    #Add try/except for error handling:
    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)
    

    #Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped purple")
  

def hemisphere_data(browser):
    # Visit URL
    url = 'https://marshemispheres.com/'

    #Empty list
    hemisphere_image_urls = []

    #Cerberus
    for i in range(4):
    ## print (i)

        #Cerberus - find by tag
        browser.visit(url)
        #browser.links.find_by_partial_text('Cerberus').click()

        browser.find_by_tag('h3')[i].click()


        #parse the resulting html with soup
        html = browser.html
        hem_soup = soup(html, 'html.parser')


        # # Find the relative image url-something like this 
        hem_url = hem_soup.select_one('div.downloads a').get("href")
        hem_title = hem_soup.select_one('h2.title').text
        
        # #put in a dictionary the img and the title?:
        hem_dict = {
                "img_url": url+hem_url,
                "title": hem_title
            }

        hemisphere_image_urls.append(hem_dict)
        browser.back()
 
    return hemisphere_image_urls

######################################################################################## 
if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
