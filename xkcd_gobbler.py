import sys
import os
import re
import eventlet
eventlet.monkey_patch()
from bs4 import BeautifulSoup

import requests


class Scraper:

    def __init__(self):
        self.success = 0
        self.failure = 0
        self.skipped = 0
        self.failed_list = []
        self.skipped_list = []
        self.tracebacks = []

    def process_director(self, url_list, threads=50):
    #   points this way and that, until the work is done
        pool = eventlet.GreenPool(threads)
        for comic_url in pool.imap(self.worker, url_list):
            pass
        print()
    
    def worker(self, comic_url):
    #   worker function that runs in coroutines to get image url from comic page
    #   pre-existing files, exceptions and sucesses increment stats
        r = requests.get(comic_url)
        rc = r.content
        soup = BeautifulSoup(rc, 'html.parser')
    
        try:
            img_url = soup.find('div', {'id':'comic'}).img['src']
        except AttributeError:
            self.skipped_list.append(img_url)
            self.skipped += 1
        else:
            image = requests.get('http:' + img_url, stream=True)
            filepath = os.path.join('Comics', img_url.split('/')[4])
            if os.path.isfile(filepath):
                self.skipped_list.append(img_url)
                self.skipped += 1
            else:
                try:
                    with open(filepath, 'wb') as image_file:
                        for bytechunk in image.iter_content():
                            image_file.write(bytechunk)
                    self.success += 1
                except:
                    self.tracebacks.append(traceback.print_exc())
                    self.failed_list.append(img_url)
                    self.failure += 1
        self.terminal_knowledge()

    def terminal_knowledge(self):
    #   provides constant feedback on fetch status.
        print('\r Sucessful:{} Failed:{} Skipped:{}'.format(self.success,
                                                            self.failure, 
                                                            self.skipped), 
                                                                flush=True,
                                                                end ='')

    def logger(self):
    #   logz
        with open('xkcd_log.txt', 'w') as logfile:
            logfile.write('Skipped: \n')
            for url in self.skipped_list:
                logfile.write(url + '\n')
            logfile.write('Failed: \n')
            for url in self.failed_list:
                logfile.write(url + '\n')
            logfile.write('Traceback(s): \n')
            for trace in self.tracebacks:
                logfile.write(trace + '\n')
    
    def get_comic_count(self):
    #   gets total number of comics from xkcd homepage.
    #   builds and returns list of all xkcd urls.
        r = requests.get('http://xkcd.com/')
        rc = r.content
        soup = BeautifulSoup(rc, "html.parser")
        num_finder = re.compile('Permanent link to this comic: http://xkcd.com/')
        get_num = soup.find(text=num_finder)
        last_comic = get_num.split('/')[3]
        url_list = [('http://xkcd.com/' + str(i)) for i in range(1, int(last_comic)+1)]
        return (last_comic, url_list)
    
    def main(self):
    #   gets a list of urls and the latest comic number from get_comic_content().
    #   gets user input from user, and configures the url_list to match the user's prefs.
    #   calls process_director() to begin comic fetching.
    #   if there are skipped/failed fetches/saves, give option to log.
        latest_data = self.get_comic_count()
        last_comic, url_list = latest_data
        
        print('Examples:')
        print('  Range-      "r: 50-100"')
        print('  Multi-      "m: 41,154,1002"')
        print('  Individual- "i: {}"\n'.format(last_comic))

        usr_range = input('Which of the {} comic(s) would you like to download?\n'.format(last_comic))
        
        print()

        choice_type, choice_value = usr_range.split(':')
        if choice_type.lower() == 'r':
            choice_value = choice_value.split('-')
            url_list = url_list[int(choice_value[0])-1:int(choice_value[1])]
        elif choice_type.lower() == 'm':
            choice_value = choice_value.split(',')
            url_list = [url_list[int(n)-1] for n in choice_value]
        elif choice_type.lower() == 'i':
            url_list = [url_list[int(choice_value)-1]]

        print('Checking/Creating "Comics" directory...')
        os.makedirs('Comics', exist_ok=True)

        try:
            usr_concur = int(input("How many downloads would you like concurrently? (Max: 255)\n"))
            print('Using {} coroutine(s)'.format(str(usr_concur)))
            print('Fetching comics...')
            self.process_director(url_list, usr_concur)
        except ValueError:
            print('Using default coroutines.')
            print('Fetching comics...')
            self.process_director(url_list)

        print()
        print('Fetch Complete...')

        if self.failed_list or self.skipped_list:
            log_input = input('There were skipped/failed attempts. Would you like a log? Y/N \n')
            if 'y' in log_input.lower():
                self.logger()
            else:
                pass
        print('Exiting...')


if __name__ == "__main__":
    s = Scraper()
    s.main()
    
