#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script serves as a manual trigger to update the cryptocurrency data file.
It imports and runs the main data update logic from the 'data_updater' module.
"""

from src.data_updater import run_update

if __name__ == "__main__":
    print("Starting manual data refresh...")
    run_update()
    print("Manual data refresh complete.")