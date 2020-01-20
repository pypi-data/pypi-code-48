"""

    SlideRunner 

    https://www5.cs.fau.de/~aubreville/

   Database functions
"""

import sqlite3
import os
import time
import numpy as np
import random
import uuid

def generate_uuid():
    return str(uuid.uuid4())


class DatabaseField(object):
    def __init__(self, keyStr:str, typeStr:str, isNull:int=0, isUnique:bool=False, isAutoincrement:bool=False, defaultValue:str='', primaryKey:int=0):
        self.key = keyStr
        self.type = typeStr
        self.isNull = isNull
        self.isUnique = isUnique
        self.isAutoincrement = isAutoincrement
        self.defaultValue = defaultValue
        self.isPrimaryKey = primaryKey

    def creationString(self):
        return ("`"+self.key+"` "+self.type+
                ((" DEFAULT %s " % self.defaultValue) if not(self.defaultValue == "") else "") + 
                (" PRIMARY KEY" if self.isPrimaryKey else "")+
                (" AUTOINCREMENT" if self.isAutoincrement else "")+
                (" UNIQUE" if self.isUnique else "") )


def isActiveClass(label, activeClasses):
        if (label) is None:
            return True
        if (label<len(activeClasses)):
            return activeClasses[label]
        else:
            print('Warning: Assigned label is: ',label,' while class list is: ',activeClasses)
            return 0

class DatabaseTable(object):
    def __init__(self, name:str):
        self.entries = dict()
        self.name = name

    def add(self, field:DatabaseField):
        self.entries[field.key] = field
        return self

    def getCreateStatement(self):
        createStatement = "CREATE TABLE `%s` (" % self.name
        cnt=0
        for idx, entry in self.entries.items():
            if cnt>0:
                createStatement += ','
            createStatement += entry.creationString()
            cnt+=1
        createStatement += ");"
        return createStatement

    def checkTableInfo(self, tableInfo):
        if (tableInfo is None) or (len(tableInfo)==0):
            return False
        allKeys=list()
        for entry in tableInfo:
            idx,key,typeStr,isNull,defaultValue,PK = entry
            if (key not in self.entries):
                return False
            if not (self.entries[key].type == typeStr):
                return False
            allKeys += [key]
        for entry in self.entries:
            if entry not in allKeys:
                return False
        # OK, defaultValue, isNull are not important to be checked

        return True


    def addMissingTableInfo(self, tableInfo, tableName):
        returnStr = list()
        if (tableInfo is None) or (len(tableInfo)==0):
            return False
        allKeys=list()
        for entry in tableInfo:
            idx,key,typeStr,isNull,defaultValue,PK = entry
            allKeys += [key]

        for entry in self.entries.keys():
            if entry not in allKeys:
                returnStr.append('ALTER TABLE %s ADD COLUMN %s' % (tableName, self.entries[entry].creationString()))

        return returnStr


from SlideRunner.dataAccess.annotations import *

from typing import Dict

class Database(object):
    annotations = Dict[int,annotation]

    minCoords = np.empty(0)
    maxCoords = np.empty(0)

    def __init__(self):
        self.dbOpened = False
        self.VA = dict()

        self.databaseStructure = dict()
        self.transformer = None
        self.annotations = dict()       
        self.doCommit = True
        self.annotationsSlide = None
        self.databaseStructure['Log'] = DatabaseTable('Log').add(DatabaseField('uid','INTEGER',isAutoincrement=True, primaryKey=1)).add(DatabaseField('dateTime','FLOAT')).add(DatabaseField('labelId','INTEGER'))
        self.databaseStructure['Slides'] = DatabaseTable('Slides').add(DatabaseField('uid','INTEGER',isAutoincrement=True, primaryKey=1)).add(DatabaseField('filename','TEXT')).add(DatabaseField('width','INTEGER')).add(DatabaseField('height','INTEGER')).add(DatabaseField('directory','TEXT')).add(DatabaseField('uuid','TEXT'))
        self.databaseStructure['Annotations'] = DatabaseTable('Annotations').add(DatabaseField('uid','INTEGER',isAutoincrement=True, primaryKey=1)).add(DatabaseField('guid','TEXT')).add(DatabaseField('deleted','INTEGER',defaultValue=0)).add(DatabaseField('slide','INTEGER')).add(DatabaseField('type','INTEGER')).add(DatabaseField('agreedClass','INTEGER')).add(DatabaseField('lastModified','REAL',defaultValue=str(time.time())))

    def isOpen(self):
        return self.dbOpened

    def appendToMinMaxCoordsList(self, anno: annotation):
        self.minCoords = np.vstack((self.minCoords, np.asarray(anno.minCoordinates().tolist()+[anno.uid])))
        self.maxCoords = np.vstack((self.maxCoords, np.asarray(anno.maxCoordinates().tolist()+[anno.uid])))
    def generateMinMaxCoordsList(self):
        # MinMaxCoords lists shows extreme coordinates from object, to decide if an object shall be shown
        self.minCoords = np.zeros(shape=(len(self.annotations),3))
        self.maxCoords = np.zeros(shape=(len(self.annotations),3))
        keys = self.annotations.keys() 
        for idx,annokey in enumerate(keys):
            annotation = self.annotations[annokey]
            self.minCoords[idx] = np.asarray(annotation.minCoordinates().tolist()+[annokey])
            self.maxCoords[idx] = np.asarray(annotation.maxCoordinates().tolist()+[annokey])

