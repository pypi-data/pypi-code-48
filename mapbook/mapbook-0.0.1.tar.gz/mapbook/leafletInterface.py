import re 
import json
from uuid import uuid4
from jinja2 import Template
from IPython.display import display, Javascript, HTML, clear_output

import logging
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # for debug
# logger.setLevel(logging.INFO)  # for user
logger.handlers = []
ch = logging.StreamHandler()        
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)        

#-----------------
# utiles
#-----------------
def dequote_value_of_key(json_str, keys):
    regex = r"((?<![\\])[\"])((?:.(?!(?<![\\])\1))*.?)\1"
    matches = re.finditer(regex, json_str, re.MULTILINE)
    dequote_flag = False
    dequote_keys = set(keys)
    for matchNum, match in enumerate(matches, start=1):
        # print(match.group(), match.start(), match.end())
        if dequote_flag:
            s = match.group()[1:-1]
            l = len(s)
            i, j = match.start(), match.end()
            s = s.replace('\\n','').replace('\\"', '"').replace("\'", "'")
            l = l - len(s)
            json_str = json_str[:i] + s + ' '*(l+2) + json_str[j:]
            dequote_flag = False
        if match.group()[1:-1] in dequote_keys:
            dequote_flag = True
    return json_str

def show(pyDiv, obj):
    plotly_templ = Template("""{
        var opts = {{ options }};
        require(['plotly', 'singleton'], 
        function (Plotly, singleton) {
          var mblut = singleton().lut;
          var div_id = "{{ div_id }}";
          mblut[div_id] = 'plotly_' + div_id;
          // Plotly.plot("{{ div_id }}", opts);
          Plotly.newPlot(div_id, opts.data, opts.layout, {responsive: true});
        }); 
    }""")
    handsontable_templ = Template("""{
        require(['handsontable', 'singleton'],
        function (Handsontable, singleton) {
          var mblut = singleton().lut;
          var div_id = "{{ div_id }}";
          mblut[div_id] = 'handsontable_' + div_id;
          var container = document.getElementById(div_id);
          fetch("{{ fjson }}")
            .then(
              function(response) {
                if (response.status !== 200) {
                  console.log("Fail to load '{{ fjson }}'. Status Code: " +
                    response.status);
                  return;
                }
                // Examine the text in the response
                response.json().then(function(data) {
                  console.log(data);
                  var hot = new Handsontable(container, {
                      data: data.data,
                      rowHeaders: data.index,
                      colHeaders: data.columns,
                      filters: true,
                      dropdownMenu: true,
                  });
                  mblut[mblut[div_id]] = hot;
                });
              })
            .catch(function(err) {
              console.log('Fetch Error :-S', err);
            });
        });
    }""")    
    n = '.'.join([obj.__module__, obj.__class__.__name__])
    if n == 'plotly.graph_objs._figurewidget.FigureWidget' \
    or n == 'plotly.graph_objs._figure.Figure':
        options = obj.to_json()
        js_str = plotly_templ.render(div_id=pyDiv.pyId, options=options)
    elif n == 'pandas.core.frame.DataFrame':
        nbytes = obj.memory_usage(index=True)
        # if nbytes>2**12: # 4.096KB
        fname = 'test_hot.json'
        obj.to_json(path_or_buf=fname, orient='split')
        js_str = handsontable_templ.render(div_id=pyDiv.pyId, fjson=fname)
    else:
        raise Exception('mapbook show function not support type:', type(obj))
    logger.debug(js_str)
    display(Javascript(js_str))

#-----------------
# base class
#-----------------

class node:
    def __init__(self):
        self.pyId = self.__class__.__name__ + '_' + uuid4().hex

#-----------------
# map sync
#-----------------

class mapSync(node):
    def __init__(self, maps=[]):
        super().__init__()
        sync_init_templ = Template("""{
        require(['mapSync', 'singleton'], 
          function (mapSync, singleton) {
              var mblut = singleton().lut;
              mblut["{{ pyId }}"] = mapSync();
          });
        }""")
        #
        js_str=sync_init_templ.render(pyId=self.pyId)
        logger.debug(js_str)
        display(Javascript(js_str))
        maps = set(maps)
        if len(maps)<2:
            self.maps = maps
        else:
            self.maps = set()
            self.sync(maps)

    def sync(self, maps=None):
        sync_templ = Template("""{
        require(['singleton'], 
          function (singleton) {
              var mblut = singleton().lut;
              mblut["{{ pyId }}"].sync([{{ js_maps }}]);
          });
        }""")
        #
        addMaps = []
        if maps is None:
            return
        else:
            addMaps = set(maps) - self.maps
        if len(self.maps)==0 and len(addMaps)==1:
            # one map only will not do sync
            return
        if len(addMaps)>0:
          js_maps = ', '.join(['mblut["%s"]'%map.pyId for map in addMaps])
          js_str=sync_templ.render(pyId=self.pyId, js_maps=js_maps)
          logger.debug(js_str)
          display(Javascript(js_str))
          self.maps = self.maps | addMaps

    def unsync(self, maps=[]):
        delMaps = self.maps & set(maps)
        if len(delMaps)==0:
            return
        if len(self.maps)-len(delMaps) == 1:
            delMaps = self.maps
        self.maps = self.maps - delMaps
        unsync_templ = Template("""{
        require(['singleton'], 
          function (singleton) {
              var mblut = singleton().lut;
              mblut["{{ pyId }}"].unsync([{{ js_maps }}]);
          });
        }""")
        #
        js_maps = ', '.join(['mblut["%s"]'%map.pyId for map in delMaps])
        js_str=unsync_templ.render(pyId=self.pyId, js_maps=js_maps)
        logger.debug(js_str)
        display(Javascript(js_str))

