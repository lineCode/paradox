from enum import Enum
import numpy


SymbolCategory = Enum('SymbolCategory', ('variable', 'constant'))


class Symbol:
    def __init__(self, value=None, name: str=None, operator=None, inputs=None, category: SymbolCategory=None):
        self.__name = None
        self.__input = []
        self.__operator = None
        self.__output = []
        self.__value = None
        self.__scala = False
        self.__category = None
        self.init(value, name, operator, inputs, category)

    def init(self, value=None, name: str=None, operator=None, inputs=None, category: SymbolCategory=None):
        if isinstance(value, Symbol):
            self.name = value.name
            self.value = value.value
            for _input in value.input:
                self.__add_input(_input.clone())
            self.__set_operator(value.__operator)
            for _output in value.output:
                self.__add_output(_output.clone())
            self.__set_category(value.category)
        else:
            self.__set_value(value)
            self.arithmetic_compute(operator, inputs)
            self.__set_category(category)
            self.__set_name(name)

    def __repr__(self):
        if self.__operator is None:
            return self.__name
        else:
            if self.__operator.operator_sign is None:
                arguments = list(map(str, self.input))
                arguments += ['{}={}'.format(k, '\'' + v + '\'' if isinstance(v, str) else v) for k, v in self.__operator.arguments.items()]
                return '{}({})'.format(self.__operator.__class__.__name__, ', '.join(arguments))
            else:
                if len(self.input) < 2:
                    return '({}{})'.format(self.__operator.operator_sign, self.input[0])
                else:
                    return '({} {} {})'.format(self.input[0], self.__operator.operator_sign, self.input[1])

    def __str__(self):
        return self.__repr__()

    def __get_name(self):
        return self.__name

    def __set_name(self, name: str):
        if name is None:
            if self.__value is None:
                self.__name = self.__class__.__name__
            else:
                if self.is_scala():
                    self.__name = str(self.__value)
                else:
                    self.__name = self.__class__.__name__
        else:
            self.__name = name

    name = property(__get_name, __set_name)

    def __get_category(self):
        return self.__category

    def __set_category(self, category: SymbolCategory):
        if category is None:
            if self.__category is None:
                self.__category = SymbolCategory.variable
        else:
            if category == SymbolCategory.constant and self.__value is None:
                raise ValueError('Constant Symbol must have value.')
            else:
                self.__category = category

    category = property(__get_category, __set_category)

    def __get_value(self):
        return self.__value

    def __set_value(self, tensor):
        if tensor is not None:
            if self.__category == SymbolCategory.constant:
                raise ValueError('Can not change value for Constant')
            else:
                self.__value = numpy.array(tensor, dtype=float)
                self.__scala = len(self.value.shape) == 0

    value = property(__get_value, __set_value)

    def __get_operator(self):
        return self.__operator

    def __set_operator(self, operator):
        from paradox.kernel.operator import Operator
        if operator is not None:
            if isinstance(operator, Operator):
                self.__operator = operator
            else:
                raise ValueError('Operator must be Operator class.')

    operator = property(__get_operator, __set_operator)

    def __get_input(self):
        return self.__input

    input = property(__get_input)

    def __add_input(self, symbol):
        if isinstance(symbol, Symbol):
            self.__input.append(symbol)
        else:
            raise ValueError('Input must be Symbol class.')

    def __remove_input(self, symbol):
        new_input = []
        for o in self.__input:
            if hash(o) != hash(symbol):
                new_input.append(o)
        self.__input = new_input

    def __get_output(self):
        return self.__output

    output = property(__get_output)

    def __add_output(self, symbol):
        if isinstance(symbol, Symbol):
            self.__output.append(symbol)
        else:
            raise ValueError('Output must be Symbol class.')

    def __remove_output(self, symbol):
        new_output = []
        for o in self.__output:
            if hash(o) != hash(symbol):
                new_output.append(o)
        self.__output = new_output

    def arithmetic_compute(self, operator, inputs):
        if operator is not None and inputs:
            self.__set_operator(operator)
            inputs_count = operator.inputs_count
            if inputs_count is None:
                inputs_count = len(inputs)
            self.__input = []
            self.__scala = True
            for symbol in inputs[:inputs_count]:
                if isinstance(symbol, Symbol):
                    if not symbol.is_scala():
                        self.__scala = False
                    self.__add_input(symbol)
                    symbol.__add_output(self)
                else:
                    raise ValueError('Input must be Symbol class.')

    def clone(self):
        clone_symbol = Symbol()
        clone_symbol.name = self.name
        clone_symbol.value = self.value
        for _input in self.input:
            clone_symbol.__add_input(_input.clone())
        clone_symbol.__set_operator(self.__operator)
        for _output in self.output:
            clone_symbol.__add_output(_output.clone())
        clone_symbol.__set_category(self.__category)
        return clone_symbol

    def clear_input(self):
        for symbol in set(self.__input):
            symbol.__remove_output(self)
        self.__input = []

    def clear_output(self):
        for symbol in set(self.__output):
            symbol.__remove_input(self)
        self.__output = []

    def clear_operator(self):
        self.clear_input()
        self.__operator = None

    def destroy(self):
        self.clear_input()
        self.clear_output()
        self.__output = []
        self.__value = None
        self.__operator = None

    def rebuild_name(self):
        self.__name = None
        self.__set_name(None)

    def is_scala(self):
        return self.__scala

    def is_constant(self):
        return self.__category == SymbolCategory.constant

    def is_variable(self):
        return self.__category == SymbolCategory.variable

    def __hash__(self):
        return id(self)

    def __neg__(self):
        return negative(self)

    def __add__(self, other):
        return plus(self, other)

    def __radd__(self, other):
        return plus(other, self)

    def __sub__(self, other):
        return subtract(self, other)

    def __rsub__(self, other):
        return subtract(other, self)

    def __mul__(self, other):
        return multiply(self, other)

    def __rmul__(self, other):
        return multiply(other, self)

    def __truediv__(self, other):
        return divide(self, other)

    def __rtruediv__(self, other):
        return divide(other, self)

    def __matmul__(self, other):
        return matrix_multiply(self, other)

    def __rmatmul__(self, other):
        return matrix_multiply(other, self)

    def __pow__(self, exponent):
        return power(self, exponent)

    def __rpow__(self, other):
        return power(other, self)

    def __eq__(self, other):
        return equal(self, other)

    def __lt__(self, other):
        return less(self, other)

    def __le__(self, other):
        return less_equal(self, other)

    def __gt__(self, other):
        return greater(self, other)

    def __ge__(self, other):
        return greater_equal(self, other)

    def __getitem__(self, item):
        return slice_select(self, item)


