import CADETMatch.util as util
import CADETMatch.score as score
import scipy.stats
import numpy
import numpy.linalg
from addict import Dict
import CADETMatch.smoothing as smoothing
import multiprocessing

name = "DextranShape"

def get_settings(feature):
    settings = Dict()
    settings.adaptive = True
    settings.badScore = 0
    settings.meta_mask = True
    settings.count = 2
    return settings

def run(sim_data, feature):
    "special score designed for dextran. This looks at only the front side of the peak up to the maximum slope and pins a value at the elbow in addition to the top"
    sim_time_values, sim_data_values = util.get_times_values(sim_data['simulation'], feature)

    exp_time_zero = feature['exp_time_zero']
    exp_data_zero = feature['exp_data_zero']
    
    sim_spline, sim_data_zero_sse = cut_front(sim_time_values, sim_data_values, 
                                             feature['min_value_front'], feature['max_value_front'],
                                             feature['critical_frequency'], feature['smoothing_factor'])

    pearson, diff_time = score.pearson_spline_fun(exp_time_zero, exp_data_zero, sim_spline)

    exp_data_zero_sse = feature['exp_data_zero_sse']

    temp = [pearson,
            feature['offsetTimeFunction'](numpy.abs(diff_time)),
            ]

    data = (temp, util.sse(sim_data_zero_sse, exp_data_zero_sse), len(sim_data_zero_sse), 
            sim_time_values, sim_data_zero_sse, exp_data_zero_sse, [1.0 - i for i in temp])

    return data

def setup(sim, feature, selectedTimes, selectedValues, CV_time, abstol, cache):
    temp = {}
    #change the stop point to be where the max positive slope is along the searched interval
    name = '%s_%s' % (sim.root.experiment_name,   feature['name'])
    exp_time_zero, exp_data_zero, exp_data_zero_sse, min_time, min_value, max_time, max_value, s, crit_fs = cut_front_find(selectedTimes, selectedValues, name, cache)

    multiprocessing.get_logger().info("Dextran %s  start: %s   stop: %s  max value: %s", name, 
                                      min_time, max_time, max_value)

    temp['min_time'] = feature['start']
    temp['max_time'] = feature['stop']
    
    temp['min_time_front'] = min_time
    temp['min_value_front'] = min_value
    temp['max_time_front'] = max_time
    temp['max_value_front'] = max_value

    temp['exp_time_zero'] = exp_time_zero
    temp['exp_data_zero'] = exp_data_zero
    temp['exp_data_zero_sse'] = exp_data_zero_sse

    decay = feature.get('decay', 1)

    if decay:
        temp['offsetTimeFunction'] = score.time_function_cv(CV_time, selectedTimes, max_time)
    else:
        temp['offsetTimeFunction'] = score.time_function_decay_cv(CV_time, selectedTimes, max_time)

    temp['peak_max'] = max_value
    temp['smoothing_factor'] = s
    temp['critical_frequency'] = crit_fs
    return temp

def headers(experimentName, feature):
    name = "%s_%s" % (experimentName, feature['name'])
    temp = ["%s_Shape" % name, 
            "%s_Time" % name,
            ]
    return temp

def cut_front_find(times, values, name, cache):
    s, crit_fs = smoothing.find_smoothing_factors(times, values, name, cache)
    values_der = smoothing.smooth_data_derivative(times, values, crit_fs, s)

    smooth_value = smoothing.smooth_data(times, values, crit_fs, s)
    
    spline_der = scipy.interpolate.InterpolatedUnivariateSpline(times, values_der, ext=1)
    spline = scipy.interpolate.InterpolatedUnivariateSpline(times, smooth_value, ext=1)

    min_time, min_value, max_time, max_value = score.find_cuts(times, smooth_value, spline, spline_der)
    
    #resample to 100 points/second
    needed_points = int( (times[-1] - times[0]) * 100)
    
    new_times = numpy.linspace(times[0], times[-1], needed_points)
    new_values = spline(new_times)

    exp_data_zero_sse, exp_min_time, exp_min_value, exp_max_time, exp_max_value = score.cut_zero(times, smooth_value, min_value, max_value)

    if exp_min_time is not None:
        min_time = exp_min_time
        min_value = exp_min_value
        max_time = exp_max_time
        max_value = exp_max_value

    exp_data_zero, _, _, _, _ = score.cut_zero(new_times, new_values, min_value, max_value)    
    
    return (new_times, exp_data_zero, exp_data_zero_sse, 
        min_time, min_value, max_time, max_value, s, crit_fs)

def cut_front(times, values, min_value, max_value, crit_fs, s):
    max_index = numpy.argmax(values >= max_value)
    
    if max_index == 0:
        #no point high enough was found so use the highest point
        s, crit_fs = smoothing.find_smoothing_factors(times, values, None, None)
        max_index = numpy.argmax(values)
        max_value = values[max_index]
    
    max_time = times[max_index]

    smooth_value = smoothing.smooth_data(times, values, crit_fs, s)

    spline = scipy.interpolate.InterpolatedUnivariateSpline(times, smooth_value, ext=1)
    
    def goal(time):
        return (spline(time)-max_value)**2
    
    result = scipy.optimize.minimize(goal, max_time, method='powell', tol=1e-10)
    
    max_time = float(result.x)
    max_index = max(numpy.argmax(values >= max_value), max_index)

    min_index = numpy.argmax(values[:max_index] >= min_value)
    min_time = times[min_index]
    
    def goal(time):
        if time > max_time:
            #don't search to the right of the max_time for a lower value
            return 1e10
        return (spline(time)-min_value)**2
    
    result = scipy.optimize.minimize(goal, min_time, method='powell', tol=1e-10)
    
    min_time = float(result.x)

    needed_points = int( (max_time - min_time) * 10)
    new_times_spline = numpy.linspace(min_time, max_time, needed_points)
    new_values_spline = spline(new_times_spline)
    
    spline = scipy.interpolate.InterpolatedUnivariateSpline(new_times_spline, new_values_spline, ext=1)
    
    return spline, score.cut_zero(times, smooth_value, min_value, max_value)[0]