#--------------------------------
# create div using golden-layer
#--------------------------------

class DivWindow(node):
    tot_wins = 0

    div_templ = Template("""{
        var div_opts = {{ options }};
        require(['mapbookDiv'], 
        function (mapbookDiv) {
            var mbdiv = mapbookDiv(div_opts);
        }); 
    }""")

    def __init__(self, **options):
        super().__init__()
        DivWindow.tot_wins = DivWindow.tot_wins + 1
        options['id'] = self.pyId
        if 'title' not in options:
            options['title'] = 'no title'
        options['title'] = "win{}: {}".format(DivWindow.tot_wins, options['title'])
        js_str = DivWindow.div_templ.render(options=json.dumps(options))
        logger.debug(js_str)
        display(Javascript(js_str))

#-----------------
# map
#-----------------

class Map(node):
    map_templ = Template("""{
        var map_opts = {{ options }};
        require(['mapbookMap'], 
        function (mapbookMap) {
          var mbdiv = mapbookMap("{{ div_id }}", map_opts);
        }); 
    }""")
    
    def __init__(self, pyDiv, **options):
        super().__init__()
        options['id'] = self.pyId
        options = json.dumps(options)
        options = dequote_value_of_key(options, ["crs"])
        js_str = Map.map_templ.render(div_id=pyDiv.pyId, options=options)
        logger.debug(js_str)
        display(Javascript(js_str))

    def setView(self, latLng, zoom=None):
        options = {"center": latLng}
        if zoom is not None:
          options["zoom"] = zoom
        setView_templ = Template("""{
          require(['leaflet', 'singleton'], 
          function (L, singleton) {
            // drawGroupLayer, drawControl, options
            var mblut = singleton().lut;
            var map = mblut["{{ map_id }}"]
            map.setView({{ options.center }}{% if 'zoom' in options%}, {{ options.zoom }}{% endif %}); 
          });         
        }""")        
        js_str = setView_templ.render(map_id=self.pyId, options=options)
        logger.debug(js_str)
        display(Javascript(js_str))
        return

    def addDraw(self):
        #--- note ---
        # this is a temperal solution for leaflet.draw plugin
        # no draw option can be set at moment.
        if hasattr(self, 'drawGroupId'):
          print('only one draw plugin allowed. No further action.')
        draw_templ = Template("""{
          require(['leaflet', 'singleton'], 
          function (L, singleton) {
            // drawGroupLayer, drawControl, options
            var mblut = singleton().lut;
            var map = mblut["{{ map_id }}"]
            var drawGroupLayer = L.featureGroup().addTo(map);
            mblut["{{ drawGroup_id }}"] = drawGroupLayer;
            var options = {
                edit: {
                    featureGroup: drawGroupLayer,
                    poly: {
                        allowIntersection: false
                    }
                },
                draw: {
                    polygon: {
                        allowIntersection: false,
                        showArea: true
                    }
                }
            };
            var drawControl = new L.Control.Draw(options);
            map.addControl(drawControl);
            map.on(L.Draw.Event.CREATED, function (event) {
                var layer = event.layer;
                drawGroupLayer.addLayer(layer);
            });
          });         
        }""")
        self.drawGroupId = self.pyId + '_drawGroup'
        js_str = draw_templ.render(map_id=self.pyId, drawGroup_id=self.drawGroupId)
        logger.debug(js_str)
        display(Javascript(js_str))
        return

    def DrawnLayertoGeoJSON(self, pyVarName, precision=6):
        #--- note ---
        # this is a temperal solution for leaflet.draw plugin
        draw_templ = Template("""{
          require(['leaflet', 'singleton'],
          function (L, singleton) {
            // drawGroupLayer, drawControl, options
            var mblut = singleton().lut;
            var drawGroupLayer = mblut["{{ drawGroup_id }}"];
            var geoms = drawGroupLayer.toGeoJSON({{ precision }});
            var py_code = "{{ varName }}='''" + JSON.stringify(geoms) + "'''";
            console.log(py_code);
            IPython.notebook.kernel.execute(py_code);
          });
        }""")
        js_str = draw_templ.render(drawGroup_id=self.drawGroupId, varName=pyVarName, precision=precision)
        logger.debug(js_str)
        display(Javascript(js_str))
        logger.info('The geojson from drawn layer is loaded in python variable `{}`'.format(pyVarName))
        
