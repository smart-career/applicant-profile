<<<<<<< HEAD
# Smart-Career Scraper v1.1

## Changelog v1.2:
### Additions:
+ Added direct upload of any job description to MongoDB (and fixed weird issues with it)
+ Now ignores duplicates when adding data.
+ Added a config file where the first line = job description and second line = period
### Changes:
+ No longer takes user input. Use config file instead.
### Removals (Just commented out):
+ None

## Changelog v1.1:
### Additions:
+ Added direct upload of any job description to MongoDB
+ Filters results to past week only.
+ Added some comments to help understand code.
### Changes:
+ Changed hard limit to 100 job descriptions to A. Test and B. Avoid stalling.
+ Currently testing getting rid of duplicates.
### Removals (Just commented out):
+ Got rid of period selection as we are focusing on past week for now.

## Changelog v1.0:
+ Initial scraper
=======
# Smart-Career Applicant Profile v1.8

## Changelog v1.8
### Additions/Changes:
+ Upload to neo4j successful.
+ Extraction of nested dictionaries successful
+ Using my local database for now.
+ Got personal skills to surround the personal skill node... Business skills nowhere to be found.
### Removals:
### To Do:
+ Get newer data that includes job titles?
+ Fix any formatting issues for our graphs

## Changelog v1.7
### Additions/Changes:
+ Framework for tomorrow.
### Removals:
+ The data extractor since... Mr. Song came up with the MongoDB to Neo4j program
### To Do:
+ Parsing through nested dictionaries.
+ Attaching a list of skills and other nodes to one entity
+ Formatting that follows our schematic

## Changelog v1.6
### Additions/Changes:
+ Jae is currently working on a new data extractor.
+ app.json which is a full export of the collection on MongoDB
### Removals:
### To Do:
+ Indeed profile scraping
+ LinkedIn data parsing

## Changelog v1.5
### Additions:
+ Date captured has been added and will apply to all future documents.
### Changes:
+ Fixed a bug where job titles and companies were not being parsed correctly. 
They will now show up in all future documents as well.
+ Changed formatting of the output log.
+ Swapped the scheduler times between pscheduler and scheduler. This is because scheduler
has no limit and therefore will take longer.
### Removals:

## Changelog v1.4
### Additions:
+ Can now see when and how many documents have been added to MongoDB via the "docnum.txt".
### Changes:
+ Changed 5 pages each to 6, to test load. Will increase by one each day.
+ Changed xpath of job_title and company so data will be properly stored.
  (Testing tomorrow since we have hit search limit!)
### Removals:

## Changelog v1.3
### Additions:
### Changes:
+ Now automatically looks up people for multiple job titles.
+ pscheduler now runs at 2pm.
+ Added extra job titles to cfg.txt
### Removals:

## Changelog v1.2
### Additions:
+ *NEW* file: pscheduler.py that, when run, will run get_people.py once a day at 1pm.
### Changes:
+ Capped page search to 5 for now so session is not kicked.
+ Seperated each script into its own folder.
### Removals:
+ My old repository (Still there, just not in use)
+ Date Captured. I could not get this to work on get_people.py

## Changelog v1.1:
+ Seperated this from job description scraper
+ Added config file
+ Trying to add date captured.

## Changelog v1.0:
+ Initial scraper
>>>>>>> 69fbffc7ae8814b6eeaaa7d0603d1f43bf56241c
