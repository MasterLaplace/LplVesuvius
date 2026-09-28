"""vesuve: one program, one pipeline per Vesuvius Challenge prize.

The equations live in the C core (`vesuve.core`), reading and writing in the Python services, and each prize in
its own package (`grand_prize`, `first_letters`, `paris4_title`, `progress`), which never imports another prize.
"""
__version__ = "0.2.0"
