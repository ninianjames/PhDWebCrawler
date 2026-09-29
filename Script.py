import requests
from bs4 import BeautifulSoup as beautifulsoup
import colorama
from urllib.parse import urlparse, urljoin
import networkx as nx
import matplotlib.pyplot as plt
import random
import time
import io

total_urls_crawled = 0

internal_urls = []


def create_list_from_file(listfile):
 return [line.strip() for line in io.open(f"{listfile}.txt", 'r', encoding="utf-8")]


def netloc_only(url):
 url = urlparse(url).netloc
 url = url.replace('http://', '')
 url = url.replace('https://', '')
 url = url.replace('www.', '')
 url = url.replace('boards.', '')
 return url


graph = nx.DiGraph()

lists = {
 "found_nocrawl_socmeds": [],
 "found_search_these_socmeds": [],
 "found_msms": [],
 "found_altms": [],
 "found_commsites": [],
 "found_pastebins": [],
 "found_genericblocklists": [],
 "urls_to_crawl": set(),
 "urls_to_document": [],
 "found_dead_websites": set()
}

colours = {"GREEN": colorama.Fore.GREEN,
   "CYAN": colorama.Fore.CYAN,
   "YELLOW": colorama.Fore.YELLOW,
   "RED": colorama.Fore.RED,
   "MAGENTA": colorama.Fore.MAGENTA,
   "BLUE": colorama.Fore.BLUE,
   "WHITE": colorama.Fore.WHITE,
   "BLACK": colorama.Fore.BLACK,
   "AZURE": colorama.Fore.LIGHTBLUE_EX,
   "LIGHTGREEN": colorama.Fore.LIGHTGREEN_EX,
   "GREY": colorama.Fore.LIGHTBLACK_EX,
   "PINK": colorama.Fore.LIGHTMAGENTA_EX,
   "RESET": colorama.Fore.RESET}


def is_valid(href):
 parsed = urlparse(href)
 return bool(parsed.netloc) and bool(parsed.scheme)


def get_hyperlinks(url):
 hyperlinks = []
 soup = beautifulsoup(requests.get(url).content, "html.parser")
 for a_tag in soup.find_all("a"):
  hyperlink = a_tag.attrs.get("href")
  if hyperlink == "" or hyperlink is None:
   continue
  if not is_valid(hyperlink):
   # if it's not a working hyperlink
   continue
  hyperlink = urljoin(url, hyperlink)
  hyperlinks.append(hyperlink)
  if not bool(hyperlinks):
   print(f"{colours['PINK']}There are no links here")

 return hyperlinks


def filter_hyperlinks(url):
 links = get_hyperlinks(url)

 nocrawl_socmed_list = create_list_from_file("socmed_list")
 search_these_socmeds = create_list_from_file("search_these_socmeds")
 altm_list = create_list_from_file("altm_list")
 genericblock_list = create_list_from_file("genericblocklist")
 linkbin_list = create_list_from_file("linkbin_list")
 msm_list = create_list_from_file("msm_list")
 commsites_list = create_list_from_file("commsites_list")
 known_dead_websites = create_list_from_file("known_dead_sites")

 for link in links:
  # hyperlink_no_query = urlparse(link).scheme + "://" + urlparse(link).netloc + urlparse(link).path
  hyperlink = urlparse(link).scheme + "://" + urlparse(link).netloc
  current_domain_name = urlparse(url).scheme + "://" + urlparse(url).netloc
  # hyperlink_no_scheme = urlparse(link).netloc
  # domain_no_scheme = urlparse(url).netloc
  if "mp4" in link:
   lists["urls_to_document"].append(link)
   continue
  if "mp3" in link:
   lists["urls_to_document"].append(link)
   continue
  if ".jpg" in link:
   lists["urls_to_document"].append(link)
   continue
  if "m4a" in link:
   lists["urls_to_document"].append(link)
   continue
  if "files" in link:
   lists["urls_to_document"].append(link)
   continue
  if "download" in link:
   lists["urls_to_document"].append(link)
  if "stream" in link:
   lists["urls_to_document"].append(link)
   continue
  if ".edu" in link:
   lists["urls_to_document"].append(link)
   continue
  if "pdf" in link:
   lists["urls_to_document"].append(link)
   continue
  if ".mil" in link:
   lists["urls_to_document"].append(link)
   continue
  if hyperlink in known_dead_websites:
   print(f"{colours['AZURE']}[!] Broken website: {link}{colours['RESET']}")
   lists['urls_to_document'].append(link)
   lists['found_dead_websites'].add(link)
   continue
  if current_domain_name in hyperlink and link not in internal_urls:
   # internal hyperlink, not interested
   print(f"{colours['MAGENTA']}[!] Internal link: {link}{colours['RESET']}")
   internal_urls.append(link)
   continue
  if link in lists['urls_to_crawl']: # it's a set now so this is irrelevant
   # already found it
   continue
  if hyperlink in nocrawl_socmed_list and link not in lists['found_nocrawl_socmeds']:
   print(f"{colours['WHITE']}[!] Blocklist social media link: {link}{colours['RESET']}")
   lists['found_nocrawl_socmeds'].append(link)
   lists["urls_to_document"].append(link)
   graph.add_edge(url, link)
   continue
  if hyperlink in search_these_socmeds and link not in lists['found_search_these_socmeds']:
   print(f"{colours['GREY']}[!] Crawlable social media link: {link}{colours['RESET']}")
   lists['found_search_these_socmeds'].append(link)
   lists['urls_to_crawl'].add(link)
   lists["urls_to_document"].append(link)
   graph.add_edge(url, link)
  if hyperlink in altm_list and link not in lists['found_altms']:
   print(f"{colours['RED']}[!] Alternative media link: {link}{colours['RESET']}")
   lists['found_altms'].append(link)
   lists["urls_to_document"].append(link)
   graph.add_edge(url, link)
   continue
  if hyperlink in genericblock_list and link not in lists['found_genericblocklists']:
   print(f"{colours['BLACK']}[!] Generic blocklist link: {link}{colours['RESET']}")
   lists['found_genericblocklists'].append(link)
   lists["urls_to_document"].append(link)
   graph.add_edge(url, link)
   continue
  if hyperlink in linkbin_list and link not in lists['found_pastebins']:
   print(f"{colours['MAGENTA']}[!] Pastebin link: {link}{colours['RESET']}")
   lists['found_pastebins'].append(link)
   lists["urls_to_document"].append(link)
   graph.add_edge(url, link)
   continue
  if hyperlink in msm_list and link not in lists['found_msms']:
   print(f"{colours['BLUE']}[!] Mainstream media link: {link}{colours['RESET']}")
   lists['found_msms'].append(link)
   lists["urls_to_document"].append(link)
   graph.add_edge(url, link)
   continue
  if hyperlink in commsites_list and link not in lists['found_commsites']:
   lists['found_commsites'].append(link)
   lists["urls_to_document"].append(link)
   graph.add_edge(url, link)
   print(f"{colours['GREEN']}[!] Commercial link: {link}{colours['RESET']}")
   continue
  if netloc_only(url) not in netloc_only(link) and link not in lists['urls_to_document']:
   # external hyperlink that does not belong to any lists
   # if link not in lists['urls_to_document']:
   lists['urls_to_crawl'].add(link)
   lists["urls_to_document"].append(link)
   graph.add_edge(url, link)
   print(f"{colours['CYAN']}[!] External link: {link}{colours['RESET']}")

 return lists["urls_to_crawl"]


