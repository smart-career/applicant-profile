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
    db = client.Backup
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

        ret = col.find().limit(50)

    except Exception as e:
        print(e)

    return ret


# Neo4j Functions
def neo4j_init():
    uri = "bolt://localhost"
    userName = "neo4j"
    passwd = "Random1234"
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

    for d in docs:
        jobTitle = d.get('Job Title')
        company = d.get('Company')
        location = d.get('Location')
        experience = d.get('Experience')
        education = d.get('Education')
        skill = d.get('Skills \u0026 Endorsements')
        industryKnowledge = d.get('Industry Knowledge')
        tool_tech = d.get('Tools \u0026 Technologies')
        interpersonal = d.get('Interpersonal Skills')
        otherSkills = d.get('Other Skills')

        cqlNode = """Merge (c:`Job Title` {Name:'%s', Company:'%s'})
                 Merge (l:`Location` {Name:'%s'})
                 Merge (c)-[:LOCATEDAT]->(l)""" % (jobTitle, company, location)

        try:
            ret = neo4j_merge(graphDB, cqlNode)

        except Exception as e:
            write_log(str(e))
            continue

        print("Neo4j inserted: %s" % ret)

        try:
            for item in experience:
                title = item['Job Title']
                comp = item['Company'].replace("'","")
                loc = item['Location']
                years = item['Years']
                formerJob = """Merge (f:`Former Job` {Name:'%s', Company:'%s', Location:'%s', Years:'%s'})
                               Merge (c)-[:PREVIOUSLYWORKEDAT]->(f)""" % (title, comp, loc, years)
                ret = neo4j_merge(graphDB, formerJob)
                print("Neo4j inserted: %s" % ret)

        except Exception as e:
            write_log(str(e))
            continue
        
        try:
            for item in education:
                school = item['School']
                degree = item['Degree'].replace("'","")
                dateWent = item['Date Attended']
                eduExp = """Merge (ed:`Education` {School:'%s', Degree:'%s', Attended:'%s'})
                            Merge (c)-[:KNOWLEDGEGAINEDFROM]->(ed)""" % (school, degree, dateWent)
                ret = neo4j_merge(graphDB, eduExp)
                print("Neo4j inserted: %s" % ret)

        except Exception as e:
            write_log(str(e))
            continue
            
        try:
            bSkillList = []
            for item in skill:
                bSkillList.append(item['Skills'])
            
            for item in tool_tech:
                bSkillList.append(item['Skills'])
            
            for item in industryKnowledge:
                bSkillList.append(item['Skills'])
            
            for skill in bSkillList:
                bSkills = """Merge (b:`Business Skills` {Name: 'BusinessSkills'})
                            Merge (b)-[:WORKRELATEDSKILLSFOR]->(c)
                            Merge (t:`Skills` {Skill:'%s'})
                            Merge (t)-[:PARTOF]->(b)""" % (skill)
                ret = neo4j_merge(graphDB, bSkills)
                print("Neo4j inserted: %s" % ret)

        except Exception as e:
            write_log(str(e))
            continue

        try:
            pSkillList = []
            for item in otherSkills:
                pSkillList.append(item['Skills'])

            for item in interpersonal: 
                pSkillList.append(item['Skills'])  

            for skill in pSkillList:
                pSkills = """Merge (p:`Personal Skills` {Name:'PersonalSkills'})
                            Merge (p)-[:PERSONALSKILLSFOR]->(c)
                            Merge (o:`Skills` {Skill:'%s'})
                            Merge (o)-[:PARTOF]->(p)""" % (skill)
                ret = neo4j_merge(graphDB, pSkills)
                print("Neo4j inserted: %s" % ret)
    
        except Exception as e:
            write_log(str(e))
            continue



    graphDB.close()
    print("completed")
