import datetime

class PlacaEcuador:
    #exceptions
    initException = ValueError("No se ingresó una placa válida")
    dateException = ValueError("No se ingresó una fecha válida, el formato es dd-mm-AA")
    timeException = ValueError("No se ingresó una hora válida, el formato es de 24h, ej: 14:55")
    lawException = ValueError("No se ingresó correctamente el tipo de ley a aplicar (antigua o nueva)")

    #init method
    def __init__(self,placaCode):
        #toUpperCase
        placaCode=placaCode.upper()

        #validation
        if placaCode[:3].isalpha() and placaCode[0]!="D" and placaCode[0]!="F" and placaCode[0]!="Ñ" and placaCode[3:].isdigit() and len(placaCode[3:])>=3 and len(placaCode[3:])<=4 :
            self.placaString=placaCode[:3].upper()
            self.placaInt=placaCode[3:]
        else:
            raise PlacaEcuador.initException
    
    #method to check range in date
    @staticmethod
    def time_in_range(start, end, x):
        if start <= end:
            return start <= x <= end
        else:
            return start <= x or x <= end

    #can be on the road? (true or false)
    def canBeOnTheRoad(self,date,time,*law):
        #date validation
        if date[0:2].isdigit() and date[3:5].isdigit() and date[6:10].isdigit() and len(date)==10:
            dd=int(date[0:2])
            mm=int(date[3:5])
            yy=int(date[6:10])
            day=datetime.datetime(yy, mm, dd, 0, 0, 0, 0)
        else:
            raise PlacaEcuador.dateException

        #time validation
        if time[0:2].isdigit() and time[3:5].isdigit() and len(time)==5:
            hours=int(time[0:2])
            minutes=int(time[3:5])
        else:
            raise PlacaEcuador.timeException

        #ranges old and new
        horarioAntiguoMananaInicio = datetime.time(7, 0, 0)
        horarioAntiguoMananaFin = datetime.time(9, 30, 0)
        horarioAntiguoTardeInicio = datetime.time(16, 0, 0)
        horarioAntiguoTardeFin = datetime.time(19, 30, 0)
        horarioNuevoInicio = datetime.time(5, 0, 0)
        horarioNuevoFin = datetime.time(20, 0, 0)
    
        #check if in range
        isTimeInRageAntiguoManana=PlacaEcuador.time_in_range(horarioAntiguoMananaInicio,
            horarioAntiguoMananaFin,
            datetime.time(hours,minutes, 0))
        isTimeInRageAntiguoTarde=PlacaEcuador.time_in_range(horarioAntiguoTardeInicio,
            horarioAntiguoTardeFin,
            datetime.time(hours, minutes, 0))
        isTimeInRageNuevo=PlacaEcuador.time_in_range(horarioNuevoInicio,
            horarioNuevoFin, datetime.time(hours,
            minutes, 0))

        #check law (antigua or nueva)
        if not law:
            law="ANTIGUA"
        else:
            law=law[0]
            law=law.upper()
        if law=="ANTIGUA":
            isTimeInRange=isTimeInRageAntiguoManana+isTimeInRageAntiguoTarde
        elif law=="NUEVA":
            isTimeInRange=isTimeInRageNuevo
        else:
            raise PlacaEcuador.lawException

        #final - check if can be on the road
        if isTimeInRange:
            if day.weekday()==0 and (self.placaInt[-1]=="1" or self.placaInt[-1]=="2"):
                return False
            elif day.weekday()==0 and (self.placaInt[-1]=="1" or self.placaInt[-1]=="2"):
                return False
            elif day.weekday()==1 and (self.placaInt[-1]=="3" or self.placaInt[-1]=="4"):
                return False
            elif day.weekday()==2 and (self.placaInt[-1]=="5" or self.placaInt[-1]=="6"):
                return False
            elif day.weekday()==3 and (self.placaInt[-1]=="7" or self.placaInt[-1]=="8"):
                return False
            elif day.weekday()==4 and (self.placaInt[-1]=="9" or self.placaInt[-1]=="0"):
                return False
            else:
                return True
        else:
            return True