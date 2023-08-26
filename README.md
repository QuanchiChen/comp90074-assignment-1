# COMP90074-Assignment-1

In COMP90074 Web Security Assignment 1, I found, analysed, exploited, and fixed several cross-site scripting (XSS) and SQL injection vulnerabilities in the provided web application.

## Repository Structure

Assignment-1-Specification.pdf is the assignment specification. To understand the context, I suggest you read through it first.

The directory server contains the source code of the vulnerable web application.

The text file vulnerabilities.txt records the three identified vulnerabilities.

The directory client contains the source code of the client program exploiting two identified vulnerabilities.

## Get Started

1. Open a Terminal and change the current working directory.

   `cd server/`

2. Run the dockerised web application.

   `./run_server.sh`

3. Open another Terminal and change the current working directory.

   `cd client/`

4. Run the dockerised client exploit program.

   `./run_client.sh`

5. Go to the signup page and register a new user.

6. Go to the login page and log in to the application.

7. You will see an alert box, "This site has been hacked!".

## Feedback