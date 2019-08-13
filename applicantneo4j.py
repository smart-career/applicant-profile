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
    col = mongodb_get_collection(db, 'Applicantprofile')

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

        ret = col.find().limit(100)

    except Exception as e:
        print(e)

    return ret


# Neo4j Functions
def neo4j_init():
    uri = "bolt://localhost:7687"
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
            merged_list.append("e" + list3[j])
            j += 1
        elif job_year > edu_year:
            merged_list.append("j" + list4[i])
            i += 1
        else:
            merged_list.append("j" + list4[i])
            merged_list.append("e" + list3[j])
            j += 1
            i += 1

    # job_time 에 남은 원소가 있다면, merged_list에 추가하기
    if i < len(list4):
        for k in list4[i:]:
            merged_list.append("j" + k)
    # edu_time 에 남은 원소가 있다면, merged_list에 추가하기
    if j < len(list3):
        for l in list3[j:]:
            merged_list.append("e" + l)
    return merged_list

if "__main__":

    print("Starting")
    docs = mongodb_read_docs('Applicantprofile')
    graphDB = neo4j_init()
    count = 0
    for d in docs:
        count += 1
        jobTitle = d.get('Job Title')
        if jobTitle == "":
            continue
        jobTitle = d['Job Title']
        location = d['Location']
        experience = d.get('Experience')
        education = d.get('Education')
        skill = d.get('Skills \u0026 Endorsements')
        industryKnowledge = d.get('Industry Knowledge')
        tool_tech = d.get('Tools \u0026 Technologies')
        interpersonal = d.get('Interpersonal Skills')
        otherSkills = d.get('Other Skills')

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
            location_list.append(item['Location'].replace("'", ""))
            years_list.append(item['Years'])
            period_list.append(item['Period'])

        edu_list = []
        edu_time = []
        edu_degree = []
        for edu in education:
            edu_time.append(edu['Date Attended'])
            edu_list.append(edu['School'].replace("'", ""))
            edu_degree.append(edu['Degree'].replace("'", ""))

        if len(edu_time) != 0 and len(period_list) != 0:
            try:
                job_n_edu_list = merge(job_time, edu_time, edu_list, job_list)
                comp_n_edu_list = merge(job_time, edu_time, edu_list, company_list)
                loc_n_edu_list = merge(job_time, edu_time, edu_list, location_list)
                per_n_edu_list = merge(job_time, edu_time, edu_list, period_list)
                job_n_deg_list = merge(job_time, edu_time, edu_degree, job_list)
            except Exception as e:
                print(e)
                #write_log(str(e))
                continue

        current_index = 0

        try:
            for element in job_n_edu_list[:-1]:
                next_index = current_index + 1
                #job to job
                if element.startswith("j") and job_n_edu_list[next_index].startswith("j"):
                    jobs_to_jobs = """MERGE (c:`Job Title`{Name: '%s', Company:'%s', Location: '%s', Period: '%s'})
                                   Merge (f:`Job Title`{Name:'%s', Company: '%s', Location: '%s', Period: '%s'})
                                   Merge (f)-[:SWITHCEDTO]->(c)""" % (element[1:], comp_n_edu_list[current_index][1:], loc_n_edu_list[current_index][1:], per_n_edu_list[current_index][1:],
                                                                      job_n_edu_list[next_index][1:], comp_n_edu_list[next_index][1:], loc_n_edu_list[next_index][1:], per_n_edu_list[next_index][1:])
                    ret = neo4j_merge(graphDB, jobs_to_jobs)

                elif element.startswith("j") and job_n_edu_list[next_index].startswith("e"):
                    edu_to_jobs = """MERGE (c:`Job Title`{Name: '%s', Company:'%s', Location: '%s', Period: '%s'})
                                   Merge (f:`Education`{Name:'%s', Degree: '%s'})
                                   Merge (f)-[:SWITHCEDTO]->(c)""" % (element[1:], comp_n_edu_list[current_index][1:],loc_n_edu_list[current_index][1:], per_n_edu_list[current_index][1:],
                                                                      job_n_edu_list[next_index][1:], job_n_deg_list[next_index][1:])
                    ret = neo4j_merge(graphDB, edu_to_jobs)

                elif element.startswith("e") and job_n_edu_list[next_index].startswith("j"):
                    jobs_to_edu = """MERGE (c:`Education`{Name: '%s', Degree: '%s'})
                                       Merge (f:`Job Title`{Name:'%s', Company: '%s', Location: '%s', Period: '%s'})
                                       Merge (f)-[:SWITHCEDTO]->(c)""" % (element[1:], job_n_deg_list[current_index][1:],
                                                                          job_n_edu_list[next_index][1:], comp_n_edu_list[next_index][1:], loc_n_edu_list[next_index][1:], per_n_edu_list[next_index][1:])
                    ret = neo4j_merge(graphDB, jobs_to_edu)

                elif element.startswith("e") and job_n_edu_list[next_index].startswith("e"):
                    edu_to_edu = """MERGE (c:`Education`{Name: '%s', Degree: '%s'})
                                       Merge (f:`Education`{Name:'%s', Degree: '%s'})
                                       Merge (f)-[:SWITHCEDTO]->(c)""" % (element[1:], job_n_deg_list[current_index][1:],
                                                                          job_n_edu_list[next_index][1:], job_n_deg_list[next_index][1:])
                    ret = neo4j_merge(graphDB, edu_to_edu)
                current_index += 1
                print("Neo4j inserted: %s" % ret)
        except Exception as e:
            # write_log(str(e))
            print(e)
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
            # print(e)
            continue


        try:
            SkillList = []
            for item in skill:
                SkillList.append(item['Skills'])

            for skill in SkillList:
                Skills = """
                            MATCH (c:`Company`{Name: '%s'})
                            Merge (b:`Skills` {Name: 'Skills', `Job Title`: '%s'})
                            Merge (c)-[:REQUIRES]->(b)
                            Merge (t:`Skill` {Skill:'%s'})
                            Merge (b)-[:PARTOF]->(t)""" % (company_list[0], job_list[0], skill)
                ret = neo4j_merge(graphDB, Skills)
                print("Neo4j inserted: %s" % ret)

        except Exception as e:
            write_log(str(e))
            print(e)
            continue

        try:
            for loc in location_list:
                if loc != '':
                    index = location_list.index(loc)
                    Locations = """
                                MATCH (c:`Company`{Name: '%s'})
                                Merge (l:`Location` {Name: '%s'})
                                Merge (c)-[:LOCATED_AT]->(l)""" % (company_list[index], loc)
                    ret = neo4j_merge(graphDB, Locations)
                    print("Neo4j inserted: %s" % ret)

        except Exception as e:
            # write_log(str(e))
            print(e)
            continue

    graphDB.close()
    print("completed")


