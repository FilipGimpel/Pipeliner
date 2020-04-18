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


class PipelinerSimplified:
    cycles_util_available: Dict[str, int] = {}
    instructions: List[Instruction] = []  # TODO do I need this? I use it in only one function, maybe just pass?
    current_cycle = 0

    def __init__(self, instructions: List[Instruction]):
        self.instructions = instructions
        self.cycles_util_available = {"R{0}".format(i): 0 for i in range(0, 10)}

    def process(self):
        while self.instructions:
            instruction = self.instructions[0]
            if self.can_execute(instruction):
                self.cycles_util_available[instruction.result_register] = 4
                print(str(instruction) + " " + str(self.current_cycle + 1))  # TODO Use stringbuffer kinda thing?
                self.instructions.remove(instruction)
            if sum(self.cycles_util_available.values()) == 0:
                break
            self.cycle()

    def can_execute(self, instruction: Instruction) -> bool:
        return (self.cycles_util_available[instruction.argument_register_1] <= 0) and \
               (self.cycles_util_available[instruction.argument_register_2] <= 1)

    def cycle(self):
        self.current_cycle += 1
        # print(str(self.current_cycle) + "\t" + str(self.register))
        self.cycles_util_available = \
            {key: (value - 1 if value > 0 else value) for (key, value) in self.cycles_util_available.items()}


def load_from_file(file_path: str) -> List[Instruction]:
    instructions: List[Instruction] = []
    file = open(file_path)
    for line in file.readlines():
        a = line.split()
        instructions.append(Instruction(a))
    return instructions


list_of_instructions = load_from_file('input.txt')
PipelinerSimplified(list_of_instructions).process()


# SIMPLE
# 1. Jezeli lista instrukcji do wykonania nie jest pusta, wez z niej instrukcje
# 2. Jeżeli możesz wykonać instrukcję*, do listy rejstrow z wynikami dodaj rejstr do ktorego dana instrukcja wrzuci wynik, ustaw mu wartosc 4 (za ile cyklow wynik bedzie dostepny)
# 3. Wykonaj cykl**