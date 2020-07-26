from selenium import webdriver
import time
import random
import os
from bs4 import BeautifulSoup
import csv
import re

base_dir = os.path.dirname(os.path.abspath(__file__))

class Crawlsystem(object):
  def __init__(self):
    global base_dir
    self.page_source = ''

  def set_driver(self):
 
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) ' \
        'Chrome/80.0.3987.132 Safari/537.36'
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument('--no-sandbox')
    chrome_option.add_argument('--disable-dev-shm-usage')
    chrome_option.add_argument('--ignore-certificate-errors')
    chrome_option.add_argument("--disable-blink-features=AutomationControlled")
    chrome_option.add_argument(f'user-agent={user_agent}')
    chrome_option.headless = True
    
    driver = webdriver.Chrome(options = chrome_option)
    return driver

  def get_data(self):
    temp_dict = {
        'job' : '',
        'location' : '',
        'salary' : '',
    }

    ########################## convert string to DOM ########################
    soup = BeautifulSoup(self.page_source, 'lxml')

    job_content = soup.find('div', id="detailOffreVolet")

    if job_content:
        try:
            job = job_content.find('h2', attrs={'itemprop': "title"})
            if job:
                print('job:', re.sub(r'\s+', ' ', job.text.strip()))
                temp_dict['job'] = re.sub(r'\s+', ' ', job.text.strip())

            location = job_content.find('p', attrs={'itemprop': "jobLocation"})
            if location:
                print('location:', re.sub(r'\s+', ' ', location.text.strip()))
                temp_dict['location'] = re.sub(r'\s+', ' ', location.text.strip())

            description_aside = job_content.find('div', class_="description-aside")
            if description_aside:
                dl = description_aside.find('dl')
                if dl:
                    salary = dl.select_one('dd:nth-of-type(3)')
                    if salary:
                        print('salary:', re.sub(r'\s+', ' ', salary.text.strip()))
                        temp_dict['salary'] = re.sub(r'\s+', ' ', salary.text.strip())

            print('----------')
        except:
            pass

    return temp_dict

  def main(self):
    self.driver = self.set_driver()
    print('----- Created Chrome Driver -----')
    self.driver.get("https://candidat.pole-emploi.fr/offres/recherche?lieux=11R&motsCles=Chauffeur%2FLivreur&offresPartenaires=false&rayon=10&tri=0")
    
    ########################## click more button ########################
    i=0
    while True:
        try:
            more_btn = self.driver.find_element_by_css_selector('#zoneAfficherPlus .results-more a')
            if more_btn:
                
                self.driver.execute_script("arguments[0].click();", more_btn)
                i+=1
                print( '**************', i, 'clicked more view button')
            else:
                break
            
            time.sleep(5)
        except:
            break

    card_contents = self.driver.find_elements_by_css_selector("#zoneAfficherListeOffres ul.result-list li.result a:first-child")
    print('Get', len(card_contents), 'Jobs.')

    for card_content in card_contents:
        try:
            self.driver.execute_script("arguments[0].click();", card_content)
            time.sleep(5)
    
            ########################## get current page source ########################
            self.page_source = self.driver.page_source
            return_data = self.get_data()
            
            if return_data['job']:
                file_exist = os.path.isfile(base_dir + '/output/result.csv')
                with open( base_dir + '/output/result.csv', 'a', newline="", encoding="latin1", errors="ignore") as result_csv:
                    fieldnames = ["job", "location", "salary"]
                    writer = csv.DictWriter(result_csv, fieldnames=fieldnames)
                    if not file_exist:
                        writer.writeheader()
                    writer.writerow(return_data)
        except:
            continue
    
    try:
        self.driver.quit()
    except:
        pass

if __name__ == '__main__':
  crawlsystem = Crawlsystem()
  crawlsystem.main()
