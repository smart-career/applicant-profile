import os
import re
import sys
import time
import json
import pprint
from selenium import webdriver
from datetime import datetime
from datetime import date
from pymongo import MongoClient
from neo4j import GraphDatabase


# Mongo DB fuctions
def mongodb_init():
    client = MongoClient('mongodb://34.73.180.107:27017')
    db = client.smartcareer
    return db


def mongodb_get_collection(db, item):
    col = db[item]
    return col


def mongodb_put_doc(doc):
    db = mongodb_init()
    col = mongodb_get_collection(db, 'applicantprofile')

    try:
        global docNum
        re = col.insert_one(doc)
        ret = re.inserted_id
        docNum += 1
    except:
        ret = doc['ProfileID']

    return ret


def mongodb_read_docs(col):
    db = mongodb_init()
    col = mongodb_get_collection(db, col)

    try:

        ret = col.find().limit(300)

    except Exception as e:
        print(e)

    return ret


# Neo4j Functions
def neo4j_init():
    uri = "bolt://34.66.112.119"
    userName = "neo4j"
    passwd = "SmartCareer0!"
    ndb = GraphDatabase.driver(uri, auth=(userName, passwd))
    return ndb


def neo4j_read(neoObj, cqlNode):
    grapDB = neoObj

    try:
        with grapDB.session() as tx:
            ret = tx.run(cqlNode)


    except Exception as e:
        print(e)

    return ret


def neo4j_merge(neoObj, cqlNode):
    grapDB = neoObj

    try:
        with grapDB.session() as tx:
            ret = tx.run(cqlNode)


    except Exception as e:
        print(e)

    return ret


def clean_item(item):
    item = item.replace('\n', ' ')
    item = item.strip()
    return item


def write_log(msg):
    logf = open("smartcareer.log", "w")
    ret = logf.write(msg)
    return ret

def tokenize(temp):
    tokens = re.split(r'\W+', temp)
    return tokens

def merge(list1, list2, list3, list4): #job_time, edu_time, edu_list, job_list
    merged_list = []
    i = 0 #for job
    j = 0 #for edu
    # 정렬되어 있는 list1과 list2의 원소들을 차례로 비교하여, 더 작은 원소를 merged_list에 추가하기
    while i < len(list1) and j < len(list2):
        job_year = tokenize(list1[i])[1]
        edu_year = tokenize(list2[j])[0]

        if job_year < edu_year:
            merged_list.append(list3[j])
            j += 1
        else:
            merged_list.append(list4[i])
            i += 1
    # list1에 남은 원소가 있다면, merged_list에 추가하기
    if i < len(list4):
        for k in list4[i:]:
            merged_list.append(k)
    # list2에 남은 원소가 있다면, merged_list에 추가하기
    if j < len(list3):
        for l in list3[j:]:
            merged_list.append(l)
    return merged_list

