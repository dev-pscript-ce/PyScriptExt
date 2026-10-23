import sys 
sys.dont_write_bytecode = True

from pathlib import Path

from ..asts.arguments import(
    StarArgument,
    NamedArgument,
    KwStarArgument,
)
from ..asts.literals import (
    Number,
    String
)
from..asts.classes import (
        ClassObject,
        BoundMethod,
        InstanceObject,
        SuperObject,
    )
from ..parsers.class_p import Instantiate
from ..asts.functions import (
    FunctionObject,
    LambdaFunction,
    FunctionCall
)
from ..asts.expressions import (
    Variable,
    MemberAccess,
    BinaryExpr,
    UnaryExpr,
    IndexExpr,
)
from ..runtimes.runtime import Runtime
from ..asts.exceptions import (
    BreakSignal,    
    ContinueSignal,
    ReturnSignal,
    )
from ..tokens.scope import Scope

# from _auto_ import (
#     imgOCRFind, 
#     imgCV2Find, 
#     imgClick,
#     imgReg,
#     imgScrSave,
#     scrCapture
#     )
# Không cần 👆 dùng 👇
from ..engines.engine_base import AutoBase 

from ..debugs.debug import debug
from ..debugs.printers import printers 
from ..debugs.runtime_printer import runtime_print
from ..asts.ast_fmt import ASTFormatter

fmt = ASTFormatter()

