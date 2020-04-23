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


class OrderedInstruction(Instruction):
    order: int

    # todo ask stackoverflow
    def __new__(cls, instruction: Instruction, order: int):
        self = super().__new__(cls, instruction.function,
                               instruction.argument_register_1,
                               instruction.argument_register_2,
                               instruction.result_register)
        self.order = order
        return self

    def __str__(self):
        return "{} {} {} {} {}".format(
            self.function,
            self.argument_register_1,
            self.argument_register_2,
            self.result_register,
            self.order
        )


def process_simplified(instructions: List[Instruction],
                       starting_cycle: int,
                       cycles_until_available: Dict[str, int]) -> List[OrderedInstruction]:

    def can_execute(instr: Instruction) -> bool:
        return (cycles_until_available[instr.argument_register_1] <= 0) and \
               (cycles_until_available[instr.argument_register_2] <= 1)

    result: List[Instruction] = []
    i = 0

    while i < len(instructions):
        instruction = instructions[i]
        if can_execute(instruction):
            cycles_until_available[instruction.result_register] = 4
            result.append(OrderedInstruction(instruction, starting_cycle+1))
            i += 1
        starting_cycle += 1
        cycles_until_available = {instruction: (cycle - 1 if cycle else cycle) for
                                  (instruction, cycle) in cycles_until_available.items()}

    return result


def process_full(instructions: List[Instruction],
                 starting_cycle: int,
                 cycles_until_available: Dict[str, int]) -> List[OrderedInstruction]:

    def can_execute_as_is(instr: Instruction) -> bool:
        return ((cycles_until_available[instr.argument_register_1] <= 0) and
                (cycles_until_available[instr.argument_register_2] <= 1))

    def can_execute_swapped(instr: Instruction) -> bool:
        return ((cycles_until_available[instr.argument_register_2] <= 0) and
                (cycles_until_available[instr.argument_register_1] <= 1))

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

    result: List[OrderedInstruction] = []
    i = 0

    while i < len(instructions):
        instruction = instructions[i]
        executable = get_executable(instruction)
        if executable:
            cycles_until_available[instruction.result_register] = 4
            result.append(OrderedInstruction(instruction, starting_cycle + 1))
            i += 1
        starting_cycle += 1
        cycles_until_available = {instruction: (cycle - 1 if cycle else cycle) for
                                  (instruction, cycle) in cycles_until_available.items()}

    return result


def process_extended(initially_optimized_instructions: Dict[Instruction, int],
                     starting_cycle: int,
                     cycles_until_available: Dict[str, int]) -> Dict[Instruction, int]:

    # defines for how many cycles the result register of this instruction will be unused
    def idle_cycles_left(instr: Instruction) -> int:
        current_instruction_starting_index = initially_optimized_instructions[instr]
        # todo fixme below list is created every time
        instructions = list(initially_optimized_instructions.keys())
        next_instruction_index = instructions.index(instr) + 1
        cycles_left = 0
        for next_instruction in instructions[next_instruction_index:]:
            if next_instruction.argument_register_1 == instr.result_register:
                next_instruction_starting_index = initially_optimized_instructions[next_instruction]
                return next_instruction_starting_index - current_instruction_starting_index - 4
            if next_instruction.argument_register_2 == instr.result_register:
                next_instruction_starting_index = initially_optimized_instructions[next_instruction]
                return next_instruction_starting_index - current_instruction_starting_index - 3
            cycles_left += 1

        return cycles_left

    idle_result_cycles: Dict[Instruction, int] = \
        {instr: idle_cycles_left(instr) for instr in initially_optimized_instructions}

    independent_instructions: List[Instruction] = [key for (key, value) in idle_result_cycles.items() if value]
    dependent_instructions: List[Instruction] = [key for (key, value) in idle_result_cycles.items() if not value]

    # result: Dict[Instruction, int] = {}
    #
    # while True:
    #     if dependent_instructions and independent_instructions:
    #         # were moving independent instruction between two dependent
    #         independent_instr = independent_instructions.pop(0)
    #         dependent_instr = dependent_instructions.pop(0)
    #
    #         if dependent_instr and independent_instr:
    #             diff = initially_optimized_instructions[dependent_instr] - initially_optimized_instructions[independent_instr]
    #             can_move = diff < idle_result_cycles[independent_instr]
    #             if can_move:
    #                 # only error = update indexes of items following the one swapped
    #                 result[dependent_instr] = initially_optimized_instructions[independent_instr]
    #                 result[independent_instr] = initially_optimized_instructions[dependent_instr]
    #             else:
    #                 result[dependent_instr] = initially_optimized_instructions[dependent_instr]
    #                 result[independent_instr] = initially_optimized_instructions[independent_instr]
    #     elif dependent_instructions:
    #         for dependent_instr in dependent_instructions:
    #             result[dependent_instr] = initially_optimized_instructions[dependent_instr]
    #         for independent_instr in independent_instructions:
    #             result[independent_instr] = initially_optimized_instructions[independent_instr]
    #         break

    result: Dict[Instruction, int] = initially_optimized_instructions.copy()

    while dependent_instructions and independent_instructions:
        # were moving independent instruction between two dependent
        independent_instr = independent_instructions.pop(0)
        dependent_instr = dependent_instructions.pop(0)

        diff = result[dependent_instr] - result[independent_instr]
        can_move = diff < idle_result_cycles[independent_instr]
        if can_move:
            result[dependent_instr], result[independent_instr] = result[independent_instr], result[dependent_instr]

            for (instr, start_cycle) in result.items():
                if instr != independent_instr and instr != dependent_instr:
                    result[instr] -= 1

    return result


def print_instructions(scheduled_instructions: Dict[Instruction, int]):
    for instruction, start_cycle in scheduled_instructions.items():
        print(str(instruction) + " " + str(start_cycle))


def print_instructions(scheduled_instructions: List[OrderedInstruction]):
    for instruction in scheduled_instructions:
        print(str(instruction))


def load_from_file(file_path: str) -> List[Instruction]:
    instructions: List[Instruction] = []
    file = open(file_path)
    for line in file.readlines():
        a = line.split()
        instructions.append(Instruction(a[0], a[1], a[2], a[3]))
    return instructions


def registers_availability_monitor(size: int):
    # TODO use xrange?
    return {"R{0}".format(i): 0 for i in range(0, size+1)}


list_of_instructions = load_from_file('input.txt')

instructions_simplified_variant = process_simplified(list_of_instructions, 0, registers_availability_monitor(10))
instructions_full_variant = process_full(list_of_instructions, 0, registers_availability_monitor(10))

# optimized_instructions = list(instructions_full_variant.keys())
#instructions_extended_variant = process_extended(instructions_full_variant, 0, registers_availability_monitor(10))

print_instructions(instructions_simplified_variant)
print()
print_instructions(instructions_full_variant)
print()
#print_instructions(instructions_extended_variant)