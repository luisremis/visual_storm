rm -rf db *.log

vdms > build_vdms_screen.log 2> build_vdms_log.log &

sleep 1

python -m unittest discover --pattern=TestVideoBench*.py -v

pkill vdms
