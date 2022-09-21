from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
import time, re
import pandas as pd

# Data analyst jobs in Perth, WA
# url = 'https://www.linkedin.com/jobs/search/?currentJobId=3263075064&distance=25&f_PP=103392068&geoId=101452733&keywords=data%20analyst'

# Data analyst jobs in Australia
# url = 'https://www.linkedin.com/jobs/search/?keywords=Data%20Analyst&location=Australia&locationId=&geoId=101452733&f_TPR=&position=1&pageNum=0'

# Exact "Data Analyst" search in Australia 
url = 'https://au.linkedin.com/jobs/search?keywords=%22Data%20Analyst%22&location=Australia&geoId=101452733&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0'

# Exact "Data Scientist" search in Australia
# url = 'https://www.linkedin.com/jobs/search?keywords=%22Data%2BScientist%22&location=Australia&geoId=101452733&trk=public_jobs_jobs-search-bar_search-submit&currentJobId=3267232669&position=1&pageNum=0'

# Exact "Data Engineer" search in Australia
# url = 'https://au.linkedin.com/jobs/search?keywords=%22Data%20Engineer%22&location=Australia&geoId=101452733&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0'

# Turn off logging options from chrome driver
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Set up chromedriver
driver = webdriver.Chrome(service=ChromeService(executable_path=ChromeDriverManager().install()), options=options)
driver.get(url=url)


# Get number of results
num_jobs = driver.find_element(By.CSS_SELECTOR, '[for="f_TPR-3"]').get_attribute('innerText')
num_jobs = int(re.sub("[^0-9]", "", num_jobs))
print(f"Number of jobs: {num_jobs}")

job_lists = driver.find_element(By.CLASS_NAME, 'jobs-search__results-list')
jobs = job_lists.find_elements(By.TAG_NAME, 'li') # return a list

# Scroll to see more jobs
while len(jobs) < num_jobs - 5:
  try:
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    jobs = job_lists.find_elements(By.TAG_NAME, 'li')
    print(f"Show jobs: {len(jobs)}")
    try:
      click_more_element = driver.find_element(By.CLASS_NAME, 'infinite-scroller__show-more-button')
      ActionChains(driver).move_to_element(click_more_element).click(click_more_element).perform()
      time.sleep(1.5)
    except:
      pass
      time.sleep(1.5)
  except:
    break

# Store all the information in the post
job_titles = []
company_names = []
locations = []
dates = []
job_links = []

job_types = []
job_descs = []

driver.maximize_window()

count = 1
for job in jobs:
  print(f"Job {count}")

  job_title = job.find_element(By.CSS_SELECTOR, 'h3').get_attribute('innerText')

  # Check if job title is Analyst
  # if "Analyst" not in job_title:
  #   print(f"Job {count} is not an Analyst job")
  #   count += 1
  #   continue

  job_titles.append(job_title)

  company_name = job.find_element(By.CSS_SELECTOR,'h4').get_attribute('innerText')
  company_names.append(company_name)

  location = job.find_element(By.CLASS_NAME,'job-search-card__location').get_attribute('innerText')
  locations.append(location)

  date = job.find_element(By.CSS_SELECTOR, 'div>div>time').get_attribute('datetime')
  dates.append(date)

  job_link = job.find_element(By.CSS_SELECTOR,'a').get_attribute('href')
  job_links.append(job_link)

  try:
    # Scroll down to the job element
    time.sleep(0.5)
    ActionChains(driver).scroll_to_element(job.find_element(By.CSS_SELECTOR, 'div>div>time')).perform()
    delta_y = 100
    ActionChains(driver).scroll_by_amount(0, delta_y).perform()
    print("Scrolled")
    time.sleep(0.5)

    # Click on job detail
    job_click_element = job.find_element(By.CLASS_NAME, 'search-entity-media').find_element(By.TAG_NAME, 'img')
    ActionChains(driver).move_to_element(job_click_element).click(job_click_element).perform()
    print("Click detail")
    time.sleep(0.5)

    job_detail = driver.find_element(By.CLASS_NAME, 'details-pane__content')
    
    job_type = job_detail.find_element(By.CLASS_NAME, 'description__job-criteria-list').get_attribute('innerText')
    job_types.append(job_type)
    # print(f"Job types: {job_type}")

    # Click on show more
    job_show_more_element = job_detail.find_element(By.CLASS_NAME, 'show-more-less-html__button')
    ActionChains(driver).move_to_element(job_show_more_element).click(job_show_more_element).perform()
    print("Click More")

    job_desc = job_detail.find_element(By.CLASS_NAME, 'show-more-less-html__markup').get_attribute('innerText')
    job_descs.append(job_desc)
    # print(f"Job desc: {job_desc}")
  except:
    print(f"Fail job {count}")
    if len(job_types) != len(job_titles):
      job_types.append("None")
    if len(job_descs) != len(job_titles):
      job_descs.append("None")
  count += 1

  # if count == 5:
  #   break

print(len(company_names))
print(len(dates))
print(len(job_titles))
print(len(locations))
print(len(job_descs))
print(len(job_types))
print(len(job_links))


job_data = pd.DataFrame(
{ 'Company': company_names,
  'Date': dates,
  'Title': job_titles,
  'Location': locations,
  'Description': job_descs,
  'Type': job_types,
  'Link': job_links,
})


t = time.localtime()
timestamp = time.strftime('%b-%d-%Y_%H%M', t)

file_name = f'LinkedIn-Job-Data-Analyst-{timestamp}.xlsx'
job_data.to_excel(f'output/{file_name}', index=False)

driver.quit()