class Interpreter(Instantiate):
    def __init__(self, runtime=None,scope = None, debug=None):

        self.runtime = runtime or Runtime() 

        # imgOCRFind.runtime = self.runtime
        # imgCV2Find.runtime = self.runtime
        # imgClick.runtime = self.runtime
        # imgScrSave.runtime = self.runtime
        # scrCapture.runtime = self.runtime
        # imgReg.runtime = self.runtime
        # Dùng 👇 không cần 👆
        AutoBase.bind_runtime(self.runtime)

        if self.runtime is not None:
            self.runtime.engine.runtime = runtime
            
        self.instantiate = self.instantiate or Instantiate()
        # self.runtime.dump_modules() #  Bật 👉 debug 

        self.global_scope = scope or Scope()

        self.current_scope = self.global_scope

        self.current_function = None
        
        self.loop_depth = 0
        self.debug = debug or {}


    def visit(self, node):
        
        methor = getattr(self, "execute_" + node.__class__.__name__)
        
        return methor(node)
    
    def execute_Assign(self, node):

        value = self.visit(node.value)

        # printers.assign(
        #     f"Assign {node.value} = {value}"
        # )

        printers.assign(
            f"{fmt.format(node.value)} = {value}"
        )

        if node.operator == "=":

            if (
                self.current_function
                and self.current_function.is_method
                and isinstance(node.target, Variable)
            ):
                name = node.target.name

                if name not in [p.name for p in self.current_function.params]:

                    if not self.current_scope.exists_local(name):

                        raise NameError(
                            f"'{name}' is not a local variable.\n"
                            f"Did you mean '{self.current_function.self_name}.{name}'?"
                        )

            self.assign_target(node.target, value)

            printers.assign(
                f"{fmt.format(node.target)} = {value}"
            )

            return value

        current = self.resolve(node.target)

        if node.operator == "+=":
            value = current + value

        elif node.operator == "-=":
            value = current - value

        elif node.operator == "*=":
            value = current * value

        elif node.operator == "/=":
            value = current / value

        elif node.operator == "%=":
            value = current % value

        else:
            raise RuntimeError(
                f"Unknown assignment operator {node.operator}"
            )

        self.assign_target(node.target, value)

        return value

    def execute_Number(self, node):
        return node.value
    
    def execute_String(self, node):
        return node.value
    
    def execute_FString(self, node):

        result = []

        for part in node.parts:

            if isinstance(part, str):
                result.append(part)
            else:
                result.append(str(self.visit(part)))

        return "".join(result)
            

    def execute_Variable(self, node):


        func = getattr(self, "current_function", None)

        # print(func)
        # print(getattr(func, "is_method", None))
        # print(getattr(func, "self_name", None))

        if (
            func
            and getattr(func, "is_method", False)
            and node.name == "self"
        ):
            raise NameError(
                f"Use '{func.self_name}' instead of 'self'"
            )

        return self.get(node.name)
    
    def execute_Boolean(self, node):
        return node.value
    
    def execute_Null(self, node):

        return None
    
    def execute_UnaryExpr(self,node):

        value = self.visit(node.expr)

        if node.op == "+":
            return +value
        elif node.op == "-":
            return -value
        
        elif node.op == "!":
            return not bool(value)
        raise RuntimeError(f"Unknown unary operator: {node.op}")
    
    def execute_BinaryExpr(self, node):

        left = self.visit(node.left)
        right = self.visit(node.right)

        # Arithmetic
        if node.op == "+":
            return left + right

        elif node.op == "-":
            return left - right

        elif node.op == "*":
            return left * right

        elif node.op == "/":
            return left / right

        elif node.op == "%":
            return left % right
        
        # Comparison
        elif node.op == "==":
            return left == right
        
        elif node.op == "!=":
            return left != right
        
        elif node.op == "<":
            return left < right
        
        elif node.op == ">":
            return left > right
        
        elif node.op == "<=":
            return left <= right
        
        elif node.op == ">=":
            return left >= right
        
        elif node.op == "in":
            return left in right
        
        # Logical
        elif node.op == "&&":
            return bool(left) and bool(right)
        
        elif node.op == "||":
            return bool(left) or bool(right)

        raise RuntimeError(f"Unknown operator: {node.op}")
    
    def execute_TernaryExpr(self, node):

        if self.visit(node.condition):
            return self.visit(node.then_expr)
        return self.visit(node.else_expr)
    
    def execute_UpdateExpr(self, node):

        old = self.resolve(node.target)

        if node.op == "++":
            new = old + 1
        else:
            new = old - 1

        self.assign_target(node.target, new)

        return new if node.prefix else old

    def execute_IfStatement(self, node):

        if self.visit(node.condition):

            self.execute_block(
                node.then_block,
                new_scope=False
            )

            return

        for cond, block in node.elif_blocks:

            if self.visit(cond):

                self.execute_block(
                    block,
                    new_scope=False
                )

                return

        if node.else_block:

            self.execute_block(
                node.else_block,
                new_scope=False
            )


    def execute_BreakStatement(self, node):

        if self.loop_depth <= 0:
            raise RuntimeError(
                "break outside loop"
            )

        raise BreakSignal()
    
    def execute_ContinueStatement(self, node):

        if self.loop_depth <= 0:
            raise RuntimeError(
                "continue outside loop"
            )

        raise ContinueSignal()
    
    def execute_WhileStatement(self, node):

        printers.loop(
            f"while {self.format_expr(node.condition)}"
        )

        self.loop_depth += 1

        try:

            while True:

                condition = self.visit(node.condition)

                printers.loop(
                    f"condition = {condition}"
                )

                if not condition:
                    break

                try:
                    self.execute_block(
                        node.block,
                        new_scope=False
                    )

                except ContinueSignal:

                    printers.loop("CONTINUE")

                    continue

                except BreakSignal:

                    printers.loop("BREAK")

                    break

        finally:
            
            self.loop_depth -= 1

            printers.loop("END WHILE")

    def execute_ForStatement(self, node):

        iterable = self.visit(node.iterable)

        printers.loop(
            f"for {node.name} in {iterable}"
        )

        has_value = False
        last_value = None

        self.loop_depth += 1

        try:

            for value in iterable:

                has_value = True
                last_value = value

                printers.loop(
                    f"{node.name} = {value}"
                )

                self.current_scope.assign_or_define(
                    node.name,
                    value
                )

                try:

                    self.execute_block(node.block)

                except ContinueSignal:

                    printers.loop(
                        f"{node.name} = {value} CONTINUE"
                    )

                    continue

                except BreakSignal:

                    printers.loop(
                        f"{node.name} = {value} BREAK"
                    )

                    break

        finally:

            self.loop_depth -= 1

        if has_value:

            printers.loop(
                f"\n{node.name} = {last_value} \nEND FOR"
            )

        else:

            printers.loop(
                f"\n{node.name} = <empty> \nEND FOR"
            )

        debug.leave()

    def execute_RangeExpression(self, node):

        start = self.visit(node.start)

        end = self.visit(node.end)

        return range(start, end)

    def execute_FunctionCall(self, node):

        func = self.visit(node.callee)
        args = []
        kwargs = {}

        for arg in node.args:

            #
            # timeout=5
            #

            if isinstance(arg, NamedArgument):

                kwargs[arg.name] = self.visit(arg.value)

            #
            # *items
            #

            elif isinstance(arg, StarArgument):

                args.extend(
                    self.visit(arg.value)
                )

            #
            # **options
            #

            elif isinstance(arg, KwStarArgument):

                kwargs.update(
                    self.visit(arg.value)
                )

            #
            # normal argument
            #

            else:

                args.append(
                    self.visit(arg)
                )

        if isinstance(func, BoundMethod):

            return self.call_function(
                func.function,
                args,
                kwargs,
                self_obj=func.owner
            )
        
        # DSL Function
        if isinstance(func, FunctionObject):
            return self.call_function(
                func,
                args,
                kwargs
            )

        # DSL Class
        if isinstance(func, ClassObject):
            return self.instantiate(
                func,
                args,
                kwargs
            )

        if isinstance(func, SuperObject):
            if args or kwargs:
                raise RuntimeError(
                    "super() takes no arguments"
                )
            return func

        callee_name = self.format_expr(node.callee)

        runtime_print.call(
            f"{callee_name}({args}, {kwargs})",
            f"\n ↪ {callee_name}({args}, {kwargs})",
        )

        # multi_char(char="-",n=4,color="G")

        return func(*args, **kwargs)
    
    def execute_FunctionDef(self, node):
        func = FunctionObject(
            node.name,
            node.params,
            node.body,
            self.current_scope
        )
        
        self.define(
            node.name,
            func
        )

    def call_function(
        self,
        func,
        args,
        kwargs,
        self_obj=None
    ):

        scope = Scope(parent=func.closure)

        if self_obj is not None:
            args = [self_obj, *args]

        self.push_scope(scope)

        old_function = self.current_function

        old_self = getattr(self, "self_obj", None)
        old_class = getattr(self, "current_class", None)

        self.current_function = func
        self.self_obj = self_obj
        self.current_class = getattr(func, "owner_class", None)

        try:

            bound = self.bind_arguments(
                func.params,
                args,
                kwargs.copy()
            )

            for name, value in bound.items():
                scope.define(name, value)

            self.execute_block(
                func.body,
                new_scope=False
            )

        except ReturnSignal as r:
            return r.value

        finally:
            self.current_function = old_function
            self.self_obj = old_self
            self.current_class = old_class
            self.pop_scope()

    def execute_Import(
        self,
        node,
    ):

        runtime = self.runtime

        last_module = None

        for (
            module_name,
            alias,
            is_file,
        ) in node.imports:

            # =========================================
            # Pscript file
            # =========================================

            if is_file:

                module = runtime.load_script(
                    module_name
                )

                name = (
                    alias
                    or Path(module_name).stem
                )

            # =========================================
            # Built-in / Runtime module
            # =========================================

            else:

                module = runtime.get_module(
                    module_name
                )

                if module is None:
                    raise ImportError(
                        module_name
                    )

                name = (
                    alias
                    or module_name
                )

            self.define(
                name,
                module,
            )

            last_module = module

        return last_module

    def execute_FromImport(self, node):

        runtime = self.runtime

        #
        # load module
        #

        if node.module.endswith(".ps"):
            module = runtime.load_script(node.module)
        else:
            module = runtime.get_module(node.module)

        if module is None:
            raise ImportError(node.module)

        #
        # from xxx import *
        #

        if (
            len(node.names) == 1
            and node.names[0][0] == "*"
        ):

            if hasattr(module, "scope"):

                for name, value in module.scope.symbols.items():

                    if name.startswith("_"):
                        continue

                    self.current_scope.define(name, value)

            else:

                for name in dir(module):

                    if name.startswith("_"):
                        continue

                    self.current_scope.define(
                        name,
                        getattr(module, name)
                    )

            return

        #
        # from xxx import a, b as c
        #

        for name, alias in node.names:

            #
            # script module
            #

            if hasattr(module, "scope"):

                value = module.scope.lookup(name)

            #
            # builtin module
            #

            else:

                value = getattr(module, name, None)

            if value is None:

                raise ImportError(
                    f"{node.module} has no member '{name}'"
                )

            self.current_scope.define(
                alias or name,
                value
            )

            
    def execute_block(self, block, new_scope=False):

        if new_scope:
            self.push_scope()

        try:
            for stmt in block.body:
                self.visit(stmt)
        finally:
            if new_scope:
                self.pop_scope()


    def execute_Block(self, node):
        self.execute_block(node, new_scope=True)

    def execute_MemberAccess(self, node):

        obj = self.visit(node.obj)

        #
        # DSL Class
        #

        if isinstance(obj, ClassObject):

            value = self.lookup_class_member(
                obj,
                node.member
            )

            if value is None:
                raise AttributeError(
                    f"Class '{obj.name}' has no member '{node.member}'"
                )

            if (
                isinstance(value, FunctionObject)
                and getattr(value, "is_method", False)
            ):
                raise TypeError(
                    f"Instance method '{node.member}' "
                    f"cannot be called on class '{obj.name}'"
                )

            return value

        # Super:
        if isinstance(obj, SuperObject):

            for base in obj.current_class.bases:

                value = self.lookup_method(

                    base,

                    node.member

                )

                if value:

                    return BoundMethod(

                        obj.instance,

                        value

                    )

            raise AttributeError(node.member)

        #
        # DSL Instance
        #

        if isinstance(obj, InstanceObject):

            #
            # field
            #

            if node.member in obj.fields:
                return obj.fields[node.member]

            #
            # method
            #
            method = self.lookup_method(
                obj.cls,
                node.member
            )
            if method is not None:
                return BoundMethod(obj, method)
            
            # class/static member (supports inheritance)

            value = self.lookup_class_member(
                obj.cls,
                node.member
            )
            if value is not None:
                return value

            raise AttributeError(
                f"'{obj.cls.name}' object has no attribute '{node.member}'"
            )

        # Python object

        return getattr(obj, node.member)
    
    def execute_LambdaExpr(self, node):

        return LambdaFunction(

            self,

            node,

            self.current_scope

        )
    
    def execute_AnonymousFunction(self, node):

        return FunctionObject(
            name="<anonymous",
            params=node.params,
            body=node.body,
            closure=self.current_scope
        )
        
    def execute_ReturnStatement(self, node):
        value = None
        if node.value:
            value = self.visit(node.value)
        raise ReturnSignal(value)
    
    def execute_ExpressionStatement(self, node):
        return self.visit(node.expr)
    
    def execute_ListLiteral(self, node):
        return [
            self.visit(expr) for expr in node.elements
        ]
    def execute_IndexExpr(self,node):

        obj = self.visit(node.target)

        idx = self.visit(node.index)

        return obj[idx]
    
    def execute_AssignIndex(self,node):

        obj = self.visit(node.target)

        idx = self.visit(node.index)

        value = self.visit(node.value)

        obj[idx] = value

        return value
    
    def execute_SliceExpr(self,node):

        obj=self.visit(node.target)

        start=None if node.start is None else self.visit(node.start)

        stop=None if node.stop is None else self.visit(node.stop)

        step=None if node.step is None else self.visit(node.step)

        return obj[start:stop:step]
    
    def execute_DictLiteral(self,node):

        d = {}

        for key,value in node.pairs:

            d[
                self.visit(key)
            ] = self.visit(value)

        return d
    
    def execute_TupleLiteral(self,node):

        return tuple(
            self.visit(e)
            for e in node.elements
        )
    
    def execute_SetLiteral(self,node):

        return {
            self.visit(e)
            for e in node.elements
        }
    
    def execute_WalrusExpr(self, node):

        value = self.visit(node.value)

        self.assign_or_define(
            node.target,
            value
        )
        return value


    def execute_ClassDef(self, node):

        class_scope = Scope(parent=self.current_scope)

        old_scope = self.current_scope
        self.current_scope = class_scope

        try:

            for stmt in node.body.body:
                self.visit(stmt)

        finally:

            self.current_scope = old_scope

        # resolve bases
        bases = [
            self.visit(base)
            for base in node.bases
        ]

        cls = ClassObject(
            node.name,
            class_scope,
            bases
        )

        self.bind_method(cls)

        self.current_scope.define(
            node.name,
            cls
        )

        return cls
    def execute_SuperExpr(self,node):

        if self.self_obj is None:
            raise RuntimeError(
                "super() outside method"
            )

        return SuperObject(

            self.self_obj,

            self.current_function.owner_class

        )

    def execute_SwitchStatement(self, node):

        value = self.visit(node.expr)

        for case in node.cases:

            matched = False

            for value_node in case.values:

                if value == self.visit(value_node):
                    matched = True
                    break

            if not matched:
                continue

            try:

                return self.visit(case.block)

            except BreakSignal:

                return None

        if node.default_block is not None:

            try:
                return self.visit(
                    node.default_block
                )
            except BreakSignal:
                return None

        return None 

    def execute_TryStatement(self, node):

        try:

            return self.visit(
                node.try_block
            )

        except (
            ReturnSignal,
            BreakSignal,
            ContinueSignal,
        ):

            raise

        except Exception as exc:

            handled = False

            for catch in node.catches:

                if not self.exception_matches(
                    exc,
                    catch.exception_type,
                ):
                    continue

                handled = True

                # -----------------------------
                # catch e
                # -----------------------------

                if catch.name is not None:

                    self.current_scope.define(
                        catch.name,
                        exc
                    )

                return self.visit(
                    catch.block
                )

            # -----------------------------
            # Không có catch phù hợp
            # -----------------------------

            if not handled:
                raise

        finally:

            if node.finally_block is not None:

                self.visit(
                    node.finally_block
                )
    
