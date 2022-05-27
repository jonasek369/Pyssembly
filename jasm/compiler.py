import argparse

nums = list("0123456789")
remove = ["", "{", "}"]

parser = argparse.ArgumentParser()

parser.add_argument("--file", type=str, help="File to assemble")
parser.add_argument("--comp", type=bool, help="Compile to cpp")
parser.add_argument("--compile", type=bool, help="Compile to cpp")
parser.add_argument("--datatype", type=str, help="Set datatype for example: long long int")
parser.add_argument("--dtype", type=str, help="Set datatype for example: long long int")


def parse_instruction(instructions):
    new = []
    for i in instructions:
        if i not in remove:
            new.append(i)
    return " ".join(new)


class VariableDoseNotExist(Exception):
    pass


def compile(program, strict=True, data_type="long long int", *memory):
    if strict:
        CPP_FILE = """#include <iostream>\nint main(){"""
    else:
        CPP_FILE = """"""
    if memory:
        memory = memory[0]
    else:
        memory = {}
    instructions = program
    instruct_pointer = 0

    jnzs = []
    for i in range(len(instructions)):
        scan = instructions[i].split(" ")
        if scan[0] == "jnz":
            jnzs.append({"instruct": i, "jnz_val": int(scan[2]), "point": scan[1]})

    while True:
        if len(instructions) == instruct_pointer:
            break

        disassemble = instructions[instruct_pointer].split(" ")
        if disassemble[0] == ";":
            instruct_pointer += 1
            continue

        for i in jnzs:
            if instruct_pointer == i["jnz_val"] + i["instruct"]:
                CPP_FILE += f"for({i['point']};{i['point']}!=0;)" + "{"

        if disassemble[0] == "mov":
            memory[f"VAR_{disassemble[1]}"] = True
            CPP_FILE += f"{data_type} {disassemble[1]}={disassemble[2]};"
        if disassemble[0] == "add":
            CPP_FILE += f"{disassemble[1]}={disassemble[2]}+{disassemble[3]};"
        elif disassemble[0] == "inc":
            CPP_FILE += f"{disassemble[1]}++;"
        elif disassemble[0] == "dec":
            CPP_FILE += f"{disassemble[1]}--;"
        elif disassemble[0] == "out":
            CPP_FILE += f"std::cout<<{disassemble[1]}<<std::endl;"
        elif disassemble[0] == "cpp":
            CPP_FILE += " ".join(disassemble[1:])
        elif disassemble[0] == "ret":
            CPP_FILE += f"return {disassemble[1]};"

        # crating function
        elif disassemble[0].startswith("."):
            func_ins_pointer = instruct_pointer

            start = instruct_pointer
            end = None

            while True:
                if end is not None:
                    break
                disassemble = instructions[func_ins_pointer].split(" ")
                for i in disassemble:
                    if "}" in i and disassemble[0] != "cpp":
                        end = func_ins_pointer + 1
                        break
                func_ins_pointer += 1
            FUNC_NAME = ""
            PARAMS = ""
            func_instructions = []
            for i in range(start, end):
                disassemble = instructions[i].split(" ")
                if disassemble[0].startswith("."):
                    full = "".join(disassemble)[1:]
                    FUNC_NAME = full[:full.find("(")]
                    func_params = (full[full.find("(") + 1:full.find(")")]).strip().split(",")
                    memory[f"{FUNC_NAME}_PARAMS"] = len(func_params)
                    func_params_CPP = ""
                    for pos, i in enumerate(func_params):
                        if pos == len(func_params) - 1:
                            func_params_CPP += f"{data_type} {i}"
                        else:
                            func_params_CPP += f"{data_type} {i},"
                    PARAMS = func_params_CPP
                else:
                    instruct = parse_instruction(disassemble)
                    func_instructions.append(instruct)
            contain = compile(func_instructions, False, data_type, memory)
            SOURCE = f"{data_type} {FUNC_NAME}({PARAMS})" + "{" + contain + "}"
            main_func = CPP_FILE.find("int main()")
            CPP_FILE = f"{CPP_FILE[:main_func]}{SOURCE}{CPP_FILE[main_func:]}"
            #CPP_FILE = f"#include <iostream>\n{SOURCE}{CPP_FILE[cppend + 1:]}"

        # calling function
        elif disassemble[0].startswith("call"):
            FUNC_NAME = disassemble[1]
            params = memory[f"{FUNC_NAME}_PARAMS"]
            params = [disassemble[i] for i in range(2, params + 2)]
            put_to = disassemble[-1]
            put_to_exist = False
            if memory.get(f"VAR_{put_to}"):
                put_to_exist = True
            for i in params:
                if i == put_to:
                    continue
                if not memory.get(f"VAR_{i}"):
                    try:
                        int(i)
                    except ValueError:
                        raise VariableDoseNotExist(
                            f"Your trying to put variable {i} into function {FUNC_NAME} as parameter but {i} is not defined")
            func_params_CPP = ""
            for pos, i in enumerate(params):
                if pos == len(params) - 1:
                    func_params_CPP += f"{i}"
                else:
                    func_params_CPP += f"{i},"
            if put_to_exist:
                CPP_FILE += f"{put_to} = {FUNC_NAME}({func_params_CPP});"
            else:
                memory[f"VAR_{put_to}"] = True
                CPP_FILE += f"{data_type} {put_to} = {FUNC_NAME}({func_params_CPP});"
        for i in jnzs:
            if instruct_pointer == i["instruct"]:
                CPP_FILE += "}"

        instruct_pointer += 1
    if strict:
        CPP_FILE += "return 0;}"
    return CPP_FILE


stack = []

args = parser.parse_args()

datatype = "int"

if args.dtype is not None:
    datatype = args.dtype

if args.datatype is not None:
    datatype = args.dtype

if args.file is not None:
    with open(args.file, "r") as file:
        file_content = file.read()
        stack = file_content.splitlines()

if args.compile or args.comp:
    with open("main.cpp", "w") as file:
        x = compile(stack, True, datatype)
        file.write(x)

print("Compilation completed !")