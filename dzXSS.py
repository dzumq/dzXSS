import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlparse, urljoin, parse_qs, urlencode
from termcolor import colored
import glob

TOOL_NAME = "dzXSS"
TOOL_VERSION = "1.0"
PAYLOADS_DIR = "payloads"

def clear_terminal():
   os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
   banner = """
 ██████╗ ███████╗██╗  ██╗███████╗███████╗
 ██╔══██╗╚══███╔╝╚██╗██╔╝██╔════╝██╔════╝
 ██║  ██║  ███╔╝  ╚███╔╝ ███████╗███████╗
 ██║  ██║ ███╔╝   ██╔██╗ ╚════██║╚════██║
 ██████╔╝███████╗██╔╝ ██╗███████║███████║
 ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝
    """
   print(colored(banner, 'red', attrs=['bold']))
   print(colored("created by dzuma youtube.com/@dzumq".center(80), 'red'))




#payload n files stuff#
def pick_payload( ):
   if not os.path.exists( PAYLOADS_DIR ):
      os.makedirs(PAYLOADS_DIR)
      print(colored(f"[+] Created '{PAYLOADS_DIR}/' folder in tool root.", 'cyan'))
      print(colored("    Put your .txt payload files there and rerun!", 'yellow'))
      input("    Press Enter to exit...")
      sys.exit(0)
   
   payload_files = sorted( glob.glob(f"{PAYLOADS_DIR}/*.txt") )
   
   if not payload_files:
      print(colored(f"[!] No .txt files found in '{PAYLOADS_DIR}/'", 'red'))
      print(colored("    Add your payload lists (one payload per line or else script doesnt work) and try again.", 'yellow'))
      sys.exit(1)
   
   print(colored("\nAvailable payload lists:", 'cyan'))
   for i, file in enumerate(payload_files, 1):
      print(colored(f"  [{i}] {os.path.basename(file)}", 'white'))
   
   while True:
      try:
         choice = input(colored("\nSelect payload file > ", 'blue')).strip()
         if not choice.isdigit():
            raise ValueError
         choice = int(choice)
         if 1 <= choice <= len(payload_files):
            selected = payload_files[choice - 1]
            with open(selected, 'r', encoding='utf-8') as f:
               payloads = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(colored(f"[+] Loaded {len(payloads)} payloads → {os.path.basename(selected)}", 'green'))
            return payloads
      except:
         print(colored("Invalid input. Enter a number.", 'red'))

#might be useless and just slow down the program with minimal evasion, consider nuking this block after further testing
def   evade ( p ):
   return [
      p,
      p.replace("script", "scr"+"ipt"),
      p.replace("alert", "prompt"),
      p.replace("<", "%3C").replace(">", "%3E"),
   ]  

def  sendk ( driver , element , text ):
   try:
      driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
      WebDriverWait(driver, 2).until(EC.element_to_be_clickable(element))  # still possible to reduce timeout dont mess with it tho
      element.clear()
      element.send_keys(text)
      return True
   except:
      try:
         driver.execute_script("arguments[0].value = arguments[1];", element, text)
         driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", element)
         driver.execute_script("arguments[0].dispatchEvent(new Event('change', { bubbles: true }));", element)
         return True
      except:
         return False

def   tf ( driver ,  form ,payloads ) :
   vuln_count = 0;
   driver.get(form['url'])
   time.sleep(0.2)  # DONT DECREASE ANYMORE IT BREAKS

   for payload in payloads:
      for ev in evade(payload):
         try:
            filled = False
            for name, _ in form['inputs']:
               try:
                  elem = WebDriverWait(driver, 3).until(  
                     EC.presence_of_element_located((By.NAME, name))
                  )
                  if sendk(driver, elem, ev):
                     filled = True
               except:
                  continue

            if not filled:
               continue

            try:
               submit = WebDriverWait(driver, 2).until(  
                  EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type=submit], button[type=submit], button, [type=submit]"))
               )
               sendk(driver, submit, "")
               submit.click()
            except:
               try:
                  driver.execute_script("document.querySelector('form').submit();")
               except:
                  continue

            time.sleep(0.2)  # DONT DECREASE ANYMORE IT BREAKS
            is_vuln = False
            try:
               WebDriverWait(driver, 1).until(EC.alert_is_present())  
               alert = driver.switch_to.alert
               full_context = driver.current_url
               print(colored(f"VULNERABLE --> {full_context} (with payload: {ev})", 'green'))
               alert.accept()
               vuln_count += 1
               is_vuln = True
            except:
               full_context = driver.current_url
               print(colored(f"NOT VULNERABLE --> {full_context} (with payload: {ev})", 'red'))
