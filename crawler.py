from bs4 import BeautifulSoup
from bs4.element import Comment
import requests
import time
from timeit import default_timer as timer
import json
from collections import Counter

def visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def build():
    base_url = "http://example.webscraping.com"

    page_list = ["/"]
    page_dict = {}
   
    for page in page_list:
        # Get the html
        url_new = requests.get(base_url.__add__(page))
        # HTML parser
        soup = BeautifulSoup(url_new.content, 'html.parser')

        texts = soup.find_all(text=True)
        visible_texts = filter(visible, texts)
        text = " ".join(t.strip() for t in visible_texts)

        words = text.split()
        # add words to dictionary with their frequency
        for word in words:
            word = word.replace(":","")
            if word not in page_dict:
                page_dict[word] = {page: 1}
            else:
                if page in page_dict[word]:
                    page_dict[word][page] += 1
                else:
                    page_dict[word].update({page: 1})
        # make a request every 5 seconds
        time.sleep(5)
        try:
            link_new_body = soup.find('body')
            for link_new in link_new_body.find_all('a'):

                if link_new.get('href') == "#":
                    continue

                link_new = link_new.get("href").split("?")[0].split("edit")[0]

                if link_new not in page_list:
                    print(link_new)
                    page_list.append(link_new)

        except:
            print("error with link")

    print(len(page_list))
    with open("pages.txt", 'w') as f:
        for item in page_list:
            f.write("%s\n" % item)
    return page_dict


def search(keyword, data):
    print("\n")
    for url in data[keyword]:
        print(url, " ", end = "")
        print(data[keyword][url])
    return keyword

def find(arguments,data):
    print("\n")

    num_arguments = len(arguments)
    page_list = []
    temp_list = []
    i = 0
    while(i < num_arguments):
        word = arguments[i]
        # print(word)
        # add all the pages for a particular word
        for url in data[word]:
            # print(data[word][url])
            temp_list.append(url)
    
        if i == 0:
            page_list = temp_list
        else:
            # only keep the values that are in both lists
            new_list = set(page_list) & set(temp_list)
            page_list = list(new_list)
        temp_list = []
        i+=1
    # list of pages that are shared by all the arguments
    if len(page_list) == 0:
        print("There are no pages that contain all of these words")
    else:
        rank(arguments, data, page_list)

def rank(arguments, data, page_list):
    counter = 0
    rank_dict = {}
    # gives each page a number
    for page in page_list:
        # initialise rank dict
        rank_dict[page] = 0
        for word in arguments:
            rank_dict[page] += data[word][page]
    # sorts the dictionary so that the highest number is first
    sorted_dict = {k: v for k, v in sorted(rank_dict.items(), key=lambda item:item[1], reverse = True)}
    for k,v in sorted_dict.items():
        counter+=1
        print(counter, ") ", end = "")
        print(k,v)
        
    pass


def main():
    print("\n\nCommands: \n")
    print(" build - crawls the webpage and creates an inverted index")
    print(" load - loads the inverted index from file if one exists")
    print(" print [word] - takes in a word and displays the inverted index for that word")
    print(" find [query phrase] - finds a certain query phrase in the inverted index and returns a list of all pages containing this phrase ")
    while True:

        user_input = input("\n\nEnter a command: ")
        user_input_split = user_input.split()

        # builds the index
        if user_input_split[0] == "build":
            start = timer()
            dict_text = build()
            # print(dict_text)
            try:
                with open('index.json', 'w') as fp:
                    json.dump(dict_text, fp)
            except:
                print("Build not complete, no file to save")
            end = timer()
            print(end - start)
        
        # loads the index
        elif user_input_split[0] == "load":
            try:
                with open('index.json', 'r') as fp:
                    data = json.load(fp)

            except:
                print("file does not exist, run build")
        # prints out
        elif user_input_split[0] == "print":
            try:
                search(user_input_split[1], data)
            except:
                print("error searching")

        # finds a query phrase
        elif user_input_split[0] == "find":
            try:
                find(user_input_split[1:], data)
            except:
                print("error")
        else:
            print("Invalid command")

if __name__ == '__main__':
    main()
