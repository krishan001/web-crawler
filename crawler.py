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
    # base_url = "http://example.webscraping.com/places/default/view/Canada-41"

    page_list = ["/"]
    dict_text = {}
   
    for page in page_list:
        url_new = requests.get(base_url.__add__(page))
        # HTML parser
        soup_new = BeautifulSoup(url_new.content, 'html.parser')

        texts = soup_new.find_all(text=True)
        visible_texts = filter(visible, texts)
        text = " ".join(t.strip() for t in visible_texts)

        words = text.split()

        for word in words:
            if word not in dict_text:
                dict_text[word] = {page: 1}
            else:
                if page in dict_text[word]:
                    dict_text[word][page] += 1
                else:
                    dict_text[word].update({page: 1})

        time.sleep(1)
        try:
            link_new_body = soup_new.find('body')
            for link_new in link_new_body.find_all('a'):

                if link_new.get('href') == "#":
                    continue

                # link_new = link_new.get("href").split("?")[0].split("index")[0].split("iso")[0].split("edit")[0]
                link_new = link_new.get("href").split("?")[0]

                if link_new not in page_list:
                    print(link_new)
                    page_list.append(link_new)

        except:
            print("error with link")

    print(len(page_list))
    with open("pages.txt", 'w') as f:
        for item in page_list:
            f.write("%s\n" % item)
    return dict_text


def search(keyword, data):
    # print(data[keyword])
    for url in data[keyword]:
        print(url, " ", end = "")
        print(data[keyword][url])
    return keyword

def find(arguments,data):
    num_arguments = len(arguments)
    page_list = []
    i = 0
    temp_list = []
    while(i<num_arguments):
        word = arguments[i]
        for url in data[word]:
            temp_list.append(url)
        if i == 0:
            page_list = temp_list
        else:
            new_list = set(page_list) & set(temp_list)
            page_list = list(new_list)
        temp_list = []
        i+=1
    # list of pages that are shared by all the arguments
    print(page_list)
    

def main():
    while True:

        user_input = input("\n\nEnter a command\n")

        user_input_split = user_input.split()

        if user_input_split[0] == "build":
            start = timer()
            dict_text = build()
            print(dict_text)
            try:
                with open('index.json', 'w') as fp:
                    json.dump(dict_text, fp)
            except:
                print("Build not complete, no file to save")
            end = timer()
            print(end - start)

        elif user_input_split[0] == "load":
            try:
                with open('index.json', 'r') as fp:
                    data = json.load(fp)
                    print(data)
            except:
                print("file does not exist, run build")

        elif user_input_split[0] == "print":
            try:
                search(user_input_split[1], data)
            except:
                print("error searching")


        elif user_input_split[0] == "find":
            try:
                find(user_input_split[1:], data)
            except:
                print("error")

if __name__ == '__main__':
    main()
