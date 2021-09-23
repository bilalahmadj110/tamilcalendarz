from selenium import webdriver
from constants import *
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from sqlalchemy import create_engine
import logging
import time
import pandas as pd
import numpy as np
from calendar import monthrange
import os


logging.basicConfig()

# ======================================================== DATABASE CREDENTIAL =======================================================
print (f'Connecting MySQL at `{SERVER_HOST}` with username: `{USERNAME}` AND database: `{DATABASE}` ...')
engine =  create_engine(F'mysql+pymysql://{USERNAME}:{PASSWORD}@{SERVER_HOST}/{DATABASE}')
# ====================================================================================================================================


class TamilCalendar:
    log = True
    to_sql = True
    
    def __init__(self, year_list=range(2011, 2021)):
        # init variable
        self.year_list = year_list
        # init logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        # init chrome
        chrome_options = Options()
        self.driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
        # self.driver.set_window_size(1900, 1000)
        
    def main_page(self):
        self.logger.debug(f"Loading '{MAIN_URL}'")
        self.driver.get(MAIN_URL)
        
        for year in self.year_list:
            self.__scrape_year(year)
        
    def __scrape_year(self, year):
        self.logger.debug(f"Starting scrapping year '{year}'")
        wait = WebDriverWait(self.driver, 10)
    
        # setting year field
        wait.until(EC.presence_of_element_located((By.XPATH, YEAR_FIELD))).send_keys(str(year))
        select = Select(self.driver.find_element_by_xpath(MONTH_DROPDOWN))
        
        for month in range(12):
            # choosing month field
            select.select_by_value(str(month))
            # submitting fields
            self.driver.find_element_by_xpath(GO_BUTTON).click()
            # wait for loading to complete and load month details
            self.__wait_loading()
            
            days = self.number_of_days_in_month(year, month + 1)
            
            for day in range(1, days + 1):
                # lets scrape the date one by one
                self.__scrape_cell(year, month + 1, day)
                self.__close_frame()
                # break
            break

            
    def __scrape_cell(self, year, month, date):
        date_cell = {
                'pday'         : None,
                'ptamil_month' : None,
                'ptamil_star'  : None,
                'pthithi_name' : None,
                'pthithi_img'  : None,
                'special_day'  : None,
                'special_img'  : None,
                'pdata_det'    : None
        }
        
        self.logger.debug(f"Scrapping date yyyy/mm/dd '{year}/{month}/{date}'")
        xpath = DATE_CELL.format(date=date, month=month)
        cell = self.driver.find_element_by_xpath(xpath)
        
        soup = BeautifulSoup(cell.get_attribute("outerHTML"), "html.parser")

        # pday
        try:
            date_cell['pday'] = soup.find_all("div", {"class": "fc-day-number"})[0].text
        except:
            self.logger.debug("ERROR: 'pday' failed to scrap.")
        # ptamil_month
        try:
            date_cell['ptamil_month'] = soup.find_all("div", {"class": "dst"})[0].text
        except:
            self.logger.debug("ERROR: 'ptamil_month' failed to scrap.")
        # ptamil_star
        try:
            date_cell['ptamil_star'] = soup.find_all("div", {"class": "str"})[0].text
        except:
            self.logger.debug("ERROR: 'ptamil_star' failed to scrap.")
        # thithi_name
        try:
            date_cell['pthithi_name'] = soup.find_all("div", {"class": "fst"})[0].text
        except:
            self.logger.debug("ERROR: 'pthithi_name' failed to scrap.")
        # thithi_img
        try:
            date_cell['pthithi_img'] = soup.find_all("img")[0].get('src')
        except:
            self.logger.debug("ERROR: 'pthithi_img' failed to scrap.")
            
        # special_day
        try:
            date_cell['special_day'] = soup.find_all("div", {"class": "mfest"})[0].text
        except:
             self.logger.debug("ERROR: 'special_day' failed to scrap.")
        # special_img
        try:
            date_cell['special_img'] = self.get_image_url(soup.find('td')['style'])
        except:
            self.logger.debug("ERROR: 'special_day' failed to scrap.")
        # detail
        try:
            date_cell['pdata_det'] = soup.find('a').get('abbr')
        except:
            self.logger.debug("ERROR: 'detail' failed to scrap.")

        inserted_id = self.push_to_sql(pd.DataFrame([date_cell]), TABLE_DATES, want_id=True)
        
        self.__close_ad()
        self.driver.find_element_by_xpath(CLICK_CELL.format(date=date, month=month)).click()
        self.__wait_loading()
        self.__scrap_frame(inserted_id)

    def __scrap_frame(self, date_id):
        self.logger.debug(f"Scrapping popup frame")
        frame = self.driver.find_element_by_xpath(POPUP_FRAME)
        self.driver.switch_to.frame(frame)
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # print (soup)
        # date_info
        self.logger.debug("Scrapping date_info")
        date_info = dict.fromkeys(['date_id', 'date', 'month', 'year', 'today_details'])
        date_info['date_id']= date_id
        try:
            table0 = soup.find_all('table')[0]
            table1 = soup.find_all('table')[1]
            table2 = soup.find_all('table')[2]
            print (table1)
            input()
            date, month, year = table1.find('span').text.split('-')
            date_info['date'] = date
            date_info['month'] = month
            date_info['year'] = year
            date_info['today_details'] = table0.find('div', {'class':'ball bbnone tamilcal_detail y'}).text.strip()
        except Exception as e:
            self.logger.debug("ERROR: while retrieving data_info -> " +  str(e))
        finally:
            if self.log:
                print ("DATE_INFO:\n", date_info)
        self.push_to_sql(pd.DataFrame([date_info]), TABLE_DATE_INFO)
  
        # kural
        kural = dict.fromkeys(['date_id', 'kural', 'pural', 'couplet', 'transliteration', 'explanation'], None)
        kural['date_id'] = date_id    
        self.logger.debug("Scrapping kural")
        try:
            table = table1.find('div' , {'id' : 'vilak'})            
            t = [x for x in table.contents if getattr(x, 'name', None) != 'br']
            kural_text = self.sanitize_cell(table1.find('p', {'id' : 'kural'}).text)           
            kural['kural'] = kural_text          
            last = ''
            for i in t:
                try:
                    i.text
                except AttributeError:
                    if last.lower() not in (kural.keys()):
                        kural['pural'] = i
                    else:
                        kural[last.lower()] = i
                finally:
                    try:last = self.sanitize_kural(i)
                    except:pass
        except Exception as e:
            self.logger.debug("ERROR: while retrieving kural -> " +  str(e))
        finally:
            if self.log:
                print ("KURAL:\n", kural)
        self.push_to_sql(pd.DataFrame([kural]), TABLE_KURAL)
                
        # tamilmonthid 
        self.logger.debug("Scrapping tamilmonthid")   
        tamilmonthid = dict.fromkeys(
            ['date_id', 'kali', 'year', 'month', 'date', 'eng_month', 'eng_day', 'muslim_year', 'muslim_date', 'muslim_nal', 'muslim_nal_img'], None)
        tamilmonthid['date_id'] = date_id
        try:
            tamilmonthid['kali'] = table2.find('td', {'class' : 'kali'}).text
        except Exception as e:
            self.logger.debug("ERROR: while retrieving kali in tamilmonthid table -> " +  str(e))
        try:
            tamilmonthid['year'] = table2.find('td', {'class' : 'tyr'}).text # year
            tamilmonthid['month'] = table2.find('td', {'class' : 'tmon'}).text # month
            tamilmonthid['date'] = table2.find('td', {'class' : 'tdate bleft o'}).text # date 
        except Exception as e:
            self.logger.debug("ERROR: while retrieving year/month/date in tamilmonthid table - " +  str(e)) 
        try:
            tamilmonthid['eng_month'] = table2.find('td', {'class' : 'e_mon'}).text # eng month
            tamilmonthid['eng_day'] = table2.find('td', {'class' : 'tamilday'}).text # eng day
        except Exception as e:
            self.logger.debug("ERROR: while retrieving eng date in tamilmonthid table - " +  str(e)) 
        try:
            tamilmonthid['muslim_year'] = table2.find('td', {'class' : 'is_year'}).text # islamic year
            tamilmonthid['muslim_date'] = table2.find('td', {'class' : 'ball'}).text # muslim date
            t = table2.find_all('td', {'class' : 'bold'})
            for i in t:
                if i.find('img') is not None:
                    tamilmonthid['muslim_nal'] = i.text
                    tamilmonthid['muslim_nal_img'] = i.find('img').get('src')
                    break
        except Exception as e:
            self.logger.debug("ERROR: while retrieving muslim dates in tamilmonthid table -> " +  str(e)) 
        if self.log:
            print ("TAMILMONTHID:\n", tamilmonthid)
        self.push_to_sql(pd.DataFrame([tamilmonthid]), TABLE_TAMIL_MONTH)
          
        # dailypalanid    
        li = soup.find_all('li')
        dailypalanid = []
        for index, dailypalan in enumerate(li):
            dailypalan_ = dict.fromkeys(['date_id', 'star', 'god_name', 'palan'], None)
            dailypalan_['date_id'] = date_id
            
            if len(dailypalan.text.split('-')) < 2:
                continue
            try:
                dailypalan_['star'] = self.sanitize_cell(dailypalan.text.split('-')[0])
            except Exception as e:
                self.logger.debug(f"ERROR: while star (index: {index}) -> " +  str(e))
            try:
                dailypalan_['god_name'] = self.sanitize_cell(dailypalan.text.split('-')[1])
            except Exception as e:
                self.logger.debug(f"ERROR: while god_name (index: {index}) -> " +  str(e))
            try:
                dailypalan_['palan'] = BeautifulSoup(dailypalan.find('a').get('abbr'), features="lxml").text
            except Exception as e:
                self.logger.debug(f"ERROR: while palan (index: {index}) -> " +  str(e))
            dailypalanid.append(dailypalan_)
        if self.log:
            print ("DAILYPALANID:\n", dailypalanid)
        self.push_to_sql(pd.DataFrame(dailypalanid), TABLE_DAILY_PALAN)
        
        

        second_last = self.__create_list_from_table(soup, "twid ball b")
        last = self.__create_list_from_table(soup, 'twid ball btnone')
        footer_table = self.__create_list_from_table(soup, 'ball bbnone')
        
        
        # ABOVE FOOTER
        above_footer = dict.fromkeys(['sulai', 'pariharam', 'chandrashtam'], None)
        try:
            above_footer['sulai'] = footer_table[1][1]
            above_footer['pariharam'] = footer_table[0][4]
            above_footer['chandrashtam'] = footer_table[4]
        except Exception as e:
            self.logger.debug(f"ERROR: while above FOOTER retreiving -> " +  str(e))
        
        # footer
        try:
            footer = dict(zip(['nalla_neram_morning', 'nalla_neram_evening', 'gowri_morning', 'gowri_evening', 'rahu_kal_morning', 'rahu_kal_evening', 'guligai_morning', 'guligai_evening', 'yamagandam_morning', 'yamagandam_evening', 'footer'],
                     self.skip_and_flat(second_last) + self.skip_and_flat(last) + [None]
            ))
            footer.update(above_footer)
            footer['date_id'] = date_id
            try:
                footer['footer'] = soup.find('td', {'class' : 'footer'}).text
            except:pass            
            if self.log:
                print ("FOOTER:\n", footer)
            self.push_to_sql(pd.DataFrame([footer]), TABLE_FOOTER)
        except Exception as e:
            self.logger.debug(f"ERROR: while FOOTER retreiving -> " +  str(e))
            
      
    
    def __create_list_from_table(self, soup, tag):
        try:
            table = soup.find('table', attrs={'class': tag})
            table_rows = table.find_all('tr') 
            l = []  
            for tr in table_rows:
                td = tr.find_all('td')
                row = [tr.text for tr in td]
                l.append(row)
            return l
        except:
            return None 
    
    def skip_and_flat(self, lst):
        np_array = np.array(lst)
        r = list(np_array[:,1:].flatten())
        ret = []
        for elem in r:
            ret.append(elem.split(':')[-1])
        return ret
                  
         
    def __wait_loading(self):
        self.logger.debug("...")
        skip = 0
        while True:       
            time.sleep(0.3)
            if not self.driver.find_element_by_xpath(LOADING_FRAME).is_displayed():
                skip += 1
            if skip >= 3:
                return

    def __close_ad(self):
        try:
            ad = self.driver.find_element_by_xpath(AD)
            if ad.is_displayed():
                ad.click()
                time.sleep(0.2)
        except:pass
    
    def __close_frame(self):
        try:self.driver.switch_to.default_content()
        except Exception as e:
            print ('.',e)
        try:
            ad = self.driver.find_element_by_xpath('/html/body/div[6]/img')
            if ad.is_displayed():
                ad.click()
                time.sleep(0.2)
        except Exception as e:
            print (e)
        try:self.driver.switch_to.default_content()
        except Exception as e:
            print (',',e)   
            
    def number_of_days_in_month(self, year, month):
        return monthrange(year, month)[1]

    def sanitize_cell(self, txt):
        if txt is None:
            return None
        if txt.strip() == '':
            return None
        return txt.strip()
    
    def sanitize_kural(self, elem):
        if elem is None:
            return None
        return elem.text.replace(":", "").strip()
    
    
    def get_image_url(self, style):
        '''
        INPUT: 
            background-image: url("images/ny.jpg");
        OUTPUT: 
            images/ny.jpg
            
        returns image url path from CSS style string
        '''
        if style is None:
            return None
        style = style.split("(")[-1]
        style = style.replace("\"", "").replace(")", "").replace(";", "")
        return style.strip()
    
    def push_to_sql(self, df, table, want_id=False):
        if not self.to_sql:
            return None
        self.logger.debug(f"Pushing to SQL table `{table}`.")
        try:
            df.to_sql(table, engine, if_exists='append', index=False)
            self.logger.debug("Successfully pushed.")
            return self.get_last_row(table) if want_id else False
        except Exception as e:
            self.logger.debug("ERROR: Failed to push data -> " + str(e))
        return want_id
            
    def get_last_row(self, table):
        a = engine.execute(f'SELECT ID FROM {table} ORDER BY ID DESC LIMIT 1;')
        for rowproxy in a:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for column, value in rowproxy.items():
                return value
        return None
         
        
 
tamil = TamilCalendar([2021]) 
tamil.log = 0
tamil.main_page()
