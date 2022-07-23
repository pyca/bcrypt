package main

import (
	"io"
	"os"
	"strconv"

	"golang.org/x/crypto/bcrypt"
)

// provides access to the golang implementation of bcrypt, for reference:
// "password" to hash is provided on stdin, cost parameter is an optional
// command-line parameter

func main() {
	cost := bcrypt.MinCost
	if len(os.Args) > 1 {
		if parsed, err := strconv.Atoi(os.Args[1]); err == nil {
			cost = parsed
		}
	}

	buf, err := io.ReadAll(os.Stdin)
	if err != nil {
		panic(err)
	}

	out, err := bcrypt.GenerateFromPassword(buf, cost)
	if err != nil {
		panic(err)
	}

	os.Stdout.Write(out)
	os.Stdout.Write([]byte("\n"))
}