class Constant(Symbol):
    def __init__(self, value=None, name: str=None, operator=None, inputs=None):
        Symbol.__init__(self)
        self.init(value, name, operator, inputs, SymbolCategory.constant)


class Variable(Symbol):
    def __init__(self, value=None, name: str=None, operator=None, inputs=None):
        Symbol.__init__(self)
        self.init(value, name, operator, inputs, SymbolCategory.variable)


def as_symbol(thing):
    if isinstance(thing, Symbol):
        return thing
    else:
        return Constant(thing)


def as_symbols(things):
    return list(map(as_symbol, things))


def negative(a):
    from paradox.kernel.operator import Negative
    return Symbol(operator=Negative(), inputs=as_symbols([a]))


def absolute(a):
    from paradox.kernel.operator import Absolute
    return Symbol(operator=Absolute(), inputs=as_symbols([a]))


def plus(a, b):
    from paradox.kernel.operator import Plus
    return Symbol(operator=Plus(), inputs=as_symbols([a, b]))


def subtract(a, b):
    from paradox.kernel.operator import Subtract
    return Symbol(operator=Subtract(), inputs=as_symbols([a, b]))


def multiply(a, b):
    from paradox.kernel.operator import Multiply
    return Symbol(operator=Multiply(), inputs=as_symbols([a, b]))


def divide(a, b):
    from paradox.kernel.operator import Divide
    return Symbol(operator=Divide(), inputs=as_symbols([a, b]))


def matrix_multiply(a, b):
    from paradox.kernel.operator import MatrixMultiply
    return Symbol(operator=MatrixMultiply(), inputs=as_symbols([a, b]))


def power(a, b):
    from paradox.kernel.operator import Power
    return Symbol(operator=Power(), inputs=as_symbols([a, b]))


def log(a):
    from paradox.kernel.operator import Log
    return Symbol(operator=Log(), inputs=as_symbols([a]))


def transpose(a, axes: int=None):
    from paradox.kernel.operator import Transpose
    return Symbol(operator=Transpose(axes), inputs=as_symbols([a]))


def reduce_sum(a, axis: int=None, invariant=False):
    from paradox.kernel.operator import ReduceSum
    return Symbol(operator=ReduceSum(axis, invariant), inputs=as_symbols([a]))


def reduce_mean(a, axis: int=None, invariant=False):
    from paradox.kernel.operator import ReduceMean
    return Symbol(operator=ReduceMean(axis, invariant), inputs=as_symbols([a]))


def expand(a, axis: int):
    from paradox.kernel.operator import Expand
    return Symbol(operator=Expand(axis), inputs=as_symbols([a]))


