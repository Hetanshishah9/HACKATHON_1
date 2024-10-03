import os

class FileHandler:
    @staticmethod
    def read_file(filename):
        """Read file data."""
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                return f.read()  # Return bytes directly
        
        raise FileNotFoundError(f"File '{filename}' not found.")

    @staticmethod
    def write_file(filename, data):
        """Write data to a file."""
        with open(filename, 'wb') as f:
            f.write(data)