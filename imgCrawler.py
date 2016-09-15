from bs4 import BeautifulSoup
import requests, argparse, os, threading

DIR = "./img"

def arguments():
    ''' command-line options parser
    imgCrawler topicID -p pageNum1 [pageNum2...] -> separate pages
    imgCrawler topicID -r pageNum1 pageNum2 -> pages range
    '''
    parser = argparse.ArgumentParser(description="Download imgs from a specific topic of voz")
    parser.add_argument("topicID", help="id of topic", type=int)
    group = parser.add_mutually_exclusive_group() # separate or range
    group.add_argument("--pages", "-p", metavar="page", help="list of pages", type=int, nargs="+")
    group.add_argument("--range", "-r", metavar=("start", "end"), help="range of pages", type=int, nargs=2)

    args = parser.parse_args()
    return args


def downloadImage(url):
    '''download an image from the url, save to DIR'''
    print("Downloading image from %s" % url)
    try:
        res = requests.get(url)
        res.raise_for_status()
        imgName = os.path.basename(url) # get the 'abc.jpg' in the url
        imgDes = os.path.join(DIR, imgName) # /abc.jpg for OS X and \\abc.jpg for Windows
        imgFile = open(imgDes, "wb") # write binary mode
        for chunk in res.iter_content(100000):
            imgFile.write(chunk)
        imgFile.close()
        print("Image downloaded")
    except Exception as exc:
        print("Couldn't download img: %s" % exc)


def downloadPage(topicID, pageID):
    '''download all images from one page'''
    res = requests.get("https://vozforums.com/showthread.php?t={}&page={}".format(topicID, pageID))
    soup = BeautifulSoup(res.text, "html.parser")
    imgs = soup.select(".voz-post-message img")
    srcs = set([img.get("src") for img in imgs])
    for src in srcs:
        if src.startswith("http"):
            downloadImage(src)


def download(args):
    '''download all images from all pages'''
    topicID = args.topicID
    pages = list(set(args.pages)) if args.pages else range(args.range[0], args.range[1]+1)
    for pageID in pages:
        downloadPage(topicID, pageID)


def downloadMultiThreads(args):
    '''MULTI THREAD IMPLEMENTATION'''
    topicID = args.topicID
    pages = list(set(args.pages)) if args.pages else range(args.range[0], args.range[1]+1)
    #downloadThreads = [] # list of Thread objects
    for pageID in pages:
        # each thread download one page concurrently
        downloadThread = threading.Thread(target=downloadPage, args=(topicID, pageID))
    #   downloadThreads.append(downloadThread)
        downloadThread.start()
    # wait for all threads to finish before execute codes after this function
    #for thread in downloadThreads:
    #   thread.join() # wait until finish

def main():
    if not os.path.exists(DIR):
        os.makedirs(DIR)
    #import time
    #start = time.time()
    #download(parser()) # 12301 -r 540 543 -> 47.776850938797
    downloadMultiThreads(arguments()) # 12301 -r 540 543 -> 11.147968053817749
    #elapsed = time.time()
    #print("Time spent: %s" % (elapsed-start))

if __name__ == "__main__":
    main()
