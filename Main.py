from typing import List, Dict, NamedTuple, Optional


class Instruction(NamedTuple):
    function: str
    argument_register_1: str
    argument_register_2: str
    result_register: str

    def is_commutative(self):
        return self.function in ["ADD", "MUL"]

    def __str__(self):
        return "{} {} {} {}".format(
            self.function,
            self.argument_register_1,
            self.argument_register_2,
            self.result_register
        )


def process_simplified(instructions: List[Instruction],
                       starting_cycle: int,
                       cycles_until_available: Dict[str, int]) -> Dict[Instruction, int]:

    def can_execute(instr: Instruction) -> bool:
        return (cycles_until_available[instr.argument_register_1] <= 0) and \
               (cycles_until_available[instr.argument_register_2] <= 1)

    result: Dict[Instruction, int] = {}
    i = 0

    while i < len(instructions):
        instruction = instructions[i]
        if can_execute(instruction):
            cycles_until_available[instruction.result_register] = 4
            result[instruction] = starting_cycle + 1
            i += 1
        starting_cycle += 1
        # print(str(self.current_cycle) + "\t" + str(self.cycles_util_available))
        cycles_until_available = \
            {key: (value - 1 if value > 0 else value) for (key, value) in cycles_until_available.items()}

    return result


def process_full(instructions: List[Instruction],
                 starting_cycle: int,
                 cycles_until_available: Dict[str, int]) -> Dict[Instruction, int]:

    def can_execute_as_is(instr: Instruction) -> bool:
        return (cycles_until_available[instr.argument_register_1] <= 0) and \
               (cycles_until_available[instr.argument_register_2] <= 1)

    def can_execute_swapped(instr: Instruction) -> bool:
        return (cycles_until_available[instr.argument_register_2] <= 0) and \
               (cycles_until_available[instr.argument_register_1] <= 1)

    def get_executable(instr: Instruction) -> Optional[Instruction]:
        if can_execute_as_is(instr):
            return instr
        if instr.is_commutative() and can_execute_swapped(instr):
            # TODO maybe swap constructor?
            return Instruction(instr.function,
                               instr.argument_register_2,
                               instr.argument_register_1,
                               instr.result_register)
        else:
            return None

    result: Dict[Instruction, int] = {}
    i = 0

    while i < len(instructions):
        instruction = instructions[i]
        executable = get_executable(instruction)
        if executable:
            cycles_until_available[instruction.result_register] = 4
            result[executable] = starting_cycle + 1
            i += 1
        starting_cycle += 1
        # print(str(self.current_cycle) + "\t" + str(self.cycles_util_available))
        cycles_until_available = \
            {key: (value - 1 if value > 0 else value) for (key, value) in cycles_until_available.items()}

    return result


def print_instructions(scheduled_instructions: Dict[Instruction, int]):
    for instruction, start_cycle in scheduled_instructions.items():
        print(str(instruction) + " " + str(start_cycle))


def load_from_file(file_path: str) -> List[Instruction]:
    instructions: List[Instruction] = []
    file = open(file_path)
    for line in file.readlines():
        a = line.split()
        instructions.append(Instruction(a[0], a[1], a[2], a[3]))
    return instructions


def registers_availability_monitor(size: int):
    return {"R{0}".format(i): 0 for i in range(0, size+1)}


list_of_instructions = load_from_file('input.txt')

instructions_simplified_variant = process_simplified(list_of_instructions, 0, registers_availability_monitor(10))
instructions_full_variant = process_full(list_of_instructions, 0, registers_availability_monitor(10))

print_instructions(instructions_simplified_variant)
print()
print_instructions(instructions_full_variant)
