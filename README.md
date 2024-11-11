# chainlit_local_persistence

This repository provides a simple demo of how to implement local persistence for Chainlit. The demo shows how you can persist data locally using either JSON (default) or Pickle file formats in the `/tmp/` directory. The implementation supports creating threads, steps, and feedbacks, though element creation is not implemented.

## Features
- Local persistence using JSON or Pickle.
- Supports the creation of threads, steps, and feedbacks.
- Data is stored in the `/tmp/` directory (modifiable).
- Demonstrates how to persist Chainlit-related data without using external databases.

## Prerequisites

- Python 3.x
- Chainlit (https://github.com/Chainlit/chainlit)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/bixentemal/chainlit_local_persistence.git
   cd chainlit_local_persistence
   
2. Install required dependencies:
   ```bash
    pip install -r requirements.txt

## Usage

By default, the demo will persist data in a JSON file within the /tmp/ directory. You can configure this to use Pickle by modifying the persistence format in the code.
To run the demo, simply execute the following:

```bash
python main.py
```

The demo will create threads, steps, and feedbacks and persist them locally. You can modify the demo to experiment with these features or extend it as needed.

## File Formats

* JSON (default): Data will be stored as JSON files. This format is human-readable and easy to inspect.
* Pickle: An alternative binary format. You can switch to Pickle for more compact storage and faster read/write operations (but not human-readable).

## Structure

* /tmp/: Directory where data is stored. You can modify the directory or file name by changing the code configuration.
* main.py: A simple demo script that demonstrates how to create threads, steps, and feedbacks.
* local_data_layer.py and cl_local_data_layer : Contains the implementation of the persistence logic (JSON and Pickle options).

## Contributing

* Fork the repository.
* Create a new branch for your feature or bugfix.
* Make your changes.
* Submit a pull request.

* ## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

* Chainlit: A powerful framework for building AI assistants.
* Pickle and JSON: Used for data serialization.

For more information about Chainlit, visit the official documentation at: https://chainlit.io


You can adjust the content depending on the specific functionality or the structure of the code. Let me know if you need any more details or adjustments!
