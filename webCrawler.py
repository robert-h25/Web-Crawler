#Imports
import re
import time
import requests
from bs4 import BeautifulSoup

#global variables
base_url = "https://quotes.toscrape.com"
politeness_policy = 6
urls = []
urls_searched = []
words = {}

# Function to search a page for words and a tags    
def search_page():
    index = 0
    # Continue searching until all URLs are processed
    while index < len(urls):
        url = urls[index]
        if url not in urls_searched:
            print("Searching",base_url+url)
            # make request to url after politeness policy
            time.sleep(0.1)
            response = requests.get(base_url+url)
            #correct response
            if response.status_code == 200:
                urls_searched.append(url)
                #parse page
                page_parse = BeautifulSoup(response.content,'html.parser')
                # Remove the <head> tag and its content
                head_tag = page_parse.find('head')
                if head_tag:
                    head_tag.decompose()
                text = page_parse.get_text()
                # get all words including apostrophes
                words_in_page = re.findall(r'\b(?:\w+(?:\'\w+)?)+\b', text.lower())
                add_words_to_dict(words_in_page,index)
                #get a tags
                next_page = page_parse.find_all("a")
                for a_tag in next_page:
                    #get href 
                    href = a_tag.get("href")
                    #ignore http to new sites and visited urls
                    if not href.startswith("http"):            
                        next_url =a_tag["href"]
                        if next_url not in urls_searched and next_url not in urls:
                            # add to an array of urls to search
                            urls.append(next_url)
            else:
                print("Failed to crawl")
                return
        # Move to the next URL
        index += 1                  
    return


# Function to add a word to a dictionary with its count and index
def add_words_to_dict(words_in_page, url_index):
    #list of check words 
    checked_words = []
    for word in words_in_page:
        #new word in words_in_page
        if word not in checked_words:
            #words exists in dictionary already
            if word in words:
                count = words_in_page.count(word)
                #append to dict
                words[word].append((count, url_index))
            #new word
            else:
                count = words_in_page.count(word)
                words[word] = [(count, url_index)]
            checked_words.append(word)

# Function to write words dict to inverted index 
def write_to_file():
    #first clear file
    with open("inverted_index.txt", 'w') as file:
        file.truncate(0)
    # open to write to
    with open("inverted_index.txt", "w",encoding="utf-8") as file:
        for word, value in words.items():
            # write in format word:(value)
            file.write(word + ': ')
            # list of count,index
            for count, index in value:
                #write value as (count1,index1)...(countn,indexn)
                file.write(f'({count}, {index}) ')
            file.write('\n') 
    words.clear()  

#Function to load index from file and save in dictionary words
def load_index():
    #open file
    with open("inverted_index.txt", 'r',encoding="utf-8") as file:
        for line in file:
            #split line into word and data
            parts = line.strip().split(':')
            current_word = parts[0].strip() 
            data = parts[1].strip() 
            line_array = []
            line_array.append((current_word,data))
            data_array = string_to_array(line_array[0])
            #add to words dict
            words[current_word] = [(data_array[0][0],data_array[0][1])]
            # then for loop and append
            for i in range(1,len(data_array)):
                words[current_word].append((data_array[i][0],data_array[i][1]))
    #return
    return words

# Function to search for a word from inverted_index
def print_inverted_index(word):
    #open file
    with open("inverted_index.txt", 'r',encoding="utf-8") as file:
        for line in file:
            #split line into word and data
            index_line = line.strip().split(':')
            current_word = index_line[0].strip() 
            data = index_line[1].strip() 
            # search for word and compare
            if current_word == word:
                #order by number of times it occurs                          
                return current_word, rank_inverted_index(data)
        print(word,"does not exist in the inverted index")
        return 0,[]

# Function to rank the inverted index word by count
def rank_inverted_index(data):
    #split by space between brackets (as formatted)
    count_index = data.split(') (')
    index = []
    for pair in count_index:
        # remove brackets
        pair = pair.strip('()')        
        # split by comma
        numbers = pair.split(',')
        # convert to ints
        numbers = [int(num) for num in numbers]
        index.append(numbers)
    #sort array by highest count first
    sorted_array = sorted(index, key=lambda x: -x[0])
    return sorted_array    

