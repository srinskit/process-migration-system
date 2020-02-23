killall -s9 pm-pro
./pm-pro
pids=($(pgrep pm-pro))
pid1=${pids[0]}
pid2=${pids[1]}

echo 'stopping' $pid2
kill -STOP $pid2

sleep 2
echo 'stopping' $pid1
kill -STOP $pid1

echo "VMEM $pid1 >>> $pid2"
sudo python ../vmem-copy/main.py $pid1 $pid2
echo "VMEM copied"

echo "KSTATE $pid1 >>> $pid2"
echo "$pid1 $pid2" >/dev/regcp
echo "KSTATE copied"

kill -KILL $pid1
kill -CONT $pid2

sleep 2
echo "Transistion"
tail -3 child-0.txt
head -3 child-1.txt