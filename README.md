# Universal Turing Machine: A Visual Interpreter and Simulator

This repository contains a complete implementation of a Universal Turing Machine (UTM) written in Python, featuring an interactive visualizer built with Pygame.


## Project Origin: A Challenge Accepted

This project began in a somewhat unconventional way. A colleague undertaking his master's degree at the Instituto Politécnico Nacional (IPN) was tasked with implementing a UTM based on a professor's formal language specification. When he found himself stuck, the problem caught my attention.

Intrigued by the challenge of translating a dense, theoretical specification into a functional, living system, I decided to take it on myself. This repository is the result of that endeavor. The core mission was to engineer a robust interpreter that could not only execute the specified language but also make the abstract process of Turing computation visual and understandable.

## Key Features

*   **Specification-Driven Interpreter:** The interpreter is a faithful implementation of the IPN professor's language specification. It parses the custom syntax, handles states, multiple symbols, `while` loops, and all specified transition cases.
*   **Interactive Visualizer:** A GUI built with Pygame allows users to load programs written in this language, set an initial input, and execute the machine step-by-step or continuously, providing a clear view of the computation as it unfolds.
*   **Dynamic Infinite Tape:** The machine simulates an infinite tape that dynamically grows in both directions as needed, providing a theoretically correct implementation.
*   **Library of Classic Algorithms:** To validate the interpreter and demonstrate the language's capabilities, this repository includes several canonical computer science algorithms, implemented according to the specification.

## My Role and Process

My role was that of a **problem-solver and systems engineer.** Starting with the same PDF specification given to the master's student, I architected and implemented the entire system from the ground up. This involved:

1.  **Deconstructing the Specification:** Deeply analyzing the formal language to understand its rules, structure, and edge cases.
2.  **Designing the Interpreter:** Architecting the core data structures (for instructions, the tape, and the machine state) and the logic engine (`do_q_z`) to faithfully execute the language.
3.  **Building the Parser:** Writing the `tokenize` function to translate the text-based language into an executable format.
4.  **Developing the Visualizer:** Creating the Pygame GUI to provide a clear and interactive window into the machine's complex operations.

This process was accelerated through a pair-programming dynamic with an advanced LLM, which served as a tool for rapidly prototyping ideas and debugging, allowing me to focus on the core architectural and logical challenges.

## Example Programs

The repository includes the following programs written in the UTM's language:

*   `sum_two_bin_strings.txt`: Adds two binary numbers.
*   `palindrome.txt`: Recognizes whether a given binary string is a palindrome.
*   `triplicate_input.txt`: Creates three copies of an input string.
*   `two_complement.txt`: Calculates the two's complement of a binary number.
*   `bsort.txt`: Sorts a binary string using the Bubble Sort algorithm.

Each of these programs was designed to test a different aspect of the machine and to explore the limits of computation at this fundamental level.

## Getting Started

1.  Clone this repository.
2.  Ensure you have Python and Pygame installed:
    ```bash
    pip install pygame
    ```
3.  Run the main application:
    ```bash
    python gui.py
    ```
4.  Use the **"Load Prog."** button to load one of the `.txt` program files.
5.  Use the **"Input"** button to set the initial tape.
6.  Explore computation in its purest form!

---