#        print(self.getVisibleAnnotations([0,0],[20,20]))
    
    def getVisibleAnnotations(self, leftUpper:list, rightLower:list) -> Dict[int, annotation]:
        potentiallyVisible =  ( (self.maxCoords[:,0] > leftUpper[0]) & (self.minCoords[:,0] < rightLower[0]) & 
                                (self.maxCoords[:,1] > leftUpper[1]) & (self.minCoords[:,1] < rightLower[1]) )
        ids = self.maxCoords[potentiallyVisible,2]
        return dict(filter(lambda i:i[0] in ids, self.annotations.items()))

    def listOfSlides(self):
        self.execute('SELECT uid,filename from Slides')
        return self.fetchall()


    def annotateImage(self, img: np.ndarray, leftUpper: list, rightLower:list, zoomLevel:float, vp : ViewingProfile, selectedAnnoID:int):
        annos = self.getVisibleAnnotations(leftUpper, rightLower)
        self.VA = annos
        for idx,anno in annos.items():
            if (isActiveClass(activeClasses=vp.activeClasses,label=anno.agreedLabel())) and not anno.deleted:
                anno.draw(img, leftUpper, zoomLevel, thickness=2, vp=vp, selected=(selectedAnnoID==anno.uid))
    
    def findIntersectingAnnotation(self, anno:annotation, vp: ViewingProfile, database=None, annoType = None):    
        if (database is None):
            database = self.VA            
        for idx,DBanno in database.items():
            if (vp.activeClasses[DBanno.agreedLabel()]):
                if (DBanno.intersectingWithAnnotation(anno )):
                    if (annoType == DBanno.annotationType) or (annoType is None):
                        return DBanno
        return None

    def findClickAnnotation(self, clickPosition, vp : ViewingProfile, database=None, annoType = None):
        if (database is None):
            database = self.VA            
        for idx,anno in database.items():
            if (vp.activeClasses[anno.agreedLabel()]):
                if (anno.positionInAnnotation(clickPosition )) and (anno.clickable):
                    if (annoType == anno.annotationType) or (annoType is None):
                        return anno
        return None

    def loadIntoMemory(self, slideId, transformer=None):
        self.annotations = dict()
        self.annotationsSlide = slideId
        self.guids = dict()
        self.transformer = transformer

        if (slideId is None):
            return

        self.dbcur.execute('SELECT uid, type,agreedClass,guid,lastModified,deleted FROM Annotations WHERE slide == %d'% slideId)
        allAnnos = self.dbcur.fetchall()


        self.dbcur.execute('SELECT coordinateX, coordinateY,annoid FROM Annotations_coordinates where annoId IN (SELECT uid FROM Annotations WHERE slide == %d) ORDER BY orderIdx' % (slideId))
        allCoords = np.asarray(self.dbcur.fetchall())

        if self.transformer is not None:
            allCoords = self.transformer(allCoords)

        for uid, annotype,agreedClass,guid,lastModified,deleted in allAnnos:
            coords = allCoords[allCoords[:,2]==uid,0:2]
            if (annotype == AnnotationType.SPOT):
                self.annotations[uid] = spotAnnotation(uid, coords[0][0], coords[0][1])
            elif (annotype == AnnotationType.SPECIAL_SPOT):
                self.annotations[uid] = spotAnnotation(uid, coords[0][0], coords[0][1], True)
            elif (annotype == AnnotationType.POLYGON):
                self.annotations[uid] = polygonAnnotation(uid, coords)
            elif (annotype == AnnotationType.AREA):
                self.annotations[uid] = rectangularAnnotation(uid, coords[0][0], coords[0][1], coords[1][0], coords[1][1])
            elif (annotype == AnnotationType.CIRCLE):
                self.annotations[uid] = circleAnnotation(uid, coords[0][0], coords[0][1], coords[1][0], coords[1][1])
            else:
                print('Unknown annotation type %d found :( ' % annotype)
            self.annotations[uid].agreedClass = agreedClass
            self.annotations[uid].guid = guid
            self.annotations[uid].lastModified = lastModified
            self.annotations[uid].deleted = deleted
            self.guids[guid] = uid
        # Add all labels
        self.dbcur.execute('SELECT annoid, person, class,uid FROM Annotations_label WHERE annoID in (SELECT uid FROM Annotations WHERE slide == %d)'% slideId)
        allLabels = self.dbcur.fetchall()

        for (annoId, person, classId,uid) in allLabels:
            self.annotations[annoId].addLabel(AnnotationLabel(person, classId, uid), updateAgreed=False)


        self.generateMinMaxCoordsList()

            
    

    def checkTableStructure(self, tableName, action='check'):
        self.dbcur.execute('PRAGMA table_info(%s)' % tableName)
        ti = self.dbcur.fetchall()
        if (action=='check'):
            return self.databaseStructure[tableName].checkTableInfo(ti)
        elif (action=='ammend'):
            return self.databaseStructure[tableName].addMissingTableInfo(ti, tableName)

    def open(self, dbfilename):
        if os.path.isfile(dbfilename):
            self.db = sqlite3.connect(dbfilename)
            self.dbcur = self.db.cursor()
            self.db.create_function("generate_uuid",0, generate_uuid)
            self.db.create_function("pycurrent_time",0, time.time)

            # Check structure of database and ammend if not proper
            if not self.checkTableStructure('Slides'):
                sql_statements = self.checkTableStructure('Slides','ammend')
                for sql in sql_statements:
                    self.dbcur.execute(sql)
                self.db.commit()

            if not self.checkTableStructure('Annotations'):
                sql_statements = self.checkTableStructure('Annotations','ammend')
                for sql in sql_statements:
                    self.dbcur.execute(sql)
                self.db.commit()

            if not self.checkTableStructure('Log'):
                # add new log, no problemo.
                self.dbcur.execute('DROP TABLE if exists `Log`')
                self.dbcur.execute(self.databaseStructure['Log'].getCreateStatement())
                self.db.commit()
            
            # Migrating vom V0 to V1 needs proper filling of GUIDs
            DBversion = self.dbcur.execute('PRAGMA user_version').fetchone()
            if (DBversion[0]==0):
                self.dbcur.execute('UPDATE Annotations set guid=generate_uuid() where guid is NULL')

                self.addTriggers()

                # Add last polygon point (close the line)
                allpolys = self.dbcur.execute('SELECT uid from Annotations where type==3').fetchall()
                for [polyid,] in allpolys:
                    coords = self.dbcur.execute(f'SELECT coordinateX, coordinateY,slide FROM Annotations_coordinates where annoid=={polyid} and orderidx==1').fetchone()
                    maxidx = self.dbcur.execute(f'SELECT MAX(orderidx) FROM Annotations_coordinates where annoid=={polyid}').fetchone()[0]+1
                    self.dbcur.execute(f'INSERT INTO Annotations_coordinates (coordinateX, coordinateY, slide, annoId, orderIdx) VALUES ({coords[0]},{coords[1]},{coords[2]},{polyid},{maxidx} )')

                DBversion = self.dbcur.execute('PRAGMA user_version = 1')
                print('Successfully migrated DB to version 1')
                self.commit()

            self.dbOpened = True
            self.dbfilename = dbfilename
            self.dbname = os.path.basename(dbfilename)



            return self
        else:
            return False
    
    def deleteTriggers(self):
        for event in ['UPDATE','INSERT']:
            self.dbcur.execute(f'DROP TRIGGER IF EXISTS updateAnnotation_fromLabel{event}')
            self.dbcur.execute(f'DROP TRIGGER IF EXISTS updateAnnotation_fromCoords{event}')
            self.dbcur.execute(f'DROP TRIGGER IF EXISTS updateAnnotation_{event}')

    def addTriggers(self):
        for event in ['UPDATE','INSERT']:
            self.dbcur.execute(f"""CREATE TRIGGER IF NOT EXISTS updateAnnotation_fromLabel{event}
                        AFTER {event} ON Annotations_label
                        BEGIN
                            UPDATE Annotations SET lastModified=pycurrent_time() where uid==new.annoId;
                        END
                        ;
                        """)

            self.dbcur.execute(f"""CREATE TRIGGER IF NOT EXISTS updateAnnotation_fromCoords{event}
                        AFTER {event} ON Annotations_coordinates
                        BEGIN
                            UPDATE Annotations SET lastModified=pycurrent_time() where uid==new.annoId;
                        END
                        ;
                        """)
            self.dbcur.execute(f"""CREATE TRIGGER IF NOT EXISTS updateAnnotation_{event}
                        AFTER {event} ON Annotations
                        BEGIN
                            UPDATE Annotations SET lastModified=pycurrent_time() where uid==new.uid;
                        END
                        ;
                        """)
    
    # copy database to new file
    def saveTo(self, dbfilename):
        new_db = sqlite3.connect(dbfilename) # create a memory database

        query = "".join(line for line in self.db.iterdump())

        # Dump old database in the new one. 
        new_db.executescript(query)

        return True

    def findSpotAnnotations(self,leftUpper, rightLower, slideUID, blinded = False, currentAnnotator=None):
        q = ('SELECT coordinateX, coordinateY, agreedClass,Annotations_coordinates.uid,annoId,type FROM Annotations_coordinates LEFT JOIN Annotations on Annotations.uid == Annotations_coordinates.annoId WHERE coordinateX >= '+str(leftUpper[0])+
                ' AND coordinateX <= '+str(rightLower[0])+' AND coordinateY >= '+str(leftUpper[1])+' AND coordinateY <= '+str(rightLower[1])+
                ' AND Annotations.slide == %d AND (type==1 OR type==4)'%(slideUID) )
        if not blinded:
            self.execute(q)
            return self.fetchall()
    
        q=(' SELECT coordinateX, coordinateY,0,uid,annoId,1 from Annotations_coordinates WHERE coordinateX >= '+str(leftUpper[0])+
                 ' AND coordinateX <= '+str(rightLower[0])+' AND coordinateY >= '+str(leftUpper[1])+' AND coordinateY <= '+str(rightLower[1])+' AND slide == %d;' % slideUID)
                
        self.execute(q)
        resp = np.asarray(self.fetchall())

        if (resp.shape[0]==0):
            return list()


        self.execute('SELECT annoId, class from Annotations_label LEFT JOIN Annotations on Annotations_label.annoId == Annotations.uid WHERE person==%d and TYPE IN (1,4) GROUP BY annoId' % currentAnnotator)
        myAnnos = np.asarray(self.fetchall())

        if (myAnnos.shape[0]==0):
            myOnes = np.zeros(resp.shape).astype(np.bool)
            mineInAll = np.empty(0)
        else:
            myOnes = np.in1d(resp[:,4],myAnnos[:,0])
            mineInAll = np.in1d(myAnnos[:,0],resp[:,4])

        if mineInAll.shape[0]>0:
            resp[myOnes,2] = myAnnos[mineInAll,1]

        self.execute('SELECT uid,type from Annotations WHERE type IN (1,4) AND slide == %d'% slideUID)
        correctTypeUIDs = np.asarray(self.fetchall())
        if (correctTypeUIDs.shape[0]==0):
            return list() # No annotation with correct type available

        typeFilter = np.in1d(resp[:,4], correctTypeUIDs[:,0])
        assignType = np.in1d(correctTypeUIDs[:,0], resp[:,4])
        resp[:,5] = correctTypeUIDs[assignType,1]
        return resp[typeFilter,:].tolist()
 

    def getUnknownInCurrentScreen(self,leftUpper, rightLower, currentAnnotator) -> annotation:
        visAnnos = self.getVisibleAnnotations(leftUpper, rightLower)
        for anno in visAnnos.keys():
            if (visAnnos[anno].labelBy(currentAnnotator) == 0):
                return anno   
        return None

    def findAllAnnotationLabels(self, uid):
        q = 'SELECT person, class, uid FROM Annotations_label WHERE annoId== %d' % uid
        self.execute(q)
        return self.fetchall()

    def checkIfAnnotatorLabeled(self, uid, person):
        q = 'SELECT COUNT(*) FROM Annotations_label WHERE annoId== %d AND person == %d' % (uid, person)
        self.execute(q)
        return self.fetchone()[0]

    def findClassidOfClass(self, classname):
        q = 'SELECT uid FROM Classes WHERE name == "%s"' % classname
        self.execute(q)
        return self.fetchall()

    def findAllAnnotations(self, annoId, slideUID = None):
        if (slideUID is None):
            q = 'SELECT coordinateX, coordinateY FROM Annotations_coordinates WHERE annoId==%d' % annoId
        else:
            q = 'SELECT coordinateX, coordinateY FROM Annotations_coordinates WHERE annoId==%d AND slide == %d' % (annoId, slideUID)
        self.execute(q)
        return self.fetchall()    

    def findSlideForAnnotation(self, annoId):
        q = 'SELECT filename FROM Annotations_coordinates LEFT JOIN Slides on Slides.uid == Annotations_coordinates.slide WHERE annoId==%d' % annoId
        self.execute(q)
        return self.fetchall()    


    def pickRandomUnlabeled(self, byAnnotator=0) -> annotation:
        annoIds = list(self.annotations.keys())
        random.shuffle(annoIds)
        for annoId in annoIds:
            if (self.annotations[annoId].labelBy(byAnnotator) == 0):
                return self.annotations[annoId]
        return None

    def findPolygonAnnotatinos(self,leftUpper,rightLower, slideUID,blinded = False, currentAnnotator=None):
        if not blinded:
            q = ('SELECT agreedClass,annoId FROM Annotations_coordinates LEFT JOIN Annotations on Annotations.uid == Annotations_coordinates.annoId WHERE coordinateX >= '+str(leftUpper[0])+
                ' AND coordinateX <= '+str(rightLower[0])+' AND coordinateY >= '+str(leftUpper[1])+' AND coordinateY <= '+str(rightLower[1])+
                ' AND Annotations.slide == %d AND type==3 '%(slideUID) +' GROUP BY Annotations_coordinates.annoId')
            self.execute(q)
            farr = self.fetchall()
        else:
            q = ('SELECT 0,annoId FROM Annotations_coordinates LEFT JOIN Annotations on Annotations.uid == Annotations_coordinates.annoId WHERE coordinateX >= '+str(leftUpper[0])+
                ' AND coordinateX <= '+str(rightLower[0])+' AND coordinateY >= '+str(leftUpper[1])+' AND coordinateY <= '+str(rightLower[1])+
                ' AND Annotations.slide == %d AND type==3 '%(slideUID) +' AND Annotations.uid NOT IN (SELECT annoId FROM Annotations_label WHERE person==%d GROUP BY annoID) GROUP BY Annotations_coordinates.annoId' % currentAnnotator)
            self.execute(q)
            farr1 = self.fetchall()

            q = ('SELECT class,Annotations_label.annoId FROM Annotations_coordinates LEFT JOIN Annotations on Annotations.uid == Annotations_coordinates.annoId LEFT JOIN Annotations_label ON Annotations_label.annoId == Annotations.uid WHERE coordinateX >= '+str(leftUpper[0])+
                ' AND coordinateX <= '+str(rightLower[0])+' AND coordinateY >= '+str(leftUpper[1])+' AND coordinateY <= '+str(rightLower[1])+
                ' AND Annotations.slide == %d AND type==3 '%(slideUID) +' AND Annotations_label.person == %d GROUP BY Annotations_coordinates.annoId' % currentAnnotator)
            self.execute(q)
            farr2 = self.fetchall()

            farr = farr1+farr2


        polysets = []
        
        toggler=True
        for entryOuter in range(len(farr)):
            # find all annotations for area:
            allAnnos = self.findAllAnnotations(farr[entryOuter][1])
            polygon = list()
            for entry in np.arange(0,len(allAnnos),1):
                polygon.append([allAnnos[entry][0],allAnnos[entry][1]])
            polygon.append([allAnnos[0][0],allAnnos[0][1]]) # close polygon
            polysets.append((polygon,farr[entryOuter][0],farr[entryOuter][1] ))

        return polysets

    def findAreaAnnotations(self,leftUpper, rightLower, slideUID, blinded = False, currentAnnotator = 0):
        if not blinded:
            q = ('SELECT coordinateX, coordinateY,agreedClass, annoId, type, orderIdx FROM Annotations_coordinates  LEFT JOIN Annotations on Annotations.uid == Annotations_coordinates.annoId WHERE annoID in (SELECT annoId FROM Annotations_coordinates LEFT JOIN Annotations on Annotations.uid == Annotations_coordinates.annoId WHERE coordinateX >= '+str(leftUpper[0])+
                ' AND coordinateX <= '+str(rightLower[0])+' AND coordinateY >= '+str(leftUpper[1])+' AND coordinateY <= '+str(rightLower[1])+
                ' AND Annotations.slide == %d AND type IN (2,5) '%(slideUID) +' group by Annotations_coordinates.annoId) ORDER BY Annotations_coordinates.annoId, orderIdx')
            self.execute(q)
            farr = self.fetchall()

            reply = []
            for entry in range(len(farr)-1):
                # find all annotations for area:
                if (farr[entry][5]==1):
                    reply.append([farr[entry][0],farr[entry][1],farr[entry+1][0],farr[entry+1][1],farr[entry][2],farr[entry][3],farr[entry][4]])
                    # tuple: x1,y1,x2,y2,class,annoId ID, type
            return reply

        else:
            q = ('SELECT 0,annoId,type FROM Annotations_coordinates LEFT JOIN Annotations on Annotations.uid == Annotations_coordinates.annoId WHERE coordinateX >= '+str(leftUpper[0])+
                ' AND coordinateX <= '+str(rightLower[0])+' AND coordinateY >= '+str(leftUpper[1])+' AND coordinateY <= '+str(rightLower[1])+
                ' AND Annotations.slide == %d AND type IN (2,5) '%(slideUID) +' AND Annotations.uid NOT IN (SELECT annoId FROM Annotations_label WHERE person==%d GROUP BY annoID) GROUP BY Annotations_coordinates.annoId' % currentAnnotator)

            self.execute(q)
            farr1 = self.fetchall()

            q = ('SELECT class,Annotations_label.annoId,type FROM Annotations_coordinates LEFT JOIN Annotations on Annotations.uid == Annotations_coordinates.annoId LEFT JOIN Annotations_label ON Annotations_label.annoId == Annotations.uid WHERE coordinateX >= '+str(leftUpper[0])+
                ' AND coordinateX <= '+str(rightLower[0])+' AND coordinateY >= '+str(leftUpper[1])+' AND coordinateY <= '+str(rightLower[1])+
                ' AND Annotations.slide == %d AND type IN (2,5) '%(slideUID) +' AND Annotations_label.person == %d GROUP BY Annotations_coordinates.annoId' % currentAnnotator)

            self.execute(q)
            farr2 = self.fetchall()

            farr = farr1+farr2
            
        reply = []
        toggler=True
        for entryOuter in range(len(farr)):
            # find all annotations for area:
            allAnnos = self.findAllAnnotations(farr[entryOuter][1])
            for entry in np.arange(0,len(allAnnos),2):
                reply.append([allAnnos[entry][0],allAnnos[entry][1],allAnnos[entry+1][0],allAnnos[entry+1][1],farr[entryOuter][0],farr[entryOuter][1],farr[entryOuter][2]])
            # tuple: x1,y1,x2,y2,class,annoId ID, type
        return reply


    def setSlideDimensions(self,slideuid,dimensions):
        if dimensions is None:
            return
        if (slideuid is None):
            return
        if (dimensions[0] is None):
            return
        if (dimensions[1] is None):
            return
        print('Setting dimensions of slide ',slideuid,'to',dimensions)
        self.execute('UPDATE Slides set width=%d, height=%d WHERE uid=%d' % (dimensions[0],dimensions[1],slideuid))
        self.db.commit()

    def findSlideWithFilename(self,slidename,slidepath, uuid:str=None):
        if (len(slidepath.split(os.sep))>1):
            directory = slidepath.split(os.sep)[-2]
        else:
            directory = ''
        ret = self.execute('SELECT uid,directory,uuid,filename from Slides ').fetchall()
        secondBest=None
        for (uid,slidedir,suuid,fname) in ret:
            if (uuid is not None) and (suuid==uuid):
                return uid
            elif (fname==slidename):
                if slidedir is None:
                    secondBest=uid
                elif (slidedir.upper() == directory.upper()):
                    return uid
                else:
                    secondBest=uid
        return secondBest
    
    def insertAnnotator(self, name):
        self.execute('INSERT INTO Persons (name) VALUES ("%s")' % (name))
        self.commit()
        query = 'SELECT last_insert_rowid()'
        return self.execute(query).fetchone()[0]

    def insertClass(self, name):
        self.execute('INSERT INTO Classes (name) VALUES ("%s")' % (name))
        self.commit()
    
    def setAgreedClass(self, classId, annoIdx):
        self.annotations[annoIdx].agreedClass = classId
        q = 'UPDATE Annotations SET agreedClass==%d WHERE uid== %d' % (classId,annoIdx)
        self.execute(q)
        self.commit()
         

    def setAnnotationLabel(self,classId,  person, entryId, annoIdx):
        q = 'UPDATE Annotations_label SET person==%d, class=%d WHERE uid== %d' % (person,classId,entryId)
        self.execute(q)
        self.commit()
        self.annotations[annoIdx].changeLabel(entryId, person, classId)
        
        # check if all labels belong to one class now
        if np.all(np.array([lab.classId for lab in self.annotations[annoIdx].labels])==classId):
            self.setAgreedClass(classId, annoIdx)

        self.checkCommonAnnotation(annoIdx)

    def checkCommonAnnotation(self, annoIdx ):
        allAnnos = self.findAllAnnotationLabels(annoIdx)
        if (len(allAnnos)>0):
            matching = allAnnos[0][1]
            for anno in allAnnos:
                if (anno[1] != matching):
                    matching=0
        else:
            matching=0
        
        q = 'UPDATE Annotations set agreedClass=%d WHERE UID=%d' % (matching, annoIdx)
        self.execute(q)
        self.commit()

    def logLabel(self, labelId):
        query = 'INSERT INTO Log (dateTime, labelId) VALUES (%d, %d)' % (time.time(), labelId)
        self.execute(query)


    def addAnnotationLabel(self,classId,  person, annoId):
        query = ('INSERT INTO Annotations_label (person, class, annoId) VALUES (%d,%d,%d)'
                 % (person, classId, annoId))
        self.execute(query)
        query = 'SELECT last_insert_rowid()'
        self.execute(query)
        newid = self.fetchone()[0]
        self.logLabel(newid)
        self.annotations[annoId].addLabel(AnnotationLabel(person, classId, newid))
        self.checkCommonAnnotation( annoId)
        self.commit()

    def exchangePolygonCoordinates(self, annoId, slideUID, annoList):
        self.annotations[annoId].annotationType = AnnotationType.POLYGON
        self.annotations[annoId].coordinates = np.asarray(annoList)
        self.generateMinMaxCoordsList()

        query = 'DELETE FROM Annotations_coordinates where annoId == %d' % annoId
        self.execute(query)
        self.commit()

        self.insertCoordinates(np.array(annoList), slideUID, annoId)
        

    def insertCoordinates(self, annoList:np.ndarray, slideUID, annoId):
        """
                Insert an annotation into the database.
                annoList must be a numpy array, but can be either 2 columns or 3 columns (3rd is order)
        """

        if self.transformer is not None:
            annoList = self.transformer(annoList, inverse=True)

        for num, annotation in enumerate(annoList.tolist()):
            query = ('INSERT INTO Annotations_coordinates (coordinateX, coordinateY, slide, annoId, orderIdx) VALUES (%d,%d,%d,%d,%d)'
                    % (annotation[0],annotation[1],slideUID, annoId, annotation[2] if len(annotation)>2 else num+1))
            self.execute(query)
        self.commit()


    def insertNewPolygonAnnotation(self, annoList, slideUID, classID, annotator, closed:bool=True):
        query = 'INSERT INTO Annotations (slide, agreedClass, type) VALUES (%d,%d,3)' % (slideUID,classID)
