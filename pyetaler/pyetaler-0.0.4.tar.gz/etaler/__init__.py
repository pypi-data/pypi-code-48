import cppyy
import os

src_dir = os.path.dirname(os.path.realpath(__file__))
cppyy.load_reflection_info(os.path.join(src_dir, "etaler_rflx.so"))


from cppyy.gbl import et
from cppyy.gbl import std

# cppyy does not print reflections like ROOT does
# But Python doesn not allow overwriting an enum's __repr__
# So we supply one to cppyy
#FIXME: cppyy cannot find et::DType in C++ for some reason
#cppyy.cppdef("""
#namespace cling {
#std::string printValue(const et::DType* dtype) {
#    auto d = *dtype;
#    if(d == et::DType::Float)
#        return "Float";
#    else if(d == et::DType::Bool)
#        return "Bool";
#    else if(d == et::DType::Int)
#        return "Int";
#    else if(d == et::DType::Half)
#        return "Half";
#    return "Unknown";
#}
#}
#""")

# helper functions

def type_from_dtype(dtype):
    if dtype == et.DType.Bool:
        return bool
    elif dtype == et.DType.Int:
        return int
    elif dtype == et.DType.Float:
        return float
    elif dtype == et.DType.Half:
        return et.half
    else:
        raise ValueError("DType {} not recognized".format(dtype))

et.dtypeToType = type_from_dtype

def in_bound(idx: int, size: int):
    if idx is None:
        return True
    elif idx >= 0:
        return idx < size
    else:
        return -idx >= size

def is_iteratable(obj):
    try:
        it = iter(obj)
        return True
    except TypeError:
        return False

# Override the default __repr__ with Etaler's function
et.Shape.__repr__ = lambda self: cppyy.gbl.cling.printValue(self)
et.Tensor.__repr__ = lambda self: cppyy.gbl.cling.printValue(self)
et.half.__repr__ = lambda self: cppyy.gbl.cling.printValue(self)

# Override the default C++ ones/zeros for better pythonic function
# TODO: A better approach is to overrite et.Shape.__init__ to
# make it initalize pythonically
cpp_ones = et.ones
cpp_zeros = et.zeros
cpp_constant = et.constant

def pythonic_shape_func(shape, func, dtype=None) -> et.Tensor:
    shape_t = type(shape)
    if shape_t is tuple or shape_t is list:
        return func(shape, dtype)
    elif shape_t is int or shape_t is np.int or shape_t is np.int32:
        return pythonic_shape_func((shape, ), func)
    else:
        raise TypeError("Cannot run shape function with type {}".format(shape_t))
et.ones = lambda shape, dtype=None: pythonic_shape_func(shape, cpp_ones, dtype)
et.zeros = lambda shape, dtype=None: pythonic_shape_func(shape, cpp_zeros, dtype)
et.constant = lambda shape, val: pythonic_shape_func(shape, lambda s: cpp_constant(s. val))

def is_index_good(self, idx):
    if type(idx) is int:
        if in_bound(idx, self.size()) is False:
            raise IndexError("index {} it our of range".format(idx))
    elif in_bound(idx.stop, self.size()) is False:
        raise IndexError("Stop index {} is out of range".format(idx.stop))
    elif in_bound(idx.start, self.size()) is False:
        raise IndexError("Start index {} is out of range".format(idx.stop))
    elif idx.step == 0:
        raise IndexError("Cannot have step size of 0")
et.Shape.is_index_good = is_index_good

def shape_to_list(self: et.Shape):
    return [int(d) for d in self]
et.Shape.to_list = shape_to_list

# Override et.Shape's __getitem__ and __setitem__
def get_subshape(self: et.Shape, idx):
    self.is_index_good(idx)

    if type(idx) is int:
        if idx < 0:
            return self.data()[len(self) + idx]
        else:
            return self.data()[idx]
    elif type(idx) is not slice and type(idx) is not range:
        raise TypeError("Cannot index with type {}".format(type(idx)))
   
    # Unfortunatelly iterators doesn't work like in C++ :(
    start = idx.start if idx.start is not None else 0
    stop = idx.stop if idx.stop is not None else self.size()
    step = idx.step if idx.step is not None else 1
    res = et.Shape()
    for i in range(start, stop, step):
        res.push_back(self[i])
    return res

