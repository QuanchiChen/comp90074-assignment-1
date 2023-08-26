# COMP90074-Assignment-1

In COMP90074 Web Security Assignment 1, I found, analysed, exploited, and fixed several cross-site scripting (XSS) and SQL injection vulnerabilities in the provided web application.

## Repository Structure

Assignment-1-Specification.pdf is the assignment specification. To understand the context, I suggest you read through it first.

The text file vulnerabilities.txt records the three identified vulnerabilities.

The source code main.go is the client program exploiting two of the three identifies vulnerabilities.

## Get Started

1. Run the dockerised web application.

   `./server/run_server.sh`

2. Run the dockerised client exploit program.

   `./run_client.sh`

3. Go to the signup page and register a new user.

4. Go to the login page and log in to the application.

5. You will see an alert box, "This site has been hacked!".

## Feedback