##### FIX BELOW PART LATER #####
            driver.get(form['url'])
            time.sleep(0.2)  # DONT DECREASE ANYMORE IT BREAKS
            try:
               WebDriverWait(driver, 1).until(EC.alert_is_present())  
               alert = driver.switch_to.alert
               print(colored(f"VULNERABLE --> {form['url']} (stored with payload: {ev})", 'green'))
               alert.accept()
               vuln_count += 1
            except:
               if not is_vuln:  # should only print if is_vuln isnt met
                  print(colored(f"NOT VULNERABLE --> {form['url']} (stored with payload: {ev})", 'red'))

         except Exception as e:
            pass  

   return vuln_count



def tu ( driver , url,  payloads ):
   vuln_count = 0
   parsed = urlparse(url)
   if not parsed.query:
      return 0


###change crappy tutorial values
   params = parse_qs(parsed.query)
   for param in params:
      for payload in payloads:
         for ev in evade(payload):
            new_params = {k: ev if k == param else v[0] for k, v in params.items()}
            new_query = urlencode(new_params, doseq=True)
            test_url = parsed._replace(query=new_query).geturl()
            try:
               driver.get(test_url)
               time.sleep(0.2)  # DONT DECREASE ANYMORE IT BREAKS

               try:
                  WebDriverWait(driver, 1).until(EC.alert_is_present())  
                  alert = driver.switch_to.alert
                  print(colored(f"VULNERABLE --> {test_url}", 'green'))
                  alert.accept()
                  vuln_count += 1
               except:
                  print(colored(f"NOT VULNERABLE --> {test_url}", 'red'))
            except Exception as e:
               pass
   return vuln_count



def  tl( driver , url ,  payloads ):
   vuln_count = 0
   driver.get(url)
   time.sleep(0.2)  # DONT DECREASE ANYMORE IT BREAKS

   inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="search"], input[type="url"], input[type="email"], textarea')

   if not inputs:
      print(colored("[!] No loose inputs found.", 'yellow'))
      return 0

   print(colored(f"[+] Found {len(inputs)} loose inputs to test", 'green'))

   for inp in inputs:
      if (not inp.is_displayed()) or (not inp.is_enabled()):
         continue

      for payload in payloads:
         for ev in evade(payload):
            try:
               if sendk(driver, inp, ev):
                  try:
                     inp.send_keys(Keys.ENTER)
                  except:
                     try:
                        submit = inp.find_element(By.XPATH, "..//button | ..//input[@type='submit']")
                        submit.click()
                     except:
                        continue

                  time.sleep(0.2)  # DONT DECREASE ANYMORE IT BREAKS

                  is_vuln = False
                  try:
                     WebDriverWait(driver, 1).until(EC.alert_is_present())  
                     alert = driver.switch_to.alert
                     full_context = driver.current_url
                     print(colored(f"VULNERABLE --> {full_context} (with payload: {ev})", 'green'))
                     alert.accept()
                     vuln_count += 1
                     is_vuln = True
                  except:
                     full_context = driver.current_url
                     print(colored(f"NOT VULNERABLE --> {full_context} (with payload: {ev})", 'red'))

                  driver.get(url)
                  time.sleep(0.2)  # DONT DECREASE ANYMORE IT BREAKS

            except Exception as e:
               pass

   return vuln_count



def crawl( domain , payloads ):
   start_time = time.time()
   vuln_count = 0
   print(colored(f"\nStarting scan on: {domain}", 'cyan', attrs=['bold']))





