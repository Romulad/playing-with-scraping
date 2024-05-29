import time
import json

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from parsel import Selector


class GetUdemyCourseReviews:
    base_url = "https://www.udemy.com/course/100-days-of-code/?couponCode=LETSLEARNNOW"

    def get_browser(self):
        options = options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        options.add_argument(f'--lang=en')
        options.add_argument(f"user-agent={self.get_random_user_agent()}")
        browser = webdriver.Firefox(options=options)
        return browser
    
    def get_random_user_agent(self):
        software_names = [SoftwareName.FIREFOX.value]
        operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]   
        user_agent_rotator = UserAgent(
            software_names=software_names, operating_systems=operating_systems, limit=100
        )

        return user_agent_rotator.get_random_user_agent()

    def get_page_source_with_reviews(self):
        print('initializing the driver')
        driver = self.get_browser()
        driver.get(self.base_url)


        print('Waiting for modal button to be visible')
        show_review_modal_btn_xpath = "//button[@data-purpose='show-reviews-modal-trigger-button']"
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located(
                (By.XPATH, show_review_modal_btn_xpath)
            )
        )
        print("🎇 It is visible, find it and click on it")
        show_review_modal_btn = driver.find_element(By.XPATH, show_review_modal_btn_xpath)
        show_review_modal_btn.click()


        print('Waiting for the reviews container to be visible')
        review_container_selc = "ul.reviews-modal--reviews-list--83xqx"
        WebDriverWait(driver, 60).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, review_container_selc)
            )
        )
        print("🎇 It is visible, finding the show more review btn and clicking ten times on it...")
        # to get 120 reviews
        more_review_btn_selc = '//button[@data-purpose="show-more-review-button"]'
        more_review_btn = driver.find_element(By.XPATH, more_review_btn_selc)
        for i in range(10):
            more_review_btn.click()
            time.sleep(5)

        print('Done! Getting the page source and shuts down the driver')
        page_source = driver.page_source
        driver.quit()

        return page_source
    
    def process_html_str(self, page_source):
        selector = Selector(text=page_source)

        all_reviews_cont = selector.css('ul.reviews-modal--reviews-list--83xqx > li')
        datas = []

        print("Extracting review datas in the html string")
        for re_contain in all_reviews_cont:
            reviewer = re_contain.css('.review--review-name-and-rating--T0S-U > p::text').get()
            since = re_contain.css('.review--time-since---NKbL::text').get()
            review = re_contain.css(".show-more-module--content--Rw-xr p::text").get()
            note = re_contain.css('.review--rating-container--PRpK3 .ud-sr-only::text').get()

            singl_data = {"reviewer":reviewer, "since":since, "review":review, "note":note}
            datas.append(singl_data)

        data_count = len(datas)
        print(f"{data_count} reviews extracted !")
        return datas

    def strore_data(self, datas):
        print('Storing the reviews in a json file called: reviews.json')
        with open("reviews.json", "w") as data_f:
            data_f.write(json.dumps(datas, indent=4))
    
    def get_reviews(self):
        page_source = self.get_page_source_with_reviews()
        datas = self.process_html_str(page_source)
        self.strore_data(datas)
        print('All is done! Thanks')



if __name__ == "__main__":
    GetUdemyCourseReviews().get_reviews()

