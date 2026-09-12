# Fract'ol

## Description

Fract'ol is a computer graphics project focused on exploring and rendering mathematical fractals.

The goal of this project is to create an interactive fractal explorer capable of displaying different fractal sets, such as the **Mandelbrot set** and **Julia sets**.

The project explores concepts such as:

- Complex numbers
- Mathematical iteration
- Fractal generation
- Computer graphics
- Zooming and navigation
- Event handling
- Rendering optimization

## Instructions

### Requirements

- Python 3
- A Python virtual environment
- The required dependencies listed in `pyproject.toml`

### Installation

Clone the repository and enter the project directory:

```bash
git clone <repository-url>
cd fractol
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the project dependencies:

```bash
pip install -e .
```

### Execution

Run the program according to the available command-line options.

For example:

```bash
python -m fractol mandelbrot
```

or:

```bash
python -m fractol julia
```

The program should display a list of available options when no valid fractal type is provided.

## Resources

### Documentation and References

- Python Documentation
- Python Complex Numbers
- Mandelbrot Set - Wikipedia
- Julia Set - Wikipedia
