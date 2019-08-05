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

        ret = col.find().limit(3)

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

        Job_list = []
        company_list = []
        location_list = []
        years_list = []
        period_list = []
        index = 0

        for i in experience:
            Job_list.append(i['Job Title'])
            company_list.append(i['Company'].replace("'", ""))
            location_list.append(i['Location'])
            years_list.append(i['Years'])
            period_list.append(i['Period'])

        try:
            for element in Job_list:
                if len(Job_list) - 1 > index:
                    next_index = index + 1
                    jobs = """MERGE (c:`Job Title`{Name: '%s', Company:'%s', Location:'%s'})
                                   Merge (f:`Job Title` {Name:'%s', Company:'%s', Location:'%s', Years:'%s', Period:'%s'})
                                   Merge (f)-[:SWITHCEDTO]->(c)""" % (Job_list[index], company_list[index],
                                                                      location_list[index], Job_list[next_index],
                                                                      company_list[next_index], location_list[next_index],
                                                                      years_list[next_index], period_list[next_index])
                    index = index + 1
                    ret = neo4j_merge(graphDB, jobs)
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
                               Merge (j)-[:WORK_AT]->(c)""" % (Job_list[index], company, company)
                ret = neo4j_merge(graphDB, companies)
                print("Neo4j inserted: %s" % ret)
        except Exception as e:
            # write_log(str(e))
            print(e)
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
                            Merge (b)-[:PARTOF]->(t)""" % (company_list[0], Job_list[0], skill)
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
