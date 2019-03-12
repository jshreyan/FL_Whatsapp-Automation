from selenium import webdriver
import time
import traceback
import os
from selenium.webdriver.chrome.options import Options


print("\nBegin.")
print("\nPlease ensure data folder path is configured in bin\config.txt file.")
URL = 'https://web.whatsapp.com'
BASELOC = None

start = time.time()

options = Options()
options.add_argument('--log-level=3')

def findbasepath():
    f = open("bin\config.txt", "r")
    path = f.read().strip()
    BASELOC =  findConfigVar(path,'PATH')
    print('Data Location:',BASELOC)
    return BASELOC

def findConfigVar(csvtxt,varname):
    if varname in csvtxt:
        start = csvtxt.find(varname)+csvtxt[csvtxt.find(varname):].find('"')+1
        end = start+csvtxt[start:].find('"')
        varvalue = csvtxt[start:end].strip()
    else:
        varvalue= 'NA'
    return varvalue

def getURL(url):
    driver.get(url)
    return driver

def ExtractImageNames(BASELOC):
    contactnames,contacttxtnames = [],[]
    for file in os.listdir(BASELOC):
        if file.endswith(".jpg"):
            contact = file[:file.index('.jpg')]
            contactnames.append(contact)
        elif file.endswith(".jpeg"):
            contact = file[:file.index('.jpeg')]
            contactnames.append(contact)

    for txtfile in os.listdir(BASELOC):
        if txtfile.endswith(".txt"):
            contacttxt = txtfile[:txtfile.index('.txt')]
            if contacttxt not in contactnames:
                contacttxtnames.append(contacttxt)
    return contactnames,contacttxtnames

def ExtractCaptionText(contactnames,contacttxtnames,BASELOC):
    contactlst,txtcontactlst={},{}
    for contact in contactnames:
        try:
            f = open(BASELOC+contact+".txt", "r")
            txtstr = f.read().strip()
            try:
                contacttxt = txtstr[txtstr.index('TEXT:=')+7:txtstr.find('"',2)].strip()
            except:
                contacttxt = 'NA'
            try:
                imagecaption = txtstr[txtstr.index('CAPTION:=')+10:txtstr.rfind('"')].strip()
            except:
                imagecaption = 'NA'            
            contactlst[contact]=[contacttxt,imagecaption]
            f.close()
        except:
            contactlst[contact]=['NA','NA']
    for txtcontact in contacttxtnames:
        try:
            ftxt = open(BASELOC+txtcontact+".txt", "r")
            txtstr2 = ftxt.read().strip()
            try:
                txtcontacttxt =  txtstr2[txtstr2.index('TEXT:=')+7:txtstr2.find('"',2)].strip()
            except:
                txtcontacttxt = 'NA'
            txtcontactlst[txtcontact]=txtcontacttxt
            ftxt.close()
        except:
            txtcontactlst[txtcontact]='NA'
    return contactlst,txtcontactlst

def sendImage(driver,contact,sendtext,imgcaption):
    #Search Contact
    phone_nums = []
    searchphns = findContactsCommand(contact)
    print('Contact Numbers Found:',','.join(searchphns))
    for idx,val in enumerate(searchphns):
        if idx != 0:
            #Search Contact
            searchphnstmp = findContactsCommand(contact)
        findcontactelement = driver.find_element_by_xpath("//img[contains(@src,'"+val+"') and ancestor-or-self::*[@class='_2wP_Y']]")
        findcontactelement.click()
        phn_num = getphnNo(driver) 
        if phn_num not in phone_nums:
            phone_nums.append(phn_num)                  
            #Send Text
            sendTextCommands(sendtext)
            #Send Image
            sendImageCommands(contact,imgcaption)             
            print('Sent to',contact,'-',phn_num)
        else:
            print('Already Sent to',contact,'-',phn_num)
        time.sleep(4)
    if len(searchphns)==0:
        print('Contact Not found:',contact)

def sendText(driver,contact,sendtext):
    #Search Contact
    phone_nums = []
    searchphns = findContactsCommand(contact)
    print('Contact Numbers Found:',','.join(searchphns))
    for idx,val in enumerate(searchphns):
        if idx != 0:
            searchphnstmp = findContactsCommand(contact)
        findcontactelement = driver.find_element_by_xpath("//img[contains(@src,'"+val+"') and ancestor-or-self::*[@class='_2wP_Y']]")
        findcontactelement.click()
        phn_num = getphnNo(driver) 
        if phn_num not in phone_nums:
            phone_nums.append(phn_num)  
            #Send Text            
            sendTextCommands(sendtext)
            print('Sent to',contact,'-',phn_num)
        else:
            print('Already Sent to',contact,'-',phn_num)
        time.sleep(4)
    if len(searchphns)==0:
        print('Contact Not found:',contact)
        
