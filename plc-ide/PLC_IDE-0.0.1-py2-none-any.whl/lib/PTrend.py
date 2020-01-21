# -*- coding: utf-8 -*-
# %matplotlib inline
from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes
import matplotlib.pyplot as plt
import random




class PAxes:
    def __init__(self):
        self.axes = []
        pass

    def __del__(self):
        self.axes = []


    def add(self,name,label,vmin,vmax,loc):
        dc = {}
        dc['name'] = name
        dc['label'] = label
        dc['min'] = min(vmin,vmax)
        dc['max'] = max(vmin,vmax)
        dc['loc'] = loc
        dc['idx'] = len(self.axes)
        self.axes.append(dc)
        pass

    def get_axes_range(self,name):
        for a in self.axes:
            if a['name'] == name:
                return (a['min'],a['max'])

        return (0,100)

    def get_axes_id(self,name):
        for i in range(len(self.axes)):
            if self.axes[i]['name'] == name:
                return i

        return None

    def get_axes_name(self,idx):
        if idx >= 0 and idx < len(self.axes):
            return self.axes[idx]['name']
        else:
            return None

    def build_axes(self,fig,xlabel):
        _left = 0.3
        _right = 0.1
        _width = 0.2
        _height = 0.8

        par = []
        for i in range(len(self.axes)):
            # ax_cof = HostAxes(fig, [0.3, 0.1, 0.5, 0.8])  # 用[left, bottom, weight, height]的方式定义axes，0 <= l,b,w,h <= 1
            if i == 0:
                host = HostAxes(fig, [_left,_right,_width,_height])
            else:
                # ax_temp = ParasiteAxes(ax_cof, sharex=ax_cof)
                _p = ParasiteAxes(host, sharex=host)

                par.append(_p)

        # append axes : ax_cof.parasites.append(ax_temp)
        for _p in par:
            host.parasites.append(_p)

        host.axis['right'].set_visible(False)
        host.axis['top'].set_visible(False)
        host.set_xlabel(xlabel)
        host.set_ylabel(self.axes[0]['label'])

        _leftoffset = 0
        _rightoffset = 0
        for i in range(len(par)):
            _p = par[i]
            if i == 0:
                _p.axis['right'].set_visible(True)
                _p.axis['right'].major_ticklabels.set_visible(True)
                _p.axis['right'].label.set_visible(True)
            else:
                _axisline = _p.get_grid_helper().new_fixed_axis
                _loc = self.axes[i+1]['loc']
                if _loc == 'left':
                    _leftoffset -= 60
                    _offset = _leftoffset
                else:
                    _rightoffset += 60
                    _offset = _rightoffset
                _p.axis['right%d' % (i+1)] = _axisline(loc=_loc, axes=_p, offset=(_offset, 0))

            _p.set_ylabel(self.axes[i+1]['label'])

        fig.add_axes(host)


        axes = [host]
        axes.extend(par)
        return axes

    def get_axes_num(self):
        return len(self.axes)



class PLine:
    def __init__(self):
        self.lines = []
        pass

    def __del__(self):
        self.lines = []

    def add(self,name,axes,color):
        def tcolor(c):

            c = c.replace('(','')
            c = c.replace(')','')
            _rgba = c.split(',')
            _r = int(_rgba[0])
            _g = int(_rgba[1])
            _b = int(_rgba[2])

            if _r < 0:
                _r = 0

            if _g < 0:
                _g = 0

            if _b < 0:
                _b = 0

            if (_r+_g+_b) == 0:
                _r = random.randint(1,255)
                _g = random.randint(1,255)
                _b = random.randint(1,255)



            val = _r*0x10000 + _g*0x100 + _b
            t = hex(val)
            t = t.replace('0x','')
            t = t.zfill(6)
            return '#'+t



        dc = {}
        dc['name'] = name
        dc['axes'] = axes
        dc['color'] = tcolor(color)
        self.lines.append(dc)

    def get_curve_byidx(self,idx):
        idx = int(idx)
        if idx < 0 or idx >= len(self.lines):
            return None
        else:
            return self.lines[idx]

    def get_num(self):
        return len(self.lines)


class PTrend():
    def __init__(self,title,xlabel):
        self.title = title
        self.xlabel = xlabel
        self.objAxes = PAxes()
        self.objLine = PLine()
        pass


    def render_random(self,filename=''):
        if self.objLine.get_num() == 0 or self.objAxes.get_axes_num() == 0:
            return -1


        fig = plt.figure(1)


        ltaxes = self.objAxes.build_axes(fig,self.xlabel)

        xval = []
        for i in range(10):
            xval.append(i)

        for i in range(self.objLine.get_num()):
            _curve = self.objLine.get_curve_byidx(i)
            if _curve == None:
                return

            ax_id = self.objAxes.get_axes_id(_curve['axes'])
            ax_cp = ltaxes[ax_id]
            if ax_id == None:
                return

            _range = self.objAxes.get_axes_range(_curve['axes'])

            yval = []
            for i in range(10):
                # yval.append(random.randrange(_range[0],_range[1]))
                yval.append(random.random()*(_range[1] - _range[0]) + _range[0])
            # print yval
            curve_cp, = ax_cp.plot(xval, yval, label=_curve['name'],color=_curve['color'])


        for i in range(len(ltaxes)):
            _aname = self.objAxes.get_axes_name(i)
            _range = self.objAxes.get_axes_range(_aname)
            ltaxes[i].set_ylim(_range[0],_range[1])

        ltaxes[0].legend()

        if filename == '':
            # plt.show()
            fig.show()
        else:
            # plt.savefig(filename)
            fig.savefig(filename)

        fig.clear()
        del fig



    def append_axes(self,name,label,vmin,vmax,loc):
        self.objAxes.add(name,label,vmin,vmax,loc)
        pass

    def append_curve(self,name,axes,color):
        self.objLine.add(name,axes,color)
        pass


    def __del__(self):
        del self.objAxes
        del self.objLine