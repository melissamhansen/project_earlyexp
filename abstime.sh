#!/bin/bash

# Define the directory
DIRECTORY="/Volumes/MerzLab/MRI_Study_of_Inhibitory_Control/Data/MRI_behavioral_data/timing_solution/CSVs"
OUTPUT_DIR="/Volumes/MerzLab/MRI_Study_of_Inhibitory_Control/Data/MRI_behavioral_data/timing_solution/timing"
OUTPUT_FILE="$OUTPUT_DIR/csv_creation_times.csv"


# Find all .csv files in the directory and extract the creation date and time
find "$DIRECTORY" -type f -name "*.csv" -exec sh -c '
  for file do
    # Extract the creation date and time using stat
    creation_datetime=$(stat -f "%SB" -t "%Y-%m-%d %H:%M:%S" "$file")
    # Extract the date and time components
    creation_date=$(echo "$creation_datetime" | cut -d " " -f 1)
    creation_time=$(echo "$creation_datetime" | cut -d " " -f 2)
    # Extract the base name of the file and get the first 5 characters
    file_basename=$(basename "$file")
    file_prefix=$(echo "$file_basename" | cut -c 1-5)
    # Print the file prefix, creation date, and creation time in CSV format
    echo "$file_prefix,$creation_date,$creation_time"
  done
' sh {} + > "$OUTPUT_FILE"

# Add headers to the CSV file
echo "file,date,csvtime" > temp_file && cat "$OUTPUT_FILE" >> temp_file && mv temp_file "$OUTPUT_FILE"
