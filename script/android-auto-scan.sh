FIFO=$@

rm -f $FIFO
mkfifo $FIFO
while :
do
    read f < $FIFO
    am broadcast \
    -a android.intent.action.MEDIA_SCANNER_SCAN_FILE \
    -d file://$PWD/$f.png
done
