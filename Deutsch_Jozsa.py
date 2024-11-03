import numpy as np
from prettytable import PrettyTable
import math
import sys

# Implementa la clase Hadamard que permite aplicar la compuerta de Hadamard a un número de qubits n
class Hadamard():
    def __init__(self):
        self.Hadamard = np.array([[1,1],[1,-1]]) / np.sqrt(2)
        self.matrix = self.Hadamard

    # Se genera la matriz de Hadamard de n qubits por medio de producto tensorial sucesivo
    def add_qubits(self, num_qubits):
        for qubit in range(num_qubits - 1):
            self.matrix = np.kron(self.Hadamard, self.matrix)

    def apply(self, state):
        return self.matrix @ state

# Implementa la clase X_last_qubit que permite aplicar la compuerta X al último qubit de un número de qubits n
# Se utiliza para negar el qubit de ancilla
class X_last_qubit():
    def __init__(self, num_qubits):
        self.X = np.array([[0,1],[1,0]])
        self.identity = np.eye(2 ** (num_qubits - 1))
        self.matrix = np.kron(self.identity, self.X)

    def apply(self, state):
        return self.matrix @ state

# Se obtiene la función oraculo utilizada en el algoritmo en forma de matriz
# Se recibe la funcion como numero binario y la dimension del espacio de Hilbert en que se está trabajando
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

# Se ejecuta el algoritmo de Deutsch-Jozsa para una función f y un número de qubits n
# Retorna el vector con el estado del sistema
def Deutsch_Jocza(f, n):
    num_qubits = n
    dim_hilbert = 2 ** num_qubits

    # Se crean las compuertas cuanticas a utilizar
    H = Hadamard()
    H.add_qubits(num_qubits)
    X = X_last_qubit(num_qubits)

    U = get_U(f, dim_hilbert)

    # Se crean el vector de estados iniciales
    s0 = np.zeros(dim_hilbert)
    s0[0] = 1

    # Applicación del algoritmo
    s1 = X.apply(s0)
    s2 = H.apply(s1)
    s3 = U @ s2
    s4 = H.apply(s3)
    return s4

# Calculate the probability that the state is (|0>⊗n)⊗|y> or not
def prob_0_or_1(state):
    prob_0 = state[0] ** 2 + state[1] ** 2
    prob_1 = 1 - prob_0
    return prob_0, prob_1

# Count the amount of ones and basedd on it determine the true result
def classical_oracle(f, n):
    one_amount = number_of_ones(f)
    if one_amount == n/2:
        return "balanced"
    elif one_amount == 0 or one_amount == n:
        return "constant"
    else:
        return "neither"

# Count the number of ones in a binary string
def number_of_ones(n):
    return bin(n).count('1')

# Iterate over all possible functions on binary strings of length n and apply Deutsch-Jozsa
# Return a table with the results
def run_all_DeutschJozsa(n):
    table = PrettyTable()
    table.field_names = ["Función", "Es balanceada", "Es constante", "Numero bits en 1", "P(|0>⊗n)", "1 - P(|0>⊗n)"]
    
    num_functions = 2 ** (2 ** n)
    len_f = 2 ** n
    num_qubits = n + 1
    balanced_count = 0

    for i in range(num_functions):
        result_state = Deutsch_Jocza(i, num_qubits) 
        classical_measure = classical_oracle(i, len_f)  

        if classical_measure == 'balanced':
            balanced_count += 1

        prob_0_or_1_result = prob_0_or_1(result_state)
        prob_0 = str(round(prob_0_or_1_result[0] * 100, 1)) + "%"
        prob_1 = str(round(prob_0_or_1_result[1] * 100, 1)) + "%"

        table.add_row([f"{i:0{len_f}b}", "Sí" if (classical_measure == 'balanced') else "No", "Sí" if (classical_measure == 'constant') else "No", number_of_ones(i), prob_0, prob_1])

    return table

def main():
    if len(sys.argv) != 2:
        print("Usage: python Deutsch_Jozsa.py <input_element_length>")
        sys.exit(1)

    try:
        n = int(sys.argv[1])
    except ValueError:
        print("The number of qubits must be an integer.")
        sys.exit(1)

    res = run_all_DeutschJozsa(n)
    print(res)

if __name__ == "__main__":
    main()

