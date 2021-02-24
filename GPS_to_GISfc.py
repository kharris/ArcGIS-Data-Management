import arcpy, pathlib, random, selenium, time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

delays = [a for a in range(5,25)]

convertedFiles = Path(r"C:\Documents\Projects\ALCM\GPS COMPRESSED\GPX\convertedFiles.txt")
fileFolder = Path(r"C:\Documents\Projects\ALCM\GPS COMPRESSED")
gpxFolder = Path(r"C:\Documents\Projects\ALCM\GPS COMPRESSED\GPX")
geoDataset = Path(r"C:\Documents\Projects\ALCM\Default.gdb\GPXimports")

converterURL = r'https://www.gpsvisualizer.com/convert_input'
downloadURL = r'https://www.gpsvisualizer.com/convert?output'

options = Options()
options.add_argument("--headless")
options.add_experimental_option('prefs',{
    'download.default_directory':str(gpxFolder),
    'download.prompt_for_download':False})

driver = webdriver.Chrome(r'./webDrivers/chromedriver',chrome_options=options)

fileList = [f for f in fileFolder.rglob(r'*.gps')]

for n,f in enumerate(fileList[198:],1):
    driver.get(converterURL)
    try:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.ID,'convert_format:gpx')))
    finally:
        driver.find_element(By.ID,'convert_format:gpx').click()
        
    time.sleep(random.choice(delays))
    driver.find_element(By.ID,'input:uploaded_file_1').send_keys(str(f))
    driver.find_element_by_name('submitted').click()

    try:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH,r'/html/body/table/tbody/tr/td[2]/p[3]/a')))
    finally:
        link = driver.find_element(By.XPATH,r'/html/body/table/tbody/tr/td[2]/p[3]/a')
        outfile = link.text.strip('Click to download ')
        link.click()

    with open(convertedFiles,'a') as outf:
        outf.write(f.stem+'\n')
    time.sleep(random.choice(delays))

    while not (gpxFolder/outfile).exists():
        time.sleep(15)

    renamedFile = (gpxFolder/'Renamed'/(f.stem+'.gpx'))
    if renamedFile.exists():
        renamedFile = (gpxFolder/'Renamed'/(f.stem+'_Dup.gpx'))
    (gpxFolder/outfile).rename(renamedFile)
        
    try:
        arcpy.GPXtoFeatures_conversion(str(renamedFile),str(geoDataset/f'{renamedFile.stem}_May18'))
        arcpy.AddField_management(str(geoDataset/f'{renamedFile.stem}_May18'),'vidName','TEXT',field_length=50,field_alias='Video Name')
        arcpy.CalculateField_management(str(geoDataset/f'{renamedFile.stem}_May18'),'vidName',f'{renamedFile.stem}','PYTHON3')
    except:
        with open(fileFolder/'notGIS.txt','a') as ngis:
            ngis.write(renamedFile.stem+'\n')
            time.sleep(random.choice(delays))
        continue
    else:
        arcpy.Append_management(str(geoDataset/f'gpx{renamedFile.stem}_May18'),str(geoDataset/'gpxAll_May18'))


outf.close()
time.sleep(5)
driver.quit()

    
print('Finished')
