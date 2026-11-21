"""
Interactive Algorithm Visualizer  -  DAA Project
=================================================
Visualises sorting and searching algorithms step by step and lets you
empirically analyse their time complexity (best / average / worst case).

Run:   python algo_visualizer.py
Needs: Python 3.8+ (Tkinter is included with standard Python)

Algorithms
  Sorting  : Bubble, Selection, Insertion, Merge, Quick, Heap
  Searching: Linear, Binary

Every algorithm is written as a Python *generator*: after each basic
operation (comparison / swap / write) it `yield`s a frame describing what
just happened. The GUI pulls one frame at a time, which gives us
play / pause / single-step for free and keeps algorithm code separate from
drawing code.
"""

import random
import sys
import time
import math
import tkinter as tk
from tkinter import ttk, messagebox

sys.setrecursionlimit(10000)

# --------------------------------------------------------------------------
#  Theme
# --------------------------------------------------------------------------
BG = "#1e1e2e"
PANEL = "#2a2a3d"
FG = "#e0e0f0"
MUTED = "#8a8aa8"
BAR = "#7aa2f7"
COMPARE = "#f9e2af"   # yellow  - elements being compared
SWAP = "#f38ba8"      # red     - elements being swapped / written
SORTED = "#a6e3a1"    # green   - element in final position
PIVOT = "#cba6f7"     # purple  - pivot (quick sort) / mid (binary search)
DIM = "#45475a"       # grey    - outside the active sub-array
FOUND = "#94e2d5"     # teal    - search hit


class Stats:
    """Counts the basic operations an algorithm performs."""

    def __init__(self):
        self.comparisons = 0
        self.swaps = 0      # swaps for exchange sorts, writes for merge/insertion


# --------------------------------------------------------------------------
#  Sorting algorithms (generators)
#  Each frame is a dict that may contain:
#    compare=(i, j)  swap=(i, j)  write=i  pivot=i  range=(lo, hi)
#    sorted=set_of_indices  found=i  msg="text"
# --------------------------------------------------------------------------
def bubble_sort(a, st, target=None):
    n = len(a)
    done = set()
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            st.comparisons += 1
            yield {"compare": (j, j + 1), "sorted": done,
                   "msg": f"Compare a[{j}]={a[j]} and a[{j+1}]={a[j+1]}"}
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                st.swaps += 1
                swapped = True
                yield {"swap": (j, j + 1), "sorted": done,
                       "msg": f"Swap -> a[{j}]={a[j]}, a[{j+1}]={a[j+1]}"}
        done.add(n - 1 - i)
        if not swapped:          # early exit -> O(n) best case
            break


def selection_sort(a, st, target=None):
    n = len(a)
    done = set()
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            st.comparisons += 1
            yield {"compare": (m, j), "pivot": m, "sorted": done,
                   "msg": f"Current min a[{m}]={a[m]}  vs  a[{j}]={a[j]}"}
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]
            st.swaps += 1
            yield {"swap": (i, m), "sorted": done,
                   "msg": f"Place minimum {a[i]} at index {i}"}
        done.add(i)


def insertion_sort(a, st, target=None):
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        yield {"pivot": i, "range": (0, i), "msg": f"Insert key = {key}"}
        while j >= 0:
            st.comparisons += 1
            yield {"compare": (j, j + 1), "range": (0, i),
                   "msg": f"Is a[{j}]={a[j]} > key {key}?"}
            if a[j] <= key:
                break
            a[j + 1] = a[j]
            st.swaps += 1
            a[j] = key
            yield {"swap": (j, j + 1), "range": (0, i),
                   "msg": f"Shift {a[j+1]} right"}
            j -= 1


def merge_sort(a, st, target=None):
    def ms(lo, hi):                      # sorts a[lo:hi]
        if hi - lo <= 1:
            return
        mid = (lo + hi) // 2
        yield from ms(lo, mid)
        yield from ms(mid, hi)
        left, right = a[lo:mid], a[mid:hi]
        i = j = 0
        k = lo
        while i < len(left) and j < len(right):
            st.comparisons += 1
            yield {"compare": (k, mid + j if mid + j < hi else k),
                   "range": (lo, hi - 1),
                   "msg": f"Merge [{lo}..{hi-1}]: compare {left[i]} and {right[j]}"}
            if left[i] <= right[j]:
                a[k] = left[i]
                i += 1
            else:
                a[k] = right[j]
                j += 1
            st.swaps += 1
            yield {"write": k, "range": (lo, hi - 1), "msg": f"Write {a[k]} at index {k}"}
            k += 1
        for v in left[i:] + right[j:]:
            a[k] = v
            st.swaps += 1
            yield {"write": k, "range": (lo, hi - 1), "msg": f"Copy remaining {v} to index {k}"}
            k += 1
    yield from ms(0, len(a))


