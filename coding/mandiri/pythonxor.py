# Define a long string of digits
long_string = "01313030303030303030303530303030303030303030303030303003"

# Initialize a variable to store the cumulative XOR result
cumulative_xor = 0

# Loop through the string in steps of 2
for i in range(0, len(long_string), 2):
    # Take a two-digit segment
    segment = long_string[i:i+2]
    
    # Convert the segment to an integer
    num = int(segment)
    
    # Perform XOR with the cumulative result
    cumulative_xor ^= num

# Print the final XOR result
print(cumulative_xor)