def breadth_first_search(start_url, depth):
 global total_urls_crawled
 if depth == 0:
  # does nothing, prints the url
  print(start_url)
 if depth == 1:
  # this is level 1. external hyperlinks i want to crawl found on one url
  filter_hyperlinks(start_url)
 else:
  queue = []
  for level in range(depth):
   if level == 1:
    print(f"First Crawl (level {level}) {colours['LIGHTGREEN']}[*] Crawling: {start_url}{colours['RESET']}")
    total_urls_crawled += 1
    filter_hyperlinks(start_url)
    for url_to_crawl in lists['urls_to_crawl']:
     if url_to_crawl not in queue:
      queue.append(url_to_crawl)
   elif level > 1:
    print(f"There are {len(queue)} URLs in the queue to crawl")
    for count in range(len(queue)):
     time.sleep(random.randint(1, 10))

     url = queue.pop(0)
     print(f"Depth Crawl level {level} {colours['LIGHTGREEN']}[*] Crawling: {url}{colours['RESET']}")
     total_urls_crawled += 1

     urls = filter_hyperlinks(url)
     for url in urls:
      if url not in queue:
       queue.append(url)


def save(folder_name, filename):
 for key, value in lists.items():
  if value:
   list_name = key
   save_location = f"/home/nin/Documents/DataCollection/{folder_name}/{filename}_{list_name}.txt"
   with open(save_location, 'w') as f:
    for item in value:
     print(item.strip(), file=f)
 nx.write_edgelist(graph, f"/home/nin/Documents/DataCollection/{folder_name}/{filename}_edgelist.txt")


def show_graph():
 nx.draw(graph, with_labels=True)
 plt.show()


def print_descriptives():
 total_social_media_links = len(lists["found_nocrawl_socmeds"]) + len(lists["found_search_these_socmeds"])
 print("[+] Total external links:", len(lists['urls_to_document']))
 print("[+] Total social media links:", total_social_media_links)
 print("[+] Total mainstream media links:", len(lists['found_msms']))
 print("[+] Total alt media links:", len(lists['found_altms']))
 print("[+] Total pastebin links:", len(lists['found_pastebins']))
 print("[+] Total commercial links:", len(lists['found_commsites']))
 print("[+] Total generic blocklist links:", len(lists['found_genericblocklists']))
 print("[+] Total crawled URLs:", total_urls_crawled)


if __name__ == "__main__":
 website = "[website]"
 file = urlparse(website).netloc
 folder = "[folder]"
 try:
  breadth_first_search(website, 4)
  save(folder, file)
  show_graph()
  print_descriptives()
 except KeyboardInterrupt:
  save(folder, file)
  show_graph()
  print_descriptives()
 
