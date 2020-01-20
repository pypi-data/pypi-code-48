'''
Created on Feb 20, 2019

@author: reynolds
'''

import os, sys, time

class simulator(object):
    ''' A data simulator class for simulating sensors'''

    def __init__(self):
        ''' Constructor '''
        super().__init__()
        self.reset()
        
    def reset(self):
        ''' resets the simulator '''
        self._len = 0
        self._i = -1
        self._error = False
        self._msgs = []
        self._dt = []
        self._port = None
        self._addr = None
        self._run = False
        
    def set_port(self,port):
        self._port = port
        
    def set_address(self,addr=('127.0.0.1',7654)):
        self._addr = addr
            
    def read(self,filename):
        ''' reads the file and parses the messages '''
        self.reset()
        print('Reading %s ... ' % filename,end='')
        if not os.path.exists(filename):
            self._error = True
            print('Error. File does not exist.')
            return False
        
    def current(self):
        ''' returns the current message number '''
        return self._i
    
    def length(self):
        ''' returns the total number of messages '''
        return self._len
        
    def getNext(self):
        ''' gets the next message '''
        self._i += 1
        if self._i == self._len: self._i = 0
        try:
            return (self._msgs[self._i],self._dt[self._i])
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno))
            self._i = 0
            return (self._msgs[self._i],self._dt[self._i])
        
    def hasNext(self):
        ''' returns whether there is another message '''
        return self._i < self._len
        
    def didError(self):
        ''' returns whether an error did occur '''
        return self._error
    
    def writeNext(self,port=None,addr=None):
        ''' writes the message to the udp port '''
        try:
            _m,_t = self.getNext()
            port.sendto(_m,addr)
            time.sleep(_t)
        except Exception as e:
            print(str(e),addr,port)
            
    def stop(self):
        self._run = False