#Function to convert a string to an array
def string_to_array(string):
    #split by space between brackets (as formatted)
    count_index = string[1].split(') (')
    array = []
    for pair in count_index:
        # remove brackets
        pair = pair.strip('()')        
        # split by comma
        numbers = pair.split(',')
        # convert to ints
        numbers = [int(num) for num in numbers]
        array.append(numbers)
    return array

# Function to find words from the words command
def find_words(words):
    #split words by space
    words = words.split()
    words_data = []
    # 1 word
    if len(words)==1:
        # print page
        word,data = print_inverted_index(''.join(words))
        for pair in data:
                # change to print index
                print(word,"appears",pair[0],"time(s) in document",base_url+urls_searched[pair[1]])     
        return
    
    #open file
    words_found = 0
    with open("inverted_index.txt", 'r',encoding="utf-8") as file:
        for line in file:
            #split line into word and data
            parts = line.strip().split(':')
            current_word = parts[0].strip() 
            data = parts[1].strip() 
            # search for word and compare
            if current_word in words:
                words_found+=1
                words_data.append((current_word,data))

        # Amount of words found
        if words_found == 0:        
            print(words,"does not exist in the inverted index") 
            return
        elif words_found<len(words):
            word_list = [word[0] for word in words_data]
            print("At least one word does not exist in the inverted index.",word_list,"found.")
        else:
            word_list = [word[0] for word in words_data]
            print("All words exist in the inverted index.")

    #combine indexes for all wordsfound
    indexes = []
    #print(words_data)
    for i in range(len(words_data)):
        for j in range(i+1, len(words_data)):
            matching_indexes = combine_indexes(words_data[i],words_data[j])
            indexes.extend(matching_indexes)
    # count number of indexes
    count_index = count_indexes(indexes)
    
    #print(count_index)
    
    sorted_counts = sorted(count_index.items(), key=lambda x: x[1], reverse=True)
    #print(sorted_counts)
    #urls_searched =['/', '/login', '/author/Albert-Einstein',                     '/tag/change/page/1/', '/tag/deep-thoughts/page/1/', '/tag/thinking/page/1/', '/tag/world/page/1/', '/author/J-K-Rowling', '/tag/abilities/page/1/', '/tag/choices/page/1/', '/tag/inspirational/page/1/', '/tag/life/page/1/', '/tag/live/page/1/', '/tag/miracle/page/1/', '/tag/miracles/page/1/', '/author/Jane-Austen', '/tag/aliteracy/page/1/', '/tag/books/page/1/', '/tag/classic/page/1/', '/tag/humor/page/1/', '/author/Marilyn-Monroe', '/tag/be-yourself/page/1/', '/tag/adulthood/page/1/', '/tag/success/page/1/', '/tag/value/page/1/', '/author/Andre-Gide', '/tag/love/page/1/', '/author/Thomas-A-Edison', '/tag/edison/page/1/', '/tag/failure/page/1/', '/tag/paraphrased/page/1/', '/author/Eleanor-Roosevelt', '/tag/misattributed-eleanor-roosevelt/page/1/', '/author/Steve-Martin', '/tag/obvious/page/1/', '/tag/simile/page/1/', '/page/2/', '/tag/love/', '/tag/inspirational/', '/tag/life/', '/tag/humor/', '/tag/books/', '/tag/reading/', '/tag/friendship/', '/tag/friends/', '/tag/truth/', '/tag/simile/', '/author/Terry-Pratchett', '/tag/open-mind/page/1/', '/tag/friends/page/1/', '/tag/heartbreak/page/1/', '/tag/sisters/page/1/', '/author/Elie-Wiesel', '/tag/activism/page/1/', '/tag/apathy/page/1/', '/tag/hate/page/1/', '/tag/indifference/page/1/', '/tag/opposite/page/1/', '/tag/philosophy/page/1/', '/tag/death/page/1/', '/author/George-Eliot', '/author/C-S-Lewis', '/tag/reading/page/1/', '/tag/tea/page/1/', '/author/Martin-Luther-King-Jr', '/tag/hope/page/1/', '/author/Helen-Keller', '/tag/inspirational/page/2/', '/author/Douglas-Adams', '/tag/navigation/page/1/', '/author/Mark-Twain', '/tag/contentment/page/1/', '/tag/friendship/page/1/', '/author/Allen-Saunders', '/tag/fate/page/1/', '/tag/misattributed-john-lennon/page/1/', '/tag/planning/page/1/', '/tag/plans/page/1/', '/author/Dr-Seuss', '/tag/comedy/page/1/', '/tag/yourself/page/1/', '/author/George-Bernard-Shaw', '/author/Ralph-Waldo-Emerson', '/tag/regrets/page/1/', '/tag/life/page/2/', '/author/Jorge-Luis-Borges', '/tag/library/page/1/', '/author/Haruki-Murakami', '/tag/thought/page/1/', '/author/Ernest-Hemingway', '/tag/novelist-quotes/page/1/', '/author/J-D-Salinger', '/tag/authors/page/1/', '/tag/literature/page/1/', '/tag/writing/page/1/', '/author/Madeleine-LEngle', '/tag/children/page/1/', '/tag/difficult/page/1/', '/tag/grown-ups/page/1/', '/tag/write/page/1/', '/tag/writers/page/1/', '/tag/books/page/2/', '/author/Garrison-Keillor', '/tag/religion/page/1/', '/author/Jim-Henson', '/author/Charles-M-Schulz', '/tag/chocolate/page/1/', '/tag/food/page/1/', '/author/Suzanne-Collins', '/author/Charles-Bukowski', '/author/George-Carlin', '/tag/insanity/page/1/', '/tag/lies/page/1/', '/tag/lying/page/1/', '/tag/self-indulgence/page/1/', '/tag/truth/page/1/', '/tag/humor/page/2/', '/author/Bob-Marley', '/author/Friedrich-Nietzsche', '/tag/lack-of-friendship/page/1/', '/tag/lack-of-love/page/1/', '/tag/marriage/page/1/', '/tag/unhappy-marriage/page/1/', '/author/Pablo-Neruda', '/tag/poetry/page/1/', '/tag/girls/page/1/', '/author/James-Baldwin', '/tag/love/page/2/', '/author/Mother-Teresa', '/tag/misattributed-to-mother-teresa/page/1/', '/author/Stephenie-Meyer', '/tag/drug/page/1/', '/tag/romance/page/1/', '/tag/courage/page/1/', '/tag/simplicity/page/1/', '/tag/understand/page/1/', '/tag/fantasy/page/1/', '/page/1/', '/page/3/', '/tag/learning/page/1/', '/tag/seuss/page/1/', '/author/William-Nicholson', '/tag/misattributed-to-c-s-lewis/page/1/', '/author/George-R-R-Martin', '/tag/read/page/1/', '/tag/readers/page/1/', '/tag/reading-books/page/1/', '/author/Alfred-Tennyson', '/tag/misattributed-mark-twain/page/1/', '/author/Jimi-Hendrix', '/author/John-Lennon', '/tag/beatles/page/1/', '/tag/connection/page/1/', '/tag/dreamers/page/1/', '/tag/dreaming/page/1/', '/tag/dreams/page/1/', '/tag/peace/page/1/', '/author/Khaled-Hosseini', '/tag/good/page/1/', '/tag/fairy-tales/page/1/', '/tag/mind/page/1/', '/tag/christianity/page/1/', '/tag/faith/page/1/', '/tag/sun/page/1/', '/author/W-C-Fields', '/tag/sinister/page/1/', '/tag/romantic/page/1/', '/tag/women/page/1/', '/author/J-M-Barrie', '/tag/adventure/page/1/', '/author/E-E-Cummings', '/tag/happiness/page/1/', '/tag/attributed-no-source/page/1/', '/tag/imagination/page/1/', '/tag/music/page/1/', '/page/4/', '/tag/knowledge/page/1/', '/tag/understanding/page/1/', '/tag/wisdom/page/1/', '/tag/dumbledore/page/1/', '/page/5/', '/page/6/', '/tag/attributed/page/1/', '/tag/fear/page/1/', '/tag/inspiration/page/1/', '/author/Alexandre-Dumas-fils', '/tag/misattributed-to-einstein/page/1/', '/page/7/', '/tag/alcohol/page/1/', '/tag/the-hunger-games/page/1/', '/author/J-R-R-Tolkien', '/tag/bilbo/page/1/', '/tag/journey/page/1/', '/tag/lost/page/1/', '/tag/quest/page/1/', '/tag/travel/page/1/', '/tag/wander/page/1/', '/tag/live-death-love/page/1/', '/tag/education/page/1/', '/tag/troubles/page/1/', '/page/8/', '/author/Ayn-Rand', '/page/9/', '/tag/mistakes/page/1/', '/tag/integrity/page/1/', '/tag/elizabeth-bennet/page/1/', '/tag/jane-austen/page/1/', '/tag/age/page/1/', '/tag/fairytales/page/1/', '/tag/growing-up/page/1/', '/tag/god/page/1/', '/page/10/', '/author/Harper-Lee', '/tag/better-life-empathy/page/1/']
    temp = []

    # check if words appear together
    print("Searching if words are together (may take some time)")
    for result in sorted_counts:
        if result[1][0]>= len(word_list):
            # get url
            url = urls_searched[result[0]] 
            time.sleep(0.1)
            response = requests.get(base_url+url)
            #correct response
            if response.status_code == 200:
                #parse page
                page_parse = BeautifulSoup(response.content,'html.parser')
                # Remove the <head> tag and its content
                head_tag = page_parse.find('head')
                if head_tag:
                    head_tag.decompose()
                text = page_parse.get_text()
                # get all words including apostrophes
                words_in_page = re.findall(r'\b(?:\w+(?:\'\w+)?)+\b', text.lower())
                # check if words appear together
            
            count_words = words_together(words_in_page, words)
            temp.append((result[0], (result[1][0], count_words)))
        else:
            temp.append(result)
    #print(temp)
    sorted_array = sorted(temp, key=lambda x: (x[1][0], x[1][1]),reverse=True)
    #print(sorted_array)
    print("Sorted by best result:")
    for index,count in sorted_array:
        print(base_url+urls_searched[index])
    return 

