from bs4 import BeautifulSoup

from typing import List, Tuple
import re


class GetTable(object):

    def __init__(self, source: str):
        self.bs = BeautifulSoup(source, "lxml")
        self.all_tr = self.find_all_tr()

    def find_all_tr(self) -> List[BeautifulSoup]:
        table = self.bs.findAll("table", attrs={"class": "tblBorderGray02"})
        return [tr for tr in table[0].findAll("tr") if tr.get("class") is None]


class ScrapeNoteBook(object):

    targets = ["液晶サイズ", "駆動時間", "幅x高さx奥行", "重量", "メモリ容量"]

    def __init__(self, tr: BeautifulSoup):
        self.target_tds = [td for td in tr.findAll("td")
                           if td.label is not None and td.label.get("title") in self.targets]
        self.manufacture, self.name = self.scrape_name(tr.findAll("td")[2])
        self.inch = self.scrape_inch(self.target_tds[0])  # 8
        self.memory = self.scrape_memory(self.target_tds[1])  # 17
        self.battery = self.scrape_battery(self.target_tds[2])  # 37
        self.width, self.height, self.depth = self.scrape_measurements(self.target_tds[3])  # 38
        self.weight = self.scrape_weight(self.target_tds[4])  # 39

    @staticmethod
    def scrape_name(td: BeautifulSoup) -> Tuple[str, str]:
        assert td.get('class')[0] == "textL", "Class Name is invalid."
        strongs = td.findAll("strong")
        return strongs[0].text, strongs[1].a.text

    @staticmethod
    def scrape_inch(td: BeautifulSoup) -> float:
        assert td.label.get("title") == "液晶サイズ", "Class Name is invalid."
        raw = td.label.text
        inch_str = re.sub(r"インチ$", "", raw)
        assert bool(re.compile("^\d+\.?\d*\Z").match(inch_str)), "inch value is not float."
        return float(inch_str)

    @staticmethod
    def scrape_battery(td: BeautifulSoup) -> float:
        assert td.label.get("title") == "駆動時間", "Class Name is invalid."
        raw_str = re.sub(r"時間$", "", td.label.text) if len(td.label.text) > 2 else "0"
        assert bool(re.compile("^\d+\.?\d*\Z").match(raw_str)), "battery value is not float"
        return float(raw_str)

    @staticmethod
    def scrape_measurements(td: BeautifulSoup) -> Tuple[float, float, float]:
        assert td.label.get("title") == "幅x高さx奥行", "Class Name is invalid."
        raw_str = re.sub(r"mm$", "", td.label.text) if len(td.label.text) > 2 else "0"
        if raw_str == "0":
            return 0.0, 0.0, 0.0
        raw_stripped = raw_str.split("x")
        assert len(raw_stripped) == 3, "Measurements values is invalid."
        return (float(size) for size in raw_stripped)

    @staticmethod
    def scrape_weight(td: BeautifulSoup) -> float:
        assert td.label.get("title") == "重量", "Class Name is invalid."
        raw_str = td.label.text if len(td.label.text) > 1 else "0"
        if raw_str == "0":
            return 0.0
        raw_sub = re.sub(r"kg$", "", raw_str)
        assert bool(re.compile("^\d+\.?\d*\Z").match(raw_sub)), "Weight value is invalid."
        return float(raw_sub)

    @staticmethod
    def scrape_memory(td: BeautifulSoup) -> int:
        assert td.label.get("title") == "メモリ容量", "Class Name is invalid."
        raw_str = td.label.text if len(td.label.text) > 2 else "0"
        if raw_str == "0":
            return 0
        raw_sub = re.sub(r"GB$", "", raw_str)
        assert raw_sub.isdigit(), "Memory value is invalid."
        return int(raw_sub)

    def __repr__(self):
        return "<ScrapedNoteBook '{name}'>".format(name=self.name)
