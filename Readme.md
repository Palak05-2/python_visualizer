# Interactive Algorithm Visualizer

A Python desktop app for the **Design and Analysis of Algorithms (DAA)** project-based learning (PBL) course. It animates sorting and searching algorithms step by step, and measures how their running time grows with input size.

## Features

- **8 algorithms**
  - Sorting: Bubble, Selection, Insertion, Merge, Quick, Heap
  - Searching: Linear, Binary
- **Step-by-step animation** with colour coding for comparisons, swaps, pivots and sorted elements
- **Controls:** Start, Pause/Resume, single Step, Reset, plus speed and array-size sliders
- **Input types:** Random, Sorted, Reversed, Nearly sorted, Few unique, or your own custom array
- **Live statistics:** comparisons, swaps/writes, steps and elapsed time
- **Algorithm info panel:** best, average and worst-case time complexity, space complexity, stability and design approach
- **Complexity Analysis window:** runs every sorting algorithm on n = 10 to 400 and plots operation counts against the theoretical n²/2 and n·log₂n curves. Use it to compare best, average and worst cases.

## Requirements

- Python 3.8 or newer
- Tkinter (included with the python.org installers)
  - Linux: `sudo apt install python3-tk`
  - macOS with Homebrew Python: `brew install python-tk`

No other packages are needed.

## How to run

```bash
python3 algo_visualizer.py
```

## How it works

Each algorithm is a Python **generator**. After every basic operation (a comparison, swap or write), it `yield`s a *frame* describing what just happened. The GUI pulls one frame at a time and redraws the bars. This design:

- makes play, pause and single-step simple to build
- keeps algorithm logic separate from drawing code
- lets the analysis mode run the exact same algorithm code without animation, just counting operations

## Colour legend

| Colour | Meaning |
|--------|---------|
| Yellow | Elements being compared |
| Red | Elements being swapped / written |
| Purple | Pivot (Quick Sort), key (Insertion Sort), mid (Binary Search) |
| Green | Element in its final sorted position |
| Teal | Search target found |
| Grey | Outside the active sub-array |

## Complexity summary

| Algorithm | Best | Average | Worst | Space | Stable |
|-----------|------|---------|-------|-------|--------|
| Bubble Sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Selection Sort | O(n²) | O(n²) | O(n²) | O(1) | No |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) | No |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | No |
| Linear Search | O(1) | O(n) | O(n) | O(1) | – |
| Binary Search | O(1) | O(log n) | O(log n) | O(1) | – |