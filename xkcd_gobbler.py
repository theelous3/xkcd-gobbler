import sys
import os
import eventlet
eventlet.monkey_patch()
from bs4 import BeautifulSoup

import requests
import re


class Scraper:

    def __init__(self):
        self.success = 0
        self.failure = 0
        self.skipped = 0

    def process_director(self, threads, url_list):
        pool = eventlet.GreenPool(threads)
        for comic_url in pool.imap(self.worker, url_list):
            pass
        print()
    
    
    def worker(self, comic_url):
        r = requests.get(comic_url)
        rc = r.content
        soup = BeautifulSoup(rc, "html.parser")
    
        try:
            img_url = soup.find('div', {'id':'comic'}).img['src']
            if not os.path.isfile('Comics/'+img_url.split('/')[4]):
                if self.save_image(img_url):
                    self.success += 1
                else:
                    self.failure += 1
            else:
                self.skipped += 1
        except AttributeError:
            self.skipped += 1
        self.terminal_knowledge()

    def save_image(self, url):
        image = requests.get('http:' + url, stream=True)

        try:
            with open('Comics/'+url.split('/')[4], 'wb') as image_file:
                for bytechunk in image.iter_content():
                    image_file.write(bytechunk)
            return True
        except Exception:
            return False

    
    
    def terminal_knowledge(self):
        sys.stdout.write('\r Sucessful:{} Failed:{} Skipped:{}'.format(self.success, self.failure, self.skipped))
        sys.stdout.flush()
    
    
    def get_comic_count(self):
        r = requests.get('http://xkcd.com/')
        rc = r.content
        soup = BeautifulSoup(rc, "html.parser")
        num_finder = re.compile('Permanent link to this comic: http://xkcd.com/')
        get_num = soup.find(text=num_finder)
        latest_comic_num = get_num.split('/')[3]
        url_list = [('http://xkcd.com/' + str(i) + '/') for i in range(1, int(latest_comic_num)+1)]
        return (latest_comic_num, url_list)
    
    
    def main(self):
        latest_data = self.get_comic_count()
        comics_available, url_list = latest_data[0], latest_data[1]
        
        print('Examples:')
        print('  Range-      "r: 50-100"')
        print('  Multi-      "m: 41,154,1002"')
        print('  Individual- "i: {}"\n'.format(comics_available))
        user_requested_range = input('Which of the {} comic(s) would you like to download?'.format(comics_available))
        print()
        u_r_concur = int(input("How many downloads would you like concurrently? (Max: 255)\n"))
        print()
        print('Checking/Creating "Comics" directory...')

        os.makedirs('Comics', exist_ok=True)

        choice_type, choice_value = user_requested_range.split(':')
        if choice_type.lower() == 'r':
            choice_value = choice_value.split('-')
            url_list = url_list[int(choice_value[0])-1:int(choice_value[1])]
        elif choice_type.lower() == 'm':
            choice_value = choice_value.split(',')
            url_list = [url_list[int(n)-1] for n in choice_value]
        elif choice_type.lower() == 'i':
            url_list = [url_list[int(choice_value)-1]]
            print(url_list)

        print('Fetching comics...')
        
        self.process_director(u_r_concur, url_list)




if __name__ == "__main__":
    s = Scraper()
    s.main()
    
