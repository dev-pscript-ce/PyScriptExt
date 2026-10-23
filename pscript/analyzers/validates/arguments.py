import sys
sys.dont_write_bytecode = True

from pscript.asts.arguments import (
    StarArgument,
    NamedArgument,
    KwStarArgument,
)

class ValidateArgument:

    def validate_arguments(
            self,
            call,
            method,
            function_name,
        ):
    
            if (
                "definition" in method
                and isinstance(
                    method["definition"],
                    dict,
                )
            ):
    
                method = method["definition"]
    
            parameters = method.get(
                "parameters",
                [],
            )
    
            # =================================
            # Parameter information
            # =================================
    
            normal_parameters = []
    
            has_varargs = False
            has_varkwargs = False
            required_varargs = False
    
            for parameter in parameters:
    
                name = parameter.get(
                    "name",
                    "",
                )
    
                # =================================
                # **kwargs
                # =================================
    
    
                if (
                    name.startswith("**")
                    or parameter.get(
                        "varkwargs",
                        False,
                    )
                ):
    
                    has_varkwargs = True
    
                    continue
    
                # =================================
                # *args
                # =================================
    
                if (
                    name.startswith("*")
                    or parameter.get("variadic", False)
                ):
    
                    has_varargs = True
    
                    if parameter.get("required", False):
                        required_varargs = True
    
                    continue
    
                normal_parameters.append(
                    parameter
                )
    
            parameter_names = {
    
                parameter["name"]
    
                for parameter
                in normal_parameters
    
            }
    
            required_names = {
    
                parameter["name"]
    
                for parameter
                in normal_parameters
    
                if parameter.get(
                    "required",
                    True,
                )
    
            }
    
            # =================================
            # Arguments
            # =================================
    
            positional_arguments = []
    
            named_arguments = []
    
            has_star_argument = False
            has_kwstar_argument = False
    
            for argument in call.args:
    
                if isinstance(
                    argument,
                    NamedArgument,
                ):
    
                    named_arguments.append(
                        argument
                    )
    
                elif isinstance(
                    argument,
                    StarArgument,
                ):
    
                    has_star_argument = True
    
                elif isinstance(
                    argument,
                    KwStarArgument,
                ):
    
                    has_kwstar_argument = True
    
                else:
    
                    positional_arguments.append(
                        argument
                    )
    
            # =================================
            # Required *args
            # =================================
    
            if (
                required_varargs
                and not positional_arguments
                and not has_star_argument
            ):
    
                self.add_error(
                    token=call.lparen_token,
                    length=2,
    
                    message=(
                        f'{function_name}() '
                        f'requires at least 1 argument'
                    ),
    
                    code=(
                        "PSCRIPT_TOO_FEW_ARGUMENTS"
                    ),
                )
    
            # =================================
            # Unknown keyword
            # =================================
    
            provided_named_names = set()
    
            for argument in named_arguments:
    
                name = argument.name
    
                # -----------------------------
                # Duplicate keyword
                # -----------------------------
    
                if name in provided_named_names:
    
                    self.add_error(
                        node=argument,
    
                        message=(
                            f'Multiple values for '
                            f'argument "{name}" '
                            f'in {function_name}()'
                        ),
    
                        code=(
                            "PSCRIPT_DUPLICATE_ARGUMENT"
                        ),
                    )
    
                    continue
    
                provided_named_names.add(
                    name
                )
    
                # -----------------------------
                # Unknown keyword
                # -----------------------------
    
                if (
                    name not in parameter_names
                    and not has_varkwargs
                    and not has_kwstar_argument
                ):
    
                    self.add_error(
                        node=argument,
    
                        message=(
                            f'Unknown keyword '
                            f'argument '
                            f'"{name}" '
                            f'in {function_name}()'
                        ),
    
                        code=(
                            "PSCRIPT_UNKNOWN_KEYWORD"
                        ),
                    )
    
            # =================================
            # Bind positional arguments
            # =================================
    
            positional_names = set()
    
            for index, argument in enumerate(
                positional_arguments
            ):
    
                if index >= len(
                    normal_parameters
                ):
    
                    if has_varargs:
                        continue
    
                    # Too many arguments
                    continue
    
                parameter_name = (
                    normal_parameters[
                        index
                    ]["name"]
                )
    
                positional_names.add(
                    parameter_name
                )
    
                # -----------------------------
                # foo(1, a=2)
                # -----------------------------
    
                if (
                    parameter_name
                    in provided_named_names
                ):
    
                    self.add_error(
                        node=argument,
    
                        message=(
                            f'Multiple values for '
                            f'argument '
                            f'"{parameter_name}" '
                            f'in {function_name}()'
                        ),
    
                        code=(
                            "PSCRIPT_DUPLICATE_ARGUMENT"
                        ),
                    )
    
            # =================================
            # Missing required arguments
            # =================================
    
            missing_names = (
                required_names
                - positional_names
                - provided_named_names
            )
    
            # Nếu có *args, runtime có thể cung cấp
            # các positional còn thiếu.
            if has_star_argument:
    
                missing_names = set()
    
            if missing_names:
    
                required_count = len(
                    required_names
                )
    
                provided_count = (
                    len(
                        positional_arguments
                    )
                    +
                    len(
                        provided_named_names
                    )
                )
    
                message = (
                    f'{function_name}() '
                    f'expects at least '
                    f'{required_count} '
                    f'argument'
                    f'{"s" if required_count != 1 else ""}, '
                    f'but got '
                    f'{provided_count}'
                )
    
                if (
                    call.lparen_token
                    is not None
                ):
    
                    self.add_error(
                        token=call.lparen_token,
                        length=2,
    
                        message=message,
    
                        code=(
                            "PSCRIPT_TOO_FEW_ARGUMENTS"
                        ),
                    )
    
                else:
    
                    self.add_error(
                        node=call.callee,
    
                        message=message,
    
                        code=(
                            "PSCRIPT_TOO_FEW_ARGUMENTS"
                        ),
                    )
    
            # =================================
            # Too many positional arguments
            # =================================
    
            if (
                not has_varargs
                and not has_star_argument
                and
                len(positional_arguments)
                >
                len(normal_parameters)
            ):
    
                provided_count = (
                    len(
                        positional_arguments
                    )
                    +
                    len(
                        provided_named_names
                    )
                )
    
                maximum_count = len(
                    normal_parameters
                )
    
                self.add_error(
                    node=call,
    
                    message=(
                        f'{function_name}() '
                        f'expects at most '
                        f'{maximum_count} '
                        f'argument'
                        f'{"s" if maximum_count != 1 else ""}, '
                        f'but got '
                        f'{provided_count}'
                    ),
    
                    code=(
                        "PSCRIPT_TOO_MANY_ARGUMENTS"
                    ),
                )