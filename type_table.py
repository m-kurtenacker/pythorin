class ThorinType:
    def __init__(self):
        self.cache = ""
    def get(self, module):
        if self.cache == "":
            self.cache = self.compile(module)
        return self.cache
    def compile(self, module):
        raise Exception("Not implemented")
    @staticmethod
    def import_type(type_entry, current_mapping):
        new_name = type_entry["name"]
        match type_entry["type"]:
            case "def_array":
                constructor = ThorinDefiniteArrayType
            case "indef_array":
                constructor = ThorinIndefiniteArrayType
            case "bottom":
                constructor = ThorinBottomType
            case "function":
                constructor = ThorinFnType
            case "closure":
                constructor = ThorinClosureType
            case "frame":
                constructor = ThorinFrameType
            case "mem":
                constructor = ThorinMemType
            case "struct":
                constructor = ThorinStructType
            case "variant":
                constructor = ThorinVariantType
            case "tuple":
                constructor = ThorinTupleType
            case "prim":
                constructor = ThorinPrimType
            case "ptr":
                constructor = ThorinPointerType
        new_type = constructor.reconstruct(type_entry, current_mapping)
        return {new_name: new_type}


class ThorinDefiniteArrayType(ThorinType):
    def __init__(self, target_type, length):
        super().__init__()
        self.target_type = target_type
        self.length = length

    def compile(self, module):
        target_type = self.target_type.get(module)

        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_def_array_" + str(save_index)

        type_table.append({"type": "def_array", "name": name, "length": self.length, "args": [target_type]})
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        new_length = type_entry["length"]
        q_args = type_entry["args"]
        args = [current_mapping[key] for key in q_args]
        return ThorinDefiniteArrayType(args[0], new_length)


class ThorinIndefiniteArrayType(ThorinType):
    def __init__(self, target_type):
        super().__init__()
        self.target_type = target_type

    def compile(self, module):
        target_type = self.target_type.get(module)

        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_indef_array_" + str(save_index)

        type_table.append({"type": "indef_array", "name": name, "args": [target_type]})
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        q_args = type_entry["args"]
        args = [current_mapping[key] for key in q_args]
        return ThorinIndefiniteArrayType(args[0])


class ThorinBottomType(ThorinType):
    def __init__(self):
        super().__init__()

    def compile(self, module):
        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_bottom_" + str(save_index)

        type_table.append({"type": "bottom", "name": name})
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        return ThorinBottomType()


class ThorinFnType(ThorinType):
    def __init__(self, args, return_type=None):
        super().__init__()
        self.args = args
        if return_type is not None:
            mem_type = ThorinMemType()
            if return_type == True:
                self.args.append(ThorinFnType([mem_type]))
            elif return_type == False:
                pass
            else:
                self.args.append(ThorinFnType([mem_type, return_type]))

    def compile(self, module):
        args = []
        for arg in self.args:
            args.append(arg.get(module))

        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_fn_" + str(save_index)

        type_table.append({"type": "function", "name": name, "args": args})
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        q_args = type_entry["args"]
        args = [current_mapping[key] for key in q_args]
        return ThorinFnType(args)


class ThorinClosureType(ThorinType):
    def __init__(self):
        super().__init__()
        assert(False)

    def compile(self, module):
        args = []
        for arg in self.args:
            args.append(arg.get(module))

        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_closure_" + str(save_index)

        type_table.append({"type": "closure", "name": name, "args": args})
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        q_args = type_entry["args"]
        args = [current_mapping[key] for key in q_args]
        return ThorinClosureType(args)


class ThorinFrameType(ThorinType):
    def __init__(self):
        super().__init__()

    def compile(self, module):
        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_frame_" + str(save_index)

        type_table.append({"type": "frame", "name": name})
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        return ThorinFrameType()


class ThorinMemType(ThorinType):
    def __init__(self):
        super().__init__()

    def compile(self, module):
        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_mem_" + str(save_index)

        type_table.append({"type": "mem", "name": name})
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        return ThorinMemType()


