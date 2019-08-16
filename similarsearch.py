# David Son 7/12/19
# This program takes in a field, and a word to search for
# and outputs all similar words or titles for that field.
# Then it goes through all the documents and replaces
# similar values with one standardizing group title.

# Important packages.
import decimal
import nltk
import string
import re
import json
import pymongo
import copy
from pymongo import MongoClient
from difflib import SequenceMatcher


def main():
    # Connecting to MongoDB to gather all of the documents.
    client = MongoClient('mongodb://34.73.180.107:27017')
    db = client.smartcareer
    col = db['Clean']
    allDocs = col.find({}, no_cursor_timeout=True)

    # User input for search and replace function.
    field = string.capwords(input("What is the field you are trying to change? "))
    newText = string.capwords(
        input("Please enter the group name. \nType 'All+' to display all values of the specified field.\n"))
    print()

    varSearch(allDocs, field, newText)


# NLP that removes all punctuation.
def punctuationRemover(description):
    noPunctuation = "".join([char for char in description if char not in string.punctuation])
    return noPunctuation


# NLP that splits words by space.
def tokenize(temp):
    tokens = re.split(r'\W+', temp)
    return tokens


# Take each document and find words or phrases similar to it.
# If there are equivalent values, increase the counter for that specific word.
# Afterwards, clean documents as needed.
def varSearch(docs, field, newText):
    similarCount = {}
    groupCount = {}
    lineCount = 0

    # Go through every document and for a specific field in each one, find similar groupings of words or titles.
    for i in docs:
        try:
            value = i.get(field)
            if newText in value and newText != "All+" and field != "Location":

                if value in similarCount:
                    similarCount[value] = similarCount.get(value) + 1

                else:
                    similarCount[value] = 1
                    if len(similarCount) > 0:

                        # Check the whole list for similar words and add to the group that is the shortest common subsequence of letters.
                        for key in similarCount.keys():
                            tMatch = SequenceMatcher(None, newText, key).find_longest_match(0, len(newText), 0,
                                                                                            len(key))

                        pureName = punctuationRemover(newText[tMatch.a: tMatch.a + tMatch.size])
                        pureName = pureName.strip()

                        if pureName in groupCount:
                            groupCount[pureName] = groupCount[pureName] + 1
                        else:
                            groupCount[pureName] = 1

                    else:
                        continue

                lineCount += 1

            # Special section for location only. Skips all the matching stuff since I already know what to replace it with.
            elif field == "Location":
                cityVal = value.split(",")
                if value in similarCount and cityVal[0] in newText:
                    similarCount[value] = similarCount.get(value) + 1

                elif cityVal[0] in newText:
                    similarCount[value] = 1
                    if len(similarCount) > 0:

                        pureName = newText

                        if pureName in groupCount:
                            groupCount[pureName] = groupCount[pureName] + 1
                        else:
                            groupCount[pureName] = 1

                lineCount += 1

            # New function: Just displays every document's specified field value. Useful for manual checking.
            elif newText == "All+":

                if value in similarCount:
                    similarCount[value] = similarCount.get(value) + 1

                else:
                    similarCount[value] = 1
                    if len(similarCount) > 0:

                        # Check the whole list for similar words and add to the group that is the shortest common subsequence of letters.
                        for key in similarCount.keys():
                            tMatch = SequenceMatcher(None, value, key).find_longest_match(0, len(value), 0, len(key))

                        pureName = punctuationRemover(value[tMatch.a: tMatch.a + tMatch.size])
                        pureName = pureName.strip()

                        # For All+, if there's more than one group we have to check through all of them for near-duplicates.
                        if len(groupCount) > 0:

                            # For each key in groupCount, try to get a match.
                            for gKey in groupCount.keys():
                                tMatch = SequenceMatcher(None, pureName, gKey).find_longest_match(0, len(pureName), 0,
                                                                                                  len(gKey))

                                # If they are exactly equal, add one to the counter of that key.
                                if pureName == gKey:
                                    groupCount[pureName] = groupCount[pureName] + 1

                                # Nearly matching, so it must be like 'Amazon' vs. 'Amazon Web Services'.
                                elif tMatch[2] > 5:

                                    # Take the shorter one and make that the main group. Remove the other longer key and give its value to the new one.
                                    if len(pureName) < len(gKey):
                                        addName = punctuationRemover(pureName[tMatch.a: tMatch.a + tMatch.size])
                                        addName = addName.strip()
                                        groupCount[addName] = groupCount.pop(gKey)

                                    # Same as above.
                                    else:
                                        addName = punctuationRemover(gKey[tMatch.b: tMatch.b + tMatch.size])
                                        addName = addName.strip()
                                        groupCount[addName] = groupCount[addName] + 1

                        else:
                            groupCount[pureName] = 1

                    else:
                        continue

                lineCount += 1

        # Skip this document since the field does not exist for it.
        except:
            continue

    print("Results:")
    print("Total Found:", lineCount, "\n")
    print("All similar texts:\n")

    # Rare occassion that similarsearch does not find anything. No need to continue.
    if (len(groupCount) == 0):
        print("There were no matches! Now stopping the program.")
        exit()

    # Print out each dictionary item and how many times it was found/percentage of all
    # documents with that word or phrase.
    for key, val in sorted(similarCount.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
        print("Ratio: {:7s} Count: {:<5d} Text: {:40s}".format(str(round((val / lineCount * 100), 2)) + "%", val, key))

    print()
    print("The group(s) of similar topics.\n")

    # Print out each topic and how many variations they have each.
    for key, val in sorted(groupCount.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
        print("Group: {:40s} Variations: {:1d}".format(key, val))
        print()

    # This section is just to confirm what will be changed in the main collection.
    choice = input(
        "[MODE CHOICE]\n[1] Auto Change to \"" + newText + "\" \n[2] Auto Change to something NEW! \n[3] Manually Change to New Text \n[4] Quit \nMODE[1,2,3,4]: ")

    # Choice 1 will automatically change all of the above to the search value.
    # Choice 2 will automatically change all of the above to the user specified value.
    if choice == "1" or choice == "2":
        x = 1
        if choice == "2":
            newText = input("Enter NewText that you want: ")
        for key, val in sorted(similarCount.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
            while x != 0:
                myquery = {field: key}
                newvalues = {"$set": {field: newText}}
                client = MongoClient('mongodb://34.73.180.107:27017')
                db = client.smartcareer
                col = db['Clean']
                x = col.update_many(myquery, newvalues)
                print(x.modified_count, "documents updated.")
                if x.modified_count == 0:
                    break
            # docReplacer(doClone, field, groupCount)
        exit()

    # Choice 3 allows the user to manually submit changes after reviewing each document.
    elif choice == "3":
        for key, val in sorted(similarCount.items(), key=lambda kv: (kv[1], kv[0]), reverse=True):
            while True:
                print(key)
                newText = input("Enter New Text: ")
                myquery = {'Experience.Location': key}
                newvalues = {"$set": {'Experience.$.Location': newText}}
                client = MongoClient('mongodb://34.73.180.107:27017')
                db = client.smartcareer
                col = db['Clean']
                x = col.update_many(myquery, newvalues)
                print(x.modified_count, "documents updated.")
                if x.modified_count == 0:
                    break
        exit()

main()