if "__main__":

    print("Starting")
    docs = mongodb_read_docs('applicantprofile')
    graphDB = neo4j_init()
    count = 0
    for d in docs:
        count += 1
        jobTitle = d.get('Job Title')
        if jobTitle == "":
            continue
        jobTitle = d['Job Title']
        #company = d['Company']
        location = d['Location']
        experience = d.get('Experience')
        education = d.get('Education')
        skill = d.get('Skills \u0026 Endorsements')
        industryKnowledge = d.get('Industry Knowledge')
        tool_tech = d.get('Tools \u0026 Technologies')
        interpersonal = d.get('Interpersonal Skills')
        otherSkills = d.get('Other Skills')
        #
        # cqlNode = """Merge (c:`Job Title` {Name:'%s', Company:'%s'})
        #          Merge (l:`Location` {Name:'%s'})
        #          Merge (c)-[:LOCATEDAT]->(l)""" % (jobTitle, company, location)
        #
        # try:
        #     ret = neo4j_merge(graphDB, cqlNode)
        #
        # except Exception as e:
        #     write_log(str(e))
        #     continue
        # print("Neo4j inserted: %s" % ret)

        job_list = []
        job_time = []
        job_n_edu_list = []
        company_list = []
        location_list = []
        years_list = []
        period_list = []

        for item in experience:
            job_list.append(item['Job Title'].replace("'", ""))
            job_time.append(item['Period'])
            company_list.append(item['Company'].replace("'", ""))
            location_list.append(item['Location'])
            years_list.append(item['Years'])
            period_list.append(item['Period'])

        edu_list = []
        edu_time = []
        edu_degree = []
        for edu in education:
            edu_time.append(edu['Date Attended'])
            edu_list.append(edu['School'])
            edu_degree.append(edu['Degree'].replace("'", "").strip())

        if len(edu_time) != 0 and len(period_list) != 0:
            try:
                job_n_edu_list = merge(job_time, edu_time, edu_list, job_list)
            except Exception as e:
                #print(e)
                #write_log(str(e))
                continue

        index = 0
        next_index = 0
        edu_index = 0

        try:
            for i in job_n_edu_list:
                if len(job_n_edu_list) - 1 > index:
                    next_index = index + 1
                    if job_n_edu_list[index] in job_list and job_n_edu_list[next_index] in job_list:
                        jobs_to_jobs = """MERGE (c:`Job Title`{Name: '%s', Company:'%s', Location:'%s'})
                                       Merge (f:`Job Title`{Name:'%s', Company:'%s', Location:'%s', Years:'%s', Period:'%s'})
                                       Merge (f)-[:SWITHCEDTO]->(c)""" % (job_n_edu_list[index], company_list[index],
                                                                          location_list[index], job_n_edu_list[next_index],
                                                                          company_list[next_index], location_list[next_index],
                                                                          years_list[next_index], period_list[next_index])
                        ret = neo4j_merge(graphDB, jobs_to_jobs)
                    elif job_n_edu_list[index] == edu_list[edu_index] and len(edu_list) > 1:
                        if job_n_edu_list[next_index] == edu_list[edu_index]:
                            edu_to_edu = """MERGE (c:`Education`{Name: '%s', Degree: '%s'})
                                           Merge (f:`FormerEducation`{Name:'%s', Degree: '%s'})
                                           Merge (f)-[:Continued]->(c)""" % (job_n_edu_list[index], edu_degree[edu_index],
                                                                              job_n_edu_list[next_index], edu_degree[edu_index+1])
                            edu_index += 1
                            ret = neo4j_merge(graphDB, edu_to_edu)
                    elif job_n_edu_list[index] in job_list and job_n_edu_list[next_index] in edu_list:
                        #if edu_degree[edu_index + 1] is not None:
                        edu_to_jobs = """MERGE (c:`Job Title`{Name: '%s', Company:'%s', Location:'%s'})
                                       Merge (f:`Education`{Name:'%s'})
                                       Merge (f)-[:SWITHCEDTO]->(c)""" % (job_n_edu_list[index], company_list[index],
                                                                          location_list[index], job_n_edu_list[next_index])
                        edu_index += 1
                        ret = neo4j_merge(graphDB, edu_to_jobs)

                    elif job_n_edu_list[index] in edu_list and job_n_edu_list[next_index] in job_list:
                        jobs_to_edu = """MERGE (c:`Education`{Name: '%s'})
                                       Merge (f:`Job Title`{Name:'%s', Company:'%s', Location:'%s', Years:'%s', Period:'%s'})
                                       Merge (f)-[:SWITHCEDTO]->(c)""" % (job_n_edu_list[index],
                                                                          job_n_edu_list[next_index], company_list[next_index],
                                                                          location_list[next_index], years_list[next_index],
                                                                          period_list[next_index])
                        ret = neo4j_merge(graphDB, jobs_to_edu)

                    index = index + 1
                print("Neo4j inserted: %s" % ret)
        except Exception as e:
            # write_log(str(e))
            #print(e)
            continue

        try:
            for company in company_list:
                index = company_list.index(company)
                companies = """MATCH (j:`Job Title`{Name: '%s', Company:'%s'})
                               Merge (c:`Company` {Name:'%s'})
                               Merge (j)-[:WORK_AT]->(c)""" % (job_list[index], company, company)
                ret = neo4j_merge(graphDB, companies)
                print("Neo4j inserted: %s" % ret)
        except Exception as e:
            # write_log(str(e))
            #print(e)
            continue

        # try:
        #     for item in experience:
        #         title = item['Job Title']
        #         comp = item['Company'].replace("'","")
        #         loc = item['Location']
        #         years = item['Years']
        #         period = item['Period']
        #         formerJob = """MATCH (c:`Job Title`{Name: '%s'})
        #                        Merge (f:`Former Job` {Name:'%s', Company:'%s', Location:'%s', Years:'%s', Period:'%s'})
        #                        Merge (f)-[:SWITHCEDTO]->(c)""" % (jobTitle, title, comp, loc, years, period)
        #         ret = neo4j_merge(graphDB, formerJob)
        #         print("Neo4j inserted: %s" % ret)
        #
        # except Exception as e:
        #     # write_log(str(e))
        #     print(e)
        #     continue

        # try:
        #     for item in education:
        #         school = item['School']
        #         degree = item['Degree'].replace("'","")
        #         dateWent = item['Date Attended']
        #         eduExp = """MATCH (c:`Job Title`{Name: '%s'})
        #                     Merge (ed:`Education` {School:'%s', Degree:'%s', Attended:'%s'})
        #                     Merge (c)-[:KNOWLEDGEGAINEDFROM]->(ed)""" % (jobTitle, school, degree, dateWent)
        #         ret = neo4j_merge(graphDB, eduExp)
        #         print("Neo4j inserted: %s" % ret)
        #
        # except Exception as e:
        #     write_log(str(e))
        #     continue
        #
        try:
            bSkillList = []
            for item in skill:
                bSkillList.append(item['Skills'])

            for skill in bSkillList:
                bSkills = """
                            MATCH (c:`Company`{Name: '%s'})
                            Merge (b:`Business Skills` {Name: 'Business Skill', `Job Title`: '%s'})
                            Merge (c)-[:BUSINESS_SKILL]->(b)
                            Merge (t:`Skills` {Skill:'%s'})
                            Merge (b)-[:PARTOF]->(t)""" % (company_list[0], job_list[0], skill)
                ret = neo4j_merge(graphDB, bSkills)
                print("Neo4j inserted: %s" % ret)

        except Exception as e:
            write_log(str(e))
            continue

        # try:
        #     bSkillList = []
        #     for item in skill:
        #         bSkillList.append(item['Skills'])
        #
        #     for item in tool_tech:
        #         bSkillList.append(item['Skills'])
        #
        #     for item in industryKnowledge:
        #         bSkillList.append(item['Skills'])
        #
        #     for skill in bSkillList:
        #         bSkills = """
        #                     MATCH (c:`Job Title`)
        #                     Merge (b:`Business Skills` {Name: 'BusinessSkills'})
        #                     Merge (b)-[:WORKRELATEDSKILLSFOR]->(c)
        #                     Merge (t:`Skills` {Skill:'%s'})
        #                     Merge (t)-[:PARTOF]->(b)""" % (skill)
        #         ret = neo4j_merge(graphDB, bSkills)
        #         print("Neo4j inserted: %s" % ret)
        #
        # except Exception as e:
        #     write_log(str(e))
        #     continue

        # try:
        #     pSkillList = []
        #     for item in otherSkills:
        #         pSkillList.append(item['Skills'])
        #
        #     for item in interpersonal:
        #         pSkillList.append(item['Skills'])
        #
        #     for skill in pSkillList:
        #         pSkills = """
        #                     MATCH (c:`Job Title`{Name: '%s'})
        #                     CREATE (p:`Personal Skills` {Name:'PersonalSkills%d'})
        #                     CREATE (p)-[:PERSONAL_SKILL]->(c)
        #                     Merge (o:`Skills` {Skill:'%s'})
        #                     Merge (o)-[:PARTOF]->(p)""" % (jobTitle, count, skill)
        #         ret = neo4j_merge(graphDB, pSkills)
        #         print("Neo4j inserted: %s" % ret)
        #
        # except Exception as e:
        #     write_log(str(e))
        #     continue



    graphDB.close()
    print("completed")


