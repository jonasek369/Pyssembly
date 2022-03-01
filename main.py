import argparse

import sys

parser = argparse.ArgumentParser()

parser.add_argument("--file", type=str, help="File to assemble")
parser.add_argument("--sim", type=bool, help="Simulate")
parser.add_argument("--simulate", type=bool, help="Simulate")

nums = list("0123456789")


def compile(program):
    memory = {"GOTO": -1, "GOTO_IP": -1}
    instructions = program
    instruct_pointer = 0
    while True:
        if len(instructions) == instruct_pointer:
            break

        if memory["GOTO"] != -1 and memory["GOTO_IP"] != -1:
            if memory["GOTO_IP"] == instruct_pointer:
                instruct_pointer = memory["GOTO"]
                memory["GOTO"] = -1
                memory["GOTO_IP"] = -1
            else:
                disassemble = instructions[instruct_pointer][4:].split(" ")
        else:
            disassemble = instructions[instruct_pointer].split(" ")

        if disassemble[0].startswith(";"):
            instruct_pointer += 1
            continue
        elif disassemble[0] == "mov":
            if disassemble[2] in memory:
                if disassemble[1] == "MEM_POINTER":
                    continue
                memory[disassemble[1]] = memory[disassemble[2]]
            else:
                memory[disassemble[1]] = int(disassemble[2])
        elif disassemble[0] == "inc":
            if disassemble[1] in memory:
                if disassemble[1] == "MEM_POINTER":
                    continue
                memory[disassemble[1]] += 1
            else:
                pass
        elif disassemble[0] == "dec":
            if disassemble[1] in memory:
                if disassemble[1] == "MEM_POINTER":
                    continue
                memory[disassemble[1]] -= 1
            else:
                pass
        elif disassemble[0] == "jnz":
            if disassemble[1] in memory:
                if memory[disassemble[1]] != 0:
                    instruct_pointer += int(disassemble[2])
                    continue
            else:
                if disassemble[1] != 0:
                    instruct_pointer += int(disassemble[2])
                    continue
        elif disassemble[0] == "jnp":
            # jump if not positibe
            if disassemble[1] in memory:
                if memory[disassemble[1]] > 0:
                    instruct_pointer += int(disassemble[2])
                    continue
            else:
                if disassemble[1] > 0:
                    instruct_pointer += int(disassemble[2])
                    continue
        elif disassemble[0] == "jmp":
            instruct_pointer = int(disassemble[1])
            continue
        elif disassemble[0] == "del":
            if disassemble[1] in memory:
                del memory[disassemble[1]]
            else:
                pass
        elif disassemble[0] == "pmem":
            print(memory)
        elif disassemble[0] == "out":
            for item in disassemble[1:]:
                if item in memory:
                    wrt = str(memory[item])
                    sys.stdout.write(wrt)
                else:
                    wrt = str(item)
                    sys.stdout.write(wrt)
                sys.stdout.write(" ")
            sys.stdout.write("\n")
        elif ":" in instructions[instruct_pointer]:
            ins_strp = instructions[instruct_pointer].strip()
            FUNC_NAME = ins_strp[:ins_strp.find(":")].strip()
            _PARAM_NUM = ins_strp[ins_strp.find(":"):ins_strp.rfind(":")].strip()
            PARAM_NUM = int("".join([i for i in _PARAM_NUM if i in nums]))
            for x in range(0, PARAM_NUM):
                memory[f"{FUNC_NAME}_PARAM{x + 1}"] = 0
            memory[f"{FUNC_NAME}_RET"] = 0
            start = None
            last = None
            finish = None
            for x in range(instruct_pointer + 1, len(instructions)):
                if [ord(w) for w in instructions[x][0:4]] == [32, 32, 32, 32]:
                    if start is None:
                        start = x
                if last is True and not [ord(w) for w in instructions[x][0:4]] == [32, 32, 32, 32]:
                    finish = x - 1
                    break
                last = instructions[x].startswith("    ")
            memory[f"{FUNC_NAME}_START"] = start
            memory[f"{FUNC_NAME}_END"] = finish
            instruct_pointer = finish + 1
            continue
        elif "call" == disassemble[0]:
            if f"{disassemble[1]}_START" in memory:
                memory["GOTO"] = instruct_pointer + 1
                memory["GOTO_IP"] = memory[f"{disassemble[1]}_END"] + 1
                instruct_pointer = memory[f"{disassemble[1]}_START"] - 1
        instruct_pointer += 1
    return memory


stack = []

args = parser.parse_args()

if args.file is not None:
    with open(args.file, "r") as file:
        file_content = file.read()
        stack = file_content.splitlines()

if args.simulate or args.sim:
    compile(stack)