# basic selenium stuff, change if chrome acts up
   options = Options( )
   options.add_argument('--headless=new')
   #next 2 fixed some issues with chrome not startin gup so leave them in
   options.add_argument('--no-sandbox')
   options.add_argument('--disable-dev-shm-usage')
   options.add_argument('--disable-gpu') #honestly not sure why this but i think i need it
   options.add_argument('--window-size=1920,1080') #consider chning resolution
   #forgot why this part is here cant find the stack post anymre lol
   options.add_experimental_option("excludeSwitches", ["enable-logging"]) # stops chrome being annoying about logs
   options.add_argument('--disable-blink-features=AutomationControlled')
   options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36') 
   #probs a good portion of the above isnt needed but dont touch because something might break

   driver = webdriver.Chrome(
      service = Service(ChromeDriverManager().install()) ,
      options = options
   )


   forms = [ ]
   param_urls = []
   visited = set()
   queue = [domain]
   max_pages = 10  # lowering increases speed but results might suffer. increase if u want more injection points
   pages_crawled = 0

   while queue and pages_crawled < max_pages:
      url = queue.pop(0)
      if url in visited: 
         continue
      visited.add(url)
      print(colored(f"[+] Crawling: {url}", 'cyan'))
      pages_crawled += 1

      try:
         driver.get(url)
         WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))  
         time.sleep(0.2)  # DONT DECREASE ANYMORE ITLL GLITCH OUT

         soup = BeautifulSoup(driver.page_source, 'html.parser')

         for form in soup.find_all('form'):
            action = urljoin(url, form.get('action') or url)
            method = form.get('method', 'get').lower()
            inputs = []
            for inp in soup.find_all(['input', 'textarea', 'select']):
               name = inp.get('name') or inp.get('id')
               if name:
                  inputs.append((name, inp.get('type', 'text')))
            if inputs:
               forms.append({'url': url, 'action': action, 'method': method, 'inputs': inputs})

         current_url = driver.current_url
         if '?' in current_url:
            param_urls.append(current_url)

         for a in soup.find_all('a', href=True):
            link = urljoin(url, a['href'])
            parsed_link = urlparse(link)
            if parsed_link.netloc == urlparse(domain).netloc and link not in visited and '?' in link:
               queue.append(link)

      except Exception as e:
         print(colored(f"[!] Crawl error at {url}: {str(e)[:100]}", 'red'))

   forms = list({f['url']: f for f in forms}.values())
   param_urls = list(set(param_urls))

   if forms:
      print(colored(f"[+] Found {len(forms)} forms", 'green'))
      for form in forms:
         vuln_count += tf(driver, form, payloads)

   if param_urls:
      print(colored(f"[+] Found {len(param_urls)} param URLs", 'green'))
      for p_url in param_urls:
         vuln_count += tu(driver, p_url, payloads)

   if not forms and not param_urls:
      print(colored("[!] No forms/params found. Testing loose inputs...", 'yellow'))
      vuln_count += tl(driver, domain, payloads)

   driver.quit()

   time_taken = time.time() - start_time
   print("\n" + "="*60)
   if vuln_count > 0:
      print(colored("TARGET IS VULNERABLE TO XSS!".center(60), 'green', attrs=['bold', 'blink']))
   else:
      print(colored("No XSS vulnerability found. keep trying :)".center(60), 'red', attrs=['bold']))
   print(colored(f"Scan completed in {time_taken:.2f} seconds. Vulnerabilities found: {vuln_count}", 'cyan'))
   print("="*60)

def main( ):
   clear_terminal()
   print_banner() #center it later

   print(colored("1. Single Domain", 'white'))
   print(colored("2. Multiple Domains (from file)", 'white'))
   mode = input(colored("\nChoose mode > ", 'blue')).strip()

   payloads = pick_payload()

   if mode == "1":
      url = input(colored("\nTarget URL > ", 'blue')).strip()
      if not url.startswith(("http://", "https://")):
         url = "https://" + url
      crawl(url, payloads)

   elif mode == "2":
      path = input(colored("\nPath to domains.txt > ", 'blue')).strip()
      try:
         with open(path) as f:
            domains = [line.strip() for line in f if line.strip() and not line.startswith('#')]
         for domain in domains:
            if not domain.startswith(("http://", "https://")):
               domain = "https://" + domain
            crawl(domain, payloads)
            time.sleep(1) 
      except FileNotFoundError:
         print(colored("File not found!", 'red'))
   else:
      print(colored("Invalid option.", 'red'))

if __name__ == "__main__":
   try:
      requests.packages.urllib3.disable_warnings()
      main()
   except KeyboardInterrupt:
      print(colored("\n[!] Scan aborted.", 'red'))



####DONT FORGET TO FIX SPEEDS AND WEBDRIVER ERROR####
#ADD PRINTS FOR ERRORS SO SCRIPT DOESNT bug OUt#
#dont forget selenium needs time to load so don't make time.sleep(s) too fast
###CENTER ASCII THING WHEN DONE###
##DELETE THESE  COMMENTS dont forget##
