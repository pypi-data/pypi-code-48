import sys
import json
import math
from datetime import datetime, timedelta
import time

import mysql.connector

from aliyunsdkcore.client import AcsClient
from aliyunsdkrds.request.v20140815.DescribeSlowLogRecordsRequest import DescribeSlowLogRecordsRequest


__version__ = "0.1.0"


class CollectSlowLogRecordsJob:
    def __init__(self, ak, secret, region_id, rdsinst_id, startT, endT, scrape_window: int, shift_time: int, dbconfig):
        self.aliyuncoreClient = AcsClient(ak, secret, region_id)

        self.startT = datetime.now() - \
            timedelta(minutes=scrape_window) if startT is None else datetime.strptime(
                startT, "%Y-%m-%d %H:%M")
        self.endT = datetime(9999, 1, 1) if endT is None else datetime.strptime(
            endT, "%Y-%m-%d %H:%M")
        self.scrape_window = scrape_window
        self.shift_time = shift_time
        self.rdsinst_id = rdsinst_id
        self.tcdb = CollectDatabase(**dbconfig)

    def toCollectDB(self, record):
        record['DBInstanceId'] = self.rdsinst_id
        d = record['ExecutionStartTime']
        record['ExecutionStartTime'] = d.replace('T', ' ')[:-1]
        self.tcdb.insertSlowlogrecords(record)

    def dateToStr(self, d):
        return d.strftime("%Y-%m-%dT%H:%MZ")

    def isScrape(self, e):
        return e < datetime.now() - timedelta(minutes=self.shift_time)

    def start(self):
        _local_startT = self.startT
        while _local_startT <= self.endT:
            _local_endT = _local_startT + timedelta(minutes=self.scrape_window)

            if self.isScrape(_local_endT):
                print("start scrape {} - {}".format(_local_startT, _local_endT))
                arsrr = AliyunRdsSRR(self.aliyuncoreClient, self.rdsinst_id, self.dateToStr(_local_startT),
                                     self.dateToStr(_local_endT))
                cnt = 0
                for i in arsrr.getAllSlr():
                    self.toCollectDB(i)
                    cnt += 1
                print("end scrape {} - {}, {} row".format(_local_startT, _local_endT, cnt))
                _local_startT = _local_endT
            else:
                time.sleep(self.scrape_window * 60)


class CollectDatabase:
    x = ("INSERT INTO aliyun.t_slowlogrecords "
         "(DBInstanceId, DBName, SQLText, QueryTimes, LockTimes, ParseRowCounts, ReturnRowCounts, ExecutionStartTime, HostAddress) "
         "VALUES (%(DBInstanceId)s, %(DBName)s, %(SQLText)s, %(QueryTimes)s, %(LockTimes)s, %(ParseRowCounts)s, %(ReturnRowCounts)s, %(ExecutionStartTime)s, %(HostAddress)s)")

    def __init__(self, mip, mport, muser, mpass, mdatabase):
        self.mip = mip
        self.mport = mport
        self.muser = muser
        self.mpass = mpass
        self.mdatabase = mdatabase
        self.createConnect()
        # print(self.insertSlowLogRecordsSQL)

    def insertSlowlogrecords(self, slrData):
        _sqltext = self.x
        cur = self.cnx.cursor()
        cur.execute(_sqltext, slrData)
        self.cnx.commit()
        cur.close()

    def createConnect(self):
        try:
            self.cnx = mysql.connector.connect(
                user=self.muser, password=self.mpass, host=self.mip, port=self.mport, database=self.mdatabase)
            # self.cnx.autocommit(True)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
            sys.exit(1)

    def closeConnect(self):
        self.cnx.close()


class AliyunRdsSRR:

    pn = 1  # page number
    req = DescribeSlowLogRecordsRequest()

    def __init__(self, acsClient, instId, st: str, et: str, pageSize=30):
        self.acsClient = acsClient
        self.instId = instId
        self.st = st
        self.et = et
        self.pageSize = pageSize
        self.initSlrReq()

    def initSlrReq(self):
        self.req.set_accept_format('json')
        self.req.set_DBInstanceId(self.instId)
        self.req.set_StartTime(self.st)
        self.req.set_EndTime(self.et)
        self.req.set_PageSize(self.pageSize)

    def reqSlrByPn(self, pn: int):
        self.req.set_PageNumber(pn)
        response = self.acsClient.do_action_with_exception(self.req)
        return json.loads(response.decode('utf-8'))

    def getAllSlr(self):
        retry = 0
        while True:
            try:
                res = self.reqSlrByPn(self.pn)
            except Exception:
                time.sleep(60)
                if retry < 10:
                    print('inst id: {} scrape retry {}.'.format(self.instId), retry)
                    continue
                else:
                    print('inst id: {} scrape faile.'.format(self.instId))
                    sys.exit(1)
                retry += 1
            if self.isMoreData(res['PageRecordCount']):
                for r in res["Items"]['SQLSlowRecord']:
                    yield r
                self.pn += 1
                time.sleep(1)
            else:
                time.sleep(1)
                return

    def isMoreData(self, prc):
        return prc >= 1  # prc > 0


if __name__ == "__main__":
    import os
    ak = os.environ.get('ak')
    secret = os.environ.get('secret')
    region_id = os.environ.get('region_id')
    inst_id = os.environ.get('inst_id')
    start_time = os.environ.get('start_time', None)
    end_time = os.environ.get('end_time', None)
    scrape_window = os.environ.get('scrape_window', 1)
    shift_time = os.environ.get('shift_time', 1)

    cdbip = os.environ.get('cdbip')
    cdbport = os.environ.get('cdbport', 3306)
    cdbuser = os.environ.get('cdbuser')
    cdbpass = os.environ.get('cdbpass')
    cdbdatabase = os.environ.get('cdbdatabase')

    for env in ['ak', 'secret', 'region_id', 'inst_id', 'cdbip',  'cdbuser', 'cdbpass', 'cdbdatabase']:
        if os.environ.get(env) is None:
            print("env {} is Nnone.".format(env))
            sys.exit(1)

    dbconfig = {"mip": cdbip, "mport": cdbport, "muser": cdbuser,
                "mpass": cdbpass, "mdatabase": cdbdatabase}

    job = CollectSlowLogRecordsJob(ak, secret, region_id, inst_id,
                                   start_time, end_time, scrape_window, shift_time, dbconfig)

    job.start()
