from typing import List, Dict


# filename as script argument
# maybe do it on the fly?
def load_instructions_from_file(file_path: str) -> List[List[str]]:
    instructions: List[List[str]] = []
    file = open(file_path)
    for line in file.readlines():
        a = line.split()
        instructions.append(a)
    return instructions


class Pipeliner:
    register: Dict[str, int] = {}  # better indexing
    instructions: List[List[str]] = []
    current_cycle = 0

    def __init__(self, instructions: List[List[str]]):
        self.instructions = instructions
        for i in range(0, 10):
            self.register["R"+str(i)] = 0  # use generator expressions to initialize

    def process(self):
        if self.instructions:
            current_instruction = self.instructions[0]
            if self.can_execute(current_instruction):
                self.instructions.pop(0)
                self.register[current_instruction[3]] = 4

    def process_while(self):
        while self.instructions:
            instruction = self.instructions[0]
            if self.can_execute(instruction):
                self.register[instruction[3]] = 4
                print(str(instruction) + " " + str(self.current_cycle + 1))
                self.instructions.pop(0)  # self.instructions.remove(instruction)
            if sum(self.register.values()) == 0:
                break
            self.cycle()

    def can_execute(self, instruction: List[str]) -> bool:  # create instruction class?
        return (self.register[instruction[1]] <= 0) and (self.register[instruction[2]] <= 1)

    def cycle(self):
        self.current_cycle += 1
        # print(str(self.current_cycle) + "\t" + str(self.register))
        self.register = {key: (value - 1 if value > 0 else value) for (key, value) in self.register.items()}


list_of_instructions = load_instructions_from_file('input.txt')
Pipeliner(list_of_instructions).process_while()

# SIMPLE
# 1. Jezeli lista instrukcji do wykonania nie jest pusta, wez z niej instrukcje
# 2. Jeżeli możesz wykonać instrukcję*, do listy rejstrow z wynikami dodaj rejstr do ktorego dana instrukcja wrzuci wynik, ustaw mu wartosc 4 (za ile cyklow wynik bedzie dostepny)
# 3. Wykonaj cykl**