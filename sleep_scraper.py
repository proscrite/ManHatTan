from time import sleep
import urllib.request
import re
import numpy as np

def find_prices_list(lines):
    parag = []
    for i,l in enumerate(lines):
        if 'item-price' in l:
            parag.append(l)

    prices = []
    for p in parag:
        for match in re.finditer('item-price h2-simulated">', p):
            val = p[match.end():match.end()+3]
            prices.append(int(val))
    prices = np.array(prices)
    return prices

def find_prices(lines, verbose = False):
    prices = []
    for match in re.finditer('item-price h2-simulated">', lines):
        val = lines[match.end():match.end()+5].replace('.', '')
        if verbose: print(val)
        try: int(val)
        except ValueError:
            val = lines[match.end():match.end()+3]
        prices.append(int(val))
    prices = np.array(prices)
    print(len(prices))
    return prices

def prices_in_url(pag : int, url : str):
    if pag == 0:
        pag = ''
    url = url + '/pagina-'+str(pag)+'.htm'

    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
           'Authority': 'www.idealista.com',
           'Method' : 'GET',
#            'Referer': 'https://www.idealista.com/alquiler-habitacion/valencia-valencia/con-precio-desde_250/pagina-14.htm',
           'Referer': 'https://www.idealista.com/alquiler-habitacion/valencia-valencia/mapa',
           'upgrade-insecure-requests': '1',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib.request.Request(url, headers=hdr)
    fp = urllib.request.urlopen(req)
    mybytes = fp.read()

    mystr = mybytes.decode("utf8")
    fp.close()
    return find_prices(mystr)

def loop_sleep_scraper(url: str, ofile: str, Npages: int = 25):

  p_array = []
  p_temp = []
  tslept = 30  # In minutes

  for i in range(1,Npages):
      try:
          p_temp.append(prices_in_url(pag=i, url=url))
          print('Scraped page ', i)
      except urllib.request.HTTPError as exception:
          print('Got exception ', exception)
          sleep(tslept * 60)
          print('Slept %i minutes, got HTTPError' %tslept)

  # Try same page (same iteration) after 30 minutes
          try:
              p_temp.append(prices_in_url(pag=i, url=url))
              print('Scraped page ', i)

          except urllib.request.HTTPError as exception:
              print('Got exception ', exception)
    # If this sleep time is not enought, report it and increase it by 10 mins

              tslept += 10
              sleep(tslept * 60)
              print('Slept %i minutes on second try, got HTTPError' %tslept)
      p_array.append(np.array(p_temp).flatten()) # Store temporal array

      with open(ofile,'a') as fin: # Flush
          np.savetxt(fin, p_temp, fmt='%.2f')

if __name__ == '__main__':
    ofile = '2rooms_antiguo_flush.txt'
    url = "https://www.idealista.com/alquiler-viviendas/donostia-san-sebastian/antiguo/con-publicado_ultimo-mes/"
    loop_sleep_scraper(url, ofile)