# ------------------------------------------------------------- #
# Bind Method:

    def bind_method(self,cls):
        for value in cls.scope.values.values():
            if isinstance(value, FunctionObject):

                value.is_method = True
                value.owner_class = cls

                if value.params:
                    value.self_name = value.params[0].name
# Bind Argument:

    def bind_arguments(
            self,
            params,
            args,
            kwargs
        ):
            bound = {}
    
            pos = 0
    
            for param in params:
    
                #
                # positional
                #
    
                if pos < len(args):
    
                    bound[param.name] = args[pos]
                    pos += 1
                    continue
    
                #
                # keyword
                #
    
                if param.name in kwargs:
    
                    bound[param.name] = kwargs.pop(param.name)
                    continue
    
                #
                # default
                #
    
                if param.default is not None:
    
                    bound[param.name] = self.visit(
                        param.default
                    )
    
                    continue
    
                raise RuntimeError(
                    f"Missing argument '{param.name}'"
                )
    
            #
            # too many args
            #
    
            if pos < len(args):
    
                raise RuntimeError(
                    "Too many positional arguments"
                )
    
            #
            # unknown kwargs
            #
    
            if kwargs:
    
                raise RuntimeError(
                    f"Unknown arguments: {', '.join(kwargs)}"
                )
    
            return bound
    
