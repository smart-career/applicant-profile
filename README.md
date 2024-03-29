# Smart-Career Applicant Profile v2.1

## Changelog v2.1
### Additions/Changes:
+ Scraper now skips profiles that have already been added to MongoDB.
+ Jae has been working on applicantneo4j.py and it is almost complete.
### Removals:
### To Do:
+ Fix bugs.
+ Get more Data.

## Changelog v2.0
### Additions/Changes:
+ Got rid of endorsements as it is a useless statistic.
+ Company names should be fixed?
+ Skills show more button should now be clicked to gather all skills
### Removals:
+ app.json since we no longer need this backup.
+ cfg.txt since Mr. Song created a new JSON file.
### To Do:
+ Fix bugs.
+ Get more Data.

## Changelog v1.9
### Additions/Changes:
+ Jaeseung found a couple of errors in the code, specifically using d.get when d[] is all that is needed.
+ Also fixed an error with relationships between jobs and education
+ Mr. Song pushed a new cfg.json file to go along with the new get_people.py
+ Jaeseung identified the cause of business skills not showing up and helped me fix it.
+ Job titles are now showing, had to reach the end of the documents to get them.
+ Fixed formatting for the most part.
### Removals:
### To Do:
+ Get more data.
+ Make it look pretty.

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
