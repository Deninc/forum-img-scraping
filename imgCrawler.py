from bs4 import BeautifulSoup
import requests, argparse, os, threading

DIR = "./img"

class VozCrawler():
    ''' Crawling a topic in vozforums '''
    def __init__(self, topicID, pages, dest):
        self.topicID = topicID
        self.pages = set(pages)
        self.dest = dest

    def download(self):
        '''Multi-thread download'''
        if not os.path.exists(self.dest):
            os.makedirs(self.dest)

        downloadThreads = []
        for pageID in self.pages:
            # each thread download one page concurrently
            downloadThread = threading.Thread(target=self._downloadPage, args=(pageID,))
            downloadThreads.append(downloadThread)
            downloadThread.start()

        # wait for all threads to finish
        for thread in downloadThreads:
            thread.join()
        print("All threads finished")

    def _downloadPage(self, pageID):
        '''download all user posted images in page
            form: ../showthread.php?t=topicID&page=pageID
        '''
        res = requests.get("https://vozforums.com/showthread.php?t={}&page={}".format(self.topicID, pageID))
        soup = BeautifulSoup(res.text, "html.parser")
        imgs = soup.select(".voz-post-message img")
        srcs = set([img.get("src") for img in imgs])
        for src in srcs:
            if src.startswith("http"):
                self.downloadImage(src, self.dest)

    @staticmethod
    def downloadImage(url, dest):
        '''download an image from the url, save to dir'''
        print("Downloading image from %s" % url)
        try:
            res = requests.get(url)
            res.raise_for_status()
            # ../abc.jpg?x=123 -> get the 'abc.jpg' name
            # could've used regex here
            imgName = url.split('/')[-1].split('?')[0]
            imgDes = os.path.join(dest, imgName) # /abc.jpg for OS X and \\abc.jpg for Windows
            imgFile = open(imgDes, "wb")
            for chunk in res.iter_content(100000):
                imgFile.write(chunk)
            imgFile.close()
        except Exception as exc:
            print("Couldn't download img: %s" % exc)


def getArguments():
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
    pages = list(set(args.pages)) if args.pages else range(args.range[0], args.range[1]+1)

    return args.topicID, pages

def main():
    topic, pages = getArguments()
    c = VozCrawler(topic, pages, DIR)
    c.download()

if __name__ == "__main__":
    main()
