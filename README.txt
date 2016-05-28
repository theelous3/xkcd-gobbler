# xkcd-gobbler

A python3 xkcd comic downloader.

Usage:
To download a range of comics, use the "r:" tag followed by hyphen seperated range "1-100"
    r: 1-100
To download multiple particular comics, use the "m:" tag followed by comma separated numbers "1,24,563"
    m: 1,24,563
To download an individual comic, use the "i:" tag followed by a comic number "1234"
    i: 1234

Advanced:
  You will be prompted to select how many coroutines you would like to run at once. 
  Leave blank if you are unsure.
  You may select any value above 1. The upper limit depends on your operating system.
  
Dependancies:
  BeautifulSoup4
  Requests
  eventlet

<Licence>
Do whatevs.
</Licence>
