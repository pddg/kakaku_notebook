from multiprocessing import Queue, Pipe, current_process
import sys
from logging import Logger, getLogger
from collections import defaultdict
from matplotlib.font_manager import FontProperties
import pandas as pd
import matplotlib.pyplot as plt
from pandas import np
from sqlalchemy.inspection import inspect
import seaborn as sns

from scraper import GetTable, ScrapeNoteBook, GetKakakuNoteBookPage
from models import NoteBook, Session, Base, engine
from logger import main_logger_configure, queue_logger_configure, LogListenerProcess


def main():
    Base.metadata.create_all(engine)
    ready_msg = "ready"
    logger_queue = Queue(-1)
    page_parent_conn, page_child_conn = Pipe()
    logger_parent_conn, logger_child_conn = Pipe()

    log_process = LogListenerProcess(queue=logger_queue, pipe=logger_child_conn, verifying_message=ready_msg,
                                     configure=main_logger_configure)
    log_process.start()
    logger_parent_conn.send(ready_msg)

    get_process = GetKakakuNoteBookPage(lcd_from="10", lcd_to="16", configure=queue_logger_configure,
                                        queue=logger_queue, pipe=page_child_conn, verifying_message=ready_msg)
    get_process.start()
    page_parent_conn.send(ready_msg)

    queue_logger_configure(logger_queue)
    logger = getLogger(current_process().name)
    logger.info("Preparing PhantomJS ...")

    logger.info("[Start MainProcess]")
    if page_parent_conn.poll(timeout=60) and logger_parent_conn.poll(timeout=60):
        assert page_parent_conn.recv() == ready_msg, "GetKakakuNoteBookPage Process can't start."
        assert logger_parent_conn.recv() == ready_msg, "LogListener Process can't start."
        logger.debug("All processes ready.")
    else:
        print("[Process start failed]")
        sys.exit(1)

    logger.info("Try to get information from kakaku.com ...")
    while True:
        if page_parent_conn.poll(timeout=60):
            table = GetTable(page_parent_conn.recv())
            for tr in table.all_tr:
                scraped = ScrapeNoteBook(tr)
                add_to_db(scraped, logger=logger)
            page_parent_conn.send("Done")
        else:
            logger.info("[Complete GetKakakuNoteBook Process]")
            break

    logger.info("[End MainProcess]")
    page_parent_conn.send(None)
    logger_queue.put(None)
    log_process.join()
    get_process.join()
    sys.exit()


def add_to_db(scraped: ScrapeNoteBook, logger: Logger):
    logger.debug("Start database process ... {name}".format(name=scraped.name))
    with Session() as sess:
        note_book = NoteBook(name=scraped.name, manufacturer=scraped.manufacture, inch=scraped.inch,
                             weight=scraped.weight, width=scraped.width, height=scraped.height,
                             depth=scraped.depth, battery=scraped.battery, memory=scraped.memory)
        try:
            sess.add(note_book)
            sess.commit()
            logger.info("[Success] " + note_book.name)
        except Exception as e:
            logger.warning("[Error] " + note_book.name)
            logger.error(e.args)


def query_to_dict(rset):
    result = defaultdict(list)
    for obj in rset:
        instance = inspect(obj)
        for key, x in instance.attrs.items():
            if key != "id":
                result[key].append(x.value)
    return result


def plot_data():
    # グラフのスタイルを決定
    sns.set('talk', 'whitegrid', 'dark', font_scale=1.5,
            rc={"lines.linewidth": 2.5, 'grid.linestyle': '--'})
    fp = FontProperties(fname="/Users/pudding/Library/Fonts/ipaexg.ttf")
    with Session() as sess:
        all_pc = sess.query(NoteBook).all()
        # data = [{k: v for k, v in pc.__dict__.items() if k != "_sa_instance_state"} for pc in all_pc]
        data = query_to_dict(all_pc)
    # 0.0は全てNaNに置き換えて計算をスキップ
    df = pd.DataFrame(data).replace("0.0", np.NaN)
    # 780kgとかいう明らかに頭おかしい数値が紛れ込んでいたので適当に削除
    df.loc[df["weight"] > 50, "weight"] = np.NaN
    bins = [10, 11.0, 13.3, 14.0, 15.6, 16]
    labels = [str(inch) + "~" for inch in bins]
    df["group"] = pd.cut(df["inch"], bins, labels=labels[0: -1], right=False)
    grouped = df.groupby("group")
    culumns = [{"column": "weight",
                "title": "重さ（kg）"},
               {"column": "width",
                "title": "横幅（mm）"},
               {"column": "battery",
                "title": "駆動時間（hour）"},
               {"column": "memory",
                "title": "メモリ量（GB）"},
               {"column": "depth",
                "title": "奥行き（mm）"},
               {"column": "height",
                "title": "高さ（mm）"}]
    for column in culumns:
        series = grouped[column["column"]].mean()
        series.plot(alpha=.5, kind="bar", rot=0)
        plt.xlabel("inch")
        plt.ylabel(column["title"], fontproperties=fp)
        plt.tight_layout()
        plt.savefig("mean_{column}.png".format(column=column["column"]))
        plt.close()

if __name__ == '__main__':
    main()
    plot_data()
