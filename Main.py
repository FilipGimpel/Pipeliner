from typing import List, Dict


class Instruction:
    function: str
    argument_register_1: str
    argument_register_2: str
    result_register: str

    def __init__(self, instruction: List[str]):
        self.function = instruction[0]
        self.argument_register_1 = instruction[1]
        self.argument_register_2 = instruction[2]
        self.result_register = instruction[3]

    def __str__(self):
        return "{} {} {} {}".format(
            self.function,
            self.argument_register_1,
            self.argument_register_2,
            self.result_register
        )

    def is_commutative(self):
        return self.function in ["ADD", "MUL"]

    def swap_arguments(self):
        self.argument_register_1, self.argument_register_2 = self.argument_register_2, self.argument_register_1


class Pipeliner:
    cycles_until_available: Dict[str, int] = {}
    instructions: List[Instruction] = []  # TODO do I need this? I use it in only one function, maybe just pass?
    current_cycle = 0

    def __init__(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.cycles_until_available = {"R{0}".format(i): 0 for i in range(0, 10)}

    def process(self):
        while self.instructions:
            instruction = self.instructions[0]
            if self.can_execute(instruction):
                self.cycles_until_available[instruction.result_register] = 4
                print(str(instruction) + " " + str(self.current_cycle + 1))  # TODO Use stringbuffer kinda thing?
                self.instructions.remove(instruction)
            self.cycle()

    def can_execute(self, instruction: Instruction) -> bool:
        if self.can_execute_as_is(instruction):
            return True
        elif instruction.is_commutative() and self.can_execute_swapped(instruction):
            instruction.swap_arguments()
            return True
        else:
            return False

    def can_execute_as_is(self, instruction: Instruction) -> bool:
        return (self.cycles_until_available[instruction.argument_register_1] <= 0) and \
               (self.cycles_until_available[instruction.argument_register_2] <= 1)

    def can_execute_swapped(self, instruction: Instruction) -> bool:
        return (self.cycles_until_available[instruction.argument_register_2] <= 0) and \
               (self.cycles_until_available[instruction.argument_register_1] <= 1)

    def cycle(self):
        self.current_cycle += 1
        # print(str(self.current_cycle) + "\t" + str(self.cycles_until_available))
        self.cycles_until_available = \
            {key: (value - 1 if value > 0 else value) for (key, value) in self.cycles_until_available.items()}


def load_from_file(file_path: str) -> List[Instruction]:
    instructions: List[Instruction] = []
    file = open(file_path)
    for line in file.readlines():
        a = line.split()
        instructions.append(Instruction(a))
    return instructions


# print()
# Pipeliner(list_of_instructions).process()


list_of_instructions = load_from_file('input.txt')


def process_simplified(instructions: List[Instruction],
                       starting_cycle: int,
                       cycles_util_available: Dict[str, int]) -> Dict[Instruction, int]:

    def can_execute(instr: Instruction) -> bool:
        return (cycles_util_available[instr.argument_register_1] <= 0) and \
               (cycles_util_available[instr.argument_register_2] <= 1)

    result: Dict[Instruction, int] = {}

    while instructions:
        instruction = instructions[0]
        if can_execute(instruction):
            cycles_util_available[instruction.result_register] = 4
            result[instruction] = starting_cycle + 1
            instructions.remove(instruction)
        starting_cycle += 1
        # print(str(self.current_cycle) + "\t" + str(self.cycles_util_available))
        cycles_util_available = \
            {key: (value - 1 if value > 0 else value) for (key, value) in cycles_util_available.items()}

    return result


def print_instructions(scheduled_instructions: Dict[Instruction, int]):
    for instruction, start_cycle in scheduled_instructions.items():
        print(str(instruction) + " " + str(start_cycle))


def registers_availability_monitor(size: int):
    return {"R{0}".format(i): 0 for i in range(0, size+1)}


instructions_simplified_variant = process_simplified(list_of_instructions, 0, registers_availability_monitor(10))
print_instructions(instructions_simplified_variant)
