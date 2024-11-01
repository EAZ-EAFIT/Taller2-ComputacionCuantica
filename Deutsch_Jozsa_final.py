import numpy as np
from prettytable import PrettyTable
import math
import sys

class Hadamard():
    def __init__(self):
        self.Hadamard = np.array([[1,1],[1,-1]]) / np.sqrt(2)
        self.matrix = self.Hadamard

    def add_qubits(self, num_qubits):
        for qubit in range(num_qubits - 1):
            self.matrix = np.kron(self.Hadamard, self.matrix)

    def apply(self, state):
        return self.matrix @ state

class X_last_qubit():
    def __init__(self, num_qubits):
        self.X = np.array([[0,1],[1,0]])
        self.identity = np.eye(2 ** (num_qubits - 1))
        self.matrix = np.kron(self.identity, self.X)

    def apply(self, state):
        return self.matrix @ state

def get_U(f, dim_hilbert):
    U = np.zeros((dim_hilbert, dim_hilbert))
    for i in range(dim_hilbert//2):
        i = i * 2
        f_x = f % 2
        f = f // 2

        x = i
        u_applied = x + 0 ^ f_x
        U[i][u_applied] = 1

        u_applied2 = x + 1 ^ f_x
        U[i+1][u_applied2] = 1
    return U

def Deutsch_Jocza(f, n):
    num_qubits = n
    dim_hilbert = 2 ** num_qubits

    H = Hadamard()
    H.add_qubits(num_qubits)
    X = X_last_qubit(num_qubits)

    U = get_U(f, dim_hilbert)

    s0 = np.zeros(dim_hilbert)
    s0[0] = 1

    s1 = X.apply(s0)
    s2 = H.apply(s1)
    s3 = U @ s2
    s4 = H.apply(s3)
    return s4

def balanced_or_constant(state):
    if abs(state[0]) > 1e-10 or abs(state[1]) > 1e-10:
        return "constant"
    else:
        return "balanced"
    
def prob_0_or_1(state):
    prob_0 = state[0] ** 2 + state[1] ** 2
    prob_1 = 1 - prob_0
    return prob_0, prob_1
    
def classical_oracle(f, n):
    one_amount = number_of_ones(f)
    if one_amount == n/2:
        return "balanced"
    elif one_amount == 0 or one_amount == n:
        return "constant"
    else:
        return "neither"
    
def number_of_ones(n):
    return bin(n).count('1')

def run_all_DeutschJozsa(n):
    table = PrettyTable()
    table.field_names = ["Función", "Es balanceada", "Es constante", "Numero bits en 1", "P(|0>⊗n)", "1 - P(|0>⊗n)"]
    
    num_functions = 2 ** (2 ** n)
    len_f = 2 ** n
    num_qubits = n + 1
    balanced_count = 0

    for i in range(num_functions):
        result_state = Deutsch_Jocza(i, num_qubits) 
        measure = balanced_or_constant(result_state)
        classical_measure = classical_oracle(i, len_f)  

        if classical_measure == 'balanced':
            balanced_count += 1

        prob_0_or_1_result = prob_0_or_1(result_state)
        prob_0 = str(int(round(prob_0_or_1_result[0], 0) * 100)) + "%"
        prob_1 = str(int(round(prob_0_or_1_result[1], 0) * 100)) + "%"

        if classical_measure == "balanced" and measure == "constant":
            print("Error: Función balanceada clasificada como constante")

        # result = "0: " + str(prob_0) + "%" + " 1: " + str(prob_1) + "%" 

        table.add_row([f"{i:0{len_f}b}", "Sí" if (classical_measure == 'balanced') else "No", "Sí" if (classical_measure == 'constant') else "No", number_of_ones(i), prob_0, prob_1])

    return table, balanced_count



def combinatoric_balanced(len_f):
    result = math.factorial(len_f)
    result = result / (math.factorial(len_f // 2) ** 2)
    return result


def main():
    if len(sys.argv) != 2:
        print("Usage: python Deutsch_Jozsa.py <number_of_qubits>")
        sys.exit(1)

    try:
        num_qubits = int(sys.argv[1])
    except ValueError:
        print("The number of qubits must be an integer.")
        sys.exit(1)

    res = run_all_DeutschJozsa(num_qubits)
    print(res[0])
    print(f"Total de funciones balanceadas: {res[1]}")
    print(f"Total de funciones balanceadas real: {combinatoric_balanced(2 ** num_qubits)}")

if __name__ == "__main__":
    main()

