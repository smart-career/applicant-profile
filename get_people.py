import os
import re
import sys
import time
import json
from selenium import webdriver
from datetime import datetime
from datetime import date
from pymongo import MongoClient

# Global Variable
docNum = 0

# REPLACE With your LinkedIn Credentials
USERNAME = ""
PASSWORD = ""

def mongodb_init():
    client=MongoClient('mongodb://34.73.180.107:27017')
    db=client.smartcareer
    return db

def mongodb_get_collection(db,item):
    col=db[item]
    return col

def mongodb_put_doc(doc):
    db=mongodb_init()
    col=mongodb_get_collection(db,'applicantprofile')

    try:
        global docNum
        re=col.insert_one(doc)
        ret=re.inserted_id
        docNum += 1
    except:
        ret=doc['ProfileID']
          
    return ret

def clean_item(item):
    item = item.replace('\n', ' ')
    item = item.strip()
    return item

# https://www.linkedin.com/search/results/people/?facetGeoRegion=%5B%22us%3A0%22%5D&keywords=Data%20Engineer&origin=FACETED_SEARCH
def generate_scrape_url(scrape_url, config):

    title = config['Job Title']


# collecting people in US only
    scrape_url += "/search/results/people/?facetGeoRegion=%5B%22us%3A0%22%5D&keywords="
    scrape_url += title
    scrape_url += "&origin=SWITCH_SEARCH_VERTICAL"


    valid_title_name = title.strip().replace(' ', '_')
    valid_title_name = re.sub(r'(?u)[^-\w.]', '', valid_title_name)

    return scrape_url


def scroll_down_page(browser, speed=8):
    current_scroll_position, new_height = 0, 1
    while current_scroll_position <= new_height:
        current_scroll_position += speed
        browser.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
        new_height = browser.execute_script("return document.body.scrollHeight")

