from concurrent.futures import ThreadPoolExecutor
import json
from tqdm import tqdm
import random
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36")
chrome_options.add_argument("service_args = ['–ignore - ssl - errors = true', '–ssl - protocol = TLSv1']")
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('useAutomationExtension=false')

job_info_list = []
number = 1
class Crawler(object):
    def __init__(self):
        self.salary = ['01','02','03','04','05','06','07','08','09','10','11','12']
        #使用selenium模拟浏览器
        self.driver = webdriver.Chrome(options=chrome_options)
        #设置请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',

        }
        #存储爬取的信息
        self.info_list = []
        #设置请求参数
    #模拟拖动滑块验证码
    def get_slider(self,distance):
        #获取滑块元素
        #按住滑块
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = random.randint(10, 50) / 100
        # 初速度
        v = random.randint(3, 7)
        while current < distance:
            if current < mid:
                # 加速度为2
                a = random.randint(10 , 25)
            else:
                # 加速度为-2
                a = -random.randint(3 , 7)
            v0 = v
            # 当前速度
            v = v0 + a * t
            # 移动距离
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        # 模拟人类行为，根据轨迹拖动滑块
        return track
    def get_info_list(self,number):
        job_list = []
        url = f'https://we.51job.com/api/job/search-pc?api_key=51job&timestamp=1717585220&keyword=&searchType=2&function=&industry=&jobArea=020000&jobArea2=&landmark=&metro=&salary=&workYear=&degree=&companyType=&companySize=&jobType=&issueDate=&sortType=0&pageNum={number}&requestId=4dff2bf654d4cdef375458e7941f3025&pageSize=100&source=1&accountId=246964694&pageCode=sou%7Csou%7Csoulb'
        for salary in self.salary:
            url = f'https://we.51job.com/api/job/search-pc?api_key=51job&timestamp=1717585220&keyword=&searchType=2&function=&industry=&jobArea=020000&jobArea2=&landmark=&metro=&salary={salary}&workYear=&degree=&companyType=&companySize=&jobType=&issueDate=&sortType=0&pageNum={number}&requestId=4dff2bf654d4cdef375458e7941f3025&pageSize=100&source=1&accountId=246964694&pageCode=sou%7Csou%7Csoulb'
            #发送请求
            self.driver.get(url)
            #查询class="nc_iconfont btn_slide"的元素
            slider = self.driver.find_element(by=By.ID, value='nc_1_n1z')
            #获取滑块的位置
            location = slider.location
            #获取滑块的大小
            size = slider.size
            #获取滑块的宽度
            width = size.get('width')
            #获取滑块的高度
            height = size.get('height')
            #获取滑块的位置
            x = location.get('x')
            y = location.get('y')
            #获取滑块的位置
            distance = 258
            #获取滑块的轨迹
            track = self.get_slider(distance)
            #按住滑块
            webdriver.ActionChains(self.driver).click_and_hold(slider).perform()
            #移动滑块
            for x in track:
                webdriver.ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
            #释放滑块
            webdriver.ActionChains(self.driver).release().perform()
            #显示等待
            self.driver.implicitly_wait(3)

            try:
                #存储json
                json_str = self.driver.find_element('tag name','pre').text
                #解析json
                json_dict = json.loads(json_str)
                #json_dict转换成dict
                tmp_list = json_dict['resultbody']['job']['items']


                self.info_list.extend(tmp_list)
                job_list.extend(tmp_list)
            except:
                pass
        return job_list

if __name__ == '__main__':
    crawler = Crawler()

    for i in tqdm(range(1, 10)):
        job_list = crawler.get_info_list(i)
        with open('job_v1.jsonl','a',encoding='utf-8') as f:
            for info in job_list:
                f.write(json.dumps(info,ensure_ascii=False)+'\n')