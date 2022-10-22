FROM golang:latest
ADD . .
RUN go build -o main.exe main.go
EXPOSE 1776
CMD ["./main.exe"]