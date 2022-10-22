package main

import (
	"fmt"
	"net/http"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintf(w, "novus ordo seclorum")
	})
	http.ListenAndServe(":1776", nil)
}
