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
        ret = doc['JobID']

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

def expAdd():
    print("hello")

def eduAdd():
    print("hello")

def skillsAdd():
    print("hello")

def industryAdd():
    print("hello")

def toolAdd():
    print("hello")

def othersAdd():
    print("hello")


if "__main__":

    print("Starting")
    docs = mongodb_read_docs('applicantprofile')
    graphDB = neo4j_init()

    for d in docs:
        jobTitle = d['Job Title']
        company = d['Company']
        location = d['Location']
        experience = d.get('Experience')
        education = d.get('Education')
        skill = d.get('Skills \u0026 Endorsements')
        industryKnowledge = d.get('Industry Knowledge')
        tool_tech = d.get('Tools \u0026 Technologies')
        interpersonal = d.get('Interpersonal Skills')
        otherSkills = d.get('Other Skills')

        cqlNode = """Merge (j:`Job Title` {Name:'%s'})
                 Merge (c:`Company` {Name:'%s'})
                 Merge (l:`Location` {Name:'%s'})
                 Merge (e:`Experience` {Name:'%s'})
                 Merge (ed:`Education` {Name:'%s'})
                 Merge (s:`Skills & Endorsements` {Name:'%s'})
                 Merge (i:`Industry Knowledge` {Name:'%s'})
                 Merge (t:`Tools & Technology` {Name: '%s'})
                 Merge (in:`Interpersonal Skils` {Name: '%s'})   
                 Merge (o:`Other Skills` {Name: '%s'})        
                 Merge (j)-[:WORK AT]->(c)
                 Merge (j)-[:LOCATED AT]->(l)
                 Merge (j)-[:EXPERIENCED AT]->(e)
                 Merge (j)-[:EDUCATED AT]->(ed)
                 Merge (j)-[:HAS]->(s)
                 Merge (j)-[:HAS]->(i)
                 Merge (j)-[:HAS]->(t)
                 Merge (j)-[:HAS]->(in)""" % (jobTitle, company, location, experience,
                                             education, skill, industryKnowledge,
                                             tool_tech, interpersonal, otherSkills)

        try:
            ret = neo4j_merge(graphDB, cqlNode)
        except Exception as e:
            write_log(str(e))
            continue

        print("Neo4j inserted: %s" % ret)

    graphDB.close()
    print("completed")