def broadcast(a, shape):
    from paradox.kernel.operator import Broadcast
    return Symbol(operator=Broadcast(shape), inputs=as_symbols([a]))


def where(condition, a, b):
    from paradox.kernel.operator import Where
    return Symbol(operator=Where(), inputs=as_symbols([condition, a, b]))


def equal(a, b):
    from paradox.kernel.operator import Equal
    return Symbol(operator=Equal(), inputs=as_symbols([a, b]))


def not_equal(a, b):
    from paradox.kernel.operator import NotEqual
    return Symbol(operator=NotEqual(), inputs=as_symbols([a, b]))


def less(a, b):
    from paradox.kernel.operator import Less
    return Symbol(operator=Less(), inputs=as_symbols([a, b]))


def less_equal(a, b):
    from paradox.kernel.operator import LessEqual
    return Symbol(operator=LessEqual(), inputs=as_symbols([a, b]))


def greater(a, b):
    from paradox.kernel.operator import Greater
    return Symbol(operator=Greater(), inputs=as_symbols([a, b]))


def greater_equal(a, b):
    from paradox.kernel.operator import GreaterEqual
    return Symbol(operator=GreaterEqual(), inputs=as_symbols([a, b]))


def maximum(a, b):
    from paradox.kernel.operator import Maximum
    return Symbol(operator=Maximum(), inputs=as_symbols([a, b]))


def minimum(a, b):
    from paradox.kernel.operator import Minimum
    return Symbol(operator=Minimum(), inputs=as_symbols([a, b]))


def sin(a):
    from paradox.kernel.operator import Sine
    return Symbol(operator=Sine(), inputs=as_symbols([a]))


def cos(a):
    from paradox.kernel.operator import Cosine
    return Symbol(operator=Cosine(), inputs=as_symbols([a]))


def tan(a):
    from paradox.kernel.operator import Tangent
    return Symbol(operator=Tangent(), inputs=as_symbols([a]))


def arcsin(a):
    from paradox.kernel.operator import ArcSine
    return Symbol(operator=ArcSine(), inputs=as_symbols([a]))


def arccos(a):
    from paradox.kernel.operator import ArcCosine
    return Symbol(operator=ArcCosine(), inputs=as_symbols([a]))


def arctan(a):
    from paradox.kernel.operator import ArcTangent
    return Symbol(operator=ArcTangent(), inputs=as_symbols([a]))


def sinh(a):
    from paradox.kernel.operator import HyperbolicSine
    return Symbol(operator=HyperbolicSine(), inputs=as_symbols([a]))


def cosh(a):
    from paradox.kernel.operator import HyperbolicCosine
    return Symbol(operator=HyperbolicCosine(), inputs=as_symbols([a]))


def tanh(a):
    from paradox.kernel.operator import HyperbolicTangent
    return Symbol(operator=HyperbolicTangent(), inputs=as_symbols([a]))


def arcsinh(a):
    from paradox.kernel.operator import HyperbolicArcSine
    return Symbol(operator=HyperbolicArcSine(), inputs=as_symbols([a]))


def arccosh(a):
    from paradox.kernel.operator import HyperbolicArcCosine
    return Symbol(operator=HyperbolicArcCosine(), inputs=as_symbols([a]))


def arctanh(a):
    from paradox.kernel.operator import HyperbolicArcTangent
    return Symbol(operator=HyperbolicArcTangent(), inputs=as_symbols([a]))


def exp(a):
    from paradox.kernel.operator import Exponential
    return Symbol(operator=Exponential(), inputs=as_symbols([a]))


def slice_assign(a, b, slice_tuple):
    from paradox.kernel.operator import SliceAssign
    return Symbol(operator=SliceAssign(slice_tuple), inputs=as_symbols([a, b]))


def slice_select(a, slice_tuple):
    from paradox.kernel.operator import SliceSelect
    return Symbol(operator=SliceSelect(slice_tuple), inputs=as_symbols([a]))


def concatenate(a, b):
    from paradox.kernel.operator import Concatenate
    return Symbol(operator=Concatenate(), inputs=as_symbols([a, b]))


def rotate90(a, count, axes):
    from paradox.kernel.operator import Rotate90
    return Symbol(operator=Rotate90(count, axes), inputs=as_symbols([a]))


def flip(a, axis):
    from paradox.kernel.operator import Flip
    return Symbol(operator=Flip(axis), inputs=as_symbols([a]))


def reshape(a, shape):
    from paradox.kernel.operator import Reshape
    return Symbol(operator=Reshape(shape), inputs=as_symbols([a]))


def spread(a, position):
    from paradox.kernel.operator import Spread
    return Symbol(operator=Spread(position), inputs=as_symbols([a]))
