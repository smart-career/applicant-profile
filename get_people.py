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

# REPLACE With your LinkedIn Credentia
USERNAME = ""
PASSWORD = ""

def mongodb_init():
    client=MongoClient('mongodb://34.73.180.107:27017')
    db=client.smartcareer
    return db

def mongodb_get_collection(db,item):
    col=db[item]
    return col

def mongodb_read_docs(col):
    db = mongodb_init()
    col = mongodb_get_collection(db, col)

    try:

        ret = col.find().limit(5000)

    except Exception as e:
        print(e)

    return ret


def mongodb_put_doc(doc):
    db=mongodb_init()
    col=mongodb_get_collection(db,'Applicantprofile')

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
    count = 0

    USERNAME = config['User Name']
    PASSWORD = config['Password']
    col=config['Collection']
    people_search_url = generate_scrape_url(base_url, config)

    print('\nSTATUS: Opening website')
    browser = webdriver.Firefox(executable_path=driver)
    browser.get(sign_in_url)
    time.sleep(2)

    print('STATUS: Signing in')
    browser.find_element_by_id('username').send_keys(USERNAME)
    time.sleep(2)

    browser.find_element_by_id('password').send_keys(PASSWORD)
    time.sleep(2)

    browser.find_element_by_class_name('login__form_action_container ').click()
    time.sleep(2)

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
    while True and count < 80:
        print('STATUS: Scraping Page ' + str(page))
        links = []
        for link in people:
            try:
                link = link.find_element_by_class_name("search-result__result-link").get_attribute("href")
                links.append(link)
            except:
                ()

        for link in links:
            obj = {'ProfileID': link.split('/')[len(link.split('/')) - 2]}
            if obj['ProfileID'] != "people" and obj['ProfileID'] not in CHECKLIST:
                browser.get(link)
                time.sleep(1)
                scroll_down_page(browser, 20)
                print("STATUS: Scraping Profile_ID: {}".format(obj['ProfileID']))

                try:
                    browser.find_element_by_xpath("//a[@class='lt-line-clamp__more']").click()
                except:
                    ()
                try:
                    browser.find_element_by_xpath(
                        "//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']").click()
                except:
                    ()

                time.sleep(1)

                try:
                    browser.find_element_by_xpath(
                        "//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']").click()
                except:
                    ()

                try:
                    companies = browser.find_element_by_id("experience-section").find_elements_by_class_name("pv-entity__position-group-pager")
                except:
                    companies = []

                experience = []
                experience_obj = {}

                for company in companies:
                    r = clean_item(company.find_element_by_tag_name('h3').text)
                    if "Company Name" in r:
                        try:
                            roles = company.find_elements_by_class_name(
                                "pv-entity__role-details-container")
                        except:
                            roles = []
                        for role in roles:
                            try:
                                experience_obj['Job Title'] = clean_item(role.find_element_by_tag_name('h3').text).replace('Title ', '')
                            except:
                                experience_obj['Job Title'] = ''

                            try:
                                experience_obj['Company'] = clean_item(company.find_element_by_tag_name('h3').text).replace('Company Name ', '')
                            except:
                                experience_obj['Company'] = ''

                            try:
                                experience_obj['Location'] = clean_item(role.find_element_by_class_name('pv-entity__location').text).replace('Location ', '')
                            except:
                                experience_obj['Location'] = ''

                            try:
                                experience_obj['Period'] = clean_item(
                                    role.find_element_by_class_name('pv-entity__date-range').text).replace('Dates Employed ', '')
                            except:
                                experience_obj['Period'] = ''

                            try:
                                experience_obj['Years'] = clean_item(role.find_element_by_class_name("pv-entity__bullet-item-v2").text)
                            except:
                                experience_obj['Years'] = ''

                            try:
                                experience_obj['Description'] = clean_item(role.find_element_by_class_name('pv-entity__description').text)
                            except:
                                experience_obj['Description'] = ''

                            experience.append(experience_obj)
                            experience_obj = {}

                    else:
                        try:
                            experience_obj['Job Title'] = clean_item(company.find_element_by_tag_name('h3').text)
                        except:
                            experience_obj['Job Title'] = ''

                        try:
                            experience_obj['Company'] = clean_item(company.find_element_by_class_name('pv-entity__secondary-title').text)
                        except:
                            experience_obj['Company'] = ''

                        try:
                            experience_obj['Location'] = clean_item(company.find_element_by_class_name('pv-entity__location').text).replace('Location ', '')
                        except:
                            experience_obj['Location'] = ''

                        try:
                            experience_obj['Period'] = clean_item(
                                company.find_element_by_class_name('pv-entity__date-range').text).replace('Dates Employed ', '')
                        except:
                            experience_obj['Period'] = ''

                        try:
                            experience_obj['Years'] = clean_item(company.find_element_by_class_name("pv-entity__bullet-item-v2").text)
                        except:
                            experience_obj['Years'] = ''

                        try:
                            experience_obj['Description'] = clean_item(company.find_element_by_class_name('pv-entity__description').text)
                        except:
                            experience_obj['Description'] = ''

                        experience.append(experience_obj)
                        experience_obj = {}

                obj = experience[0]
                try:
                    obj['Profile Summary'] = clean_item(
                        browser.find_element_by_class_name("pv-about__summary-text").text)
                except:
                    obj['Profile Summary'] = ''
                obj['ProfileID'] = link.split('/')[len(link.split('/')) - 2]
                del experience[0]
                obj['Experience'] = experience
                try:
                    browser.find_element_by_xpath(
                        "//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']").click()
                except:
                    ()
                time.sleep(1)
                try:
                    browser.find_element_by_xpath(
                        "//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']").click()
                except:
                    ()

                try:
                    institutes = browser.find_element_by_id("education-section").find_elements_by_class_name("pv-entity__summary-info")
                except:
                    institutes = []

                education = []
                education_obj = {}

                for institute in institutes:
                    education_obj['School'] = clean_item(institute.find_element_by_tag_name('h3').text)
                    if "High School" not in education_obj['School']:
                        try:
                            education_obj['School'] = clean_item(institute.find_element_by_tag_name('h3').text)
                        except:
                            education_obj['School'] = ''

                        try:
                            education_obj['Degree'] = clean_item(institute.find_element_by_class_name('pv-entity__degree-name').text).replace('Degree Name ', '')
                        except:
                            try:
                                degree = clean_item(institute.find_element_by_class_name('pv-entity__fos').text).replace('Field Of Study ', '')
                                if ' in ' in degree:
                                    e = degree.split(' in ')
                                    education_obj['Degree'] = e[0]
                            except:
                                education_obj['Degree'] = ''

                            education_obj['Degree'] = ''

                        try:
                            education_obj['Major'] = clean_item(institute.find_element_by_class_name('pv-entity__fos').text).replace('Field Of Study ', '')
                        except:
                            try:
                                major = education_obj['Degree'].split(' in ')
                                education_obj['Major'] = major[1]
                            except:
                                education_obj['Major'] = ''

                            education_obj['Major'] = ''

                        try:
                            education_obj['Date Attended'] = clean_item(institute.find_element_by_class_name('pv-entity__dates').text).replace('Dates attended or expected graduation ', '')
                        except:
                            education_obj['Date Attended'] = ''

                        if ' in ' in education_obj['Degree']:
                            g = education_obj['Degree'].split(' in ')
                            education_obj['Degree'] = g[0]

                        elif ' in ' in education_obj['Major']:
                            m = education_obj['Major'].split(' in ')
                            education_obj['Major'] = m[1]

                        education.append(education_obj)
                        education_obj = {}

                obj['Education'] = education

                try:
                    browser.find_element_by_xpath(
                        "//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']").click()
                except:
                    ()
                time.sleep(1)
                try:
                    browser.find_element_by_xpath(
                        "//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']").click()
                except:
                    ()

                time.sleep(1)
                try:
                    browser.find_element_by_xpath(
                        "//button[@class='pv-profile-section__see-more-inline pv-profile-section__text-truncate-toggle link link-without-hover-state']").click()
                except:
                    ()

                try:
                    certifications = browser.find_element_by_id("certifications-section").find_elements_by_class_name("pv-profile-section__sortable-item")
                except:
                    certifications = []

                license = []
                license_obj = {}

                for certification in certifications:
                    try:
                        license_obj['Name'] = clean_item(certification.find_element_by_tag_name('h3').text)
                    except:
                        license_obj['Name'] = ''
                    try:
                        license_obj['Issuing Authority'] = clean_item(certification.find_element_by_tag_name('p').text).replace('Issuing authority ', '')
                    except:
                        license_obj['Issuing Authority'] = ''

                    license.append(license_obj)
                    license_obj = {}

                obj['Licenses & Certifications'] = license

                try:
                    organizations = browser.find_element_by_class_name("volunteering-section").find_elements_by_class_name("pv-entity__summary-info")
                except:
                    organizations = []

                volunteer = []
                volunteer_obj = {}

                for organization in organizations:
                    try:
                        volunteer_obj['Job Title'] = clean_item(organization.find_element_by_tag_name('h3').text)
                    except:
                        volunteer_obj['Job Title'] = ''

                    try:
                        volunteer_obj['Organization'] = clean_item(organization.find_element_by_class_name('pv-entity__secondary-title').text)
                    except:
                        volunteer_obj['Organization'] = ''

                    try:
                        volunteer_obj['Period'] = clean_item(
                            organization.find_element_by_class_name('pv-entity__date-range').text).replace('Dates volunteered ', '')
                    except:
                        volunteer_obj['Period'] = ''

                    try:
                        volunteer_obj['Years'] = clean_item(organization.find_element_by_class_name("pv-entity__bullet-item").text)
                    except:
                        volunteer_obj['Years'] = ''

                    try:
                        volunteer_obj['Field'] = clean_item(organization.find_element_by_class_name('pv-volunteer-causes').text)
                    except:
                        volunteer_obj['Field'] = ''

                    try:
                        volunteer_obj['Description'] = clean_item(
                            organization.find_element_by_class_name('pv-entity__description').text)
                    except:
                        volunteer_obj['Description'] = ''

                    volunteer.append(volunteer_obj)
                    volunteer_obj = {}
                obj['Volunteer Experience'] = volunteer

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
        count += 1
        next_page = people_search_url + '&page=' + str(page)
        browser.get(next_page)
        time.sleep(2)
        scroll_down_page(browser, 4)

        people = browser.find_elements_by_xpath('//div[@class="search-result__info pt3 pb4 ph0"]')
        if len(people) == 0:
            break

    browser.quit()

if __name__ == '__main__':
    docs = mongodb_read_docs('Applicantprofile')
    CHECKLIST = []
    for d in docs:
        try:
            CHECK = d['ProfileID']
            CHECKLIST.append(CHECK)
        except:
            CHECK = None
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
