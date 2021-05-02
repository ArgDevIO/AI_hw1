from constraint import *


def get_character_distance(char1, char2):
    return abs(ord(char1.upper()) - ord(char2.upper()))


def check_adjacent(a, b):
    if get_character_distance(a, b) > 1:
        return True
    return False


if __name__ == "__main__":
    problem = Problem(BacktrackingSolver())

    variables = ['лав', 'тигар', 'папагал', 'срна', 'жирафа', 'питон', 'газела']
    domain = ['A', 'B', 'C', 'D']

    problem.addVariables(variables, domain)

    problem.addConstraint(lambda a: a == "A", ("лав",))

    problem.addConstraint(lambda a, b: a == b, ('жирафа', 'газела'))

    problem.addConstraint(lambda a, b, c: a != c and b != c, ('лав', 'тигар', 'срна'))

    problem.addConstraint(lambda a, b: check_adjacent(a, b), ("лав", "срна"))
    problem.addConstraint(lambda a, b: check_adjacent(a, b), ("тигар", "срна"))

    problem.addConstraint(lambda a, b: a != b, ('лав', 'тигар'))

    problem.addConstraint(lambda a, b, c, d, e, f: a != b and a != c and a != d and a != e and a != f,
                          ('питон', 'лав', 'папагал', 'срна', 'жирафа', 'газела'))

    problem.addConstraint(lambda a, b, c, d: a != b and a != c and a != d,
                          ('тигар', 'жирафа', 'газела', 'папагал'))

    problem.addConstraint(lambda a, b: a != b, ('папагал', 'лав'))

    solutions = problem.getSolutions()

    print(f"# Total solutions: {len(solutions)}")

    for solution in solutions:
        print(solution)
