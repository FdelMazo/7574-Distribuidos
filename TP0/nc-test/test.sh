MSG="i want you back"
echo "$MSG" | nc server 12345 | grep "$MSG"
test $? -eq 0 && echo "OK" || echo "ERROR: Message doesn't match"
