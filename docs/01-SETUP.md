# Setup Guide

This guide will help you set up the Dario Electricista project on your local machine.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- You have a working installation of [Node.js](https://nodejs.org/) (version X.X.X or later).
- You have [npm](https://www.npmjs.com/) installed (comes with Node.js).

## Steps to Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/mutafiaforneto1/Dario-electricista-pro.git
    cd Dario-electricista-pro
    ```

2. **Install Dependencies**:
    ```bash
    npm install
    ```

3. **Configure Environment Variables**:
   - Create a `.env` file in the root directory of the project.
   - Add the necessary variables. For example:
     ```env
     DB_HOST=localhost
     DB_USER=root
     DB_PASS=password
     ```

4. **Run the Application**:
    ```bash
    npm start
    ```

5. **Open your browser**:
   - Go to `http://localhost:3000` to see your application in action.

## Troubleshooting

- Ensure your database is running if your application does not connect.
- Refer to the logs for any errors that occur during startup.

## Conclusion

You should now have a fully functional setup of the Dario Electricista project! If you have further questions, check the repository issues or contact support.