#        query = 'INSERT INTO Annotations (coordinateX1, coordinateY1, coordinateX2, coordinateY2, slide, class1, person1) VALUES (%d,%d,%d,%d,%d,%d, %d)' % (x1,y1,x2,y2,slideUID,classID,annotator)
        if (isinstance(annoList, np.ndarray)):
            annoList=annoList.tolist()
        if (closed):
            annoList.append(annoList[0])
        self.execute(query)
        query = 'SELECT last_insert_rowid()'
        self.execute(query)
        annoId = self.fetchone()[0]
        assert(len(annoList)>0)
        self.annotations[annoId] = polygonAnnotation(annoId, np.asarray(annoList))
        self.appendToMinMaxCoordsList(self.annotations[annoId])
        self.insertCoordinates(np.array(annoList), slideUID, annoId)

        self.addAnnotationLabel(classId=classID, person=annotator, annoId=annoId)

        self.commit()
        return annoId

    def addAnnotationToDatabase(self, anno:annotation, slideUID:int, classID:int, annotatorID:int):
        if (anno.annotationType == AnnotationType.AREA):
            self.insertNewAreaAnnotation(anno.x1,anno.y1,anno.x2,anno.y2,slideUID,classID, annotatorID)
        elif (anno.annotationType == AnnotationType.POLYGON):
            self.insertNewPolygonAnnotation(anno.coordinates, slideUID, classID, annotatorID)
        elif (anno.annotationType == AnnotationType.CIRCLE):
            self.insertNewAreaAnnotation(anno.x1,anno.y1,anno.x2,anno.y2,slideUID,classID, annotatorID, typeId=5)
        elif (anno.annotationType == AnnotationType.SPOT):
            self.insertNewSpotAnnotation(anno.x1, anno.y1, slideUID, classID, annotatorID)
        elif (anno.annotationType == AnnotationType.SPECIAL_SPOT):
            self.insertNewSpotAnnotation(anno.x1, anno.y1, slideUID, classID, annotatorID, type=4)
        

    def getGUID(self, annoid) -> str:
        try:
            return self.execute(f'SELECT guid from Annotations where uid=={annoid}').fetchone()[0]
        except:
            return None

    def insertNewAreaAnnotation(self, x1,y1,x2,y2, slideUID, classID, annotator, typeId=2, uuid=None):
        query = 'INSERT INTO Annotations (slide, agreedClass, type) VALUES (%d,%d,%d)' % (slideUID,classID, typeId)
