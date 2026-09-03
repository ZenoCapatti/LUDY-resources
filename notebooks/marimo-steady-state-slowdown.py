# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.10",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo

    # A/B switch: keep the same 95 source cells while removing the large,
    # interactive table outputs.
    show_rich_outputs = True

    def make_rows(block: int) -> list[dict[str, object]]:
        statuses = ("accepted", "review", "derived", "stable")
        regions = ("soft", "collinear", "hard", "threshold")
        rows = []
        for row in range(18):
            numerator = ((block + 3) * (row + 11)) % 997
            rows.append(
                {
                    "row": row,
                    "quantity": f"q_{block:02d}_{row:02d}",
                    "value": round(numerator / 17.0, 6),
                    "uncertainty": f"{(block + row + 1) / 10000:.4e}",
                    "status": statuses[(block + row) % len(statuses)],
                    "region": regions[(2 * block + row) % len(regions)],
                    "source": f"block-{block:02d}/record-{row:02d}",
                    "comment": "deterministic benchmark record",
                }
            )
        return rows

    return make_rows, mo, show_rich_outputs


@app.cell
def _(mo):
    mo.md(r"""
    # Stock-Marimo steady-state editor slowdown reproducer

    This notebook deliberately contains **95 real Marimo cells**, including
    32 native `mo.ui.table` outputs and 60 Markdown analysis cells. It has
    no Symbolica, Typst, pandas, NumPy, or network dependency.

    ## Reproduction protocol

    1. Run `marimo edit marimo-steady-state-slowdown.py`.
    2. Wait until execution is complete, press **End**, then **Home**, and
       wait a few seconds. This gives progressive editor mounting a chance
       to reach steady state.
    3. Edit the sentence in the next cell at `EDIT_PROBE`; type and erase
       roughly 20 characters several times.
    4. Open the command palette with **Cmd-K**. Measure the first opening,
       dismiss it, then repeat several times to measure the warm path.
    5. Record typing-to-paint and scrolling latency with the browser
       performance panel or a screen recording. Also note long tasks and
       dropped frames.
    6. Set `show_rich_outputs = False` in the first cell and repeat. Cell
       count stays fixed; only the native rich table outputs disappear.
    7. For an editor-count control, compare against a three-cell notebook,
       or delete or comment out roughly half of
       the repeated cells and repeat.

    Useful report metadata: Marimo version, browser/version, OS, hardware,
    whether a Python language server is enabled, cell count, and whether
    `show_rich_outputs` is true.

    ## Reference measurement

    A Marimo 0.23.16 run on macOS produced the following steady-state values.
    The edit timings include browser-automation overhead, so their ratios are
    more useful than their absolute values.

    | case | DOM nodes | body HTML | median 19-character edit |
    |---|---:|---:|---:|
    | 3-cell control | 1,123 | 116 KB | 1.079 s |
    | 95 cells, rich outputs off | 20,970 | 2.00 MB | 1.892 s |
    | 95 cells, rich outputs on | 22,079 | 2.34 MB | 2.195 s |

    This separates a large steady-state editor-count cost from the additional
    cost of mounting the native rich tables.

    ### Command-palette A/B on Marimo 0.24.0

    The same browser session, with the three-cell control opened first,
    produced:

    | case | first open | warm median |
    |---|---:|---:|
    | 3-cell control | 3.12 s | 269 ms |
    | this 95-cell notebook | 4.61 s | 534 ms |

    Both first openings include Marimo's lazy palette loading. The additional
    large-notebook cost remains about 1.49 s on the first open and 265 ms once
    warm. Marimo 0.24.0 therefore does not resolve the scaling problem.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Editable latency probe

    **EDIT_PROBE:** Type and erase text at the end of this sentence while
    watching whether the caret and rendered es

    This cell is intentionally small. Its source and rendered output should
    be cheap in isolation, so lag here reflects the already-mounted
    notebook rather than expensive work inside the edited cell.
    """)
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 01

    Deterministic records for analysis block 01.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(0), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 01\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 02

    Deterministic records for analysis block 02.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(1), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 02\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 03

    Deterministic records for analysis block 03.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(2), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 03\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 04

    Deterministic records for analysis block 04.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(3), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 04\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 05

    Deterministic records for analysis block 05.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(4), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 05\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 06

    Deterministic records for analysis block 06.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(5), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 06\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 07

    Deterministic records for analysis block 07.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(6), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 07\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 08

    Deterministic records for analysis block 08.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(7), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 08\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 09

    Deterministic records for analysis block 09.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(8), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 09\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 10

    Deterministic records for analysis block 10.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(9), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 10\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 11

    Deterministic records for analysis block 11.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(10), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 11\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 12

    Deterministic records for analysis block 12.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(11), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 12\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 13

    Deterministic records for analysis block 13.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(12), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 13\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 14

    Deterministic records for analysis block 14.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(13), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 14\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 15

    Deterministic records for analysis block 15.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(14), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 15\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 16

    Deterministic records for analysis block 16.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(15), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 16\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 17

    Deterministic records for analysis block 17.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(16), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 17\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 18

    Deterministic records for analysis block 18.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(17), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 18\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 19

    Deterministic records for analysis block 19.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(18), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 19\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 20

    Deterministic records for analysis block 20.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(19), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 20\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 21

    Deterministic records for analysis block 21.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(20), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 21\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 22

    Deterministic records for analysis block 22.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(21), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 22\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 23

    Deterministic records for analysis block 23.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(22), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 23\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 24

    Deterministic records for analysis block 24.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(23), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 24\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 25

    Deterministic records for analysis block 25.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(24), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 25\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 26

    Deterministic records for analysis block 26.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(25), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 26\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 27

    Deterministic records for analysis block 27.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(26), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 27\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 28

    Deterministic records for analysis block 28.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(27), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 28\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 29

    Deterministic records for analysis block 29.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(28), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 29\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 30

    Deterministic records for analysis block 30.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(29), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 30\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 31

    Deterministic records for analysis block 31.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(30), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 31\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(make_rows, mo, show_rich_outputs):
    if show_rich_outputs:
        _output = mo.vstack(
            [
                mo.md(
                    r"""
    ### Result table 32

    Deterministic records for analysis block 32.
    The table is deliberately unpaginated so its full rich output is mounted.
    """
                ),
                mo.ui.table(make_rows(31), pagination=False),
            ],
            gap=0.25,
        )
    else:
        _output = mo.md(
            "### Result table 32\n\n"
            "Rich output disabled for the editors-only A/B run."
        )
    _output
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 01

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{1}$ | $(2 x + 3) / (3 + x^2)$ | retained |
    | $\Delta_{1}$ | $r_{1} - r_{2}$ | checked |
    | block | `01` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 02

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{2}$ | $(3 x + 4) / (4 + x^2)$ | retained |
    | $\Delta_{2}$ | $r_{2} - r_{3}$ | checked |
    | block | `02` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 03

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{3}$ | $(4 x + 5) / (5 + x^2)$ | retained |
    | $\Delta_{3}$ | $r_{3} - r_{4}$ | checked |
    | block | `03` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 04

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{4}$ | $(5 x + 6) / (6 + x^2)$ | retained |
    | $\Delta_{4}$ | $r_{4} - r_{5}$ | checked |
    | block | `04` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 05

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{5}$ | $(6 x + 7) / (7 + x^2)$ | retained |
    | $\Delta_{5}$ | $r_{5} - r_{6}$ | checked |
    | block | `05` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 06

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{6}$ | $(7 x + 8) / (8 + x^2)$ | retained |
    | $\Delta_{6}$ | $r_{6} - r_{7}$ | checked |
    | block | `06` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 07

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{7}$ | $(8 x + 9) / (9 + x^2)$ | retained |
    | $\Delta_{7}$ | $r_{7} - r_{8}$ | checked |
    | block | `07` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 08

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{8}$ | $(9 x + 10) / (10 + x^2)$ | retained |
    | $\Delta_{8}$ | $r_{8} - r_{9}$ | checked |
    | block | `08` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 09

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{9}$ | $(10 x + 11) / (11 + x^2)$ | retained |
    | $\Delta_{9}$ | $r_{9} - r_{10}$ | checked |
    | block | `09` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 10

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{10}$ | $(11 x + 12) / (12 + x^2)$ | retained |
    | $\Delta_{10}$ | $r_{10} - r_{11}$ | checked |
    | block | `10` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 11

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{11}$ | $(12 x + 13) / (13 + x^2)$ | retained |
    | $\Delta_{11}$ | $r_{11} - r_{12}$ | checked |
    | block | `11` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 12

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{12}$ | $(13 x + 14) / (14 + x^2)$ | retained |
    | $\Delta_{12}$ | $r_{12} - r_{13}$ | checked |
    | block | `12` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 13

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{13}$ | $(14 x + 15) / (15 + x^2)$ | retained |
    | $\Delta_{13}$ | $r_{13} - r_{14}$ | checked |
    | block | `13` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 14

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{14}$ | $(15 x + 16) / (16 + x^2)$ | retained |
    | $\Delta_{14}$ | $r_{14} - r_{15}$ | checked |
    | block | `14` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 15

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{15}$ | $(16 x + 17) / (17 + x^2)$ | retained |
    | $\Delta_{15}$ | $r_{15} - r_{16}$ | checked |
    | block | `15` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 16

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{16}$ | $(17 x + 18) / (18 + x^2)$ | retained |
    | $\Delta_{16}$ | $r_{16} - r_{17}$ | checked |
    | block | `16` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 17

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{17}$ | $(18 x + 19) / (19 + x^2)$ | retained |
    | $\Delta_{17}$ | $r_{17} - r_{18}$ | checked |
    | block | `17` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 18

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{18}$ | $(19 x + 20) / (20 + x^2)$ | retained |
    | $\Delta_{18}$ | $r_{18} - r_{19}$ | checked |
    | block | `18` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 19

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{19}$ | $(20 x + 21) / (21 + x^2)$ | retained |
    | $\Delta_{19}$ | $r_{19} - r_{20}$ | checked |
    | block | `19` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 20

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{20}$ | $(21 x + 22) / (22 + x^2)$ | retained |
    | $\Delta_{20}$ | $r_{20} - r_{21}$ | checked |
    | block | `20` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 21

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{21}$ | $(22 x + 23) / (23 + x^2)$ | retained |
    | $\Delta_{21}$ | $r_{21} - r_{22}$ | checked |
    | block | `21` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 22

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{22}$ | $(23 x + 24) / (24 + x^2)$ | retained |
    | $\Delta_{22}$ | $r_{22} - r_{23}$ | checked |
    | block | `22` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 23

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{23}$ | $(24 x + 25) / (25 + x^2)$ | retained |
    | $\Delta_{23}$ | $r_{23} - r_{24}$ | checked |
    | block | `23` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 24

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{24}$ | $(25 x + 26) / (26 + x^2)$ | retained |
    | $\Delta_{24}$ | $r_{24} - r_{25}$ | checked |
    | block | `24` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 25

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{25}$ | $(26 x + 27) / (27 + x^2)$ | retained |
    | $\Delta_{25}$ | $r_{25} - r_{26}$ | checked |
    | block | `25` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 26

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{26}$ | $(27 x + 28) / (28 + x^2)$ | retained |
    | $\Delta_{26}$ | $r_{26} - r_{27}$ | checked |
    | block | `26` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 27

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{27}$ | $(28 x + 29) / (29 + x^2)$ | retained |
    | $\Delta_{27}$ | $r_{27} - r_{28}$ | checked |
    | block | `27` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 28

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{28}$ | $(29 x + 30) / (30 + x^2)$ | retained |
    | $\Delta_{28}$ | $r_{28} - r_{29}$ | checked |
    | block | `28` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 29

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{29}$ | $(30 x + 31) / (31 + x^2)$ | retained |
    | $\Delta_{29}$ | $r_{29} - r_{30}$ | checked |
    | block | `29` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 30

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{30}$ | $(31 x + 32) / (32 + x^2)$ | retained |
    | $\Delta_{30}$ | $r_{30} - r_{31}$ | checked |
    | block | `30` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 31

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{31}$ | $(32 x + 33) / (33 + x^2)$ | retained |
    | $\Delta_{31}$ | $r_{31} - r_{32}$ | checked |
    | block | `31` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 32

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{32}$ | $(33 x + 34) / (34 + x^2)$ | retained |
    | $\Delta_{32}$ | $r_{32} - r_{33}$ | checked |
    | block | `32` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 33

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{33}$ | $(34 x + 35) / (35 + x^2)$ | retained |
    | $\Delta_{33}$ | $r_{33} - r_{34}$ | checked |
    | block | `33` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 34

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{34}$ | $(35 x + 36) / (36 + x^2)$ | retained |
    | $\Delta_{34}$ | $r_{34} - r_{35}$ | checked |
    | block | `34` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 35

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{35}$ | $(36 x + 37) / (37 + x^2)$ | retained |
    | $\Delta_{35}$ | $r_{35} - r_{36}$ | checked |
    | block | `35` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 36

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{36}$ | $(37 x + 38) / (38 + x^2)$ | retained |
    | $\Delta_{36}$ | $r_{36} - r_{37}$ | checked |
    | block | `36` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 37

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{37}$ | $(38 x + 39) / (39 + x^2)$ | retained |
    | $\Delta_{37}$ | $r_{37} - r_{38}$ | checked |
    | block | `37` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 38

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{38}$ | $(39 x + 40) / (40 + x^2)$ | retained |
    | $\Delta_{38}$ | $r_{38} - r_{39}$ | checked |
    | block | `38` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 39

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{39}$ | $(40 x + 41) / (41 + x^2)$ | retained |
    | $\Delta_{39}$ | $r_{39} - r_{40}$ | checked |
    | block | `39` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 40

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{40}$ | $(41 x + 42) / (42 + x^2)$ | retained |
    | $\Delta_{40}$ | $r_{40} - r_{41}$ | checked |
    | block | `40` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 41

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{41}$ | $(42 x + 43) / (43 + x^2)$ | retained |
    | $\Delta_{41}$ | $r_{41} - r_{42}$ | checked |
    | block | `41` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 42

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{42}$ | $(43 x + 44) / (44 + x^2)$ | retained |
    | $\Delta_{42}$ | $r_{42} - r_{43}$ | checked |
    | block | `42` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 43

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{43}$ | $(44 x + 45) / (45 + x^2)$ | retained |
    | $\Delta_{43}$ | $r_{43} - r_{44}$ | checked |
    | block | `43` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 44

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{44}$ | $(45 x + 46) / (46 + x^2)$ | retained |
    | $\Delta_{44}$ | $r_{44} - r_{45}$ | checked |
    | block | `44` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 45

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{45}$ | $(46 x + 47) / (47 + x^2)$ | retained |
    | $\Delta_{45}$ | $r_{45} - r_{46}$ | checked |
    | block | `45` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 46

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{46}$ | $(47 x + 48) / (48 + x^2)$ | retained |
    | $\Delta_{46}$ | $r_{46} - r_{47}$ | checked |
    | block | `46` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 47

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{47}$ | $(48 x + 49) / (49 + x^2)$ | retained |
    | $\Delta_{47}$ | $r_{47} - r_{48}$ | checked |
    | block | `47` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 48

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{48}$ | $(49 x + 50) / (50 + x^2)$ | retained |
    | $\Delta_{48}$ | $r_{48} - r_{49}$ | checked |
    | block | `48` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 49

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{49}$ | $(50 x + 51) / (51 + x^2)$ | retained |
    | $\Delta_{49}$ | $r_{49} - r_{50}$ | checked |
    | block | `49` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 50

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{50}$ | $(51 x + 52) / (52 + x^2)$ | retained |
    | $\Delta_{50}$ | $r_{50} - r_{51}$ | checked |
    | block | `50` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 51

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{51}$ | $(52 x + 53) / (53 + x^2)$ | retained |
    | $\Delta_{51}$ | $r_{51} - r_{52}$ | checked |
    | block | `51` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 52

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{52}$ | $(53 x + 54) / (54 + x^2)$ | retained |
    | $\Delta_{52}$ | $r_{52} - r_{53}$ | checked |
    | block | `52` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 53

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{53}$ | $(54 x + 55) / (55 + x^2)$ | retained |
    | $\Delta_{53}$ | $r_{53} - r_{54}$ | checked |
    | block | `53` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 54

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{54}$ | $(55 x + 56) / (56 + x^2)$ | retained |
    | $\Delta_{54}$ | $r_{54} - r_{55}$ | checked |
    | block | `54` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 55

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{55}$ | $(56 x + 57) / (57 + x^2)$ | retained |
    | $\Delta_{55}$ | $r_{55} - r_{56}$ | checked |
    | block | `55` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 56

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{56}$ | $(57 x + 58) / (58 + x^2)$ | retained |
    | $\Delta_{56}$ | $r_{56} - r_{57}$ | checked |
    | block | `56` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 57

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{57}$ | $(58 x + 59) / (59 + x^2)$ | retained |
    | $\Delta_{57}$ | $r_{57} - r_{58}$ | checked |
    | block | `57` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 58

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{58}$ | $(59 x + 60) / (60 + x^2)$ | retained |
    | $\Delta_{58}$ | $r_{58} - r_{59}$ | checked |
    | block | `58` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 59

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{59}$ | $(60 x + 61) / (61 + x^2)$ | retained |
    | $\Delta_{59}$ | $r_{59} - r_{60}$ | checked |
    | block | `59` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ### Analysis note 60

    This is deterministic stock Markdown output. It stands in for a short
    derivation or explanation in a scientific notebook.

    | quantity | definition | state |
    |---|---:|---|
    | $r_{60}$ | $(61 x + 62) / (62 + x^2)$ | retained |
    | $\Delta_{60}$ | $r_{60} - r_{61}$ | checked |
    | block | `60` | complete |

    The prose and small table make the rendered output nontrivial without
    requiring Typst, Symbolica, NumPy, pandas, or network access.
    """)
    return


if __name__ == "__main__":
    app.run()
