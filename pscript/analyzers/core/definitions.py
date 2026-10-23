
KEYWORDS = [
  "class",
  "func",
  "if",
  "else",
  "elif",
  "while",
  "for",
  "return",
  "break",
  "continue",
  "import",
  "from",
  "as",
  "try",
  "catch",
  "finally",
  "super",
  "this",
  "in",
]

CONSTANTS = ["true", "false", "null"]

MODULES = {

    "ocr": {

        "methods": {

            "FIND_TEXT": {

                "parameters": [
                    {
                        "name": "text",
                        "required": True,

                    },
                    {
                        "name": "debug",
                        "required": False,

                    },
                    {
                        "name": "save_temp",
                        "required": False,

                    },
                    {
                        "name": "click",
                        "required": False,

                    },
                ],

                "description": (
                    "Find text on screen"
                ),
            },

            "CLICK_TEXT": {

                "parameters": [
                    {
                        "name": "text",
                        "required": True,
                    },
                ],

                "description": (
                    "Find and click text "
                ),
            },
            "WAIT_TEXT": {

                "parameters": [
                    {
                        "name": "text",
                        "required": True,
                    },
                ],

                "description": (
                    "Wait  text "
                ),
            },
        },
    },

    "cv2": {
        "methods": {
            "FIND_IMG": {
                "parameters": [
                    {
                        "name": "img_path",
                        "required": True,
                        
                    },
                    {
                        "name": "click",
                        "required": False,
                    },
                    {
                        "name": "debug",
                        "required": False
                    }
                ],

                "description": (
                    "Find a image on screen and *options  "
                )
            },
            "FIND_CLICK": {
                "parameters": [
                    {
                        "name": "img_path",
                        "required": True,
                    },
                    {
                        "name": "click",
                        "required": False,
                    },
                    {
                        "name": "debug",
                        "required": False
                    }
                ],

                "description": (
                    "Find And Click a image on screen and *options  "
                )
            },
            "CLICK": {
                "parameters": [
                    {
                        "name": "x",
                        "required": True,
                    },
                    {
                        "name": "y",
                        "required": True,
                    },

                ],

                "description": (
                    "Find And Click a image on screen and *options  "
                )
            },
            "SMART_FIND": {
                "parameters": [
                    {
                        "name": "img_path",
                        "required": True,
                    },
                    {
                        "name": "debug",
                        "required": False,
                    },
                ],

                "description": (
                    "Smart find a image on screen and *options  "
                )
            },
            "CLICK_IMG": {
                "parameters": [
                    {
                        "name": "img_path",
                        "required": True,
                    }
                ],

                "description": (
                    "Click a image on screen "
                )
            },
            "SMART_CLICK": {
                "parameters": [
                    {
                        "name": "img_path",
                        "required": True,
                    }
                ],

                "description": (
                    "Smart click a image on screen "
                )
            },
            "WAIT_IMG": {
                "parameters": [
                    {
                        "name": "img_path",
                        "required": True,
                    }
                ],

                "description": (
                    "Wait a image ... "
                )
            },
        },
    },

    "std": {
        "methods": {
            "PRINTL": {
                "parameters": [
                    {
                        "name": "args",
                        "required": False,
                        "variadic": True,
                    },
                ],

                "description": (
                    "Print argument to console"
                )
            },
            "INPUTL": {
                "parameters": [
                    {
                        "name": "prompt",
                        "required": False,
                    },
                    {
                        "name": "color",
                        "required": False,
                    },
                ],

                "description": (
                    "Input argument to console"
                )
            },
            "WRITEL": {
                "parameters": [
                    {
                        "name": "args",
                        "required": True,
                    },
                ],

                "description": (
                    "Find And Click a image on screen and *options  "
                )
            },
        },
    },

    "cre": {
        "methods": {
            "CREATE_FILE": {
                "parameters": [
                    {
                        "name": "file_name",
                        "required": False,
                        "variadic": True,
                    },
                    {
                        "name": "ext",
                        "required": False,
                        "variadic": True,
                    },
                ],

                "description":"Create a file in the project"
            },
            
        },
    },

}
# -------------------------------------------------------------------------- # 

