import sys
import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

class AnyEc:
    """ Use with WebDriverWait to combine expected_conditions
        in an OR.
    """
    def __init__(self, *args):
        self.ecs = args
    def __call__(self, driver):
        for fn in self.ecs:
            try:
                if fn(driver): return True
            except:
                pass

def getItemPrice(driver, lego_id, amount, shop):
    if shop == 'SuT':
        return getItemPriceSuT(driver, lego_id, amount)
    elif shop == 'PaB':
        return getItemPricePaB(driver, lego_id, amount)
    else:
        raise(Exception('Please select either >SuT< or >Pab< as shop.'))

def addToBasket(driver, lego_id, amount, shop):
    if shop == 'SuT':
        return getItemPriceSuT(driver, lego_id, amount, True)
    elif shop == 'PaB':
        return getItemPricePaB(driver, lego_id, amount, True)
    else:
        raise(Exception('Please select either >SuT< or >Pab< as shop.'))


def getItemPriceSuT(driver, lego_id, amount, add_to_basket=False):
    element = driver.find_element_by_xpath('//input[@ng-model="itemNumber"]')
    element.clear()
    element.send_keys(lego_id)
    element.send_keys(Keys.RETURN)

    # wait until page is loaded
    try:
        element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//button[@ng-click="addToBasket(brick,$event)"]')))  
        # print ("Page \""+driver.title+"\" is ready!")
    except TimeoutException:
        print ("Loading took too much time!")

    status = [0]
    # check if item is not available
    try:
        driver.find_element_by_xpath('//div[@class="list-item is-sold-out"]')

        print ("Item "+str(lego_id)+" is not available at SuT.")
        status[0] = 1
        status.append(lego_id)
        status.append("NA")

    except NoSuchElementException:
        # fill the item 'amount' times in the basket
        if amount > 200:
            amount = 200
            print('Cannot order more than 200 of item '+str(lego_id))

        if add_to_basket:
            for i in range(amount):
                element.click()
  
        status.append(amount)

        element = driver.find_elements_by_xpath('//td[@class="ng-binding"]')
        price = element[2].get_attribute('innerHTML')
        price = price.split()
        status.append(price[1])

    # return to the search page
    element = driver.find_element_by_xpath('//button[@ng-click="anotherSet()"]')
    element.click()

    return (status)

def getItemPricePaB(driver, lego_id, amount, add_to_basket=False):
    element = driver.find_element_by_id('element_id-0')
    element.clear()
    element.send_keys(lego_id)
    element.send_keys(Keys.RETURN)

    # wait until result is loaded
    try:
        WebDriverWait(driver, 10).until(AnyEc(
            EC.text_to_be_present_in_element((By.XPATH, '//div[@class="pab-search__header-count"]'), "Anzeige: 0 von 0 steine"), 
            EC.text_to_be_present_in_element((By.XPATH, '//div[@class="pab-search__header-count"]'), "Anzeige: 1 von 1 steine")))
        # print ("Page \""+driver.title+"\" is ready!")
    except TimeoutException:
        print ("Loading took too much time!")

    # element = driver.find_element_by_xpath('//div[@class="pab-search__header-count"]')
    # available = "Anzeige: 1 von 1 steine" in (element.get_attribute('innerHTML'))
    # if(available):
    status = [0]
    try:
        element = driver.find_element_by_xpath('//span[@class="pab-item-summary__price"]')
        price = element.get_attribute('innerHTML')
        price = price.split()

        if add_to_basket:
            element = driver.find_element_by_id('pab-item-summary__input')
            element.clear()
            element.send_keys(amount)

            element = driver.find_element_by_xpath('//button[@class="pab-item__btn-pick"]')
            element.click()

        status.append(amount)
        status.append(price[0])

    except WebDriverException:
        print ("Item "+str(lego_id)+" is not available at PaB.")
        status[0] = 1
        status.append(lego_id)
        status.append("NA")

    element = driver.find_element_by_xpath('//button[@class="pab-filters-basic__btn-clear"]')
    element.click()

    return status

def createPriceDifferenceCSV(csvfile,driver1,driver2):
    start_time = time.time()
    number_of_elements = 0
    unavailable = []

    outfile = open('price_difference_'+csvfile, 'w')
    with open(csvfile, 'r') as infile:
        reader = csv.reader(infile)
        # This skips the first row of the CSV file.
        next(reader)

        writer = csv.writer(outfile)
        writer.writerow( ('LEGO element ID', 'Amount', 'Price SuT', 'Price PaB') )        

        for row in reader:
            lego_id = row[0]
            amount = row[1]
            number_of_elements += 1

            status1 = getItemPrice(driver1,lego_id,int(amount),'SuT')
            status2 = getItemPrice(driver2,lego_id,int(amount),'PaB')
            if status1[0]==1 and status2[0]==1:
                unavailable.append(lego_id)
            writer.writerow( (lego_id, amount, status1[2], status2[2]) )

    outfile.close()
    infile.close()

    duration = divmod(time.time()-start_time,60)
    print ()
    print('Priced {} elements in {:.0f} minutes and {:.1f} seconds.'.format(number_of_elements,duration[0],duration[1]))
    if len(unavailable) > 0:
        print('Currently unavailable in both shops are {} parts. The IDs are {}'.format(len(unavailable),unavailable))

