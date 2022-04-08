source /.env
echo "$MSG" | nc -w 1 $SERVER_IP $SERVER_PORT | grep "$MSG"
test $? -eq 0 && echo "OK" || echo "ERROR: Message doesn't match"