def quick_sort(a, st, target=None):
    done = set()

    def qs(lo, hi):
        if lo > hi:
            return
        if lo == hi:
            done.add(lo)
            return
        pivot = a[hi]                    # Lomuto partition, last element pivot
        i = lo
        for j in range(lo, hi):
            st.comparisons += 1
            yield {"compare": (j, hi), "pivot": hi, "range": (lo, hi), "sorted": done,
                   "msg": f"Partition [{lo}..{hi}]: is {a[j]} < pivot {pivot}?"}
            if a[j] < pivot:
                if i != j:
                    a[i], a[j] = a[j], a[i]
                    st.swaps += 1
                    yield {"swap": (i, j), "pivot": hi, "range": (lo, hi), "sorted": done,
                           "msg": f"Move {a[i]} to left side"}
                i += 1
        if i != hi:
            a[i], a[hi] = a[hi], a[i]
            st.swaps += 1
        done.add(i)
        yield {"swap": (i, hi), "sorted": done, "range": (lo, hi),
               "msg": f"Pivot {a[i]} fixed at index {i}"}
        yield from qs(lo, i - 1)
        yield from qs(i + 1, hi)

    yield from qs(0, len(a) - 1)


def heap_sort(a, st, target=None):
    n = len(a)
    done = set()

    def sift_down(root, end):
        while 2 * root + 1 < end:
            child = 2 * root + 1
            if child + 1 < end:
                st.comparisons += 1
                yield {"compare": (child, child + 1), "range": (0, end - 1), "sorted": done,
                       "msg": f"Pick larger child of a[{root}]"}
                if a[child] < a[child + 1]:
                    child += 1
            st.comparisons += 1
            yield {"compare": (root, child), "range": (0, end - 1), "sorted": done,
                   "msg": f"Heapify: parent {a[root]} vs child {a[child]}"}
            if a[root] < a[child]:
                a[root], a[child] = a[child], a[root]
                st.swaps += 1
                yield {"swap": (root, child), "range": (0, end - 1), "sorted": done,
                       "msg": "Swap parent and child"}
                root = child
            else:
                return

    for s in range(n // 2 - 1, -1, -1):          # build max-heap: O(n)
        yield from sift_down(s, n)
    for end in range(n - 1, 0, -1):              # extract max n-1 times
        a[0], a[end] = a[end], a[0]
        st.swaps += 1
        done.add(end)
        yield {"swap": (0, end), "sorted": done, "msg": f"Move max {a[end]} to index {end}"}
        yield from sift_down(0, end)


# --------------------------------------------------------------------------
#  Searching algorithms
# --------------------------------------------------------------------------
def linear_search(a, st, target):
    for i, v in enumerate(a):
        st.comparisons += 1
        yield {"compare": (i,), "msg": f"Check a[{i}]={v} == {target}?"}
        if v == target:
            yield {"found": i, "msg": f"Found {target} at index {i} "
                                      f"after {st.comparisons} comparisons"}
            return
    yield {"msg": f"{target} not found ({st.comparisons} comparisons)"}


def binary_search(a, st, target):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        st.comparisons += 1
        yield {"pivot": mid, "range": (lo, hi),
               "msg": f"lo={lo}, hi={hi}, mid={mid}: a[mid]={a[mid]} vs {target}"}
        if a[mid] == target:
            yield {"found": mid, "range": (lo, hi),
                   "msg": f"Found {target} at index {mid} after {st.comparisons} comparisons"}
            return
        if a[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    yield {"range": (1, 0), "msg": f"{target} not found ({st.comparisons} comparisons)"}


# --------------------------------------------------------------------------
#  Algorithm metadata (shown in the info panel)
# --------------------------------------------------------------------------
ALGORITHMS = {
    "Bubble Sort": dict(fn=bubble_sort, kind="sort", best="O(n)", avg="O(n²)", worst="O(n²)",
                        space="O(1)", stable="Yes", paradigm="Brute force",
                        desc="Repeatedly swaps adjacent out-of-order elements; "
                             "largest element 'bubbles' to the end each pass."),
    "Selection Sort": dict(fn=selection_sort, kind="sort", best="O(n²)", avg="O(n²)", worst="O(n²)",
                           space="O(1)", stable="No", paradigm="Brute force / Greedy",
                           desc="Selects the minimum of the unsorted part and places it "
                                "at the front. Always n(n-1)/2 comparisons."),
    "Insertion Sort": dict(fn=insertion_sort, kind="sort", best="O(n)", avg="O(n²)", worst="O(n²)",
                           space="O(1)", stable="Yes", paradigm="Decrease & conquer",
                           desc="Inserts each element into its place in the sorted prefix. "
                                "Very fast on nearly-sorted data."),
    "Merge Sort": dict(fn=merge_sort, kind="sort", best="O(n log n)", avg="O(n log n)",
                       worst="O(n log n)", space="O(n)", stable="Yes", paradigm="Divide & conquer",
                       desc="Splits array in halves, sorts each recursively, merges. "
                            "Recurrence T(n) = 2T(n/2) + O(n)."),
    "Quick Sort": dict(fn=quick_sort, kind="sort", best="O(n log n)", avg="O(n log n)",
                       worst="O(n²)", space="O(log n)", stable="No", paradigm="Divide & conquer",
                       desc="Partitions around a pivot (last element, Lomuto). Worst case "
                            "on already-sorted input: T(n) = T(n-1) + O(n)."),
    "Heap Sort": dict(fn=heap_sort, kind="sort", best="O(n log n)", avg="O(n log n)",
                      worst="O(n log n)", space="O(1)", stable="No", paradigm="Transform & conquer",
                      desc="Builds a max-heap in O(n), then extracts the max n-1 times, "
                           "each costing O(log n)."),
    "Linear Search": dict(fn=linear_search, kind="search", best="O(1)", avg="O(n)", worst="O(n)",
                          space="O(1)", stable="-", paradigm="Brute force",
                          desc="Checks each element one by one. Works on unsorted data."),
    "Binary Search": dict(fn=binary_search, kind="search", best="O(1)", avg="O(log n)",
                          worst="O(log n)", space="O(1)", stable="-", paradigm="Decrease & conquer",
                          desc="Halves the search space each step. Requires sorted input "
                               "(array is sorted automatically)."),
}
SORTS = [k for k, v in ALGORITHMS.items() if v["kind"] == "sort"]


# --------------------------------------------------------------------------
#  Main application
# --------------------------------------------------------------------------
class Visualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Algorithm Visualizer - DAA Project")
        self.geometry("1180x760")
        self.minsize(900, 560)
        self.configure(bg=BG)

        self.arr = []
        self.gen = None
        self.stats = Stats()
        self.running = False
        self.paused = False
        self.after_id = None
        self.t_start = 0.0
        self.t_elapsed = 0.0
        self.last_frame = {}

        self._style()
        self._build_ui()
        self.generate()
        self.on_algo_change()

    # ---------------- UI construction ----------------
    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure(".", background=BG, foreground=FG, fieldbackground=PANEL)
        s.configure("TFrame", background=BG)
        s.configure("Panel.TFrame", background=PANEL)
        s.configure("TLabel", background=BG, foreground=FG, font=("Segoe UI", 10))
        s.configure("Panel.TLabel", background=PANEL, foreground=FG, font=("Segoe UI", 10))
        s.configure("Head.TLabel", background=PANEL, foreground=BAR, font=("Segoe UI", 12, "bold"))
        s.configure("Stat.TLabel", background=PANEL, foreground=COMPARE, font=("Consolas", 12, "bold"))
        s.configure("TButton", background=PANEL, foreground=FG, padding=6, font=("Segoe UI", 10))
        s.map("TButton", background=[("active", "#3b3b55"), ("disabled", BG)],
              foreground=[("disabled", MUTED)])
        s.configure("Accent.TButton", background="#3d59a1")
        s.map("Accent.TButton", background=[("active", "#5174d1")])
        s.configure("TCombobox", fieldbackground=PANEL, background=PANEL, foreground=FG,
                    arrowcolor=FG)
        s.map("TCombobox", fieldbackground=[("readonly", PANEL)], foreground=[("readonly", FG)],
              selectbackground=[("readonly", PANEL)], selectforeground=[("readonly", FG)])
        s.configure("TEntry", fieldbackground=PANEL, foreground=FG, insertcolor=FG)
        s.configure("Treeview", background=PANEL, fieldbackground=PANEL, foreground=FG,
                    rowheight=22, font=("Consolas", 10))
        s.configure("Treeview.Heading", background=BG, foreground=BAR, font=("Segoe UI", 10, "bold"))
        self.option_add("*TCombobox*Listbox.background", PANEL)
        self.option_add("*TCombobox*Listbox.foreground", FG)
        s.configure("Horizontal.TScale", background=BG, troughcolor=PANEL)

    def _build_ui(self):
        # --- row 1: algorithm & data controls
        top = ttk.Frame(self, padding=(10, 8, 10, 2))
        top.pack(fill="x")

        ttk.Label(top, text="Algorithm").pack(side="left")
        self.algo_var = tk.StringVar(value="Bubble Sort")
        cb = ttk.Combobox(top, textvariable=self.algo_var, values=list(ALGORITHMS),
                          state="readonly", width=16)
        cb.pack(side="left", padx=(6, 16))
        cb.bind("<<ComboboxSelected>>", lambda e: self.on_algo_change())

        ttk.Label(top, text="Size").pack(side="left")
        self.size_var = tk.IntVar(value=30)
        self.size_lbl = ttk.Label(top, text="30", width=4)
        ttk.Scale(top, from_=5, to=150, variable=self.size_var, length=130,
                  command=lambda v: self._on_size(v)).pack(side="left", padx=4)
        self.size_lbl.pack(side="left", padx=(0, 12))

        ttk.Label(top, text="Input").pack(side="left")
        self.case_var = tk.StringVar(value="Random")
        ttk.Combobox(top, textvariable=self.case_var, state="readonly", width=13,
                     values=["Random", "Sorted", "Reversed", "Nearly sorted", "Few unique"]
                     ).pack(side="left", padx=(6, 8))
        ttk.Button(top, text="Generate", command=self.generate).pack(side="left", padx=4)

        ttk.Label(top, text="   Custom").pack(side="left")
        self.custom_var = tk.StringVar()
        e = ttk.Entry(top, textvariable=self.custom_var, width=22)
        e.pack(side="left", padx=6)
        e.bind("<Return>", lambda ev: self.set_custom())
        ttk.Button(top, text="Set", command=self.set_custom).pack(side="left")

        # --- row 2: playback controls
        ctl = ttk.Frame(self, padding=(10, 4, 10, 6))
        ctl.pack(fill="x")
        self.btn_start = ttk.Button(ctl, text="▶ Start", style="Accent.TButton", command=self.start)
        self.btn_start.pack(side="left", padx=(0, 4))
        self.btn_pause = ttk.Button(ctl, text="⏸ Pause", command=self.toggle_pause)
        self.btn_pause.pack(side="left", padx=4)
        ttk.Button(ctl, text="⏭ Step", command=self.step).pack(side="left", padx=4)
        ttk.Button(ctl, text="↺ Reset", command=self.reset).pack(side="left", padx=4)

        ttk.Label(ctl, text="     Speed").pack(side="left")
        self.speed_var = tk.IntVar(value=60)
        ttk.Scale(ctl, from_=1, to=100, variable=self.speed_var, length=160).pack(side="left", padx=6)

        self.target_lbl = ttk.Label(ctl, text="   Search target")
        self.target_var = tk.StringVar()
        self.target_entry = ttk.Entry(ctl, textvariable=self.target_var, width=8)

        ttk.Button(ctl, text="📊 Complexity Analysis", command=lambda: AnalysisWindow(self)
                   ).pack(side="right")

        # --- body: canvas + side panel
        body = ttk.Frame(self, padding=(10, 0, 10, 10))
        body.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(body, bg=BG, highlightthickness=1, highlightbackground=PANEL)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw(self.last_frame))

        side = ttk.Frame(body, style="Panel.TFrame", padding=12, width=290)
        side.pack(side="right", fill="y", padx=(10, 0))
        side.pack_propagate(False)

        ttk.Label(side, text="Statistics", style="Head.TLabel").pack(anchor="w")
        self.stat_labels = {}
        for key in ("Comparisons", "Swaps / Writes", "Steps", "Time (s)"):
            row = ttk.Frame(side, style="Panel.TFrame")
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=key, style="Panel.TLabel").pack(side="left")
            lbl = ttk.Label(row, text="0", style="Stat.TLabel")
            lbl.pack(side="right")
            self.stat_labels[key] = lbl

        ttk.Separator(side).pack(fill="x", pady=10)
        self.info_title = ttk.Label(side, text="", style="Head.TLabel")
        self.info_title.pack(anchor="w")
        self.info_rows = {}
        for key in ("Best", "Average", "Worst", "Space", "Stable", "Paradigm"):
            row = ttk.Frame(side, style="Panel.TFrame")
            row.pack(fill="x", pady=1)
            ttk.Label(row, text=key, style="Panel.TLabel", foreground=MUTED).pack(side="left")
            lbl = ttk.Label(row, text="", style="Panel.TLabel")
            lbl.pack(side="right")
            self.info_rows[key] = lbl
        self.info_desc = ttk.Label(side, text="", style="Panel.TLabel", wraplength=260,
                                   justify="left", foreground=MUTED)
        self.info_desc.pack(anchor="w", pady=(8, 0))

        ttk.Separator(side).pack(fill="x", pady=8)
        ttk.Label(side, text="Legend", style="Head.TLabel").pack(anchor="w")
        for color, text in ((COMPARE, "Comparing"), (SWAP, "Swap / Write"),
                            (PIVOT, "Pivot / Key / Mid"), (SORTED, "Sorted (final)"),
                            (FOUND, "Found"), (DIM, "Outside active range")):
            row = ttk.Frame(side, style="Panel.TFrame")
            row.pack(fill="x", pady=1)
            tk.Label(row, bg=color, width=2).pack(side="left")
            ttk.Label(row, text="  " + text, style="Panel.TLabel").pack(side="left")

        # --- status bar
        self.status = tk.Label(self, text="", bg=PANEL, fg=FG, anchor="w",
                               font=("Consolas", 11), padx=10, pady=6)
        self.status.pack(fill="x", side="bottom")

    # ---------------- data ----------------
    def _on_size(self, v):
        self.size_lbl.config(text=str(int(float(v))))

    def generate(self):
        self.stop()
        n = int(self.size_var.get())
        self.arr = make_array(n, self.case_var.get())
        self._new_data()

    def set_custom(self):
        txt = self.custom_var.get().replace(",", " ").split()
        try:
            vals = [int(x) for x in txt]
        except ValueError:
            messagebox.showerror("Invalid input", "Enter integers separated by commas or spaces.")
            return
        if not 2 <= len(vals) <= 150:
            messagebox.showerror("Invalid input", "Enter between 2 and 150 numbers.")
            return
        if min(vals) < 1:
            messagebox.showerror("Invalid input", "Use positive integers (they are drawn as bar heights).")
            return
        self.stop()
        self.arr = vals
        self._new_data()

    def _new_data(self):
        self.original = list(self.arr)
        self.gen = None
        self.stats = Stats()
        self.t_elapsed = 0.0
        self.last_frame = {}
        if ALGORITHMS[self.algo_var.get()]["kind"] == "search":
            self.target_var.set(str(random.choice(self.arr)))
        self.update_stats()
        self.draw({})
        self.set_status(f"Array of {len(self.arr)} elements ready. Press Start.")

    def reset(self):
        self.stop()
        self.arr = list(self.original)
        self._new_data()

    def on_algo_change(self):
        name = self.algo_var.get()
        info = ALGORITHMS[name]
        self.info_title.config(text=name)
        self.info_rows["Best"].config(text=info["best"], foreground=SORTED)
        self.info_rows["Average"].config(text=info["avg"], foreground=COMPARE)
        self.info_rows["Worst"].config(text=info["worst"], foreground=SWAP)
        self.info_rows["Space"].config(text=info["space"])
        self.info_rows["Stable"].config(text=info["stable"])
        self.info_rows["Paradigm"].config(text=info["paradigm"])
        self.info_desc.config(text=info["desc"])
        if info["kind"] == "search":
            self.target_lbl.pack(side="left")
            self.target_entry.pack(side="left", padx=6)
        else:
            self.target_lbl.pack_forget()
            self.target_entry.pack_forget()
        self.reset()

    # ---------------- playback ----------------
    def _prepare(self):
        name = self.algo_var.get()
        info = ALGORITHMS[name]
        self.stats = Stats()
        target = None
        if info["kind"] == "search":
            try:
                target = int(self.target_var.get())
            except ValueError:
                messagebox.showerror("Target needed", "Enter an integer search target.")
                return False
            if name == "Binary Search":
                self.arr.sort()
        self.gen = info["fn"](self.arr, self.stats, target)
        self.steps = 0
        self.t_elapsed = 0.0
        return True

    def start(self):
        if self.running and not self.paused:
            return
        if self.gen is None and not self._prepare():
            return
        self.running = True
        self.paused = False
        self.btn_pause.config(text="⏸ Pause")
        self.t_start = time.perf_counter()
        self._tick()

    def toggle_pause(self):
        if not self.running:
            return
        if self.paused:
            self.start()
        else:
            self.paused = True
            self.t_elapsed += time.perf_counter() - self.t_start
            self.btn_pause.config(text="▶ Resume")
            if self.after_id:
                self.after_cancel(self.after_id)
                self.after_id = None

    def step(self):
        if self.running and not self.paused:
            self.toggle_pause()
        if self.gen is None:
            if not self._prepare():
                return
            self.running, self.paused = True, True
            self.btn_pause.config(text="▶ Resume")
        self._advance()

    def stop(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.running = False
        self.paused = False
        self.gen = None
        if hasattr(self, "btn_pause"):
            self.btn_pause.config(text="⏸ Pause")

    def _delay(self):
        s = self.speed_var.get()
        return max(1, int(800 * ((100 - s) / 99) ** 2.2))   # 800 ms .. 1 ms

    def _tick(self):
        if not self.running or self.paused:
            return
        # at top speed process several frames per redraw so large arrays stay fast
        batch = 1 if self.speed_var.get() < 95 else max(1, len(self.arr) // 15)
        for _ in range(batch):
            if not self._advance(redraw=False):
                return
        self.draw(self.last_frame)
        self.after_id = self.after(self._delay(), self._tick)

    def _advance(self, redraw=True):
        try:
            frame = next(self.gen)
        except StopIteration:
            self._finish()
            return False
        self.steps += 1
        self.last_frame = frame
        if redraw:
            self.draw(frame)
        self.update_stats()
        if "msg" in frame:
            self.set_status(frame["msg"])
        return True

    def _finish(self):
        if self.running and not self.paused:
            self.t_elapsed += time.perf_counter() - self.t_start
        name = self.algo_var.get()
        if ALGORITHMS[name]["kind"] == "sort":
            self.last_frame = {"sorted": set(range(len(self.arr)))}
            self.set_status(f"✔ {name} finished: {self.stats.comparisons} comparisons, "
                            f"{self.stats.swaps} swaps/writes for n = {len(self.arr)}")
        self.draw(self.last_frame)
        self.running = False
        self.paused = False
        self.gen = None
        self.after_id = None
        self.update_stats()

    # ---------------- rendering ----------------
    def update_stats(self):
        t = self.t_elapsed
        if self.running and not self.paused:
            t += time.perf_counter() - self.t_start
        self.stat_labels["Comparisons"].config(text=str(self.stats.comparisons))
        self.stat_labels["Swaps / Writes"].config(text=str(self.stats.swaps))
        self.stat_labels["Steps"].config(text=str(getattr(self, "steps", 0)))
        self.stat_labels["Time (s)"].config(text=f"{t:.2f}")

    def set_status(self, msg):
        self.status.config(text=msg)

    def draw(self, f):
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        n = len(self.arr)
        if n == 0 or w < 10:
            return
        f = f or {}
        top_pad, bot_pad = 26, 22 if n <= 40 else 6
        maxv = max(self.arr)
        bw = w / n
        gap = 2 if bw > 6 else (1 if bw > 3 else 0)

        compare = set(f.get("compare", ()))
        swap = set(f.get("swap", ()))
        if "write" in f:
            swap.add(f["write"])
        pivot = f.get("pivot")
        done = f.get("sorted", set())
        found = f.get("found")
        rng = f.get("range")

        for i, v in enumerate(self.arr):
            if i == found:
                color = FOUND
            elif i in swap:
                color = SWAP
            elif i in compare:
                color = COMPARE
            elif i == pivot:
                color = PIVOT
            elif i in done:
                color = SORTED
            elif rng and not (rng[0] <= i <= rng[1]):
                color = DIM
            else:
                color = BAR
            bh = (v / maxv) * (h - top_pad - bot_pad)
            x0, x1 = i * bw + gap / 2, (i + 1) * bw - gap / 2
            y0 = h - bot_pad - bh
            c.create_rectangle(x0, y0, x1, h - bot_pad, fill=color, outline="")
            if n <= 40:
                fs = 9 if n <= 25 else 7
                c.create_text((x0 + x1) / 2, y0 - 9, text=str(v), fill=FG, font=("Consolas", fs))
                c.create_text((x0 + x1) / 2, h - 10, text=str(i), fill=MUTED, font=("Consolas", 7))


# --------------------------------------------------------------------------
#  Input generators (used by both the visualizer and the analysis window)
# --------------------------------------------------------------------------
def make_array(n, case, rng=random):
    if case == "Sorted":
        a = sorted(rng.randint(5, 100) for _ in range(n))
    elif case == "Reversed":
        a = sorted((rng.randint(5, 100) for _ in range(n)), reverse=True)
    elif case == "Nearly sorted":
        a = sorted(rng.randint(5, 100) for _ in range(n))
        for _ in range(max(1, n // 10)):
            i, j = rng.randrange(n), rng.randrange(n)
            a[i], a[j] = a[j], a[i]
    elif case == "Few unique":
        vals = [rng.randint(5, 100) for _ in range(4)]
        a = [rng.choice(vals) for _ in range(n)]
    else:
        a = [rng.randint(5, 100) for _ in range(n)]
    return a


def count_ops(fn, arr):
    st = Stats()
    for _ in fn(arr, st):
        pass
    return st


# --------------------------------------------------------------------------
#  Complexity analysis window
# --------------------------------------------------------------------------
PLOT_COLORS = ["#f38ba8", "#fab387", "#f9e2af", "#a6e3a1", "#89dceb", "#cba6f7"]


class AnalysisWindow(tk.Toplevel):
    """Runs every sorting algorithm on growing input sizes (no animation) and
    plots operation count vs n, so the growth rates can be compared with theory."""

    SIZES = [10, 25, 50, 100, 150, 200, 300, 400]

    def __init__(self, master):
        super().__init__(master)
        self.title("Empirical Complexity Analysis")
        self.geometry("1000x680")
        self.configure(bg=BG)

        bar = ttk.Frame(self, padding=10)
        bar.pack(fill="x")
        ttk.Label(bar, text="Input case").pack(side="left")
        self.case = tk.StringVar(value="Random")
        ttk.Combobox(bar, textvariable=self.case, state="readonly", width=13,
                     values=["Random", "Sorted", "Reversed", "Nearly sorted", "Few unique"]
                     ).pack(side="left", padx=(6, 16))
        ttk.Label(bar, text="Metric").pack(side="left")
        self.metric = tk.StringVar(value="Comparisons")
        ttk.Combobox(bar, textvariable=self.metric, state="readonly", width=16,
                     values=["Comparisons", "Swaps / Writes", "Total operations"]
                     ).pack(side="left", padx=(6, 16))
        self.ref = tk.BooleanVar(value=True)
        tk.Checkbutton(bar, text="Reference curves (n²/2, n·log₂n)", variable=self.ref,
                       bg=BG, fg=FG, selectcolor=PANEL, activebackground=BG,
                       activeforeground=FG).pack(side="left")
        ttk.Button(bar, text="Run analysis", style="Accent.TButton",
                   command=self.run).pack(side="right")

        self.enabled = {}
        sel = ttk.Frame(self, padding=(10, 0))
        sel.pack(fill="x")
        for i, name in enumerate(SORTS):
            v = tk.BooleanVar(value=True)
            self.enabled[name] = v
            tk.Checkbutton(sel, text=name, variable=v, bg=BG, fg=PLOT_COLORS[i],
                           selectcolor=PANEL, activebackground=BG,
                           command=self.redraw).pack(side="left", padx=4)

        self.canvas = tk.Canvas(self, bg=BG, highlightthickness=0, height=400)
        self.canvas.pack(fill="both", expand=True, padx=10)
        self.canvas.bind("<Configure>", lambda e: self.redraw())

        self.table = ttk.Treeview(self, height=7, show="headings",
                                  columns=["alg"] + [str(s) for s in self.SIZES])
        self.table.heading("alg", text="Algorithm \\ n")
        self.table.column("alg", width=140, anchor="w")
        for s in self.SIZES:
            self.table.heading(str(s), text=f"n={s}")
            self.table.column(str(s), width=90, anchor="e")
        self.table.pack(fill="x", padx=10, pady=10)

        self.results = None
        self.after(100, self.run)

    def run(self):
        self.config(cursor="watch")
        self.update()
        case, metric = self.case.get(), self.metric.get()
        trials = 3 if case in ("Random", "Nearly sorted", "Few unique") else 1
        res = {}
        for name in SORTS:
            fn = ALGORITHMS[name]["fn"]
            pts = []
            for n in self.SIZES:
                tot = 0
                for t in range(trials):
                    arr = make_array(n, case, random.Random(1000 * n + t))   # same input for every algo
                    st = count_ops(fn, arr)
                    tot += {"Comparisons": st.comparisons,
                            "Swaps / Writes": st.swaps}.get(metric, st.comparisons + st.swaps)
                pts.append(tot / trials)
            res[name] = pts
        self.results = (case, metric, res)
        self.table.delete(*self.table.get_children())
        for name, pts in res.items():
            self.table.insert("", "end", values=[name] + [f"{p:,.0f}" for p in pts])
        self.config(cursor="")
        self.redraw()

    def redraw(self):
        c = self.canvas
        c.delete("all")
        if not self.results:
            return
        case, metric, res = self.results
        w, h = c.winfo_width(), c.winfo_height()
        L, R, T, B = 80, 20, 30, 40
        xs = self.SIZES
        shown = {k: v for k, v in res.items() if self.enabled[k].get()}
        refs = {}
        if self.ref.get():
            refs = {"n²/2": [n * n / 2 for n in xs], "n·log₂n": [n * math.log2(n) for n in xs]}
        allv = [v for pts in list(shown.values()) + list(refs.values()) for v in pts] or [1]
        ymax = nice_max(max(allv))
        xmax = xs[-1]

        def px(x):
            return L + (x / xmax) * (w - L - R)

        def py(y):
            return h - B - (y / ymax) * (h - T - B)

        # grid + axes
        for k in range(6):
            yv = ymax * k / 5
            c.create_line(L, py(yv), w - R, py(yv), fill=PANEL)
            c.create_text(L - 8, py(yv), text=f"{yv:,.0f}", fill=MUTED, anchor="e", font=("Consolas", 9))
        for x in xs:
            c.create_line(px(x), h - B, px(x), h - B + 4, fill=MUTED)
            c.create_text(px(x), h - B + 14, text=str(x), fill=MUTED, font=("Consolas", 9))
        c.create_line(L, T, L, h - B, fill=MUTED)
        c.create_line(L, h - B, w - R, h - B, fill=MUTED)
        c.create_text(w / 2, h - 8, text="Input size n", fill=FG, font=("Segoe UI", 10))
        c.create_text(L, 12, text=f"{metric}  —  {case} input", fill=FG, anchor="w",
                      font=("Segoe UI", 11, "bold"))

        for name, pts in refs.items():
            c.create_line(*[v for x, y in zip(xs, pts) for v in (px(x), py(y))],
                          fill=MUTED, dash=(4, 4), width=1)
            c.create_text(px(xs[-1]) - 4, py(pts[-1]) - 8, text=name, fill=MUTED, anchor="e",
                          font=("Consolas", 9))

        legend_y = T + 6
        for i, name in enumerate(SORTS):
            if name not in shown:
                continue
            pts, col = shown[name], PLOT_COLORS[i]
            coords = [v for x, y in zip(xs, pts) for v in (px(x), py(y))]
            c.create_line(*coords, fill=col, width=2.5, smooth=False)
            for x, y in zip(xs, pts):
                c.create_oval(px(x) - 3, py(y) - 3, px(x) + 3, py(y) + 3, fill=col, outline="")
            c.create_rectangle(L + 16, legend_y - 5, L + 28, legend_y + 5, fill=col, outline="")
            c.create_text(L + 34, legend_y, text=name, fill=FG, anchor="w", font=("Segoe UI", 9))
            legend_y += 18


def nice_max(v):
    if v <= 0:
        return 1
    p = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if v <= m * p:
            return m * p
    return 10 * p


if __name__ == "__main__":
    Visualizer().mainloop()