#!/bin/bash
echo "Starting Ngrok Tunnel..."
echo "Domain: brush-unseemly-subpar.ngrok-free.dev"
echo "Your permanent bot URL will be: https://brush-unseemly-subpar.ngrok-free.dev"
echo ""
echo "Note: If you are using a different ngrok account, edit this script and change the url,"
echo "or just run 'ngrok http 8080' for a temporary URL."
echo ""
ngrok http --url=brush-unseemly-subpar.ngrok-free.dev 8080