def findContactsCommand(contact):
    #Search Contact
    searchphns = []
    time.sleep(2)
    searchcontact = driver.find_element_by_xpath('//*[@title="Search or start new chat"]')
    searchcontact.clear()
    searchcontact.send_keys(contact)    
    #Select Searched Contact
    time.sleep(4)
    panel = driver.find_element_by_id("pane-side")
    searchphns = findAllPhones(panel,contact)
    #print(searchphns)
    time.sleep(2)
    return searchphns

def findAllPhones(panel,contact):
    searchphns = []
    xpathstr = '[title="'+contact+'"]'
    main = panel.find_elements_by_class_name("_2EXPL")
    for img in main:
        try:
            rightone = img.find_element_by_css_selector(xpathstr)
            imgsrc = img.find_element_by_class_name("Qgzj8").get_attribute("src")
            phone_num = extractPhoneNo(imgsrc)
            searchphns.append(phone_num)
        except:
            None
    return searchphns

def extractPhoneNo(imgsrc):
    strt = imgsrc.find('u=')+2
    phone_num = imgsrc[strt: strt+imgsrc[strt:].find('%')]
    return phone_num

def sendTextCommands(sendtext):
    if sendtext !='NA':
        #Send Text
        time.sleep(4)
        inputtxt = driver.find_element_by_xpath('//*[@contenteditable="true"]')
        inputtxt.clear()
        inputtxt.send_keys(sendtext)
        time.sleep(4)
        #driver.find_element_by_class_name('_2lkdt').click() 
        driver.find_element_by_class_name('_35EW6').click()

def sendImageCommands(contact,imgcaption):
    #Select Image
    time.sleep(2)    
    driver.find_element_by_xpath('//*[@title="Attach"]').click()
    time.sleep(2) 
    driver.find_elements_by_xpath("//input[@type='file']")[0].send_keys(BASELOC+'/'+contact+'.jpg')      
    #Enter Caption
    if imgcaption !='NA':
        time.sleep(4)
        inputcap = driver.find_element_by_xpath('//*[@contenteditable="true"]')
        inputcap.clear()
        inputcap.send_keys(imgcaption)
    #Send Image and Caption
    time.sleep(4)
    driver.find_elements_by_class_name('_3hV1n')[0].click()
    
def getphnNo(driver):
    try:
        main = driver.find_element_by_id("main")
        header = main.find_element_by_tag_name("header")
        imgsrc = header.find_element_by_tag_name("img").get_attribute("src")
        phone_num = extractPhoneNo(imgsrc)
    except:
        phone_num = 'NA' 
    return phone_num
    
def fetchData():
    global BASELOC
    BASELOC = findbasepath()
    contactnames,contacttxtnames = ExtractImageNames(BASELOC)
    contactlst,txtcontactlst = ExtractCaptionText(contactnames,contacttxtnames,BASELOC)
    print('\nContactDetails(Text):\n',txtcontactlst)
    print('\nContactDetails(Image & Text):\n',contactlst)
    return contactlst,txtcontactlst

def processData(driver,txtcontactlst,contactlst):
    print('\nPart1 - Sending Texts to contacts in progress.')
    for key,val in txtcontactlst.items():
        name = key
        text = val
        print('\nContact Name:',name,'\nText:',text)
        try:
            sendText(driver,name,text)
        except:
            print('Failed in sending Text to:',name)
            #print(traceback.format_exc())
            
    print('\nPart2 - Sending Images/Texts to contacts in progress.')            
    for key,val in contactlst.items():
        name = key
        text = val[0]
        caption = val[1]
        print('\nContact Name:',name,'\nText:',text,'\nImage Caption:',caption)
        try:
            sendImage(driver,name,text,caption)
        except:
            print('Failed in sending Image/Text to:',name)
            print(traceback.format_exc())

try:
    print('\nFetching Contacts and Data.')
    contactlst,txtcontactlst = fetchData()
    print('\nLaunching Browser.')
    driver = webdriver.Chrome('bin/chromedriver.exe',chrome_options=options,service_log_path='NUL')
    driver = getURL(URL)
    input('\nScan QR Code and Press Enter when chats are loaded:')
    print('Loading..')
    time.sleep(10)
    processData(driver,txtcontactlst,contactlst)
    print('\nSending Complete.')
    print('\nRefreshing Page.')
    driver.refresh()
except:
    print('\nSomething went wrong.')
    print('\nError:\n',traceback.format_exc())

end = time.time()
print('\nTime taken:',end - start, 'Seconds')
time.sleep(10)
print('\nPlease wait till all images are uploaded successfully. ')
input('If yes, press enter key to exit browser & this window.. \n')
time.sleep(2)
driver.quit()