# Function to combine indexes of two results
def combine_indexes(string1,string2):
    array1 = string_to_array(string1)
    array2 = string_to_array(string2)
    combined_array = array1 + array2
    result_array = [item[1] for item in combined_array]
    return result_array

# Function to count indexes of an array of indexes
def count_indexes(indexes):
    #print(indexes)
    counts = {}
    # Count occurrences of each number and set together value as 0
    for number in indexes:
        if number in counts:
            counts[number] = (counts[number][0] + 1, 0)
        else:
            counts[number] = (1, 0)

    return counts
    
# Function to sort indexes by number of times it appears
def sort_by_occurrences(indexes):
    # store count of each number as a dictionary
    counts = {}
    for num in indexes:
        if num in counts:
            counts[num] += 1
        else:
            counts[num] = 1
    #sort by count
    sorted_indexes = sorted(counts.items(), key=lambda x: x[1], reverse=True)

    #for num, count in sorted_indexes:
        #print(num,"appears",count,"times")
    return sorted_indexes

# Function to see if words are together in a page
def words_together(words_in_page, words):
    count = 0
    sequence_length = len(words)
    for i in range(len(words_in_page) - sequence_length + 1):
        if words_in_page[i:i+sequence_length] == words:
            count += 1
    return count

if __name__ == "__main__":
    built = 0
    while True:
        command = input("Enter command: build, load, print, find, exit: ").lower()
        #command = "build"
        if command == 'build':
            if built>=1:
                print("Inverted Index already built.")
            else:
                urls.append("/")
                search_page()
                write_to_file()
                print("Index built and saved to inverted_index.txt")
                built+=1
            
        elif command == 'load':
            if built>=1:
                # load inverted index from file
                words = load_index()
                print("Index loaded ")
            else:
                print("First build with the command: build")
        elif command == 'print':
            if built>=1:
                word = input("Enter word to print index for: ")
                current_word,data = print_inverted_index(word)
                for pair in data:
                    print(current_word,"appears",pair[0],"time(s) in document with index",pair[1])  
            else:
                print("First build with the command: build")
        elif command == 'find':
            if built>=1:
                query = input("Enter search query: ")
                find_words(query)
            else:
                print("First build with the command: build")
        elif command == 'exit':
            break
        else:
            print("Invalid command. Please try again.")