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
