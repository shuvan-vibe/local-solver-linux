#!/bin/bash
echo "Starting Ngrok Tunnel..."
echo "Domain: winner-snarl-progress.ngrok-free.dev"
echo "Your permanent bot URL will be: https://winner-snarl-progress.ngrok-free.dev"
echo ""
echo "Note: If you are using a different ngrok account, edit this script and change the domain,"
echo "or just run 'ngrok http 8080' for a temporary URL."
echo ""
ngrok http --domain=winner-snarl-progress.ngrok-free.dev 8080