def pscrape(config):
    start_time = time.time()
    # driver download: https://github.com/mozilla/geckodriver/releases
    # windows \, Linux and Max /
    driver = os.getcwd() + "/geckodriver.exe"
    base_url = "https://www.linkedin.com"
    sign_in_url = "https://www.linkedin.com/uas/login?fromSignIn=true"
    people_data = []
    page = 1

    USERNAME = config['User Name']
    PASSWORD = config['Password']
    col=config['Collection']
    people_search_url = generate_scrape_url(base_url, config)

    print('\nSTATUS: Opening website')
    browser = webdriver.Firefox(executable_path=driver)
    browser.get(sign_in_url)
    time.sleep(1)

    print('STATUS: Signing in')
    browser.find_element_by_id('username').send_keys(USERNAME)
    time.sleep(1)

    browser.find_element_by_id('password').send_keys(PASSWORD)
    time.sleep(1)

    browser.find_element_by_class_name('login__form_action_container ').click()
    time.sleep(1)

    print('STATUS: Searching for people\n')
    browser.get(people_search_url)
    time.sleep(2)
    scroll_down_page(browser, 4)

    people = browser.find_elements_by_xpath('//div[@class="search-result__info pt3 pb4 ph0"]')

    if len(people) == 0:
        print('STATUS: No people found. Press any key to exit scraper')
        print("Check docnum.txt for # of documents submitted!")
        today = datetime.now()
        f = open("docnum.txt","w+")
        f.write("Ran:\n")
        f.write(str(today))
        f.write("\n")
        f.write("\nNumber of documents submitted:\n")
        f.write(str(docNum))
        f.close()
        browser.quit()
        exit = input('')
        sys.exit(0)

    #Scraping up to 6 pages per search.
    while True and page != 6:
        print('STATUS: Scraping Page ' + str(page))
        links = []
        for link in people:
            try:
                link = link.find_element_by_class_name("search-result__result-link").get_attribute("href")
                links.append(link)
            except:
                ()

        for link in links:
            obj = {}
            browser.get(link)
            time.sleep(2)

            scroll_down_page(browser, 20)
  
            obj['ProfileID'] = link.split('/')[len(link.split('/'))-2]
            if obj['ProfileID'] != "people":
                print("STATUS: Scraping Profile_ID: {}".format(obj['ProfileID']))

                try:
                    browser.find_element_by_xpath("//a[@class='lt-line-clamp__more']").click()
                except:
                    ()
                try:
                    browser.find_element_by_xpath("//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']").click()
                except:
                    ()

                try:
                    obj['Job Title'] = clean_item(browser.find_element_by_xpath("//h2[@class='mt1 t-18 t-black t-normal']").text)
                except:
                    obj['Job Title'] = ''

                try:
                    obj['Location'] = clean_item(browser.find_element_by_xpath("//li[@class='t-16 t-black t-normal inline-block']").text)
                except:
                    obj['Location'] = ''

                try:
                    obj['Profile Summary'] = clean_item(browser.find_element_by_class_name("pv-about__summary-text").text)
                except:
                    obj['Profile Summary'] = ''
                
                try:
                    companies = browser.find_element_by_id("experience-section").find_elements_by_class_name("pv-profile-section__card-item-v2")
                except:
                    companies = []

                experience = []
                experience_obj = {}

                for company in companies:
                    try:
                        experience_obj['Job Title'] = clean_item(company.find_element_by_tag_name('h3').text)
                    except:
                        experience_obj['Job Title'] = ''

                    try:
                        experience_obj['Company'] = clean_item(company.find_element_by_class_name('pv-entity__secondary-title').text)
                    except:
                        experience_obj['Company'] = ''

                    try:
                        experience_obj['Period'] = clean_item(company.find_element_by_class_name('pv-entity__date-range').text).replace('Dates Employed ', '')
                    except:
                        experience_obj['Period'] = ''

                    try:
                        experience_obj['Years'] = clean_item(company.find_element_by_class_name("pv-entity__bullet-item-v2").text)
                    except:
                        experience_obj['Years'] = ''

                    try:
                        experience_obj['Location'] = clean_item(company.find_element_by_class_name('pv-entity__location').text).replace('Location ', '')
                    except:
                        experience_obj['Location'] = ''

                    try:
                        experience_obj['Description'] = clean_item(company.find_element_by_class_name('pv-entity__description').text)
                    except:
                        experience_obj['Description'] = ''

                    experience.append(experience_obj)
                    experience_obj = {}

                obj['Experience'] = experience

                try:
                    institutes = browser.find_element_by_id("education-section").find_elements_by_class_name("pv-entity__summary-info")
                except:
                    institutes = []

                education = []
                education_obj = {}

                for institute in institutes:
                    try:
                        education_obj['School'] = clean_item(institute.find_element_by_xpath("//h3[@class='pv-entity__school-name t-16 t-black t-bold']").text)
                    except:
                        education_obj['School'] = ''

                    try:
                        degree_name = clean_item(institute.find_element_by_class_name('pv-entity__degree-name').text).replace('Degree Name ', '')
                    except:
                        degree_name = ''

                    try:
                        field_of_study = clean_item(institute.find_element_by_class_name('pv-entity__fos').text).replace('Field Of Study ', '')
                    except:
                        field_of_study = ''

                    try:
                        grade = clean_item(institute.find_element_by_class_name('pv-entity__grade').text).replace('Grade ', '')
                    except:
                        grade = ''

                    education_obj['Degree'] = degree_name+' '+field_of_study+' '+grade

                    try:
                        education_obj['Date Attended'] = clean_item(institute.find_element_by_class_name('pv-entity__dates').text).replace('Dates attended or expected graduation ', '')
                    except:
                        education_obj['Date Attended'] = ''

                    education.append(education_obj)
                    education_obj = {}

                obj['Education'] = education
            
                try:
                    browser.find_element_by_xpath("//button[@class='pv-profile-section__card-action-bar pv-skills-section__additional-skills artdeco-container-card-action-bar artdeco-button artdeco-button--tertiary artdeco-button--3 artdeco-button--fluid']").click()
                except:
                    print("No Skills")

                try:
                    skill_sets = browser.find_element_by_class_name("pv-skill-categories-section__top-skills").find_elements_by_class_name("pv-skill-category-entity__skill-wrapper")
                except:
                    skill_sets = []

                skills = []
                skills_obj = {}

                for skill_set in skill_sets:
                    try:
                        skills_obj['Skills'] = clean_item(skill_set.find_element_by_class_name('pv-skill-category-entity__name').text)
                    except:
                        skills_obj['Skills'] = ''

                    skills.append(skills_obj)
                    skills_obj = {}

                obj['Skills & Endorsements'] = skills

                try:
                    all_skillsets = browser.find_elements_by_xpath("//div[@class='pv-skill-category-list pv-profile-section__section-info mb6 ember-view']")
                except:
                    all_skillsets = []


                for one in all_skillsets:
                    general_skills = []
                    try:
                        g_skills = one.find_elements_by_class_name("pv-skill-category-entity")
                        for g_skill in g_skills:
                            try:
                                skills_obj['Skills'] = clean_item(
                                    g_skill.find_element_by_class_name('pv-skill-category-entity__name').text)
                            except:
                                skills_obj['Skills'] = ''

                            general_skills.append(skills_obj)
                            skills_obj = {}
                    except:
                        general_skills = []

                    try:
                        category_name = clean_item(one.find_element_by_tag_name('h3').text)
                    except:
                        category_name = "Skills"

                    obj[category_name] = general_skills

                try:
                    dateCaptured = date.today()
                    obj['Date Captured'] = str(dateCaptured)
                except:
                    obj['Date Captured'] = ''

                people_data.append(obj)
            
                doc_id=mongodb_put_doc(obj)
                print('post id: ', doc_id)
            else:
                print("STATUS: Skipping Profile_ID: {}".format(obj['ProfileID']))

        page += 1
        next_page = people_search_url + '&page=' + str(page)
        browser.get(next_page)
        time.sleep(2)
        scroll_down_page(browser, 4)

        people = browser.find_elements_by_xpath('//div[@class="search-result__info pt3 pb4 ph0"]')
        if len(people) == 0:
            break

    browser.quit()

if __name__ == '__main__':
    # Reads in the config file so input is automatic.
    with open("cfg.json") as json_cfg:
        d = json.load(json_cfg)
    
    jobTitle = d['Job Title']

    jobList = []
    tempStr = ""

    pscrape(d)
    # while len(configArray) > 0:
    #     try:
    #         int(configArray[0])
    #         break
    #     except:
    #         jobList.append(configArray[0])
    #         del configArray[0]

    # # Searches multiple jobs in a row.
    # for x in range(len(jobList)):
    #     print("Now scraping:", jobList[0])
    #     pscrape(jobList[0], configArray)
    #     time.sleep(5)
    #     del jobList[0]

    print("Daily automation has been completed for: get_people.py")
    print("Check docnum.txt for # of documents submitted!")
    today = datetime.now()
    f = open("docnum.txt","w+")
    f.write("Ran:\n")
    f.write(str(today))
    f.write("\n")
    f.write("\nNumber of documents submitted:\n")
    f.write(str(docNum))
    f.close()

    sys.exit(0)