def set_subshape(self: et.Shape, idx, value):
    self.is_index_good(idx)
    idx = idx if type(idx) is not int else range(idx, idx+1, 1)

    rng = range(
            idx.start if idx.start is not None else 0,
            idx.stop if idx.stop is not None else self.size(),
            idx.step if idx.step is not None else 1) # incase idx is slice
    values = (value,) if is_iteratable(value) is False else value

    if len(rng) != len(values):
        raise ValueError('Cannot assign {} values into {} variables'.format(len(values), len(rng)))

    for i, j in enumerate(rng):
        self.data()[j] = values[i] if values[i] is not None else -1 # -1 is None in Etaler

et.Shape.__getitem__ = get_subshape
et.Shape.__setitem__ = set_subshape

# Override the __setitem__ and __getitem__ function of et.Tensor
# To allow Python style subscription
def get_tensor_view(self: et.Tensor, slices) -> et.Tensor:

    tup = None
    if type(slices) is int or type(slices) is range or type(slices) is slice:
        tup = (slices,)
    else:
        tup = slices

    rgs = et.IndexList(len(tup))
    shape = self.shape()
    for i, r in enumerate(tup):
        if type(r) is int:
            rgs[i] = r
        elif type(r) is range or type(r) is slice:
            start = std.nullopt if r.start is None else r.start
            stop = std.nullopt if r.stop is None else r.stop
            step = std.nullopt if r.step is None else r.step
            rgs[i] = et.Range(start, stop, step)
            # No need to check to out-of-bounds access. The C++ side does that
        else:
            raise TypeError("indices must be a int, range or slice")

    return self.view(rgs)

et.Tensor.__getitem__ = get_tensor_view
et.Tensor.__setitem__ = lambda self, slices, value: self.__getitem__(slices).assign(value)

# Override the default C++ item<T>() with a Python one
cpp_get_tensor_item = et.Tensor.item
def get_tensor_item(self: et.Tensor):
    return cpp_get_tensor_item[et.dtypeToType(self.dtype())](self)
et.Tensor.item = get_tensor_item

# Override the default C++ toHost<T> with a Python one
# TODO: Should the function return a list/np.array instead of a std.vector?
cpp_tensor_to_host = et.Tensor.toHost
def tensor_to_host(self: et.Tensor):
    uint8_t = cppyy.gbl.uint8_t
    if self.dtype() == et.DType.Bool:
        return cpp_tensor_to_host[uint8_t](self)
    return cpp_tensor_to_host[et.dtypeToType(self.dtype())](self)
et.Tensor.toHost = tensor_to_host

# Handle the misleading __bool__ function generated by cppyy
def tensor_trueness(self: et.Tensor) -> bool:
    if self.size() == 0:
        raise ValueError("The true-ness of a empty tensor is not defined.")
    elif self.size() > 1:
        raise  ValueError("The true-ness of a non-scalar is ambiguous. Please use any() or all()")
    if self.has_value() is False:
        return False
    return self.item() != 0 if self.dtype() == et.DType.Half else bool(self.item()) 

et.Tensor.__bool__ = tensor_trueness

# Implement our __len__ to match numpy's behaivour
et.Tensor.__len__ = lambda self: self.shape()[0] if self.has_value else 0

# interop with numpy conversion
try:
    import numpy as np
    def tensor_to_np(self: et.Tensor) -> np.array:
        vec = self.toHost()
        t = type_from_dtype(self.dtype())
        lst = [t(x) for x in vec]
        return np.array(lst).reshape(tuple(self.shape()))
    et.Tensor.numpy = tensor_to_np

    def tensor_tolist(self: et.Tensor) -> list:
        return tensor_to_np(self).tolist()
    et.Tensor.tolist = tensor_tolist

    def nptype_to_ettype(dtype):
        if dtype == np.int32 or dtype == np.int: #int is 64 bit, but anyway...
            return et.DType.Int32
        elif dtype == np.float32 or dtype == np.float:
            return et.DType.Float
        elif dtype == np.half: # np.float16 is np.half -> True
            return et.DType.Half
        elif dtype == np.bool:
            return et.DType.Bool        
        raise ValueError("numpy type {} cannot be mapped into a Etaler type".format(dtype))
    def tensor_from_numpy(array):
        # Try to convert to numpy array if the param is not one
        if type(array) is not np.ndarray:
            return tensor_from_numpy(np.array(array))
        et_dtype = nptype_to_ettype(array.dtype)
        cpp_type = type_from_dtype(et_dtype)
        vec = std.vector[cpp_type](array.size)
        #TODO: We need a faster way to fill the vector
        for i, v in enumerate(np.nditer(array)):
            vec[i] = cpp_type(v)
        return et.Tensor(et.Shape(array.shape), vec.data())
    et.Tensor.from_numpy = staticmethod(tensor_from_numpy)


except ImportError:
    pass