#        query = 'INSERT INTO Annotations (coordinateX1, coordinateY1, coordinateX2, coordinateY2, slide, class1, person1) VALUES (%d,%d,%d,%d,%d,%d, %d)' % (x1,y1,x2,y2,slideUID,classID,annotator)
        self.execute(query)
        query = 'SELECT last_insert_rowid()'
        self.execute(query)
        annoId = self.fetchone()[0]
        if (typeId==2):
            self.annotations[annoId] = rectangularAnnotation(annoId, x1,y1,x2,y2)
        else:
            self.annotations[annoId] = circleAnnotation(annoId, x1,y1,x2,y2)
        
        self.appendToMinMaxCoordsList(self.annotations[annoId])

        annoList = np.array([[x1,y1,1],[x2,y2,2]])
        self.insertCoordinates(np.array(annoList), slideUID, annoId)
        
        self.addAnnotationLabel(classId=classID, person=annotator, annoId=annoId)

        self.commit()
        return annoId

    def setLastModified(self, annoid:int, lastModified:float):
        self.execute(f'UPDATE Annotations SET lastModified="{lastModified}" where uid={annoid}')
        self.annotations[annoid].lastModified = lastModified

    def setGUID(self, annoid:int, guid:str):
        self.execute(f'UPDATE Annotations SET guid="{guid}" where uid={annoid}')
        self.guids[guid]=annoid
    
    def last_inserted_id() -> int:
            query = 'SELECT last_insert_rowid()'
            self.execute(query)
            return self.fetchone()[0]


    def insertNewSpotAnnotation(self,xpos_orig,ypos_orig, slideUID, classID, annotator, type = 1):

        if (type == 4):
            query = 'INSERT INTO Annotations (slide, agreedClass, type) VALUES (%d,0,%d)' % (slideUID, type)
            self.execute(query)
            query = 'SELECT last_insert_rowid()'
            self.execute(query)
            annoId = self.fetchone()[0]

            self.insertCoordinates(np.array([[xpos_orig, ypos_orig,1]]), slideUID, annoId)
            self.annotations[annoId] = spotAnnotation(annoId, xpos_orig,ypos_orig, (type==4))

        else:
            query = 'INSERT INTO Annotations (slide, agreedClass, type) VALUES (%d,%d,%d)' % (slideUID,classID, type)
            self.execute(query)
            query = 'SELECT last_insert_rowid()'
            self.execute(query)
            annoId = self.fetchone()[0]

            self.insertCoordinates(np.array([[xpos_orig, ypos_orig,1]]), slideUID, annoId)
            self.execute(query)

            self.annotations[annoId] = spotAnnotation(annoId, xpos_orig,ypos_orig, (type==4))
            self.addAnnotationLabel(classId=classID, person=annotator, annoId=annoId)

        self.appendToMinMaxCoordsList(self.annotations[annoId])
        self.commit()
        return annoId

    def removeFileFromDatabase(self, fileUID:str):
        self.execute('DELETE FROM Annotations_label where annoID IN (SELECT uid FROM Annotations where slide == %d)' % fileUID)
        self.execute('DELETE FROM Annotations_coordinates where annoID IN (SELECT uid FROM Annotations where slide == %d)' % fileUID)
        self.execute('DELETE FROM Annotations where slide == %d' % fileUID)
        self.execute('DELETE FROM Slides where uid == %d' % fileUID)
        self.commit()

    def removeAnnotationLabel(self, labelIdx, annoIdx):
            q = 'DELETE FROM Annotations_label WHERE uid == %d' % labelIdx
            self.execute(q)
            self.annotations[annoIdx].removeLabel(labelIdx)
            self.commit()
            self.checkCommonAnnotation(annoIdx)

    def changeAnnotationID(self, annoId:int, newAnnoID:int):
            self.execute('SELECT COUNT(*) FROM Annotations where uid == (%d)' % newAnnoID)
            if (self.fetchone()[0] > 0):
                return False

            self.execute('UPDATE Annotations_label SET annoId = %d WHERE annoId == %d' % (newAnnoID,annoId))
            self.execute('UPDATE Annotations_coordinates SET annoId = %d WHERE annoId == %d' % (newAnnoID,annoId))
            self.execute('UPDATE Annotations SET uid= %d WHERE uid == %d ' % (newAnnoID,annoId))
            self.annotations[annoId].uid = newAnnoID
            self.annotations[newAnnoID] = self.annotations[annoId]
            self.annotations.pop(annoId)
            self.appendToMinMaxCoordsList(self.annotations[newAnnoID])
            self.commit()
            return True


    def removeAnnotation(self, annoId, onlyMarkDeleted:bool=True):
            if (onlyMarkDeleted):
                self.execute('UPDATE Annotations SET deleted=1 WHERE uid == '+str(annoId))
                self.annotations[annoId].deleted = 1
            else:
                self.execute('DELETE FROM Annotations_label WHERE annoId == %d' % annoId)
                self.execute('DELETE FROM Annotations_coordinates WHERE annoId == %d' % annoId)
                self.execute('DELETE FROM Annotations WHERE uid == '+str(annoId))
                self.annotations.pop(annoId)
            self.commit()
            

    def insertNewSlide(self,slidename:str,slidepath:str,uuid:str=""):
            if (len(slidepath.split(os.sep))>1):
                directory = slidepath.split(os.sep)[-2]
            else:
                directory = ''
            self.execute('INSERT INTO Slides (filename,directory,uuid) VALUES ("%s","%s", "%s")' % (slidename,directory,uuid))
            self.commit()


    def fetchall(self):
        if (self.isOpen()):
            return self.dbcur.fetchall()
        else:
            print('Warning: DB not opened for fetch.')

    def fetchone(self):
        if (self.isOpen()):
            return self.dbcur.fetchone()
        else:
            print('Warning: DB not opened for fetch.')

    def execute(self, query):
        if (self.isOpen()):
            return self.dbcur.execute(query)
        else:
            print('Warning: DB not opened.')

    def getDBname(self):
        if (self.dbOpened):
            return self.dbname
        else:
            return ''
    
    def getAnnotatorByID(self, id):
        if (id is None):
            return ''
        self.execute('SELECT name FROM Persons WHERE uid == %d' % id)
        fo = self.fetchone()
        if (fo is not None):
            return fo[0]
        else:
            return ''

    def getClassByID(self, id):
        try:
            self.execute('SELECT name FROM Classes WHERE uid == %d' % id)
            return self.fetchone()[0]
        except:
            return '-unknown-'+str(id)+'-'


    def getAllPersons(self):
        self.execute('SELECT name, uid FROM Persons ORDER BY uid')
        return self.fetchall()

    def getAllClasses(self):
        self.execute('SELECT name,uid FROM Classes ORDER BY uid')
        return self.fetchall()
    
    def renameClass(self, classID, name):
        self.execute('UPDATE Classes set name="%s" WHERE uid ==  %d' % (name, classID))
        self.commit()

    def commit(self):
        return self.db.commit()

    def countEntryPerClass(self, slideID = 0):
        retval = {'unknown' :  {'uid': 0, 'count_total':0, 'count_slide':0}}
        self.dbcur.execute('SELECT Classes.uid, COUNT(*), name FROM Annotations LEFT JOIN Classes on Classes.uid == Annotations.agreedClass GROUP BY Classes.uid')
        allClasses = self.dbcur.fetchall()
    
        classids = np.zeros(len(allClasses))        
        for idx,element in enumerate(allClasses):
                name = element[2] if element[2] is not None else 'unknown'
                
                retval[name] = {'uid': element[0], 'count_total':element[1], 'count_slide':0}
        uidToName = {uid:name for uid,_,name in allClasses}


        if (slideID is not None):

            self.dbcur.execute('SELECT Classes.uid, COUNT(*), name FROM Annotations LEFT JOIN Classes on Classes.uid == Annotations.agreedClass where slide==%d GROUP BY Classes.uid' % slideID)
            allClasses = self.dbcur.fetchall()
            
            for uid,cnt,name in allClasses:
                name = 'unknown' if name is None else name
                retval[name]['count_slide'] = cnt

        return retval


    def countEntries(self):
        self.dbcur.execute('SELECT COUNT(*) FROM Annotations')
        num1 = self.dbcur.fetchone()

        return num1[0]

    def fetchSpotAnnotation(self,entryId=0):
        self.dbcur.execute('SELECT coordinateX, coordinateY FROM Annotations_coordinates WHERE annoId ==  '+str(entryId))
        coords = self.dbcur.fetchone()
        
        class1,class2,person1,person2=None,None,None,None
        self.dbcur.execute('SELECT Classes.name FROM Annotations_label LEFT JOIN Classes on Annotations_label.class == Classes.uid WHERE Annotations_label.annoId ==  '+str(entryId))
        classes = self.dbcur.fetchall()

        self.dbcur.execute('SELECT Persons.name FROM Annotations_label LEFT JOIN Persons on Annotations_label.person == Persons.uid WHERE Annotations_label.annoId ==  '+str(entryId))
        persons = self.dbcur.fetchall()

        return coords, classes, persons

    def fetchAreaAnnotation(self,entryId=0):
        self.dbcur.execute('SELECT coordinateX, coordinateY FROM Annotations_coordinates WHERE annoId ==  '+str(entryId)+' ORDER BY Annotations_coordinates.orderIdx')
        coords1 = self.dbcur.fetchone()
        coords2 = self.dbcur.fetchone()
        
        class1,class2,person1,person2=None,None,None,None
        self.dbcur.execute('SELECT Classes.name FROM Annotations_label LEFT JOIN Classes on Annotations_label.class == Classes.uid WHERE Annotations_label.annoId ==  '+str(entryId))
        classes = self.dbcur.fetchall()

        self.dbcur.execute('SELECT Persons.name FROM Annotations_label LEFT JOIN Persons on Annotations_label.person == Persons.uid WHERE Annotations_label.annoId ==  '+str(entryId))
        persons = self.dbcur.fetchall()

        return coords1, coords2, classes, persons

    

    def create(self,dbfilename) -> bool:
 
        if (os.path.isfile(dbfilename)):
             # ok, remove old file
            os.remove(dbfilename)

        try:
            tempdb = sqlite3.connect(dbfilename)
        except sqlite3.OperationalError:
            return False

        tempcur = tempdb.cursor()

        tempcur.execute('CREATE TABLE `Annotations_label` ('
            '	`uid`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,'
            '	`person`	INTEGER,'
            '	`class`	INTEGER,'
            '	`annoId`	INTEGER'
            ');')
        
        tempcur.execute('CREATE TABLE `Annotations_coordinates` ('
            '`uid`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,'
            '`coordinateX`	INTEGER,'
            '`coordinateY`	INTEGER,'
            '`slide`	INTEGER,'
            '`annoId`	INTEGER,'
            '`orderIdx`	INTEGER'
            ');')

        tempcur.execute('CREATE TABLE `Annotations` ('
            '`uid`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,'
            '`slide`	INTEGER,'
           	'`guid`	TEXT,'
            f'`lastModified`	REAL DEFAULT {time.time()},'
         	'`deleted`	INTEGER DEFAULT 0,'
            '`type`	INTEGER,'
            '`agreedClass`	INTEGER'
            ');')

        tempcur.execute('CREATE TABLE `Classes` ('
            '`uid`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,'
            '`name`	TEXT'
            ');')
        
        tempcur.execute('CREATE TABLE `Persons` ('
            '`uid`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,'
            '`name`	TEXT'
            ');')

        tempcur.execute('CREATE TABLE `Slides` ('
            '`uid`	INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,'
            '`filename`	TEXT,'
            '`width`	INTEGER,'
            '`height`	INTEGER,'
            '`directory` TEXT,'
            '`uuid` TEXT' 
            ');')

        tempdb.commit()
        self.db = tempdb
        self.dbcur = self.db.cursor()
        self.dbcur.execute('PRAGMA user_version = 1')
        self.db.create_function("generate_uuid",0, generate_uuid)
        self.db.create_function("pycurrent_time",0, time.time)
        self.dbfilename = dbfilename
        self.dbcur.execute(self.databaseStructure['Log'].getCreateStatement())
        self.annotations = dict()
        self.dbname = os.path.basename(dbfilename)
        self.dbOpened=True
        self.generateMinMaxCoordsList()
        self.addTriggers()

        return self
