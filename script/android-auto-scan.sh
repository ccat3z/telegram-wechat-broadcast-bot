: > log

tail -f log | {
    while :
    do
        read f
        am broadcast \
        -a android.intent.action.MEDIA_SCANNER_SCAN_FILE \
        -d file://$PWD/$f.png
    done
}