class ThorinStructType(ThorinType):
    def __init__(self, struct_name, formated_args=None):
        super().__init__()
        self.struct_name = struct_name
        self.formated_args = formated_args

    def compile(self, module):
        assert(self.formated_args)

        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_struct_" + str(save_index)
        self.cache = name

        arg_names = []
        for arg_name, arg in self.formated_args:
            arg_names.append(arg_name)

        type_table.append({"type": "struct", "name": name, "struct_name": self.struct_name, "arg_names": arg_names})

        args = []
        for arg_name, arg in self.formated_args:
            args.append(arg.get(module))

        type_table.append({"type": "struct", "name": name, "struct_name": self.struct_name, "arg_names": arg_names, "args": args})
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        struct_name = type_entry["struct_name"]

        if "args" in type_entry:
            old_entry = current_mapping[type_entry["name"]]
            assert(old_entry)

            arg_names = type_entry["arg_names"]
            q_args = type_entry["args"]
            args = [current_mapping[key] for key in q_args]

            formated_args = list(zip(arg_names, args))
            old_entry.formated_args = formated_args

            return old_entry
        else:
            return ThorinStructType(struct_name)


class ThorinVariantType(ThorinType):
    def __init__(self, variant_name, formated_args=None):
        super().__init__()
        self.variant_name = variant_name
        self.formated_args = formated_args

    def compile(self, module):
        assert(self.formated_args)

        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_variant_" + str(save_index)
        self.cache = name

        arg_names = []
        for name, arg in self.formated_args:
            arg_names.append(name)

        type_table.append({"type": "variant", "name": name, "variant_name": self.variant_name, "arg_names": arg_names})

        args = []
        for name, arg in self.formated_args:
            args.append(arg.get(module))

        type_table.append({"type": "variant", "name": name, "arg_names": arg_names, "args": args})
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        variant_name = type_entry["variant_name"]

        if "args" in type_entry:
            old_entry = current_mapping[type_entry["name"]]
            assert(old_entry)

            arg_names = type_entry["arg_names"]
            q_args = type_entry["args"]
            args = [current_mapping[key] for key in q_args]

            formated_args = list(zip(arg_names, args))
            old_entry.formated_args = formated_args

            return old_entry
        else:
            return ThorinStructType(variant_name)


class ThorinTupleType(ThorinType):
    def __init__(self, args):
        super().__init__()
        self.args = args

    def compile(self, module):
        args = []
        for arg in self.args:
            args.append(arg.get(module))

        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_tuple_" + str(save_index)

        type_table.append({"type": "tuple", "name": name, "args": args})
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        q_args = type_entry["args"]
        args = [current_mapping[key] for key in q_args]
        return ThorinTupleType(args)


class ThorinPrimType(ThorinType):
    def __init__(self, tag, length=1):
        super().__init__()
        self.tag = tag
        self.length = length

    def compile(self, module):
        tag = self.tag
        length = self.length

        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_prim_" + str(save_index)

        type_table.append({"type": "prim", "name": name, "tag": tag, "length": length})
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        tag = type_entry["tag"]
        if "length" in type_entry:
            length = type_entry["length"]
            return ThorinPrimType(tag, length)
        else:
            return ThorinPrimType(tag)


class ThorinPointerType(ThorinType):
    def __init__(self, pointee, length=1, device=None, addrspace=None):
        super().__init__()
        self.pointee = pointee
        self.length = length
        self.device = device
        self.addrspace = addrspace

    def compile(self, module):
        pointee = self.pointee.get(module)
        length = self.length

        type_table = module["type_table"]
        save_index = len(type_table)
        name = "_ptr_" + str(save_index)

        my_def = {"type": "ptr", "name": name, "length": length, "args": [pointee]}
        if self.device:
            my_def.update({"device": device})
        if self.addrspace:
            my_def.update({"addrspace": addrspace})

        type_table.append(my_def)
        return name

    @staticmethod
    def reconstruct(type_entry, current_mapping):
        q_args = type_entry["args"]
        args = [current_mapping[key] for key in q_args]
        if "length" in type_entry:
            length = type_entry["length"]
            return ThorinPointerType(args[0], length)
        else:
            return ThorinPointerType(args[0])
