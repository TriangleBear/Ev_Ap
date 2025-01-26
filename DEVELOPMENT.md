# Development Guide

Welcome to the Event Attendance repository! This document will guide you through the development setup and contribution process.

## Getting Started

### Prerequisites

Before you start developing, make sure you have the following tools installed:

- Python 3.x (Recommended version: 3.8+)
- Git
- A code editor like Visual Studio Code, PyCharm, etc.

### Setting Up the Development Environment

1. Clone the repository to your local machine:
    ```bash
    git clone https://github.com/your-username/event-attendance.git
    cd event-attendance
    ```

2. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application Locally

To start the application locally, use the following command:

```bash
python app.py
```

## Contributing

If you'd like to contribute, please follow these steps:

1. Fork the repository and clone it to your local machine.
2. Create a new branch for your feature or bug fix:
    ```bash
    git checkout -b feature/your-feature-name
    ```
3. Make your changes, ensuring that your code is well-documented and follows the style guide.
4. Commit your changes with a clear and concise message:
    ```bash
    git commit -m "Add feature: your-feature-name"
    ```
5. Push your changes to your fork:
    ```bash
    git push origin feature/your-feature-name
    ```
6. Open a pull request against the `main` branch of this repository.

Please ensure that your code passes all tests and adheres to the project's coding standards.

## Running Tests

To run the test suite, use the following command:

```bash
pytest
```

Ensure that all tests pass before submitting your pull request.

## Code Style

We follow the [PEP 8](https://peps.python.org/pep-0008/) style guide for Python code. Please ensure your code adheres to it.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license (see `LICENSE`).

## Need Help?

If you need help or have any questions, feel free to reach out by opening an issue or asking for assistance in the discussions.
