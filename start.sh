#!/bin/bash

# remove CATEGORIES_PK from .env file
sed -i '/CATEGORIES_PK/d' .env

# Run your setup script
python pre_run_generate_categories.py

# Then start your Python application
python financebot.py