#-----------------
# layer and sub
#-----------------

class Layer(node):
    def addTo(self, map):
        self.map = map
        addTo_tmpl = Template("""{
          require(['mapbookAddTo'], 
          function (mapbookAddTo) {
              mapbookAddTo("{{ lay_id }}", "{{ map_id}}");
          });
        }""")
        js_str = addTo_tmpl.render(map_id=map.pyId, lay_id=self.pyId)
        logger.debug(js_str)
        display(Javascript(js_str))
        return

    def remove(self):
        self.removeFrom(self.map)
        return

    def removeFrom(self, map):
        removeFrom_tmpl = Template("""{
          require(['mapbookRemoveFrom'], 
          function (mapbookRemoveFrom) {
              mapbookRemoveFrom("{{ lay_id }}", "{{ map_id}}");
          });
        }""")
        js_str = removeFrom_tmpl.render(map_id=map.pyId, lay_id=self.pyId)
        logger.debug(js_str)
        display(Javascript(js_str))
        self.map = None
        return

class imageOverlay(Layer):
    imageOverlay_templ = Template("""{      
        var url = "{{ imageUrl }}";
        var bounds = {{ bounds }};
        var lay_opts = {{ options }};

        require(['mapbookImageOverlay'], 
        function (mapbookImageOverlay) {
            var mbdiv = mapbookImageOverlay(url, bounds, lay_opts);
        });     
    }""")

    def __init__(self, imageUrl, bounds, **options):
        super().__init__()
        self.map = None
        options['id'] = self.pyId
        js_str = imageOverlay.imageOverlay_templ.render(imageUrl=imageUrl, bounds=json.dumps(bounds), options=json.dumps(options))
        logger.debug(js_str)
        display(Javascript(js_str))

class tileLayer(Layer):
    tileLayer_templ = Template("""{
        var url = "{{ urlTemplate }}";
        var lay_opts = {{ options }};

        require(['mapbookTileLayer'], 
        function (mapbookTileLayer) {
            var mbdiv = mapbookTileLayer(url, lay_opts);
        });     
    }""")

    def __init__(self, urlTemplate, **options):
        super().__init__()
        options['id'] = self.pyId;
        self.map = None
        js_str = tileLayer.tileLayer_templ.render(urlTemplate=urlTemplate, options=json.dumps(options))
        logger.debug(js_str)
        display(Javascript(js_str))

class GeoJSON(Layer):
    geojson_templ = Template("""{
        var data = {{ geopandasData }};
        var lay_opts = {{ options }};

        require(['mapbookGeoJSON'],
        function (mapbookGeoJSON) {
            var mbdiv = mapbookGeoJSON(data, lay_opts);
        });        
    }""")

    def __init__(self, geopandasData, **options):
        super().__init__()
        options['id'] = self.pyId;
        self.map = None
        if isinstance(geopandasData, str):
            data = geopandasData
        else:
            data = geopandasData.to_json()
        options=json.dumps(options)
        options = dequote_value_of_key(options, ["style", "onEachFeature", "filter"])      
        js_str = GeoJSON.geojson_templ.render(geopandasData=data, options=options, lay_id=self.pyId)
        logger.debug(js_str)
        display(Javascript(js_str))

class vectorGrid(Layer):
    vectorGrid_templ = Template("""{
        var data = {{ geopandasData }};
        var lay_opts = {{ options }};

        require(['mapbookVectorGrid'],
        function (mapbookVectorGrid) {
            var mbdiv = mapbookVectorGrid(data, lay_opts);
        });
    }""")

    def __init__(self, geopandasData, **options):
        super().__init__()
        options['id'] = self.pyId;
        self.map = None
        if isinstance(geopandasData, str):
            data = geopandasData
        else:
            data = geopandasData.to_json()
        options = json.dumps(options)
        options = dequote_value_of_key(options, ["rendererFactory", "sliced"])
        js_str = vectorGrid.vectorGrid_templ.render(geopandasData=data, options=options)
        logger.debug(js_str)
        display(Javascript(js_str))

#-----------------
# control and sub
#-----------------

#class Control(Layer):
#    pass

class layersControl(Layer):
    def __init__(self):
        super().__init__()

class coordinatesControl(Layer):
    coordinatesControl_templ = Template("""{
        var ctrl_opts = {{ options }};
        require(['mapbookCoordCtrl'],
        function (mapbookCoordCtrl) {
            var coordCtrl = mapbookCoordCtrl(ctrl_opts);
        });
    }""")
    def __init__(self, **options):
        super().__init__()
        options['id'] = self.pyId;        
        js_str = coordinatesControl.coordinatesControl_templ.render(options=json.dumps(options))
        logger.debug(js_str)
        display(Javascript(js_str))

  