BUILTINS = {
    "methods": {
        "Find_Text": {
            "parameters": [
                {
                    "name": "text",
                    "required": True,
                },
                {
                    "name": "debug",
                    "required": False,
                },
                {
                    "name": "save_temp",
                    "required": False,
                },
                {
                    "name": "click",
                    "required": False,
                },
            ],
            "description": "Find text on screen",
        },

        "Click_Text": {
            "parameters": [
                {
                    "name": "text",
                    "required": True,
                },
            ],
            "description": "Find and click text",
        },

        "Write": {
            "parameters": [
                {
                    "name": "text",
                    "required": True,
                },
            ],
            "description": "Write texts",
        },

        "Set_Interval": {
            "parameters": [
                {
                    "name": "interval",
                    "required": False,
                },
            ],
            "description": "Write texts",
        },

        "Hot_Key": {
            "parameters": [
                {
                    "name": "keys",
                    "required": False,
                    "variadic":True,
                },
            ],
            "description": "Write texts",
        },

        "Press": {
            "parameters": [
                {
                    "name": "keys",
                    "required": False,
                    "variadic":True,
                },
            ],
            "description": "Write texts",
        },

        "printl": {
            "parameters": [
                {
                    "name": "*args",
                    "required": True,
                    "variadic":True,
                },
            ],
            "description": "Print arguments to the console",
        },

        "inputl": {
            "parameters": [
                {
                    "name": "*args",
                    "required": True,
                    "variadic":True,
                },
            ],
            "description": "Input arguments to the console",
        },

        "writel": {
            "parameters": [
                {
                    "name": "*args",
                    "required": True,
                    "variadic":True,
                },
            ],
            "description": "Print arguments to the console",
        },

        "ask_option": {
            "parameters": [
                {
                    "name": "question",
                    "required": True,
                    "variadic":True,
                },
                {
                    "name": "options",
                    "required": True,
                    "variadic":True,
                },
                {
                    "name": "is_num",
                    "required": False,
                    "variadic":True,
                },
            ],
            "description": "Question and options ",
        },

        "range": {
            "parameters": [
                {
                    "name": "start",
                    "required": True,
                    "variadic":True,
                },
                {
                    "name": "end",
                    "required": True,
                    "variadic":True,
                },
            ],
            "description": "Builtin-Function (range)",
        },

        "push": {
            "parameters": [
                {
                    "name":"obj",
                    "required": False,

                },
                {
                    "name":"obj",
                    "required": False,

                }
            ],
            "description": "Push a obj to ..",
        },

        "tuple": {
            "parameters": [
                {
                    "name":"obj",
                    "required": False,

                },
                {
                    "name":"obj",
                    "required": False,

                }
            ],
            "description": "Push a obj to ..",
        },

        "list": {
            "parameters": [
                {
                    "name":"obj",
                    "required": False,

                },
                {
                    "name":"obj",
                    "required": False,

                }
            ],
            "description": "Push a obj to ..",
        },

        "dict": {
            "parameters": [
                {
                    "name":"obj",
                    "required": False,

                },
                {
                    "name":"obj",
                    "required": False,

                }
            ],
            "description": "Push a obj to ..",
        },

        "pop": {
            "parameters": [
                {
                    "name":"obj",
                    "required": False,
                }
            ],
            "description": "Pop a obj to ..",
        },

        "set": {
            "parameters": [
                {
                    "name":"obj",
                    "required": False,
                }
            ],
            "description": "init a obj",
        },

        "stack": {
            "parameters": [],
            "description": "init a stack",
        },

        "banner": {
            "parameters": [
                {
                    "name": "title",
                    "required": True,
                },
                {
                    "name": "color_title",
                    "required": True,
                },
                {
                    "name": "char",
                    "required": True,
                },
                {
                    "name": "color_char",
                    "required": True,
                },
                {
                    "name": "number",
                    "required": False,
                },
            ],
            "description": "Print arguments to the console",
        },

        "split":{
            "parameters":[
                {
                    "name":"separator",
                    "required": True,
                },
                {
                    "name":"item",
                    "required": True,
                },
                {
                    "name":"limit",
                    "required": False,
                },
                {
                    "name":"str_single_value",
                    "required": False,
                },
                {
                    "name":"index_filter",
                    "required": False,
                },
            ],
        },

        "join":{
            "parameters":[
                {
                    "name":"separator",
                    "required": True,
                },
                {
                    "name":"item",
                    "required": True,
                },
            ],
        },
        
        "error":{
            "parameters":[
                {
                    "name":"error_text",
                    "required": True,
                },
                {
                    "name":"warn_text",
                    "required": False,
                },
                {
                    "name":"throw_err",
                    "required": False,
                },
            ],
        },

        "create_file":{
            "parameters":[
                {
                    "name":"file_name",
                    "required": False,
                },
                {
                    "name":"ext",
                    "required": False,
                },
            ],
            "description":"Create a file in the project"
        },
    },

# -------------------------------------------------------------------------- # 
    "objects": {

        "print": {

            "callable": True,

            "parameters": [
                {
                    "name":"args",
                    "required": True,
                    "variadic":True,
                },
            ],
            "description": "Print arguments to the console",

            "methods": {

                "R": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print Red text",
                },

                "rR": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print RGB_RED Text",
                },

                "G": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print Green text",
                },

                "rG": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print RGB_GREEN Text",
                },

                "Y": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print Yellow text",
                },

                "rY": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print RGB_YELLOW text",
                },

                "B": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print Blue text",
                },

                "rB": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print RGB_BLUE Text",
                },

                "M": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print Magenta text",
                },

                "C": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print Cyan text",
                },

                "rC": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print RGB_CYAN Text",
                },

                "A": {
                    "methods":{
                        "b":{
                            "methods":{
                                "i":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                
                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "i":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "u":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "u":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },
                        "u":{
                            "methods":{
                                "b":{
                                    "methods":{
                                        "i":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },
                                "i":{
                                    "methods":{
                                        "b":{
                                            "parameters":[
                                                {
                                                    "name":"text",
                                                    "required":True,
                                                }
                                            ],
                                        },
                                    },
                                    "parameters":[
                                        {
                                            "name":"text",
                                            "required":True,
                                        }
                                    ],
                                },

                            },
                            "parameters":[
                                {
                                    "name":"text",
                                    "required":True,
                                }
                            ],
                        },

                    },

                    "parameters": [
                        {
                            "name": "text",
                            "required": True,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Print Gray text",
                },

                "error": {
                    "parameters": [
                        {
                            "name": "args",
                            "required": True,
                            "variadic": True,
                        },
                    ],
                },

                "warn": {
                    "parameters": [
                        {
                            "name": "args",
                            "required": True,
                            "variadic": True,
                        },
                    ],
                },

                "logt": {
                    "parameters": [
                        {
                            "name": "args",
                            "required": True,
                            "variadic": True,
                        },
                    ],
                },
                
            },
        },

        "input": {

            "callable": True,

            "parameters": [
                {
                    "name":"*args",
                    "required": True,
                    "variadic":True,
                },
            ],

            "description": "Input arguments to the console",

            "methods": {

                "select":{
                    "parameters":[
                        {
                            "name":"args_list",
                            "required":False,
                        },
                        {
                            "name":"multi",
                            "required":False,
                        }
                    ],
                    "description":"select opt ..."
                },

                "R": {
                    "parameters": [
                        {
                            "name": "text",
                            "required": False,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Show text red",
                },

                "G": {
                
                    "parameters": [
                        {
                            "name": "text",
                            "required": False,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Show text green",

                },

                "Y": {
                    "parameters": [
                        {
                            "name": "text",
                            "required": False,
                            "variadic":True,
                        },
                        
                    ],
                },

                "B": {

                    "parameters": [
                        {
                            "name": "text",
                            "required": False,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Show text blue",
                },

                "M": {

                    "parameters": [
                        {
                            "name": "text",
                            "required": False,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Show text magenta",
                },

                "C": {

                    "parameters": [
                        {
                            "name": "text",
                            "required": False,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Show text cyan",
                },

                "A": {

                    "parameters": [
                        {
                            "name": "text",
                            "required": False,
                            "variadic":True,
                        },
                        
                    ],
                    "description":"Show text gray",
                },

                "error": {
                    "parameters": [
                        {
                            "name": "args",
                            "required": False,
                            "variadic": True,
                        },
                    ],
                },
                "warn": {
                    "parameters": [
                        {
                            "name": "args",
                            "required": False,
                            "variadic": True,
                        },
                    ],
                },

                "logt": {
                    "parameters": [
                        {
                            "name": "args",
                            "required": False,
                            "variadic": True,
                        },
                    ],
                },
                
            },
        },

        "ansi": {
            "methods": {
                "ansi_basic": {
                    "parameters":[
                        {
                            "name":"ansi_number",
                            "required":True,
                        }
                    ],
                    "methods": {
                        "u": {},
                        "b": {},
                        "i": {},
                    },
                },
                "hex": {
                    "methods": {
                        "u": {},
                        "b": {},
                        "i": {},
                    },
                },
                "rgb": {
                    "parameters":[
                        {
                            "name":"r",
                            "required":True,
                            "variadic":True,
                        },
                        {
                            "name":"g",
                            "required":True,
                            "variadic":True,
                        },
                        {
                            "name":"b",
                            "required":True,
                            "variadic":True,
                        }
                    ]
                },
            },
        },
    },
}

