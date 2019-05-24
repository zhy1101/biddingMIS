import pandas as pd
import pymysql
from sqlalchemy import create_engine
import bidHelp

engine = create_engine('mysql+pymysql://root:zhy2153411@127.0.0.1:3306/bidHelp', echo=False)
cnx = engine.raw_connection()

def computeBidConditoin():
    projects = bidHelp.models.Project.objects.filter(pState__paramID = 21)
    pIDs=[]
    devicese=[]
    cIDs = []
    quantity=[]
    bidPrice = []
    isWin=[]
    contractPrice=[]
    lostRrason1=[]
    lostRrason2 =[]
    lostRrason3 =[]
    lostRrason4=[]
    lostRrason5=[]
    time = []
    for project in projects:
        pIDs.append(project.pID)
        devicese.append(project.aimDevice.id)
        cIDs.append(bidHelp.fastGetter.getCustomerBypID(project.pID).cID)
        quantity.append(project.quantity)
        bidPrice.append(project.bidPrice)
        isWin.append(bidHelp.fastGetter.getBidResultByPID(project.pID))
        try:
             contractPrice.append(bidHelp.fastGetter.getContractByPID(project.pID).contractPrice)
        except:
             contractPrice.append(0)
        lostRrason1.append(bidHelp.fastGetter.lostReasonisPrice(project.pID))
        lostRrason2.append(bidHelp.fastGetter.lostReasonisTec(project.pID))
        lostRrason3.append(bidHelp.fastGetter.lostReasonisRelation(project.pID))
        lostRrason4.append(bidHelp.fastGetter.lostReasonisAftersale(project.pID))
        lostRrason5.append(bidHelp.fastGetter.lostReasonisOther(project.pID))
        time.append(project.startTime)
    data={'pID':list(pIDs),'device':list(devicese),'cID':list(cIDs),'quantity':list(quantity),'bidPrice':bidPrice,'isWin':isWin,'contractPrice':contractPrice,'lostReason1':lostRrason1,'lostReason2':lostRrason2,'lostReason3':lostRrason3,'lostReason4':lostRrason4,'lostReason5':lostRrason5,'time':time}
    frame = pd.DataFrame(data)
    frame['time'] = pd.to_datetime(frame['time'])
    # 将date设置为index
    df = frame.set_index('time')
    timeSet=['2012Q1','2012Q2','2012Q3','2012Q4','2013Q1','2013Q2','2013Q3','2013Q4','2014Q1','2014Q2','2014Q3',
             '2014Q4','2015Q1','2015Q2','2015Q3','2015Q4','2016Q1','2016Q2','2016Q3','2016Q4','2017Q1','2017Q2',
             '2017Q3','2017Q4','2018Q1','2018Q2','2018Q3','2018Q4']
    Q_Frame = df.resample('Q')  #全体重采样
    Q_count_Frame = Q_Frame.count()
    bidNum = Q_count_Frame.pID.iloc[4:32].tolist()  #季度投标总数统计
    winNum = df[df['isWin']>0].resample('Q').count().pID.iloc[4:32].tolist() #季度中标总数统计
    winRate = []   #季度中标率
    for i in range(len(bidNum)):
        winRate.append('%.2f' %(winNum[i]/bidNum[i]*100))

    #机型占比统计
    deviceName=['制粒线机型','贴标机','灯检机','压片机','包衣机','装盒机','胶囊填充机','胶囊称重机','灭菌柜','水制备系统','外洗机','轧盖机','检漏机','注射器灌封线','西林瓶灌封设备','安瓿瓶灌封设备','卡式瓶灌封设备']
    sql_data = pd.read_sql('select count(case when aimDevice_id in (74,1,82,98,45,55,71,27,6,68) then quantity end) as 制粒线机型,count(case when aimDevice_id in (74,1,82,98,89,49) then quantity end) as 贴标机,'+
                'count(case when aimDevice_id in (62,61,12,87,77,76,86) then quantity end) as 灯检机,count(case when aimDevice_id in (50,84,37,4,5,67) then quantity end) as 压片机,count(case when aimDevice_id in (33,83) then quantity end) as 包衣机,'+
                'count(case when aimDevice_id in (66,45,35,34,57) then quantity end) as 装盒机,count(case when aimDevice_id in (20,40,22,2,21,38,18,19) then quantity end) as 胶囊填充机,count(case when aimDevice_id in (3) then quantity end) as 胶囊称重机,'+
                'count(case when aimDevice_id in (25,13) then quantity end) as 灭菌柜,count(case when aimDevice_id in (36,42,59,58) then quantity end) as 水制备系统,count(case when aimDevice_id in (94) then quantity end) as 外洗机,'+
                'count(case when aimDevice_id in (15,52) then quantity end) as 轧盖机,count(case when aimDevice_id in (72) then quantity end) as 检漏机,count(case when aimDevice_id in (63,64,11,10,23,32) then quantity end) as 注射器灌封线,'+
                'count(case when aimDevice_id in (54,69,96,7,8,79,51,65,29,73) then quantity end) as 西林瓶灌封设备,count(case when aimDevice_id in (24,93,78,85,30,99,97,26,78) then quantity end) as 安瓿瓶灌封设备,'+
                'count(case when aimDevice_id in (32,53,44,9) then quantity end) as 卡式瓶灌封设备 from bidhelp_project', cnx)
    deviceNum = sql_data[0:1].values[0]
    deviceName_Num = zip(deviceName,deviceNum)

    #统计季度标价下浮率
    sumBidPrice = df[df['isWin'] > 0].resample('Q').sum().bidPrice.iloc[4:32].tolist()
    sumContractPrice = df[df['isWin'] > 0].resample('Q').sum().contractPrice.iloc[4:32].tolist()

    #统计失标原因
    sumLostPro = len(df[df['isWin'] < 1])   #总失标数
    lostForPrice = len(df[df['lostReason1'] > 0])  #由于价格失标的项目数
    lostForTec = len(df[df['lostReason2'] > 0])  # 由于技术设计失标的项目数
    lostForRelation = len(df[df['lostReason3'] > 0])  # 由于客户关系失标的项目数
    lostForAfterSale = len(df[df['lostReason4'] > 0])  # 由于售后服务失标的项目数
    lostForOther = len(df[df['lostReason5'] > 0])  # 由于售后服务失标的项目数

    result={'timeSet':timeSet,'bidNum_Q':bidNum,'winNum_Q':winNum,'winRate_Q':winRate,'deviceName_Num':deviceName_Num,'deviceName':deviceName,
            'sumBidPrice_Q':sumBidPrice,'sumContractPrice_Q':sumContractPrice,'sumLostPro':sumLostPro,
            'lostForPrice':lostForPrice,'lostForTec':lostForTec,'lostForRelation':lostForRelation,'lostForAfterSale':lostForAfterSale,
            'lostForOther':lostForOther}
    return result