def addToBasketWithPriceDifference(csvfile,driver1,driver2):
    start_time = time.time()
    total_parts = 0
    total_items = 0
    total_price = 0
    total_saved = 0
    PaB_parts = 0
    Pab_items = 0
    unavailable = []

    with open(csvfile, 'r') as infile:
        reader = csv.reader(infile)
        # This skips the first row of the CSV file.
        next(reader)       

        for row in reader:
            lego_id = row[0]
            amount = int(row[1])
            if row[2] == 'NA' and row[3] == 'NA':
                unavailable.append(lego_id)
            else:
                if row[2] == 'NA':
                    status = addToBasket(driver2, lego_id, amount, 'PaB')
                    total_price += float(row[3].replace(',','.')) * amount
                    PaB_parts += 1
                    Pab_items += amount
                elif row[3] == 'NA':
                    status = addToBasket(driver1, lego_id, amount, 'SuT')
                    total_price += float(row[2].replace(',','.')) * amount
                else:
                    price_SuT = float(row[2].replace(',','.'))
                    price_PaB = float(row[3].replace(',','.'))
                    if price_PaB - price_SuT >= 0:
                        status = addToBasket(driver1, lego_id, amount, 'SuT')
                        total_price += price_SuT * amount
                    else:
                        status = addToBasket(driver2, lego_id, amount, 'PaB')
                        total_price += price_PaB * amount
                        total_saved += (price_SuT - price_PaB) * amount
                        PaB_parts += 1
                        Pab_items += amount
                total_parts += 1
                total_items += amount
    infile.close()


    duration = divmod(time.time()-start_time,60)
    print ()
    print('Placed {} parts with {} items and a total cost of {:.2f} EUR in {:.0f} minutes and {:.1f} seconds in the shopping cart.'.format(total_parts,total_items,total_price,duration[0],duration[1]))
    if len(unavailable) > 0:
        print('Currently unavailable in both shops are {} parts. The IDs are {}'.format(len(unavailable),unavailable))
    print('Buying {} parts with {} items at Pick-a-Brick saves a total amount of {:.2f} EUR.'.format(PaB_parts,Pab_items, total_saved))

def addToBasketFromCSV(infile,driver,shop='SuT'):
    start_time = time.time()
    total_parts = 0
    total_items = 0
    unavailable = []

    with open(infile, 'r') as csvfile:
        reader = csv.reader(csvfile)
        # This skips the first row of the CSV file.
        next(reader)

        for row in reader:
            lego_id = row[0]
            amount = int(row[1])

            status = addToBasket(driver, lego_id, amount, shop)

            if status[0] == 0:
                total_parts += 1
                total_items += status[1]
            elif status[0] == 1:
                unavailable.append(status[1])

    csvfile.close()

    duration = divmod(time.time()-start_time,60)
    print ()
    print('Placed {} parts with {} items in {:.0f} minutes and {:.1f} seconds in the shopping cart.'.format(total_parts,total_items,duration[0],duration[1]))
    if len(unavailable) > 0:
        print('{} parts are currently unavailable. The IDs are {}'.format(len(unavailable),unavailable))

def getDriverForSuT():
    # open window for SuT
    driver = webdriver.Firefox()
    driver.get('https://www.lego.com/de-de/service/replacementparts')

    linkElem = driver.find_element_by_xpath('//a[@ng-click="showAgeAndCountryPopUp(3)"]')
    linkElem.click()

    linkElem = driver.find_element_by_xpath('//input[@name="rpAgeAndCountryAgeField"]')
    linkElem.send_keys("28")
    linkElem.send_keys(Keys.RETURN)

    try:
        linkElem = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//input[@ng-model="itemNumber"]')))  
        # print ("Page \""+driver.title+"\" is ready!")
    except TimeoutException:
        print ("Loading took too much time!")

    return driver

def getDriverForPaB():
    # open window for PaB
    driver = webdriver.Firefox()
    driver.get('https://shop.lego.com/de-DE/Pick-a-Brick')

    return driver

def getDriverForLego(shop='SuT'):
    if shop == 'SuT':
        return getDriverForSuT()
    elif shop == 'PaB':
        return getDriverForPaB()
    else:
        raise(Exception('Please select either >SuT< or >Pab< as shop.'))



if __name__ == "__main__":
    # use with python3
    if any(sys.argv[1] in s for s in ['ATLAS_full.csv', 'ATLAS_mid-size.csv', 'ATLAS_mini.csv', 'LHC_micro_full.csv']):
        createPriceDifferenceCSV(sys.argv[1],getDriverForLego('SuT'),getDriverForLego('PaB'))
        # addToBasketWithPriceDifference('price_difference_'+sys.argv[1],getDriverForLego('SuT'),getDriverForLego('PaB'))
        # addToBasketFromCSV(sys.argv[1],getDriverForLego('SuT'),'SuT')
        # addToBasketFromCSV(sys.argv[1],getDriverForLego('PaB'),'PaB')
    else:
        raise(Exception('Please provide part list.'))

