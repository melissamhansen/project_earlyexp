#!/bin/bash

# Define the directory containing the JSON files
JSON_DIR="/Volumes/MerzLab/MRI_Study_of_Inhibitory_Control/Data/MRI_behavioral_data/timing_solution/jsons"
OUTPUT_DIR="/Volumes/MerzLab/MRI_Study_of_Inhibitory_Control/Data/MRI_behavioral_data/timing_solution/timing"
OUTPUT_FILE="$OUTPUT_DIR/json_acquisition_times.csv"

# Initialize the CSV file with headers
echo "file,AcquisitionTime" > "$OUTPUT_FILE"

# Loop through all JSON files in the directory
for JSON_FILE in "$JSON_DIR"/*.json; do
  # Use jq to extract the "AcquisitionTime"
  ACQUISITION_TIME=$(jq -r '.AcquisitionTime' "$JSON_FILE")
  
  # Extract the HH:MM:SS part of the "AcquisitionTime"
  HHMMSS=$(echo "$ACQUISITION_TIME" | cut -d '.' -f 1)
  
  # Extract the base name of the file (without path)
  FILE_NAME=$(basename "$JSON_FILE")
  
  # Append the file name and extracted HH:MM:SS to the CSV file
  echo "$FILE_NAME,$HHMMSS" >> "$OUTPUT_FILE"
done
