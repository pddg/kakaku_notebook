from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from time import sleep
from logging import getLogger
from multiprocessing import Process, Pipe, Queue, current_process


class GetKakakuNoteBookPage(Process):
    url = "http://kakaku.com/specsearch/0020/"
    des_cap = dict(DesiredCapabilities.PHANTOMJS)
    des_cap['phantomjs.page.settings.userAgent'] = (
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
        'Chrome/28.0.1500.52 Safari/537.36'
    )

    def __init__(self, lcd_from: str, lcd_to: str, configure, queue: Queue, pipe: Pipe, verifying_message: str):
        super(GetKakakuNoteBookPage, self).__init__()
        assert int(lcd_to) > int(lcd_from) > 0, "lcd_to should be bigger than lcd_from."
        self.lcd_from = lcd_from
        self.lcd_to = lcd_to
        self.paging = True
        self.current_page_num = 1
        self.queue = queue
        self.pipe = pipe
        self.log_configure = configure
        self.driver = self.initialize()
        self.verifying_message = verifying_message

    def initialize(self) -> webdriver.PhantomJS:
        driver = webdriver.PhantomJS(desired_capabilities=self.des_cap)
        driver.get(self.url)
        # select lcd size
        lcd_option = driver.find_elements_by_name("LCDSize")
        select_lcd_from = Select(lcd_option[0])
        select_lcd_to = Select(lcd_option[1])
        select_lcd_from.select_by_value(self.lcd_from)
        select_lcd_to.select_by_value(self.lcd_to)

        # select exists only
        exists_option = driver.find_element_by_id("lDispNonPrice")
        exists_option.click()

        # Enter
        enter = driver.find_elements_by_css_selector("div.mTop10 input")
        for option in enter:
            if option.get_attribute("type") == "image":
                option.click()
        return driver

    def run(self):
        self.log_configure(self.queue)
        logger = getLogger(current_process().name)
        logger.info("[Start GetKakakuNoteBook Process]")
        if self.pipe.poll(timeout=5):
            assert self.pipe.recv() == self.verifying_message, "MainProcess didn't send message."
            self.pipe.send(self.verifying_message)
        else:
            logger.info("Can't start GetKakakuNoteBook process.")
            import sys
            sys.exit(1)
        try:
            while self.paging:
                if self.pipe.poll(timeout=5):
                    if self.pipe.recv() is None:
                        import sys
                        logger.info("[End GetKakakuNoteBook Process]")
                        sys.exit()
                self.pipe.send(self.driver.page_source)
                move_page_buttons = self.driver.find_elements_by_css_selector("div.paging a")
                if move_page_buttons[-1].text.isdigit():
                    self.paging = False
                    logger.info("Finished get page.")
                else:
                    self.current_page_num += 1
                    logger.debug("Try to get page {num}".format(num=str(self.current_page_num)))
                    move_page_buttons[-1].click()
                    logger.info("[Success] Get page {num}".format(num=str(self.current_page_num)))
                logger.debug("Wait for 30 seconds ...")
                sleep(30)
        except BrokenPipeError:
            logger.info("Pipe is broken. Process finished.")
            import sys
            sys.exit()
