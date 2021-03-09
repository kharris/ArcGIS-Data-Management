import arcpy, pathlib, random, selenium, time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

#Create a list of possible time delays to use between each use of the online converter
delays = [a for a in range(5,25)]

#Set variables to file folder file paths for input and each stage of output
convertedFiles = Path(r"C:\Documents\Projects\ALCM\GPS COMPRESSED\GPX\convertedFiles.txt")
fileFolder = Path(r"C:\Documents\Projects\ALCM\GPS COMPRESSED")
gpxFolder = Path(r"C:\Documents\Projects\ALCM\GPS COMPRESSED\GPX")
geoDataset = Path(r"C:\Documents\Projects\ALCM\Default.gdb\GPXimports")

#Set variables for urls needed to use the online converter and collect the converted files
converterURL = r'https://www.gpsvisualizer.com/convert_input'
downloadURL = r'https://www.gpsvisualizer.com/convert?output'

#Set optional specifications for the Selenium Chrome webdriver
options = Options()
options.add_argument("--headless")
options.add_experimental_option('prefs',{
    'download.default_directory':str(gpxFolder),
    'download.prompt_for_download':False})

#Initiate the webdriver object
driver = webdriver.Chrome(r'./webDrivers/chromedriver',chrome_options=options)

#Create a list of .gps filepaths to be converted
fileList = [f for f in fileFolder.rglob(r'*.gps')]

#Loop through the list of gps files
for n,f in enumerate(fileList,1):
    #Access the input page for the online file converter
    driver.get(converterURL)
    try:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.ID,'convert_format:gpx')))
    finally:
        driver.find_element(By.ID,'convert_format:gpx').click()
    
    #Choose a number from the list of integers to use as a delay time
    time.sleep(random.choice(delays))
    
    #Enter the filepath of the gps file to be converted and submit
    driver.find_element(By.ID,'input:uploaded_file_1').send_keys(str(f))
    driver.find_element_by_name('submitted').click()

    #Wait for the results page to load
    try:
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH,r'/html/body/table/tbody/tr/td[2]/p[3]/a')))
    finally:
        #Find the download button and click
        link = driver.find_element(By.XPATH,r'/html/body/table/tbody/tr/td[2]/p[3]/a')
        outfile = link.text.strip('Click to download ')
        link.click()
    
    #Add the file name to a list of converted files to track progress in case the connection breaks
    with open(convertedFiles,'a') as outf:
        outf.write(f.stem+'\n')
    time.sleep(random.choice(delays))
    
    #Wait for the converted file to finish downloading to the selected output folder
    while not (gpxFolder/outfile).exists():
        time.sleep(15)

    #Rename the newly converted file to match the input file's name
    renamedFile = (gpxFolder/'Renamed'/(f.stem+'.gpx'))
    #Mark the file as a duplicate if a gpx file by the same name exisits in the output folder
    if renamedFile.exists():
        renamedFile = (gpxFolder/'Renamed'/(f.stem+'_Dup.gpx'))
    (gpxFolder/outfile).rename(renamedFile)
    
    #Import the gpx file as a feature class in ArcGIS and log the file name in a new field in the feature class
    try:
        arcpy.GPXtoFeatures_conversion(str(renamedFile),str(geoDataset/f'{renamedFile.stem}_May18'))
        arcpy.AddField_management(str(geoDataset/f'{renamedFile.stem}_May18'),'vidName','TEXT',field_length=50,field_alias='Video Name')
        arcpy.CalculateField_management(str(geoDataset/f'{renamedFile.stem}_May18'),'vidName',f'{renamedFile.stem}','PYTHON3')
    #If the file cannot be imported to a feature class, log the file name in a tracking text file and continue on to the next gps file
    except:
        with open(fileFolder/'notGIS.txt','a') as ngis:
            ngis.write(renamedFile.stem+'\n')
            time.sleep(random.choice(delays))
        continue
    #If the gpx file succesfully imports to a feature class, add the new feature class to the master feature class of previously imported gpx files
    else:
        arcpy.Append_management(str(geoDataset/f'gpx{renamedFile.stem}_May18'),str(geoDataset/'gpxAll_May18'))


#Close the tracking list text file, delay for 5 seconds, and quite the webdriver object
outf.close()
time.sleep(5)
driver.quit()

    
print('Finished')