# ------------------------------------------------------------- #
# Lookup Method:

    def lookup_method(self, cls, name):

        value = self.lookup_class_member(cls, name)

        if isinstance(value, FunctionObject):
            return value

        return None

    def lookup_class_member(

        self,

        cls,

        name

    ):

        #
        # current class
        #

        if name in cls.scope.values:
            return cls.scope.values[name]

        #
        # search base classes
        #

        for base in cls.bases:

            value = self.lookup_class_member(
                base,
                name
            )

            if value is not None:
                return value

        return None
# ------------------------------------------------------------- #

    def define(self, name, value):
        self.current_scope.define(name, value)

    def assign(self, name, value):
        self.current_scope.assign(name, value)

    def get(self, name):# không cần lookup()

        scope = self.find_scope(name)

        if scope is not None:
            return scope.values[name]

        value = self.runtime.get(name)

        if value is not None:
            return value

        raise NameError(f"{name} not found")

    # def get(self, name): # cần lookup()

    #     try:
    #         return self.lookup(name)
    #     except NameError:
    #         pass

    #     value = self.runtime.get(name)

    #     if value is not None:
    #         return value

    #     raise NameError(f"{name} not found")
    
    def push_scope(self, parent=None):

        self.current_scope = Scope(
            parent or self.current_scope
        )

    def pop_scope(self):

        self.current_scope = self.current_scope.parent

    def assign_target(self, target, value):

        # x = ...
        if isinstance(target, Variable):

            self.assign_or_define(
                target.name,
                value
            )

            return 

        # obj.member = ...
        if isinstance(target, MemberAccess):

            obj = self.visit(target.obj)

            if isinstance(obj, InstanceObject):
                obj.fields[target.member] = value
                return

            setattr(obj, target.member, value)
            return 

        # arr[i] = ...
        if isinstance(target, IndexExpr):

            obj = self.visit(target.target)

            index = self.visit(target.index)

            obj[index] = value

            return 

        raise RuntimeError(
            f"Cannot assign to {type(target).__name__}"
        )
    
    def assign_or_define(self, name, value):

        scope = self.find_scope(name)

        if scope:
            scope.assign(name, value)
        else:
            self.current_scope.define(name, value)

    def find_scope(self, name):

        scope = self.current_scope

        while scope:

            if name in scope.values:      # hoặc scope.has_local(name)
                return scope

            scope = scope.parent

        return None
    
    # def lookup(self, name): # kết hợp get()

    #     scope = self.find_scope(name)

    #     if scope is None:
    #         raise NameError(name)

    #     return scope.values[name]

    def resolve(self, target):

        # x
        if isinstance(target, Variable):
            return self.current_scope.get(target.name)

        # obj.member
        if isinstance(target, MemberAccess):

            obj = self.visit(target.object)

            return getattr(
                obj,
                target.member
            )

        # arr[index]
        if isinstance(target, IndexExpr):

            obj = self.visit(target.object)

            index = self.visit(target.index)

            return obj[index]

        raise RuntimeError(
            f"Cannot resolve {type(target).__name__}"
        )
    
    def format_expr(self, node):

        if isinstance(node, Number):
            return str(node.value)

        if isinstance(node, String):
            return repr(node.value)

        if isinstance(node, Variable):
            return node.name

        if isinstance(node, BinaryExpr):
            return (
                f"{self.format_expr(node.left)} "
                f"{node.op} "
                f"{self.format_expr(node.right)}"
            )

        if isinstance(node, UnaryExpr):
            return f"{node.op}{self.format_expr(node.expr)}"

        if isinstance(node, FunctionCall):
            args = ", ".join(
                self.format_expr(a)
                for a in node.args
            )
            return f"{self.format_expr(node.callee)}({args})"

        if isinstance(node, MemberAccess):
            return (
                f"{self.format_expr(node.obj)}."
                f"{node.member}"
            )

        return type(node).__name__


    def exception_matches(self, exc, exception_type):

        # catch:
        if exception_type is None:
            return True

        # Hiện tại catch type dự kiến là Variable
        if not isinstance(
            exception_type,
            Variable
        ):
            return False

        name = exception_type.name

        # ---------------------------------
        # Kiểm tra toàn bộ MRO
        # ---------------------------------

        for cls in type(exc).__mro__:

            if cls.__name__ == name:
                return True

        return False
# ------------------------------------------------------------- #

    def execute_Program(self, node):
        for stmt in node.body:
            self.visit(stmt)

